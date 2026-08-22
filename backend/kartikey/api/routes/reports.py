"""GET /api/v1/analyses/{id}/report — export a completed analysis as structured JSON."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from shared.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analyses", tags=["reports"])


@router.get("/{analysis_id}/report")
async def get_report(analysis_id: str) -> JSONResponse:
    """
    Export a completed analysis as a structured report.

    Returns the full analysis with requirements, standards, findings, and evidence.
    Intended to be used by frontend for PDF generation or download.

    TODO: implement once the full pipeline is wired.
    """
    # TODO(kartikey): retrieve completed analysis and format as report
    raise HTTPException(
        status_code=501,
        detail="Report generation not yet implemented.",
    )
