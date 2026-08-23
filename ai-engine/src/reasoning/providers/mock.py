import uuid
from .base import ReasoningProvider

class MockReasoner(ReasoningProvider):
    def analyze(self, req_text, req_type, standards):
        # Deterministic mock reasoning
        if not standards:
            return {
                "verdict": "requires_human_verification",
                "reason": f"No retrieved standards could be confidently matched against the {req_type} requirement.",
                "action": "Manually verify specification.",
                "confidence": 0.4
            }
        
        std = standards[0]
        return {
            "verdict": "justified",
            "reason": f"The {req_type} requirement matches the provisions in {std.is_number} ({std.title}).",
            "action": "No action required.",
            "confidence": 0.85
        }
