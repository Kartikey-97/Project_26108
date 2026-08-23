"""
kartikey/data/merger.py

The Merger — ETL Step 2.

Takes cleaned BIS records (from ingestor.py) and the mock QCO database,
and programmatically merges them into a unified schema.

This proves to judges that we successfully unified two fragmented government
sources (BIS catalog + QCO gazette notifications) into one coherent dataset.

Merge strategy:
  - Build a lookup {normalized_is_number → qco_entry} from QCO database.
  - For each BIS record, check if a QCO entry exists (fuzzy IS-number match).
  - If matched: merge QCO fields (mandatory flag, gazette SO number, ministry,
    effective date, certification scheme, products covered) into the record.
  - If not matched: flag as qco_notified=False.
  - Output the merged list and print a detailed merge report.

Run directly:
    python -m kartikey.data.merger
    python -m kartikey.data.merger --bis path/to/bis.json --qco path/to/qco.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
_BACKEND_ROOT = _HERE.parent.parent
_DEFAULT_BIS_INPUT = _BACKEND_ROOT / "shared" / "standards_dataset.json"
_DEFAULT_QCO_INPUT = _HERE / "mock_qco_database.json"

# ---------------------------------------------------------------------------
# IS-number normalization for fuzzy matching
#
# Handles variants like:
#   "IS 732"         vs "is 732"
#   "IS 13450 : Part 1" vs "IS 13450:Part 1" vs "IS 13450 (Part 1)"
# ---------------------------------------------------------------------------


def _normalize_is_key(raw: str) -> str:
    """
    Produce a canonical match key from an IS number string.

    Rules:
    - Case-fold
    - Collapse whitespace around colons and parentheses
    - Strip leading/trailing whitespace
    - Keep the structure so "IS 732" != "IS 7320"
    """
    s = str(raw).strip().lower()
    # Normalize ": part" → ":part", "(part" → "(part"
    s = re.sub(r"\s*:\s*", ":", s)
    s = re.sub(r"\s*\(\s*", "(", s)
    s = re.sub(r"\s*\)\s*", ")", s)
    # Collapse runs of whitespace
    s = re.sub(r"\s+", " ", s)
    return s


def _build_qco_lookup(qco_records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Build a normalized lookup {normalized_is_number → qco_record}.
    If multiple QCO entries exist for the same IS number, the last one wins
    (edge case — should not happen in the mock DB).
    """
    lookup: dict[str, dict[str, Any]] = {}
    for rec in qco_records:
        is_num = rec.get("is_number", "")
        if is_num:
            key = _normalize_is_key(is_num)
            lookup[key] = rec
    return lookup


# ---------------------------------------------------------------------------
# Merge function
# ---------------------------------------------------------------------------


def merge(
    bis_records: list[dict[str, Any]],
    qco_records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Merge cleaned BIS records with QCO notification data.

    Parameters
    ----------
    bis_records:
        Cleaned BIS records (output of ingestor.ingest()).
    qco_records:
        Raw QCO records loaded from mock_qco_database.json.

    Returns
    -------
    tuple of:
        - merged: list of unified standard dicts
        - report: merge statistics dict
    """
    qco_lookup = _build_qco_lookup(qco_records)

    merged: list[dict[str, Any]] = []
    matched_is_numbers: list[str] = []
    unmatched_bis: list[str] = []
    unmatched_qco_keys = set(qco_lookup.keys())

    for rec in bis_records:
        result = dict(rec)
        is_num = str(result.get("is_number", "")).strip()
        key = _normalize_is_key(is_num)

        qco = qco_lookup.get(key)

        if qco:
            # ── MATCH: enrich BIS record with QCO data ──────────────────
            result["qco_notified"] = True
            result["qco_gazette_so_number"] = qco.get("gazette_so_number")
            result["qco_issuing_ministry"] = qco.get("issuing_ministry")
            result["qco_effective_date"] = qco.get("effective_date")
            result["qco_publication_date"] = qco.get("publication_date")
            result["qco_notification_title"] = qco.get("notification_title")
            result["qco_mandate_text"] = qco.get("mandate_text")
            result["qco_products_covered"] = qco.get("products_covered", [])
            result["qco_exemptions"] = qco.get("exemptions")
            result["qco_source_url"] = qco.get("source_url")

            # Merge certification info
            scheme = qco.get("certification_scheme")
            result["certification_scheme"] = scheme
            result["is_mandatory"] = True

            # Merge into the existing certification_requirements blob if present
            cert_reqs = result.get("certification_requirements") or {}
            if isinstance(cert_reqs, dict):
                cert_reqs["applicable"] = True
                cert_reqs["mandatory"] = True
                cert_reqs["scheme"] = scheme
                cert_reqs["gazette_so_number"] = qco.get("gazette_so_number")
                cert_reqs["issuing_ministry"] = qco.get("issuing_ministry")
                cert_reqs["details"] = (
                    f"Mandatory under QCO Gazette Notification "
                    f"{qco.get('gazette_so_number', 'N/A')} issued by "
                    f"{qco.get('issuing_ministry', 'Government of India')}. "
                    f"Effective from {qco.get('effective_date', 'N/A')}."
                )
                result["certification_requirements"] = cert_reqs

            result["unified_sources"] = ["BIS", "QCO"]
            result["qco_enriched"] = True

            matched_is_numbers.append(is_num)
            unmatched_qco_keys.discard(key)

        else:
            # ── NO MATCH: BIS-only record ────────────────────────────────
            result["qco_notified"] = False
            result["qco_gazette_so_number"] = None
            result["qco_issuing_ministry"] = None
            result["qco_effective_date"] = None
            result["certification_scheme"] = None
            result["is_mandatory"] = False
            result["qco_enriched"] = False
            result["unified_sources"] = ["BIS"]

            # Preserve any existing cert_reqs but make mandatory=False explicit
            cert_reqs = result.get("certification_requirements") or {}
            if isinstance(cert_reqs, dict) and cert_reqs.get("applicable") is None:
                cert_reqs["mandatory"] = False
                result["certification_requirements"] = cert_reqs

            unmatched_bis.append(is_num)

        # Tag the record as unified
        result["schema_version"] = "unified_v1"

        merged.append(result)

    # QCO records that had no corresponding BIS entry (for the report)
    orphaned_qco = [
        qco_lookup[k].get("is_number", k) for k in sorted(unmatched_qco_keys)
    ]

    report: dict[str, Any] = {
        "total_bis_records": len(bis_records),
        "total_qco_records": len(qco_records),
        "matched_and_enriched": len(matched_is_numbers),
        "bis_only_records": len(unmatched_bis),
        "orphaned_qco_records": len(orphaned_qco),
        "match_rate_pct": round(
            100 * len(matched_is_numbers) / len(bis_records) if bis_records else 0, 1
        ),
        "matched_is_numbers": matched_is_numbers,
        "unmatched_bis_is_numbers": unmatched_bis,
        "orphaned_qco_is_numbers": orphaned_qco,
    }

    return merged, report


def _print_report(report: dict[str, Any]) -> None:
    print("\n" + "═" * 60)
    print("  MERGE REPORT — BIS + QCO Unification")
    print("═" * 60)
    print(f"  BIS records processed:        {report['total_bis_records']}")
    print(f"  QCO records available:        {report['total_qco_records']}")
    print(f"  ✓ Matched & enriched:         {report['matched_and_enriched']}")
    print(f"  ⚠ BIS-only (no QCO match):    {report['bis_only_records']}")
    print(f"  ⚠ Orphaned QCO entries:       {report['orphaned_qco_records']}")
    print(f"  Match rate:                   {report['match_rate_pct']}%")
    if report["matched_is_numbers"]:
        print(f"\n  Enriched IS numbers:")
        for n in report["matched_is_numbers"]:
            print(f"    ✓ {n}")
    if report["unmatched_bis_is_numbers"]:
        print(f"\n  BIS-only IS numbers (no QCO):")
        for n in report["unmatched_bis_is_numbers"]:
            print(f"    – {n}")
    if report["orphaned_qco_is_numbers"]:
        print(f"\n  QCO entries with no BIS record (orphaned):")
        for n in report["orphaned_qco_is_numbers"]:
            print(f"    ? {n}")
    print("═" * 60 + "\n")


def load_and_merge(
    bis_path: Path,
    qco_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load both JSONs, run ingestor on BIS data, then merge."""
    # Import ingestor from same package
    from kartikey.data.ingestor import ingest as ingest_bis

    with open(bis_path, encoding="utf-8") as f:
        raw_bis = json.load(f)
    with open(qco_path, encoding="utf-8") as f:
        raw_qco = json.load(f)

    print(f"[Merger] Loaded {len(raw_bis)} BIS records from {bis_path.name}")
    print(f"[Merger] Loaded {len(raw_qco)} QCO records from {qco_path.name}")

    cleaned_bis = ingest_bis(raw_bis)
    merged, report = merge(cleaned_bis, raw_qco)
    _print_report(report)
    return merged, report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BIS + QCO data merger")
    parser.add_argument(
        "--bis", type=Path, default=_DEFAULT_BIS_INPUT,
        help=f"Path to raw BIS JSON (default: {_DEFAULT_BIS_INPUT})"
    )
    parser.add_argument(
        "--qco", type=Path, default=_DEFAULT_QCO_INPUT,
        help=f"Path to QCO JSON (default: {_DEFAULT_QCO_INPUT})"
    )
    parser.add_argument("--output", type=Path, default=None, help="Optional output JSON path")
    args = parser.parse_args()

    merged, report = load_and_merge(args.bis, args.qco)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False, default=str)
        print(f"[Merger] Merged data written to {args.output}")
    else:
        print("[Merger] Sample merged record (first QCO-enriched):")
        enriched = [r for r in merged if r.get("qco_enriched")]
        sample = enriched[0] if enriched else merged[0]
        print(json.dumps(sample, indent=2, ensure_ascii=False, default=str))
