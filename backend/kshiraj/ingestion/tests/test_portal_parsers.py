"""
kshiraj/ingestion/tests/test_portal_parsers.py

Unit tests for portal-specific parsers: BIS, CPPP, DPIIT, and eGazette.
"""

from __future__ import annotations

import pytest

from kshiraj.ingestion.models import PageMetadata, RawDocument
from kshiraj.ingestion.parsers import (
    BisPortalParser,
    CpppPortalParser,
    DpiitPortalParser,
    EgazettePortalParser,
)


class TestPortalParsers:

    def test_bis_portal_parser_from_table(self):
        parser = BisPortalParser()
        raw_doc = RawDocument(
            source_url="https://services.bis.gov.in/standards/10322",
            canonical_url="https://services.bis.gov.in/standards/10322",
            source_name="BIS Catalog",
            text_content="Scope: Specification for luminaires and emergency lighting systems.",
            metadata=PageMetadata(
                title="BIS Standards Directory",
                tables=[
                    [
                        {
                            "is_number": "IS 10322 : Part 5 : Sec 3 : 2014",
                            "title": "Luminaires - Emergency Lighting",
                            "status": "active",
                            "year": "2014",
                        }
                    ]
                ]
            )
        )

        assert parser.can_handle(raw_doc) is True
        payload = parser.parse_document(raw_doc)

        assert payload["is_number"] == "IS 10322"
        assert payload["part"] == 5
        assert payload["section"] == 3
        assert payload["year"] == 2014
        assert payload["title"] == "Luminaires - Emergency Lighting"
        assert payload["status"] == "active"

    def test_bis_portal_parser_from_text(self):
        parser = BisPortalParser()
        raw_doc = RawDocument(
            source_url="https://bis.gov.in/standards/is2062",
            canonical_url="https://bis.gov.in/standards/is2062",
            source_name="BIS",
            text_content="IS 2062:2011 Hot Rolled Medium and High Tensile Structural Steel. Technical Committee: CED 02. Division: Civil Engineering.",
            metadata=PageMetadata(title="IS 2062 Specification")
        )

        payload = parser.parse_document(raw_doc)
        assert payload["is_number"] == "IS 2062"
        assert payload["year"] == 2011
        assert "CED 02" in payload["technical_committee"]

    def test_cppp_portal_parser(self):
        parser = CPPP_parser = CpppPortalParser()
        raw_doc = RawDocument(
            source_url="https://eprocure.gov.in/tenders/tender123",
            canonical_url="https://eprocure.gov.in/tenders/tender123",
            source_name="CPPP eProcure",
            text_content="Tender Reference: 2026_CPWD_555432_1. Work of Electrical Rewiring. All wiring must comply with IS 732. Control gear safe as per IS 15885. Procuring Authority: CPWD.",
            metadata=PageMetadata(title="NIT for Hospital Electrification")
        )

        assert parser.can_handle(raw_doc) is True
        payload = parser.parse_document(raw_doc)

        assert payload["tender_id"] == "2026_CPWD_555432_1"
        assert "CPWD" in payload["procuring_authority"]
        assert "IS 732" in payload["referenced_standards"]
        assert "IS 15885" in payload["referenced_standards"]

    def test_dpiit_qco_parser(self):
        parser = DpiitPortalParser()
        raw_doc = RawDocument(
            source_url="https://dpiit.gov.in/qco_steel",
            canonical_url="https://dpiit.gov.in/qco_steel",
            source_name="DPIIT QCO Notification",
            text_content="S.O. 4567(E) Ministry of Steel. In exercise of powers conferred by BIS Act, Steel and Steel Products Quality Control Order mandates IS 1786. Implementation Date: 15th October 2026.",
            metadata=PageMetadata(title="Steel Quality Control Order 2026")
        )

        assert parser.can_handle(raw_doc) is True
        payload = parser.parse_document(raw_doc)

        assert payload["gazette_so_number"] == "S.O. 4567(E)"
        assert "Ministry of Steel" in payload["issuing_ministry"]
        assert "IS 1786" in payload["is_number"]
        assert payload["effective_date"] is not None

    def test_egazette_parser(self):
        parser = EgazettePortalParser()
        raw_doc = RawDocument(
            source_url="https://egazette.gov.in/notif/275689",
            canonical_url="https://egazette.gov.in/notif/275689",
            source_name="eGazette",
            text_content="Extraordinary Gazette CG-UP-E-22082026-275689. Ministry of Railways. Notification under Railways Act. Date: 22-Aug-2026.",
            metadata=PageMetadata(title="Gazette Notification")
        )

        assert parser.can_handle(raw_doc) is True
        payload = parser.parse_document(raw_doc)

        assert payload["gazette_so_number"] == "CG-UP-E-22082026-275689"
