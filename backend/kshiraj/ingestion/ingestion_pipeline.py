"""
kshiraj/ingestion/ingestion_pipeline.py

End-to-end ingestion pipeline orchestrator.
Connects acquisition -> extraction -> deduplication -> source adapters -> stores -> vector indexer.
Reuses existing Kshiraj source adapters, knowledge stores, and Qdrant vector pipeline.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple, Union

from shared.models import Evidence, EvidenceSourceType, Standard, StandardStatus
from shared.utils import SourceAdapterError, get_logger, utcnow
from kshiraj.ingestion.crawler import GovtCrawler
from kshiraj.ingestion.deduplication import DocumentDeduplicator, DocumentState
from kshiraj.ingestion.frontier import normalize_url
from kshiraj.ingestion.html_extractor import HtmlExtractor
from kshiraj.ingestion.http_client import GovtHttpClient
from kshiraj.ingestion.incremental import IncrementalIngestionTracker
from kshiraj.ingestion.json_extractor import JsonExtractor
from kshiraj.ingestion.models import (
    CrawlPolicy,
    CrawlResult,
    ExtractionStatus,
    FetchedResource,
    IngestionResult,
    IngestionStatus,
    RawDocument,
)
from kshiraj.ingestion.pdf_extractor import PdfExtractor
from kshiraj.ingestion.source_registry import GovernmentSourceConfig, SourceRegistry
from kshiraj.knowledge.evidence_store import EvidenceStore
from kshiraj.knowledge.standards_store import StandardsStore
from kshiraj.knowledge.vector_indexer import VectorIndexer
from kshiraj.source_adapters.base import BaseSourceAdapter
from kshiraj.source_adapters.bis_adapter import BisAdapter
from kshiraj.source_adapters.bis_drafts_adapter import BisDraftsAdapter
from kshiraj.source_adapters.cppp_adapter import CpppAdapter
from kshiraj.source_adapters.qco_adapter import QcoAdapter

logger = get_logger(__name__)


class IngestionPipeline:
    """
    Unified ingestion pipeline for acquiring, parsing, and storing government intelligence.
    """

    def __init__(
        self,
        standards_store: Optional[StandardsStore] = None,
        evidence_store: Optional[EvidenceStore] = None,
        vector_indexer: Optional[VectorIndexer] = None,
        source_registry: Optional[SourceRegistry] = None,
        http_client: Optional[GovtHttpClient] = None,
        crawler: Optional[GovtCrawler] = None,
        deduplicator: Optional[DocumentDeduplicator] = None,
        incremental_tracker: Optional[IncrementalIngestionTracker] = None,
    ) -> None:
        self.standards_store = standards_store or StandardsStore()
        self.evidence_store = evidence_store or EvidenceStore()
        self.vector_indexer = vector_indexer
        self.source_registry = source_registry or SourceRegistry()
        self.http_client = http_client or GovtHttpClient()
        self.crawler = crawler or GovtCrawler(http_client=self.http_client)
        self.deduplicator = deduplicator or DocumentDeduplicator()
        self.incremental_tracker = incremental_tracker or IncrementalIngestionTracker()

        from kshiraj.ingestion.policy import PolicyEvaluator
        self.policy_evaluator = PolicyEvaluator()

        # Instantiate portal parsers
        from kshiraj.ingestion.parsers import (
            BisPortalParser,
            CpppPortalParser,
            DpiitPortalParser,
            EgazettePortalParser,
        )
        self.bis_parser = BisPortalParser()
        self.cppp_parser = CpppPortalParser()
        self.dpiit_parser = DpiitPortalParser()
        self.egazette_parser = EgazettePortalParser()

        # Instantiate existing adapters
        self.bis_adapter = BisAdapter()
        self.bis_drafts_adapter = BisDraftsAdapter()
        self.cppp_adapter = CpppAdapter()
        self.qco_adapter = QcoAdapter()

        self.html_extractor = HtmlExtractor()
        self.pdf_extractor = PdfExtractor()
        self.json_extractor = JsonExtractor()

    # ------------------------------------------------------------------
    # Single URL / Resource Ingestion
    # ------------------------------------------------------------------

    def ingest_url(
        self,
        url: str,
        source_name: Optional[str] = None,
        adapter_override: Optional[str] = None,
        force_reindex: bool = False,
    ) -> IngestionResult:
        """
        Fetch, deduplicate, adapt, and index a single URL.
        """
        t0 = time.perf_counter()
        canonical = normalize_url(url)
        if not canonical:
            return IngestionResult(
                source_url=url,
                status=IngestionStatus.FAILED,
                error_message=f"Invalid URL: {url}",
                elapsed_seconds=round(time.perf_counter() - t0, 3),
            )

        # 1. Match source configuration
        source_cfg = self.source_registry.match_source_by_url(canonical)
        effective_source_name = source_name or (source_cfg.name if source_cfg else "Government Source")
        effective_adapter = adapter_override or (source_cfg.adapter_name if source_cfg else "auto")
        source_type = source_cfg.source_type if source_cfg else EvidenceSourceType.OTHER_GOVERNMENT

        # 2. Check conditional sync headers
        headers = self.incremental_tracker.get_conditional_headers(canonical)

        # 3. Fetch resource
        try:
            fetched = self.http_client.fetch(canonical, headers=headers)
        except Exception as exc:
            self.incremental_tracker.record_sync_failure(canonical, IngestionStatus.FAILED)
            return IngestionResult(
                source_url=canonical,
                status=IngestionStatus.FAILED,
                error_message=f"Fetch failed: {exc}",
                elapsed_seconds=round(time.perf_counter() - t0, 3),
            )

        # Handle 304 Not Modified
        if fetched.status_code == 304:
            logger.info("URL %s returned 304 Not Modified. Skipping ingestion.", canonical)
            return IngestionResult(
                source_url=canonical,
                status=IngestionStatus.UNCHANGED,
                content_hash=self.deduplicator.get_hash_for_url(canonical) or "",
                elapsed_seconds=round(time.perf_counter() - t0, 3),
            )

        if fetched.status_code >= 400 or fetched.is_blocked:
            status = IngestionStatus.REQUIRES_HUMAN_VERIFICATION if fetched.requires_human_verification else IngestionStatus.FAILED
            self.incremental_tracker.record_sync_failure(canonical, status)
            return IngestionResult(
                source_url=canonical,
                status=status,
                error_message=fetched.error_message or f"HTTP {fetched.status_code}",
                elapsed_seconds=round(time.perf_counter() - t0, 3),
            )

        # 4. Deduplication & Hash evaluation
        doc_state = self.deduplicator.evaluate_document(
            url=canonical,
            content_hash=fetched.content_hash,
            source_name=effective_source_name,
        )

        if doc_state == DocumentState.UNCHANGED_DOCUMENT and not force_reindex:
            logger.info("Document at %s unchanged (hash=%s). Skipping parsing and re-indexing.", canonical, fetched.content_hash[:8])
            self.incremental_tracker.record_sync_success(
                url=canonical,
                content_hash=fetched.content_hash,
                etag=fetched.etag,
                last_modified=fetched.last_modified,
                status=IngestionStatus.UNCHANGED,
            )
            return IngestionResult(
                source_url=canonical,
                status=IngestionStatus.UNCHANGED,
                content_hash=fetched.content_hash,
                elapsed_seconds=round(time.perf_counter() - t0, 3),
            )

        # 5. Extract raw document representation
        raw_doc = self._extract_document_from_fetched(fetched, effective_source_name, source_type)

        # 6. Adapt and persist domain models
        result = self.ingest_raw_document(
            raw_doc=raw_doc,
            adapter_name=effective_adapter,
            force_reindex=force_reindex,
        )
        result.elapsed_seconds = round(time.perf_counter() - t0, 3)

        # Update incremental tracker
        self.incremental_tracker.record_sync_success(
            url=canonical,
            content_hash=fetched.content_hash,
            etag=fetched.etag,
            last_modified=fetched.last_modified,
            status=result.status,
        )

        return result

    # ------------------------------------------------------------------
    # Raw Document Ingestion & Adapter Dispatch
    # ------------------------------------------------------------------

    def ingest_raw_document(
        self,
        raw_doc: RawDocument,
        adapter_name: str = "auto",
        force_reindex: bool = False,
    ) -> IngestionResult:
        """
        Process a RawDocument through the designated SourceAdapter, stores, and vector indexer.
        """
        t0 = time.perf_counter()
        target_adapter = adapter_name.lower().strip()

        created_standards: List[Standard] = []
        created_evidence: List[Evidence] = []
        error_msg: Optional[str] = None

        try:
            # 1. BIS Standard Adapter
            if target_adapter == "bis":
                if raw_doc.raw_payload:
                    std_payloads = [raw_doc.raw_payload]
                else:
                    std_payloads = self.bis_parser.extract_multiple_standards(raw_doc)

                for payload in std_payloads:
                    std, ev_list = self.bis_adapter.parse_standard_data(payload, source_url=raw_doc.source_url)
                    created_standards.append(std)
                    created_evidence.extend(ev_list)

            # 2. BIS Drafts Adapter
            elif target_adapter == "bis_drafts":
                payload = raw_doc.raw_payload or self._create_bis_draft_payload_from_doc(raw_doc)
                std, ev_list = self.bis_drafts_adapter.parse_draft_data(payload, source_url=raw_doc.source_url)
                created_standards.append(std)
                created_evidence.extend(ev_list)

            # 3. CPPP Tender Adapter
            elif target_adapter == "cppp":
                payload = raw_doc.raw_payload or self.cppp_parser.parse_document(raw_doc)
                ev_list = self.cppp_adapter.parse_tender_data(payload, source_url=raw_doc.source_url)
                created_evidence.extend(ev_list)

            # 4. QCO Gazette Adapter
            elif target_adapter == "qco":
                if "egazette" in raw_doc.canonical_url.lower():
                    payload = raw_doc.raw_payload or self.egazette_parser.parse_document(raw_doc)
                else:
                    payload = raw_doc.raw_payload or self.dpiit_parser.parse_document(raw_doc)
                qco_meta, ev_list = self.qco_adapter.parse_qco_data(payload, source_url=raw_doc.source_url)
                created_evidence.extend(ev_list)

            # 5. Auto or Generic Government Document
            else:
                if self.bis_parser.can_handle(raw_doc):
                    payload = self.bis_parser.parse_document(raw_doc)
                    std, ev_list = self.bis_adapter.parse_standard_data(payload, source_url=raw_doc.source_url)
                    created_standards.append(std)
                    created_evidence.extend(ev_list)
                elif self.cppp_parser.can_handle(raw_doc):
                    payload = self.cppp_parser.parse_document(raw_doc)
                    ev_list = self.cppp_adapter.parse_tender_data(payload, source_url=raw_doc.source_url)
                    created_evidence.extend(ev_list)
                elif self.dpiit_parser.can_handle(raw_doc) or self.egazette_parser.can_handle(raw_doc):
                    payload = self.dpiit_parser.parse_document(raw_doc) if self.dpiit_parser.can_handle(raw_doc) else self.egazette_parser.parse_document(raw_doc)
                    qco_meta, ev_list = self.qco_adapter.parse_qco_data(payload, source_url=raw_doc.source_url)
                    created_evidence.extend(ev_list)
                else:
                    ev = Evidence(
                        source_type=raw_doc.source_type,
                        source_name=raw_doc.source_name or f"Government Document ({raw_doc.source_url})",
                        authority="Government of India",
                        url=raw_doc.source_url,
                        section=raw_doc.metadata.title or "Main Content",
                        excerpt=raw_doc.text_content[:2000] if raw_doc.text_content else raw_doc.source_name,
                        retrieval_date=raw_doc.retrieved_at,
                        confidence=0.9,
                    )
                    created_evidence.append(ev)

        except Exception as exc:
            logger.error("Adapter '%s' failed for %s: %s", target_adapter, raw_doc.source_url, exc)
            error_msg = f"Adapter parsing error: {exc}"
            return IngestionResult(
                source_url=raw_doc.source_url,
                status=IngestionStatus.FAILED,
                content_hash=raw_doc.content_hash,
                error_message=error_msg,
                elapsed_seconds=round(time.perf_counter() - t0, 3),
            )

        # Persist to Knowledge Stores
        for std in created_standards:
            self.standards_store.upsert(std)

        for ev in created_evidence:
            self.evidence_store.upsert(ev)

        # Vector Indexing via VectorIndexer
        indexed_count = 0
        if self.vector_indexer is not None:
            if created_standards:
                try:
                    indexed_count += self.vector_indexer.index_standards(created_standards)
                except Exception as v_err:
                    logger.warning("Vector indexing failed for standards: %s", v_err)

            if created_evidence:
                try:
                    indexed_count += self.vector_indexer.index_evidence(created_evidence)
                except Exception as v_err:
                    logger.warning("Vector indexing failed for evidence: %s", v_err)

        self.deduplicator.register_document(
            url=raw_doc.source_url,
            content_hash=raw_doc.content_hash,
            source_name=raw_doc.source_name,
        )

        return IngestionResult(
            source_url=raw_doc.source_url,
            status=IngestionStatus.SUCCESS,
            content_hash=raw_doc.content_hash,
            standards_created=len(created_standards),
            evidence_created=len(created_evidence),
            standard_ids=[s.id for s in created_standards],
            evidence_ids=[e.id for e in created_evidence],
            indexed_vector_count=indexed_count,
            error_message=None,
            elapsed_seconds=round(time.perf_counter() - t0, 3),
        )

    # ------------------------------------------------------------------
    # Source / Multi-Page Crawl Ingestion
    # ------------------------------------------------------------------

    def ingest_source(
        self,
        source_name: str,
        policy_override: Optional[CrawlPolicy] = None,
    ) -> CrawlResult:
        """
        Execute an end-to-end multi-page crawl and ingestion run for a registered source.
        """
        source_cfg = self.source_registry.get_source(source_name)
        if not source_cfg:
            raise SourceAdapterError(f"Source '{source_name}' not found in SourceRegistry.", code="SOURCE_NOT_FOUND")

        policy = policy_override or source_cfg.crawl_policy or CrawlPolicy()
        results: List[IngestionResult] = []

        def on_doc(raw_doc: RawDocument):
            res = self.ingest_raw_document(raw_doc, adapter_name=source_cfg.adapter_name)
            results.append(res)

        crawl_result, raw_docs = self.crawler.crawl_source(
            seed_urls=source_cfg.base_urls,
            policy=policy,
            source_name=source_cfg.name,
            source_type=source_cfg.source_type,
            on_document_acquired=on_doc,
        )

        crawl_result.ingestion_results = results
        crawl_result.standards_ingested = sum(r.standards_created for r in results)
        crawl_result.evidence_ingested = sum(r.evidence_created for r in results)
        return crawl_result

    # ------------------------------------------------------------------
    # Helper payload synthesizers from raw document text/metadata
    # ------------------------------------------------------------------

    def _extract_document_from_fetched(
        self,
        fetched: FetchedResource,
        source_name: str,
        source_type: EvidenceSourceType,
    ) -> RawDocument:
        ct = fetched.content_type.lower()
        if "application/pdf" in ct or fetched.canonical_url.lower().endswith(".pdf"):
            return self.pdf_extractor.extract_document(
                pdf_bytes=fetched.content_bytes,
                source_url=fetched.canonical_url,
                source_name=source_name,
                source_type=source_type,
            )
        elif "application/json" in ct or fetched.canonical_url.lower().endswith(".json"):
            return self.json_extractor.extract_document(
                json_data=fetched.content_bytes or fetched.text_content,
                source_url=fetched.canonical_url,
                source_name=source_name,
                source_type=source_type,
                content_hash=fetched.content_hash,
            )
        else:
            return self.html_extractor.extract_document(
                html_content=fetched.text_content,
                source_url=fetched.canonical_url,
                source_name=source_name,
                source_type=source_type,
                content_hash=fetched.content_hash,
            )

    @staticmethod
    def _create_bis_payload_from_doc(doc: RawDocument) -> Dict[str, Any]:
        """Synthesize a structured BIS dictionary payload from RawDocument text/metadata."""
        title = doc.metadata.title or "Indian Standard Document"
        is_num = "IS Unknown"
        
        # Scan for IS number pattern in title or text
        import re
        m = re.search(r"\bIS\s*(\d{2,6})\b", doc.text_content, re.IGNORECASE)
        if m:
            is_num = f"IS {m.group(1)}"
        elif "IS" in title:
            is_num = title

        return {
            "is_number": is_num,
            "title": title,
            "scope": doc.text_content[:1500],
            "status": "active",
            "source_url": doc.source_url,
        }

    @staticmethod
    def _create_bis_draft_payload_from_doc(doc: RawDocument) -> Dict[str, Any]:
        title = doc.metadata.title or "Wide Circulation Draft Standard"
        draft_num = "DRAFT Standard"
        import re
        m = re.search(r"\b(?:DRAFT|DOC|WC)\s*[:\-]?\s*(\w+[\/\-]\w+)\b", doc.text_content, re.IGNORECASE)
        if m:
            draft_num = f"DRAFT {m.group(1)}"

        return {
            "draft_number": draft_num,
            "title": title,
            "scope": doc.text_content[:1500],
            "source_url": doc.source_url,
        }

    @staticmethod
    def _create_cppp_payload_from_doc(doc: RawDocument) -> Dict[str, Any]:
        tender_id = "TENDER_NOTICE"
        import re
        m = re.search(r"\b(?:Tender\s*(?:ID|Ref|No|Reference))\s*[:\-]?\s*([\w\d_\-\/]+)\b", doc.text_content, re.IGNORECASE)
        if m:
            tender_id = m.group(1)

        return {
            "tender_id": tender_id,
            "technical_specification": doc.text_content,
            "procuring_authority": doc.metadata.author or "Central Public Procurement Portal",
            "source_url": doc.source_url,
        }

    @staticmethod
    def _create_qco_payload_from_doc(doc: RawDocument) -> Dict[str, Any]:
        so_num = "S.O. Notification"
        import re
        m = re.search(r"\bS\.O\.\s*(\d+)\s*\([A-Z]\)\b", doc.text_content, re.IGNORECASE)
        if m:
            so_num = f"S.O. {m.group(1)}(E)"

        is_num = None
        is_m = re.search(r"\bIS\s*(\d{2,6})\b", doc.text_content, re.IGNORECASE)
        if is_m:
            is_num = f"IS {is_m.group(1)}"

        return {
            "gazette_so_number": so_num,
            "is_number": is_num or "Mandatory Standards",
            "issuing_ministry": "Ministry / DPIIT",
            "excerpt": doc.text_content[:2000],
            "source_url": doc.source_url,
        }
