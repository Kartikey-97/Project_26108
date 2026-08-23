"""
kshiraj/knowledge/embedding_service.py

Embedding service for semantic vector generation using SentenceTransformers.
Default model: BAAI/bge-small-en-v1.5 (384-dimensional dense vectors).

Handles single/batch text encoding, L2 normalization for cosine similarity,
and dependency isolation for test environments.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional

from shared.utils import AppError, get_logger

logger = get_logger(__name__)


class EmbeddingServiceError(AppError):
    """Raised when embedding generation or model loading fails."""

    def __init__(self, message: str, code: str = "EMBEDDING_ERROR") -> None:
        super().__init__(message, code=code)


class EmbeddingService:
    """
    Service wrapper around SentenceTransformer models for semantic embedding generation.
    """

    DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"
    DEFAULT_DIMENSION = 384

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: str = "auto",
        batch_size: int = 32,
        model: Optional[Any] = None,
    ) -> None:
        """
        Initialize the embedding service.

        Parameters
        ----------
        model_name:
            Name or path of the HuggingFace model.
        device:
            Target compute device ('cpu', 'mps', 'cuda', or 'auto').
        batch_size:
            Batch size for vector encoding.
        model:
            Optional pre-initialized or mock model object (useful for offline unit testing).
        """
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self._model = model
        self._dimension = self.DEFAULT_DIMENSION if model is None else getattr(model, "dimension", self.DEFAULT_DIMENSION)

    @property
    def dimension(self) -> int:
        """Return the vector dimensionality of the embedding model."""
        return self._dimension

    def _get_model(self) -> Any:
        """Lazy load the SentenceTransformer model if not already provided."""
        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            logger.error("sentence-transformers package is not installed.")
            raise EmbeddingServiceError(
                "The 'sentence-transformers' package is required for vector embeddings. "
                "Install it using `pip install sentence-transformers`.",
                code="DEPENDENCY_MISSING",
            ) from exc

        try:
            logger.info("Loading SentenceTransformer model '%s' on device '%s'...", self.model_name, self.device)
            target_device = None if self.device == "auto" else self.device
            self._model = SentenceTransformer(self.model_name, device=target_device)
            # Try to get dimension from model if available
            if hasattr(self._model, "get_embedding_dimension"):
                self._dimension = int(self._model.get_embedding_dimension())
            elif hasattr(self._model, "get_sentence_embedding_dimension"):
                self._dimension = int(self._model.get_sentence_embedding_dimension())
            return self._model
        except Exception as exc:
            logger.error("Failed to load SentenceTransformer model '%s': %s", self.model_name, exc)
            raise EmbeddingServiceError(
                f"Failed to initialize embedding model '{self.model_name}': {exc}",
                code="MODEL_LOAD_FAILED",
            ) from exc

    def _normalize_vector(self, vec: List[float]) -> List[float]:
        """L2 normalize a 1D vector."""
        sq_sum = sum(v * v for v in vec)
        norm = math.sqrt(sq_sum)
        if norm < 1e-12:
            return [0.0] * len(vec)
        return [v / norm for v in vec]

    def encode_text(self, text: str) -> List[float]:
        """
        Generate a normalized embedding vector for a single text string.

        Parameters
        ----------
        text:
            Input text to embed.

        Returns
        -------
        List[float]
            Normalized embedding vector.
        """
        if not text or not text.strip():
            return [0.0] * self.dimension

        model = self._get_model()

        try:
            raw_embedding = model.encode(
                text.strip(),
                batch_size=1,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            if hasattr(raw_embedding, "tolist"):
                vec = raw_embedding.tolist()
            else:
                vec = list(raw_embedding)

            if vec and isinstance(vec[0], list):
                vec = vec[0]

            return self._normalize_vector([float(x) for x in vec])
        except Exception as exc:
            logger.error("Error encoding text snippet: %s", exc)
            raise EmbeddingServiceError(f"Failed to encode text: {exc}") from exc

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate normalized embedding vectors for a batch of text strings.

        Parameters
        ----------
        texts:
            List of input text strings.

        Returns
        -------
        List[List[float]]
            List of normalized embedding vectors.
        """
        if not texts:
            return []

        cleaned_texts = [t.strip() if t and t.strip() else "" for t in texts]
        non_empty_indices = [i for i, t in enumerate(cleaned_texts) if t]

        results: List[List[float]] = [[0.0] * self.dimension for _ in texts]
        if not non_empty_indices:
            return results

        non_empty_texts = [cleaned_texts[i] for i in non_empty_indices]
        model = self._get_model()

        try:
            raw_embeddings = model.encode(
                non_empty_texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            if hasattr(raw_embeddings, "tolist"):
                vec_list = raw_embeddings.tolist()
            else:
                vec_list = [list(v) for v in raw_embeddings]

            for original_idx, raw_vec in zip(non_empty_indices, vec_list):
                norm_vec = self._normalize_vector([float(x) for x in raw_vec])
                results[original_idx] = norm_vec

            return results
        except Exception as exc:
            logger.error("Error encoding batch of %s items: %s", len(texts), exc)
            raise EmbeddingServiceError(f"Failed to encode text batch: {exc}") from exc
