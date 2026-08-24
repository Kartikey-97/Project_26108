"""
kshiraj/ingestion/tests/test_extractors.py

Unit tests for HTML, PDF, and JSON extractors.
"""

from __future__ import annotations

import io
import pytest

from shared.models import EvidenceSourceType
from kshiraj.ingestion.html_extractor import HtmlExtractor
from kshiraj.ingestion.json_extractor import JsonExtractor
from kshiraj.ingestion.models import ExtractionStatus
from kshiraj.ingestion.pdf_extractor import PdfExtractor


class TestHtmlExtractor:

    def test_extract_html_tables_and_metadata(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>BIS Standard IS 10322</title>
            <meta name="description" content="Luminaires specification for general lighting">
            <meta name="keywords" content="BIS, IS 10322, Lighting">
        </head>
        <body>
            <h1>Bureau of Indian Standards</h1>
            <h2>Specification Details</h2>
            <p>Scope: This standard covers luminaires for emergency and general lighting.</p>
            <table>
                <thead>
                    <tr><th>Standard Number</th><th>Title</th><th>Action</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>IS 10322 (Part 5/Sec 3)</td>
                        <td>Luminaires Specification</td>
                        <td><a href="/download/is10322.pdf">Download PDF</a></td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        extractor = HtmlExtractor()
        doc = extractor.extract_document(
            html_content=html,
            source_url="https://services.bis.gov.in/standards/10322",
            source_name="BIS Catalog",
            source_type=EvidenceSourceType.BIS_STANDARD,
        )

        assert doc.extraction_status == ExtractionStatus.SUCCESS
        assert doc.metadata.title == "BIS Standard IS 10322"
        assert doc.metadata.description == "Luminaires specification for general lighting"
        assert "BIS" in doc.metadata.keywords
        assert len(doc.metadata.headings["h1"]) == 1
        assert len(doc.metadata.tables) == 1
        assert doc.metadata.tables[0][0]["standard_number"] == "IS 10322 (Part 5/Sec 3)"
        assert doc.metadata.tables[0][0]["action_link"] == "/download/is10322.pdf"
        assert "Scope: This standard covers luminaires" in doc.text_content

    def test_extract_empty_html(self):
        extractor = HtmlExtractor()
        doc = extractor.extract_document(
            html_content="",
            source_url="https://bis.gov.in/empty",
        )
        assert doc.extraction_status == ExtractionStatus.EMPTY


class TestJsonExtractor:

    def test_extract_valid_json_dict(self):
        payload = {
            "is_number": "IS 269",
            "title": "Ordinary Portland Cement, 33 Grade - Specification",
            "year": 2015,
            "status": "active",
            "division_council": "Civil Engineering",
        }
        extractor = JsonExtractor()
        doc = extractor.extract_document(
            json_data=payload,
            source_url="https://services.bis.gov.in/api/v1/standards/269",
            source_name="BIS API",
        )

        assert doc.extraction_status == ExtractionStatus.SUCCESS
        assert doc.raw_payload == payload
        assert "Ordinary Portland Cement" in doc.text_content
        assert doc.content_hash != ""

    def test_extract_malformed_json_string(self):
        extractor = JsonExtractor()
        doc = extractor.extract_document(
            json_data="{invalid json: true",
            source_url="https://services.bis.gov.in/api/bad",
        )
        assert doc.extraction_status == ExtractionStatus.MALFORMED


class TestPdfExtractor:

    def test_extract_empty_pdf(self):
        extractor = PdfExtractor()
        doc = extractor.extract_document(
            pdf_bytes=b"",
            source_url="https://bis.gov.in/empty.pdf",
        )
        assert doc.extraction_status == ExtractionStatus.EMPTY

    def test_extract_scanned_pdf_flags_ocr_required(self):
        # Mock minimal PDF bytes with no text
        extractor = PdfExtractor()
        doc = extractor.extract_document(
            pdf_bytes=b"%PDF-1.4 dummy non-text binary payload",
            source_url="https://bis.gov.in/scanned_gazette.pdf",
        )
        assert doc.extraction_status in (ExtractionStatus.OCR_REQUIRED, ExtractionStatus.MALFORMED)
