"""
GET /api/v1/standards/search  — search standards by query
GET /api/v1/standards/{id}    — get a specific standard by ID

These routes delegate to kshiraj/knowledge/retrieval_service.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from shared.models import Standard
from shared.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/standards", tags=["standards"])


@router.get("/search", response_model=list[Standard])
async def search_standards(
    q: str = Query(..., description="Search query — product description or standard number"),
    limit: int = Query(10, ge=1, le=50),
) -> list[Standard]:
    """
    Search for relevant Indian Standards by natural language query or standard number.

    Delegates to kshiraj/knowledge/retrieval_service.py.
    """
    # TODO(kshiraj): wire retrieval_service.search_standards(query=q, limit=limit)
    logger.info("Standards search: q='%s' limit=%d", q, limit)
    return []


@router.get("/{standard_id}", response_model=Standard)
async def get_standard(standard_id: str) -> Standard:
    """Get a specific standard by its internal ID."""
    # TODO(kshiraj): wire standards_store.get_by_id(standard_id)
    raise HTTPException(status_code=404, detail=f"Standard '{standard_id}' not found.")
