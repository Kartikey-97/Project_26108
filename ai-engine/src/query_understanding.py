"""
ai-engine/src/query_understanding.py

Converts a raw procurement query / tender excerpt into a structured
QueryUnderstanding dict that drives retrieval, ranking, and gap detection.

Strategy:
  1. Try Gemini to produce a richly-structured JSON understanding.
  2. Fall back to an improved regex extractor if Gemini is unavailable.

The regex fallback is *substantially* more capable than the old version —
it handles `220 V`, `IP 66`, `6500 K`, `≤ 10 %`, `130 lm/W`, etc.
"""

import json
import logging
import os
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex-based fallback extractor
# ---------------------------------------------------------------------------

# Compiled patterns for common procurement parameters
_PATTERNS = {
    # Power:  120W  /  120 W  /  120 watt  /  120 watts
    "power": re.compile(
        r"(\d+(?:\.\d+)?)\s*(?:W\b|watts?\b|watt\b)", re.IGNORECASE
    ),
    # Voltage:  230V  /  140V-270V  /  220 volts
    "voltage": re.compile(
        r"(\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?)\s*(?:V\b|volts?\b|VAC\b|Vac\b)",
        re.IGNORECASE,
    ),
    # IP rating:  IP 66  /  IP66  /  IP-65
    "ip_rating": re.compile(r"\bIP[\s\-]?(\d{2})\b", re.IGNORECASE),
    # Color temperature:  5700K  /  6500 K  /  6500°K
    "cct": re.compile(r"(\d{4,5})\s*(?:°?\s*K\b)", re.IGNORECASE),
    # Luminous efficacy:  130 lm/W  /  130 lm per watt
    "efficacy": re.compile(
        r"(\d+(?:\.\d+)?)\s*lm\s*(?:/\s*W\b|per\s+watt\b)", re.IGNORECASE
    ),
    # THD:  ≤ 10%  /  < 10 %  /  10% THD
    "thd": re.compile(
        r"(?:THD|Total\s+Harmonic\s+Distortion)[^\d]*(\d+(?:\.\d+)?)\s*%"
        r"|(\d+(?:\.\d+)?)\s*%\s*(?:THD|Total\s+Harmonic)",
        re.IGNORECASE,
    ),
    # Power factor:  PF ≥ 0.95  /  power factor 0.95
    "power_factor": re.compile(
        r"(?:PF|power\s+factor)[^\d]*(\d+(?:\.\d+)?)", re.IGNORECASE
    ),
    # Surge protection:  10 kV  /  10kV SPD
    "surge_kv": re.compile(r"(\d+)\s*kV\b", re.IGNORECASE),
}

# Explicit IS/IEC standard references
_IS_REF_PATTERN = re.compile(
    r"\b(?:IS|IS/IEC|IEC|ISO)\s*[\d]+(?:\s*:\s*(?:Part\s*\d+)?(?:\s*:\s*Section\s*\d+)?(?:\s*:\s*\d{4})?)?\b",
    re.IGNORECASE,
)

# Certification keywords
_CERT_KEYWORDS = [
    "BIS", "CRS", "QCO", "QCO Mark", "BIS CRS", "ISI Mark",
    "NABL", "BEE", "star rating", "certification", "mandatory",
]


def _regex_fallback(query: str) -> dict:
    """
    Regex-based structured extraction — handles queries that Gemini can't process.
    """
    tech_requirements = []

    for param, pattern in _PATTERNS.items():
        match = pattern.search(query)
        if match:
            # First non-None group is the value
            value = next((g for g in match.groups() if g is not None), "")
            unit_map = {
                "power": "W", "voltage": "V", "cct": "K",
                "efficacy": "lm/W", "thd": "%", "power_factor": "",
                "ip_rating": "", "surge_kv": "kV",
            }
            tech_requirements.append({
                "parameter": param,
                "value": value.strip(),
                "unit": unit_map.get(param, ""),
            })

    explicit_refs = list(set(_IS_REF_PATTERN.findall(query)))
    cert_reqs = [kw for kw in _CERT_KEYWORDS if kw.lower() in query.lower()]

    # Application heuristics (very rough — Gemini does this far better)
    application = None
    app_match = re.search(r"\bfor\s+(highway|road|building|industrial|municipal|indoor|outdoor)", query, re.IGNORECASE)
    if app_match:
        application = app_match.group(1)

    return {
        "product": None,       # cannot reliably extract without LLM
        "domain": None,
        "application": application,
        "technical_requirements": tech_requirements,
        "explicit_standard_refs": [r.strip() for r in explicit_refs],
        "certification_requirements": cert_reqs,
        "_source": "regex_fallback",
    }


# ---------------------------------------------------------------------------
# LLM-powered extractor
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a procurement specification parser for Indian government tenders.
Extract structured information from the given procurement query or tender specification excerpt.

Respond ONLY with a valid JSON object matching exactly this schema:
{
  "product": "short product name (e.g. LED street light luminaire)",
  "domain": "technical domain (e.g. road lighting, electrical safety, motors)",
  "application": "intended use context (e.g. national highway, industrial plant)",
  "technical_requirements": [
    {"parameter": "power", "value": "120", "unit": "W"},
    {"parameter": "voltage", "value": "140-270", "unit": "V"},
    {"parameter": "ip_rating", "value": "IP66", "unit": ""},
    {"parameter": "cct", "value": "5700", "unit": "K"},
    {"parameter": "efficacy", "value": "130", "unit": "lm/W"},
    {"parameter": "thd", "value": "10", "unit": "%"},
    {"parameter": "power_factor", "value": "0.95", "unit": ""},
    {"parameter": "surge_protection", "value": "10", "unit": "kV"}
  ],
  "explicit_standard_refs": ["IS 10322", "IEC 60598"],
  "certification_requirements": ["BIS CRS", "QCO Mark", "BEE 5-Star"]
}

Only include fields that are explicitly mentioned or clearly implied. Use empty lists if nothing is found.
"""


def parse_query(query: str) -> dict:
    """
    Parse a procurement query into a structured QueryUnderstanding dict.

    Tries Gemini first; falls back to regex if unavailable or on error.
    """
    api_key = os.getenv("AI_ENGINE_GEMINI_KEY")
    if not api_key:
        logger.warning("AI_ENGINE_GEMINI_KEY not set — using regex fallback for query understanding.")
        return _regex_fallback(query)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{_SYSTEM_PROMPT}\n\nQuery:\n{query}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )
        result = json.loads(response.text)
        result["_source"] = "gemini"
        logger.info(
            "Query understanding via Gemini: product=%s domain=%s refs=%s",
            result.get("product"), result.get("domain"), result.get("explicit_standard_refs"),
        )
        return result

    except Exception as exc:
        logger.warning("Gemini query understanding failed (%s) — using regex fallback.", exc)
        return _regex_fallback(query)
