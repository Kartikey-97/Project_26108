"""
kartikey/api/routes/standards.py

GET /api/v1/standards/search  — search standards by query
GET /api/v1/standards/{id}    — get a specific standard by ID

These endpoints allow the frontend to provide a manual standard search/lookup
feature for the procurement officer, independent of the automated analysis.

Delegates entirely to Kshiraj's knowledge retrieval service.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from shared.models import Standard
from shared.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/standards", tags=["standards"])


@router.get("/search", response_model=list[Standard])
async def search_standards(
    q: str = Query(..., min_length=2, description="Search query — product description, IS number, etc."),
    limit: int = Query(10, ge=1, le=50),
) -> list[Standard]:
    """
    Search for relevant Indian Standards by natural language query or exact IS number.
    
    This provides a manual search capability for the frontend.
    Delegates to kshiraj/knowledge/retrieval_service.py (wired in Step 7).
    """
    logger.info("Manual standards search: q='%s' limit=%d", q, limit)
    
    # TODO(Step 7): wire retrieval_service.search_standards(query=q, limit=limit)
    # For now, return an empty list as a stub until Kshiraj's retrieval layer is ready.
    return []


@router.get("/{standard_id}", response_model=Standard)
async def get_standard(standard_id: str) -> Standard:
    """
    Get the full details of a specific standard by its internal ID.
    
    TODO(Step 7): wire standards_store.get_by_id(standard_id)
    """
    # For now, raise 404 until the DB and knowledge store are wired
    raise HTTPException(
        status_code=404,
        detail={
            "error": "STANDARD_NOT_FOUND",
            "message": f"Standard lookup is not yet wired. Cannot find ID '{standard_id}'.",
        },
    )
