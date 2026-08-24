"""
kshiraj/knowledge/test_vector_store.py

Unit tests for kshiraj.knowledge.vector_store.VectorStore.
Tests use mock or in-memory client and run completely isolated without external network calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from shared.models import Evidence, EvidenceSourceType, Standard, StandardStatus

from kshiraj.knowledge.vector_store import VectorStore, _to_uuid


@pytest.fixture
def mock_qdrant_client():
    """Mock QdrantClient maintaining points in memory."""
    client = MagicMock()
    collections = {}

    def create_collection(collection_name, vectors_config=None, **kwargs):
        if collection_name not in collections:
            collections[collection_name] = []

    def upsert(collection_name, points, **kwargs):
        if collection_name not in collections:
            collections[collection_name] = []
        collections[collection_name].extend(points)

    def count(collection_name, **kwargs):
        res = MagicMock()
        res.count = len(collections.get(collection_name, []))
        return res

    def query_points(collection_name, query=None, query_filter=None, limit=10, **kwargs):
        points = collections.get(collection_name, [])
        hits = []
        for p in points[:limit]:
            hit = MagicMock()
            if isinstance(p, dict):
                hit.id = p.get("id", "1")
                hit.payload = p.get("payload", {})
            else:
                hit.id = getattr(p, "id", "1")
                hit.payload = getattr(p, "payload", {})
            hit.score = 0.95
            hits.append(hit)
        res = MagicMock()
        res.points = hits
        return res

    client.create_collection.side_effect = create_collection
    client.upsert.side_effect = upsert
    client.count.side_effect = count
    client.query_points.side_effect = query_points
    client.collection_exists.return_value = False

    return client


class TestVectorStore:
    """Test suite for VectorStore."""

    def test_stable_uuid_generation(self):
        id1 = "std-123"
        uuid1 = _to_uuid(id1)
        uuid2 = _to_uuid(id1)
        assert uuid1 == uuid2
        assert len(uuid1) == 36

    def test_collection_creation(self, mock_qdrant_client):
        store = VectorStore(client=mock_qdrant_client)
        store.create_collections_if_needed()
        assert mock_qdrant_client.create_collection.call_count == 2

    def test_upsert_and_count_standards(self, mock_qdrant_client):
        store = VectorStore(client=mock_qdrant_client)
        std = Standard(id="s1", is_number="IS 10322", title="Luminaires", status=StandardStatus.ACTIVE)
        vec = [0.1] * 384

        store.upsert_standards([std], [vec])
        assert store.count_standards() == 1

    def test_upsert_and_count_evidence(self, mock_qdrant_client):
        store = VectorStore(client=mock_qdrant_client)
        ev = Evidence(id="e1", source_type=EvidenceSourceType.BIS_STANDARD, source_name="BIS Standard", excerpt="Scope text")
        vec = [0.1] * 384

        store.upsert_evidence([ev], [vec])
        assert store.count_evidence() == 1

    def test_search_standards(self, mock_qdrant_client):
        store = VectorStore(client=mock_qdrant_client)
        std = Standard(id="s1", is_number="IS 10322", title="Luminaires", status=StandardStatus.ACTIVE)
        vec = [0.1] * 384

        store.upsert_standards([std], [vec])
        results = store.search_standards(query_vector=vec, top_k=5)

        assert len(results) == 1
        assert results[0]["id"] == "s1"
        assert results[0]["payload"]["is_number"] == "IS 10322"
        assert results[0]["type"] == "standard"

    def test_search_evidence(self, mock_qdrant_client):
        store = VectorStore(client=mock_qdrant_client)
        ev = Evidence(id="e1", source_type=EvidenceSourceType.BIS_STANDARD, source_name="BIS Standard", excerpt="Scope text")
        vec = [0.1] * 384

        store.upsert_evidence([ev], [vec])
        results = store.search_evidence(query_vector=vec, top_k=5)

        assert len(results) == 1
        assert results[0]["id"] == "e1"
        assert results[0]["type"] == "evidence"

    def test_empty_search_returns_empty(self, mock_qdrant_client):
        store = VectorStore(client=mock_qdrant_client)
        assert store.search_standards(query_vector=[]) == []
        assert store.search_evidence(query_vector=[]) == []

    def test_delete_standard(self, mock_qdrant_client):
        store = VectorStore(client=mock_qdrant_client)
        store.delete_standard("s1")
        assert mock_qdrant_client.delete.called
