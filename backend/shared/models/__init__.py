"""
Shared Pydantic domain models.

These are the core data shapes used across kartikey/ and kshiraj/.
Agree on these before building repositories or API responses.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AnalysisStatus(str, Enum):
    QUEUED = "queued"
    EXTRACTING = "extracting"
    RETRIEVING = "retrieving"
    ANALYZING = "analyzing"
    ENRICHING = "enriching"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"


class Verdict(str, Enum):
    JUSTIFIED = "justified"
    POTENTIALLY_UNNECESSARY = "potentially_unnecessary"
    OUTDATED_REFERENCE = "outdated_reference"
    INCORRECT_STANDARD = "incorrect_standard"
    WRONG_SCOPE = "wrong_scope"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"
    CONFLICTING = "conflicting"
    POTENTIALLY_OVER_RESTRICTIVE = "potentially_over_restrictive"
    UNABLE_TO_DETERMINE = "unable_to_determine"
    REQUIRES_HUMAN_VERIFICATION = "requires_human_verification"


class StandardStatus(str, Enum):
    ACTIVE = "active"
    REVISED = "revised"
    WITHDRAWN = "withdrawn"
    AMENDMENT = "amendment"
    DRAFT_IN_PROGRESS = "draft_in_progress"
    UNKNOWN = "unknown"


class InputType(str, Enum):
    TEXT = "text"
    DOCUMENT = "document"


# ---------------------------------------------------------------------------
# Core domain models
# ---------------------------------------------------------------------------


class Requirement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str
    text: str
    category: str | None = None  # e.g. "technical", "certification", "performance"
    normalized_text: str | None = None
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class Standard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    standard_number: str          # e.g. "IS 10322"
    part: str | None = None       # e.g. "Part 5/Sec 3"
    title: str
    version: str | None = None    # e.g. "2012"
    status: StandardStatus = StandardStatus.UNKNOWN
    current_version: str | None = None   # if REVISED, what is current?
    source_url: str | None = None
    retrieved_at: datetime | None = None
    text_excerpt: str | None = None


class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: str              # e.g. "bis_document", "cppp_tender", "qco_notification"
    source_name: str
    url: str | None = None
    document_section: str | None = None   # page/section reference if known
    text: str
    retrieval_date: datetime = Field(default_factory=datetime.utcnow)
    confidence: float | None = None       # 0.0 – 1.0


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requirement_id: str
    verdict: Verdict
    reason: str
    applicable_standards: list[Standard] = []
    evidence: list[Evidence] = []
    confidence: float            # 0.0 – 1.0
    recommended_action: str | None = None
    requires_human_verification: bool = False


class Analysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input_type: InputType
    raw_text: str | None = None
    document_id: str | None = None
    status: AnalysisStatus = AnalysisStatus.QUEUED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    requirements: list[Requirement] = []
    findings: list[Finding] = []
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
