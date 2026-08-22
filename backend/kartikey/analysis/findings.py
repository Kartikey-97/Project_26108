"""
Buyer-side findings assembler.

Receives:
  - AI/ML output (AimlResponse)
  - Enrichment data (version info, cross-references from kshiraj/enrichment)
  - Evidence records (from kshiraj/knowledge/evidence_store)

Produces:
  - List[Finding] with full evidence attached

IMPORTANT: This is where we prevent LLM hallucination from reaching the API.
AI/ML returns evidence_ids and standard_ids — we fetch the real records here.
"""

from __future__ import annotations

from shared.contracts import AimlResponse
from shared.models import Evidence, Finding, Standard, Verdict
from shared.utils import get_logger

logger = get_logger(__name__)


def assemble_findings(
    aiml_response: AimlResponse,
    standards_by_id: dict[str, Standard],
    evidence_by_id: dict[str, Evidence],
) -> list[Finding]:
    """
    Assemble final Finding objects from AI/ML output + retrieved records.

    Parameters
    ----------
    aiml_response:
        Structured output from the AI/ML component.
    standards_by_id:
        Map of standard_id → Standard (fetched from DB, not LLM-generated).
    evidence_by_id:
        Map of evidence_id → Evidence (fetched from DB, not LLM-generated).

    Returns
    -------
    list[Finding]
        Evidence-grounded findings ready for the API response.
    """
    findings: list[Finding] = []

    for item in aiml_response.findings:
        try:
            verdict = Verdict(item.verdict)
        except ValueError:
            logger.warning("Unknown verdict '%s' from AI/ML — defaulting to UNABLE_TO_DETERMINE", item.verdict)
            verdict = Verdict.UNABLE_TO_DETERMINE

        standards = [standards_by_id[sid] for sid in item.applicable_standard_ids if sid in standards_by_id]
        evidence = [evidence_by_id[eid] for eid in item.evidence_ids if eid in evidence_by_id]

        if len(standards) < len(item.applicable_standard_ids):
            logger.warning(
                "Finding %s: %d standard IDs not found in DB",
                item.finding_id,
                len(item.applicable_standard_ids) - len(standards),
            )

        findings.append(
            Finding(
                id=item.finding_id,
                requirement_id=item.requirement_id,
                verdict=verdict,
                reason=item.reason,
                applicable_standards=standards,
                evidence=evidence,
                confidence=item.confidence,
                recommended_action=item.recommended_action,
                requires_human_verification=(
                    verdict in {Verdict.UNABLE_TO_DETERMINE, Verdict.REQUIRES_HUMAN_VERIFICATION}
                    or item.confidence < 0.6
                ),
            )
        )

    return findings
