import logging
from .base import ReasoningProvider

logger = logging.getLogger(__name__)

class MockReasoner(ReasoningProvider):
    def analyze(self, req_text, req_type, standards, is_reference=None, cited_year=None):
        """Deterministic mock reasoning — used when AI_MODE=mock or Gemini unavailable."""
        if not standards:
            return {
                "verdict": "requires_human_verification",
                "reason": (
                    f"No retrieved standards could be confidently matched against "
                    f"the {req_type} requirement. Manual verification is required."
                ),
                "action": "Manually verify specification against applicable BIS standards.",
                "confidence": 0.4,
            }

        std = standards[0]

        # If the tender cites a specific IS reference, mention it in the reason
        ref_note = f" (cited reference: {is_reference})" if is_reference else ""

        return {
            "verdict": "justified",
            "reason": (
                f"The {req_type} requirement{ref_note} aligns with the provisions "
                f"in {std.is_number} — {std.title}. This is a standard mock analysis; "
                "enable Gemini for detailed AI-powered assessment."
            ),
            "action": "Verify compliance details against the full standard text.",
            "confidence": 0.75,
        }
