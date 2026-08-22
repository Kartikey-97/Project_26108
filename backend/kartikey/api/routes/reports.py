"""
kartikey/api/routes/reports.py

GET /api/v1/analyses/{id}/report

Exports a completed analysis as a structured report (JSON or eventually PDF).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from kartikey.api.routes.analyses import _analyses
from shared.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analyses", tags=["reports"])


@router.get("/{analysis_id}/report")
async def get_report(analysis_id: str) -> dict:
    """
    Export a completed analysis as a structured report.
    
    This is a placeholder for Step 9 (Report Generation).
    Eventually, this might return a PDF buffer or a heavily formatted JSON
    tailored for printing/downloading.
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

    if analysis.status != "completed":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ANALYSIS_NOT_COMPLETED",
                "message": f"Cannot generate report for analysis in state '{analysis.status}'.",
            },
        )

    # TODO(Step 9): Generate and return a proper PDF or structured export format.
    raise HTTPException(
        status_code=501,
        detail={
            "error": "NOT_IMPLEMENTED",
            "message": "Report generation (Step 9) is not yet implemented.",
        },
    )
