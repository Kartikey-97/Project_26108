"""
kartikey/api/main.py

FastAPI application entry point.

Run locally:
    cd backend
    uvicorn kartikey.api.main:app --reload --port 8000

Routers are mounted under /api/v1/.
The /health endpoint lives at root for load-balancer checks.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.config import settings
from shared.utils import AppError, get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="SIH 26108 — Procurement Intelligence API",
    description=(
        "An AI-powered procurement intelligence platform that unifies fragmented "
        "standards, regulations, certifications, and procurement data into a single "
        "workflow. Helps procurement officers make faster, more accurate, transparent, "
        "and defensible decisions."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# Adjust allow_origins before any production deployment.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global error handler — converts AppError subclasses to structured JSON
# ---------------------------------------------------------------------------
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("AppError [%s]: %s", exc.code, exc.message)
    return JSONResponse(
        status_code=400,
        content={"error": exc.code, "message": exc.message},
    )


# ---------------------------------------------------------------------------
# Routers
# Uncomment each router as it is implemented.
# ---------------------------------------------------------------------------

from kartikey.api.routes import documents, analyses, standards, reports, simulator

app.include_router(documents.router, prefix="/api/v1")
app.include_router(analyses.router,  prefix="/api/v1")
app.include_router(standards.router, prefix="/api/v1")
app.include_router(reports.router,   prefix="/api/v1")
app.include_router(simulator.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["health"])
async def health() -> dict:
    """
    Health check — confirms the server is up and returns basic stack info.
    Frontend and DevOps can poll this to verify the backend is reachable.
    """
    return {
        "status": "ok",
        "service": "sih26108-backend",
        "version": "0.1.0",
        "environment": settings.app_env,
    }


# ---------------------------------------------------------------------------
# Startup / shutdown events
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def on_startup() -> None:
    logger.info(
        "SIH 26108 backend starting up — env=%s debug=%s",
        settings.app_env,
        settings.app_debug,
    )
    
    from kartikey.orchestration.knowledge_registry import initialize_knowledge_registry
    from shared.seed_data import get_seed_standards, get_seed_evidence
    
    registry = initialize_knowledge_registry()
    
    # Load seed data (MVP vertical slice)
    for std in get_seed_standards():
        registry.standards_store.add(std)
    for ev in get_seed_evidence():
        registry.evidence_store.add(ev)
        
    logger.info(
        "Loaded seed data: %d standards, %d evidence records.",
        registry.standards_store.count(),
        registry.evidence_store.count(),
    )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("SIH 26108 backend shutting down.")
