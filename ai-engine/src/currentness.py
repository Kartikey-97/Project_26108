"""
ai-engine/src/currentness.py

Deterministic currentness verification engine.

Given a standard record from the knowledge base (and optionally a year cited
in the tender), this module checks:
  - Whether the standard has been superseded
  - Whether the cited year/edition is the latest known
  - Whether amendments are available
  - Whether status is Active / Withdrawn / Superseded

Returns a structured CurrentnessVerdict dict — no AI involved.
"""

import logging
from datetime import date

logger = logging.getLogger(__name__)

# Verdict constants
UP_TO_DATE = "up_to_date"
OUTDATED_REFERENCE = "outdated_reference"
SUPERSEDED = "superseded"
AMENDMENT_AVAILABLE = "amendment_available"
WITHDRAWN = "withdrawn"
UNVERIFIABLE = "unverifiable"


def check_currentness(standard_record: dict, cited_year: int | None = None) -> dict:
    """
    Verify the currentness of a standard record.

    Parameters
    ----------
    standard_record : dict
        A record from bis_50_knowledge_base.json or the raw BIS catalogue.
    cited_year : int | None
        The year cited in the tender (e.g. 2018 for "IS 10322:2018").
        If None, only checks whether the record itself is current.

    Returns
    -------
    dict with keys:
        verdict       : str  — one of the verdict constants above
        message       : str  — human-readable explanation
        latest_edition: str | None
        latest_year   : int | None
        amendments    : list[str]
        confidence    : float — how certain we are (based on verification_status)
    """
    is_number = standard_record.get("is_number", "unknown")
    version = standard_record.get("version") or {}
    status_data = standard_record.get("status") or {}
    amendments = standard_record.get("amendments") or []

    latest_edition = version.get("latest_known_edition")
    latest_year = version.get("latest_known_year")
    superseded_by = version.get("superseded_by")
    verification_status = version.get("verification_status", "not_verified")
    status_value = status_data.get("value", "").lower()

    # Confidence: verified records are high-confidence; others are medium
    confidence = 0.9 if verification_status == "verified" else 0.6

    # -----------------------------------------------------------------------
    # 1. Withdrawn / Superseded by another standard
    # -----------------------------------------------------------------------
    if status_value in ("withdrawn", "cancelled"):
        return {
            "verdict": WITHDRAWN,
            "message": f"{is_number} has been withdrawn and is no longer active.",
            "latest_edition": latest_edition,
            "latest_year": latest_year,
            "amendments": amendments,
            "confidence": confidence,
        }

    if superseded_by:
        return {
            "verdict": SUPERSEDED,
            "message": (
                f"{is_number} has been superseded by {superseded_by}. "
                "Update the tender specification to reference the current standard."
            ),
            "latest_edition": superseded_by,
            "latest_year": latest_year,
            "amendments": amendments,
            "confidence": confidence,
        }

    # -----------------------------------------------------------------------
    # 2. Cited year is older than the latest known edition
    # -----------------------------------------------------------------------
    if cited_year and latest_year and cited_year < latest_year:
        return {
            "verdict": OUTDATED_REFERENCE,
            "message": (
                f"Tender cites {is_number}:{cited_year}, but the latest known edition is "
                f"{latest_edition or is_number}:{latest_year}. "
                "Consider updating the specification."
            ),
            "latest_edition": latest_edition,
            "latest_year": latest_year,
            "amendments": amendments,
            "confidence": confidence,
        }

    # -----------------------------------------------------------------------
    # 3. Amendments available
    # -----------------------------------------------------------------------
    if amendments:
        amendment_list = ", ".join(str(a) for a in amendments[:3])
        return {
            "verdict": AMENDMENT_AVAILABLE,
            "message": (
                f"{is_number} has {len(amendments)} amendment(s) available "
                f"({amendment_list}). Verify whether they affect your specification."
            ),
            "latest_edition": latest_edition,
            "latest_year": latest_year,
            "amendments": amendments,
            "confidence": confidence,
        }

    # -----------------------------------------------------------------------
    # 4. Cannot verify (insufficient metadata)
    # -----------------------------------------------------------------------
    if verification_status == "not_verified" and not latest_year:
        return {
            "verdict": UNVERIFIABLE,
            "message": (
                f"Currentness of {is_number} could not be automatically verified — "
                "manual check on bis.gov.in is recommended."
            ),
            "latest_edition": latest_edition,
            "latest_year": latest_year,
            "amendments": amendments,
            "confidence": 0.4,
        }

    # -----------------------------------------------------------------------
    # 5. Up to date
    # -----------------------------------------------------------------------
    return {
        "verdict": UP_TO_DATE,
        "message": (
            f"{is_number} appears current"
            + (f" (latest edition: {latest_edition}:{latest_year})" if latest_year else "")
            + "."
        ),
        "latest_edition": latest_edition,
        "latest_year": latest_year,
        "amendments": amendments,
        "confidence": confidence,
    }


def check_explicit_reference(is_ref: str, cited_year: int | None, standards: list[dict]) -> dict | None:
    """
    When the tender explicitly cites an IS number, find it in the knowledge
    base and run a currentness check.

    Returns the CurrentnessVerdict dict, or None if the standard is not found.
    """
    ref_lower = is_ref.strip().lower().replace(" ", "")
    for std in standards:
        std_num = std.get("is_number", "").lower().replace(" ", "").replace(":", "")
        if ref_lower.replace(":", "") in std_num or std_num in ref_lower.replace(":", ""):
            return check_currentness(std, cited_year=cited_year)
    return None
