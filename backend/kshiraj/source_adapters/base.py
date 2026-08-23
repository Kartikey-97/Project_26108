"""
kshiraj/source_adapters/base.py

Base class and shared utilities for external data source adapters.

Provides clean HTTP transport abstraction and defensive field parsing.
All HTTP failures, connection errors, and timeouts map to `shared.utils.SourceAdapterError`.
"""

from __future__ import annotations

from datetime import date, datetime
import re
from typing import Any, Optional

import httpx

from shared.utils import SourceAdapterError, get_logger, utcnow

logger = get_logger(__name__)


class BaseSourceAdapter:
    """
    Abstract base class for all source adapters (BIS, BIS Drafts, CPPP, QCO).
    """

    def __init__(self, default_timeout: float = 30.0) -> None:
        self.default_timeout = default_timeout

    def fetch_url(self, url: str, timeout: Optional[float] = None) -> str:
        """
        Synchronously fetch content from a URL with timeout and error handling.

        Raises:
            SourceAdapterError: On network error, timeout, or HTTP status error.
        """
        to = timeout if timeout is not None else self.default_timeout
        logger.info("Fetching URL: %s (timeout=%s s)", url, to)

        try:
            with httpx.Client(timeout=to) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.text
        except httpx.TimeoutException as exc:
            logger.error("Timeout fetching %s: %s", url, exc)
            raise SourceAdapterError(
                f"Request to {url} timed out after {to}s.",
                code="TIMEOUT",
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP %s fetching %s", exc.response.status_code, url)
            raise SourceAdapterError(
                f"HTTP {exc.response.status_code} error fetching {url}.",
                code=f"HTTP_{exc.response.status_code}",
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Network error fetching %s: %s", url, exc)
            raise SourceAdapterError(
                f"Network connection error fetching {url}: {exc}",
                code="CONNECTION_ERROR",
            ) from exc

    async def fetch_url_async(self, url: str, timeout: Optional[float] = None) -> str:
        """
        Asynchronously fetch content from a URL with timeout and error handling.

        Raises:
            SourceAdapterError: On network error, timeout, or HTTP status error.
        """
        to = timeout if timeout is not None else self.default_timeout
        logger.info("Async fetching URL: %s (timeout=%s s)", url, to)

        try:
            async with httpx.AsyncClient(timeout=to) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except httpx.TimeoutException as exc:
            logger.error("Timeout async fetching %s: %s", url, exc)
            raise SourceAdapterError(
                f"Async request to {url} timed out after {to}s.",
                code="TIMEOUT",
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP %s async fetching %s", exc.response.status_code, url)
            raise SourceAdapterError(
                f"HTTP {exc.response.status_code} error fetching {url}.",
                code=f"HTTP_{exc.response.status_code}",
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Network error async fetching %s: %s", url, exc)
            raise SourceAdapterError(
                f"Network connection error fetching {url}: {exc}",
                code="CONNECTION_ERROR",
            ) from exc

    # ------------------------------------------------------------------
    # Defensive parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def parse_year(val: Any) -> Optional[int]:
        """Safely extract a 4-digit year from string or int."""
        if val is None:
            return None
        if isinstance(val, int):
            return val if 1900 <= val <= 2100 else None
        s = str(val).strip()
        m = re.search(r"\b(19\d\d|20\d\d)\b", s)
        return int(m.group(1)) if m else None

    @staticmethod
    def parse_date(val: Any) -> Optional[date]:
        """Safely parse ISO date string (YYYY-MM-DD)."""
        if val is None or isinstance(val, date):
            return val
        s = str(val).strip()
        try:
            return date.fromisoformat(s)
        except ValueError:
            return None

    @staticmethod
    def parse_int(val: Any) -> Optional[int]:
        """Safely convert value to int."""
        if val is None:
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None
