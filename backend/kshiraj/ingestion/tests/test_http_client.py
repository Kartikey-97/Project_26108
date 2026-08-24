"""
kshiraj/ingestion/tests/test_http_client.py

Unit tests for GovtHttpClient: retries, backoff, SSRF defense, size limits, and CAPTCHA detection.
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch
import pytest

import httpx

from kshiraj.ingestion.http_client import GovtHttpClient, GovtHttpClientError
from kshiraj.ingestion.models import FetchedResource


class MockStreamResponse:
    """Mock httpx streaming response."""
    def __init__(self, status_code=200, content=b"Hello Govt", headers=None, url="https://bis.gov.in/test"):
        self.status_code = status_code
        self._content = content
        self.headers = headers or {"content-type": "text/html; charset=utf-8"}
        self.url = httpx.URL(url)
        self.history = []
        self.encoding = "utf-8"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def iter_bytes(self, chunk_size=65536):
        for i in range(0, len(self._content), chunk_size):
            yield self._content[i:i + chunk_size]


class TestGovtHttpClient:

    def test_fetch_success(self):
        mock_client = MagicMock()
        mock_client.stream.return_value = MockStreamResponse(200, b"<html>BIS Standards</html>")

        client = GovtHttpClient(custom_client=mock_client, enable_ssrf_protection=False)
        res = client.fetch("https://services.bis.gov.in/standards")

        assert res.status_code == 200
        assert res.text_content == "<html>BIS Standards</html>"
        assert res.content_hash != ""
        assert res.is_blocked is False
        assert res.requires_human_verification is False

    def test_fetch_404_not_found(self):
        mock_client = MagicMock()
        mock_client.stream.return_value = MockStreamResponse(404, b"Not Found")

        client = GovtHttpClient(custom_client=mock_client, enable_ssrf_protection=False)
        res = client.fetch("https://services.bis.gov.in/missing")

        assert res.status_code == 404
        assert res.error_message == "HTTP 404"

    def test_fetch_429_with_retry_after(self):
        mock_client = MagicMock()
        resp_429 = MockStreamResponse(429, b"Too Many Requests", headers={"retry-after": "2", "content-type": "text/html"})
        resp_200 = MockStreamResponse(200, b"Success After Wait")
        mock_client.stream.side_effect = [resp_429, resp_200]

        sleep_calls = []
        def fake_sleep(duration):
            sleep_calls.append(duration)

        client = GovtHttpClient(custom_client=mock_client, max_retries=2, enable_ssrf_protection=False)
        res = client.fetch("https://services.bis.gov.in/rate_limited", sleep_fn=fake_sleep)

        assert res.status_code == 200
        assert res.text_content == "Success After Wait"
        assert len(sleep_calls) == 1
        assert sleep_calls[0] >= 2.0  # Respected Retry-After header

    def test_fetch_503_exponential_backoff(self):
        mock_client = MagicMock()
        resp_503 = MockStreamResponse(503, b"Service Unavailable")
        resp_200 = MockStreamResponse(200, b"Recovered")
        mock_client.stream.side_effect = [resp_503, resp_503, resp_200]

        sleep_calls = []
        client = GovtHttpClient(custom_client=mock_client, max_retries=3, backoff_factor=0.5, enable_ssrf_protection=False)
        res = client.fetch("https://services.bis.gov.in/flaky", sleep_fn=lambda s: sleep_calls.append(s))

        assert res.status_code == 200
        assert len(sleep_calls) == 2

    def test_ssrf_protection_blocks_private_ips(self):
        client = GovtHttpClient(enable_ssrf_protection=True)

        with pytest.raises(GovtHttpClientError) as exc_info:
            client.fetch("http://127.0.0.1/admin")
        assert exc_info.value.code == "SSRF_BLOCKED"

        with pytest.raises(GovtHttpClientError) as exc_info2:
            client.fetch("http://169.254.169.254/latest/meta-data")
        assert exc_info2.value.code == "SSRF_BLOCKED"

        with pytest.raises(GovtHttpClientError) as exc_info3:
            client.fetch("http://192.168.1.50/internal")
        assert exc_info3.value.code == "SSRF_BLOCKED"

    def test_max_response_size_protection(self):
        huge_bytes = b"A" * 2000
        mock_client = MagicMock()
        mock_client.stream.return_value = MockStreamResponse(200, huge_bytes)

        # Set max response size to 1000 bytes
        client = GovtHttpClient(custom_client=mock_client, max_response_size=1000, enable_ssrf_protection=False)

        with pytest.raises(GovtHttpClientError) as exc_info:
            client.fetch("https://services.bis.gov.in/huge_file.pdf")
        assert exc_info.value.code == "RESPONSE_TOO_LARGE"

    def test_captcha_detection(self):
        mock_client = MagicMock()
        captcha_html = b"<html><body>Please solve the captcha: <div class='g-recaptcha'></div></body></html>"
        mock_client.stream.return_value = MockStreamResponse(403, captcha_html)

        client = GovtHttpClient(custom_client=mock_client, enable_ssrf_protection=False)
        res = client.fetch("https://eprocure.gov.in/protected")

        assert res.status_code == 403
        assert res.is_blocked is True
        assert res.requires_human_verification is True

    def test_download_document_convenience_method(self):
        mock_client = MagicMock()
        pdf_bytes = b"%PDF-1.4 standard content"
        mock_client.stream.return_value = MockStreamResponse(200, pdf_bytes, headers={"content-type": "application/pdf"})

        client = GovtHttpClient(custom_client=mock_client, enable_ssrf_protection=False)
        res = client.download_document("https://services.bis.gov.in/standard.pdf")

        assert res.status_code == 200
        assert res.content_bytes == pdf_bytes
        assert res.content_length == len(pdf_bytes)

    def test_verify_ssl_configuration(self):
        client_secure = GovtHttpClient(verify_ssl=True, enable_ssrf_protection=False)
        assert client_secure.verify_ssl is True

        client_custom = GovtHttpClient(verify_ssl=False, enable_ssrf_protection=False)
        assert client_custom.verify_ssl is False
