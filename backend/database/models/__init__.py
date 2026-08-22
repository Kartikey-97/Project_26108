"""
ORM table definitions.

Keep these in sync with shared.models domain models.
Use Alembic (migrations/) to apply schema changes — do not call create_all() in production.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from shared.models import AnalysisStatus, InputType, StandardStatus, Verdict


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


class AnalysisORM(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    input_type: Mapped[str] = mapped_column(Enum(InputType), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(AnalysisStatus), default=AnalysisStatus.QUEUED, nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    requirements: Mapped[list[RequirementORM]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )
    findings: Mapped[list[FindingORM]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# Requirement
# ---------------------------------------------------------------------------


class RequirementORM(Base):
    __tablename__ = "requirements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    normalized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    analysis: Mapped[AnalysisORM] = relationship(back_populates="requirements")
    findings: Mapped[list[FindingORM]] = relationship(back_populates="requirement")


# ---------------------------------------------------------------------------
# Standard
# ---------------------------------------------------------------------------


class StandardORM(Base):
    __tablename__ = "standards"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    standard_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    part: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(StandardStatus), default=StandardStatus.UNKNOWN
    )
    current_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    text_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    # pgvector embedding column — add via migration once pgvector extension is confirmed
    # embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=True)


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


class EvidenceORM(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    finding_id: Mapped[str | None] = mapped_column(ForeignKey("findings.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_section: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    finding: Mapped[FindingORM | None] = relationship(back_populates="evidence")


# ---------------------------------------------------------------------------
# Finding
# ---------------------------------------------------------------------------


class FindingORM(Base):
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id"), nullable=False)
    requirement_id: Mapped[str] = mapped_column(ForeignKey("requirements.id"), nullable=False)
    verdict: Mapped[str] = mapped_column(Enum(Verdict), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_human_verification: Mapped[bool] = mapped_column(default=False)

    analysis: Mapped[AnalysisORM] = relationship(back_populates="findings")
    requirement: Mapped[RequirementORM] = relationship(back_populates="findings")
    evidence: Mapped[list[EvidenceORM]] = relationship(
        back_populates="finding", cascade="all, delete-orphan"
    )
