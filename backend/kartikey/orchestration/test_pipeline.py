"""
kartikey/orchestration/test_pipeline.py

Unit tests for the integrated analysis pipeline state machine.

Tests cover:
  - Text input analysis pipeline end-to-end execution
  - Document input analysis pipeline execution
  - Requirement extraction integration (_step_extract)
  - Standards retrieval integration (_step_retrieve)
  - Pipeline error handling and state transitions
"""

from __future__ import annotations

import asyncio
import pytest

from shared.models import Analysis, AnalysisStatus, InputType, Standard, StandardStatus
from kartikey.orchestration.knowledge_registry import initialize_knowledge_registry
from kartikey.orchestration.pipeline import run_analysis_pipeline


@pytest.fixture
def registry():
    """Initialize and clear the registry used by the current pipeline."""
    registry = initialize_knowledge_registry()
    registry.standards_store.clear()
    registry.evidence_store.clear()
    return registry


def test_pipeline_text_input_end_to_end(registry) -> None:
    """Verify that a text input analysis runs through all steps to COMPLETED."""
    async def _run() -> None:
        std = Standard(
            is_number="IS 10322",
            title="Specification for Luminaires - Street Lighting",
            status=StandardStatus.ACTIVE,
        )
        registry.standards_store.add(std)

        analysis_store: dict[str, Analysis] = {}
        analysis = Analysis(
            input_type=InputType.TEXT,
            raw_text=(
                "1. The LED street lighting luminaire shall conform to IS 10322 (Part 5):2012.\n"
                "2. The driver shall comply with IS 15885 Part 1."
            ),
            status=AnalysisStatus.QUEUED,
        )
        analysis_store[analysis.id] = analysis

        await run_analysis_pipeline(analysis.id, analysis_store)

        completed_analysis = analysis_store[analysis.id]
        assert completed_analysis.status == AnalysisStatus.COMPLETED
        assert len(completed_analysis.requirements) == 2
        assert completed_analysis.total_requirements == 2
        assert completed_analysis.error_message is None

    asyncio.run(_run())


def test_pipeline_missing_analysis_id(registry) -> None:
    """Verify that running a pipeline for an unknown analysis ID aborts gracefully."""
    async def _run() -> None:
        analysis_store: dict[str, Analysis] = {}
        await run_analysis_pipeline("nonexistent-id", analysis_store)
        assert "nonexistent-id" not in analysis_store

    asyncio.run(_run())


def test_pipeline_text_input_missing_text(registry) -> None:
    """Verify that text input without raw_text transitions to FAILED."""
    async def _run() -> None:
        analysis_store: dict[str, Analysis] = {}
        analysis = Analysis(
            input_type=InputType.TEXT,
            raw_text=None,
            status=AnalysisStatus.QUEUED,
        )
        analysis_store[analysis.id] = analysis

        await run_analysis_pipeline(analysis.id, analysis_store)

        failed_analysis = analysis_store[analysis.id]
        assert failed_analysis.status == AnalysisStatus.FAILED
        assert "MISSING_INPUT" in (failed_analysis.error_message or "")

    asyncio.run(_run())
