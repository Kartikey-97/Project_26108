import json
import logging
from typing import List, Dict, Any
from src.llm_config import GEMINI_MODEL, get_gemini_client

logger = logging.getLogger(__name__)

def compare_standards(is_numbers: List[str], standards_db: List[Dict]) -> Dict[str, Any]:
    """
    Compares two or more standards by finding them in the KB and asking the LLM
    to generate a side-by-side structured comparison.
    """
    if not is_numbers or len(is_numbers) < 2:
        return {"error": "At least two standard numbers must be provided for comparison."}

    # Find the standards in the DB
    found_stds = []
    for is_num in is_numbers:
        # Simple exact/contains match on is_number
        matched = False
        for std in standards_db:
            if std.get("is_number", "").lower().replace(" ", "") == is_num.lower().replace(" ", ""):
                found_stds.append(std)
                matched = True
                break
        if not matched:
            return {"error": f"Standard '{is_num}' not found in the knowledge base."}

    # Prepare context for the LLM
    context_blocks = []
    for std in found_stds:
        scope = std.get("scope", {}).get("value", "No scope available") if isinstance(std.get("scope"), dict) else str(std.get("scope", "No scope"))
        ctx = f"--- Standard: {std.get('is_number')} ---\n"
        ctx += f"Title: {std.get('title')}\n"
        ctx += f"Scope: {scope}\n"
        ctx += f"Categories: {', '.join(std.get('product_categories', []))}\n"
        ctx += f"Test Methods: {', '.join(std.get('test_methods', []))}\n"
        ctx += f"Normative References: {', '.join(std.get('normative_references', []))}\n"
        cert = std.get("certification", {})
        ctx += f"Certification Mandatory: {cert.get('mandatory') if isinstance(cert, dict) else 'Unknown'}\n"
        context_blocks.append(ctx)

    context_str = "\n\n".join(context_blocks)

    prompt = f"""
You are a BIS Standards Expert. Compare the following Indian Standards (IS).

Provide a structured JSON comparison matrix evaluating their overlap, differences, and applicability.

Standard Contexts:
{context_str}

Return EXACTLY a JSON object with this structure:
{{
  "comparison_summary": "A 2-3 sentence high-level summary of how they differ.",
  "matrix": [
    {{
      "feature": "Scope & Application",
      "standard_1": "...",
      "standard_2": "...",
      "overlap": "..."
    }},
    {{
      "feature": "Testing & Certification",
      "standard_1": "...",
      "standard_2": "...",
      "overlap": "..."
    }}
  ],
  "recommendation": "When to use which standard in a procurement context."
}}
"""
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"LLM comparison failed: {e}")
        return {"error": f"Comparison generation failed: {str(e)}"}
