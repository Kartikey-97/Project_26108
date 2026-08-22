"""
FastAPI application entry point.

Run locally:
    uvicorn kartikey.api.main:app --reload --port 8000

All routes are mounted under /api/v1/.
The /health endpoint is at root level for load-balancer checks.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kartikey.api.routes import analyses, documents, reports, standards
from shared.utils import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="SIH 26108 — Procurement Intelligence API",
    description=(
        "AI-Powered Recommendation Engine for Identifying Applicable "
        "Indian Standards for Procurement Specifications."
    ),
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — adjust origins before production deployment
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(analyses.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(standards.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"])
async def health() -> dict:
    """
    Health check endpoint.
    Returns stack info so the team can verify which instance is running.
    """
    return {
        "status": "ok",
        "service": "sih26108-backend",
        "version": "0.1.0",
    }
