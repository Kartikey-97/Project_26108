"""
kshiraj/ingestion/tests/test_robots.py

Unit tests for RobotsPolicy and crawl-delay enforcement.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock
import pytest

from kshiraj.ingestion.robots import RobotsPolicy


class TestRobotsPolicy:

    def test_robots_txt_disallow(self):
        policy = RobotsPolicy()
        robots_content = """
User-agent: *
Disallow: /admin/
Disallow: /private/
Crawl-delay: 2
"""
        policy.parse_robots_txt("bis.gov.in", robots_content)

        assert policy.is_allowed("https://bis.gov.in/standards") is True
        assert policy.is_allowed("https://bis.gov.in/admin/dashboard") is False
        assert policy.get_crawl_delay("bis.gov.in") == 2.0

    def test_wait_if_needed(self):
        policy = RobotsPolicy(default_crawl_delay=1.0)
        sleep_durations = []

        def mock_sleep(secs):
            sleep_durations.append(secs)

        # First access: no wait
        policy.wait_if_needed("services.bis.gov.in", sleep_fn=mock_sleep)
        assert len(sleep_durations) == 0

        # Immediate second access: should trigger wait
        policy.wait_if_needed("services.bis.gov.in", sleep_fn=mock_sleep)
        assert len(sleep_durations) == 1
        assert sleep_durations[0] > 0.0
