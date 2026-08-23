"""
kshiraj/source_adapters/test_adapters.py

Comprehensive unit tests for kshiraj.source_adapters package:
  - BaseSourceAdapter
  - BisAdapter
  - BisDraftsAdapter
  - CpppAdapter
  - QcoAdapter
"""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from shared.models import (
    CertificationScheme,
    DocumentType,
    Evidence,
    EvidenceSourceType,
    Standard,
    StandardStatus,
)
from shared.utils import SourceAdapterError

from kshiraj.source_adapters.base import BaseSourceAdapter
from kshiraj.source_adapters.bis_adapter import BisAdapter
from kshiraj.source_adapters.bis_drafts_adapter import BisDraftsAdapter
from kshiraj.source_adapters.cppp_adapter import CpppAdapter
from kshiraj.source_adapters.qco_adapter import QcoAdapter


# ===========================================================================
# 1. BaseSourceAdapter Tests
# ===========================================================================

class TestBaseSourceAdapter:

    def test_parse_year(self):
        adapter = BaseSourceAdapter()
        assert adapter.parse_year(2012) == 2012
        assert adapter.parse_year("2012") == 2012
        assert adapter.parse_year("Published in 2015 Amd.2") == 2015
        assert adapter.parse_year(None) is None
        assert adapter.parse_year("Invalid") is None

    def test_parse_date(self):
        adapter = BaseSourceAdapter()
        d = date(2024, 1, 15)
        assert adapter.parse_date(d) == d
        assert adapter.parse_date("2024-01-15") == d
        assert adapter.parse_date(None) is None
        assert adapter.parse_date("invalid-date") is None

    def test_parse_int(self):
        adapter = BaseSourceAdapter()
        assert adapter.parse_int(5) == 5
        assert adapter.parse_int("12") == 12
        assert adapter.parse_int(None) is None
        assert adapter.parse_int("abc") is None

    def test_fetch_url_success(self):
        adapter = BaseSourceAdapter()
        mock_resp = MagicMock()
        mock_resp.text = "<html>BIS Standard content</html>"

        with patch("httpx.Client.get", return_value=mock_resp) as mock_get:
            result = adapter.fetch_url("http://bis.gov.in/std/10322")
            assert result == "<html>BIS Standard content</html>"
            mock_get.assert_called_once_with("http://bis.gov.in/std/10322")

    def test_fetch_url_http_error(self):
        adapter = BaseSourceAdapter()
        req = httpx.Request("GET", "http://bis.gov.in/std/99999")
        resp = httpx.Response(500, request=req)

        with patch("httpx.Client.get", side_effect=httpx.HTTPStatusError("500 Error", request=req, response=resp)):
            with pytest.raises(SourceAdapterError) as exc_info:
                adapter.fetch_url("http://bis.gov.in/std/99999")
            assert exc_info.value.code == "HTTP_500"

    def test_fetch_url_timeout(self):
        adapter = BaseSourceAdapter()
        with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Timeout")):
            with pytest.raises(SourceAdapterError) as exc_info:
                adapter.fetch_url("http://bis.gov.in/std/10322")
            assert exc_info.value.code == "TIMEOUT"

    def test_fetch_url_connection_error(self):
        adapter = BaseSourceAdapter()
        with patch("httpx.Client.get", side_effect=httpx.RequestError("Connection refused")):
            with pytest.raises(SourceAdapterError) as exc_info:
                adapter.fetch_url("http://bis.gov.in/std/10322")
            assert exc_info.value.code == "CONNECTION_ERROR"

    @pytest.mark.asyncio
    async def test_fetch_url_async_success(self):
        adapter = BaseSourceAdapter()
        mock_resp = MagicMock()
        mock_resp.text = "Async content"

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            result = await adapter.fetch_url_async("http://bis.gov.in/std/10322")
            assert result == "Async content"


# ===========================================================================
# 2. BisAdapter Tests
# ===========================================================================

class TestBisAdapter:

    @pytest.fixture
    def adapter(self) -> BisAdapter:
        return BisAdapter()

    def test_parse_full_standard_data_dict(self, adapter: BisAdapter):
        payload = {
            "is_number": "IS 10322",
            "part": "Part 5",
            "section": "Sec 3",
            "year": 2012,
            "title": "Luminaires - Particular Requirements",
            "scope": "Covers floodlights for industrial outdoor lighting.",
            "status": "active",
            "document_type": "product_specification",
            "ics_code": "91.100.10",
            "division_council": "ETD",
            "technical_committee": "ETD 13",
            "reaffirmation_year": 2017,
            "amendments": [
                {
                    "amendment_number": 1,
                    "year": 2015,
                    "description": "Clause 4.1 updated.",
                    "gazette_so_number": "S.O. 100(E)",
                }
            ],
            "source_url": "http://standardsbis.gov.in/std/10322-5-3",
        }

        std, evidence_list = adapter.parse_standard_data(payload)

        assert isinstance(std, Standard)
        assert std.is_number == "IS 10322"
        assert std.part == "Part 5"
        assert std.section == "Sec 3"
        assert std.year == 2012
        assert std.designation == "IS 10322 (Part 5/Sec 3):2012 Amd.1"
        assert std.status == StandardStatus.ACTIVE
        assert std.document_type == DocumentType.PRODUCT_SPECIFICATION
        assert std.reaffirmation_year == 2017
        assert len(std.amendments) == 1
        assert std.amendments[0].amendment_number == 1
        assert std.source_url == "http://standardsbis.gov.in/std/10322-5-3"

        assert len(evidence_list) == 2
        assert evidence_list[0].source_type == EvidenceSourceType.BIS_STANDARD
        assert evidence_list[0].authority == "BIS"
        assert evidence_list[1].source_type == EvidenceSourceType.BIS_AMENDMENT
        assert evidence_list[1].amendment_number == 1

    def test_parse_standard_json_string(self, adapter: BisAdapter):
        payload_json = '{"is_number": "IS 694", "title": "PVC Insulated Cables", "year": 2010, "status": "active"}'
        std, evidence_list = adapter.parse_standard_data(payload_json, source_url="http://bis.gov.in/694")

        assert std.is_number == "IS 694"
        assert std.title == "PVC Insulated Cables"
        assert std.source_url == "http://bis.gov.in/694"
        assert evidence_list[0].url == "http://bis.gov.in/694"

    def test_parse_standard_missing_required_fields_raises(self, adapter: BisAdapter):
        with pytest.raises(SourceAdapterError) as exc_info:
            adapter.parse_standard_data({"year": 2020})
        assert exc_info.value.code == "MISSING_REQUIRED_FIELDS"

    def test_parse_standard_malformed_json_raises(self, adapter: BisAdapter):
        with pytest.raises(SourceAdapterError) as exc_info:
            adapter.parse_standard_data("invalid json {{{")
        assert exc_info.value.code == "INVALID_PAYLOAD"

    def test_parse_standard_superseded_and_withdrawn_status(self, adapter: BisAdapter):
        payload_sup = {
            "is_number": "IS 10322",
            "year": 1982,
            "title": "Old Luminaires",
            "status": "superseded",
            "superseded_by": "IS 10322 (Part 5/Sec 3):2012",
        }
        std_sup, _ = adapter.parse_standard_data(payload_sup)
        assert std_sup.status == StandardStatus.SUPERSEDED
        assert std_sup.superseded_by == "IS 10322 (Part 5/Sec 3):2012"


# ===========================================================================
# 3. BisDraftsAdapter Tests
# ===========================================================================

class TestBisDraftsAdapter:

    @pytest.fixture
    def adapter(self) -> BisDraftsAdapter:
        return BisDraftsAdapter()

    def test_parse_draft_data(self, adapter: BisDraftsAdapter):
        payload = {
            "draft_number": "ETD 13 (12345)",
            "title": "Draft Specification for LED Drivers",
            "scope": "Covers safety and performance of electronic drivers.",
            "technical_committee": "ETD 13",
            "draft_date": "2026-02-01",
        }
        url = "http://bis.gov.in/drafts/ETD13_12345"

        std, evidence_list = adapter.parse_draft_data(payload, source_url=url)

        assert std.is_number == "DRAFT ETD 13 (12345)"
        assert std.title == "Draft Specification for LED Drivers"
        assert std.status == StandardStatus.UNDER_REVISION  # Drafts are UNDER_REVISION
        assert std.source_url == url

        assert len(evidence_list) == 1
        assert evidence_list[0].source_type == EvidenceSourceType.BIS_WIDE_CIRCULATION_DRAFT
        assert evidence_list[0].authority == "BIS"
        assert evidence_list[0].url == url
        assert evidence_list[0].confidence == 0.85

    def test_parse_draft_already_prefixed(self, adapter: BisDraftsAdapter):
        payload = {
            "draft_number": "DRAFT IS 10322-5-3",
            "title": "Draft revision",
        }
        std, _ = adapter.parse_draft_data(payload)
        assert std.is_number == "DRAFT IS 10322-5-3"

    def test_parse_draft_missing_fields_raises(self, adapter: BisDraftsAdapter):
        with pytest.raises(SourceAdapterError) as exc_info:
            adapter.parse_draft_data({"scope": "Some scope without title or number"})
        assert exc_info.value.code == "MISSING_REQUIRED_FIELDS"


# ===========================================================================
# 4. CpppAdapter Tests
# ===========================================================================

class TestCpppAdapter:

    @pytest.fixture
    def adapter(self) -> CpppAdapter:
        return CpppAdapter()

    def test_parse_tender_data_full(self, adapter: CpppAdapter):
        payload = {
            "tender_id": "2026_DEPT_123456_1",
            "technical_specification": "Supply of LED streetlight luminaires conforming to IS 10322.",
            "procuring_authority": "Public Works Department",
            "publication_date": "2026-01-10",
            "corrigendum_number": 1,
            "clauses": [
                {
                    "clause_number": "Clause 4.1",
                    "text": "Luminaires shall have IP66 protection.",
                }
            ],
        }
        url = "http://eprocure.gov.in/tender/2026_DEPT_123456_1"

        evidence_list = adapter.parse_tender_data(payload, source_url=url)

        assert len(evidence_list) == 2
        ev1 = evidence_list[0]
        assert ev1.source_type == EvidenceSourceType.CPPP_TENDER
        assert ev1.tender_id == "2026_DEPT_123456_1"
        assert ev1.corrigendum_number == 1
        assert ev1.authority == "Public Works Department"
        assert ev1.url == url
        assert "Supply of LED streetlight" in ev1.excerpt

        ev2 = evidence_list[1]
        assert ev2.section == "Clause 4.1"
        assert "IP66" in ev2.excerpt

    def test_parse_tender_missing_required_fields_raises(self, adapter: CpppAdapter):
        with pytest.raises(SourceAdapterError) as exc_info:
            adapter.parse_tender_data({"procuring_authority": "PWD"})
        assert exc_info.value.code == "MISSING_REQUIRED_FIELDS"


# ===========================================================================
# 5. QcoAdapter Tests
# ===========================================================================

class TestQcoAdapter:

    @pytest.fixture
    def adapter(self) -> QcoAdapter:
        return QcoAdapter()

    def test_parse_qco_data_full(self, adapter: QcoAdapter):
        payload = {
            "gazette_so_number": "S.O. 219(E)",
            "is_number": "IS 10322",
            "issuing_ministry": "DPIIT",
            "effective_date": "2024-06-01",
            "certification_scheme": "isi_mark",
            "mandate_text": "Mandatory BIS certification required for all luminaires under IS 10322.",
        }
        url = "http://egazette.gov.in/so219e.pdf"

        qco_meta, evidence_list = adapter.parse_qco_data(payload, source_url=url)

        assert qco_meta["gazette_so_number"] == "S.O. 219(E)"
        assert qco_meta["is_number"] == "IS 10322"
        assert qco_meta["issuing_ministry"] == "DPIIT"
        assert qco_meta["certification_scheme"] == CertificationScheme.ISI_MARK
        assert qco_meta["qco_notified"] is True

        assert len(evidence_list) == 1
        ev = evidence_list[0]
        assert ev.source_type == EvidenceSourceType.QCO_NOTIFICATION
        assert ev.authority == "DPIIT"
        assert ev.gazette_so_number == "S.O. 219(E)"
        assert ev.url == url

    def test_parse_qco_missing_required_fields_raises(self, adapter: QcoAdapter):
        with pytest.raises(SourceAdapterError) as exc_info:
            adapter.parse_qco_data({"issuing_ministry": "MeitY"})
        assert exc_info.value.code == "MISSING_REQUIRED_FIELDS"
