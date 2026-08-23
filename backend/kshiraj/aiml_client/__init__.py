"""
kshiraj/aiml_client/__init__.py

Public interface for the AI/ML integration subsystem.
"""

from kshiraj.aiml_client.client import AimlClient, adapt_retrieved_standards
from kshiraj.aiml_client.schemas import (
    AimlClientError,
    AimlResponseError,
    AimlTimeoutError,
)

__all__ = [
    "AimlClient",
    "adapt_retrieved_standards",
    "AimlClientError",
    "AimlTimeoutError",
    "AimlResponseError",
]
