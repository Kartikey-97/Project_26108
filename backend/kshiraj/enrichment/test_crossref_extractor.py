"""
kshiraj/enrichment/test_crossref_extractor.py

Unit tests for kshiraj.enrichment.crossref_extractor.CrossRefExtractor.
"""

from __future__ import annotations

import pytest

from shared.models import Standard, StandardStatus
from kshiraj.enrichment.crossref_extractor import CrossRefExtractor, CrossRefResult


@pytest.fixture
def extractor() -> CrossRefExtractor:
    return CrossRefExtractor()


class TestCrossRefExtractor:
    """Test suite for CrossRefExtractor."""

    def test_single_is_reference(self, extractor: CrossRefExtractor):
        text = "Conforms to IS 2062 specifications."
        result = extractor.extract(text)

        assert isinstance(result, CrossRefResult)
        assert result.source_is_number == ""
        assert result.referenced_is_numbers == ["IS 2062"]
        assert result.raw_matches == ["IS 2062"]

    def test_multiple_is_references(self, extractor: CrossRefExtractor):
        text = "Conforms to IS 2062 and testing shall be carried out according to IS 1608."
        result = extractor.extract(text)

        assert result.referenced_is_numbers == ["IS 2062", "IS 1608"]
        assert result.raw_matches == ["IS 2062", "IS 1608"]

    def test_duplicate_references_deduplicated(self, extractor: CrossRefExtractor):
        text = "IS 2062 steel plates shall meet IS 2062 requirements and IS 1608 test standards."
        result = extractor.extract(text)

        assert result.referenced_is_numbers == ["IS 2062", "IS 1608"]
        assert len(result.raw_matches) == 3
        assert result.raw_matches == ["IS 2062", "IS 2062", "IS 1608"]

    def test_full_designation_with_year(self, extractor: CrossRefExtractor):
        text = "Specification as per IS 10322:2012 for indoor luminaires."
        result = extractor.extract(text)

        assert result.referenced_is_numbers == ["IS 10322"]
        assert result.raw_matches == ["IS 10322:2012"]

    def test_part_section_designation(self, extractor: CrossRefExtractor):
        text = "Luminaires shall comply with IS 10322 (Part 5/Sec 3):2012."
        result = extractor.extract(text)

        assert result.referenced_is_numbers == ["IS 10322"]
        assert result.raw_matches == ["IS 10322 (Part 5/Sec 3):2012"]

    def test_amendment_suffix(self, extractor: CrossRefExtractor):
        text = "Cables per IS 694:2010 Amd.2 for fixed wiring."
        result = extractor.extract(text)

        assert result.referenced_is_numbers == ["IS 694"]
        assert result.raw_matches == ["IS 694:2010 Amd.2"]

    def test_lowercase_mixed_case_is(self, extractor: CrossRefExtractor):
        text = "Check is 2062 and Is 1180 and iS 694."
        result = extractor.extract(text)

        assert result.referenced_is_numbers == ["IS 2062", "IS 1180", "IS 694"]
        assert result.raw_matches == ["is 2062", "Is 1180", "iS 694"]

    def test_no_references(self, extractor: CrossRefExtractor):
        text = "General technical specifications for indoor equipment."
        result = extractor.extract(text)

        assert result.source_is_number == ""
        assert result.referenced_is_numbers == []
        assert result.raw_matches == []

    def test_numbers_without_is_ignored(self, extractor: CrossRefExtractor):
        text = "Clause 2062 on page 1180 published in 2014 under S.O. 219(E)."
        result = extractor.extract(text)

        assert result.referenced_is_numbers == []
        assert result.raw_matches == []

    def test_standard_object_input_scope(self, extractor: CrossRefExtractor):
        std = Standard(
            is_number="IS 10322",
            title="Luminaires",
            scope="This standard references IS 2062 steel and IS 694 wiring.",
            status=StandardStatus.ACTIVE,
        )
        result = extractor.extract(std)

        assert result.source_is_number == "IS 10322"
        assert result.referenced_is_numbers == ["IS 2062", "IS 694"]

    def test_standard_object_input_text_excerpt(self, extractor: CrossRefExtractor):
        std = Standard(
            is_number="IS 1180",
            title="Transformers",
            scope=None,
            text_excerpt="Testing per IS 2026 and IS 1608 specifications.",
            status=StandardStatus.ACTIVE,
        )
        result = extractor.extract(std)

        assert result.source_is_number == "IS 1180"
        assert result.referenced_is_numbers == ["IS 2026", "IS 1608"]

    def test_source_is_number_populated_for_standard(self, extractor: CrossRefExtractor):
        std = Standard(
            is_number="IS 2062",
            title="Structural Steel",
            scope="General structural steel specifications.",
            status=StandardStatus.ACTIVE,
        )
        result = extractor.extract(std)

        assert result.source_is_number == "IS 2062"

    def test_input_standard_not_mutated(self, extractor: CrossRefExtractor):
        std = Standard(
            is_number="IS 10322",
            title="Luminaires",
            scope="Conforms to IS 2062.",
            status=StandardStatus.ACTIVE,
        )
        std_copy = std.model_copy(deep=True)

        extractor.extract(std)

        assert std == std_copy

    def test_reference_ordering_follows_first_appearance(self, extractor: CrossRefExtractor):
        text = "First IS 1180, then IS 2062, then IS 694."
        result = extractor.extract(text)

        assert result.referenced_is_numbers == ["IS 1180", "IS 2062", "IS 694"]

    def test_multiple_appearances_different_years_normalize_same(self, extractor: CrossRefExtractor):
        text = "Refers to IS 10322:2012 and also older IS 10322:2002 version."
        result = extractor.extract(text)

        assert result.referenced_is_numbers == ["IS 10322"]
        assert result.raw_matches == ["IS 10322:2012", "IS 10322:2002"]
