"""
kartikey/analysis/llm_client.py

Thin wrapper around the Google Gemini API (google-genai SDK).

Responsibilities:
  - Configure the Gemini client from settings
  - Model selection with a working fallback chain
  - Retry logic for transient errors (429 rate limit, 503 overload)
  - Consistent JSON output extraction from model responses
  - Structured error reporting so callers don't need to handle SDK internals

Model selection rationale:
  - Primary:  gemini-2.5-flash  (stable, 1M context, best quality/speed ratio)
  - Fallback: gemini-2.5-flash-lite (faster, cheaper, same context window)
  - The model is resolved at runtime by probing the API — this makes the code
    robust to the availability changes that commonly affect Gemini API keys.

Why we use JSON mode:
  - Requirement extraction returns structured data (list of Requirement objects)
  - Plain text output is unpredictable; JSON mode forces schema compliance
  - We still validate and parse the output ourselves rather than trusting the model

Security note:
  - Tender documents are untrusted input.
  - The prompt explicitly frames the document as data-to-analyse, not instructions.
  - We never tell the model to "execute" or "run" anything from the document.
"""

from __future__ import annotations

import json
import time
from typing import Any

from shared.config import settings
from shared.utils import AnalysisError, get_logger

logger = get_logger(__name__)

# Models tried in order — first one available wins.
# This list is ordered: stable → lite → preview.
# Update when Google deprecates models, but always keep at least 2 entries.
_MODEL_PRIORITY = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
]

# Retry settings for transient errors
_MAX_RETRIES = 3
_RETRY_WAIT_SECONDS = 2.0


class GeminiClient:
    """
    Gemini API client with automatic model selection and retry logic.

    Usage:
        client = GeminiClient()
        result = await client.generate_json(prompt, system_prompt)
    """

    def __init__(self) -> None:
        self._api_key = settings.google_api_key
        if not self._api_key:
            raise AnalysisError(
                "GOOGLE_API_KEY is not set. Add it to backend/.env.",
                code="LLM_NOT_CONFIGURED",
            )
        self._client = None
        self._working_model: str | None = None

    def _get_client(self):
        """Lazy-initialize the Gemini client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
            except ImportError as exc:
                raise AnalysisError(
                    "google-genai is not installed. Run: pip install google-genai",
                    code="LLM_NOT_CONFIGURED",
                ) from exc
        return self._client

    def _resolve_model(self) -> str:
        """
        Find the first model in _MODEL_PRIORITY that actually responds.
        Result is cached after the first successful probe.
        """
        if self._working_model:
            return self._working_model

        client = self._get_client()
        from google.genai import errors as genai_errors

        for model in _MODEL_PRIORITY:
            try:
                client.models.generate_content(
                    model=model,
                    contents="ping",
                    config={"max_output_tokens": 1},
                )
                self._working_model = model
                logger.info("GeminiClient: using model '%s'", model)
                return model
            except genai_errors.ClientError as e:
                if "404" in str(e) or "NOT_FOUND" in str(e):
                    logger.debug("Model '%s' not available — trying next.", model)
                    continue
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    # Key has no credits — nothing will work
                    raise AnalysisError(
                        f"Gemini API key has depleted credits (RESOURCE_EXHAUSTED on '{model}'). "
                        "Please use a free-tier key from aistudio.google.com or top up credits.",
                        code="LLM_QUOTA_EXHAUSTED",
                    ) from e
                logger.warning("Model '%s' failed with unexpected error: %s", model, e)
                continue

        raise AnalysisError(
            f"No Gemini model is available. Tried: {_MODEL_PRIORITY}. "
            "Check your API key and model availability at aistudio.google.com.",
            code="LLM_NO_MODEL_AVAILABLE",
        )

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.1,  # low temp for structured extraction
    ) -> dict | list:
        """
        Call Gemini and return parsed JSON output.

        Parameters
        ----------
        prompt:
            The user-turn prompt containing the document/data to analyse.
        system_prompt:
            System-level instructions (persona, task framing, output format).
        temperature:
            Sampling temperature. Keep low (0.1–0.2) for extraction tasks
            where determinism matters.

        Returns
        -------
        dict | list
            Parsed JSON from the model response.

        Raises
        ------
        AnalysisError
            LLM_NOT_CONFIGURED   — API key missing or SDK not installed
            LLM_QUOTA_EXHAUSTED  — out of credits
            LLM_PARSE_ERROR      — model returned non-JSON output
            LLM_CALL_FAILED      — unrecoverable API error after retries
        """
        from google import genai
        from google.genai import errors as genai_errors
        from google.genai import types

        model = self._resolve_model()
        client = self._get_client()

        # Build contents
        contents = prompt
        config_kwargs: dict[str, Any] = {
            "temperature": temperature,
            "response_mime_type": "application/json",
        }
        if system_prompt:
            config_kwargs["system_instruction"] = system_prompt

        config = types.GenerateContentConfig(**config_kwargs)

        last_exc: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                raw = response.text.strip() if response.text else ""
                return _parse_json_response(raw)

            except genai_errors.ClientError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    raise AnalysisError(
                        "Gemini API quota exhausted. Free-tier: get a new key at aistudio.google.com.",
                        code="LLM_QUOTA_EXHAUSTED",
                    ) from e
                if "404" in str(e):
                    # Model disappeared mid-session — reset and retry
                    self._working_model = None
                    model = self._resolve_model()
                    last_exc = e
                    continue
                # Other 4xx — no point retrying
                raise AnalysisError(
                    f"Gemini API client error: {e}",
                    code="LLM_CALL_FAILED",
                ) from e

            except genai_errors.ServerError as e:
                # 5xx — transient, worth retrying
                logger.warning(
                    "Gemini server error (attempt %d/%d): %s",
                    attempt, _MAX_RETRIES, e,
                )
                last_exc = e
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_WAIT_SECONDS * attempt)
                continue

            except Exception as e:
                last_exc = e
                logger.warning(
                    "Unexpected error calling Gemini (attempt %d/%d): %s",
                    attempt, _MAX_RETRIES, e,
                )
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_WAIT_SECONDS)
                continue

        raise AnalysisError(
            f"Gemini call failed after {_MAX_RETRIES} attempts: {last_exc}",
            code="LLM_CALL_FAILED",
        ) from last_exc


def _parse_json_response(raw: str) -> dict | list:
    """
    Parse JSON from a model response, handling common wrapping patterns.

    Gemini sometimes wraps JSON in markdown code fences even with
    response_mime_type=application/json. We strip those defensively.
    """
    if not raw:
        raise AnalysisError(
            "Model returned an empty response.",
            code="LLM_PARSE_ERROR",
        )

    # Strip markdown code fences if present
    text = raw
    if text.startswith("```"):
        # e.g. ```json\n{...}\n```
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        # Try to find JSON within the response as last resort
        start = text.find("[")
        if start == -1:
            start = text.find("{")
        if start != -1:
            try:
                return json.loads(text[start:])
            except json.JSONDecodeError:
                pass
        raise AnalysisError(
            f"Model did not return valid JSON. Raw output (first 300 chars): {raw[:300]}",
            code="LLM_PARSE_ERROR",
        ) from exc


# Singleton — lazily created on first use
_client_instance: GeminiClient | None = None


def get_llm_client() -> GeminiClient:
    """Return the shared GeminiClient instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = GeminiClient()
    return _client_instance
