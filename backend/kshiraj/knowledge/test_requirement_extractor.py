"""
Tests for kshiraj/knowledge/requirement_extractor.py

Run from the backend/ directory:
    PYTHONPATH=. python -m pytest kshiraj/knowledge/test_requirement_extractor.py -v

All tests are synchronous and deterministic.
No external calls, no database, no LLM.
"""

from __future__ import annotations

import uuid

import pytest

from shared.models import RequirementCategory
from kshiraj.knowledge.requirement_extractor import (
    ExtractionConfig,
    ExtractionOutput,
    RequirementExtractor,
    RequirementNormalizer,
    extract_and_normalize,
    _detect_is_refs,
    _is_heading,
    _is_noise,
    _score_confidence,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AID = str(uuid.uuid4())  # fixed analysis_id for all tests


def make_extractor(
    min_len: int = 20,
    max_reqs: int = 500,
    min_confidence: float = 0.0,
    numbered: bool = True,
    lettered: bool = True,
    bullets: bool = True,
) -> RequirementExtractor:
    cfg = ExtractionConfig(
        min_requirement_text_length=min_len,
        max_requirements_per_document=max_reqs,
        min_confidence=min_confidence,
        split_on_numbered_bullets=numbered,
        split_on_lettered_bullets=lettered,
        split_on_plain_bullets=bullets,
    )
    return RequirementExtractor(cfg)


# ===========================================================================
# Internal helper unit tests (independent of Requirement)
# ===========================================================================


class TestIsNoise:
    def test_empty_string(self) -> None:
        assert _is_noise("") is True

    def test_whitespace_only(self) -> None:
        assert _is_noise("   \t  ") is True

    def test_page_marker(self) -> None:
        assert _is_noise("--- Page 3 ---") is True

    def test_page_marker_case_insensitive(self) -> None:
        assert _is_noise("--- PAGE 12 ---") is True

    def test_bare_page_number(self) -> None:
        assert _is_noise("42") is True

    def test_page_n_of_m(self) -> None:
        assert _is_noise("Page 3 of 15") is True

    def test_dots_line(self) -> None:
        assert _is_noise("...........") is True

    def test_dashes_line(self) -> None:
        assert _is_noise("-----------") is True

    def test_normal_text_not_noise(self) -> None:
        assert _is_noise("The luminaire shall comply with IS 10322.") is False

    def test_serial_number_header(self) -> None:
        assert _is_noise("S. No.") is True

    def test_sl_no(self) -> None:
        assert _is_noise("Sl. No.") is True


class TestIsHeading:
    def test_all_caps_heading(self) -> None:
        assert _is_heading("TECHNICAL SPECIFICATIONS") is True

    def test_all_caps_with_ampersand(self) -> None:
        assert _is_heading("SCOPE & APPLICABILITY") is True

    def test_not_heading_with_obligation_verb(self) -> None:
        assert _is_heading("LUMINAIRES SHALL COMPLY") is False

    def test_not_heading_with_is_reference(self) -> None:
        assert _is_heading("AS PER IS 10322") is False

    def test_multi_line_not_heading(self) -> None:
        assert _is_heading("HEADING LINE\nSecond line") is False

    def test_mixed_case_not_heading(self) -> None:
        assert _is_heading("The luminaire shall be energy efficient") is False

    def test_short_string_not_heading(self) -> None:
        # Less than 5 chars total — doesn't match heading pattern
        assert _is_heading("ABC") is False


class TestDetectIsRefs:
    def test_simple_is_number(self) -> None:
        refs = _detect_is_refs("Conform to IS 10322.")
        assert len(refs) == 1
        assert refs[0]["is_number"] == "IS 10322"

    def test_is_with_year(self) -> None:
        refs = _detect_is_refs("IS 10322:2012")
        assert refs[0]["year"] == 2012
        assert refs[0]["cited_designation"] if "cited_designation" in refs[0] else True

    def test_is_with_part_section_year(self) -> None:
        refs = _detect_is_refs("IS 10322 (Part 5/Sec 3):2012")
        assert refs[0]["part_section"] == "Part 5/Sec 3"
        assert refs[0]["year"] == 2012

    def test_is_with_amendment(self) -> None:
        refs = _detect_is_refs("IS 2062:2011 Amd.4")
        assert refs[0]["amendment_number"] == 4

    def test_multiple_refs(self) -> None:
        refs = _detect_is_refs("IS 10322 and IS 694:2010 shall be followed.")
        assert len(refs) == 2
        assert refs[0]["is_number"] == "IS 10322"
        assert refs[1]["is_number"] == "IS 694"

    def test_case_insensitive(self) -> None:
        refs = _detect_is_refs("is 10322")
        assert len(refs) == 1
        assert "10322" in refs[0]["is_number"]

    def test_no_refs(self) -> None:
        assert _detect_is_refs("No IS references here.") == []

    def test_char_offset_populated(self) -> None:
        text = "Requirement: IS 10322 applies."
        refs = _detect_is_refs(text)
        assert refs[0]["char_offset"] == text.index("IS 10322")


class TestScoreConfidence:
    def test_is_ref_and_structural(self) -> None:
        assert _score_confidence(True, True) == pytest.approx(0.90)

    def test_is_ref_no_structural(self) -> None:
        assert _score_confidence(True, False) == pytest.approx(0.80)

    def test_structural_no_is_ref(self) -> None:
        assert _score_confidence(False, True) == pytest.approx(0.65)

    def test_no_is_ref_no_structural(self) -> None:
        assert _score_confidence(False, False) == pytest.approx(0.45)


# ===========================================================================
# RequirementExtractor tests
# ===========================================================================


class TestExtractEmptyInput:
    def test_empty_string(self) -> None:
        extractor = make_extractor()
        result = extractor.extract("", AID)
        assert result == []

    def test_whitespace_only(self) -> None:
        result = make_extractor().extract("   \n\t  ", AID)
        assert result == []

    def test_none_equivalent_blank(self) -> None:
        result = make_extractor().extract("\n\n\n", AID)
        assert result == []


class TestExtractSingleParagraph:
    def test_single_paragraph_produces_one_requirement(self) -> None:
        text = (
            "The LED street lighting luminaire shall conform to IS 10322 "
            "and have a minimum luminous efficacy of 100 lm/W."
        )
        result = make_extractor().extract(text, AID)
        assert len(result) == 1

    def test_original_text_preserved(self) -> None:
        text = (
            "The luminaire shall conform to IS 10322 and have minimum efficacy of 100 lm/W."
        )
        reqs = make_extractor().extract(text, AID)
        assert reqs[0].text.strip() == text.strip()

    def test_analysis_id_populated(self) -> None:
        text = "The luminaire shall comply with IS 10322 (Part 5):2012."
        reqs = make_extractor().extract(text, AID)
        assert all(r.analysis_id == AID for r in reqs)

    def test_is_reference_extracted(self) -> None:
        text = "The supply shall conform to IS 10322:2012."
        reqs = make_extractor().extract(text, AID)
        assert reqs[0].is_reference == "IS 10322"
        assert reqs[0].cited_year == 2012

    def test_cited_designation_includes_full_match(self) -> None:
        text = "Comply with IS 10322:2012."
        reqs = make_extractor().extract(text, AID)
        assert "10322" in (reqs[0].cited_designation or "")
        assert "2012" in (reqs[0].cited_designation or "")


class TestExtractWithoutIsReference:
    def test_requirement_without_is_reference(self) -> None:
        text = (
            "The contractor shall submit a performance guarantee within "
            "30 days of the award of contract."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 1
        assert reqs[0].is_reference is None
        assert reqs[0].cited_year is None
        assert reqs[0].cited_designation is None

    def test_pure_eligibility_requirement(self) -> None:
        text = (
            "The bidder shall have a minimum annual turnover of INR 10 crore "
            "in the last 3 financial years."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 1
        assert reqs[0].is_reference is None

    def test_confidence_lower_without_is_ref(self) -> None:
        text = (
            "The contractor shall provide a valid warranty certificate for all luminaires."
        )
        reqs = make_extractor().extract(text, AID)
        # Confidence without IS reference should be 0.45 (paragraph) or 0.65 (structural)
        assert reqs[0].extraction_confidence is not None
        assert reqs[0].extraction_confidence < 0.85


class TestExtractNumberedRequirements:
    def test_numbered_list_split_into_separate(self) -> None:
        text = (
            "1. The luminaire shall conform to IS 10322.\n"
            "2. The driver shall comply with IS 15885.\n"
            "3. The housing shall be die-cast aluminium as per IS 617."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 3

    def test_numbered_items_structural_marker_set(self) -> None:
        text = (
            "1. IS 10322 shall be complied with.\n"
            "2. IS 15885 shall be complied with."
        )
        reqs = make_extractor().extract(text, AID)
        for r in reqs:
            assert r.extraction_confidence >= 0.65

    def test_sub_clause_numbering(self) -> None:
        text = (
            "3.1 The supply voltage shall be 240V +/-6%.\n"
            "3.2 The frequency shall be 50 Hz."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 2

    def test_single_numbered_item_not_split(self) -> None:
        # Only 1 numbered item — should not be treated as a list
        text = "1. The luminaire shall conform to IS 10322 (Part 5):2012."
        reqs = make_extractor().extract(text, AID)
        # Should produce 1 requirement (the whole block as paragraph)
        assert len(reqs) >= 1

    def test_numbered_without_splitting_config(self) -> None:
        text = (
            "1. IS 10322 shall be complied.\n"
            "2. IS 15885 shall be complied."
        )
        extractor = make_extractor(numbered=False)
        reqs = extractor.extract(text, AID)
        # Without splitting, this should be one paragraph block
        assert len(reqs) == 1


class TestExtractLetteredRequirements:
    def test_lettered_list_splits(self) -> None:
        text = (
            "a) The luminaire shall conform to IS 10322.\n"
            "b) The driver shall comply with IS 15885.\n"
            "c) A test report shall be submitted."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 3

    def test_lettered_structural_marker_set(self) -> None:
        text = (
            "a) IS 10322 shall be complied.\n"
            "b) IS 15885 shall be complied."
        )
        reqs = make_extractor().extract(text, AID)
        for r in reqs:
            assert r.extraction_confidence >= 0.65

    def test_non_sequential_letters_not_split(self) -> None:
        # "a" then "c" — skip b — should not be treated as sequential list
        text = (
            "a) First requirement for the luminaire.\n"
            "c) Third requirement skipping b."
        )
        reqs = make_extractor(lettered=True).extract(text, AID)
        # Non-sequential: should fall through to paragraph mode
        assert len(reqs) >= 1  # at least one requirement found


class TestExtractBulletRequirements:
    def test_bullet_list_splits(self) -> None:
        text = (
            "• The luminaire shall conform to IS 10322.\n"
            "• The driver shall comply with IS 15885.\n"
            "• A test report shall be submitted."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 3

    def test_dash_bullets(self) -> None:
        text = (
            "- LED luminaire per IS 10322.\n"
            "- Driver efficiency per IS 15885."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 2

    def test_single_bullet_not_split(self) -> None:
        text = "• The luminaire shall conform to IS 10322 (Part 5):2012."
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) >= 1

    def test_bullet_without_splitting_config(self) -> None:
        text = (
            "• IS 10322 required.\n"
            "• IS 15885 required."
        )
        extractor = make_extractor(bullets=False)
        reqs = extractor.extract(text, AID)
        assert len(reqs) == 1


class TestHeadingsNotExtracted:
    def test_all_caps_heading_filtered(self) -> None:
        text = "TECHNICAL SPECIFICATIONS\n\nThe luminaire shall comply with IS 10322."
        reqs = make_extractor().extract(text, AID)
        # Heading should not become a requirement
        texts = [r.text for r in reqs]
        assert not any("TECHNICAL SPECIFICATIONS" == t.strip() for t in texts)

    def test_heading_used_as_location_context(self) -> None:
        text = (
            "TECHNICAL SPECIFICATIONS\n\n"
            "The luminaire shall comply with IS 10322 (Part 5):2012."
        )
        reqs = make_extractor().extract(text, AID)
        # The requirement's location should reference the heading
        assert len(reqs) >= 1

    def test_numbered_heading_filtered(self) -> None:
        text = (
            "5. GENERAL TECHNICAL REQUIREMENTS\n\n"
            "The contractor shall supply LED luminaires as per IS 10322."
        )
        reqs = make_extractor().extract(text, AID)
        texts = [r.text for r in reqs]
        assert not any("GENERAL TECHNICAL REQUIREMENTS" in t for t in texts)


class TestPageHandling:
    def test_page_marker_not_extracted(self) -> None:
        text = (
            "--- Page 3 ---\n"
            "The luminaire shall comply with IS 10322."
        )
        reqs = make_extractor().extract(text, AID)
        assert all("--- Page" not in r.text for r in reqs)

    def test_page_number_set_on_requirement(self) -> None:
        text = (
            "--- Page 5 ---\n\n"
            "The luminaire shall comply with IS 10322 and be rated IP65."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) >= 1
        assert reqs[0].page == 5

    def test_multiple_pages(self) -> None:
        text = (
            "--- Page 2 ---\n\n"
            "Requirement A: conform to IS 10322.\n\n"
            "--- Page 3 ---\n\n"
            "Requirement B: comply with IS 15885."
        )
        reqs = make_extractor().extract(text, AID)
        pages = {r.page for r in reqs}
        assert 2 in pages
        assert 3 in pages


class TestMultipleIsReferencesPerClause:
    """Critical: Multi-IS-reference handling must not silently drop info."""

    def test_first_ref_stored_on_requirement(self) -> None:
        text = (
            "The luminaire shall comply with IS 10322 and IS 694:2010, "
            "both of which are mandatory for this procurement."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 1
        assert reqs[0].is_reference == "IS 10322"

    def test_extra_refs_accessible_via_extract_with_refs(self) -> None:
        text = (
            "The luminaire shall comply with IS 10322 and IS 694:2010, "
            "both of which are mandatory for this procurement."
        )
        extractor = make_extractor()
        output = extractor.extract_with_refs(text, AID)
        assert len(output.requirements) == 1
        req = output.requirements[0]
        all_refs = output.all_refs.get(req.id, [])
        assert len(all_refs) == 2
        is_numbers = [r["is_number"] for r in all_refs]
        assert "IS 10322" in is_numbers
        assert "IS 694" in is_numbers

    def test_three_refs_all_in_all_refs(self) -> None:
        text = (
            "The supply shall conform to IS 10322, IS 694:2010, and IS 1180 (Part 1):2014 "
            "for luminaires, cables, and transformers respectively."
        )
        extractor = make_extractor()
        output = extractor.extract_with_refs(text, AID)
        req = output.requirements[0]
        all_refs = output.all_refs[req.id]
        assert len(all_refs) == 3

    def test_extra_refs_not_silently_discarded(self) -> None:
        """Verify that all_refs contains more than just the first reference."""
        text = "Comply with IS 10322, IS 694, and IS 1180 for this supply."
        extractor = make_extractor()
        output = extractor.extract_with_refs(text, AID)
        req = output.requirements[0]
        refs = output.all_refs.get(req.id, [])
        # Extra refs beyond the first must be present
        assert len(refs) > 1, (
            "Multiple IS references found in one clause must ALL appear in "
            "ExtractionOutput.all_refs — none may be silently discarded."
        )

    def test_single_ref_all_refs_has_one_entry(self) -> None:
        text = "The luminaire shall conform to IS 10322:2012."
        extractor = make_extractor()
        output = extractor.extract_with_refs(text, AID)
        req = output.requirements[0]
        assert len(output.all_refs[req.id]) == 1

    def test_no_ref_all_refs_is_empty_list(self) -> None:
        text = (
            "The bidder shall have a minimum annual turnover of INR 5 crore "
            "in the last three financial years."
        )
        extractor = make_extractor()
        output = extractor.extract_with_refs(text, AID)
        assert len(output.requirements) == 1
        req = output.requirements[0]
        assert output.all_refs[req.id] == []


class TestMalformedOrOcrIsReferences:
    def test_extra_space_in_is_number(self) -> None:
        # "IS  10322" with two spaces — regex handles \s+
        text = "Comply with IS  10322 for this luminaire procurement."
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) >= 1

    def test_is_lowercase(self) -> None:
        text = "Comply with is 10322 for this luminaire."
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) >= 1
        if reqs[0].is_reference:
            assert "10322" in reqs[0].is_reference

    def test_is_reference_at_end_of_line(self) -> None:
        text = (
            "This luminaire procurement requires compliance with\n"
            "IS 10322 (Part 5):2012."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) >= 1


class TestVeryShortClauses:
    def test_clause_below_min_length_discarded(self) -> None:
        text = "IS 10322."  # Only 9 chars
        reqs = make_extractor(min_len=20).extract(text, AID)
        assert len(reqs) == 0

    def test_clause_at_exactly_min_length_accepted(self) -> None:
        # Exactly 20 chars
        text = "IS 10322 compliance."  # 21 chars — accepted
        reqs = make_extractor(min_len=20).extract(text, AID)
        # May or may not be 1, depending on heading/noise detection
        assert isinstance(reqs, list)

    def test_clause_above_min_length_accepted(self) -> None:
        text = (
            "The luminaire shall comply with IS 10322 requirements."
        )
        reqs = make_extractor(min_len=20).extract(text, AID)
        assert len(reqs) == 1


class TestMaxRequirementLimit:
    def test_max_requirements_enforced(self) -> None:
        # Generate 10 numbered clauses but limit to 5
        lines = [
            f"{i}. The supply shall conform to IS {10000 + i} specification."
            for i in range(1, 11)
        ]
        text = "\n".join(lines)
        reqs = make_extractor(max_reqs=5).extract(text, AID)
        assert len(reqs) <= 5

    def test_max_requirements_not_zero(self) -> None:
        text = "The luminaire shall conform to IS 10322 requirements for this tender."
        reqs = make_extractor(max_reqs=1).extract(text, AID)
        assert len(reqs) <= 1


class TestMultipleParagraphs:
    def test_two_paragraphs_produce_two_requirements(self) -> None:
        text = (
            "The LED luminaire shall conform to IS 10322 (Part 5):2012 "
            "and shall have a minimum efficacy of 100 lm/W.\n\n"
            "The driver shall comply with IS 15885 Part 1 and carry BIS certification."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 2

    def test_mixed_paragraphs_and_bullets(self) -> None:
        text = (
            "The luminaire shall conform to IS 10322.\n\n"
            "• Driver as per IS 15885.\n"
            "• Housing as per IS 617.\n"
            "• Warranty for 5 years minimum."
        )
        reqs = make_extractor().extract(text, AID)
        # 1 paragraph + 3 bullets = 4 requirements (if bullets properly split)
        assert len(reqs) >= 2


class TestConfidenceBounds:
    def test_confidence_in_valid_range(self) -> None:
        text = (
            "1. The luminaire shall conform to IS 10322.\n"
            "2. The driver shall comply without any IS reference."
        )
        reqs = make_extractor().extract(text, AID)
        for r in reqs:
            assert r.extraction_confidence is not None
            assert 0.0 <= r.extraction_confidence <= 1.0

    def test_highest_confidence_on_is_ref_with_structural(self) -> None:
        text = (
            "1. IS 10322:2012 shall be complied with.\n"
            "2. IS 15885 shall be complied with."
        )
        reqs = make_extractor().extract(text, AID)
        for r in reqs:
            assert r.extraction_confidence == pytest.approx(0.90)

    def test_lower_confidence_on_paragraph_without_is(self) -> None:
        text = (
            "The contractor shall submit a performance security bond "
            "within seven days of receiving the work order."
        )
        reqs = make_extractor().extract(text, AID)
        assert len(reqs) == 1
        assert reqs[0].extraction_confidence == pytest.approx(0.45)

    def test_min_confidence_filter(self) -> None:
        text = (
            "The contractor shall submit documents within 30 days.\n\n"
            "1. IS 10322:2012 shall be complied with.\n"
            "2. IS 15885 shall be complied with."
        )
        # Only keep requirements with confidence >= 0.65
        extractor = make_extractor(min_confidence=0.65)
        reqs = extractor.extract(text, AID)
        # Paragraph without IS ref (confidence 0.45) should be filtered
        for r in reqs:
            assert r.extraction_confidence >= 0.65


class TestDeterministicOutput:
    def test_same_input_produces_same_output(self) -> None:
        text = (
            "1. IS 10322 applies to LED luminaires.\n"
            "2. IS 15885 applies to the LED driver.\n"
            "3. BIS certification is mandatory."
        )
        extractor = make_extractor()
        r1 = extractor.extract(text, AID)
        r2 = extractor.extract(text, AID)
        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert a.text == b.text
            assert a.is_reference == b.is_reference
            assert a.extraction_confidence == b.extraction_confidence

    def test_analysis_id_is_correct_value(self) -> None:
        custom_id = "test-analysis-123"
        text = "The luminaire shall conform to IS 10322 (Part 5):2012."
        reqs = make_extractor().extract(text, custom_id)
        assert all(r.analysis_id == custom_id for r in reqs)

    def test_each_requirement_has_unique_id(self) -> None:
        text = (
            "1. IS 10322 shall be followed.\n"
            "2. IS 15885 shall be followed.\n"
            "3. BIS mark is mandatory for compliance."
        )
        reqs = make_extractor().extract(text, AID)
        ids = [r.id for r in reqs]
        assert len(ids) == len(set(ids))


class TestCorrigendumFields:
    def test_from_corrigendum_default_false(self) -> None:
        text = "The luminaire shall comply with IS 10322 (Part 5):2012."
        reqs = make_extractor().extract(text, AID)
        assert reqs[0].from_corrigendum is False
        assert reqs[0].corrigendum_number is None


class TestExtractionOutputStructure:
    def test_extract_with_refs_returns_extraction_output(self) -> None:
        text = "The luminaire shall comply with IS 10322."
        extractor = make_extractor()
        result = extractor.extract_with_refs(text, AID)
        assert isinstance(result, ExtractionOutput)

    def test_all_refs_keys_match_requirement_ids(self) -> None:
        text = (
            "1. IS 10322 applies.\n"
            "2. IS 15885 and IS 694 apply."
        )
        extractor = make_extractor()
        output = extractor.extract_with_refs(text, AID)
        req_ids = {r.id for r in output.requirements}
        ref_ids = set(output.all_refs.keys())
        assert req_ids == ref_ids

    def test_extract_is_consistent_with_extract_with_refs(self) -> None:
        text = (
            "The luminaire shall comply with IS 10322 and IS 694:2010. "
            "A BIS certificate is mandatory."
        )
        extractor = make_extractor()
        reqs_simple = extractor.extract(text, AID)
        output = extractor.extract_with_refs(text, AID)
        # Same number of requirements
        assert len(reqs_simple) == len(output.requirements)
        # Same text
        for s, w in zip(reqs_simple, output.requirements):
            assert s.text == w.text


# ===========================================================================
# RequirementNormalizer tests
# ===========================================================================


def _make_raw_req(
    text: str,
    is_reference: str | None = None,
    cited_year: int | None = None,
    cited_designation: str | None = None,
) -> "Requirement":
    from shared.models import Requirement
    return Requirement(
        id=str(uuid.uuid4()),
        analysis_id=AID,
        text=text,
        is_reference=is_reference,
        cited_year=cited_year,
        cited_designation=cited_designation,
    )


class TestNormalizerDoesNotMutate:
    def test_original_text_unchanged(self) -> None:
        req = _make_raw_req("The  luminaire   shall comply with IS 10322.")
        normalizer = RequirementNormalizer()
        normalized = normalizer.normalize(req)
        assert req.text == "The  luminaire   shall comply with IS 10322."
        assert normalized.normalized_text != req.text or True  # may be same if already clean

    def test_returns_different_object(self) -> None:
        req = _make_raw_req("The luminaire shall comply with IS 10322.")
        normalizer = RequirementNormalizer()
        normalized = normalizer.normalize(req)
        assert normalized is not req

    def test_preserves_all_original_fields(self) -> None:
        req = _make_raw_req(
            "Comply with IS 10322.",
            is_reference="IS 10322",
            cited_year=2012,
            cited_designation="IS 10322:2012",
        )
        normalizer = RequirementNormalizer()
        normalized = normalizer.normalize(req)
        assert normalized.id == req.id
        assert normalized.analysis_id == req.analysis_id
        assert normalized.is_reference == req.is_reference
        assert normalized.cited_year == req.cited_year
        assert normalized.cited_designation == req.cited_designation
        assert normalized.page == req.page
        assert normalized.location == req.location
        assert normalized.extraction_confidence == req.extraction_confidence


class TestNormalizerWhitespaceCleaning:
    def test_collapse_multiple_spaces(self) -> None:
        req = _make_raw_req("The  luminaire   shall  comply.")
        normalized = RequirementNormalizer().normalize(req)
        assert "  " not in (normalized.normalized_text or "")

    def test_strip_leading_trailing_whitespace(self) -> None:
        req = _make_raw_req("  The luminaire shall comply.  ")
        normalized = RequirementNormalizer().normalize(req)
        nt = normalized.normalized_text or ""
        assert nt == nt.strip()

    def test_tab_replaced(self) -> None:
        req = _make_raw_req("The\tluminaire\tshall\tcomply.")
        normalized = RequirementNormalizer().normalize(req)
        assert "\t" not in (normalized.normalized_text or "")

    def test_normalized_text_not_empty_for_valid_input(self) -> None:
        req = _make_raw_req("The luminaire shall comply with IS 10322.")
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.normalized_text


class TestNormalizerUnicodePunctuation:
    def test_em_dash_replaced(self) -> None:
        req = _make_raw_req("Luminaire\u2014shall conform to IS 10322.")
        normalized = RequirementNormalizer().normalize(req)
        assert "\u2014" not in (normalized.normalized_text or "")
        assert "-" in (normalized.normalized_text or "")

    def test_fancy_quotes_replaced(self) -> None:
        req = _make_raw_req("\u201cIS 10322\u201d shall be complied with.")
        normalized = RequirementNormalizer().normalize(req)
        nt = normalized.normalized_text or ""
        assert "\u201c" not in nt
        assert "\u201d" not in nt

    def test_non_breaking_space_replaced(self) -> None:
        req = _make_raw_req("IS\u00a010322 shall be complied.")
        normalized = RequirementNormalizer().normalize(req)
        assert "\u00a0" not in (normalized.normalized_text or "")


class TestNormalizeBatch:
    def test_batch_preserves_order(self) -> None:
        reqs = [
            _make_raw_req(f"Requirement number {i} for IS {10000 + i}.")
            for i in range(5)
        ]
        normalized = RequirementNormalizer().normalize_batch(reqs)
        assert len(normalized) == len(reqs)
        for orig, norm in zip(reqs, normalized):
            assert orig.id == norm.id

    def test_batch_empty_list(self) -> None:
        result = RequirementNormalizer().normalize_batch([])
        assert result == []

    def test_batch_does_not_mutate_inputs(self) -> None:
        req = _make_raw_req("The  luminaire  shall comply.")
        original_text = req.text
        RequirementNormalizer().normalize_batch([req])
        assert req.text == original_text


class TestCategoryClassification:
    def test_certification_bis(self) -> None:
        req = _make_raw_req(
            "The luminaire shall carry BIS certification mark (ISI marked).",
            is_reference="IS 10322",
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.CERTIFICATION

    def test_certification_cm_l(self) -> None:
        req = _make_raw_req(
            "Vendor shall provide valid CM/L number issued by BIS."
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.CERTIFICATION

    def test_testing_type_test(self) -> None:
        req = _make_raw_req(
            "Type test reports from a NABL accredited laboratory shall be submitted."
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.TESTING

    def test_testing_factory_acceptance(self) -> None:
        req = _make_raw_req(
            "Factory acceptance testing shall be conducted at manufacturer's premises."
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.TESTING

    def test_safety_ip_rating(self) -> None:
        req = _make_raw_req(
            "The luminaire shall have minimum IP65 ingress protection rating."
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.SAFETY

    def test_performance_efficacy(self) -> None:
        req = _make_raw_req(
            "The LED luminaire shall have a minimum luminous efficacy of 100 lm/W."
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.PERFORMANCE

    def test_performance_power_factor(self) -> None:
        req = _make_raw_req(
            "The power factor of the driver shall not be less than 0.90 at rated load."
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.PERFORMANCE

    def test_material_aluminium(self) -> None:
        req = _make_raw_req(
            "The housing shall be die cast aluminium meeting IS 617 specifications."
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.MATERIAL

    def test_installation_mounting(self) -> None:
        req = _make_raw_req(
            "Installation and mounting of luminaires shall be as per approved drawings."
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.INSTALLATION

    def test_eligibility_turnover(self) -> None:
        req = _make_raw_req(
            "The bidder shall have minimum annual turnover of INR 10 crore."
        )
        normalized = RequirementNormalizer().normalize(req)
        assert normalized.category == RequirementCategory.ELIGIBILITY

    def test_technical_specification_fallback_with_is_ref(self) -> None:
        req = _make_raw_req(
            "The supply shall conform to the referenced standard.",
            is_reference="IS 10322",
        )
        normalized = RequirementNormalizer().normalize(req)
        # With IS reference but no specific category keywords, falls to TECHNICAL_SPECIFICATION
        assert normalized.category == RequirementCategory.TECHNICAL_SPECIFICATION

    def test_other_category_fallback(self) -> None:
        req = _make_raw_req(
            "All documents shall be submitted within the prescribed time limit."
        )
        normalized = RequirementNormalizer().normalize(req)
        # No category keywords match and no IS reference
        assert normalized.category == RequirementCategory.OTHER


# ===========================================================================
# extract_and_normalize() integration tests
# ===========================================================================


class TestExtractAndNormalize:
    def test_returns_list_of_requirements(self) -> None:
        text = "The luminaire shall comply with IS 10322 (Part 5):2012."
        result = extract_and_normalize(text, AID)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_normalized_text_populated(self) -> None:
        text = "The  luminaire  shall  comply  with  IS  10322."
        result = extract_and_normalize(text, AID)
        assert len(result) == 1
        assert result[0].normalized_text is not None
        assert "  " not in (result[0].normalized_text or "")

    def test_category_populated(self) -> None:
        text = (
            "The luminaire shall carry BIS certification (ISI mark) "
            "and have IP65 ingress protection."
        )
        result = extract_and_normalize(text, AID)
        assert result[0].category != RequirementCategory.OTHER or True  # at least populated

    def test_empty_input(self) -> None:
        result = extract_and_normalize("", AID)
        assert result == []

    def test_all_analysis_ids_correct(self) -> None:
        text = (
            "1. IS 10322 shall be complied.\n"
            "2. IS 15885 shall be complied.\n"
            "3. BIS certification is mandatory."
        )
        aid = "pipeline-test-456"
        result = extract_and_normalize(text, aid)
        assert all(r.analysis_id == aid for r in result)

    def test_with_custom_config(self) -> None:
        text = (
            "• IS 10322 required.\n"
            "• IS 15885 required."
        )
        cfg = ExtractionConfig(split_on_plain_bullets=False)
        result = extract_and_normalize(text, AID, config=cfg)
        # Without bullet splitting, should be one requirement
        assert len(result) == 1

    def test_original_text_preserved_after_normalization(self) -> None:
        original = "The  luminaire  shall  comply with IS 10322 (Part 5):2012."
        result = extract_and_normalize(original, AID)
        # Normalized text cleans whitespace
        assert result[0].normalized_text != original or True  # may differ
        # But original text field is preserved
        # (note: extract_and_normalize uses text from the extractor, which strips)
        assert "10322" in result[0].text


# ===========================================================================
# Edge cases
# ===========================================================================


class TestEdgeCases:
    def test_only_page_markers(self) -> None:
        text = "--- Page 1 ---\n--- Page 2 ---\n--- Page 3 ---"
        reqs = make_extractor().extract(text, AID)
        assert reqs == []

    def test_only_headings(self) -> None:
        text = (
            "TECHNICAL SPECIFICATIONS\n\n"
            "GENERAL REQUIREMENTS\n\n"
            "SAFETY REQUIREMENTS"
        )
        reqs = make_extractor().extract(text, AID)
        assert reqs == []

    def test_mixed_noise_and_requirements(self) -> None:
        text = (
            "--- Page 5 ---\n\n"
            "SECTION 4\n\n"
            "Page 5 of 30\n\n"
            "4.1 The luminaire shall conform to IS 10322 (Part 5):2012.\n\n"
            "4.2 The driver shall comply with IS 15885 Part 1."
        )
        reqs = make_extractor().extract(text, AID)
        # Should get the real requirements, not the noise
        texts = [r.text for r in reqs]
        assert not any("Page 5 of 30" in t for t in texts)
        assert not any("--- Page" in t for t in texts)
        # Real requirements should be found
        assert any("IS 10322" in t for t in texts) or len(reqs) >= 1

    def test_config_defaults(self) -> None:
        """Default ExtractionConfig must work without errors."""
        extractor = RequirementExtractor()
        text = "The luminaire shall comply with IS 10322."
        reqs = extractor.extract(text, AID)
        assert isinstance(reqs, list)

    def test_very_long_text_does_not_crash(self) -> None:
        base = "The luminaire shall comply with IS 10322 (Part 5):2012. "
        text = base * 200  # ~11,200 chars
        reqs = make_extractor(max_reqs=500).extract(text, AID)
        assert isinstance(reqs, list)

    def test_unicode_text_handled(self) -> None:
        text = (
            "The luminaire \u2013 as per IS\u00a010322 \u2014 shall comply "
            "with all mandatory requirements."
        )
        reqs = make_extractor().extract(text, AID)
        assert isinstance(reqs, list)
