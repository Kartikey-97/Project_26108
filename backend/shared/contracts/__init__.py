"""
API request/response contracts.

These are the schemas that cross component boundaries:
  - Frontend → Backend API (APIRequest / APIResponse)
  - Backend → AI/ML (AimlRequest)
  - AI/ML → Backend (AimlResponse)

Neither side should reach inside the other's internals.
All inter-component communication goes through these schemas.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from shared.models import (
    AnalysisStatus,
    Evidence,
    Finding,
    InputType,
    Requirement,
    Standard,
)


# ---------------------------------------------------------------------------
# Frontend ↔ Backend
# ---------------------------------------------------------------------------


class CreateAnalysisRequest(BaseModel):
    """POST /api/v1/analyses"""

    input_type: InputType
    text: str | None = None          # used when input_type == "text"
    document_id: str | None = None   # used when input_type == "document"
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisStatusResponse(BaseModel):
    """GET /api/v1/analyses/{id} — polling response."""

    id: str
    status: AnalysisStatus
    created_at: str
    updated_at: str
    requirements: list[Requirement] = []
    standards: list[Standard] = []
    findings: list[Finding] = []
    evidence: list[Evidence] = []
    summary: str | None = None
    error_message: str | None = None


class UploadDocumentResponse(BaseModel):
    """POST /api/v1/documents/upload"""

    document_id: str
    filename: str
    size_bytes: int
    message: str


# ---------------------------------------------------------------------------
# Backend → AI/ML
# ---------------------------------------------------------------------------


class AimlRequest(BaseModel):
    """
    Input the backend sends to the AI/ML component.

    The backend provides:
      - raw extracted text (for context)
      - normalized requirements
      - pre-retrieved candidate standards (with text excerpts)

    The AI/ML component should NOT make its own database calls.
    """

    analysis_id: str
    extracted_text: str
    requirements: list[Requirement]
    retrieved_standards: list[Standard]


# ---------------------------------------------------------------------------
# AI/ML → Backend
# ---------------------------------------------------------------------------


class AimlFinding(BaseModel):
    """
    A single finding returned by the AI/ML component.

    IMPORTANT: The backend assembles the final evidence records.
    The AI/ML component returns IDs, not full evidence objects.
    This prevents the LLM from hallucinating evidence text.
    """

    finding_id: str
    requirement_id: str
    verdict: str                      # maps to shared.models.Verdict
    reason: str
    evidence_ids: list[str] = []      # references to evidence already in DB
    applicable_standard_ids: list[str] = []
    confidence: float                 # 0.0 – 1.0
    recommended_action: str | None = None


class AimlResponse(BaseModel):
    """Response the AI/ML component returns to the backend."""

    analysis_id: str
    findings: list[AimlFinding]
