"""
kshiraj/ingestion/deduplication.py

Content-based deduplication and version change tracking using SHA-256 hashing.
Prevents redundant embedding generation and unnecessary Qdrant re-indexing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import threading
from typing import Dict, Optional, Set

from shared.utils import get_logger, utcnow
from kshiraj.ingestion.frontier import normalize_url

logger = get_logger(__name__)


class DocumentState(str, Enum):
    NEW_DOCUMENT = "new_document"
    UNCHANGED_DOCUMENT = "unchanged_document"
    MODIFIED_DOCUMENT = "modified_document"
    DUPLICATE_URL = "duplicate_url"


@dataclass
class DocumentHashRecord:
    """Tracked hash entry for an ingested document."""
    content_hash: str
    canonical_url: str
    source_name: str
    first_seen: datetime = field(default_factory=utcnow)
    last_seen: datetime = field(default_factory=utcnow)
    version_count: int = 1
    associated_urls: Set[str] = field(default_factory=set)


class DocumentDeduplicator:
    """
    Registry for detecting duplicate documents across URLs and tracking version mutations.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # Hash -> Record
        self._by_hash: Dict[str, DocumentHashRecord] = {}
        # Canonical URL -> latest content_hash
        self._by_url: Dict[str, str] = {}

    @staticmethod
    def calculate_hash(content: bytes | str) -> str:
        """Calculate SHA-256 hash of byte or text content."""
        if isinstance(content, str):
            content = content.encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def evaluate_document(
        self,
        url: str,
        content_hash: str,
        source_name: str = "Government Source",
    ) -> DocumentState:
        """
        Determine if the acquired document is NEW, UNCHANGED, or MODIFIED.
        """
        if not content_hash:
            return DocumentState.NEW_DOCUMENT

        canonical = normalize_url(url)

        with self._lock:
            existing_hash_for_url = self._by_url.get(canonical)

            # 1. Exact same URL and same hash -> UNCHANGED
            if existing_hash_for_url == content_hash:
                record = self._by_hash.get(content_hash)
                if record:
                    record.last_seen = utcnow()
                return DocumentState.UNCHANGED_DOCUMENT

            # 2. Same URL but DIFFERENT hash -> MODIFIED
            if existing_hash_for_url is not None and existing_hash_for_url != content_hash:
                old_record = self._by_hash.get(existing_hash_for_url)
                new_record = self._by_hash.get(content_hash)

                if new_record is None:
                    new_record = DocumentHashRecord(
                        content_hash=content_hash,
                        canonical_url=canonical,
                        source_name=source_name,
                        version_count=(old_record.version_count + 1) if old_record else 2,
                    )
                    self._by_hash[content_hash] = new_record
                else:
                    new_record.last_seen = utcnow()

                self._by_url[canonical] = content_hash
                return DocumentState.MODIFIED_DOCUMENT

            # 3. New URL, but hash already seen elsewhere -> DUPLICATE
            if content_hash in self._by_hash:
                record = self._by_hash[content_hash]
                record.associated_urls.add(canonical)
                record.last_seen = utcnow()
                self._by_url[canonical] = content_hash
                return DocumentState.DUPLICATE_URL

            # 4. Brand new hash and new URL -> NEW
            new_record = DocumentHashRecord(
                content_hash=content_hash,
                canonical_url=canonical,
                source_name=source_name,
                associated_urls={canonical},
            )
            self._by_hash[content_hash] = new_record
            self._by_url[canonical] = content_hash
            return DocumentState.NEW_DOCUMENT

    def register_document(
        self,
        url: str,
        content_hash: str,
        source_name: str = "Government Source",
    ) -> DocumentHashRecord:
        """Explicitly record an ingested document hash."""
        canonical = normalize_url(url)
        with self._lock:
            record = self._by_hash.get(content_hash)
            if record is None:
                record = DocumentHashRecord(
                    content_hash=content_hash,
                    canonical_url=canonical,
                    source_name=source_name,
                    associated_urls={canonical},
                )
                self._by_hash[content_hash] = record
            else:
                record.associated_urls.add(canonical)
                record.last_seen = utcnow()

            self._by_url[canonical] = content_hash
            return record

    def get_record_by_hash(self, content_hash: str) -> Optional[DocumentHashRecord]:
        with self._lock:
            return self._by_hash.get(content_hash)

    def get_hash_for_url(self, url: str) -> Optional[str]:
        canonical = normalize_url(url)
        with self._lock:
            return self._by_url.get(canonical)

    def clear(self) -> None:
        with self._lock:
            self._by_hash.clear()
            self._by_url.clear()
