"""
kshiraj/ingestion/attachment_discovery.py

Scans HTML documents, tables, and portal pages for downloadable government attachments.
Detects:
  - Direct links to PDF, DOC, DOCX, XLS, XLSX, CSV, JSON, XML
  - Embedded viewer elements (iframe, object, embed)
  - Download buttons with contextual metadata (table rows, headers, anchor descriptions)
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from shared.utils import get_logger
from kshiraj.ingestion.frontier import classify_link, normalize_url
from kshiraj.ingestion.models import DiscoveredLink, LinkType

logger = get_logger(__name__)

_ATTACHMENT_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".csv": "text/csv",
    ".json": "application/json",
    ".xml": "application/xml",
}


class AttachmentDiscovery:
    """
    Finds and extracts document attachments from HTML structures.
    """

    def discover_attachments(
        self,
        html_content: str,
        base_url: str,
        depth: int = 0,
    ) -> List[DiscoveredLink]:
        """
        Scan HTML content and return all discovered downloadable document links with context.
        """
        if not html_content or not html_content.strip():
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        discovered: List[DiscoveredLink] = []
        seen_urls: Set[str] = set()

        # 1. Inspect standard <a> anchor tags
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href", "").strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            canonical = normalize_url(href, base_url=base_url)
            if not canonical or canonical in seen_urls:
                continue

            link_type, mime_hint = classify_link(canonical)

            # Also check if anchor text or class mentions download/document
            anchor_text = a_tag.get_text(separator=" ", strip=True)
            classes = " ".join(a_tag.get("class", []))
            title_attr = a_tag.get("title", "")

            is_doc_candidate = link_type == LinkType.DOCUMENT or any(
                ext in href.lower() for ext in _ATTACHMENT_MIME_TYPES.keys()
            )

            if not is_doc_candidate:
                # Check for download indicators
                if any(kw in anchor_text.lower() for kw in ("download", "view document", "view pdf", "gazette pdf", "tender document")):
                    is_doc_candidate = True
                    mime_hint = "application/pdf"

            if is_doc_candidate:
                # Extract surrounding table row context if inside a table
                context_meta = self._extract_table_context(a_tag)
                if title_attr and "title" not in context_meta:
                    context_meta["title"] = title_attr

                discovered.append(
                    DiscoveredLink(
                        url=href,
                        canonical_url=canonical,
                        anchor_text=anchor_text or title_attr,
                        link_type=LinkType.DOCUMENT,
                        parent_url=base_url,
                        depth=depth,
                        mime_type_hint=mime_hint or "application/octet-stream",
                        attributes=context_meta,
                    )
                )
                seen_urls.add(canonical)

        # 2. Inspect <iframe>, <embed>, <object> tags embedding PDFs
        for elem in soup.find_all(["iframe", "embed", "object"]):
            src = elem.get("src") or elem.get("data")
            if src:
                canonical = normalize_url(src, base_url=base_url)
                if canonical and canonical not in seen_urls:
                    if any(ext in canonical.lower() for ext in _ATTACHMENT_MIME_TYPES.keys()):
                        discovered.append(
                            DiscoveredLink(
                                url=src,
                                canonical_url=canonical,
                                anchor_text="Embedded Document",
                                link_type=LinkType.ATTACHMENT,
                                parent_url=base_url,
                                depth=depth,
                                mime_type_hint="application/pdf",
                                attributes={"embedded_tag": elem.name},
                            )
                        )
                        seen_urls.add(canonical)

        return discovered

    def _extract_table_context(self, tag) -> Dict[str, str]:
        """Extract column headers and adjacent cell values if tag is within a table row."""
        meta: Dict[str, str] = {}
        tr = tag.find_parent("tr")
        if not tr:
            return meta

        table = tr.find_parent("table")
        headers: List[str] = []
        if table:
            th_cells = table.find_all("th")
            headers = [th.get_text(strip=True) for th in th_cells]

        td_cells = tr.find_all(["td", "th"])
        cell_texts = [td.get_text(separator=" ", strip=True) for td in td_cells]

        if headers and len(headers) == len(cell_texts):
            for h, val in zip(headers, cell_texts):
                if h and val:
                    meta[f"col_{h}"] = val
        elif cell_texts:
            meta["row_text"] = " | ".join(cell_texts)

        return meta
