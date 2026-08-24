"""
kshiraj/knowledge/vector_indexer.py

Indexing service for creating and upserting dense vector embeddings of Standard
and Evidence domain models into the Qdrant VectorStore.

Does not mutate source domain models or replace canonical stores.
"""

from __future__ import annotations

from typing import List, Optional

from shared.models import Evidence, Standard
from shared.utils import get_logger

from kshiraj.knowledge.embedding_service import EmbeddingService
from kshiraj.knowledge.evidence_store import EvidenceStore
from kshiraj.knowledge.standards_store import StandardsStore
from kshiraj.knowledge.vector_store import VectorStore

logger = get_logger(__name__)


class VectorIndexer:
    """
    Indexer for converting domain models into searchable text and upserting embeddings into Qdrant.
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStore] = None,
    ) -> None:
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    @staticmethod
    def build_standard_text(standard: Standard) -> str:
        """Construct rich searchable text representation of a Standard model."""
        parts = [standard.designation, standard.title]
        if standard.scope:
            parts.append(f"Scope: {standard.scope}")
        if standard.division_council:
            parts.append(f"Division: {standard.division_council}")
        if standard.technical_committee:
            parts.append(f"Committee: {standard.technical_committee}")
        return " | ".join(p.strip() for p in parts if p and p.strip())

    @staticmethod
    def build_evidence_text(evidence: Evidence) -> str:
        """Construct rich searchable text representation of an Evidence model."""
        parts = [evidence.source_name]
        if evidence.authority:
            parts.append(f"Authority: {evidence.authority}")
        if evidence.section:
            parts.append(f"Section: {evidence.section}")
        if evidence.excerpt:
            parts.append(f"Excerpt: {evidence.excerpt}")
        return " | ".join(p.strip() for p in parts if p and p.strip())

    def index_standards(self, standards: List[Standard]) -> int:
        """
        Batch embed and upsert a list of Standard objects into Qdrant.

        Returns
        -------
        int
            Number of standards successfully indexed.
        """
        if not standards:
            return 0

        texts = [self.build_standard_text(std) for std in standards]

        try:
            embeddings = self.embedding_service.encode_batch(texts)
            self.vector_store.upsert_standards(standards, embeddings)
            logger.info("VectorIndexer: indexed %s standards.", len(standards))
            return len(standards)
        except Exception as exc:
            logger.error("VectorIndexer error indexing standards: %s", exc)
            return 0

    def index_standards_from_store(self, standards_store: StandardsStore) -> int:
        """
        Index all Standards currently residing in a StandardsStore instance.

        Returns
        -------
        int
            Number of standards indexed.
        """
        standards = standards_store.list_all()
        return self.index_standards(standards)

    def index_evidence(self, evidence_items: List[Evidence]) -> int:
        """
        Batch embed and upsert a list of Evidence objects into Qdrant.

        Returns
        -------
        int
            Number of evidence records successfully indexed.
        """
        if not evidence_items:
            return 0

        texts = [self.build_evidence_text(ev) for ev in evidence_items]

        try:
            embeddings = self.embedding_service.encode_batch(texts)
            self.vector_store.upsert_evidence(evidence_items, embeddings)
            logger.info("VectorIndexer: indexed %s evidence records.", len(evidence_items))
            return len(evidence_items)
        except Exception as exc:
            logger.error("VectorIndexer error indexing evidence: %s", exc)
            return 0

    def index_evidence_from_store(self, evidence_store: EvidenceStore) -> int:
        """
        Index all Evidence records currently residing in an EvidenceStore instance.

        Returns
        -------
        int
            Number of evidence records indexed.
        """
        evidence_items = evidence_store.list_all()
        return self.index_evidence(evidence_items)
