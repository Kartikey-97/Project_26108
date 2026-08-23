"""
kshiraj/ingestion/dynamic_renderer.py

Dynamic JavaScript page rendering abstraction for interactive government portals.
Supports optional Playwright rendering with fallback to standard HTTP fetching.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from shared.utils import get_logger, utcnow
from kshiraj.ingestion.http_client import GovtHttpClient
from kshiraj.ingestion.models import FetchedResource

logger = get_logger(__name__)


class BasePageRenderer:
    """Abstract interface for page rendering."""

    def render(
        self,
        url: str,
        wait_selector: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ) -> FetchedResource:
        raise NotImplementedError


class HttpFallbackRenderer(BasePageRenderer):
    """Default renderer relying on standard synchronous HTTP requests."""

    def __init__(self, http_client: Optional[GovtHttpClient] = None) -> None:
        self.http_client = http_client or GovtHttpClient()

    def render(
        self,
        url: str,
        wait_selector: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ) -> FetchedResource:
        logger.debug("HttpFallbackRenderer fetching %s via HTTP", url)
        return self.http_client.fetch(url, timeout=timeout_seconds)


class PlaywrightRenderer(BasePageRenderer):
    """
    Dynamic renderer using Playwright headless browser for JavaScript execution.
    Only instantiated if `playwright` package is available in the environment.
    """

    def __init__(
        self,
        headless: bool = True,
        user_agent: Optional[str] = None,
        fallback_renderer: Optional[BasePageRenderer] = None,
    ) -> None:
        self.headless = headless
        self.user_agent = user_agent
        self.fallback = fallback_renderer or HttpFallbackRenderer()
        self._is_available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check if Playwright is installed and ready."""
        if self._is_available is not None:
            return self._is_available
        try:
            import playwright  # noqa: F401
            from playwright.sync_api import sync_playwright  # noqa: F401
            self._is_available = True
        except ImportError:
            self._is_available = False
            logger.info("Playwright not installed; dynamic rendering will fall back to HTTP.")
        return self._is_available

    def render(
        self,
        url: str,
        wait_selector: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ) -> FetchedResource:
        if not self.is_available():
            return self.fallback.render(url, timeout_seconds=timeout_seconds)

        try:
            from playwright.sync_api import sync_playwright
            import hashlib

            t_start = time.perf_counter()
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context_kwargs: Dict[str, Any] = {}
                if self.user_agent:
                    context_kwargs["user_agent"] = self.user_agent

                context = browser.new_context(**context_kwargs)
                page = context.new_page()

                # Navigate and wait
                response = page.goto(
                    url,
                    timeout=int(timeout_seconds * 1000),
                    wait_until="networkidle",
                )

                if wait_selector:
                    try:
                        page.wait_for_selector(wait_selector, timeout=5000)
                    except Exception:
                        logger.debug("Selector %s not found within timeout on %s", wait_selector, url)

                html_content = page.content()
                status_code = response.status if response else 200
                final_url = page.url
                browser.close()

                elapsed = time.perf_counter() - t_start
                content_bytes = html_content.encode("utf-8")
                content_hash = hashlib.sha256(content_bytes).hexdigest()

                is_captcha = GovtHttpClient.detect_captcha(html_content, status_code)

                return FetchedResource(
                    url=url,
                    canonical_url=final_url,
                    status_code=status_code,
                    headers={},
                    content_bytes=content_bytes,
                    text_content=html_content,
                    content_type="text/html",
                    content_length=len(content_bytes),
                    content_hash=content_hash,
                    retrieved_at=utcnow(),
                    elapsed_seconds=round(elapsed, 4),
                    is_blocked=is_captcha or status_code in (403, 429),
                    requires_human_verification=is_captcha,
                )

        except Exception as exc:
            logger.warning("Playwright rendering failed for %s: %s. Falling back to HTTP.", url, exc)
            return self.fallback.render(url, timeout_seconds=timeout_seconds)
