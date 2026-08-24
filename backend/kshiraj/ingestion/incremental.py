"""
kshiraj/ingestion/incremental.py

Incremental ingestion tracker for conditional HTTP requests (ETag / If-Modified-Since).
Reduces network bandwidth and database write load by skipping unchanged documents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import threading
from typing import Dict, Optional

from shared.utils import get_logger, utcnow
from kshiraj.ingestion.frontier import normalize_url
from kshiraj.ingestion.models import IngestionStatus

logger = get_logger(__name__)


@dataclass
class UrlSyncState:
    """State metadata for a single tracked URL."""
    canonical_url: str
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    content_hash: Optional[str] = None
    last_crawled_at: datetime = field(default_factory=utcnow)
    status: IngestionStatus = IngestionStatus.NEW
    error_count: int = 0


class IncrementalIngestionTracker:
    """
    Maintains per-URL HTTP caching and synchronization metadata.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._states: Dict[str, UrlSyncState] = {}

    def get_conditional_headers(self, url: str) -> Dict[str, str]:
        """
        Construct conditional HTTP request headers (If-None-Match, If-Modified-Since)
        for a given URL if previous sync state exists.
        """
        canonical = normalize_url(url)
        headers: Dict[str, str] = {}

        with self._lock:
            state = self._states.get(canonical)
            if state:
                if state.etag:
                    headers["If-None-Match"] = state.etag
                if state.last_modified:
                    headers["If-Modified-Since"] = state.last_modified

        return headers

    def record_sync_success(
        self,
        url: str,
        content_hash: str,
        etag: Optional[str] = None,
        last_modified: Optional[str] = None,
        status: IngestionStatus = IngestionStatus.SUCCESS,
    ) -> UrlSyncState:
        """
        Update sync state after a successful document fetch.
        """
        canonical = normalize_url(url)
        with self._lock:
            state = self._states.get(canonical)
            if state is None:
                state = UrlSyncState(
                    canonical_url=canonical,
                    etag=etag,
                    last_modified=last_modified,
                    content_hash=content_hash,
                    last_crawled_at=utcnow(),
                    status=status,
                    error_count=0,
                )
                self._states[canonical] = state
            else:
                state.etag = etag or state.etag
                state.last_modified = last_modified or state.last_modified
                state.content_hash = content_hash or state.content_hash
                state.last_crawled_at = utcnow()
                state.status = status
                state.error_count = 0
            return state

    def record_sync_failure(self, url: str, status: IngestionStatus = IngestionStatus.FAILED) -> None:
        """Update sync state after a failed fetch."""
        canonical = normalize_url(url)
        with self._lock:
            state = self._states.get(canonical)
            if state is None:
                state = UrlSyncState(
                    canonical_url=canonical,
                    last_crawled_at=utcnow(),
                    status=status,
                    error_count=1,
                )
                self._states[canonical] = state
            else:
                state.last_crawled_at = utcnow()
                state.status = status
                state.error_count += 1

    def get_state(self, url: str) -> Optional[UrlSyncState]:
        canonical = normalize_url(url)
        with self._lock:
            return self._states.get(canonical)

    def clear(self) -> None:
        with self._lock:
            self._states.clear()
