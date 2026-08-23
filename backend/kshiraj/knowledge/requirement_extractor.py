"""
kshiraj/knowledge/requirement_extractor.py

Deterministic extraction and normalization of procurement requirements
from raw tender text.

Module responsibilities
-----------------------
RequirementExtractor
    Takes raw extracted text (str) produced by
    ``kartikey/document_processing/extractor.py`` and yields a list of
    ``shared.models.Requirement`` objects.  Uses regex and structural
    heuristics only — no LLM, no HTTP, no embeddings.

RequirementNormalizer
    Takes raw ``Requirement`` objects and returns *copies* with
    ``normalized_text`` and ``category`` populated.  Deterministic
    keyword classification only.

ExtractionOutput
    Wrapper returned by :meth:`RequirementExtractor.extract_with_refs` that
    exposes *all* IS references detected per requirement, not just the first.
    This is needed because ``shared.models.Requirement.is_reference`` can only
    hold one IS number.  The extra references are stored here and must be
    reviewed before pipeline integration decides how to handle them.

extract_and_normalize()
    Pipeline-level convenience function that runs extraction then normalization
    in one call.  Returns ``list[Requirement]``.

IS reference regex
------------------
The regex pattern is derived from the one in
``kartikey/document_processing/extractor.py``.  It is intentionally
re-defined here (not imported) so that this module has no cross-boundary
dependency on kartikey.  If the regex is ever moved to ``shared/``, both
copies should be replaced with a single import.

Multi-IS-reference limitation
------------------------------
``shared.models.Requirement`` has a single ``is_reference: str | None`` field.
When multiple IS numbers appear in one clause, we:
  1. Populate ``is_reference`` with the *first* detected reference.
  2. Store *all* detected references (including the first) in
     ``ExtractionOutput.all_refs[req.id]``.
  3. NEVER silently discard the additional references.

Callers that need all detected references must use
:meth:`RequirementExtractor.extract_with_refs` instead of
:meth:`RequirementExtractor.extract`.  The pipeline (once wired) should
use ``ExtractionOutput`` to build retrieval queries for every detected IS
reference, not only the first.

Extraction confidence
---------------------
``extraction_confidence`` is a step-function heuristic score in [0.0, 1.0].
It is NOT a calibrated probability.  Its purpose is to allow downstream
components to deprioritize low-confidence extractions.

    0.90  IS reference found AND structural marker present
    0.80  IS reference found, no structural marker (paragraph mode)
    0.65  No IS reference, but structural marker present
    0.45  No IS reference, no structural marker (paragraph heuristic)

Anything scoring below the configured threshold is discarded; the default
threshold is 0.0 (keep everything that passes length checks).
"""

from __future__ import annotations

import re
import string
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from shared.models import Requirement, RequirementCategory


# ===========================================================================
# IS reference regex
# (mirrors the pattern in kartikey/document_processing/extractor.py)
# ===========================================================================

_IS_REF_RE = re.compile(
    r"IS\s+"              # "IS " prefix (case-insensitive due to re.IGNORECASE below)
    r"(\d+)"              # IS number digits
    r"(?:\s*\(([^)]+)\))?"  # optional (Part N/Sec M)
    r"(?:\s*:\s*(\d{4}))?"  # optional :YYYY year
    r"(?:\s+Amd\.?\s*(\d+))?",  # optional Amd.N
    re.IGNORECASE,
)

# ===========================================================================
# Structural heuristic patterns
# ===========================================================================

# Page markers inserted by extractor.py's PDF extraction
_PAGE_MARKER_RE = re.compile(
    r"^---\s*page\s+(\d+)\s*---\s*$", re.IGNORECASE
)

# Numbered clause/sub-clause: "1.", "1)", "1.1", "1.1.1", "3.2.4" at line start
_NUMBERED_CLAUSE_RE = re.compile(
    r"^(\d+(?:\.\d+)+|\d+[.)])\s*(.+)", re.DOTALL
)

# Lettered clause: "a)", "b.", "A)", "A." at line start
_LETTERED_CLAUSE_RE = re.compile(
    r"^([a-zA-Z])\s*[.)]\s+(.+)", re.DOTALL
)

# Bullet: "•", "-", "*", "–", "→" at line start
_BULLET_RE = re.compile(
    r"^[•\-\*–→]\s+(.+)", re.DOTALL
)

# Section heading heuristic:
#   - ALL CAPS lines of 5–80 chars (e.g. "TECHNICAL SPECIFICATIONS")
#   - Lines matching "N. HEADING TEXT" where heading is all-caps
#   - Lines ending with ":" and no sentence-forming words
_HEADING_RE = re.compile(
    r"^(?:"
    r"[A-Z][A-Z\s\-/()&,]{4,79}"   # ALL-CAPS block (at least 5 chars total)
    r"|"
    r"\d+(?:\.\d+)*\.?\s+[A-Z][A-Z\s\-/()]{4,60}"  # numbered ALL-CAPS heading
    r")$"
)

# Page number line: bare integer, possibly "Page N", "Page N of M", or "N of M"
_PAGE_NUMBER_RE = re.compile(
    r"^(?:page\s+)?\d+(?:\s+of\s+\d+)?$", re.IGNORECASE
)

# Mostly-dots line (table of contents filler / table borders)
_DOTS_LINE_RE = re.compile(r"^[.\-_=]{5,}$")

# Noise patterns in running headers/footers
_HEADER_FOOTER_RE = re.compile(
    r"^\s*(?:"
    r"s\.?\s*no\.?|serial\s+no\.?|sl\.?\s*no\.?"  # serial number column headers
    r"|tender\s+ref(?:erence)?|tender\s+no\.?"
    r"|bid\s+document|national\s+competitive"
    r"|cppp|gem\s+bid"
    r")\s*$",
    re.IGNORECASE,
)

# Procurement obligation verbs — strong signal that a span is a requirement
_OBLIGATION_RE = re.compile(
    r"\b(?:shall|must|should|required|mandatory|comply|conform|meet|"
    r"provide|supply|furnish|ensure|guarantee|certify|approved)\b",
    re.IGNORECASE,
)


# ===========================================================================
# Configuration
# ===========================================================================


@dataclass(frozen=True)
class ExtractionConfig:
    """Controls the behavior of :class:`RequirementExtractor`.

    All parameters have documented rationale so callers can adjust them
    for different tender formats without guessing.
    """

    #: Minimum character length (after stripping) for a span to become a Requirement.
    #: Shorter spans are almost always noise — table cell labels, column headers, etc.
    min_requirement_text_length: int = 20

    #: Hard upper bound on the number of Requirements produced from a single document.
    #: Guards against garbage text producing thousands of tiny fragments.
    max_requirements_per_document: int = 500

    #: If True, split numbered lists ("1. Clause\n2. Clause") into separate Requirements.
    split_on_numbered_bullets: bool = True

    #: If True, split lettered lists ("a) Clause\nb) Clause") into separate Requirements.
    split_on_lettered_bullets: bool = True

    #: If True, split bullet-point lists into separate Requirements.
    split_on_plain_bullets: bool = True

    #: Minimum extraction_confidence for a span to be kept (0.0 = keep all).
    #: Increase to 0.45 to discard low-confidence paragraph-mode extractions.
    min_confidence: float = 0.0


# ===========================================================================
# IS reference dict type alias
# ===========================================================================

#: One IS reference as detected by ``_IS_REF_RE``.
#: Keys: matched_text, is_number, part_section, year, amendment_number, char_offset
IsRefDict = Dict[str, object]


# ===========================================================================
# ExtractionOutput — carries full multi-reference information
# ===========================================================================


@dataclass
class ExtractionOutput:
    """
    Full output of :meth:`RequirementExtractor.extract_with_refs`.

    Use this instead of :meth:`~RequirementExtractor.extract` when you
    need access to *all* IS references detected within each requirement span,
    not just the first one.

    Attributes
    ----------
    requirements:
        The list of :class:`~shared.models.Requirement` objects.
        ``is_reference`` / ``cited_year`` / ``cited_designation`` are populated
        from the **first** detected IS reference in each span.
    all_refs:
        Maps each ``requirement.id`` → list of all IS reference dicts found in
        that span (same order as they appear in the text).  Includes the
        reference that was stored in ``is_reference``.
        Empty list if no IS references were found in that span.

    Multi-reference limitation
    --------------------------
    ``shared.models.Requirement.is_reference`` holds only one IS number.
    When a span contains multiple IS references (e.g. "IS 10322 and IS 694"),
    the extra references are accessible here.  They are NOT silently discarded.

    Before the pipeline is wired, the caller should iterate ``all_refs`` and
    decide how to handle multi-reference spans (e.g. generate one
    :class:`~kshiraj.knowledge.retrieval_service.RetrievalQuery` per
    detected reference).
    """

    requirements: List[Requirement]
    all_refs: Dict[str, List[IsRefDict]] = field(default_factory=dict)


# ===========================================================================
# Internal helpers
# ===========================================================================


def _detect_is_refs(text: str) -> List[IsRefDict]:
    """Return all IS references found in *text*, in order of appearance."""
    results: List[IsRefDict] = []
    for m in _IS_REF_RE.finditer(text):
        results.append(
            {
                "matched_text": m.group(0).strip(),
                "is_number": f"IS {m.group(1)}",
                "part_section": m.group(2),  # str | None
                "year": int(m.group(3)) if m.group(3) else None,
                "amendment_number": int(m.group(4)) if m.group(4) else None,
                "char_offset": m.start(),
            }
        )
    return results


def _score_confidence(has_is_ref: bool, has_structural_marker: bool) -> float:
    """Return the extraction confidence for a span.

    This is a step-function heuristic, NOT a calibrated probability.

    +------------------+--------------------+-----------+
    | has_is_ref       | has_structural     | score     |
    +------------------+--------------------+-----------+
    | True             | True               | 0.90      |
    | True             | False              | 0.80      |
    | False            | True               | 0.65      |
    | False            | False              | 0.45      |
    +------------------+--------------------+-----------+
    """
    if has_is_ref and has_structural_marker:
        return 0.90
    if has_is_ref:
        return 0.80
    if has_structural_marker:
        return 0.65
    return 0.45


def _is_noise(text: str) -> bool:
    """Return True if the text is clearly not a requirement."""
    stripped = text.strip()
    if not stripped:
        return True
    if _PAGE_MARKER_RE.match(stripped):
        return True
    if _PAGE_NUMBER_RE.match(stripped):
        return True
    if _DOTS_LINE_RE.match(stripped):
        return True
    if _HEADER_FOOTER_RE.match(stripped):
        return True
    return False


def _is_heading(text: str) -> bool:
    """Return True if the text looks like a section heading rather than a requirement.

    A heading:
      - Is a single line
      - Is either ALL-CAPS or matches the numbered-ALL-CAPS heading pattern
      - Does NOT contain procurement obligation verbs ("shall", "must", etc.)
      - Does NOT contain IS references
    """
    stripped = text.strip()
    lines = stripped.splitlines()
    if len(lines) != 1:
        return False
    if _OBLIGATION_RE.search(stripped):
        return False
    if _IS_REF_RE.search(stripped):
        return False
    return bool(_HEADING_RE.match(stripped))


@dataclass
class _Span:
    """Internal intermediate representation of a candidate requirement span."""

    text: str
    page: Optional[int]
    location_hint: Optional[str]
    structural_marker: bool  # True if came from a bullet/numbered/lettered list
    from_corrigendum: bool = False
    corrigendum_number: Optional[int] = None


# ===========================================================================
# RequirementExtractor
# ===========================================================================


class RequirementExtractor:
    """Deterministic, rule-based extractor that converts raw tender text to
    :class:`~shared.models.Requirement` objects.

    No LLM, no HTTP, no database calls, no embeddings.

    Parameters
    ----------
    config:
        Optional :class:`ExtractionConfig`.  Defaults to ``ExtractionConfig()``
        if not provided.

    Usage::

        extractor = RequirementExtractor()
        requirements = extractor.extract(text, analysis_id)

        # For full multi-IS-reference access:
        output = extractor.extract_with_refs(text, analysis_id)
        for req in output.requirements:
            all_is_refs = output.all_refs.get(req.id, [])
    """

    def __init__(self, config: Optional[ExtractionConfig] = None) -> None:
        self._config = config or ExtractionConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, text: str, analysis_id: str) -> List[Requirement]:
        """Extract requirements from *text* and return them.

        ``is_reference`` on each Requirement is set to the **first** IS
        reference detected in that span.  Additional references are silently
        accessible only via :meth:`extract_with_refs`.

        Parameters
        ----------
        text:
            Raw extracted text from a tender document or free-text input.
            Expected to come from
            ``kartikey.document_processing.extractor.extract_text()``.
        analysis_id:
            The ``Analysis.id`` these requirements belong to.

        Returns
        -------
        list[Requirement]
            Ordered by appearance in the source text.
        """
        return self.extract_with_refs(text, analysis_id).requirements

    def extract_with_refs(
        self, text: str, analysis_id: str
    ) -> ExtractionOutput:
        """Extract requirements and return full multi-IS-reference information.

        Use this method when you need to act on every IS reference in a clause,
        not just the first.  See :class:`ExtractionOutput` for details on the
        multi-reference limitation.

        Parameters
        ----------
        text:
            Raw extracted text.
        analysis_id:
            The ``Analysis.id`` to set on every produced requirement.

        Returns
        -------
        ExtractionOutput
            ``.requirements`` — ordered list of Requirement objects
            ``.all_refs``     — maps req.id → list of all IS ref dicts
        """
        cfg = self._config

        if not text or not text.strip():
            return ExtractionOutput(requirements=[], all_refs={})

        # Step 1: Parse text into candidate spans with page/location context.
        spans = self._parse_spans(text)

        # Step 2: Build Requirement objects from spans, filtering noise.
        requirements: List[Requirement] = []
        all_refs: Dict[str, List[IsRefDict]] = {}

        current_location: Optional[str] = None

        for span in spans:
            if len(requirements) >= cfg.max_requirements_per_document:
                break

            span_text = span.text.strip()

            if len(span_text) < cfg.min_requirement_text_length:
                continue
            if _is_noise(span_text):
                continue
            if _is_heading(span_text):
                # Use headings as location context for subsequent spans
                current_location = span_text
                continue

            # Detect IS references within this span
            is_refs = _detect_is_refs(span_text)
            has_is_ref = len(is_refs) > 0
            has_structural = span.structural_marker

            confidence = _score_confidence(has_is_ref, has_structural)
            if confidence < cfg.min_confidence:
                continue

            # Populate the single-value IS reference fields from the first ref
            first_ref = is_refs[0] if is_refs else None
            is_reference: Optional[str] = (
                str(first_ref["is_number"]) if first_ref else None
            )
            cited_year: Optional[int] = (
                int(first_ref["year"])  # type: ignore[arg-type]
                if first_ref and first_ref["year"] is not None
                else None
            )
            cited_designation: Optional[str] = (
                str(first_ref["matched_text"]) if first_ref else None
            )

            location = span.location_hint or current_location

            req = Requirement(
                id=str(uuid.uuid4()),
                analysis_id=analysis_id,
                text=span_text,
                is_reference=is_reference,
                cited_year=cited_year,
                cited_designation=cited_designation,
                page=span.page,
                location=location,
                extraction_confidence=confidence,
                from_corrigendum=span.from_corrigendum,
                corrigendum_number=span.corrigendum_number,
            )
            requirements.append(req)
            # Store ALL detected refs (including the first) for callers that need them.
            all_refs[req.id] = is_refs

        return ExtractionOutput(requirements=requirements, all_refs=all_refs)

    # ------------------------------------------------------------------
    # Internal: span parsing
    # ------------------------------------------------------------------

    def _parse_spans(self, text: str) -> List[_Span]:
        """Break *text* into candidate requirement spans.

        Strategy:
          1. Split on blank lines to get paragraph blocks.
          2. Track page markers to propagate ``page`` to subsequent spans.
          3. For each block, check if it is a list (numbered/lettered/bulleted)
             and split it further if configured to do so.
          4. Return the flat list of candidate ``_Span`` objects.
        """
        cfg = self._config
        spans: List[_Span] = []
        current_page: Optional[int] = None
        current_section: Optional[str] = None

        # Split on runs of blank lines to separate paragraph blocks
        raw_blocks = re.split(r"\n{2,}", text)

        for block in raw_blocks:
            block = block.strip()
            if not block:
                continue

            # Check if this block is a page marker
            page_match = _PAGE_MARKER_RE.match(block)
            if page_match:
                current_page = int(page_match.group(1))
                continue

            # Check if this block contains page markers mid-block (PDF join artifact)
            # Split at page markers and process sub-blocks
            sub_blocks = re.split(
                r"(?m)^---\s*page\s+(\d+)\s*---\s*$", block, flags=re.IGNORECASE
            )
            if len(sub_blocks) > 1:
                # Odd-indexed parts are page numbers, even-indexed are text
                for idx, sub in enumerate(sub_blocks):
                    sub = sub.strip()
                    if not sub:
                        continue
                    if re.fullmatch(r"\d+", sub):
                        current_page = int(sub)
                        continue
                    spans.extend(
                        self._block_to_spans(
                            sub, current_page, current_section, cfg
                        )
                    )
                continue

            spans.extend(
                self._block_to_spans(block, current_page, current_section, cfg)
            )

        return spans

    def _block_to_spans(
        self,
        block: str,
        page: Optional[int],
        section: Optional[str],
        cfg: ExtractionConfig,
    ) -> List[_Span]:
        """Convert one paragraph block into zero or more ``_Span`` objects.

        If the block looks like a list, it is split into individual items.
        Otherwise the whole block becomes one span.
        """
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines:
            return []

        # --- Attempt to detect a multi-item list within the block ---

        if cfg.split_on_numbered_bullets:
            items = self._split_numbered_list(lines)
            if items:
                return [
                    _Span(
                        text=item,
                        page=page,
                        location_hint=section,
                        structural_marker=True,
                    )
                    for item in items
                ]

        if cfg.split_on_lettered_bullets:
            items = self._split_lettered_list(lines)
            if items:
                return [
                    _Span(
                        text=item,
                        page=page,
                        location_hint=section,
                        structural_marker=True,
                    )
                    for item in items
                ]

        if cfg.split_on_plain_bullets:
            items = self._split_bullet_list(lines)
            if items:
                return [
                    _Span(
                        text=item,
                        page=page,
                        location_hint=section,
                        structural_marker=True,
                    )
                    for item in items
                ]

        # --- No list structure — treat as a single paragraph span ---
        return [
            _Span(
                text=block,
                page=page,
                location_hint=section,
                structural_marker=False,
            )
        ]

    # ------------------------------------------------------------------
    # Internal: list detection and splitting
    # ------------------------------------------------------------------

    def _split_numbered_list(self, lines: List[str]) -> List[str]:
        """If *lines* form a numbered list, return the items; else return []."""
        items: List[str] = []
        current: List[str] = []

        for line in lines:
            m = _NUMBERED_CLAUSE_RE.match(line.strip())
            if m:
                if current:
                    items.append(" ".join(current))
                current = [m.group(2).strip()]
            else:
                if current:
                    current.append(line.strip())

        if current:
            items.append(" ".join(current))

        # Only return as a list if at least 2 items were found
        return items if len(items) >= 2 else []

    def _split_lettered_list(self, lines: List[str]) -> List[str]:
        """If *lines* form a lettered list (a), b), ...), return items; else []."""
        items: List[str] = []
        current: List[str] = []
        last_letter: Optional[str] = None

        for line in lines:
            m = _LETTERED_CLAUSE_RE.match(line.strip())
            if m:
                letter = m.group(1).lower()
                # Accept only sequential letters to avoid false positives
                if last_letter is None or ord(letter) == ord(last_letter) + 1:
                    if current:
                        items.append(" ".join(current))
                    current = [m.group(2).strip()]
                    last_letter = letter
                else:
                    if current:
                        current.append(line.strip())
            else:
                if current:
                    current.append(line.strip())

        if current:
            items.append(" ".join(current))

        return items if len(items) >= 2 else []

    def _split_bullet_list(self, lines: List[str]) -> List[str]:
        """If *lines* form a bullet list, return items; else return []."""
        items: List[str] = []
        current: List[str] = []

        for line in lines:
            m = _BULLET_RE.match(line.strip())
            if m:
                if current:
                    items.append(" ".join(current))
                current = [m.group(1).strip()]
            else:
                if current:
                    current.append(line.strip())

        if current:
            items.append(" ".join(current))

        return items if len(items) >= 2 else []


# ===========================================================================
# RequirementNormalizer
# ===========================================================================

# Punctuation translation table: replaces fancy quotes, dashes, etc.
_UNICODE_PUNCT_MAP = str.maketrans(
    {
        "\u2019": "'",   # right single quotation mark
        "\u2018": "'",   # left single quotation mark
        "\u201c": '"',   # left double quotation mark
        "\u201d": '"',   # right double quotation mark
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u00a0": " ",   # non-breaking space
        "\u00ad": "",    # soft hyphen
    }
)

# Patterns that indicate running headers / footers to strip from the start/end
_BOILERPLATE_LINE_RE = re.compile(
    r"(?im)^(?:"
    r"page\s+\d+(?:\s+of\s+\d+)?"
    r"|tender\s+ref(?:erence)?\s*:?\s*\S+"
    r"|bid\s+document\s+no\."
    r"|confidential"
    r")\s*$"
)

# Collapse runs of whitespace (spaces and tabs)
_MULTI_SPACE_RE = re.compile(r"[ \t]+")

# Category keyword maps — each maps a RequirementCategory to a list of
# lowercase token substrings or regexes that are strong signals for that category.
# Order matters: first match wins.
_CATEGORY_KEYWORDS: List[Tuple[RequirementCategory, List[str]]] = [
    (
        RequirementCategory.CERTIFICATION,
        [
            "bis certification", "isi mark", "isi marked", "cm/l", "r-number",
            "hallmarking", "huid", "certifi", "licence", "license", r"\bbom\b",
            "bureau of indian standards", "bis registered", r"\bcrs\b",
        ],
    ),
    (
        RequirementCategory.TESTING,
        [
            "type test", "factory acceptance test", "routine test", "test report",
            "testing certificate", "third party test", "acceptance test",
            "test at site", "commissioning test",
        ],
    ),
    (
        RequirementCategory.SAFETY,
        [
            "ip65", "ip66", "ip54", r"\bip\d+\b",
            "iec 60598", "iec 60529", "iec ",
            "earthing", "grounding", "short circuit",
            "fire rating", "flame retardant", "self-extinguishing",
            "protective earth", "double insulated", "class ii",
        ],
    ),
    (
        RequirementCategory.PERFORMANCE,
        [
            "luminous efficacy", "lumen output", "colour rendering",
            r"\bcri\b", "correlated colour", r"\bcct\b", "power factor",
            "total harmonic distortion", r"\bthd\b", r"\bwatt\b", r"\blux\b",
            "illuminance", "efficiency", "rated output", r"\bflux\b",
        ],
    ),
    (
        RequirementCategory.MATERIAL,
        [
            "material ", "die cast", "aluminium", "aluminum", "stainless steel",
            "galvanised", "galvanized", "polycarbonate", "glass",
            "copper conductor", "acsr", "pvc insulated",
        ],
    ),
    (
        RequirementCategory.INSTALLATION,
        [
            "installation", "mounting", "fixing", "commissioning",
            "erection", "civil work", "cable laying", "pulling",
        ],
    ),
    (
        RequirementCategory.ELIGIBILITY,
        [
            "experience", "annual turnover", "registered",
            "empanelled", r"\boem\b", "authorized", "authorised",
            "manufacturer", "years of experience",
        ],
    ),
    (
        RequirementCategory.TECHNICAL_SPECIFICATION,
        [
            "is 10322", "is 1180", "is 694", "as per is", "conform to is",
            "comply with is", "as per standard", "shall conform",
            "technical specification", "specification", "standard",
        ],
    ),
]


class RequirementNormalizer:
    """Cleans and classifies raw :class:`~shared.models.Requirement` objects.

    Returns *copies* — never mutates the input.

    Normalization steps applied:
    1. Translate Unicode punctuation (fancy quotes, em-dash, etc.)
    2. Remove boilerplate header/footer lines
    3. Collapse runs of spaces/tabs to a single space
    4. Strip leading/trailing whitespace

    Category classification:
    - Keyword-heuristic only (no ML, no LLM).
    - Returns the first matching category from ``_CATEGORY_KEYWORDS``.
    - Falls back to ``RequirementCategory.OTHER`` if no keywords match.
    - The classification is conservative: it will not override an explicit
      IS-reference-based signal.

    Do NOT interpret the assigned category as authoritative.  It is a best-
    effort label to assist the AI/ML layer.  The AI/ML component may override
    it.
    """

    def normalize(self, requirement: Requirement) -> Requirement:
        """Return a new Requirement with ``normalized_text`` and ``category`` set.

        The input Requirement is not modified.
        All fields not touched by normalization are copied verbatim.
        """
        raw = requirement.text
        cleaned = self._clean_text(raw)
        category = self._classify_category(cleaned, requirement.is_reference)

        return requirement.model_copy(
            update={
                "normalized_text": cleaned,
                "category": category,
            }
        )

    def normalize_batch(
        self, requirements: List[Requirement]
    ) -> List[Requirement]:
        """Normalize a list of requirements and return a new list.

        Order is preserved.  The input list and its elements are not modified.
        """
        return [self.normalize(r) for r in requirements]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _clean_text(self, raw: str) -> str:
        """Apply all text cleaning steps to *raw* and return the result."""
        # 1. Translate Unicode punctuation to ASCII equivalents
        text = raw.translate(_UNICODE_PUNCT_MAP)

        # 2. Remove boilerplate header/footer lines
        text = _BOILERPLATE_LINE_RE.sub("", text)

        # 3. Collapse multiple spaces/tabs (preserve newlines)
        text = _MULTI_SPACE_RE.sub(" ", text)

        # 4. Strip each line then rejoin to remove leading/trailing spaces per line
        lines = [ln.strip() for ln in text.splitlines()]
        # Remove empty lines that appeared after boilerplate removal
        lines = [ln for ln in lines if ln]
        text = " ".join(lines)  # flatten to a single line

        # 5. Final strip
        return text.strip()

    def _classify_category(
        self, normalized_text: str, is_reference: Optional[str]
    ) -> RequirementCategory:
        """Classify a requirement using keyword heuristics.

        Matches the *first* category whose keywords appear in the lowercased
        normalized text.  Falls back to ``OTHER``.

        Note: This is not ML.  Keywords are hand-curated for the LED street
        lighting MVP vertical and will require extension for other verticals.
        """
        lower = normalized_text.lower()

        for category, keywords in _CATEGORY_KEYWORDS:
            for kw in keywords:
                if "\\" in kw or kw.startswith(r"\b"):
                    if re.search(kw, lower):
                        return category
                elif kw in lower:
                    return category

        # If an IS reference is present but no other category matched, this is
        # at minimum a technical specification.
        if is_reference:
            return RequirementCategory.TECHNICAL_SPECIFICATION

        return RequirementCategory.OTHER


# ===========================================================================
# Pipeline convenience function
# ===========================================================================


def extract_and_normalize(
    text: str,
    analysis_id: str,
    config: Optional[ExtractionConfig] = None,
) -> List[Requirement]:
    """Extract requirements from *text* and normalize them in one call.

    This is the intended entry point for the pipeline
    (``kartikey/orchestration/pipeline._step_extract``).

    Parameters
    ----------
    text:
        Raw extracted text from a tender document or free-text input.
    analysis_id:
        The ``Analysis.id`` that these requirements belong to.
    config:
        Optional extraction config.  Defaults to ``ExtractionConfig()``.

    Returns
    -------
    list[Requirement]
        Ordered by appearance.  All requirements have ``normalized_text`` and
        ``category`` populated.  ``is_reference`` is set to the **first**
        IS reference found in each clause.

    Notes
    -----
    If you need access to additional IS references in multi-citation clauses,
    use :class:`RequirementExtractor` and :meth:`~RequirementExtractor.extract_with_refs`
    directly instead of this function.
    """
    extractor = RequirementExtractor(config)
    normalizer = RequirementNormalizer()
    raw = extractor.extract(text, analysis_id)
    return normalizer.normalize_batch(raw)
