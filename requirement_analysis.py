"""
Deterministic requirement-level analysis for procurement text.

This is intentionally conservative. It extracts explicit signals from
the supplied text and does not claim that a standard is applicable.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


UNIT_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(W|kW|V|A|mm|cm|m|kg|lm|K|%)\b",
    re.IGNORECASE,
)

IS_PATTERN = re.compile(
    r"\bIS\s*[-:]?\s*\d+(?:\s*:\s*(?:Part|Sec|Section)\s*[\w:]+)?(?:\s*:\s*\d{4})?\b",
    re.IGNORECASE,
)


def _sentences(text: str) -> List[str]:
    return [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+|\n+", text or "")
        if s.strip()
    ]


def extract_requirements(text: str) -> List[Dict[str, Any]]:
    sentences = _sentences(text)
    requirements: List[Dict[str, Any]] = []

    for idx, sentence in enumerate(sentences, start=1):
        lower = sentence.lower()

        signals = {
            "product": any(
                term in lower
                for term in [
                    "led", "luminaire", "street light",
                    "lighting", "lamp", "light fitting"
                ]
            ),
            "specification": bool(UNIT_PATTERN.search(sentence)),
            "standard_reference": bool(IS_PATTERN.search(sentence)),
            "mandatory_language": any(
                term in lower
                for term in [
                    "shall", "must", "required", "conform",
                    "comply", "mandatory", "should"
                ]
            ),
        }

        if not any(signals.values()):
            continue

        units = [
            {
                "value": float(value),
                "unit": unit,
                "text": match.group(0),
            }
            for match in UNIT_PATTERN.finditer(sentence)
            for value, unit in [match.groups()]
        ]

        standard_refs = [
            match.group(0)
            for match in IS_PATTERN.finditer(sentence)
        ]

        requirements.append(
            {
                "requirement_id": f"REQ-{idx:03d}",
                "name": (
                    "LED/lighting procurement requirement"
                    if signals["product"]
                    else "Procurement requirement"
                ),
                "value": sentence,
                "unit": units[0]["unit"] if units else None,
                "specifications": units,
                "context": {
                    "source_type": "supplied_text",
                    "sentence_index": idx,
                },
                "source_location": {
                    "sentence_index": idx,
                    "text": sentence,
                },
                "explicit_standard_references": standard_refs,
                "signals": signals,
                "confidence": (
                    "HIGH"
                    if signals["mandatory_language"]
                    and (signals["product"] or signals["standard_reference"])
                    else "MEDIUM"
                ),
            }
        )

    return requirements


def analyze_requirement_text(text: str) -> Dict[str, Any]:
    requirements = extract_requirements(text)

    return {
        "input_text": text,
        "requirement_count": len(requirements),
        "requirements": requirements,
        "status": (
            "EXTRACTED"
            if requirements
            else "NO_STRUCTURED_REQUIREMENT_FOUND"
        ),
    }
