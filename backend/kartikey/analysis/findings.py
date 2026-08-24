"""
kartikey/analysis/findings.py

Findings assembler — the final step in the analysis pipeline.

This module takes:
  1. AI/ML output (AimlResponse with per-requirement findings + evidence_ids/standard_ids)
  2. Compliance check results (version, status, QCO — all deterministic)
  3. Retrieved standards from the knowledge base

And produces:
  Final Finding objects with full evidence chains that are returned to the frontend.

The assembly process has a strict rule:
  The LLM may SUGGEST a verdict. The compliance checks may OVERRIDE it.
  Whichever is more severe (more confident in a problem) wins.
  This ensures that database facts always beat LLM reasoning for factual questions.

Evidence assembly rule:
  AI/ML returns evidence_ids and standard_ids (references to DB records).
  This assembler resolves those IDs against the knowledge stores.
  It NEVER uses LLM-generated evidence text directly in the final response.
  This is the core anti-hallucination guardrail of the system.

Current state (Step 6):
  AI/ML and knowledge retrieval are not yet wired (Steps 6-7).
  The assembler works on whatever is available:
  - If AI/ML is wired: uses AimlFindings to drive verdict + evidence
  - If not yet wired: uses compliance-only findings from retrieved standards
  This design means the assembler is useful and testable at every stage.
"""

from __future__ import annotations

from shared.contracts import AimlFinding, AimlResponse
from shared.models import (
    Analysis,
    Evidence,
    Finding,
    Requirement,
    Standard,
    Verdict,
)
from shared.utils import AnalysisError, get_logger

from kartikey.analysis.compliance import ComplianceResult, run_compliance_checks

logger = get_logger(__name__)


# ===========================================================================
# Public interface
# ===========================================================================

def assemble_findings(
    analysis: Analysis,
    retrieved_standards: list[Standard],
    aiml_response: AimlResponse | None,
    standards_lookup: dict[str, Standard],
    evidence_lookup: dict[str, Evidence],
) -> list[Finding]:
    """
    Assemble final Finding objects for an analysis.

    Parameters
    ----------
    analysis:
        The Analysis object (contains requirements).
    retrieved_standards:
        Standards retrieved by the knowledge layer, ranked by relevance.
    aiml_response:
        Optional response from the AI/ML component.
        None when AI/ML is not yet wired (Steps 1-6).
    standards_lookup:
        Dict of standard_id → Standard for resolving AI/ML references.
        Populated from the knowledge store.
    evidence_lookup:
        Dict of evidence_id → Evidence for resolving AI/ML references.
        Populated from the evidence store.

    Returns
    -------
    list[Finding]
        Final assembled findings with full evidence chains.
    """
    if not analysis.requirements:
        logger.info(
            "assemble_findings: no requirements to process for analysis_id=%s",
            analysis.id,
        )
        return []

    findings: list[Finding] = []

    if aiml_response is not None:
        # --- Path A: AI/ML is wired — use AI findings as primary, compliance as override ---
        findings = _assemble_with_aiml(
            analysis=analysis,
            aiml_response=aiml_response,
            retrieved_standards=retrieved_standards,
            standards_lookup=standards_lookup,
            evidence_lookup=evidence_lookup,
        )
    else:
        # --- Path B: AI/ML not yet wired — use compliance-only findings ---
        # This runs in Steps 5-6 before the AI/ML client is connected.
        # It still produces real, useful findings based on IS reference matches.
        findings = _assemble_compliance_only(
            analysis=analysis,
            retrieved_standards=retrieved_standards,
        )

    logger.info(
        "assemble_findings: produced %d findings for analysis_id=%s",
        len(findings), analysis.id,
    )
    return findings


# ===========================================================================
# Assembly paths
# ===========================================================================

def _assemble_with_aiml(
    analysis: Analysis,
    aiml_response: AimlResponse,
    retrieved_standards: list[Standard],
    standards_lookup: dict[str, Standard],
    evidence_lookup: dict[str, Evidence],
) -> list[Finding]:
    """
    Assemble findings using AI/ML output as the primary source.

    For each AimlFinding:
      1. Resolve standard_ids → Standard objects from the knowledge store
      2. Resolve evidence_ids → Evidence objects from the evidence store
      3. Run compliance checks on the matched standards (deterministic override)
      4. Merge: use stricter of (AI verdict, compliance verdict)
      5. Assemble final Finding with full evidence chain
    """
    # Build a quick lookup from requirement_id → Requirement
    req_lookup: dict[str, Requirement] = {r.id: r for r in analysis.requirements}

    findings: list[Finding] = []

    for aiml_finding in aiml_response.findings:
        req = req_lookup.get(aiml_finding.requirement_id)
        if not req:
            logger.warning(
                "AimlFinding references unknown requirement_id=%s — skipping.",
                aiml_finding.requirement_id,
            )
            continue

        # Resolve standard IDs
        applicable_standards: list[Standard] = []
        for sid in aiml_finding.applicable_standard_ids:
            std = standards_lookup.get(sid)
            if std:
                applicable_standards.append(std)
            else:
                logger.warning(
                    "AimlFinding references unknown standard_id=%s — skipping.", sid,
                )

        # Resolve evidence IDs — anti-hallucination guardrail
        ai_evidence: list[Evidence] = []
        for eid in aiml_finding.evidence_ids:
            ev = evidence_lookup.get(eid)
            if ev:
                ai_evidence.append(ev)
            else:
                logger.warning(
                    "AimlFinding references unknown evidence_id=%s — skipping.", eid,
                )

        # Run compliance checks on matched standards
        compliance_results: list[ComplianceResult] = []
        for std in applicable_standards:
            try:
                result = run_compliance_checks(req, std)
                compliance_results.append(result)
            except Exception as exc:
                logger.error(
                    "Compliance check failed for req=%s std=%s: %s",
                    req.id[:8], std.designation, exc,
                )

        # Determine final verdict: AI vs compliance — stricter wins
        try:
            ai_verdict = Verdict(aiml_finding.verdict)
        except ValueError:
            logger.warning(
                "Unknown verdict '%s' from AI/ML — defaulting to UNABLE_TO_DETERMINE.",
                aiml_finding.verdict,
            )
            ai_verdict = Verdict.UNABLE_TO_DETERMINE

        final_verdict, final_confidence, verdict_source = _merge_verdicts(
            ai_verdict=ai_verdict,
            ai_confidence=aiml_finding.confidence,
            compliance_results=compliance_results,
        )

        # Collect all evidence
        all_evidence = list(ai_evidence)
        for cr in compliance_results:
            all_evidence.extend(cr.evidence)

        # Build currentness context
        currentness = _build_currentness_context(compliance_results)

        # Determine if human review is needed
        needs_human = (
            final_verdict == Verdict.REQUIRES_HUMAN_VERIFICATION
            or final_confidence < 0.60
            or any(cr.qco_check.qco_notified for cr in compliance_results)
        )

        finding = Finding(
            requirement_id=req.id,
            analysis_id=analysis.id,
            verdict=final_verdict,
            reason=_build_reason(
                aiml_finding=aiml_finding,
                compliance_results=compliance_results,
                verdict_source=verdict_source,
            ),
            recommended_action=_build_recommended_action(
                final_verdict, compliance_results,
            ),
            applicable_standards=applicable_standards,
            currentness=currentness,
            evidence=all_evidence,
            confidence=final_confidence,
            requires_human_verification=needs_human,
            verification_reason=(
                "Low confidence score or QCO-notified product requires officer review."
                if needs_human else None
            ),
        )
        findings.append(finding)

    return findings


def _assemble_compliance_only(
    analysis: Analysis,
    retrieved_standards: list[Standard],
) -> list[Finding]:
    """
    Assemble findings using only compliance checks (no AI/ML).

    For each requirement:
      - Match against retrieved standards by IS number
      - Run compliance checks on matched standards
      - Produce a Finding based purely on deterministic rules

    This path runs before the AI/ML client is connected.
    It produces real, useful findings for IS-citation requirements
    but cannot reason about non-IS requirements (performance specs, etc.)
    """
    # Build IS-number → [Standard] lookup from retrieved standards
    is_number_to_standards: dict[str, list[Standard]] = {}
    for std in retrieved_standards:
        key = std.is_number.strip().casefold()
        is_number_to_standards.setdefault(key, []).append(std)

    findings: list[Finding] = []

    for req in analysis.requirements:
        if not req.is_reference:
            # Can't do compliance checks without an IS reference
            finding = Finding(
                requirement_id=req.id,
                analysis_id=analysis.id,
                verdict=Verdict.UNABLE_TO_DETERMINE,
                reason=(
                    f"Requirement '{req.text[:80]}...' does not cite a specific Indian Standard. "
                    "Cannot perform automated compliance check. "
                    "Full AI analysis will assess this requirement when the AI/ML layer is wired."
                ),
                recommended_action="Review manually or wait for full AI analysis.",
                applicable_standards=[],
                currentness=None,
                evidence=[],
                confidence=0.0,
                requires_human_verification=True,
                verification_reason="No IS reference — cannot automate compliance check.",
            )
            findings.append(finding)
            continue

        # Find matching standards for this IS reference
        req_key = req.is_reference.strip().casefold()
        matched_standards = is_number_to_standards.get(req_key, [])

        if not matched_standards:
            # IS cited but not found in knowledge base
            finding = Finding(
                requirement_id=req.id,
                analysis_id=analysis.id,
                verdict=Verdict.UNABLE_TO_DETERMINE,
                reason=(
                    f"Standard '{req.is_reference}' cited in the tender was not found "
                    "in the knowledge base. Cannot verify its current status."
                ),
                recommended_action=(
                    "Verify this IS number on the BIS 'Know Your Standard' portal "
                    "(standardsbis.gov.in) and confirm it is active."
                ),
                applicable_standards=[],
                currentness=None,
                evidence=[],
                confidence=0.3,
                requires_human_verification=True,
                verification_reason=f"'{req.is_reference}' not found in knowledge base.",
            )
            findings.append(finding)
            continue

        # Run compliance checks on all matched standards
        compliance_results: list[ComplianceResult] = []
        for std in matched_standards:
            try:
                cr = run_compliance_checks(req, std)
                compliance_results.append(cr)
            except Exception as exc:
                logger.error(
                    "Compliance check failed: req=%s std=%s: %s",
                    req.id[:8], std.designation, exc,
                )

        if not compliance_results:
            findings.append(Finding(
                requirement_id=req.id,
                analysis_id=analysis.id,
                verdict=Verdict.UNABLE_TO_DETERMINE,
                reason="Compliance checks could not be completed.",
                recommended_action="Review manually.",
                applicable_standards=matched_standards,
                evidence=[],
                confidence=0.0,
                requires_human_verification=True,
                verification_reason="Compliance check error.",
            ))
            continue

        # Use the most severe compliance result
        best_cr = min(compliance_results, key=lambda cr: _verdict_severity(cr.suggested_verdict))
        all_evidence = [ev for cr in compliance_results for ev in cr.evidence]

        needs_human = (
            best_cr.suggested_verdict == Verdict.REQUIRES_HUMAN_VERIFICATION
            or best_cr.confidence < 0.60
            or any(cr.qco_check.qco_notified for cr in compliance_results)
        )

        finding = Finding(
            requirement_id=req.id,
            analysis_id=analysis.id,
            verdict=best_cr.suggested_verdict,
            reason=_build_compliance_reason(req, compliance_results),
            recommended_action=_build_recommended_action(best_cr.suggested_verdict, compliance_results),
            applicable_standards=matched_standards,
            currentness=_build_currentness_context(compliance_results),
            evidence=all_evidence,
            confidence=best_cr.confidence,
            requires_human_verification=needs_human,
            verification_reason=(
                "QCO-notified product or low confidence — officer review recommended."
                if needs_human else None
            ),
        )
        findings.append(finding)

    return findings


# ===========================================================================
# Verdict merging
# ===========================================================================

# Severity order — lower index = more severe problem
_VERDICT_SEVERITY_ORDER = [
    Verdict.INCORRECT_STANDARD,
    Verdict.CONFLICTING,
    Verdict.OUTDATED_REFERENCE,
    Verdict.WRONG_SCOPE,
    Verdict.MISSING_REQUIREMENT,
    Verdict.POTENTIALLY_OVER_RESTRICTIVE,
    Verdict.POTENTIALLY_UNNECESSARY,
    Verdict.UNSUPPORTED,
    Verdict.AMBIGUOUS,
    Verdict.REQUIRES_HUMAN_VERIFICATION,
    Verdict.UNABLE_TO_DETERMINE,
    Verdict.JUSTIFIED,
]


def _verdict_severity(verdict: Verdict) -> int:
    """Lower return value = more severe."""
    try:
        return _VERDICT_SEVERITY_ORDER.index(verdict)
    except ValueError:
        return len(_VERDICT_SEVERITY_ORDER)


def _merge_verdicts(
    ai_verdict: Verdict,
    ai_confidence: float,
    compliance_results: list[ComplianceResult],
) -> tuple[Verdict, float, str]:
    """
    Choose the final verdict from AI verdict and compliance verdicts.
    The more severe (higher priority in severity order) verdict wins.

    Returns (final_verdict, final_confidence, source_description)
    """
    if not compliance_results:
        return ai_verdict, ai_confidence, "ai_only"

    # Find the most severe compliance verdict
    best_compliance = min(
        compliance_results,
        key=lambda cr: _verdict_severity(cr.suggested_verdict),
    )

    ai_severity = _verdict_severity(ai_verdict)
    compliance_severity = _verdict_severity(best_compliance.suggested_verdict)

    if compliance_severity < ai_severity:
        # Compliance check found a more severe issue — override AI
        return best_compliance.suggested_verdict, best_compliance.confidence, "compliance_override"
    elif ai_severity < compliance_severity:
        # AI found something the compliance rules didn't catch
        return ai_verdict, ai_confidence, "ai_primary"
    else:
        # Same severity — average confidences, keep AI reasoning
        avg_confidence = (ai_confidence + best_compliance.confidence) / 2
        return ai_verdict, avg_confidence, "ai_and_compliance_agree"


# ===========================================================================
# Text builders
# ===========================================================================

def _build_reason(
    aiml_finding: AimlFinding,
    compliance_results: list[ComplianceResult],
    verdict_source: str,
) -> str:
    parts = [aiml_finding.reason]

    if verdict_source == "compliance_override" and compliance_results:
        best = min(compliance_results, key=lambda cr: _verdict_severity(cr.suggested_verdict))
        parts.append(f"[Compliance override] {best.version_check.note}")
        parts.append(f"[Status] {best.status_check.note}")
        if best.qco_check.qco_notified:
            parts.append(f"[QCO] {best.qco_check.note}")
    elif compliance_results:
        best = min(compliance_results, key=lambda cr: _verdict_severity(cr.suggested_verdict))
        if not best.version_check.is_current:
            parts.append(f"[Version] {best.version_check.note}")
        if best.qco_check.qco_notified:
            parts.append(f"[QCO] {best.qco_check.note}")

    return " ".join(parts)


def _build_compliance_reason(
    requirement: Requirement,
    compliance_results: list[ComplianceResult],
) -> str:
    """Build a human-readable reason from compliance-only results."""
    if not compliance_results:
        return "No compliance data available."

    best = min(compliance_results, key=lambda cr: _verdict_severity(cr.suggested_verdict))
    parts = [best.version_check.note, best.status_check.note]
    if best.qco_check.qco_notified:
        parts.append(best.qco_check.note)

    return " ".join(parts)


def _build_recommended_action(
    verdict: Verdict,
    compliance_results: list[ComplianceResult],
) -> str | None:
    """Build a recommended action for the procurement officer."""
    qco_notified = any(cr.qco_check.qco_notified for cr in compliance_results)
    superseded_by = next(
        (cr.status_check.superseded_by for cr in compliance_results
         if cr.status_check.superseded_by), None,
    )

    actions = {
        Verdict.JUSTIFIED: (
            "No action required. Standard reference appears correct and current."
            + (" Ensure BIS certification (CM/L or R-number) is explicitly required in bid documents." if qco_notified else "")
        ),
        Verdict.OUTDATED_REFERENCE: (
            f"Update the IS reference to the current edition"
            + (f": {superseded_by}" if superseded_by else "")
            + ". Verify on standardsbis.gov.in."
        ),
        Verdict.INCORRECT_STANDARD: (
            "This standard has been withdrawn by BIS and cannot be used. "
            "Remove this requirement and identify the correct replacement standard."
        ),
        Verdict.MISSING_REQUIREMENT: (
            "Add the applicable IS standard to the technical specification. "
            + ("This is mandatory due to a QCO notification." if qco_notified else "")
        ),
        Verdict.AMBIGUOUS: (
            "Specify the year of the IS edition to avoid disputes during bid evaluation."
        ),
        Verdict.REQUIRES_HUMAN_VERIFICATION: (
            "Flag for senior procurement officer review before finalizing the tender."
        ),
        Verdict.POTENTIALLY_OVER_RESTRICTIVE: (
            "Review whether this requirement narrows competition unreasonably. "
            "Consider accepting equivalent international standards."
        ),
        Verdict.UNABLE_TO_DETERMINE: (
            "Verify this requirement manually. "
            "Check the BIS portal (standardsbis.gov.in) for current status."
        ),
    }
    return actions.get(verdict, "Review this requirement.")


def _build_currentness_context(compliance_results: list[ComplianceResult]) -> dict | None:
    """Build the 'currentness' dict for a finding from compliance results."""
    if not compliance_results:
        return None

    best = min(compliance_results, key=lambda cr: _verdict_severity(cr.suggested_verdict))
    vc = best.version_check
    sc = best.status_check

    return {
        "cited_year": vc.cited_year,
        "current_year": vc.current_year,
        "is_current": vc.is_current,
        "year_omitted": vc.is_year_omitted,
        "gap_years": vc.gap_years,
        "status": sc.status.value,
        "superseded_by": sc.superseded_by,
        "transition_deadline": sc.transition_deadline.isoformat() if sc.transition_deadline else None,
        "within_transition": sc.within_transition,
        "qco_notified": best.qco_check.qco_notified,
        "qco_ministry": best.qco_check.issuing_ministry,
    }
