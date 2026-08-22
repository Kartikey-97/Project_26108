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

from shared.models import Analysis, AnalysisStatus, InputType
from shared.utils import AnalysisError, get_logger, utcnow

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


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

    Requirement extraction (AI/ML) is wired in Step 5.
    For now, text is returned as-is so the pipeline can proceed end-to-end.
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

    # TODO(Step 5): Call AI/ML requirement extractor here.
    # For now, log that extraction is a stub.
    logger.info(
        "_step_extract: text ready (%d chars). "
        "Requirement extraction AI/ML will be wired in Step 5.",
        len(extracted_text),
    )

    return extracted_text


async def _step_retrieve(analysis: Analysis, extracted_text: str) -> list:
    """
    Search the knowledge base for standards relevant to the extracted text.

    TODO(Step 7): Wire kshiraj/knowledge/retrieval_service here.
    Interface: retrieval_service.search_standards(query, filters, top_k)
    """
    await asyncio.sleep(0)  # yield control (non-blocking stub)
    logger.info(
        "_step_retrieve: stub — knowledge retrieval will be wired in Step 7. "
        "analysis_id=%s",
        analysis.id,
    )
    return []   # returns list[Standard] once wired


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
