"""
kartikey/orchestration/pipeline.py

Analysis pipeline — the state machine that coordinates the full workflow.

State transitions:
    queued → extracting → retrieving → analyzing → enriching → completed
                                                              ↘ partially_completed
                                                              ↘ failed

This module is invoked as a FastAPI BackgroundTask (no Celery/Redis for MVP).
Each step calls into the appropriate subsystem:

  _step_extract   → kartikey/document_processing + AI/ML requirement extraction
  _step_retrieve  → kshiraj/knowledge/retrieval_service (called via interface)
  _step_analyze   → kshiraj/aiml_client (called via interface)
  _step_enrich    → kshiraj/enrichment + kartikey/analysis/findings

Steps that depend on Kshiraj's subsystems are currently stubs.
They are wired in Step 7 (Source Unification) once both sides are ready.

IMPORTANT:
  The pipeline mutates the Analysis object in the shared store.
  The GET /analyses/{id} endpoint reads from the same store.
  This is safe in single-process uvicorn (the default for MVP).
  If multi-worker deployment is needed later, replace the in-memory
  store with a database-backed approach.
"""

from __future__ import annotations

import asyncio
import traceback
from typing import TYPE_CHECKING

from shared.models import Analysis, AnalysisStatus, InputType, Standard, StandardStatus
from shared.utils import AnalysisError, get_logger, utcnow

from kshiraj.knowledge.evidence_store import EvidenceStore
from kshiraj.knowledge.requirement_extractor import extract_and_normalize
from kshiraj.knowledge.retrieval_service import RetrievalQuery, RetrievalService
from kshiraj.knowledge.standards_store import StandardsStore

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)

# Shared module-level store instances for candidate retrieval
_standards_store = StandardsStore()
_evidence_store = EvidenceStore()


# ===========================================================================
# Entry point — called by FastAPI BackgroundTasks
# ===========================================================================

async def run_analysis_pipeline(
    analysis_id: str,
    store: dict[str, Analysis],
) -> None:
    """
    Coordinate the full analysis pipeline for one analysis job.

    Parameters
    ----------
    analysis_id:
        The ID of the analysis to run.
    store:
        Shared in-memory dict of analyses (keyed by analysis_id).
        Mutated in place as the pipeline progresses.
    """
    analysis = store.get(analysis_id)
    if not analysis:
        logger.error("Pipeline started for unknown analysis_id=%s — aborting.", analysis_id)
        return

    logger.info("Pipeline started: analysis_id=%s input_type=%s", analysis_id, analysis.input_type)

    try:
        # ----------------------------------------------------------------
        # Step 1: Extract text and requirements
        # ----------------------------------------------------------------
        _transition(analysis, AnalysisStatus.EXTRACTING)
        extracted_text = await _step_extract(analysis)

        # ----------------------------------------------------------------
        # Step 2: Retrieve relevant standards from knowledge base
        # ----------------------------------------------------------------
        _transition(analysis, AnalysisStatus.RETRIEVING)
        retrieved_standards = await _step_retrieve(analysis, extracted_text)

        # ----------------------------------------------------------------
        # Step 3: AI/ML analysis
        # ----------------------------------------------------------------
        _transition(analysis, AnalysisStatus.ANALYZING)
        aiml_response = await _step_analyze(analysis, extracted_text, retrieved_standards)

        # ----------------------------------------------------------------
        # Step 4: Enrich — version checks, cross-refs, QCO, compliance
        # ----------------------------------------------------------------
        _transition(analysis, AnalysisStatus.ENRICHING)
        await _step_enrich(analysis, aiml_response)

        # ----------------------------------------------------------------
        # Done
        # ----------------------------------------------------------------
        analysis.total_requirements = len(analysis.requirements)
        analysis.issues_found = sum(
            1 for f in analysis.findings
            if f.verdict.value not in ("justified",)
        )
        _transition(analysis, AnalysisStatus.COMPLETED)
        logger.info(
            "Pipeline completed: analysis_id=%s requirements=%d issues=%d",
            analysis_id,
            analysis.total_requirements,
            analysis.issues_found,
        )

    except AnalysisError as exc:
        logger.error("Pipeline failed [%s]: %s", exc.code, exc.message)
        analysis.error_message = f"[{exc.code}] {exc.message}"
        _transition(analysis, AnalysisStatus.FAILED)

    except Exception as exc:  # noqa: BLE001
        # Catch-all so the background task never crashes silently
        logger.error(
            "Pipeline unexpected failure for analysis_id=%s:\n%s",
            analysis_id,
            traceback.format_exc(),
        )
        analysis.error_message = f"Unexpected error: {exc}"
        _transition(analysis, AnalysisStatus.FAILED)


# ===========================================================================
# Pipeline steps
# ===========================================================================

async def _step_extract(analysis: Analysis) -> str:
    """
    Extract plain text from the input and pull out structured requirements.

    For TEXT input: the raw_text is used directly.
    For DOCUMENT input: text is loaded from storage (already extracted during upload).

    Structured requirements are extracted and normalized via
    `kshiraj.knowledge.requirement_extractor` and stored on `analysis.requirements`.
    """
    if analysis.input_type == InputType.TEXT:
        if not analysis.raw_text:
            raise AnalysisError(
                "Analysis has input_type=TEXT but raw_text is empty.",
                code="MISSING_INPUT",
            )
        extracted_text = analysis.raw_text
        logger.debug("_step_extract: using raw_text (%d chars)", len(extracted_text))

    elif analysis.input_type == InputType.DOCUMENT:
        if not analysis.document_id:
            raise AnalysisError(
                "Analysis has input_type=DOCUMENT but document_id is missing.",
                code="MISSING_DOCUMENT_ID",
            )
        from kartikey.document_processing.storage import get_extracted_text
        extracted_text = get_extracted_text(analysis.document_id)
        if not extracted_text:
            raise AnalysisError(
                f"No extracted text found for document_id={analysis.document_id}. "
                "Ensure the document was uploaded and extracted successfully.",
                code="NO_EXTRACTED_TEXT",
            )
        logger.debug(
            "_step_extract: loaded document text (%d chars) for document_id=%s",
            len(extracted_text),
            analysis.document_id,
        )
    else:
        raise AnalysisError(
            f"Unknown input_type: {analysis.input_type}",
            code="INVALID_INPUT_TYPE",
        )

    # Perform requirement extraction and normalization
    requirements = extract_and_normalize(extracted_text, analysis.id)
    analysis.requirements = requirements
    analysis.total_requirements = len(requirements)

    logger.info(
        "_step_extract: text ready (%d chars), extracted %d requirement(s) for analysis_id=%s",
        len(extracted_text),
        len(requirements),
        analysis.id,
    )

    return extracted_text


async def _step_retrieve(analysis: Analysis, extracted_text: str) -> list[Standard]:
    """
    Search the knowledge base for standards relevant to the extracted requirements.
    Uses `kshiraj.knowledge.retrieval_service.RetrievalService`.
    """
    await asyncio.sleep(0)  # yield control

    service = RetrievalService(
        standards_store=_standards_store,
        evidence_store=_evidence_store,
    )

    retrieved_standards: list[Standard] = []
    seen_ids: set[str] = set()

    if analysis.requirements:
        for req in analysis.requirements:
            query_text = (req.normalized_text or req.text).strip()
            if req.is_reference and req.is_reference not in query_text:
                query_text = f"{req.is_reference} {query_text}"

            q = RetrievalQuery(
                query_text=query_text,
                status_filter=[
                    StandardStatus.ACTIVE,
                    StandardStatus.REAFFIRMED,
                    StandardStatus.UNDER_REVISION,
                ],
                include_evidence=True,
                top_k=5,
            )
            res = service.search_standards(q)
            for cand in res.candidates:
                if cand.standard.id not in seen_ids:
                    seen_ids.add(cand.standard.id)
                    retrieved_standards.append(cand.standard)
    else:
        # Fallback to direct query on extracted_text if no requirements extracted
        q = RetrievalQuery(
            query_text=extracted_text,
            status_filter=[
                StandardStatus.ACTIVE,
                StandardStatus.REAFFIRMED,
                StandardStatus.UNDER_REVISION,
            ],
            include_evidence=True,
            top_k=10,
        )
        res = service.search_standards(q)
        for cand in res.candidates:
            if cand.standard.id not in seen_ids:
                seen_ids.add(cand.standard.id)
                retrieved_standards.append(cand.standard)

    logger.info(
        "_step_retrieve: retrieved %d unique candidate standard(s) for analysis_id=%s",
        len(retrieved_standards),
        analysis.id,
    )

    return retrieved_standards


async def _step_analyze(
    analysis: Analysis,
    extracted_text: str,
    retrieved_standards: list,
) -> object:
    """
    Send requirements + retrieved standards to the AI/ML component.

    TODO(Step 6): Wire kshiraj/aiml_client/client here.
    Interface: aiml_client.run_analysis(AimlRequest) → AimlResponse
    """
    await asyncio.sleep(0)
    logger.info(
        "_step_analyze: stub — AI/ML client will be wired in Step 6. "
        "analysis_id=%s",
        analysis.id,
    )
    return None   # returns AimlResponse once wired


async def _step_enrich(analysis: Analysis, aiml_response: object) -> None:
    """
    Enrich findings with version intelligence, cross-references, and QCO data.
    Then assemble final Finding objects with full evidence.

    TODO(Step 7): Wire kshiraj/enrichment + kartikey/analysis/findings here.
    """
    await asyncio.sleep(0)
    logger.info(
        "_step_enrich: stub — enrichment + findings assembly will be wired in Step 7. "
        "analysis_id=%s",
        analysis.id,
    )


# ===========================================================================
# Internal helpers
# ===========================================================================

def _transition(analysis: Analysis, new_status: AnalysisStatus) -> None:
    """Update analysis status and timestamp."""
    analysis.status = new_status
    analysis.updated_at = utcnow()
    logger.info("Analysis %s → %s", analysis.id, new_status.value)
