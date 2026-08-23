"""
kshiraj/ingestion/pagination.py

Multi-page pagination discovery and traversal logic for government portals and tables.
Detects:
  - Query-parameter increments (e.g. ?page=2, ?pageNo=2, ?offset=20)
  - Next-link HTML anchors (rel="next", "Next >", "»", "अगला")
  - Numbered pagination controls
"""

from __future__ import annotations

import re
from typing import List, Optional, Set
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

from shared.utils import get_logger
from kshiraj.ingestion.frontier import normalize_url

logger = get_logger(__name__)

# Text patterns indicating a "next page" button/link
_NEXT_PAGE_TEXT_PATTERNS = [
    r"^next\b",
    r"^next\s*>",
    r"^next\s*»",
    r"^»$",
    r"^>$",
    r"अगला",
    r"आगे",
    r"next\s*page",
]

_PAGE_PARAM_NAMES = ["page", "pageno", "page_no", "p", "page_number", "pagenum", "start", "offset"]


class PaginationHandler:
    """
    Identifies and resolves multi-page pagination links from HTML and URL structures.
    """

    def __init__(self, max_pages_per_section: int = 50) -> None:
        self.max_pages_per_section = max_pages_per_section

    def extract_pagination_links(self, html_content: str, current_url: str) -> List[str]:
        """
        Extract candidate pagination links from HTML DOM.
        """
        if not html_content or not html_content.strip():
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        discovered: List[str] = []
        seen: Set[str] = set()

        # 1. Explicit rel="next" tag
        for a_tag in soup.find_all("a", rel=lambda r: r and "next" in r.lower() if r else False):
            href = a_tag.get("href")
            if href:
                full_url = normalize_url(href, base_url=current_url)
                if full_url and full_url not in seen:
                    seen.add(full_url)
                    discovered.append(full_url)

        # 2. Text-based "Next" anchors
        for a_tag in soup.find_all("a", href=True):
            text = (a_tag.get_text() or "").strip().lower()
            if any(re.search(pat, text, re.IGNORECASE) for pat in _NEXT_PAGE_TEXT_PATTERNS):
                href = a_tag.get("href")
                if href and not href.startswith("javascript:void") and not href.startswith("#"):
                    full_url = normalize_url(href, base_url=current_url)
                    if full_url and full_url not in seen:
                        seen.add(full_url)
                        discovered.append(full_url)

        # 3. Dedicated pagination containers (.pagination, .pager, #pagination)
        containers = soup.find_all(
            ["div", "ul", "nav", "section"],
            class_=lambda c: c and any(k in c.lower() for k in ("pagination", "pager", "page-nav", "paging")) if c else False
        )
        for cont in containers:
            for a_tag in cont.find_all("a", href=True):
                href = a_tag.get("href")
                if href and not href.startswith("#") and not href.startswith("javascript:"):
                    full_url = normalize_url(href, base_url=current_url)
                    if full_url and full_url not in seen and full_url != current_url:
                        seen.add(full_url)
                        discovered.append(full_url)

        return discovered

    def construct_next_page_url(self, current_url: str, current_page: int) -> Optional[str]:
        """
        Synthesize the URL for the next page by incrementing or appending a page parameter.
        """
        parsed = urlparse(current_url)
        query_dict = dict(parse_qsl(parsed.query, keep_blank_values=False))

        # Check existing parameter name
        found_param = None
        for p in _PAGE_PARAM_NAMES:
            if p in query_dict:
                found_param = p
                break

        target_page = current_page + 1
        if target_page > self.max_pages_per_section:
            return None

        if found_param:
            query_dict[found_param] = str(target_page)
        else:
            query_dict["page"] = str(target_page)

        sorted_params = sorted(query_dict.items(), key=lambda x: x[0])
        new_query = urlencode(sorted_params)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", new_query, ""))
