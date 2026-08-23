"""
kartikey/api/routes/reports.py

GET /api/v1/analyses/{id}/report

Exports a completed analysis as a structured report (JSON or eventually PDF).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from kartikey.api.routes.analyses import _analyses
from shared.contracts import AnalysisResponse
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

    if analysis.status not in {"completed", "partially_completed"}:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ANALYSIS_NOT_COMPLETED",
                "message": f"Cannot generate report for analysis in state '{analysis.status}'.",
            },
        )

    standards = []
    seen_standard_ids: set[str] = set()
    for finding in analysis.findings:
        for standard in finding.applicable_standards:
            if standard.id not in seen_standard_ids:
                standards.append(standard)
                seen_standard_ids.add(standard.id)

    return {
        "report_type": "procurement_compliance_report",
        "generated_at": analysis.updated_at.isoformat(),
        "analysis": AnalysisResponse(
            id=analysis.id,
            status=analysis.status,
            input_type=analysis.input_type,
            tender_id=analysis.tender_id,
            tender_title=analysis.tender_title,
            created_at=analysis.created_at.isoformat(),
            updated_at=analysis.updated_at.isoformat(),
            requirements=analysis.requirements,
            total_requirements=analysis.total_requirements,
            standards=standards,
            findings=analysis.findings,
            issues_found=analysis.issues_found,
            summary=analysis.summary,
            error_message=analysis.error_message,
            metadata=analysis.metadata,
            analysis_mode=analysis.metadata.get("analysis_mode", "fallback"),
            degraded_reason=analysis.metadata.get("degraded_reason"),
        ).model_dump(mode="json"),
    }
