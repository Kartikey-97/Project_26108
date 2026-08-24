"""
kshiraj/knowledge/test_hybrid_retrieval.py

Unit tests for kshiraj.knowledge.hybrid_retrieval.HybridRetrievalService.
Verifies fusion of lexical RetrievalService and vector VectorStore, score normalization,
deduplication, and deterministic tie-breaking.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from shared.models import Standard, StandardStatus

from kshiraj.knowledge.evidence_store import EvidenceStore
from kshiraj.knowledge.hybrid_retrieval import HybridRetrievalService
from kshiraj.knowledge.retrieval_service import RetrievalQuery, RetrievalResult
from kshiraj.knowledge.standards_store import StandardsStore


@pytest.fixture
def stores():
    std_store = StandardsStore()
    ev_store = EvidenceStore()

    s1 = Standard(id="s1", is_number="IS 10322", title="Luminaires", year=2012, status=StandardStatus.ACTIVE)
    s2 = Standard(id="s2", is_number="IS 2062", title="Steel Plates", year=2011, status=StandardStatus.ACTIVE)
    s3 = Standard(id="s3", is_number="IS 694", title="PVC Cables", year=2010, status=StandardStatus.ACTIVE)

    std_store.add(s1)
    std_store.add(s2)
    std_store.add(s3)

    return std_store, ev_store


@pytest.fixture
def mock_embedding_service():
    srv = MagicMock()
    srv.encode_text.return_value = [0.1] * 384
    srv.encode_batch.return_value = [[0.1] * 384]
    return srv


@pytest.fixture
def mock_vector_store():
    store = MagicMock()
    # Mock vector hits
    store.search_standards.return_value = [
        {"id": "s1", "score": 0.90, "payload": {"is_number": "IS 10322"}, "type": "standard"},
        {"id": "s2", "score": 0.70, "payload": {"is_number": "IS 2062"}, "type": "standard"},
    ]
    return store


class TestHybridRetrievalService:
    """Test suite for HybridRetrievalService."""

    def test_search_fusion_lexical_and_vector(self, stores, mock_embedding_service, mock_vector_store):
        std_store, ev_store = stores
        hybrid = HybridRetrievalService(
            standards_store=std_store,
            evidence_store=ev_store,
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            lexical_weight=0.4,
            vector_weight=0.6,
        )

        res = hybrid.search("Luminaires IS 10322")

        assert isinstance(res, RetrievalResult)
        assert res.total_candidates > 0
        top_cand = res.candidates[0]
        assert top_cand.standard.is_number == "IS 10322"
        assert top_cand.score > 0

    def test_empty_query_returns_zero(self, stores, mock_embedding_service, mock_vector_store):
        std_store, ev_store = stores
        hybrid = HybridRetrievalService(
            standards_store=std_store,
            evidence_store=ev_store,
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
        )

        res = hybrid.search("")
        assert res.total_candidates == 0
        assert res.candidates == []

    def test_deduplication(self, stores, mock_embedding_service, mock_vector_store):
        std_store, ev_store = stores
        hybrid = HybridRetrievalService(
            standards_store=std_store,
            evidence_store=ev_store,
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
        )

        res = hybrid.search("IS 10322")
        ids = [c.standard.id for c in res.candidates]
        assert len(ids) == len(set(ids))

    def test_top_k_truncation(self, stores, mock_embedding_service, mock_vector_store):
        std_store, ev_store = stores
        hybrid = HybridRetrievalService(
            standards_store=std_store,
            evidence_store=ev_store,
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
        )

        res = hybrid.search("IS", top_k=1)
        assert len(res.candidates) == 1
        assert res.total_candidates >= 1

    def test_index_standard_and_batch(self, stores, mock_embedding_service, mock_vector_store):
        std_store, ev_store = stores
        hybrid = HybridRetrievalService(
            standards_store=std_store,
            evidence_store=ev_store,
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
        )

        std = std_store.get_by_id("s1")
        hybrid.index_standard(std)
        assert mock_embedding_service.encode_text.called
        assert mock_vector_store.upsert_standards.called

        hybrid.index_standards_batch([std])
        assert mock_embedding_service.encode_batch.called
