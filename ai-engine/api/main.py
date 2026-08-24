"""
ai-engine/api/main.py

FastAPI entrypoint for the StandIQ AI Engine.

Endpoints:
  GET  /          — welcome message
  GET  /health    — liveness check (Render health probe)
  POST /analyze   — per-requirement compliance analysis (called by backend)
  POST /recommend — end-to-end standard recommendation from a free-text query
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from src.reasoning.analyzer import Analyzer
from src.recommender import Recommender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="StandIQ AI Engine",
    description="BIS standards recommendation and compliance analysis engine",
    version="2.0.0",
)

# CORS — allow backend and frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup — instantiate singletons once
# ---------------------------------------------------------------------------
logger.info("Initialising Analyzer…")
analyzer = Analyzer()

logger.info("Initialising Recommender (this will generate embeddings for 1015 standards)…")
recommender = Recommender()

# ---------------------------------------------------------------------------
# Request / Response models for /analyze
# ---------------------------------------------------------------------------
class Requirement(BaseModel):
    id: str
    analysis_id: str
    text: str
    normalized_text: Optional[str] = None
    category: str = "other"
    is_reference: Optional[str] = None
    cited_year: Optional[int] = None
    cited_designation: Optional[str] = None
    location: Optional[str] = None
    page: Optional[int] = None
    extracted_at: Optional[str] = None
    extraction_confidence: Optional[float] = None
    from_corrigendum: bool = False
    corrigendum_number: Optional[int] = None

class Standard(BaseModel):
    id: str
    is_number: str
    title: str
    status: str
    year: Optional[int] = None

class AimlRequest(BaseModel):
    analysis_id: str
    extracted_text: str
    requirements: List[Requirement]
    retrieved_standards: List[Standard]

class AimlFinding(BaseModel):
    finding_id: str
    requirement_id: str
    verdict: str
    reason: str
    recommended_action: Optional[str] = None
    applicable_standard_ids: List[str] = []
    evidence_ids: List[str] = []
    confidence: float

class AimlResponse(BaseModel):
    analysis_id: str
    findings: List[AimlFinding]
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)

# ---------------------------------------------------------------------------
# Request / Response models for /recommend
# ---------------------------------------------------------------------------
class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000,
                       description="Free-text procurement query or tender excerpt")
    top_k: int = Field(default=5, ge=1, le=20,
                       description="Number of standards to return")

class RecommendResponse(BaseModel):
    query: str
    query_understanding: Dict[str, Any] = {}
    recommendations: List[Dict[str, Any]] = []
    related_standards: List[str] = []
    test_methods: List[str] = []
    safety_standards: List[str] = []
    normative_references: List[str] = []
    potential_gaps: List[Dict[str, Any]] = []
    currentness: Dict[str, Any] = {}
    additional_currentness: Dict[str, Any] = {}
    confidence: str = "low"
    error: Optional[str] = None

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "StandIQ AI Engine",
        "version": "2.0.0",
        "endpoints": ["/health", "/analyze", "/recommend"],
        "standards_indexed": len(recommender.standards),
    }


@app.get("/health")
def health():
    """Liveness check — Render uses this to confirm the service is up."""
    return {
        "status": "ok",
        "recommender_ready": recommender.retriever is not None,
        "standards_count": len(recommender.standards),
        "analyzer_mode": getattr(analyzer, "_mode", "unknown"),
    }


@app.post("/analyze", response_model=AimlResponse)
def analyze(request: AimlRequest):
    """
    Per-requirement compliance analysis.
    Called by the StandIQ backend with pre-extracted requirements and pre-retrieved standards.
    """
    try:
        response = analyzer.process(request)
        return response
    except Exception as exc:
        logger.error("Analysis failed for analysis_id=%s: %s", request.analysis_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/recommend")
def recommend(request: RecommendRequest):
    """
    End-to-end BIS standards recommendation from a free-text procurement query.

    Uses hybrid BM25 + semantic retrieval, Gemini query understanding,
    deterministic currentness checking, and structured gap detection.
    """
    try:
        result = recommender.recommend(request.query, top_k=request.top_k)
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Recommend endpoint failed for query='%s': %s", request.query[:80], exc)
        raise HTTPException(status_code=500, detail=str(exc))
