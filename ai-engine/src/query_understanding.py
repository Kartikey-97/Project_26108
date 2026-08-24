"""
ai-engine/src/query_understanding.py

Converts a raw procurement query / tender excerpt into a structured
QueryUnderstanding dict that drives retrieval, ranking, and gap detection.

Strategy:
  1. Try Gemini to produce a richly-structured JSON understanding.
  2. Fall back to a general regex extractor if Gemini is unavailable.
"""

import json
import logging
import os
import re

logger = logging.getLogger(__name__)

# Explicit IS/IEC standard references
_IS_REF_PATTERN = re.compile(
    r"\b(?:IS|IS/IEC|IEC|ISO)\s*[\d]+(?:\s*:\s*(?:Part\s*\d+)?(?:\s*:\s*Section\s*\d+)?(?:\s*:\s*\d{4})?)?\b",
    re.IGNORECASE,
)

def _regex_fallback(query: str) -> dict:
    """
    Minimal regex-based structured extraction — handles queries that Gemini can't process.
    """
    explicit_refs = list(set(_IS_REF_PATTERN.findall(query)))
    
    # Generic parameter extraction heuristic: "Number Unit" pairs (e.g. 90 W, 10 kg, 220 V)
    tech_requirements = []
    param_matches = re.finditer(r"(\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?)\s*([a-zA-Z/%]+)", query)
    for m in param_matches:
        val, unit = m.groups()
        if unit.lower() not in ["and", "or", "to", "the"]:
            tech_requirements.append({
                "parameter": f"specification_{unit}",
                "value": val.strip(),
                "unit": unit.strip(),
                "operator": "exact"
            })

    return {
        "product": None,
        "domain": None,
        "application": None,
        "technical_requirements": tech_requirements,
        "explicit_standard_refs": [r.strip() for r in explicit_refs],
        "certification_requirements": [],
        "_source": "regex_fallback",
    }


# ---------------------------------------------------------------------------
# LLM-powered extractor
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a procurement specification parser for Indian government tenders.
Extract structured information from the given procurement query or tender specification excerpt.
Your extraction must be entirely generalized—it should work for LED lights, concrete cement, office chairs, electric motors, or any other product.

Respond ONLY with a valid JSON object matching exactly this schema:
{
  "product": "short product name (e.g. 'LED street light', 'office chair', 'Portland cement')",
  "domain": "technical domain (e.g. 'lighting', 'furniture', 'construction')",
  "application": "intended use context if specified (e.g. 'national highway', 'commercial office')",
  "technical_requirements": [
    {
      "parameter": "name of the parameter (e.g. 'power', 'backrest tilt', 'compressive strength')",
      "value": "numeric or string value (e.g. '90', '15', '33')",
      "unit": "unit of measurement if any (e.g. 'W', 'degrees', 'MPa')",
      "operator": "comparison operator (e.g. '==', '>=', '<=', 'approx')"
    }
  ],
  "explicit_standard_refs": ["array of exact IS/IEC references found, e.g. 'IS 10322'"],
  "certification_requirements": ["array of certifications, e.g. 'BIS CRS', 'BEE 5-Star']
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
            model="gemini-3.6-flash",
            contents=f"{_SYSTEM_PROMPT}\n\nQuery:\n{query}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )
        result = json.loads(response.text)
        result["_source"] = "gemini"
        logger.info(
            "Query understanding via Gemini: product=%s domain=%s refs=%s reqs=%d",
            result.get("product"), result.get("domain"), result.get("explicit_standard_refs"), len(result.get("technical_requirements", []))
        )
        return result

    except Exception as exc:
        logger.warning("Gemini query understanding failed (%s) — using regex fallback.", exc)
        return _regex_fallback(query)

