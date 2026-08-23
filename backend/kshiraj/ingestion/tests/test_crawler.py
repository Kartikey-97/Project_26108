"""
kshiraj/ingestion/tests/test_crawler.py

Unit tests for GovtCrawler multi-page crawling and link discovery.
"""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from shared.models import EvidenceSourceType
from kshiraj.ingestion.crawler import GovtCrawler
from kshiraj.ingestion.http_client import GovtHttpClient
from kshiraj.ingestion.models import CrawlPolicy, FetchedResource


class TestGovtCrawler:

    def test_crawl_multi_page_with_attachments(self):
        page1_html = """
        <html>
        <body>
            <h1>BIS Standards Directory</h1>
            <a href="/standards/is10322">IS 10322 Page</a>
            <a href="/downloads/is10322_amendment.pdf">Download PDF</a>
            <a href="https://external-unallowed.com/link">External Link</a>
        </body>
        </html>
        """
        page2_html = """
        <html>
        <body>
            <h2>IS 10322 Details</h2>
            <p>Scope: Luminaires specification for emergency lighting.</p>
        </body>
        </html>
        """

        mock_http = MagicMock(spec=GovtHttpClient)

        def mock_fetch(url, **kwargs):
            if "is10322_amendment.pdf" in url:
                return FetchedResource(
                    url=url,
                    canonical_url=url,
                    status_code=200,
                    content_bytes=b"%PDF-1.4 sample",
                    content_type="application/pdf",
                    content_hash="pdfhash1",
                )
            elif "is10322" in url:
                return FetchedResource(
                    url=url,
                    canonical_url=url,
                    status_code=200,
                    text_content=page2_html,
                    content_type="text/html",
                    content_hash="page2hash",
                )
            else:
                return FetchedResource(
                    url=url,
                    canonical_url=url,
                    status_code=200,
                    text_content=page1_html,
                    content_type="text/html",
                    content_hash="page1hash",
                )

        mock_http.fetch.side_effect = mock_fetch
        mock_http.download_document.side_effect = mock_fetch

        crawler = GovtCrawler(http_client=mock_http)
        policy = CrawlPolicy(
            allowed_domains=["services.bis.gov.in"],
            max_depth=2,
            max_pages=10,
            respect_robots_txt=False,
        )

        acquired_docs = []
        result, docs = crawler.crawl_source(
            seed_urls=["https://services.bis.gov.in/standards"],
            policy=policy,
            source_name="BIS",
            on_document_acquired=lambda d: acquired_docs.append(d),
        )

        assert result.pages_crawled >= 2
        assert result.pages_succeeded >= 2
        assert result.pages_failed == 0
        assert len(docs) >= 2
        assert len(acquired_docs) == len(docs)
