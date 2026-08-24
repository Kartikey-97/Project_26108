"""
kshiraj/ingestion/tests/test_pagination.py

Unit tests for PaginationHandler.
"""

from __future__ import annotations

import pytest

from kshiraj.ingestion.pagination import PaginationHandler


class TestPaginationHandler:

    def test_extract_rel_next_link(self):
        html = """
        <html>
        <body>
            <div class="pagination">
                <a href="/standards?page=1">1</a>
                <a href="/standards?page=2" rel="next">Next &raquo;</a>
            </div>
        </body>
        </html>
        """
        handler = PaginationHandler()
        links = handler.extract_pagination_links(html, "https://services.bis.gov.in/standards?page=1")

        assert len(links) >= 1
        assert any("page=2" in l for l in links)

    def test_construct_next_page_url(self):
        handler = PaginationHandler(max_pages_per_section=10)

        # Existing param
        url1 = "https://eprocure.gov.in/tenders?category=civil&page=1"
        next_url1 = handler.construct_next_page_url(url1, current_page=1)
        assert next_url1 == "https://eprocure.gov.in/tenders?category=civil&page=2"

        # Exceed max pages cutoff
        exceeded = handler.construct_next_page_url(url1, current_page=10)
        assert exceeded is None
