"""
kartikey/orchestration/knowledge_registry.py

Singleton registry that holds the shared knowledge store instances.

This module is the bridge between Kartikey's pipeline and Kshiraj's knowledge layer.
It creates and owns the StandardsStore, EvidenceStore, and RetrievalService
instances used across the entire application.

Why a registry (not DI / FastAPI Depends):
  - The stores are stateful (in-memory dict with lock)
  - They must be shared across the pipeline BackgroundTask AND the API routes
  - FastAPI Depends creates new instances per-request, which breaks shared state
  - A module-level singleton is the correct pattern for shared in-memory state
    in a single-process FastAPI application (our MVP deployment model)

Initialization:
  - Call `initialize_knowledge_registry()` at FastAPI startup
  - This loads seed data into the stores
  - After that, `get_registry()` returns the populated instance

Production path (post-hackathon):
  - Replace in-memory stores with DB-backed implementations
  - Keep this registry — just swap the store implementations
  - The pipeline and API routes don't need to change
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.utils import get_logger

logger = get_logger(__name__)


@dataclass
class KnowledgeRegistry:
    """
    Holds singleton instances of the knowledge layer components.
    All fields are set during initialization and are read-only after that.
    """
    standards_store: object   # StandardsStore
    evidence_store: object    # EvidenceStore
    retrieval_service: object # RetrievalService


# Module-level singleton — None until initialize_knowledge_registry() is called
_registry: KnowledgeRegistry | None = None


def get_registry() -> KnowledgeRegistry:
    """Return the initialized knowledge registry."""
    if _registry is None:
        raise RuntimeError(
            "Knowledge registry has not been initialized. "
            "Call initialize_knowledge_registry() at application startup."
        )
    return _registry


def initialize_knowledge_registry() -> KnowledgeRegistry:
    """
    Initialize the knowledge registry with empty stores and wire up the retrieval service.

    Called once at FastAPI startup (see kartikey/api/main.py).
    After this call, get_registry() returns the populated registry.
    """
    global _registry

    from kshiraj.knowledge.standards_store import StandardsStore
    from kshiraj.knowledge.evidence_store import EvidenceStore
    from kshiraj.knowledge.retrieval_service import RetrievalService

    standards_store = StandardsStore()
    evidence_store = EvidenceStore()
    retrieval_service = RetrievalService(
        standards_store=standards_store,
        evidence_store=evidence_store,
    )

    _registry = KnowledgeRegistry(
        standards_store=standards_store,
        evidence_store=evidence_store,
        retrieval_service=retrieval_service,
    )

    logger.info("Knowledge registry initialized (empty stores).")
    return _registry
