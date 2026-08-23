"""
kshiraj/enrichment/version_checker.py

Deterministic version/currentness checking for tender requirements.

This module compares the edition year cited in a Requirement against
the year of a candidate Standard.

It deliberately does NOT mutate either input object and does not perform
network access or source discovery. Status/QCO enrichment can be layered
on top of this result by the orchestration/analysis layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.models import Requirement, Standard


@dataclass(frozen=True)
class VersionCheckResult:
    """Result of comparing a cited standard edition with a candidate standard."""

    cited_year: int | None
    current_year: int | None
    is_current: bool
    is_year_omitted: bool
    gap_years: int | None
    note: str


class VersionChecker:
    """
    Compare the version cited in a procurement requirement with a Standard.

    The checker is intentionally deterministic:

      cited year == current year
          -> current

      cited year < current year
          -> outdated

      cited year > current year
          -> future/unknown reference, therefore not current

      cited year is None
          -> year omitted; cannot establish edition equality, but the
             reference itself is not classified as outdated

      candidate standard year is None
          -> current edition cannot be established
    """

    def check(
        self,
        requirement: Requirement,
        standard: Standard,
    ) -> VersionCheckResult:
        """
        Compare requirement.cited_year with standard.year.

        Neither requirement nor standard is modified.
        """

        cited_year = requirement.cited_year
        current_year = standard.year

        # The tender omitted the edition year.
        if cited_year is None:
            return VersionCheckResult(
                cited_year=None,
                current_year=current_year,
                is_current=True,
                is_year_omitted=True,
                gap_years=None,
                note=(
                    f"The tender cites {requirement.is_reference or standard.is_number} "
                    "without specifying an edition year. The reference is not "
                    "classified as outdated, but the omitted year creates "
                    "version ambiguity."
                ),
            )

        # We do not know the year of the candidate/current standard.
        if current_year is None:
            return VersionCheckResult(
                cited_year=cited_year,
                current_year=None,
                is_current=False,
                is_year_omitted=False,
                gap_years=None,
                note=(
                    f"The tender cites the {cited_year} edition, but the current "
                    "standard year is unavailable. Currentness cannot be "
                    "established."
                ),
            )

        gap_years = current_year - cited_year

        # Exact edition match.
        if gap_years == 0:
            return VersionCheckResult(
                cited_year=cited_year,
                current_year=current_year,
                is_current=True,
                is_year_omitted=False,
                gap_years=0,
                note=(
                    f"The cited {cited_year} edition matches the current "
                    f"standard edition ({current_year})."
                ),
            )

        # Tender cites an older edition.
        if gap_years > 0:
            return VersionCheckResult(
                cited_year=cited_year,
                current_year=current_year,
                is_current=False,
                is_year_omitted=False,
                gap_years=gap_years,
                note=(
                    f"The tender cites the {cited_year} edition, which is "
                    f"{gap_years} year(s) older than the current "
                    f"{current_year} edition."
                ),
            )

        # Tender cites an edition newer than the candidate standard.
        return VersionCheckResult(
            cited_year=cited_year,
            current_year=current_year,
            is_current=False,
            is_year_omitted=False,
            gap_years=gap_years,
            note=(
                f"The tender cites the {cited_year} edition, which is "
                f"{abs(gap_years)} year(s) newer than the candidate "
                f"{current_year} edition. This reference is not treated "
                "as current."
            ),
        )
