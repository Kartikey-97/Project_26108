"""
In-memory repository for Evidence objects.

Design goals
------------
- Pure repository abstraction: no scraping, no HTTP, no embeddings,
  no semantic search, no AI/ML, no ranking, no quality inference.
- Public interface is stable enough that the backing store can later be
  replaced by PostgreSQL without requiring callers to change.
- Thread-safe via a single ``threading.Lock``.
- Secondary indexes (source_type, url) are kept consistent across all
  mutating operations and never expose mutable internal structures to callers.

URL normalisation
-----------------
Only surrounding whitespace is stripped before indexing.  No further
canonicalisation is applied: percent-encoding, trailing slashes, etc. are
left untouched to avoid silently mismatching legitimate URLs.

Limitations (intentional for MVP)
----------------------------------
- Storage is lost on process restart — persistence belongs to a future DB layer.
- No full-text or semantic search; that is the responsibility of
  retrieval_service.py.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Dict, List, Optional, Set

from shared.models import Evidence, EvidenceSourceType


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _normalize_url(raw: str) -> str:
    """Strip surrounding whitespace from a URL for index keying.

    Only whitespace is removed.  No further canonicalisation is applied.
    """
    return raw.strip()


# ---------------------------------------------------------------------------
# Public exceptions
# ---------------------------------------------------------------------------


class DuplicateEvidenceIDError(ValueError):
    """Raised when :meth:`EvidenceStore.add` is called with an ID that already
    exists in the store.  Use :meth:`EvidenceStore.upsert` to replace."""


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------


class EvidenceStore:
    """In-memory repository for :class:`shared.models.Evidence` objects.

    All mutating operations acquire ``_lock`` to maintain consistency under
    concurrent access.  Read operations also hold the lock so callers always
    observe a coherent snapshot.

    Secondary indexes
    -----------------
    ``_by_source_type``
        Maps :class:`~shared.models.EvidenceSourceType` → set of evidence IDs.
    ``_by_url``
        Maps normalised URL string → set of evidence IDs.
        Only populated for evidence records that carry a non-``None`` ``url``.

    Typical usage::

        store = EvidenceStore()
        store.add(evidence)
        result = store.get_by_id(evidence.id)
        by_type = store.get_by_source_type(EvidenceSourceType.BIS_STANDARD)
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        # Primary index: id -> Evidence
        self._by_id: Dict[str, Evidence] = {}
        # Secondary index: source_type -> set[id]
        self._by_source_type: Dict[EvidenceSourceType, Set[str]] = defaultdict(set)
        # Secondary index: normalised url -> set[id]
        self._by_url: Dict[str, Set[str]] = defaultdict(set)

    # ------------------------------------------------------------------
    # Internal index helpers (must be called while lock is held)
    # ------------------------------------------------------------------

    def _index_add(self, ev: Evidence) -> None:
        """Add *ev* to all secondary indexes. Lock must be held by caller."""
        self._by_source_type[ev.source_type].add(ev.id)
        if ev.url is not None:
            self._by_url[_normalize_url(ev.url)].add(ev.id)

    def _index_remove(self, ev: Evidence) -> None:
        """Remove *ev* from all secondary indexes. Lock must be held by caller."""
        bucket = self._by_source_type.get(ev.source_type)
        if bucket is not None:
            bucket.discard(ev.id)
            if not bucket:
                del self._by_source_type[ev.source_type]

        if ev.url is not None:
            key = _normalize_url(ev.url)
            url_bucket = self._by_url.get(key)
            if url_bucket is not None:
                url_bucket.discard(ev.id)
                if not url_bucket:
                    del self._by_url[key]

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add(self, evidence: Evidence) -> None:
        """Add a new evidence record to the store.

        Parameters
        ----------
        evidence:
            The :class:`~shared.models.Evidence` object to persist.

        Raises
        ------
        DuplicateEvidenceIDError
            If a record with the same ``id`` already exists.
            Use :meth:`upsert` to intentionally overwrite.
        """
        with self._lock:
            if evidence.id in self._by_id:
                raise DuplicateEvidenceIDError(
                    f"Evidence with id '{evidence.id}' already exists. "
                    "Use upsert() to replace it."
                )
            self._by_id[evidence.id] = evidence
            self._index_add(evidence)

    def upsert(self, evidence: Evidence) -> None:
        """Insert or replace an evidence record, keyed by ``id``.

        If a record with the same ``id`` already exists it is replaced in full.
        Secondary indexes are updated atomically: if ``source_type`` or ``url``
        changed, the old index entries are removed and new ones are added.
        Count does not increase when replacing an existing record.
        """
        with self._lock:
            old = self._by_id.get(evidence.id)
            if old is not None:
                self._index_remove(old)
            self._by_id[evidence.id] = evidence
            self._index_add(evidence)

    def remove(self, evidence_id: str) -> bool:
        """Remove an evidence record by ``id``.

        Returns
        -------
        bool
            ``True`` if the record was found and removed, ``False`` if it
            was not present.
        """
        with self._lock:
            ev = self._by_id.pop(evidence_id, None)
            if ev is None:
                return False
            self._index_remove(ev)
            return True

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_by_id(self, evidence_id: str) -> Optional[Evidence]:
        """Return the evidence record with the given ``id``, or ``None``."""
        with self._lock:
            return self._by_id.get(evidence_id)

    def get_by_source_type(
        self, source_type: EvidenceSourceType
    ) -> List[Evidence]:
        """Return all evidence records whose ``source_type`` matches *source_type*.

        Matching is exact (enum identity).  Order of results is not guaranteed.
        """
        with self._lock:
            ids = set(self._by_source_type.get(source_type, set()))
            return [ev for eid in ids if (ev := self._by_id.get(eid)) is not None]

    def get_by_source_url(self, url: str) -> List[Evidence]:
        """Return all evidence records whose ``url`` normalises to the same key
        as *url* (surrounding whitespace stripped).

        Records with ``url=None`` are never matched.
        Order of results is not guaranteed.
        """
        key = _normalize_url(url)
        with self._lock:
            ids = set(self._by_url.get(key, set()))
            return [ev for eid in ids if (ev := self._by_id.get(eid)) is not None]

    def list_all(self) -> List[Evidence]:
        """Return a snapshot of all stored evidence records."""
        with self._lock:
            return list(self._by_id.values())

    def count(self) -> int:
        """Return the total number of evidence records currently in the store."""
        with self._lock:
            return len(self._by_id)

    def clear(self) -> None:
        """Remove all evidence records from the store.

        Primarily intended for test teardown or full-reload scenarios.
        """
        with self._lock:
            self._by_id.clear()
            self._by_source_type.clear()
            self._by_url.clear()
