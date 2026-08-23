"""
kshiraj/ingestion/tests/test_end_to_end_ingestion.py

Deterministic integration test demonstrating the complete Government Ingestion flow:
Government Data -> Policy Check -> Extraction -> Portal Parsers -> Adapters ->
Domain Models -> Knowledge Stores -> EmbeddingService (384-d) -> Qdrant -> Hybrid Retrieval.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock
import pytest

from shared.models import EvidenceSourceType, StandardStatus
from kshiraj.ingestion.deduplication import DocumentDeduplicator
from kshiraj.ingestion.http_client import GovtHttpClient
from kshiraj.ingestion.incremental import IncrementalIngestionTracker
from kshiraj.ingestion.ingestion_pipeline import IngestionPipeline
from kshiraj.ingestion.models import FetchedResource, IngestionStatus
from kshiraj.ingestion.policy import PolicyEvaluator
from kshiraj.knowledge.embedding_service import EmbeddingService
from kshiraj.knowledge.evidence_store import EvidenceStore
from kshiraj.knowledge.hybrid_retrieval import HybridRetrievalService
from kshiraj.knowledge.retrieval_service import RetrievalQuery
from kshiraj.knowledge.standards_store import StandardsStore
from kshiraj.knowledge.vector_indexer import VectorIndexer
from kshiraj.knowledge.vector_store import VectorStore


class TestEndToEndGovernmentIngestion:

    @pytest.fixture
    def full_stack_pipeline(self):
        standards_store = StandardsStore()
        evidence_store = EvidenceStore()
        
        # Real in-memory Qdrant and fast sentence transformer
        embedding_service = EmbeddingService()
        vector_store = VectorStore(location=":memory:", dimension=384)
        vector_indexer = VectorIndexer(embedding_service=embedding_service, vector_store=vector_store)

        mock_http = MagicMock(spec=GovtHttpClient)
        deduplicator = DocumentDeduplicator()
        incremental_tracker = IncrementalIngestionTracker()

        pipeline = IngestionPipeline(
            standards_store=standards_store,
            evidence_store=evidence_store,
            vector_indexer=vector_indexer,
            http_client=mock_http,
            deduplicator=deduplicator,
            incremental_tracker=incremental_tracker,
        )

        hybrid_retrieval = HybridRetrievalService(
            standards_store=standards_store,
            evidence_store=evidence_store,
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

        return pipeline, standards_store, evidence_store, vector_store, embedding_service, hybrid_retrieval, mock_http

    def test_end_to_end_bis_and_cppp_ingestion_and_semantic_hybrid_retrieval(self, full_stack_pipeline):
        (
            pipeline,
            std_store,
            ev_store,
            vec_store,
            embed_svc,
            hybrid_service,
            mock_http,
        ) = full_stack_pipeline

        # 1. Simulate BIS Portal Standard Page
        bis_html = """
        <html>
        <head><title>IS 2062 Structural Steel Specification</title></head>
        <body>
            <h1>Bureau of Indian Standards</h1>
            <p>IS 2062:2011 Hot Rolled Medium and High Tensile Structural Steel.</p>
            <p>Scope: This standard specifies requirements for steel used in structural fabrication, bridges, and general building construction.</p>
            <p>Technical Committee: CED 02. Division: Civil Engineering Division.</p>
        </body>
        </html>
        """
        bis_url = "https://www.bis.gov.in/standards/is2062"
        mock_http.fetch.return_value = FetchedResource(
            url=bis_url,
            canonical_url=bis_url,
            status_code=200,
            content_bytes=bis_html.encode("utf-8"),
            text_content=bis_html,
            content_type="text/html; charset=utf-8",
            content_hash="bis_2062_hash_v1",
        )

        # Ingest BIS Standard URL
        bis_res = pipeline.ingest_url(bis_url, adapter_override="bis")
        assert bis_res.status == IngestionStatus.SUCCESS
        assert bis_res.standards_created == 1
        assert bis_res.indexed_vector_count >= 1

        # Verify Standard Stored
        stds = std_store.get_by_is_number("IS 2062")
        assert len(stds) == 1
        assert stds[0].year == 2011
        assert "CED 02" in stds[0].technical_committee
        assert stds[0].source_url == bis_url

        # 2. Simulate CPPP Tender Notice
        cppp_json = {
            "tender_id": "2026_CPWD_STEEL_FAB_001",
            "title": "Fabrication and Erection of Structural Steel Bridge Framing",
            "procuring_authority": "Central Public Works Department (CPWD)",
            "technical_specification": "All raw structural steel sections must strictly comply with IS 2062 Grade E250. Welding must follow BIS standards.",
            "source_url": "https://eprocure.gov.in/tenders/steel_bridge_2026",
        }
        cppp_url = "https://eprocure.gov.in/tenders/steel_bridge_2026"
        mock_http.fetch.return_value = FetchedResource(
            url=cppp_url,
            canonical_url=cppp_url,
            status_code=200,
            content_bytes=json.dumps(cppp_json).encode("utf-8"),
            text_content=json.dumps(cppp_json),
            content_type="application/json",
            content_hash="cppp_steel_tender_hash",
        )

        # Ingest CPPP Tender URL
        cppp_res = pipeline.ingest_url(cppp_url, adapter_override="cppp")
        assert cppp_res.status == IngestionStatus.SUCCESS
        assert cppp_res.evidence_created >= 1

        # Verify Evidence Stored
        evidence_items = ev_store.get_by_source_type(EvidenceSourceType.CPPP_TENDER)
        assert len(evidence_items) >= 1
        assert evidence_items[0].tender_id == "2026_CPWD_STEEL_FAB_001"

        # 3. Test Semantic Query (NO exact IS number in query!)
        # Query: "steel requirements for structural fabrication"
        semantic_query = RetrievalQuery(
            query_text="steel requirements for structural fabrication",
            include_evidence=True,
            top_k=5,
        )
        retrieval_result = hybrid_service.search_standards(semantic_query)

        # 4. Verify Hybrid Retrieval found the ingested standard
        assert len(retrieval_result.candidates) >= 1
        top_match = retrieval_result.candidates[0]
        assert top_match.standard.is_number == "IS 2062"
        assert top_match.score > 0.0
        assert top_match.standard.source_url == bis_url

        # 5. Test Exact Keyword Query
        exact_query = RetrievalQuery(query_text="IS 2062", include_evidence=True, top_k=5)
        exact_result = hybrid_service.search_standards(exact_query)
        assert len(exact_result.candidates) >= 1
        assert exact_result.candidates[0].standard.is_number == "IS 2062"
        assert "IS 2062" in exact_result.candidates[0].matched_terms or exact_result.candidates[0].score > 5.0
