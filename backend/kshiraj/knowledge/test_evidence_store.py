"""
Tests for kshiraj/knowledge/evidence_store.py.

Run from the backend/ directory:
    pytest kshiraj/knowledge/test_evidence_store.py -v

All tests are synchronous; the store itself is not async.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone

import pytest

from shared.models import Evidence, EvidenceSourceType
from kshiraj.knowledge.evidence_store import DuplicateEvidenceIDError, EvidenceStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_evidence(
    source_type: EvidenceSourceType = EvidenceSourceType.BIS_STANDARD,
    source_name: str = "Test Source",
    url: str | None = "https://bis.gov.in/test",
    excerpt: str = "Sample evidence text.",
    authority: str | None = "BIS",
) -> Evidence:
    """Factory for test Evidence objects with a fresh UUID each call."""
    return Evidence(
        id=str(uuid.uuid4()),
        source_type=source_type,
        source_name=source_name,
        url=url,
        excerpt=excerpt,
        authority=authority,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def store() -> EvidenceStore:
    """Fresh EvidenceStore for each test."""
    return EvidenceStore()


# ---------------------------------------------------------------------------
# 1 & 2 — add + get_by_id / missing ID returns None
# ---------------------------------------------------------------------------


class TestAddAndGetById:
    def test_add_then_get_returns_correct_record(self, store: EvidenceStore) -> None:
        ev = _make_evidence()
        store.add(ev)
        result = store.get_by_id(ev.id)
        assert result is not None
        assert result.id == ev.id
        assert result.source_name == ev.source_name
        assert result.excerpt == ev.excerpt

    def test_get_by_id_missing_returns_none(self, store: EvidenceStore) -> None:
        assert store.get_by_id("nonexistent-id") is None

    def test_get_by_id_missing_after_store_has_other_records(
        self, store: EvidenceStore
    ) -> None:
        store.add(_make_evidence())
        assert store.get_by_id("not-in-store") is None


# ---------------------------------------------------------------------------
# 3 & 4 — duplicate ID raises / failed add does not mutate
# ---------------------------------------------------------------------------


class TestDuplicateIDHandling:
    def test_add_duplicate_id_raises(self, store: EvidenceStore) -> None:
        ev = _make_evidence()
        store.add(ev)
        duplicate = ev.model_copy()  # same id
        with pytest.raises(DuplicateEvidenceIDError):
            store.add(duplicate)

    def test_failed_duplicate_add_does_not_change_stored_record(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(excerpt="Original")
        store.add(ev)
        intruder = ev.model_copy(update={"excerpt": "Intruder"})
        with pytest.raises(DuplicateEvidenceIDError):
            store.add(intruder)
        assert store.get_by_id(ev.id).excerpt == "Original"

    def test_failed_duplicate_add_does_not_change_count(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence()
        store.add(ev)
        with pytest.raises(DuplicateEvidenceIDError):
            store.add(ev.model_copy())
        assert store.count() == 1

    def test_failed_duplicate_add_does_not_duplicate_in_type_index(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(source_type=EvidenceSourceType.BIS_STANDARD)
        store.add(ev)
        with pytest.raises(DuplicateEvidenceIDError):
            store.add(ev.model_copy())
        results = store.get_by_source_type(EvidenceSourceType.BIS_STANDARD)
        assert len(results) == 1

    def test_failed_duplicate_add_does_not_duplicate_in_url_index(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url="https://bis.gov.in/dup")
        store.add(ev)
        with pytest.raises(DuplicateEvidenceIDError):
            store.add(ev.model_copy())
        results = store.get_by_source_url("https://bis.gov.in/dup")
        assert len(results) == 1


# ---------------------------------------------------------------------------
# 5, 6, 7 — get_by_source_type
# ---------------------------------------------------------------------------


class TestGetBySourceType:
    def test_get_by_source_type_returns_matching_record(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(source_type=EvidenceSourceType.BIS_STANDARD)
        store.add(ev)
        results = store.get_by_source_type(EvidenceSourceType.BIS_STANDARD)
        assert len(results) == 1
        assert results[0].id == ev.id

    def test_multiple_records_same_source_type(self, store: EvidenceStore) -> None:
        e1 = _make_evidence(
            source_type=EvidenceSourceType.QCO_NOTIFICATION,
            source_name="QCO A",
        )
        e2 = _make_evidence(
            source_type=EvidenceSourceType.QCO_NOTIFICATION,
            source_name="QCO B",
        )
        store.add(e1)
        store.add(e2)
        results = store.get_by_source_type(EvidenceSourceType.QCO_NOTIFICATION)
        ids = {r.id for r in results}
        assert ids == {e1.id, e2.id}

    def test_different_source_types_are_isolated(self, store: EvidenceStore) -> None:
        bis = _make_evidence(source_type=EvidenceSourceType.BIS_STANDARD)
        qco = _make_evidence(source_type=EvidenceSourceType.QCO_NOTIFICATION)
        cppp = _make_evidence(source_type=EvidenceSourceType.CPPP_TENDER)
        for ev in (bis, qco, cppp):
            store.add(ev)
        assert len(store.get_by_source_type(EvidenceSourceType.BIS_STANDARD)) == 1
        assert len(store.get_by_source_type(EvidenceSourceType.QCO_NOTIFICATION)) == 1
        assert len(store.get_by_source_type(EvidenceSourceType.CPPP_TENDER)) == 1

    def test_get_by_source_type_returns_empty_list_for_unknown_type(
        self, store: EvidenceStore
    ) -> None:
        store.add(_make_evidence(source_type=EvidenceSourceType.BIS_STANDARD))
        assert store.get_by_source_type(EvidenceSourceType.SECONDARY) == []


# ---------------------------------------------------------------------------
# 8, 9, 10 — get_by_source_url
# ---------------------------------------------------------------------------


class TestGetBySourceUrl:
    def test_get_by_source_url_returns_matching_record(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url="https://bis.gov.in/is1180")
        store.add(ev)
        results = store.get_by_source_url("https://bis.gov.in/is1180")
        assert len(results) == 1
        assert results[0].id == ev.id

    def test_url_lookup_strips_surrounding_whitespace(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url="https://bis.gov.in/is1180")
        store.add(ev)
        # Look up with surrounding spaces — should still match
        results = store.get_by_source_url("  https://bis.gov.in/is1180  ")
        assert len(results) == 1
        assert results[0].id == ev.id

    def test_stored_url_with_whitespace_is_indexed_stripped(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url="  https://bis.gov.in/space  ")
        store.add(ev)
        results = store.get_by_source_url("https://bis.gov.in/space")
        assert len(results) == 1

    def test_multiple_records_sharing_same_url(self, store: EvidenceStore) -> None:
        shared_url = "https://bis.gov.in/shared"
        e1 = _make_evidence(url=shared_url, source_name="Fragment A")
        e2 = _make_evidence(url=shared_url, source_name="Fragment B")
        store.add(e1)
        store.add(e2)
        results = store.get_by_source_url(shared_url)
        ids = {r.id for r in results}
        assert ids == {e1.id, e2.id}

    def test_get_by_source_url_returns_empty_for_no_match(
        self, store: EvidenceStore
    ) -> None:
        store.add(_make_evidence(url="https://bis.gov.in/a"))
        assert store.get_by_source_url("https://bis.gov.in/b") == []

    def test_evidence_with_none_url_not_returned_by_url_lookup(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url=None)
        store.add(ev)
        # Any lookup should return empty — None is not indexed
        assert store.get_by_source_url("") == []
        assert store.get_by_source_url("None") == []


# ---------------------------------------------------------------------------
# 11–15 — upsert behaviour
# ---------------------------------------------------------------------------


class TestUpsert:
    def test_upsert_new_evidence_is_stored(self, store: EvidenceStore) -> None:
        ev = _make_evidence()
        store.upsert(ev)
        assert store.get_by_id(ev.id) is not None

    def test_upsert_replaces_existing_record(self, store: EvidenceStore) -> None:
        ev = _make_evidence(excerpt="Original")
        store.add(ev)
        updated = ev.model_copy(update={"excerpt": "Updated"})
        store.upsert(updated)
        assert store.get_by_id(ev.id).excerpt == "Updated"

    def test_upsert_changing_source_type_updates_index(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(source_type=EvidenceSourceType.BIS_STANDARD)
        store.add(ev)
        reclassified = ev.model_copy(
            update={"source_type": EvidenceSourceType.BIS_AMENDMENT}
        )
        store.upsert(reclassified)
        # Old type bucket must be empty
        assert store.get_by_source_type(EvidenceSourceType.BIS_STANDARD) == []
        # New type bucket must contain the record
        results = store.get_by_source_type(EvidenceSourceType.BIS_AMENDMENT)
        assert len(results) == 1
        assert results[0].id == ev.id

    def test_upsert_changing_url_updates_index(self, store: EvidenceStore) -> None:
        ev = _make_evidence(url="https://bis.gov.in/old")
        store.add(ev)
        moved = ev.model_copy(update={"url": "https://bis.gov.in/new"})
        store.upsert(moved)
        assert store.get_by_source_url("https://bis.gov.in/old") == []
        results = store.get_by_source_url("https://bis.gov.in/new")
        assert len(results) == 1
        assert results[0].id == ev.id

    def test_upsert_does_not_increase_count_on_replace(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence()
        store.add(ev)
        store.upsert(ev.model_copy(update={"excerpt": "Changed"}))
        assert store.count() == 1

    def test_upsert_url_none_to_url_set_updates_index(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url=None)
        store.add(ev)
        with_url = ev.model_copy(update={"url": "https://bis.gov.in/added"})
        store.upsert(with_url)
        results = store.get_by_source_url("https://bis.gov.in/added")
        assert len(results) == 1

    def test_upsert_url_set_to_none_removes_from_index(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url="https://bis.gov.in/was-there")
        store.add(ev)
        without_url = ev.model_copy(update={"url": None})
        store.upsert(without_url)
        assert store.get_by_source_url("https://bis.gov.in/was-there") == []

    def test_repeated_upsert_does_not_duplicate_in_type_index(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(source_type=EvidenceSourceType.BIS_STANDARD)
        store.upsert(ev)
        store.upsert(ev.model_copy(update={"excerpt": "Again"}))
        results = store.get_by_source_type(EvidenceSourceType.BIS_STANDARD)
        assert len(results) == 1

    def test_repeated_upsert_does_not_duplicate_in_url_index(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url="https://bis.gov.in/repeat")
        store.upsert(ev)
        store.upsert(ev.model_copy(update={"excerpt": "Again"}))
        results = store.get_by_source_url("https://bis.gov.in/repeat")
        assert len(results) == 1


# ---------------------------------------------------------------------------
# 16–19 — remove behaviour
# ---------------------------------------------------------------------------


class TestRemove:
    def test_remove_existing_returns_true(self, store: EvidenceStore) -> None:
        ev = _make_evidence()
        store.add(ev)
        assert store.remove(ev.id) is True

    def test_remove_nonexistent_returns_false(self, store: EvidenceStore) -> None:
        assert store.remove("ghost-id") is False

    def test_removed_evidence_not_retrievable_by_id(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence()
        store.add(ev)
        store.remove(ev.id)
        assert store.get_by_id(ev.id) is None

    def test_removed_evidence_disappears_from_source_type_index(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(source_type=EvidenceSourceType.CPPP_TENDER)
        store.add(ev)
        store.remove(ev.id)
        assert store.get_by_source_type(EvidenceSourceType.CPPP_TENDER) == []

    def test_removed_evidence_disappears_from_url_index(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url="https://cppp.gov.in/tender/123")
        store.add(ev)
        store.remove(ev.id)
        assert store.get_by_source_url("https://cppp.gov.in/tender/123") == []

    def test_remove_one_of_two_leaves_other_in_type_index(
        self, store: EvidenceStore
    ) -> None:
        e1 = _make_evidence(source_type=EvidenceSourceType.BIS_GAZETTE_NOTIFICATION)
        e2 = _make_evidence(source_type=EvidenceSourceType.BIS_GAZETTE_NOTIFICATION)
        store.add(e1)
        store.add(e2)
        store.remove(e1.id)
        results = store.get_by_source_type(EvidenceSourceType.BIS_GAZETTE_NOTIFICATION)
        assert len(results) == 1
        assert results[0].id == e2.id

    def test_remove_one_of_two_leaves_other_in_url_index(
        self, store: EvidenceStore
    ) -> None:
        url = "https://shared.gov.in/doc"
        e1 = _make_evidence(url=url, source_name="Part A")
        e2 = _make_evidence(url=url, source_name="Part B")
        store.add(e1)
        store.add(e2)
        store.remove(e1.id)
        results = store.get_by_source_url(url)
        assert len(results) == 1
        assert results[0].id == e2.id

    def test_remove_evidence_with_none_url_does_not_error(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence(url=None)
        store.add(ev)
        result = store.remove(ev.id)
        assert result is True
        assert store.count() == 0


# ---------------------------------------------------------------------------
# 20 & 21 — list_all snapshot behaviour
# ---------------------------------------------------------------------------


class TestListAll:
    def test_list_all_returns_all_records(self, store: EvidenceStore) -> None:
        evs = [_make_evidence(source_name=f"src-{i}") for i in range(5)]
        for ev in evs:
            store.add(ev)
        listed = store.list_all()
        assert len(listed) == 5
        assert {e.id for e in listed} == {e.id for e in evs}

    def test_list_all_empty_store(self, store: EvidenceStore) -> None:
        assert store.list_all() == []

    def test_list_all_returns_snapshot_not_live_view(
        self, store: EvidenceStore
    ) -> None:
        ev = _make_evidence()
        store.add(ev)
        snapshot = store.list_all()
        store.remove(ev.id)
        # Snapshot captured before removal should still contain the record
        assert len(snapshot) == 1
        assert snapshot[0].id == ev.id


# ---------------------------------------------------------------------------
# 22 — count increments / decrements
# ---------------------------------------------------------------------------


class TestCount:
    def test_count_starts_at_zero(self, store: EvidenceStore) -> None:
        assert store.count() == 0

    def test_count_increments_on_add(self, store: EvidenceStore) -> None:
        store.add(_make_evidence())
        assert store.count() == 1
        store.add(_make_evidence())
        assert store.count() == 2

    def test_count_decrements_on_remove(self, store: EvidenceStore) -> None:
        ev = _make_evidence()
        store.add(ev)
        store.remove(ev.id)
        assert store.count() == 0

    def test_count_unchanged_after_failed_add(self, store: EvidenceStore) -> None:
        ev = _make_evidence()
        store.add(ev)
        with pytest.raises(DuplicateEvidenceIDError):
            store.add(ev.model_copy())
        assert store.count() == 1

    def test_count_unchanged_after_remove_nonexistent(
        self, store: EvidenceStore
    ) -> None:
        store.add(_make_evidence())
        store.remove("not-real")
        assert store.count() == 1


# ---------------------------------------------------------------------------
# 23 — clear resets the store
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear_resets_count(self, store: EvidenceStore) -> None:
        for _ in range(4):
            store.add(_make_evidence())
        store.clear()
        assert store.count() == 0

    def test_clear_empties_list_all(self, store: EvidenceStore) -> None:
        for _ in range(3):
            store.add(_make_evidence())
        store.clear()
        assert store.list_all() == []

    def test_clear_empties_type_index(self, store: EvidenceStore) -> None:
        ev = _make_evidence(source_type=EvidenceSourceType.BIS_STANDARD)
        store.add(ev)
        store.clear()
        assert store.get_by_source_type(EvidenceSourceType.BIS_STANDARD) == []

    def test_clear_empties_url_index(self, store: EvidenceStore) -> None:
        ev = _make_evidence(url="https://bis.gov.in/cleared")
        store.add(ev)
        store.clear()
        assert store.get_by_source_url("https://bis.gov.in/cleared") == []

    def test_store_usable_after_clear(self, store: EvidenceStore) -> None:
        store.add(_make_evidence())
        store.clear()
        ev = _make_evidence()
        store.add(ev)
        assert store.count() == 1
        assert store.get_by_id(ev.id) is not None


# ---------------------------------------------------------------------------
# 24 — all EvidenceSourceType enum values can be stored and retrieved
# ---------------------------------------------------------------------------


class TestAllSourceTypes:
    def test_all_enum_values_storable_and_filterable(
        self, store: EvidenceStore
    ) -> None:
        """Every member of EvidenceSourceType can round-trip through the store."""
        created: dict[EvidenceSourceType, str] = {}
        for st in EvidenceSourceType:
            ev = _make_evidence(source_type=st, source_name=f"src-{st.value}")
            store.add(ev)
            created[st] = ev.id

        for st, eid in created.items():
            results = store.get_by_source_type(st)
            assert len(results) == 1, f"Expected 1 result for {st}, got {len(results)}"
            assert results[0].id == eid


# ---------------------------------------------------------------------------
# 25 — concurrent additions produce the correct final count
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def test_concurrent_adds_produce_correct_count(
        self, store: EvidenceStore
    ) -> None:
        """Concurrent inserts from 50 threads must all succeed without data loss."""
        evidences = [_make_evidence(source_name=f"E{i}") for i in range(50)]
        errors: list[Exception] = []

        def _add(ev: Evidence) -> None:
            try:
                store.add(ev)
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=_add, args=(ev,)) for ev in evidences]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Unexpected errors during concurrent add: {errors}"
        assert store.count() == 50

    def test_concurrent_adds_populate_type_index_correctly(
        self, store: EvidenceStore
    ) -> None:
        """All 50 concurrent inserts should appear in the type index."""
        source_type = EvidenceSourceType.BIS_STANDARD
        evidences = [_make_evidence(source_type=source_type) for _ in range(50)]

        threads = [
            threading.Thread(target=store.add, args=(ev,)) for ev in evidences
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        results = store.get_by_source_type(source_type)
        assert len(results) == 50
