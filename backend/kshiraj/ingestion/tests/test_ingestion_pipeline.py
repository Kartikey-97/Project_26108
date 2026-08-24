"""
kshiraj/ingestion/tests/test_ingestion_pipeline.py

Integration tests for the complete IngestionPipeline end-to-end flow:
Acquisition -> Extraction -> Deduplication -> Source Adapters -> Knowledge Stores -> Vector Indexer -> Qdrant.
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
from kshiraj.ingestion.source_registry import SourceRegistry
from kshiraj.knowledge.embedding_service import EmbeddingService
from kshiraj.knowledge.evidence_store import EvidenceStore
from kshiraj.knowledge.standards_store import StandardsStore
from kshiraj.knowledge.vector_indexer import VectorIndexer
from kshiraj.knowledge.vector_store import VectorStore


class DummyMockEmbeddingService:
    """Fast deterministic mock for embeddings in unit tests."""
    def __init__(self, dimension=384):
        self.dimension = dimension

    def encode_text(self, text: str):
        return [0.1] * self.dimension

    def encode_batch(self, texts):
        return [[0.1] * self.dimension for _ in texts]


class TestIngestionPipeline:

    @pytest.fixture
    def pipeline_setup(self):
        standards_store = StandardsStore()
        evidence_store = EvidenceStore()
        mock_embedder = DummyMockEmbeddingService()
        vector_store = VectorStore(location=":memory:", dimension=384)
        vector_indexer = VectorIndexer(embedding_service=mock_embedder, vector_store=vector_store)

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
        return pipeline, standards_store, evidence_store, vector_store, mock_http

    def test_ingest_bis_standard_flow(self, pipeline_setup):
        pipeline, std_store, ev_store, vec_store, mock_http = pipeline_setup

        bis_json = {
            "is_number": "IS 10322",
            "title": "Luminaires - Specification",
            "year": 2014,
            "status": "active",
            "scope": "Covers lighting requirements.",
        }
        json_bytes = json.dumps(bis_json).encode("utf-8")

        mock_http.fetch.return_value = FetchedResource(
            url="https://services.bis.gov.in/standards/10322",
            canonical_url="https://services.bis.gov.in/standards/10322",
            status_code=200,
            content_bytes=json_bytes,
            text_content=json.dumps(bis_json),
            content_type="application/json",
            content_hash="bis10322hash",
        )

        res = pipeline.ingest_url("https://services.bis.gov.in/standards/10322", adapter_override="bis")

        assert res.status_code == 200 if hasattr(res, 'status_code') else res.status == IngestionStatus.SUCCESS
        assert res.standards_created == 1
        assert res.evidence_created >= 1
        assert res.indexed_vector_count >= 2  # Standard + Evidence indexed

        # Verify Knowledge Store persistence
        stored_stds = std_store.get_by_is_number("IS 10322")
        assert len(stored_stds) == 1
        assert stored_stds[0].title == "Luminaires - Specification"

        # Verify Evidence Store persistence
        stored_evs = ev_store.get_by_source_type(EvidenceSourceType.BIS_STANDARD)
        assert len(stored_evs) >= 1

    def test_ingest_cppp_tender_flow(self, pipeline_setup):
        pipeline, std_store, ev_store, vec_store, mock_http = pipeline_setup

        cppp_json = {
            "tender_id": "2026_CPWD_99999",
            "technical_specification": "All electrical fittings must comply with IS 732.",
            "procuring_authority": "CPWD",
        }
        json_bytes = json.dumps(cppp_json).encode("utf-8")

        mock_http.fetch.return_value = FetchedResource(
            url="https://eprocure.gov.in/tenders/99999",
            canonical_url="https://eprocure.gov.in/tenders/99999",
            status_code=200,
            content_bytes=json_bytes,
            text_content=json.dumps(cppp_json),
            content_type="application/json",
            content_hash="cppp99999hash",
        )

        res = pipeline.ingest_url("https://eprocure.gov.in/tenders/99999", adapter_override="cppp")

        assert res.status == IngestionStatus.SUCCESS
        assert res.evidence_created >= 1

        stored_tenders = ev_store.get_by_source_type(EvidenceSourceType.CPPP_TENDER)
        assert len(stored_tenders) >= 1
        assert stored_tenders[0].tender_id == "2026_CPWD_99999"

    def test_deduplication_skips_unchanged_document(self, pipeline_setup):
        pipeline, std_store, ev_store, vec_store, mock_http = pipeline_setup

        payload = {"is_number": "IS 269", "title": "Portland Cement", "year": 2015}
        json_bytes = json.dumps(payload).encode("utf-8")

        mock_http.fetch.return_value = FetchedResource(
            url="https://services.bis.gov.in/standards/269",
            canonical_url="https://services.bis.gov.in/standards/269",
            status_code=200,
            content_bytes=json_bytes,
            text_content=json.dumps(payload),
            content_type="application/json",
            content_hash="cement269hash",
        )

        # 1st Ingestion -> Success
        res1 = pipeline.ingest_url("https://services.bis.gov.in/standards/269", adapter_override="bis")
        assert res1.status == IngestionStatus.SUCCESS

        # 2nd Ingestion with identical content hash -> Skips parsing & re-indexing
        res2 = pipeline.ingest_url("https://services.bis.gov.in/standards/269", adapter_override="bis")
        assert res2.status == IngestionStatus.UNCHANGED
        assert res2.standards_created == 0
        assert res2.evidence_created == 0
