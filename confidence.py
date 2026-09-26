"""
Confidence classification.

Confidence describes how strongly the system can support its result.
It is NOT a legal applicability decision.
"""

from __future__ import annotations

from typing import Any, Dict, List


def classify_confidence(
    relevance_score: float,
    evidence: List[Dict[str, Any]],
    issues: List[Dict[str, Any]],
) -> Dict[str, Any]:
    verified_evidence = sum(
        1 for item in evidence if item.get("authoritative")
    )

    high_issues = sum(
        1 for issue in issues
        if issue.get("severity") == "HIGH"
    )

    medium_issues = sum(
        1 for issue in issues
        if issue.get("severity") == "MEDIUM"
    )

    score = float(relevance_score)

    if high_issues:
        level = "REQUIRES_HUMAN_REVIEW"
    elif score >= 0.70 and verified_evidence >= 1:
        level = "HIGH"
    elif score >= 0.50:
        level = "MEDIUM"
    else:
        level = "LOW"

    if high_issues:
        reason = "High-severity evidence or verification issue detected."
    elif verified_evidence == 0:
        reason = "No verified/authoritative evidence is attached."
    elif medium_issues:
        reason = "Relevant evidence exists, but some verification gaps remain."
    else:
        reason = "Relevance score and available evidence support the result."

    return {
        "level": level,
        "relevance_score": round(score, 6),
        "verified_evidence_count": verified_evidence,
        "high_severity_issue_count": high_issues,
        "medium_severity_issue_count": medium_issues,
        "requires_human_review": level == "REQUIRES_HUMAN_REVIEW",
        "reason": reason,
    }
