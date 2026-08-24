"""
kshiraj/aiml_client/schemas.py

Client-specific exceptions and auxiliary schemas for the AI/ML integration layer.

Note:
  Primary request/response contracts (AimlRequest, AimlResponse, AimlFinding)
  are imported from `shared.contracts`. They are NOT duplicated here.
"""

from __future__ import annotations

from shared.utils import AnalysisError


class AimlClientError(AnalysisError):
    """Base exception for AI/ML client errors."""

    def __init__(self, message: str, code: str = "AIML_CLIENT_ERROR") -> None:
        super().__init__(message, code=code)


class AimlTimeoutError(AimlClientError):
    """Raised when the AI/ML service request times out."""

    def __init__(self, message: str = "AI/ML service request timed out.") -> None:
        super().__init__(message, code="AIML_TIMEOUT")


class AimlResponseError(AimlClientError):
    """Raised when the HTTP call fails or response format/payload is invalid."""

    def __init__(self, message: str, code: str = "AIML_RESPONSE_ERROR") -> None:
        super().__init__(message, code=code)
