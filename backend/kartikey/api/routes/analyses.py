"""
kartikey/api/routes/analyses.py

POST /api/v1/analyses      — create a new analysis job
GET  /api/v1/analyses/{id} — poll status + retrieve results

Design:
  - POST returns 202 Accepted immediately with analysis_id.
    The analysis runs as a FastAPI BackgroundTask.
  - GET returns the current state at any lifecycle stage.
    Frontend polls this every few seconds until status is "completed" or "failed".
  - The in-memory store (_analyses dict) is the MVP persistence layer.
    It will be replaced with database-backed storage once the DB layer is wired.

Status lifecycle:
  queued → extracting → retrieving → analyzing → enriching → completed
                                                            ↘ partially_completed
                                                            ↘ failed
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from kartikey.orchestration.pipeline import run_analysis_pipeline
from kartikey.persistence.analysis_repository import AnalysisRepository
from shared.contracts import AnalysisResponse, CreateAnalysisRequest
from shared.models import Analysis, AnalysisStatus, InputType
from shared.config import settings
from shared.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/analyses", tags=["analyses"])

# ---------------------------------------------------------------------------
# In-memory store (MVP)
# Keyed by analysis_id → Analysis object.
# Safe for single-process uvicorn. Replace with DB queries in later step.
# ---------------------------------------------------------------------------
_analyses: dict[str, Analysis] = {}
repository = AnalysisRepository(settings.analysis_database_path)


async def initialize_persistence() -> None:
    """Restore saved analyses so dashboard and history survive restarts."""
    await repository.initialize()
    for analysis in await repository.list():
        _analyses[analysis.id] = analysis


# ===========================================================================
# POST /api/v1/analyses
# ===========================================================================

@router.post("", status_code=202)
async def create_analysis(
    body: CreateAnalysisRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Create a new procurement analysis.

    Accepts either:
      - { "input_type": "text",     "text": "<tender description>" }
      - { "input_type": "document", "document_id": "<id from /documents/upload>" }

    Returns 202 Accepted with analysis_id.
    Poll GET /api/v1/analyses/{id} for progress and results.

    Errors:
      400 — missing required field for the given input_type
    """
    # ----------------------------------------------------------------
    # Validate required fields per input type
    # ----------------------------------------------------------------
    if body.input_type == InputType.TEXT:
        if not body.text or not body.text.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "MISSING_TEXT",
                    "message": "'text' is required and must not be empty when input_type is 'text'.",
                },
            )

    elif body.input_type == InputType.DOCUMENT:
        if not body.document_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "MISSING_DOCUMENT_ID",
                    "message": "'document_id' is required when input_type is 'document'. "
                               "Upload a document first via POST /api/v1/documents/upload.",
                },
            )

    # ----------------------------------------------------------------
    # Create analysis object
    # ----------------------------------------------------------------
    analysis = Analysis(
        input_type=body.input_type,
        raw_text=body.text,
        document_id=body.document_id,
        tender_id=body.tender_id,
        tender_title=body.tender_title,
        status=AnalysisStatus.QUEUED,
        metadata=body.metadata,
    )
    _analyses[analysis.id] = analysis
    await repository.save(analysis)

    logger.info(
        "Analysis created: id=%s input_type=%s",
        analysis.id,
        analysis.input_type,
    )

    # ----------------------------------------------------------------
    # Dispatch pipeline as a background task
    # BackgroundTasks runs after the response is sent.
    # ----------------------------------------------------------------
    background_tasks.add_task(run_analysis_pipeline, analysis.id, _analyses, repository.save)

    return {
        "analysis_id": analysis.id,
        "status": analysis.status,
        "message": (
            "Analysis queued. Poll GET /api/v1/analyses/{id} for status and results."
        ),
    }


# ===========================================================================
# GET /api/v1/analyses/{analysis_id}
# ===========================================================================

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str) -> AnalysisResponse:
    """
    Poll an analysis for status and results.

    Returns the current state at any stage of the pipeline.
    Fields are populated progressively:
      - requirements: available after 'extracting' step (Step 5)
      - standards, findings: available after 'analyzing' step (Step 6)
      - full evidence: available after 'enriching' step (Step 7)

    Errors:
      404 — analysis_id not found
    """
    analysis = _analyses.get(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ANALYSIS_NOT_FOUND",
                "message": f"No analysis found with id '{analysis_id}'.",
            },
        )

    # Collect all unique standards referenced across findings
    seen_standard_ids: set[str] = set()
    all_standards = []
    for finding in analysis.findings:
        for standard in finding.applicable_standards:
            if standard.id not in seen_standard_ids:
                all_standards.append(standard)
                seen_standard_ids.add(standard.id)

    return AnalysisResponse(
        id=analysis.id,
        status=analysis.status,
        input_type=analysis.input_type,
        tender_id=analysis.tender_id,
        tender_title=analysis.tender_title,
        created_at=analysis.created_at.isoformat(),
        updated_at=analysis.updated_at.isoformat(),
        requirements=analysis.requirements,
        total_requirements=analysis.total_requirements,
        standards=all_standards,
        findings=analysis.findings,
        issues_found=analysis.issues_found,
        summary=analysis.summary,
        error_message=analysis.error_message,
        metadata=analysis.metadata,
        analysis_mode=analysis.metadata.get("analysis_mode", "fallback"),
        degraded_reason=analysis.metadata.get("degraded_reason"),
    )


# ===========================================================================
# GET /api/v1/analyses  (list — useful for frontend dashboard)
# ===========================================================================

@router.get("", response_model=list[dict])
async def list_analyses() -> list[dict]:
    """
    List all analyses with their current status.
    Useful for a frontend dashboard showing recent analysis jobs.
    """
    return [
        {
            "analysis_id": a.id,
            "status": a.status,
            "input_type": a.input_type,
            "tender_id": a.tender_id,
            "tender_title": a.tender_title,
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat(),
            "total_requirements": a.total_requirements,
            "issues_found": a.issues_found,
            "metadata": a.metadata,
            "summary": a.summary,
            "analysis_mode": a.metadata.get("analysis_mode", "fallback"),
            "degraded_reason": a.metadata.get("degraded_reason"),
        }
        for a in sorted(_analyses.values(), key=lambda x: x.created_at, reverse=True)
    ]
