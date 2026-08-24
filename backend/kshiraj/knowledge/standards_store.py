"""
In-memory repository for canonical Standard objects.

Design goals
------------
- Pure repository abstraction: no search ranking, no embeddings, no scraping,
  no version inference.
- Public interface is stable enough that the backing store can later be swapped
  for PostgreSQL without requiring callers (retrieval_service.py) to change.
- Thread-safe via a single ``threading.Lock``; suitable for the async FastAPI /
  BackgroundTask usage pattern used by the MVP pipeline.
- IS-number lookup is normalised (case-fold + strip) so that
  "IS 10322", "is 10322 ", and "Is 10322" all resolve to the same bucket.

Limitations (intentional for MVP)
----------------------------------
- Storage is lost on process restart.  Persistence belongs to a future DB layer.
- No semantic or full-text search; that is the responsibility of retrieval_service.py.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Dict, List, Optional

from shared.models import Standard, StandardStatus


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _normalize_is_number(raw: str) -> str:
    """Return a canonical key for a raw IS-number string.

    Strips surrounding whitespace and case-folds.  Internal whitespace is
    **not** collapsed: "IS 10322" and "IS10322" are intentionally distinct keys.
    Fuzzy/collapsed matching belongs in retrieval_service.py, not here.
    """
    return raw.strip().casefold()


# ---------------------------------------------------------------------------
# Public exceptions
# ---------------------------------------------------------------------------


class DuplicateStandardIDError(ValueError):
    """Raised when :meth:`StandardsStore.add` is called with an ID that already
    exists in the store.  Use :meth:`StandardsStore.upsert` to replace."""


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------


class StandardsStore:
    """In-memory repository for :class:`shared.models.Standard` objects.

    All mutating operations acquire ``_lock`` to keep the store safe when
    used from a single-process multi-threaded ASGI server (uvicorn workers
    share no memory, so per-process in-memory state is fine for the MVP).

    Read operations also acquire the lock so that callers always observe a
    consistent snapshot even during concurrent writes.

    Typical usage::

        store = StandardsStore()
        store.add(standard)
        result = store.get_by_id(standard.id)
        by_number = store.get_by_is_number("IS 10322")
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        # Primary index: id -> Standard
        self._by_id: Dict[str, Standard] = {}
        # Secondary index: normalised is_number -> list[id]
        # Preserves insertion order within each bucket.
        self._by_number: Dict[str, List[str]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add(self, standard: Standard) -> None:
        """Add a new standard to the store.

        Parameters
        ----------
        standard:
            The :class:`~shared.models.Standard` to persist.

        Raises
        ------
        DuplicateStandardIDError
            If a standard with the same ``id`` already exists.
            Use :meth:`upsert` to intentionally overwrite.
        """
        with self._lock:
            if standard.id in self._by_id:
                raise DuplicateStandardIDError(
                    f"Standard with id '{standard.id}' already exists. "
                    "Use upsert() to replace it."
                )
            self._by_id[standard.id] = standard
            key = _normalize_is_number(standard.is_number)
            if standard.id not in self._by_number[key]:
                self._by_number[key].append(standard.id)

    def upsert(self, standard: Standard) -> None:
        """Insert or replace a standard, keyed by ``id``.

        If a standard with the same ``id`` already exists its entry is
        replaced in full (including any change to ``is_number``).
        The secondary index is updated atomically under the lock.
        """
        with self._lock:
            old = self._by_id.get(standard.id)
            if old is not None:
                old_key = _normalize_is_number(old.is_number)
                try:
                    self._by_number[old_key].remove(old.id)
                except ValueError:
                    pass  # index was already inconsistent — heal silently
                if not self._by_number[old_key]:
                    del self._by_number[old_key]

            self._by_id[standard.id] = standard
            new_key = _normalize_is_number(standard.is_number)
            if standard.id not in self._by_number[new_key]:
                self._by_number[new_key].append(standard.id)

    def remove(self, standard_id: str) -> bool:
        """Remove a standard by ``id``.

        Returns
        -------
        bool
            ``True`` if the standard was found and removed, ``False`` if it
            was not present.
        """
        with self._lock:
            standard = self._by_id.pop(standard_id, None)
            if standard is None:
                return False
            key = _normalize_is_number(standard.is_number)
            try:
                self._by_number[key].remove(standard_id)
            except ValueError:
                pass
            if key in self._by_number and not self._by_number[key]:
                del self._by_number[key]
            return True

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_by_id(self, standard_id: str) -> Optional[Standard]:
        """Return the standard with the given ``id``, or ``None``."""
        with self._lock:
            return self._by_id.get(standard_id)

    def get_by_is_number(self, is_number: str) -> List[Standard]:
        """Return all standards whose ``is_number`` normalises to the same key
        as *is_number*.

        Lookup is case-insensitive and strips surrounding whitespace, so
        ``"IS 10322"``, ``"is 10322"``, and ``" IS 10322 "`` all match.

        All versions and parts sharing the same IS number are returned.
        Order reflects insertion order within the bucket.
        """
        key = _normalize_is_number(is_number)
        with self._lock:
            ids = list(self._by_number.get(key, []))
            # Resolve IDs inside the lock for a consistent snapshot.
            return [s for sid in ids if (s := self._by_id.get(sid)) is not None]

    def list_all(self) -> List[Standard]:
        """Return a snapshot of all stored standards in insertion order."""
        with self._lock:
            return list(self._by_id.values())

    def filter_by_status(self, status: StandardStatus) -> List[Standard]:
        """Return all standards whose ``status`` matches *status*."""
        with self._lock:
            return [s for s in self._by_id.values() if s.status == status]

    def get_active(self) -> List[Standard]:
        """Convenience helper — return all standards with status ``ACTIVE``.

        Note: ``ACTIVE`` is a metadata label set by the caller (e.g. a source
        adapter or the version_checker enrichment step).  This method performs
        a pure metadata filter; it does not infer currency from year or
        amendment numbers.
        """
        return self.filter_by_status(StandardStatus.ACTIVE)

    def count(self) -> int:
        """Return the total number of standards currently in the store."""
        with self._lock:
            return len(self._by_id)

    def clear(self) -> None:
        """Remove all standards from the store.

        Primarily intended for test teardown or full-reload scenarios.
        """
        with self._lock:
            self._by_id.clear()
            self._by_number.clear()
