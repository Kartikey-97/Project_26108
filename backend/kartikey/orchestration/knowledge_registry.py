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
    retrieval_mode: str = "lexical"
    retrieval_reason: str | None = None


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

    import os
    import json
    from datetime import date
    from shared.models import Standard, StandardStatus
    from kshiraj.knowledge.standards_store import StandardsStore
    from kshiraj.knowledge.evidence_store import EvidenceStore
    from kshiraj.knowledge.retrieval_service import RetrievalService
    from kshiraj.knowledge.embedding_service import EmbeddingService
    from kshiraj.knowledge.vector_store import VectorStore
    from kshiraj.knowledge.hybrid_retrieval import HybridRetrievalService
    from shared.config import settings

    standards_store = StandardsStore()
    evidence_store = EvidenceStore()
    
    # 1. Load the dataset
    dataset_path = os.path.join(os.path.dirname(__file__), "../../shared/bis_full_catalog_1015.json")
    standards_list = []
    
    if os.path.exists(dataset_path):
        logger.info(f"Loading BIS dataset from {dataset_path}")
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                # Map JSON fields to Standard model
                raw = item.get("raw_record", item)
                source_status = str(item.get("status", "")).casefold()
                status = {
                    "active": StandardStatus.ACTIVE,
                    "reaffirmed": StandardStatus.REAFFIRMED,
                    "superseded": StandardStatus.SUPERSEDED,
                    "withdrawn": StandardStatus.WITHDRAWN,
                }.get(source_status, StandardStatus.UNKNOWN)
                std = Standard(
                    is_number=item.get("normalized_is_number", item.get("is_number", "")),
                    year=item.get("edition_year", item.get("year")),
                    title=item.get("clean_title", item.get("title", "")),
                    scope=raw.get("scope", "") or "",
                    status=status,
                    source_url="https://standardsbis.gov.in",
                    qco_notified=False,
                    retrieved_at=date.today()
                )
                
                # --- DEMO ENRICHMENT ---
                # Provide rich mock data for key standards to make the comparison UI look great
                is_num_clean = std.is_number.upper()
                if "IS 2274" in is_num_clean:
                    std.demo_operating_voltage = "230V / 400V (Exceeding 650 Volts)"
                    std.demo_ip_rating = "Not Applicable (Wiring Code)"
                    std.demo_surge_protection = "Not Stated"
                    std.demo_thermal_dissipation = "Ambient 45°C rating"
                    std.demo_test_methods = "IS 2274 Appendix A"
                    std.qco_notified = False
                elif "IS 13140" in is_num_clean:
                    std.demo_operating_voltage = "220V / 240V AC"
                    std.demo_ip_rating = "IP20 Minimum"
                    std.demo_surge_protection = "1.5 kV / 2.5 kV"
                    std.demo_thermal_dissipation = "Max Tj = 125°C"
                    std.demo_test_methods = "CISPR 15 / IEC 61000-3-2"
                    std.qco_notified = False
                elif "IS 10322" in is_num_clean:
                    std.demo_operating_voltage = "140V - 270V AC, 50Hz"
                    std.demo_ip_rating = "IP 66 for optical/driver"
                    std.demo_surge_protection = "External 10 kV SPD"
                    std.demo_thermal_dissipation = "Die-cast ADC12, Tj < 85°C"
                    std.demo_test_methods = "IS 10322 (Part 5/Sec 3)"
                    std.qco_notified = True
                elif "IS 15885" in is_num_clean:
                    std.demo_operating_voltage = "90V - 300V AC"
                    std.demo_ip_rating = "IP20 Minimum (Driver only)"
                    std.demo_surge_protection = "Built-in 4 kV"
                    std.demo_thermal_dissipation = "Tc max 85°C"
                    std.demo_test_methods = "IS 15885 (Part 2/Sec 13)"
                    std.qco_notified = True
                elif "IS 16107" in is_num_clean:
                    std.demo_operating_voltage = "140V - 270V AC"
                    std.demo_ip_rating = "IP 65 / IP 66"
                    std.demo_surge_protection = "10 kV external SPD"
                    std.demo_thermal_dissipation = "LM 79 / LM 80 compliant"
                    std.demo_test_methods = "IS 16107 Part 2"
                    std.qco_notified = True
                elif "IS 2062" in is_num_clean:
                    std.demo_operating_voltage = "Not Applicable (Steel)"
                    std.demo_ip_rating = "Not Applicable"
                    std.demo_surge_protection = "Not Applicable"
                    std.demo_thermal_dissipation = "Hot Rolled 250 MPa min"
                    std.demo_test_methods = "IS 1608 / IS 1599"
                    std.qco_notified = True

                standards_list.append(std)
                standards_store.add(std)
        logger.info(f"Loaded {len(standards_list)} standards into StandardsStore.")
    else:
        logger.warning(f"BIS dataset not found at {dataset_path}")

    # 2. Initialize Lexical Retrieval
    lexical_service = RetrievalService(
        standards_store=standards_store,
        evidence_store=evidence_store,
    )

    # 3. Initialize semantic retrieval when its optional runtime is available.
    # Lexical retrieval is already a complete fallback and must keep the API
    # bootable when Qdrant, sentence-transformers, or model assets are absent.
    retrieval_service = lexical_service
    retrieval_mode = "lexical"
    retrieval_reason = "Semantic retrieval is not initialized."
    if settings.semantic_retrieval_enabled:
      try:
        embedding_service = EmbeddingService(model_name="BAAI/bge-small-en-v1.5")
        vector_store = VectorStore(dimension=embedding_service.dimension)

        if standards_list:
            logger.info("Indexing standards in VectorStore (this may take a few seconds)...")
            vector_store.create_collections_if_needed()

            batch_size = 100
            for i in range(0, len(standards_list), batch_size):
                batch = standards_list[i:i + batch_size]
                texts = [f"{s.is_number} {s.title} {s.scope}" for s in batch]
                embeddings = embedding_service.encode_batch(texts)
                vector_store.upsert_standards(batch, embeddings)
            logger.info("VectorStore indexing complete.")

        retrieval_service = HybridRetrievalService(
            standards_store=standards_store,
            evidence_store=evidence_store,
            lexical_service=lexical_service,
            embedding_service=embedding_service,
            vector_store=vector_store,
            lexical_weight=0.4,
            vector_weight=0.6,
        )
        retrieval_mode = "hybrid"
        retrieval_reason = None
      except Exception as exc:
        logger.warning(
            "Semantic retrieval is unavailable (%s); using lexical retrieval.",
            exc,
        )
        retrieval_reason = str(exc)
    else:
        retrieval_reason = "Semantic retrieval is disabled; set SEMANTIC_RETRIEVAL_ENABLED=true after preparing the embedding model."

    _registry = KnowledgeRegistry(
        standards_store=standards_store,
        evidence_store=evidence_store,
        retrieval_service=retrieval_service,
        retrieval_mode=retrieval_mode,
        retrieval_reason=retrieval_reason,
    )

    logger.info("Knowledge registry initialized.")
    return _registry
