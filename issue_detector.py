"""
Evidence-aware issue detection.

Issues are deliberately phrased as alerts/review requirements rather
than unsupported legal conclusions.
"""

from __future__ import annotations

from typing import Any, Dict, List


def detect_issues(
    requirement: Dict[str, Any],
    standard: Dict[str, Any],
    evidence: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    status = standard.get("status") or {}
    version = standard.get("version") or {}
    certification = standard.get("certification") or {}
    source = standard.get("source") or {}

    if status and not status.get("verified"):
        issues.append({
            "type": "STATUS_UNVERIFIED",
            "severity": "MEDIUM",
            "message": "Standard status is present but not verified in the knowledge base.",
            "requires_human_review": True,
        })

    if version and version.get("verification_status") != "verified":
        issues.append({
            "type": "VERSION_UNVERIFIED",
            "severity": "MEDIUM",
            "message": "Version information is present but its verification status is not verified.",
            "requires_human_review": True,
        })

    if version.get("superseded_by"):
        issues.append({
            "type": "POSSIBLE_SUPERSESSION",
            "severity": "HIGH",
            "message": f"Record indicates a superseding standard: {version['superseded_by']}.",
            "requires_human_review": True,
        })

    if version.get("supersedes"):
        issues.append({
            "type": "VERSION_RELATIONSHIP",
            "severity": "LOW",
            "message": f"Record indicates that this standard supersedes: {version['supersedes']}.",
            "requires_human_review": False,
        })

    if not standard.get("scope"):
        issues.append({
            "type": "MISSING_SCOPE",
            "severity": "MEDIUM",
            "message": "No explicit scope is available in the record, so applicability cannot be fully evidenced from scope.",
            "requires_human_review": True,
        })

    if not evidence:
        issues.append({
            "type": "NO_EVIDENCE",
            "severity": "HIGH",
            "message": "No supporting evidence is available for this recommendation.",
            "requires_human_review": True,
        })

    if not any(item.get("authoritative") for item in evidence):
        issues.append({
            "type": "NO_VERIFIED_EVIDENCE",
            "severity": "HIGH",
            "message": "Supporting information exists, but none is marked as authoritative/verified.",
            "requires_human_review": True,
        })

    if certification and not certification.get("verified"):
        issues.append({
            "type": "CERTIFICATION_UNVERIFIED",
            "severity": "MEDIUM",
            "message": "Certification/QCO information is not verified in the record.",
            "requires_human_review": True,
        })

    if source and not source.get("verified"):
        issues.append({
            "type": "SOURCE_UNVERIFIED",
            "severity": "MEDIUM",
            "message": "The record's source metadata is not marked verified.",
            "requires_human_review": True,
        })

    explicit_refs = requirement.get("explicit_standard_references") or []
    is_number = str(standard.get("is_number") or "").lower()

    if explicit_refs and is_number:
        matched = any(
            ref.lower().replace(" ", "") in is_number.replace(" ", "")
            or is_number.replace(" ", "") in ref.lower().replace(" ", "")
            for ref in explicit_refs
        )
        if not matched:
            issues.append({
                "type": "EXPLICIT_STANDARD_MISMATCH",
                "severity": "HIGH",
                "message": "The tender text explicitly references a standard that does not match this candidate.",
                "requires_human_review": True,
            })

    return issues
