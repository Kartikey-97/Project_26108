import os
import json
from .base import ReasoningProvider
from google import genai
from google.genai import types

class GeminiReasoner(ReasoningProvider):
    def __init__(self):
        api_key = os.getenv("AI_ENGINE_GEMINI_KEY")
        if not api_key:
            print("WARNING: AI_ENGINE_GEMINI_KEY is not set.")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.6-flash"

    def analyze(self, req_text, req_type, standards):
        if not standards:
            return {
                "verdict": "requires_human_verification",
                "reason": f"No retrieved standards could be confidently matched against the {req_type} requirement.",
                "action": "Manually verify specification.",
                "confidence": 0.4
            }
        
        # Prepare standards text
        stds_context = "\n".join([f"- {s.is_number}: {s.title}" for s in standards])
        
        prompt = f"""
You are an expert Indian Standards (BIS) auditor.
Analyze the following procurement requirement against the provided candidate standards.

Requirement: "{req_text}"
Requirement Type: {req_type}

Candidate Standards:
{stds_context}

Determine the verdict (one of: justified, potentially_unnecessary, outdated_reference, incorrect_standard, wrong_scope, ambiguous, conflicting, potentially_over_restrictive, unsupported, requires_human_verification).
Provide a concise reason (1-2 sentences).
Provide a recommended action for the procurement officer.
Provide a confidence score between 0.0 and 1.0.

Respond ONLY with a valid JSON object matching exactly this schema:
{{
  "verdict": "justified",
  "reason": "explanation here",
  "action": "action here",
  "confidence": 0.9
}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            return {
                "verdict": "requires_human_verification",
                "reason": f"AI reasoning failed: {str(e)}",
                "action": "Manually verify specification against standards.",
                "confidence": 0.1
            }
