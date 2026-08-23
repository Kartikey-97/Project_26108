"""
kshiraj/knowledge/test_embedding_service.py

Unit tests for kshiraj.knowledge.embedding_service.EmbeddingService.
All tests use mock models and do NOT require live HuggingFace downloads or internet access.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from kshiraj.knowledge.embedding_service import EmbeddingService, EmbeddingServiceError


@pytest.fixture
def mock_transformer_model():
    """Mock SentenceTransformer object returning deterministic vectors."""
    model = MagicMock()
    model.dimension = 384

    def mock_encode(sentences, batch_size=32, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True):
        if isinstance(sentences, str):
            return [0.1] * 384
        return [[0.1 * (i + 1)] * 384 for i in range(len(sentences))]

    model.encode.side_effect = mock_encode
    return model


class TestEmbeddingService:
    """Test suite for EmbeddingService."""

    def test_single_embedding(self, mock_transformer_model):
        service = EmbeddingService(model=mock_transformer_model)
        vec = service.encode_text("Luminaires standard IS 10322")

        assert isinstance(vec, list)
        assert len(vec) == 384
        # L2 norm check
        norm = sum(x * x for x in vec) ** 0.5
        assert pytest.approx(norm, 1e-4) == 1.0

    def test_batch_embedding(self, mock_transformer_model):
        service = EmbeddingService(model=mock_transformer_model)
        texts = ["Text 1", "Text 2", "Text 3"]
        vecs = service.encode_batch(texts)

        assert isinstance(vecs, list)
        assert len(vecs) == 3
        for v in vecs:
            assert len(v) == 384
            norm = sum(x * x for x in v) ** 0.5
            assert pytest.approx(norm, 1e-4) == 1.0

    def test_empty_text_handling(self, mock_transformer_model):
        service = EmbeddingService(model=mock_transformer_model)
        empty_vec = service.encode_text("")
        ws_vec = service.encode_text("   ")

        assert empty_vec == [0.0] * 384
        assert ws_vec == [0.0] * 384

    def test_empty_batch_handling(self, mock_transformer_model):
        service = EmbeddingService(model=mock_transformer_model)
        vecs = service.encode_batch([])
        assert vecs == []

    def test_batch_with_empty_strings(self, mock_transformer_model):
        service = EmbeddingService(model=mock_transformer_model)
        vecs = service.encode_batch(["Valid text", "", "   "])
        assert len(vecs) == 3
        assert vecs[1] == [0.0] * 384
        assert vecs[2] == [0.0] * 384

    def test_dimension_property(self, mock_transformer_model):
        service = EmbeddingService(model=mock_transformer_model)
        assert service.dimension == 384

    def test_device_selection(self, mock_transformer_model):
        service = EmbeddingService(device="cpu", model=mock_transformer_model)
        assert service.device == "cpu"

    def test_model_reuse(self, mock_transformer_model):
        service = EmbeddingService(model=mock_transformer_model)
        m1 = service._get_model()
        m2 = service._get_model()
        assert m1 is m2
