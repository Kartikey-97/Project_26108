"""
kshiraj/ingestion/html_extractor.py

HTML document extractor for parsing government portal content, structured tables,
and metadata while preserving provenance and attribution.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment

from shared.models import EvidenceSourceType
from shared.utils import get_logger, utcnow
from kshiraj.ingestion.frontier import normalize_url
from kshiraj.ingestion.models import ExtractionStatus, PageMetadata, RawDocument

logger = get_logger(__name__)


class HtmlExtractor:
    """
    Extracts structured data, tables, metadata, and clean text from HTML content.
    """

    def extract_document(
        self,
        html_content: str,
        source_url: str,
        source_name: str = "Government Portal",
        source_type: EvidenceSourceType = EvidenceSourceType.OTHER_GOVERNMENT,
        content_hash: str = "",
    ) -> RawDocument:
        """
        Parse HTML content and construct a fully populated RawDocument.
        """
        if not html_content or not html_content.strip():
            return RawDocument(
                source_url=source_url,
                canonical_url=normalize_url(source_url),
                source_name=source_name,
                source_type=source_type,
                mime_type="text/html",
                content_hash=content_hash,
                text_content="",
                extraction_status=ExtractionStatus.EMPTY,
                retrieved_at=utcnow(),
            )

        soup = BeautifulSoup(html_content, "html.parser")

        # Strip scripts, styles, comments, and navigation chrome
        for element in soup(["script", "style", "noscript", "svg", "header", "footer"]):
            element.decompose()

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        metadata = self._extract_metadata(soup)
        tables = self._extract_tables(soup)
        metadata.tables = tables

        # Clean text
        text_content = soup.get_text(separator="\n", strip=True)
        # Collapse multiple blank lines
        text_content = re.sub(r"\n{3,}", "\n\n", text_content)

        return RawDocument(
            source_url=source_url,
            canonical_url=normalize_url(source_url),
            source_name=source_name,
            source_type=source_type,
            mime_type="text/html",
            content_hash=content_hash,
            content_length=len(html_content.encode("utf-8")),
            text_content=text_content,
            page_texts={1: text_content},
            page_count=1,
            metadata=metadata,
            extraction_status=ExtractionStatus.SUCCESS if text_content else ExtractionStatus.EMPTY,
            retrieved_at=utcnow(),
        )

    def _extract_metadata(self, soup: BeautifulSoup) -> PageMetadata:
        """Extract metadata tags, JSON-LD, headings, and title."""
        title = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        meta_desc = None
        desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)}) or \
                   soup.find("meta", attrs={"property": "og:description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        keywords: List[str] = []
        kw_tag = soup.find("meta", attrs={"name": re.compile(r"keywords", re.I)})
        if kw_tag and kw_tag.get("content"):
            keywords = [k.strip() for k in kw_tag["content"].split(",") if k.strip()]

        headings: Dict[str, List[str]] = {"h1": [], "h2": [], "h3": []}
        for level in ("h1", "h2", "h3"):
            for h in soup.find_all(level):
                h_text = h.get_text(strip=True)
                if h_text:
                    headings[level].append(h_text)

        # JSON-LD extraction
        json_ld_list: List[Dict[str, Any]] = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                if script.string:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        json_ld_list.append(data)
                    elif isinstance(data, list):
                        json_ld_list.extend(d for d in data if isinstance(d, dict))
            except Exception:
                pass

        return PageMetadata(
            title=title,
            description=meta_desc,
            keywords=keywords,
            headings=headings,
            json_ld=json_ld_list,
        )

    def _extract_tables(self, soup: BeautifulSoup) -> List[List[Dict[str, Any]]]:
        """
        Extract structured HTML tables into list of row dictionaries.
        """
        extracted_tables: List[List[Dict[str, Any]]] = []

        for table in soup.find_all("table"):
            tbody = table.find("tbody")
            thead = table.find("thead")

            headers: List[str] = []
            if thead:
                th_cells = thead.find_all(["th", "td"])
                headers = [th.get_text(strip=True) for th in th_cells]

            if tbody:
                data_rows = tbody.find_all("tr")
            elif thead:
                data_rows = [tr for tr in table.find_all("tr") if tr not in thead.find_all("tr")]
            else:
                all_tr = table.find_all("tr")
                if not all_tr:
                    continue
                first_row = all_tr[0]
                th_cells = first_row.find_all(["th", "td"])
                headers = [th.get_text(strip=True) for th in th_cells]
                data_rows = all_tr[1:]

            if not data_rows:
                continue

            # Clean header keys
            cleaned_headers = [
                re.sub(r"[^\w\s]", "", h).strip().lower().replace(" ", "_") or f"col_{i}"
                for i, h in enumerate(headers)
            ]

            table_data: List[Dict[str, Any]] = []
            for tr in data_rows:
                cells = tr.find_all(["td", "th"])
                if not cells:
                    continue
                row_dict: Dict[str, Any] = {}
                for idx, cell in enumerate(cells):
                    col_name = cleaned_headers[idx] if idx < len(cleaned_headers) else f"col_{idx}"
                    cell_text = cell.get_text(separator=" ", strip=True)
                    # Check for anchor href
                    a_link = cell.find("a", href=True)
                    if a_link:
                        row_dict[f"{col_name}_link"] = a_link["href"]
                    row_dict[col_name] = cell_text
                if row_dict:
                    table_data.append(row_dict)

            if table_data:
                extracted_tables.append(table_data)

        return extracted_tables
