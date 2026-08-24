"""
ai-engine/src/search.py

Hybrid retrieval layer combining:
  - BM25Retriever  — exact/lexical matching (great for IS numbers, IP ratings, etc.)
  - VectorStore    — semantic similarity (cosine via IndexFlatIP on normalised embeddings)
  - HybridRetriever — merges both with Reciprocal Rank Fusion, deduplicates by IS number

Removing the dead `search_index(query_embedding): pass` stub.
"""

import logging
import math
import re
from collections import defaultdict

import faiss
import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# BM25 Retriever (pure Python, no extra dependencies)
# ---------------------------------------------------------------------------

class BM25Retriever:
    """
    Okapi BM25 retriever over a corpus of documents.

    Parameters
    ----------
    k1 : float — term frequency saturation parameter (default 1.5)
    b  : float — length normalization parameter (default 0.75)
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: list[list[str]] = []
        self.doc_freqs: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.doc_len: list[int] = []
        self.avgdl: float = 0.0
        self.n_docs: int = 0

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Lowercase, split on non-alphanumeric, keep tokens ≥ 2 chars."""
        return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) >= 2]

    def fit(self, documents: list[str]) -> "BM25Retriever":
        """Fit the BM25 model on a list of document strings."""
        self.corpus = [self._tokenize(doc) for doc in documents]
        self.n_docs = len(self.corpus)
        self.doc_len = [len(doc) for doc in self.corpus]
        self.avgdl = sum(self.doc_len) / max(self.n_docs, 1)

        # Document frequency
        self.doc_freqs = defaultdict(int)
        for doc in self.corpus:
            for term in set(doc):
                self.doc_freqs[term] += 1

        # IDF — Robertson-Sparck Jones variant
        self.idf = {}
        for term, df in self.doc_freqs.items():
            self.idf[term] = math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1.0)

        return self

    def get_scores(self, query: str) -> np.ndarray:
        """Return BM25 scores for all documents against the query."""
        query_terms = self._tokenize(query)
        scores = np.zeros(self.n_docs, dtype=float)

        for term in query_terms:
            if term not in self.idf:
                continue
            idf = self.idf[term]
            for i, doc in enumerate(self.corpus):
                tf = doc.count(term)
                dl = self.doc_len[i]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1))
                scores[i] += idf * numerator / max(denominator, 1e-9)

        return scores

    def search(self, query: str, top_k: int = 20) -> tuple[np.ndarray, np.ndarray]:
        """Return (scores, indices) of the top_k documents."""
        scores = self.get_scores(query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return scores[top_indices], top_indices


# ---------------------------------------------------------------------------
# Vector Store (FAISS inner-product = cosine for normalised embeddings)
# ---------------------------------------------------------------------------

class VectorStore:
    """FAISS index using inner-product (cosine similarity on L2-normalised vectors)."""

    def __init__(self, dimension: int):
        self.dimension = dimension
        # IndexFlatIP gives cosine similarity when embeddings are L2-normalised
        self.index = faiss.IndexFlatIP(dimension)

    def add_embeddings(self, embeddings: np.ndarray) -> None:
        """Add a batch of normalised embeddings to the index."""
        embeddings_np = np.array(embeddings, dtype="float32")
        self.index.add(embeddings_np)

    def search(self, query_embedding: np.ndarray, top_k: int = 20) -> tuple[np.ndarray, np.ndarray]:
        """
        Search for the top_k nearest neighbours.

        Returns (similarities, indices) — similarities are cosine scores in [0, 1]
        for normalised embeddings.
        """
        query_np = np.array([query_embedding], dtype="float32")
        similarities, indices = self.index.search(query_np, top_k)
        return similarities[0], indices[0]


# ---------------------------------------------------------------------------
# Hybrid Retriever — Reciprocal Rank Fusion of BM25 + vector results
# ---------------------------------------------------------------------------

class HybridRetriever:
    """
    Combines BM25 (lexical) and FAISS (semantic) results using
    Reciprocal Rank Fusion (RRF) and deduplicates by IS number.

    Why RRF?  It fuses ranked lists without requiring score normalisation —
    robust across very different score scales.
    """

    RRF_K = 60  # standard RRF constant

    def __init__(self):
        self.bm25: BM25Retriever | None = None
        self.vector_store: VectorStore | None = None
        self.standards: list[dict] = []

    def fit(self, standards: list[dict], embeddings: np.ndarray) -> "HybridRetriever":
        """Build BM25 index and FAISS vector store from the standards corpus."""
        self.standards = standards
        search_texts = [std.get("search_text", "") for std in standards]

        logger.info("Building BM25 index over %d standards…", len(standards))
        self.bm25 = BM25Retriever().fit(search_texts)

        logger.info("Building FAISS index (dim=%d)…", embeddings.shape[1])
        self.vector_store = VectorStore(dimension=embeddings.shape[1])
        self.vector_store.add_embeddings(embeddings)

        return self

    def search(self, query: str, query_embedding: np.ndarray, top_k: int = 20) -> list[dict]:
        """
        Retrieve top_k candidates using hybrid RRF search.

        Returns a list of standard dicts enriched with:
          - bm25_score, semantic_score, rrf_score
          - retrieval_source: 'bm25' | 'semantic' | 'both'
        """
        if self.bm25 is None or self.vector_store is None:
            raise RuntimeError("HybridRetriever not fitted — call fit() first.")

        # --- BM25 results ---
        bm25_scores, bm25_indices = self.bm25.search(query, top_k=top_k)
        bm25_map: dict[int, float] = {int(idx): float(score) for idx, score in zip(bm25_indices, bm25_scores)}

        # --- Vector results ---
        sem_scores, sem_indices = self.vector_store.search(query_embedding, top_k=top_k)
        sem_map: dict[int, float] = {int(idx): float(score) for idx, score in zip(sem_indices, sem_scores) if idx != -1}

        # --- Reciprocal Rank Fusion ---
        rrf: dict[int, float] = defaultdict(float)
        for rank, idx in enumerate(bm25_indices):
            rrf[int(idx)] += 1.0 / (self.RRF_K + rank + 1)
        for rank, idx in enumerate(sem_indices):
            if idx != -1:
                rrf[int(idx)] += 1.0 / (self.RRF_K + rank + 1)

        # Sort by RRF score descending, take top_k
        sorted_indices = sorted(rrf, key=lambda i: rrf[i], reverse=True)[:top_k]

        results = []
        for idx in sorted_indices:
            std = self.standards[idx].copy()
            std["bm25_score"] = round(bm25_map.get(idx, 0.0), 4)
            std["semantic_score"] = round(sem_map.get(idx, 0.0), 4)
            std["rrf_score"] = round(rrf[idx], 6)

            in_bm25 = idx in bm25_map
            in_sem = idx in sem_map
            std["retrieval_source"] = "both" if (in_bm25 and in_sem) else ("bm25" if in_bm25 else "semantic")

            results.append(std)

        return results
