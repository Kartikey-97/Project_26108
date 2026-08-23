"""
kshiraj/aiml_client/client.py

AI/ML client that orchestrates the LLM interaction for analyzing requirements
against retrieved standards.

This module implements the backend → AI/ML boundary.
It receives an AimlRequest, formats the context for the LLM, parses the
structured response, and returns an AimlResponse.

CRITICAL GUARDRAIL:
The LLM returns only standard_ids and evidence_ids. The backend resolves these
into actual objects in the enrichment step. This is how we prevent the LLM
from hallucinating evidence text.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from shared.contracts import AimlFinding, AimlRequest, AimlResponse
from shared.models import Verdict
from shared.utils import AnalysisError, get_logger

from kartikey.analysis.llm_client import get_llm_client

logger = get_logger(__name__)


# ===========================================================================
# Prompts
# ===========================================================================

_SYSTEM_PROMPT = """You are an expert Indian procurement and standardization officer.
Your job is to evaluate procurement tender requirements against authoritative BIS (Bureau of Indian Standards) data.

You will be provided with:
1. A list of REQUIREMENTS extracted from a tender document.
2. A list of RETRIEVED STANDARDS from the knowledge base.

For EACH requirement, you must return a structured evaluation.

EVALUATION RULES:
1. Compare the requirement against the retrieved standards.
2. Determine if the requirement cites the correct, current standard, or if it is outdated, missing mandatory certifications (like QCOs), or completely wrong.
3. If the requirement cites an IS number, look it up in the retrieved standards.
4. If the requirement does NOT cite an IS number but describes a product/test (e.g. "IP65", "Power factor > 0.9"), check if any of the retrieved standards cover that.
5. If you cannot determine the answer from the retrieved standards, use "unable_to_determine".
6. DO NOT invent or guess. Only rely on the provided retrieved standards.

OUTPUT FORMAT:
Return a JSON array of objects, one for each requirement, matching exactly this structure:
[
  {
    "requirement_id": "string (copy from input)",
    "verdict": "string (must be one of the exact verdict codes below)",
    "reason": "string (brief explanation)",
    "applicable_standard_ids": ["string (copy standard IDs from retrieved standards that apply)"],
    "confidence": 0.0 to 1.0
  }
]

VERDICT CODES:
- justified: The requirement is correct and current.
- outdated_reference: The requirement cites an older year of a standard that has been updated or superseded.
- missing_requirement: The tender completely missed a mandatory standard (e.g. QCO).
- ambiguous: Unclear or missing year.
- potentially_over_restrictive: Requires something beyond normal standards without clear need.
- incorrect_standard: Cites a withdrawn standard or one that does not apply.
- unable_to_determine: Not enough information in the retrieved standards to judge.
"""


def _format_request_prompt(request: AimlRequest) -> str:
    """Format the AimlRequest into a prompt string for the LLM."""
    prompt_parts = []
    
    prompt_parts.append("=== RETRIEVED STANDARDS (KNOWLEDGE BASE) ===")
    if not request.retrieved_standards:
        prompt_parts.append("None retrieved.")
    else:
        for std in request.retrieved_standards:
            prompt_parts.append(
                f"Standard ID: {std.id}\n"
                f"Designation: {std.designation}\n"
                f"Title: {std.title}\n"
                f"Status: {std.status.value}\n"
                f"QCO Notified: {std.qco_notified}\n"
                f"Scope: {std.scope}\n"
                "---"
            )

    prompt_parts.append("\n=== TENDER REQUIREMENTS ===")
    if not request.requirements:
        prompt_parts.append("No requirements extracted.")
    else:
        for req in request.requirements:
            prompt_parts.append(
                f"Requirement ID: {req.id}\n"
                f"Text: {req.text}\n"
                f"Cited Reference: {req.is_reference or 'None'}\n"
                f"Cited Year: {req.cited_year or 'None'}\n"
                "---"
            )
            
    return "\n".join(prompt_parts)


# ===========================================================================
# Public API
# ===========================================================================

def analyze_requirements(request: AimlRequest) -> AimlResponse:
    """
    Analyze extracted requirements against retrieved standards using the LLM.
    
    This runs synchronously but could be made async if needed.
    """
    logger.info(
        "analyze_requirements: starting analysis for analysis_id=%s "
        "(%d requirements, %d retrieved standards)",
        request.analysis_id,
        len(request.requirements),
        len(request.retrieved_standards),
    )
    
    if not request.requirements:
        return AimlResponse(
            analysis_id=request.analysis_id,
            findings=[],
            extraction_metadata={"note": "No requirements provided"}
        )

    # 1. Format prompt
    user_prompt = _format_request_prompt(request)
    
    # 2. Call LLM
    client = get_llm_client()
    start_time = datetime.now(tz=timezone.utc)
    
    try:
        raw_json = client.generate_json(
            prompt=user_prompt,
            system_prompt=_SYSTEM_PROMPT,
            temperature=0.1,  # Low temp for deterministic logic
        )
    except AnalysisError as e:
        logger.error("AI/ML call failed: %s", e)
        raise

    end_time = datetime.now(tz=timezone.utc)
    duration_ms = int((end_time - start_time).total_seconds() * 1000)

    # 3. Parse and validate response
    if not isinstance(raw_json, list):
        logger.error("AI/ML returned non-list JSON: %s", type(raw_json))
        raw_json = [raw_json] if isinstance(raw_json, dict) else []

    findings: list[AimlFinding] = []
    
    # Valid verdict strings mapping
    valid_verdicts = {v.value for v in Verdict}

    for item in raw_json:
        if not isinstance(item, dict):
            continue
            
        req_id = item.get("requirement_id")
        if not req_id:
            continue
            
        raw_verdict = str(item.get("verdict", "")).lower()
        if raw_verdict not in valid_verdicts:
            raw_verdict = Verdict.UNABLE_TO_DETERMINE.value
            
        std_ids = item.get("applicable_standard_ids", [])
        if not isinstance(std_ids, list):
            std_ids = []
            
        confidence = item.get("confidence", 0.5)
        try:
            confidence = float(confidence)
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            confidence = 0.5

        finding = AimlFinding(
            finding_id=f"fnd_{req_id[:8]}",  # Deterministic ID for tracing
            requirement_id=req_id,
            verdict=raw_verdict,
            reason=str(item.get("reason", "No reason provided by AI.")),
            applicable_standard_ids=[str(s) for s in std_ids],
            evidence_ids=[],  # We rely on backend enrichment to supply evidence
            confidence=confidence,
        )
        findings.append(finding)

    logger.info(
        "analyze_requirements: finished in %dms. Generated %d findings.",
        duration_ms, len(findings),
    )

    return AimlResponse(
        analysis_id=request.analysis_id,
        findings=findings,
        extraction_metadata={
            "duration_ms": duration_ms,
            "model_used": client._working_model,
        }
    )
