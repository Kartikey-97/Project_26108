"""
kshiraj/ingestion/http_client.py

Robust HTTP client tailored for acquiring government publications and documents.
Provides:
  - Connection pooling & session persistence
  - SSRF defense (blocking private, loopback, link-local, and reserved IP ranges)
  - Configurable exponential backoff retry with jitter
  - Retry-After header parsing (both numeric seconds and RFC HTTP-dates)
  - Streaming size enforcement to defend against memory exhaustion & compression bombs
  - Automatic content-type and charset decoding
  - SHA-256 content hashing during download
  - Non-invasive CAPTCHA / bot challenge detection (flagging for human verification)
"""

from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import ipaddress
import random
import socket
import time
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple
from urllib.parse import urlparse

import httpx

from shared.utils import SourceAdapterError, get_logger, utcnow
from kshiraj.ingestion.models import FetchedResource

logger = get_logger(__name__)

# Standard IP networks that must be blocked under SSRF rules
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),       # Link-local / AWS metadata
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),       # Carrier-grade NAT
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),        # TEST-NET-1
    ipaddress.ip_network("198.51.100.0/24"),     # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),      # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),         # Multicast
    ipaddress.ip_network("240.0.0.0/4"),         # Reserved
    ipaddress.ip_network("::1/128"),             # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),            # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),           # IPv6 Link-Local
]

# Patterns indicating bot-protection or CAPTCHA challenges
_CAPTCHA_SIGNATURES = [
    "g-recaptcha",
    "cf-chl-bypass",
    "turnstile",
    "hcaptcha",
    "security verification",
    "please solve the captcha",
    "enter the characters shown",
    "access denied - captcha required",
    "bot verification",
    "distil_ident",
    "perimeterx",
]


class GovtHttpClientError(SourceAdapterError):
    """Specific error raised by GovtHttpClient."""


class GovtHttpClient:
    """
    Production-grade HTTP client for crawling government portals and standards depositories.
    """

    DEFAULT_USER_AGENT = "Project26108-GovtIngestionBot/1.0 (+https://github.com/Kartikey-97/ThreatLens)"
    DEFAULT_MAX_SIZE = 50 * 1024 * 1024  # 50 MB
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_RETRIES = 3
    RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = 1.0,
        max_response_size: int = DEFAULT_MAX_SIZE,
        enable_ssrf_protection: bool = True,
        follow_redirects: bool = True,
        verify_ssl: Union[bool, str] = True,
        headers: Optional[Dict[str, str]] = None,
        custom_client: Optional[httpx.Client] = None,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_response_size = max_response_size
        self.enable_ssrf_protection = enable_ssrf_protection
        self.follow_redirects = follow_redirects
        self.verify_ssl = verify_ssl
        
        self.base_headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,application/json,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        if headers:
            self.base_headers.update(headers)

        self._client = custom_client or httpx.Client(
            timeout=httpx.Timeout(self.timeout, connect=10.0),
            follow_redirects=self.follow_redirects,
            verify=self.verify_ssl,
            headers=self.base_headers,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        )

    def close(self) -> None:
        """Close the underlying HTTP client session."""
        if self._client:
            self._client.close()

    def __enter__(self) -> GovtHttpClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # ------------------------------------------------------------------
    # SSRF Validation
    # ------------------------------------------------------------------

    def validate_url_security(self, url: str) -> None:
        """
        Validate that the target URL does not resolve to private, loopback,
        or reserved internal IP addresses.
        """
        if not self.enable_ssrf_protection:
            return

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise GovtHttpClientError(
                f"Unsupported URL scheme '{parsed.scheme}': only http and https are allowed.",
                code="INVALID_SCHEME",
            )

        hostname = parsed.hostname
        if not hostname:
            raise GovtHttpClientError("URL missing valid hostname.", code="INVALID_URL")

        # Check for localhost / loopback aliases
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            raise GovtHttpClientError(
                f"SSRF violation: target hostname '{hostname}' is a loopback address.",
                code="SSRF_BLOCKED",
            )

        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                for blocked in _BLOCKED_NETWORKS:
                    if ip_obj in blocked:
                        logger.warning("SSRF blocked attempt to access private/internal IP %s for %s", ip_str, url)
                        raise GovtHttpClientError(
                            f"SSRF violation: target {hostname} resolved to protected internal IP {ip_str}.",
                            code="SSRF_BLOCKED",
                        )
        except socket.gaierror as exc:
            logger.debug("DNS resolution failed for hostname %s: %s", hostname, exc)
            # We let the HTTP client handle connection failure if DNS fails

    # ------------------------------------------------------------------
    # Backoff & Retry Logic
    # ------------------------------------------------------------------

    def _parse_retry_after(self, response: httpx.Response) -> Optional[float]:
        """Parse Retry-After header as numeric seconds or RFC date."""
        val = response.headers.get("retry-after")
        if not val:
            return None
        val = val.strip()
        try:
            return max(0.0, float(val))
        except ValueError:
            pass

        try:
            dt = parsedate_to_datetime(val)
            diff = (dt - datetime.now(timezone.utc)).total_seconds()
            return max(0.0, diff)
        except Exception:
            return None

    def _calculate_backoff(self, attempt: int, retry_after: Optional[float] = None) -> float:
        """Calculate wait time with exponential backoff and randomized jitter."""
        if retry_after is not None and retry_after > 0:
            # Add up to 10% jitter to Retry-After
            return retry_after + random.uniform(0.1, min(2.0, retry_after * 0.1))
        # standard exponential backoff: factor * 2^(attempt-1) + jitter
        base = self.backoff_factor * (2 ** (attempt - 1))
        jitter = random.uniform(0.1, 0.5 * base)
        return min(30.0, base + jitter)

    # ------------------------------------------------------------------
    # CAPTCHA / Bot Detection
    # ------------------------------------------------------------------

    @staticmethod
    def detect_captcha(text: str, status_code: int) -> bool:
        """Heuristic check for CAPTCHA and anti-bot verification walls."""
        if status_code in (403, 429, 503):
            lower_text = text.lower()
            return any(sig in lower_text for sig in _CAPTCHA_SIGNATURES)
        lower_text = text.lower()
        return any(sig in lower_text for sig in _CAPTCHA_SIGNATURES)

    # ------------------------------------------------------------------
    # Core Fetch Execution
    # ------------------------------------------------------------------

    def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Any] = None,
        timeout: Optional[float] = None,
        stream_max_size: Optional[int] = None,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> FetchedResource:
        """
        Fetch a URL synchronously with full retry, streaming size limits,
        and SSRF protection.
        """
        self.validate_url_security(url)

        max_size = stream_max_size or self.max_response_size
        req_timeout = timeout or self.timeout
        merged_headers = dict(self.base_headers)
        if headers:
            merged_headers.update(headers)

        attempt = 0
        last_error: Optional[Exception] = None
        redirected_urls: List[str] = []

        while attempt <= self.max_retries:
            attempt += 1
            t_start = time.perf_counter()

            try:
                logger.debug("HTTP %s %s (attempt %s/%s)", method, url, attempt, self.max_retries + 1)
                with self._client.stream(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=req_timeout,
                ) as response:
                    elapsed = time.perf_counter() - t_start

                    # Check for redirects
                    if response.history:
                        redirected_urls = [str(r.url) for r in response.history]

                    final_url = str(response.url)
                    status_code = response.status_code

                    # If retryable status code and not on last attempt
                    if status_code in self.RETRY_STATUS_CODES and attempt <= self.max_retries:
                        retry_after = self._parse_retry_after(response)
                        backoff = self._calculate_backoff(attempt, retry_after)
                        logger.warning(
                            "HTTP %s on %s. Retrying in %.2fs (attempt %s/%s)...",
                            status_code, url, backoff, attempt, self.max_retries
                        )
                        sleep_fn(backoff)
                        continue

                    # Stream content with size capping
                    hasher = hashlib.sha256()
                    chunks: List[bytes] = []
                    total_bytes = 0

                    for chunk in response.iter_bytes(chunk_size=65536):
                        total_bytes += len(chunk)
                        if total_bytes > max_size:
                            raise GovtHttpClientError(
                                f"Response size exceeded limit of {max_size} bytes (read {total_bytes} bytes).",
                                code="RESPONSE_TOO_LARGE",
                            )
                        chunks.append(chunk)
                        hasher.update(chunk)

                    content_bytes = b"".join(chunks)
                    content_hash = hasher.hexdigest()
                    content_type = response.headers.get("content-type", "application/octet-stream")

                    # Decode text
                    text_content = ""
                    try:
                        encoding = response.encoding or "utf-8"
                        text_content = content_bytes.decode(encoding, errors="replace")
                    except Exception:
                        text_content = content_bytes.decode("utf-8", errors="replace")

                    # Check CAPTCHA / bot challenge
                    is_captcha = self.detect_captcha(text_content, status_code)
                    is_blocked = status_code in (401, 403, 429) or is_captcha

                    return FetchedResource(
                        url=url,
                        canonical_url=final_url,
                        status_code=status_code,
                        headers=dict(response.headers),
                        content_bytes=content_bytes,
                        text_content=text_content,
                        content_type=content_type,
                        content_length=len(content_bytes),
                        content_hash=content_hash,
                        etag=response.headers.get("etag"),
                        last_modified=response.headers.get("last-modified"),
                        retrieved_at=utcnow(),
                        redirected_urls=redirected_urls,
                        elapsed_seconds=round(elapsed, 4),
                        is_blocked=is_blocked,
                        requires_human_verification=is_captcha,
                        error_message=None if status_code < 400 else f"HTTP {status_code}",
                    )

            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError, httpx.WriteError) as exc:
                last_error = exc
                if attempt <= self.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    logger.warning("Network error on %s (%s). Retrying in %.2fs...", url, exc, backoff)
                    sleep_fn(backoff)
                else:
                    break
            except GovtHttpClientError:
                raise
            except Exception as exc:
                last_error = exc
                logger.error("Unexpected error fetching %s: %s", url, exc)
                break

        # If loop terminated without returning
        elapsed = time.perf_counter() - t_start
        err_msg = f"Failed to fetch {url} after {attempt} attempts: {last_error}"
        logger.error(err_msg)
        return FetchedResource(
            url=url,
            canonical_url=url,
            status_code=0,
            headers={},
            content_bytes=b"",
            text_content="",
            content_type="",
            content_length=0,
            content_hash="",
            retrieved_at=utcnow(),
            elapsed_seconds=round(elapsed, 4),
            is_blocked=True,
            error_message=err_msg,
        )

    def download_document(self, url: str, timeout: Optional[float] = None) -> FetchedResource:
        """Convenience method for downloading PDFs and other attachments."""
        return self.fetch(url, method="GET", timeout=timeout or 60.0)
