"""
Evidence/provenance mapping.

This module only exposes evidence that is actually present in the
knowledge-base record. It does not invent clauses, page numbers,
URLs, or applicability statements.
"""

from __future__ import annotations

from typing import Any, Dict, List


def _evidence(
    *,
    standard: Dict[str, Any],
    field: str,
    value: Any,
    evidence_type: str,
    authoritative: bool,
    note: str = "",
) -> Dict[str, Any]:
    source = standard.get("source") or {}
    return {
        "field": field,
        "value": value,
        "evidence_type": evidence_type,
        "authoritative": authoritative,
        "source": {
            "organization": source.get("organization"),
            "source_type": source.get("source_type"),
            "url": source.get("url"),
            "verified": bool(source.get("verified")),
        },
        "note": note,
    }


def build_evidence_map(
    standard: Dict[str, Any],
    requirement_text: str,
) -> List[Dict[str, Any]]:
    evidence: List[Dict[str, Any]] = []

    # Exact structured fields are stronger than derived search text.
    if standard.get("scope"):
        evidence.append(
            _evidence(
                standard=standard,
                field="scope",
                value=standard["scope"],
                evidence_type="scope",
                authoritative=bool(
                    (standard.get("source") or {}).get("verified")
                ),
                note="Scope supplied by the knowledge-base record.",
            )
        )

    if standard.get("scope_summary"):
        evidence.append(
            _evidence(
                standard=standard,
                field="scope_summary",
                value=standard["scope_summary"],
                evidence_type="derived_summary",
                authoritative=False,
                note="Derived summary; do not treat as an authoritative clause.",
            )
        )

    if standard.get("normative_references"):
        evidence.append(
            _evidence(
                standard=standard,
                field="normative_references",
                value=standard["normative_references"],
                evidence_type="normative_reference",
                authoritative=bool(
                    (standard.get("source") or {}).get("verified")
                ),
                note="Only references stored in the record are returned.",
            )
        )

    if standard.get("related_standards"):
        evidence.append(
            _evidence(
                standard=standard,
                field="related_standards",
                value=standard["related_standards"],
                evidence_type="related_standard",
                authoritative=bool(
                    (standard.get("source") or {}).get("verified")
                ),
                note="Relationship is reported as stored; it is not inferred from similarity.",
            )
        )

    if standard.get("test_methods"):
        evidence.append(
            _evidence(
                standard=standard,
                field="test_methods",
                value=standard["test_methods"],
                evidence_type="test_method",
                authoritative=bool(
                    (standard.get("source") or {}).get("verified")
                ),
            )
        )

    version = standard.get("version") or {}
    if version:
        evidence.append(
            _evidence(
                standard=standard,
                field="version",
                value=version,
                evidence_type="version_record",
                authoritative=bool(
                    (standard.get("source") or {}).get("verified")
                    and version.get("verification_status") == "verified"
                ),
                note="Version information is reported with its verification status.",
            )
        )

    status = standard.get("status") or {}
    if status:
        evidence.append(
            _evidence(
                standard=standard,
                field="status",
                value=status,
                evidence_type="status_record",
                authoritative=bool(
                    status.get("verified")
                    and (standard.get("source") or {}).get("verified")
                ),
                note="Status is not treated as confirmed when the record says it is unverified.",
            )
        )

    certification = standard.get("certification") or {}
    if certification:
        evidence.append(
            _evidence(
                standard=standard,
                field="certification",
                value=certification,
                evidence_type="certification_record",
                authoritative=bool(
                    certification.get("verified")
                    and (standard.get("source") or {}).get("verified")
                ),
                note="Certification/QCO applicability is only confirmed when verified in the record.",
            )
        )

    if standard.get("source"):
        evidence.append(
            _evidence(
                standard=standard,
                field="source",
                value=standard["source"],
                evidence_type="record_source",
                authoritative=bool(
                    (standard.get("source") or {}).get("verified")
                ),
                note="Knowledge-base provenance.",
            )
        )

    if not evidence:
        evidence.append(
            _evidence(
                standard=standard,
                field="none",
                value=None,
                evidence_type="missing",
                authoritative=False,
                note="No supporting structured evidence is available.",
            )
        )

    return evidence


def evidence_summary(evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    authoritative_count = sum(
        1 for item in evidence if item.get("authoritative")
    )
    return {
        "evidence_count": len(evidence),
        "authoritative_evidence_count": authoritative_count,
        "has_authoritative_evidence": authoritative_count > 0,
    }
