"""
kshiraj/enrichment/test_version_checker.py

Unit tests for kshiraj.enrichment.version_checker.VersionChecker.
"""

from __future__ import annotations

import pytest

from shared.models import Requirement, Standard, StandardStatus
from kshiraj.enrichment.version_checker import VersionCheckResult, VersionChecker


@pytest.fixture
def checker() -> VersionChecker:
    return VersionChecker()


class TestVersionChecker:
    """Test suite for VersionChecker.check()."""

    def test_exact_year_match(self, checker: VersionChecker):
        req = Requirement(analysis_id="a1", text="IS 10322:2012", is_reference="IS 10322", cited_year=2012)
        std = Standard(is_number="IS 10322", title="Luminaires", year=2012, status=StandardStatus.ACTIVE)

        res = checker.check(req, std)

        assert isinstance(res, VersionCheckResult)
        assert res.cited_year == 2012
        assert res.current_year == 2012
        assert res.is_current is True
        assert res.is_year_omitted is False
        assert res.gap_years == 0
        assert "matches the current standard edition" in res.note

    def test_outdated_cited_year(self, checker: VersionChecker):
        req = Requirement(analysis_id="a1", text="IS 10322:2012", is_reference="IS 10322", cited_year=2012)
        std = Standard(is_number="IS 10322", title="Luminaires", year=2022, status=StandardStatus.ACTIVE)

        res = checker.check(req, std)

        assert res.cited_year == 2012
        assert res.current_year == 2022
        assert res.is_current is False
        assert res.is_year_omitted is False
        assert res.gap_years == 10
        assert "10 year(s) older" in res.note

    def test_future_cited_year(self, checker: VersionChecker):
        req = Requirement(analysis_id="a1", text="IS 10322:2025", is_reference="IS 10322", cited_year=2025)
        std = Standard(is_number="IS 10322", title="Luminaires", year=2022, status=StandardStatus.ACTIVE)

        res = checker.check(req, std)

        assert res.cited_year == 2025
        assert res.current_year == 2022
        assert res.is_current is False
        assert res.is_year_omitted is False
        assert res.gap_years == -3
        assert "3 year(s) newer" in res.note

    def test_omitted_cited_year(self, checker: VersionChecker):
        req = Requirement(analysis_id="a1", text="IS 10322", is_reference="IS 10322", cited_year=None)
        std = Standard(is_number="IS 10322", title="Luminaires", year=2022, status=StandardStatus.ACTIVE)

        res = checker.check(req, std)

        assert res.cited_year is None
        assert res.current_year == 2022
        assert res.is_current is True
        assert res.is_year_omitted is True
        assert res.gap_years is None
        assert "without specifying an edition year" in res.note

    def test_missing_standard_year(self, checker: VersionChecker):
        req = Requirement(analysis_id="a1", text="IS 10322:2012", is_reference="IS 10322", cited_year=2012)
        std = Standard(is_number="IS 10322", title="Luminaires", year=None, status=StandardStatus.UNKNOWN)

        res = checker.check(req, std)

        assert res.cited_year == 2012
        assert res.current_year is None
        assert res.is_current is False
        assert res.is_year_omitted is False
        assert res.gap_years is None
        assert "unavailable" in res.note

    def test_no_mutation_of_inputs(self, checker: VersionChecker):
        req = Requirement(analysis_id="a1", text="IS 10322:2012", is_reference="IS 10322", cited_year=2012)
        std = Standard(is_number="IS 10322", title="Luminaires", year=2022, status=StandardStatus.ACTIVE)

        req_copy = req.model_copy(deep=True)
        std_copy = std.model_copy(deep=True)

        checker.check(req, std)

        assert req == req_copy
        assert std == std_copy

    def test_independent_of_standard_status(self, checker: VersionChecker):
        req = Requirement(analysis_id="a1", text="IS 10322:2012", is_reference="IS 10322", cited_year=2012)
        
        # Test with SUPERSEDED status but matching year
        std_superseded = Standard(is_number="IS 10322", title="Luminaires", year=2012, status=StandardStatus.SUPERSEDED)
        res_superseded = checker.check(req, std_superseded)
        assert res_superseded.is_current is True
        assert res_superseded.gap_years == 0

        # Test with WITHDRAWN status but matching year
        std_withdrawn = Standard(is_number="IS 10322", title="Luminaires", year=2012, status=StandardStatus.WITHDRAWN)
        res_withdrawn = checker.check(req, std_withdrawn)
        assert res_withdrawn.is_current is True
        assert res_withdrawn.gap_years == 0