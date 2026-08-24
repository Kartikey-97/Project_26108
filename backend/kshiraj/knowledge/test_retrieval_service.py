"""
Tests for kshiraj/knowledge/retrieval_service.py.

Run from the backend/ directory:
    pytest kshiraj/knowledge/test_retrieval_service.py -v

All tests are synchronous.  The service is stateless beyond its store
references, so each test constructs its own stores and service instance.
"""

from __future__ import annotations

import threading
import uuid

import pytest

from shared.models import (
    Evidence,
    EvidenceSourceType,
    Standard,
    StandardStatus,
)
from kshiraj.knowledge.evidence_store import EvidenceStore
from kshiraj.knowledge.standards_store import StandardsStore
from kshiraj.knowledge.retrieval_service import (
    CandidateStandard,
    RetrievalQuery,
    RetrievalResult,
    RetrievalService,
)


# ---------------------------------------------------------------------------
# Test factories
# ---------------------------------------------------------------------------


def _std(
    is_number: str = "IS 10322",
    title: str = "Street Lighting Standard",
    status: StandardStatus = StandardStatus.ACTIVE,
    scope: str | None = None,
    source_url: str | None = None,
    technical_committee: str | None = None,
    division_council: str | None = None,
    year: int | None = 2012,
    part: str | None = None,
    section: str | None = None,
) -> Standard:
    """Build a Standard with a fresh UUID for testing."""
    return Standard(
        id=str(uuid.uuid4()),
        is_number=is_number,
        title=title,
        status=status,
        scope=scope,
        source_url=source_url,
        technical_committee=technical_committee,
        division_council=division_council,
        year=year,
        part=part,
        section=section,
    )


def _ev(
    source_type: EvidenceSourceType = EvidenceSourceType.BIS_STANDARD,
    url: str | None = "https://bis.gov.in/test",
    excerpt: str = "Evidence text.",
    source_name: str = "BIS Test",
) -> Evidence:
    """Build an Evidence object with a fresh UUID for testing."""
    return Evidence(
        id=str(uuid.uuid4()),
        source_type=source_type,
        source_name=source_name,
        url=url,
        excerpt=excerpt,
    )


def _make_service(
    standards: list[Standard] | None = None,
    evidence: list[Evidence] | None = None,
) -> RetrievalService:
    """Build a RetrievalService pre-populated with the given objects."""
    ss = StandardsStore()
    es = EvidenceStore()
    for s in standards or []:
        ss.add(s)
    for e in evidence or []:
        es.add(e)
    return RetrievalService(standards_store=ss, evidence_store=es)


def _query(
    text: str,
    status_filter: list[StandardStatus] | None = None,
    include_evidence: bool = False,
    top_k: int | None = None,
) -> RetrievalQuery:
    return RetrievalQuery(
        query_text=text,
        status_filter=status_filter,
        include_evidence=include_evidence,
        top_k=top_k,
    )


# ---------------------------------------------------------------------------
# Helper assertions
# ---------------------------------------------------------------------------


def _ids(result: RetrievalResult) -> list[str]:
    """Return standard IDs from the result candidates list."""
    return [c.standard.id for c in result.candidates]


# ===========================================================================
# 1. Empty query
# ===========================================================================


class TestEmptyQuery:
    def test_empty_string_returns_no_candidates(self) -> None:
        svc = _make_service(standards=[_std()])
        result = svc.search_standards(_query(""))
        assert result.candidates == []
        assert result.total_candidates == 0

    def test_whitespace_only_query_returns_no_candidates(self) -> None:
        svc = _make_service(standards=[_std()])
        result = svc.search_standards(_query("   \t  "))
        assert result.candidates == []
        assert result.total_candidates == 0

    def test_empty_query_echoes_query_object(self) -> None:
        q = _query("")
        svc = _make_service()
        result = svc.search_standards(q)
        assert result.query is q


# ===========================================================================
# 2. No matching standards
# ===========================================================================


class TestNoMatch:
    def test_no_token_overlap_returns_empty(self) -> None:
        svc = _make_service(
            standards=[_std(is_number="IS 10322", title="Street Lighting")]
        )
        result = svc.search_standards(_query("transformer oil pressure"))
        assert result.candidates == []
        assert result.total_candidates == 0

    def test_empty_store_returns_empty(self) -> None:
        svc = _make_service()
        result = svc.search_standards(_query("IS 10322 lighting"))
        assert result.candidates == []


# ===========================================================================
# 3. Exact / strong text match
# ===========================================================================


class TestExactMatch:
    def test_exact_is_number_match(self) -> None:
        std = _std(is_number="IS 10322")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("IS 10322"))
        assert len(result.candidates) == 1
        assert result.candidates[0].standard.id == std.id

    def test_is_number_in_longer_query(self) -> None:
        std = _std(is_number="IS 1180", title="Transformers for power distribution")
        svc = _make_service(standards=[std])
        result = svc.search_standards(
            _query("requirement per IS 1180 for transformer procurement")
        )
        assert std.id in _ids(result)

    def test_title_word_match(self) -> None:
        std = _std(is_number="IS 694", title="PVC insulated cables")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("cables for underground distribution"))
        assert std.id in _ids(result)

    def test_relevance_score_is_positive(self) -> None:
        std = _std(is_number="IS 10322")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("IS 10322"))
        assert result.candidates[0].score > 0.0

    def test_relevance_score_populated_on_returned_standard(self) -> None:
        std = _std(is_number="IS 10322")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("IS 10322"))
        returned_std = result.candidates[0].standard
        assert returned_std.relevance_score is not None
        assert returned_std.relevance_score > 0.0

    def test_original_stored_standard_not_mutated(self) -> None:
        """The service must copy the Standard rather than mutate the stored one."""
        ss = StandardsStore()
        es = EvidenceStore()
        std = _std(is_number="IS 10322")
        ss.add(std)
        svc = RetrievalService(standards_store=ss, evidence_store=es)
        svc.search_standards(_query("IS 10322"))
        stored = ss.get_by_id(std.id)
        assert stored.relevance_score is None  # original is untouched


# ===========================================================================
# 4. Case-insensitive matching
# ===========================================================================


class TestCaseInsensitiveMatching:
    def test_lowercase_query_matches_uppercase_title(self) -> None:
        std = _std(title="LED Street Lighting Luminaires")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("led street lighting"))
        assert std.id in _ids(result)

    def test_uppercase_query_matches_lowercase_title(self) -> None:
        std = _std(title="pvc insulated cables")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("PVC CABLES"))
        assert std.id in _ids(result)

    def test_mixed_case_is_number_query(self) -> None:
        std = _std(is_number="IS 10322")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("is 10322"))
        assert std.id in _ids(result)


# ===========================================================================
# 5. Multiple matching standards
# ===========================================================================


class TestMultipleMatches:
    def test_multiple_standards_can_match(self) -> None:
        s1 = _std(is_number="IS 10322", title="LED street lighting")
        s2 = _std(is_number="IS 694", title="LED strip lighting cables")
        svc = _make_service(standards=[s1, s2])
        result = svc.search_standards(_query("LED lighting"))
        ids = set(_ids(result))
        assert s1.id in ids
        assert s2.id in ids

    def test_stronger_match_scored_higher(self) -> None:
        # s1 has both IS-number and title match; s2 has only title match
        s1 = _std(is_number="IS 10322", title="Street lighting luminaires")
        s2 = _std(is_number="IS 694", title="Luminaires for indoor use")
        svc = _make_service(standards=[s1, s2])
        result = svc.search_standards(_query("IS 10322 luminaires"))
        # s1 must be first (IS-number exact match gives it a much higher score)
        assert result.candidates[0].standard.id == s1.id

    def test_total_candidates_reflects_all_matches(self) -> None:
        stds = [
            _std(is_number="IS 10322", title="Street lighting"),
            _std(is_number="IS 694", title="Lighting cables"),
            _std(is_number="IS 1180", title="Transformers"),
        ]
        svc = _make_service(standards=stds)
        result = svc.search_standards(_query("lighting"))
        # IS 1180 (Transformers) has no 'lighting' token — should not appear
        matching_ids = {c.standard.id for c in result.candidates}
        assert stds[0].id in matching_ids
        assert stds[1].id in matching_ids
        assert stds[2].id not in matching_ids


# ===========================================================================
# 6. Status filtering
# ===========================================================================


class TestStatusFiltering:
    def test_active_filter_excludes_superseded(self) -> None:
        active = _std(is_number="IS 10322", title="Lighting", status=StandardStatus.ACTIVE)
        superseded = _std(
            is_number="IS 10322", title="Lighting old", status=StandardStatus.SUPERSEDED
        )
        svc = _make_service(standards=[active, superseded])
        result = svc.search_standards(
            _query("IS 10322 lighting", status_filter=[StandardStatus.ACTIVE])
        )
        ids = _ids(result)
        assert active.id in ids
        assert superseded.id not in ids

    def test_multiple_statuses_in_filter(self) -> None:
        active = _std(title="Lighting", status=StandardStatus.ACTIVE)
        reaffirmed = _std(title="Lighting reaffirmed", status=StandardStatus.REAFFIRMED)
        withdrawn = _std(title="Lighting withdrawn", status=StandardStatus.WITHDRAWN)
        svc = _make_service(standards=[active, reaffirmed, withdrawn])
        result = svc.search_standards(
            _query(
                "lighting",
                status_filter=[StandardStatus.ACTIVE, StandardStatus.REAFFIRMED],
            )
        )
        ids = _ids(result)
        assert active.id in ids
        assert reaffirmed.id in ids
        assert withdrawn.id not in ids

    def test_none_status_filter_includes_all_statuses(self) -> None:
        stds = [
            _std(title="lighting", status=st)
            for st in StandardStatus
        ]
        svc = _make_service(standards=stds)
        result = svc.search_standards(_query("lighting", status_filter=None))
        assert len(result.candidates) == len(stds)

    def test_empty_status_filter_list_returns_nothing(self) -> None:
        svc = _make_service(standards=[_std(title="Lighting")])
        result = svc.search_standards(_query("lighting", status_filter=[]))
        assert result.candidates == []
        assert result.total_candidates == 0

    def test_status_filter_with_no_match_returns_empty(self) -> None:
        std = _std(title="Lighting", status=StandardStatus.ACTIVE)
        svc = _make_service(standards=[std])
        result = svc.search_standards(
            _query("lighting", status_filter=[StandardStatus.WITHDRAWN])
        )
        assert result.candidates == []


# ===========================================================================
# 7 & 8. Evidence records / evidence association
# ===========================================================================


class TestEvidenceAssociation:
    def test_evidence_not_attached_by_default(self) -> None:
        std = _std(source_url="https://bis.gov.in/is10322")
        ev = _ev(url="https://bis.gov.in/is10322")
        svc = _make_service(standards=[std], evidence=[ev])
        result = svc.search_standards(_query("IS 10322", include_evidence=False))
        assert result.candidates[0].evidence == []

    def test_evidence_attached_when_requested(self) -> None:
        std = _std(is_number="IS 10322", source_url="https://bis.gov.in/is10322")
        ev = _ev(url="https://bis.gov.in/is10322")
        svc = _make_service(standards=[std], evidence=[ev])
        result = svc.search_standards(_query("IS 10322", include_evidence=True))
        assert len(result.candidates[0].evidence) == 1
        assert result.candidates[0].evidence[0].id == ev.id

    def test_multiple_evidence_records_attached(self) -> None:
        std = _std(is_number="IS 10322", source_url="https://bis.gov.in/is10322")
        ev1 = _ev(url="https://bis.gov.in/is10322", excerpt="Clause 1")
        ev2 = _ev(url="https://bis.gov.in/is10322", excerpt="Clause 2")
        svc = _make_service(standards=[std], evidence=[ev1, ev2])
        result = svc.search_standards(_query("IS 10322", include_evidence=True))
        attached_ids = {e.id for e in result.candidates[0].evidence}
        assert attached_ids == {ev1.id, ev2.id}

    def test_evidence_url_mismatch_not_attached(self) -> None:
        std = _std(is_number="IS 10322", source_url="https://bis.gov.in/is10322")
        ev = _ev(url="https://bis.gov.in/OTHER")
        svc = _make_service(standards=[std], evidence=[ev])
        result = svc.search_standards(_query("IS 10322", include_evidence=True))
        assert result.candidates[0].evidence == []

    def test_standard_with_none_source_url_gets_no_evidence(self) -> None:
        std = _std(is_number="IS 10322", source_url=None)
        ev = _ev(url="https://bis.gov.in/is10322")
        svc = _make_service(standards=[std], evidence=[ev])
        result = svc.search_standards(_query("IS 10322", include_evidence=True))
        assert result.candidates[0].evidence == []

    def test_evidence_with_none_url_not_attached(self) -> None:
        std = _std(is_number="IS 10322", source_url="https://bis.gov.in/is10322")
        ev = _ev(url=None)
        svc = _make_service(standards=[std], evidence=[ev])
        result = svc.search_standards(_query("IS 10322", include_evidence=True))
        assert result.candidates[0].evidence == []

    def test_evidence_isolated_between_standards(self) -> None:
        s1 = _std(is_number="IS 10322", source_url="https://bis.gov.in/s1")
        s2 = _std(is_number="IS 694", source_url="https://bis.gov.in/s2")
        ev1 = _ev(url="https://bis.gov.in/s1")
        ev2 = _ev(url="https://bis.gov.in/s2")
        svc = _make_service(standards=[s1, s2], evidence=[ev1, ev2])
        result = svc.search_standards(
            _query("IS 10322 IS 694 lighting cables", include_evidence=True)
        )
        # Build a map of standard id -> evidence for easy assertion
        ev_map = {c.standard.id: c.evidence for c in result.candidates}
        assert any(e.id == ev1.id for e in ev_map.get(s1.id, []))
        assert any(e.id == ev2.id for e in ev_map.get(s2.id, []))
        assert all(e.id != ev2.id for e in ev_map.get(s1.id, []))


# ===========================================================================
# 9. Deterministic ordering
# ===========================================================================


class TestDeterministicOrdering:
    def test_higher_score_comes_first(self) -> None:
        # IS-number exact match gives high score; title-only match gives lower score
        s_high = _std(is_number="IS 10322", title="Lighting")
        s_low = _std(is_number="IS 9999", title="Lighting equipment")
        svc = _make_service(standards=[s_high, s_low])
        result = svc.search_standards(_query("IS 10322 lighting"))
        assert result.candidates[0].standard.id == s_high.id

    def test_equal_score_sorted_by_is_number(self) -> None:
        # Both have title "lighting" and no IS-number match — equal score
        s_a = _std(is_number="IS 100", title="lighting specification")
        s_b = _std(is_number="IS 200", title="lighting specification")
        svc = _make_service(standards=[s_b, s_a])  # stored in reverse order
        result = svc.search_standards(_query("lighting specification"))
        assert result.candidates[0].standard.is_number == "IS 100"
        assert result.candidates[1].standard.is_number == "IS 200"

    def test_ordering_is_stable_across_calls(self) -> None:
        stds = [_std(is_number=f"IS {i}", title="lighting") for i in range(10)]
        svc = _make_service(standards=stds)
        q = _query("lighting")
        r1 = svc.search_standards(q)
        r2 = svc.search_standards(q)
        assert _ids(r1) == _ids(r2)


# ===========================================================================
# 10. Duplicate candidates not returned
# ===========================================================================


class TestNoDuplicateCandidates:
    def test_same_standard_not_returned_twice(self) -> None:
        """Even if the store somehow exposes the same ID twice, results deduplicate."""
        std = _std(is_number="IS 10322", title="LED street lighting")
        # Normally the store prevents duplicate IDs; we bypass by patching list_all.
        ss = StandardsStore()
        es = EvidenceStore()
        ss.add(std)
        svc = RetrievalService(standards_store=ss, evidence_store=es)

        # Monkey-patch list_all to return the same standard twice
        original_list_all = ss.list_all
        ss.list_all = lambda: [std, std]  # type: ignore[method-assign]

        result = svc.search_standards(_query("IS 10322"))
        # Restore
        ss.list_all = original_list_all  # type: ignore[method-assign]

        ids = _ids(result)
        assert ids.count(std.id) == 1

    def test_results_contain_unique_ids(self) -> None:
        stds = [_std(is_number=f"IS {i}", title="lighting") for i in range(5)]
        svc = _make_service(standards=stds)
        result = svc.search_standards(_query("lighting IS 1 IS 2 IS 3"))
        all_ids = _ids(result)
        assert len(all_ids) == len(set(all_ids))


# ===========================================================================
# 11. Empty stores
# ===========================================================================


class TestEmptyStores:
    def test_empty_standards_store_returns_empty(self) -> None:
        svc = _make_service()
        result = svc.search_standards(_query("IS 10322"))
        assert result.candidates == []
        assert result.total_candidates == 0

    def test_empty_evidence_store_with_include_evidence(self) -> None:
        std = _std(is_number="IS 10322", source_url="https://bis.gov.in/s")
        svc = _make_service(standards=[std], evidence=[])
        result = svc.search_standards(_query("IS 10322", include_evidence=True))
        assert result.candidates[0].evidence == []


# ===========================================================================
# 12. top_k truncation
# ===========================================================================


class TestTopK:
    def test_top_k_limits_results(self) -> None:
        stds = [_std(is_number=f"IS {i}", title="lighting") for i in range(10)]
        svc = _make_service(standards=stds)
        result = svc.search_standards(_query("lighting", top_k=3))
        assert len(result.candidates) == 3

    def test_total_candidates_reflects_pre_truncation_count(self) -> None:
        stds = [_std(is_number=f"IS {i}", title="lighting") for i in range(8)]
        svc = _make_service(standards=stds)
        result = svc.search_standards(_query("lighting", top_k=3))
        assert len(result.candidates) == 3
        assert result.total_candidates == 8

    def test_top_k_none_returns_all(self) -> None:
        stds = [_std(is_number=f"IS {i}", title="lighting") for i in range(6)]
        svc = _make_service(standards=stds)
        result = svc.search_standards(_query("lighting", top_k=None))
        assert len(result.candidates) == 6

    def test_top_k_larger_than_results_returns_all(self) -> None:
        stds = [_std(is_number=f"IS {i}", title="lighting") for i in range(3)]
        svc = _make_service(standards=stds)
        result = svc.search_standards(_query("lighting", top_k=100))
        assert len(result.candidates) == 3


# ===========================================================================
# 13. Scope and committee field matching
# ===========================================================================


class TestScopeAndCommitteeMatching:
    def test_scope_field_contributes_to_score(self) -> None:
        std = _std(
            is_number="IS 10322",
            title="Luminaires",
            scope="Covers street lighting for roads and highways",
        )
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("roads highways lighting"))
        assert std.id in _ids(result)

    def test_technical_committee_field_contributes(self) -> None:
        std = _std(
            is_number="IS 9999",
            title="Cable specification",
            technical_committee="Electrotechnical Division Council",
        )
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("electrotechnical specification"))
        assert std.id in _ids(result)

    def test_division_council_field_contributes(self) -> None:
        std = _std(
            is_number="IS 8888",
            title="General specification",
            division_council="Civil Engineering",
        )
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("civil engineering specification"))
        assert std.id in _ids(result)


# ===========================================================================
# 14. matched_terms populated correctly
# ===========================================================================


class TestMatchedTerms:
    def test_matched_terms_not_empty_on_match(self) -> None:
        std = _std(is_number="IS 10322", title="Street lighting")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("IS 10322 lighting"))
        assert len(result.candidates[0].matched_terms) > 0

    def test_matched_terms_contain_query_tokens(self) -> None:
        std = _std(is_number="IS 10322", title="LED street lighting luminaires")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("IS 10322 luminaires"))
        terms = result.candidates[0].matched_terms
        # "luminaires" should appear in matched terms (title hit)
        assert any("luminaires" in t.lower() for t in terms)

    def test_matched_terms_have_no_duplicates(self) -> None:
        std = _std(is_number="IS 10322", title="Lighting")
        svc = _make_service(standards=[std])
        result = svc.search_standards(_query("IS 10322 lighting"))
        terms = result.candidates[0].matched_terms
        assert len(terms) == len(set(terms))


# ===========================================================================
# 15. RetrievalResult structure
# ===========================================================================


class TestRetrievalResultStructure:
    def test_result_echoes_original_query(self) -> None:
        q = _query("IS 10322")
        svc = _make_service(standards=[_std(is_number="IS 10322")])
        result = svc.search_standards(q)
        assert result.query is q

    def test_total_candidates_equals_len_candidates_without_top_k(self) -> None:
        stds = [_std(is_number=f"IS {i}", title="lighting") for i in range(4)]
        svc = _make_service(standards=stds)
        result = svc.search_standards(_query("lighting"))
        assert result.total_candidates == len(result.candidates)


# ===========================================================================
# 16. Malformed / boundary input
# ===========================================================================


class TestBoundaryInput:
    def test_query_with_only_punctuation_returns_empty(self) -> None:
        svc = _make_service(standards=[_std()])
        result = svc.search_standards(_query("!!! ??? ###"))
        # Punctuation stripped → no tokens → no matches
        assert result.candidates == []

    def test_single_character_query_returns_empty(self) -> None:
        # Tokens shorter than _MIN_TOKEN_LEN (2) are discarded
        svc = _make_service(standards=[_std(title="IS")])
        result = svc.search_standards(_query("a"))
        assert result.candidates == []

    def test_very_long_query_does_not_error(self) -> None:
        svc = _make_service(standards=[_std(is_number="IS 10322", title="Lighting")])
        long_query = " ".join(["lighting"] * 500)
        result = svc.search_standards(_query(long_query))
        assert isinstance(result, RetrievalResult)

    def test_numeric_only_query_matches_is_number(self) -> None:
        std = _std(is_number="IS 10322")
        svc = _make_service(standards=[std])
        # "10322" is a token; IS number tokenises to ["is", "10322"]
        result = svc.search_standards(_query("10322"))
        assert std.id in _ids(result)


# ===========================================================================
# 17. Thread-safe / read-only behaviour
# ===========================================================================


class TestThreadSafety:
    def test_concurrent_searches_produce_consistent_results(self) -> None:
        """Multiple threads searching simultaneously must all see the same results."""
        stds = [_std(is_number=f"IS {i}", title="lighting standard") for i in range(20)]
        svc = _make_service(standards=stds)
        q = _query("lighting standard")

        results: list[RetrievalResult] = []
        errors: list[Exception] = []

        def _search() -> None:
            try:
                results.append(svc.search_standards(q))
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=_search) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Errors during concurrent search: {errors}"
        assert len(results) == 20
        # All results must agree on the same candidate IDs and order
        first_ids = _ids(results[0])
        for r in results[1:]:
            assert _ids(r) == first_ids

    def test_search_does_not_mutate_store(self) -> None:
        ss = StandardsStore()
        es = EvidenceStore()
        std = _std(is_number="IS 10322")
        ss.add(std)
        svc = RetrievalService(standards_store=ss, evidence_store=es)
        count_before = ss.count()
        svc.search_standards(_query("IS 10322"))
        assert ss.count() == count_before
        assert ss.get_by_id(std.id).relevance_score is None  # not mutated


# ===========================================================================
# 18. Designation field matching
# ===========================================================================


class TestDesignationMatching:
    def test_full_designation_in_query_matches_standard(self) -> None:
        """Querying with the canonical designation string should match."""
        std = _std(is_number="IS 10322", part="Part 5", section="Sec 3", year=2012)
        svc = _make_service(standards=[std])
        # Standard.designation → "IS 10322 (Part 5/Sec 3):2012"
        result = svc.search_standards(_query("IS 10322 (Part 5/Sec 3):2012"))
        assert std.id in _ids(result)
