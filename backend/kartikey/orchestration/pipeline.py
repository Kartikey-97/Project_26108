"""
kartikey/orchestration/pipeline.py

Analysis pipeline — the state machine that coordinates the full workflow.

State transitions:
    queued → extracting → retrieving → analyzing → enriching → completed
                                                              ↘ partially_completed
                                                              ↘ failed

This module is invoked as a FastAPI BackgroundTask (no Celery/Redis for MVP).
Each step calls into the appropriate subsystem:

  _step_extract   → kartikey/document_processing + AI/ML requirement extraction (Step 5)
  _step_retrieve  → kshiraj/knowledge/retrieval_service (Step 7)
  _step_analyze   → kshiraj/aiml_client (Step 6)
  _step_enrich    → kshiraj/enrichment + kartikey/analysis/findings (Step 7)

Step 4 (this step) focuses on:
  - Robust per-step error handling with PARTIAL_COMPLETED state
  - Correct state transitions even when sub-steps fail
  - Populating interim results (IS references from preliminary scan)
    so the frontend has something to show before full AI analysis is ready
  - Clear logging at every transition

IMPORTANT:
  The pipeline mutates the Analysis object in the shared store.
  The GET /analyses/{id} endpoint reads from the same store.
  This is safe in single-process uvicorn (the default for MVP).
  If multi-worker deployment is needed later, replace the in-memory
  store with a database-backed approach.
"""

from __future__ import annotations

import asyncio
import traceback

from shared.models import Analysis, AnalysisStatus, InputType, Requirement, RequirementCategory
from shared.utils import AnalysisError, get_logger, utcnow

logger = get_logger(__name__)


# ===========================================================================
# Entry point — called by FastAPI BackgroundTasks
# ===========================================================================

async def run_analysis_pipeline(
    analysis_id: str,
    store: dict[str, Analysis],
) -> None:
    """
    Coordinate the full analysis pipeline for one analysis job.

    Parameters
    ----------
    analysis_id:
        The ID of the analysis to run.
    store:
        Shared in-memory dict of analyses (keyed by analysis_id).
        Mutated in place as the pipeline progresses.
    """
    analysis = store.get(analysis_id)
    if not analysis:
        logger.error("Pipeline started for unknown analysis_id=%s — aborting.", analysis_id)
        return

    logger.info(
        "Pipeline started: analysis_id=%s input_type=%s",
        analysis_id,
        analysis.input_type.value,
    )

    extracted_text: str = ""
    retrieved_standards: list = []
    aiml_response = None

    try:
        # ----------------------------------------------------------------
        # Step 1: Extract text + preliminary requirement scan
        # ----------------------------------------------------------------
        _transition(analysis, AnalysisStatus.EXTRACTING)
        extracted_text = await _step_extract(analysis)

        # ----------------------------------------------------------------
        # Step 2: Retrieve relevant standards from knowledge base
        # ----------------------------------------------------------------
        _transition(analysis, AnalysisStatus.RETRIEVING)
        retrieved_standards = await _step_retrieve(analysis, extracted_text)

        # ----------------------------------------------------------------
        # Step 3: AI/ML analysis
        # ----------------------------------------------------------------
        _transition(analysis, AnalysisStatus.ANALYZING)
        aiml_response = await _step_analyze(analysis, extracted_text, retrieved_standards)

        # ----------------------------------------------------------------
        # Step 4: Enrich — version checks, QCO, compliance, findings assembly
        # ----------------------------------------------------------------
        _transition(analysis, AnalysisStatus.ENRICHING)
        await _step_enrich(analysis, retrieved_standards, aiml_response)

        # ----------------------------------------------------------------
        # Finalize counts and mark completed
        # ----------------------------------------------------------------
        analysis.total_requirements = len(analysis.requirements)
        analysis.issues_found = sum(
            1 for f in analysis.findings
            if f.verdict.value != "justified"
        )

        # If we have requirements but zero findings, something partially failed
        if analysis.total_requirements > 0 and not analysis.findings:
            _transition(analysis, AnalysisStatus.PARTIALLY_COMPLETED)
            analysis.error_message = (
                "Requirements were extracted but analysis could not produce findings. "
                "This may be because the AI/ML or retrieval layer is not yet wired."
            )
        else:
            _transition(analysis, AnalysisStatus.COMPLETED)

        logger.info(
            "Pipeline finished: analysis_id=%s status=%s requirements=%d issues=%d",
            analysis_id,
            analysis.status.value,
            analysis.total_requirements,
            analysis.issues_found,
        )

    except AnalysisError as exc:
        # Known, recoverable errors from our own code
        logger.error(
            "Pipeline failed [%s]: %s (analysis_id=%s)",
            exc.code, exc.message, analysis_id,
        )
        analysis.error_message = f"[{exc.code}] {exc.message}"
        _transition(analysis, AnalysisStatus.FAILED)

    except Exception:
        # Unexpected errors — log full traceback, never let background task crash silently
        logger.error(
            "Pipeline unexpected failure for analysis_id=%s:\n%s",
            analysis_id,
            traceback.format_exc(),
        )
        analysis.error_message = "An unexpected internal error occurred."
        _transition(analysis, AnalysisStatus.FAILED)


# ===========================================================================
# Pipeline steps
# ===========================================================================

async def _step_extract(analysis: Analysis) -> str:
    """
    Load the document text and run a preliminary IS reference scan.

    For TEXT input:   raw_text is used directly.
    For DOCUMENT input: loads the already-extracted text from storage.

    Interim result: populates analysis.requirements with candidate requirements
    found by the regex IS reference scanner. These are PRELIMINARY — they will
    be replaced by proper AI-extracted requirements in Step 5.
    The interim requirements allow the frontend to show something useful
    before the full AI analysis completes.

    Full AI requirement extraction is wired in Step 5.
    """
    # --- Load text ---
    if analysis.input_type == InputType.TEXT:
        if not analysis.raw_text or not analysis.raw_text.strip():
            raise AnalysisError(
                "Analysis has input_type=TEXT but raw_text is empty.",
                code="MISSING_INPUT",
            )
        extracted_text = analysis.raw_text
        logger.debug(
            "_step_extract: using raw_text (%d chars) for analysis_id=%s",
            len(extracted_text), analysis.id,
        )

    elif analysis.input_type == InputType.DOCUMENT:
        if not analysis.document_id:
            raise AnalysisError(
                "Analysis has input_type=DOCUMENT but document_id is missing.",
                code="MISSING_DOCUMENT_ID",
            )
        from kartikey.document_processing.storage import get_extracted_text
        extracted_text = get_extracted_text(analysis.document_id)
        if not extracted_text:
            raise AnalysisError(
                f"No extracted text found for document_id={analysis.document_id}. "
                "Ensure the document was uploaded successfully via POST /documents/upload.",
                code="NO_EXTRACTED_TEXT",
            )
        logger.debug(
            "_step_extract: loaded document text (%d chars) for document_id=%s",
            len(extracted_text), analysis.document_id,
        )
    else:
        raise AnalysisError(
            f"Unknown input_type: {analysis.input_type}",
            code="INVALID_INPUT_TYPE",
        )

    # --- AI-powered requirement extraction (Step 5) ---
    # Try the LLM extractor first. If unavailable (no API key / quota exhausted),
    # fall back to the regex IS reference scanner so the pipeline always produces
    # some output and doesn't hard-fail just because the LLM is unreachable.
    from kartikey.analysis.requirement_extractor import extract_requirements
    from kartikey.document_processing.extractor import scan_is_references
    from shared.utils import AnalysisError as _AnalysisError

    ai_extraction_succeeded = False
    try:
        ai_requirements = extract_requirements(
            analysis_id=analysis.id,
            document_text=extracted_text,
        )
        analysis.requirements = ai_requirements
        analysis.total_requirements = len(ai_requirements)
        ai_extraction_succeeded = True
        logger.info(
            "_step_extract: AI extraction succeeded — %d requirements found. analysis_id=%s",
            len(ai_requirements), analysis.id,
        )
    except _AnalysisError as exc:
        if exc.code in ("LLM_NOT_CONFIGURED", "LLM_QUOTA_EXHAUSTED", "LLM_NO_MODEL_AVAILABLE"):
            # LLM unavailable — fall back to regex scan gracefully
            logger.warning(
                "_step_extract: LLM unavailable (%s: %s). "
                "Falling back to regex IS reference scan for analysis_id=%s.",
                exc.code, exc.message, analysis.id,
            )
            analysis.metadata["extraction_fallback"] = True
            analysis.metadata["extraction_fallback_reason"] = exc.code
        else:
            # LLM responded but errored mid-extraction — re-raise to fail the pipeline
            raise

    # Regex fallback — runs when LLM is unavailable OR when LLM found zero requirements
    if not ai_extraction_succeeded or not analysis.requirements:
        is_refs = scan_is_references(extracted_text)
        if is_refs:
            logger.info(
                "_step_extract: regex scan found %d IS reference(s) as %s. analysis_id=%s",
                len(is_refs),
                "fallback" if not ai_extraction_succeeded else "supplement",
                analysis.id,
            )
            regex_requirements = [
                Requirement(
                    analysis_id=analysis.id,
                    text=ref["matched_text"],
                    normalized_text=ref["matched_text"],
                    category=RequirementCategory.TECHNICAL_SPECIFICATION,
                    is_reference=ref["is_number"],
                    cited_year=ref["year"],
                    cited_designation=ref["matched_text"],
                    extraction_confidence=0.6,
                )
                for ref in is_refs
            ]
            analysis.requirements = regex_requirements
            analysis.total_requirements = len(regex_requirements)
        else:
            logger.info(
                "_step_extract: no requirements found by AI or regex. analysis_id=%s",
                analysis.id,
            )

    return extracted_text




async def _step_retrieve(
    analysis: Analysis,
    extracted_text: str,
) -> list[Standard]:
    """
    Search the knowledge base for standards matching the extracted requirements.
    Delegates to the retrieval service for vector/lexical search.
    """
    await asyncio.sleep(0)

    if not analysis.requirements:
        logger.info(
            "_step_retrieve: no requirements to retrieve standards for. analysis_id=%s",
            analysis.id,
        )
        return []

    from kartikey.orchestration.knowledge_registry import get_registry
    from kshiraj.knowledge.retrieval_service import RetrievalQuery

    registry = get_registry()
    retrieved_standards: list[Standard] = []
    seen_ids: set[str] = set()

    for req in analysis.requirements:
        # If the requirement cites a specific IS number, use that as the primary query.
        # Otherwise, use the raw text. The retrieval service handles both.
        query_text = req.is_reference if req.is_reference else req.text
        
        # We don't need a huge top_k per requirement because many will hit the same core standards
        query = RetrievalQuery(
            query_text=query_text,
            top_k=3,
            include_evidence=False,  # Evidence is fetched separately in enrichment
        )
        
        result = registry.retrieval_service.search_standards(query)
        
        for candidate in result.candidates:
            if candidate.standard.id not in seen_ids:
                seen_ids.add(candidate.standard.id)
                retrieved_standards.append(candidate.standard)

    logger.info(
        "_step_retrieve: found %d distinct standards across %d requirements. analysis_id=%s",
        len(retrieved_standards), len(analysis.requirements), analysis.id,
    )
    
    return retrieved_standards


# ===========================================================================
# 3. Analyze (Step 8)
# ===========================================================================

async def _step_analyze(
    analysis: Analysis,
    extracted_text: str,
    retrieved_standards: list[Standard],
) -> AimlResponse | None:
    """
    Send requirements + retrieved standards to the AI/ML component for analysis.
    """
    await asyncio.sleep(0)

    if not analysis.requirements:
        logger.info(
            "_step_analyze: no requirements to analyze. analysis_id=%s",
            analysis.id,
        )
        return None

    logger.info(
        "_step_analyze: starting AI analysis for %d requirements against %d standards. analysis_id=%s",
        len(analysis.requirements),
        len(retrieved_standards),
        analysis.id,
    )
    
    from shared.contracts import AimlRequest
    from kshiraj.aiml_client.client import analyze_requirements
    from shared.utils import AnalysisError as _AnalysisError
    
    request = AimlRequest(
        analysis_id=analysis.id,
        extracted_text=extracted_text,
        requirements=analysis.requirements,
        retrieved_standards=retrieved_standards,
    )
    
    try:
        aiml_response = analyze_requirements(request)
        return aiml_response
    except _AnalysisError as exc:
        logger.warning(
            "_step_analyze: AI/ML call failed (%s). "
            "Falling back to compliance-only logic. analysis_id=%s",
            exc.code, analysis.id,
        )
        return None


# ===========================================================================
# 4. Enrich — Findings Assembly & Compliance Rules (Step 6/7)
# ===========================================================================

async def _step_enrich(
    analysis: Analysis,
    retrieved_standards: list[Standard],
    aiml_response: object,
) -> None:
    """
    Assemble final findings by merging AI/ML results with deterministic
    compliance checks against the retrieved standards.
    """
    await asyncio.sleep(0)

    from kartikey.orchestration.knowledge_registry import get_registry
    from kartikey.analysis.findings import assemble_findings

    registry = get_registry()

    # Pass lookup dicts to the assembler so it can resolve any ID the AI/ML returns
    # to a real object. This enforces the anti-hallucination guardrail.
    standards_lookup = {std.id: std for std in registry.standards_store.list_all()}
    # We fetch all evidence here; a production DB would use IN queries.
    evidence_lookup = {ev.id: ev for ev in registry.evidence_store.list_all()}

    findings = assemble_findings(
        analysis=analysis,
        retrieved_standards=retrieved_standards,
        aiml_response=aiml_response,
        standards_lookup=standards_lookup,
        evidence_lookup=evidence_lookup,
    )
    analysis.findings = findings

    logger.info(
        "_step_enrich: assembled %d findings for analysis_id=%s "
        "(AI/ML wired=%s, retrieved_standards=%d)",
        len(findings),
        analysis.id,
        aiml_response is not None,
        len(retrieved_standards),
    )


# ===========================================================================
# Internal helpers
# ===========================================================================

def _transition(analysis: Analysis, new_status: AnalysisStatus) -> None:
    """Update analysis status and timestamp, and log the transition."""
    old = analysis.status.value
    analysis.status = new_status
    analysis.updated_at = utcnow()
    logger.info(
        "Analysis %s: %s → %s",
        analysis.id, old, new_status.value,
    )
