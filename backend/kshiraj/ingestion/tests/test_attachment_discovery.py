"""
kshiraj/ingestion/tests/test_attachment_discovery.py

Unit tests for AttachmentDiscovery from HTML portals and tables.
"""

from __future__ import annotations

import pytest

from kshiraj.ingestion.attachment_discovery import AttachmentDiscovery
from kshiraj.ingestion.models import LinkType


class TestAttachmentDiscovery:

    def test_discover_pdf_and_doc_links(self):
        html = """
        <html>
        <body>
            <h2>Tender Documents</h2>
            <table>
                <tr>
                    <th>Doc No</th>
                    <th>Description</th>
                    <th>Download</th>
                </tr>
                <tr>
                    <td>NIT-01</td>
                    <td>Technical Specifications</td>
                    <td><a href="/downloads/specs.pdf">Download PDF</a></td>
                </tr>
                <tr>
                    <td>BOQ-01</td>
                    <td>Bill of Quantities</td>
                    <td><a href="/downloads/boq.xlsx">Download BOQ</a></td>
                </tr>
            </table>
            <div>
                <iframe src="/preview/tender_notice.pdf"></iframe>
            </div>
        </body>
        </html>
        """
        discovery = AttachmentDiscovery()
        links = discovery.discover_attachments(html, base_url="https://eprocure.gov.in/tenders/101")

        assert len(links) == 3
        canonical_urls = [l.canonical_url for l in links]

        assert "https://eprocure.gov.in/downloads/specs.pdf" in canonical_urls
        assert "https://eprocure.gov.in/downloads/boq.xlsx" in canonical_urls
        assert "https://eprocure.gov.in/preview/tender_notice.pdf" in canonical_urls

        # Verify table context extraction
        pdf_link = next(l for l in links if "specs.pdf" in l.url)
        assert pdf_link.attributes.get("col_doc_no") == "NIT-01" or "NIT-01" in str(pdf_link.attributes)
