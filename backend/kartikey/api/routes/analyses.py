"""
POST /api/v1/analyses      — create a new analysis
GET  /api/v1/analyses/{id} — poll status and retrieve results
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from kartikey.orchestration.pipeline import run_analysis_pipeline
from shared.contracts import AnalysisStatusResponse, CreateAnalysisRequest
from shared.models import Analysis, AnalysisStatus, InputType
from shared.utils import get_logger, utcnow_iso

logger = get_logger(__name__)
router = APIRouter(prefix="/analyses", tags=["analyses"])

# ---------------------------------------------------------------------------
# In-memory store for MVP — replace with DB queries once ORM is wired
# ---------------------------------------------------------------------------

_analyses: dict[str, Analysis] = {}


@router.post("", response_model=dict, status_code=202)
async def create_analysis(
    body: CreateAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Create a new procurement analysis.

    Accepts either:
      - input_type="text"     + text="..."
      - input_type="document" + document_id="..."

    Returns the analysis_id immediately; poll GET /analyses/{id} for results.
    """
    if body.input_type == InputType.TEXT and not body.text:
        raise HTTPException(status_code=400, detail="'text' is required when input_type is 'text'")
    if body.input_type == InputType.DOCUMENT and not body.document_id:
        raise HTTPException(
            status_code=400, detail="'document_id' is required when input_type is 'document'"
        )

    analysis = Analysis(
        input_type=body.input_type,
        raw_text=body.text,
        document_id=body.document_id,
        status=AnalysisStatus.QUEUED,
        metadata=body.metadata,
    )
    _analyses[analysis.id] = analysis

    logger.info("Analysis created: %s (status=queued)", analysis.id)

    # Dispatch pipeline as a background task — no Celery needed for MVP
    background_tasks.add_task(run_analysis_pipeline, analysis.id, _analyses)

    return {
        "analysis_id": analysis.id,
        "status": analysis.status,
        "message": "Analysis queued. Poll GET /api/v1/analyses/{id} for results.",
    }


@router.get("/{analysis_id}", response_model=AnalysisStatusResponse)
async def get_analysis(analysis_id: str) -> AnalysisStatusResponse:
    """
    Poll analysis status and retrieve results when completed.

    Status lifecycle:
        queued → extracting → retrieving → analyzing → enriching → completed
                                                                  ↘ partially_completed
                                                                  ↘ failed
    """
    analysis = _analyses.get(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found.")

    return AnalysisStatusResponse(
        id=analysis.id,
        status=analysis.status,
        created_at=analysis.created_at.isoformat(),
        updated_at=analysis.updated_at.isoformat(),
        requirements=analysis.requirements,
        standards=[],   # populated after retrieval step
        findings=analysis.findings,
        evidence=[],    # populated after enrichment step
        summary=None,
        error_message=analysis.error_message,
    )
