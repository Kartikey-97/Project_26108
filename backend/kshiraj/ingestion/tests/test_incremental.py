"""
kshiraj/ingestion/tests/test_incremental.py

Unit tests for IncrementalIngestionTracker.
"""

from __future__ import annotations

import pytest

from kshiraj.ingestion.incremental import IncrementalIngestionTracker
from kshiraj.ingestion.models import IngestionStatus


class TestIncrementalIngestionTracker:

    def test_conditional_headers_generation(self):
        tracker = IncrementalIngestionTracker()
        url = "https://services.bis.gov.in/catalog/is10322"

        # Initially no headers
        assert tracker.get_conditional_headers(url) == {}

        # Record initial sync with ETag and Last-Modified
        tracker.record_sync_success(
            url=url,
            content_hash="abc123hash",
            etag='"5f9b-1234"',
            last_modified="Wed, 21 Oct 2025 07:28:00 GMT",
        )

        headers = tracker.get_conditional_headers(url)
        assert headers.get("If-None-Match") == '"5f9b-1234"'
        assert headers.get("If-Modified-Since") == "Wed, 21 Oct 2025 07:28:00 GMT"

    def test_sync_failure_tracking(self):
        tracker = IncrementalIngestionTracker()
        url = "https://eprocure.gov.in/failing"

        tracker.record_sync_failure(url, IngestionStatus.FAILED)
        state = tracker.get_state(url)
        assert state is not None
        assert state.status == IngestionStatus.FAILED
        assert state.error_count == 1

        tracker.record_sync_failure(url, IngestionStatus.FAILED)
        assert tracker.get_state(url).error_count == 2
