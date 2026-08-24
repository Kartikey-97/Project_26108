"""
kshiraj/ingestion/tests/test_frontier.py

Unit tests for UrlFrontier and URL normalization.
"""

from __future__ import annotations

import pytest

from kshiraj.ingestion.frontier import (
    UrlFrontier,
    classify_link,
    extract_domain,
    normalize_url,
)
from kshiraj.ingestion.models import CrawlPolicy, LinkType


class TestUrlNormalization:

    def test_canonical_normalization(self):
        url1 = "HTTP://Services.BIS.Gov.IN:80/php/standards/?b=2&a=1#section3"
        expected = "http://services.bis.gov.in/php/standards/?a=1&b=2"
        assert normalize_url(url1) == expected

    def test_tracking_params_removed(self):
        url = "https://bis.gov.in/page?id=123&utm_source=twitter&utm_medium=social&gclid=xyz"
        expected = "https://bis.gov.in/page?id=123"
        assert normalize_url(url) == expected

    def test_relative_url_resolution(self):
        base = "https://services.bis.gov.in/php/BIS_2.0/catalog/"
        rel = "../drafts/IS10322.pdf"
        expected = "https://services.bis.gov.in/php/BIS_2.0/drafts/IS10322.pdf"
        assert normalize_url(rel, base_url=base) == expected

    def test_classify_link(self):
        link_type, mime = classify_link("https://bis.gov.in/standards/IS_10322.PDF")
        assert link_type == LinkType.DOCUMENT
        assert mime == "application/pdf"

        link_type_p, _ = classify_link("https://eprocure.gov.in/tenders?page=3")
        assert link_type_p == LinkType.PAGINATION

        link_type_n, _ = classify_link("https://eprocure.gov.in/tenders/view_details")
        assert link_type_n == LinkType.NAVIGATION


class TestUrlFrontier:

    def test_domain_allowlist(self):
        policy = CrawlPolicy(allowed_domains=["services.bis.gov.in", "bis.gov.in"])
        frontier = UrlFrontier(policy=policy)

        assert frontier.is_domain_allowed("https://services.bis.gov.in/page1") is True
        assert frontier.is_domain_allowed("https://sub.bis.gov.in/page2") is True
        assert frontier.is_domain_allowed("https://google.com/search") is False

    def test_max_depth_enforcement(self):
        policy = CrawlPolicy(allowed_domains=["bis.gov.in"], max_depth=2)
        frontier = UrlFrontier(seed_urls=["https://bis.gov.in/"], policy=policy)

        # Pop seed at depth 0
        item = frontier.pop_next()
        assert item is not None
        assert item[1] == 0

        # Add child at depth 1 -> OK
        assert frontier.add_url("https://bis.gov.in/level1", depth=1) is True
        # Add child at depth 2 -> OK
        assert frontier.add_url("https://bis.gov.in/level2", depth=2) is True
        # Add child at depth 3 (exceeds max_depth 2) -> Rejected
        assert frontier.add_url("https://bis.gov.in/level3", depth=3) is False

    def test_duplicate_url_deduplication(self):
        policy = CrawlPolicy(allowed_domains=["bis.gov.in"])
        frontier = UrlFrontier(seed_urls=["https://bis.gov.in/std"], policy=policy)

        # Attempt to re-add same URL with different case/fragment
        assert frontier.add_url("https://BIS.GOV.IN/std#fragment", depth=1) is False
        assert len(frontier) == 1

    def test_max_pages_cutoff(self):
        policy = CrawlPolicy(allowed_domains=["bis.gov.in"], max_pages=2)
        frontier = UrlFrontier(
            seed_urls=["https://bis.gov.in/p1", "https://bis.gov.in/p2", "https://bis.gov.in/p3"],
            policy=policy,
        )

        assert frontier.has_next() is True
        frontier.pop_next()  # visited = 1
        assert frontier.has_next() is True
        frontier.pop_next()  # visited = 2
        assert frontier.has_next() is False  # Reached max_pages=2
