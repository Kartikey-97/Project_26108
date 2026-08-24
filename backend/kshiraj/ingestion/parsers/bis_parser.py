"""
kshiraj/ingestion/parsers/bis_parser.py

Portal-specific parser for Bureau of Indian Standards (BIS) documents, catalog tables, and web pages.
Extracts standard metadata, designation, title, year, committee, status, and scope
without unauthorized full-text copying of restricted standards documents.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from shared.utils import get_logger
from kshiraj.ingestion.models import RawDocument
from kshiraj.ingestion.parsers.base_parser import BasePortalParser

logger = get_logger(__name__)

# Regex for standard designations: e.g. "IS 10322 : Part 5 : Sec 3 : 2014" or "IS 732:2019"
_IS_PATTERN = re.compile(r"\bIS\s*([0-9]{2,6})(?:\s*[\:\-\/]\s*Part\s*([0-9]+))?(?:\s*[\:\-\/]\s*Sec\s*([0-9]+))?(?:\s*[\:\-]?\s*([12][0-9]{3}))?\b", re.IGNORECASE)
_DRAFT_PATTERN = re.compile(r"\b(?:DRAFT|DOC|WC)\s*[:\-]?\s*([A-Za-z0-9\/\-_]+)\b", re.IGNORECASE)
_COMMITTEE_PATTERN = re.compile(r"\b([A-Z]{2,4}\s*[0-9]{1,3})\b")
_DIVISION_KEYWORDS = {
    "CED": "Civil Engineering Division",
    "ETD": "Electrotechnical Division",
    "MED": "Mechanical Engineering Division",
    "CHD": "Chemical Division",
    "TXD": "Textile Division",
    "FAD": "Food and Agriculture Division",
    "LITD": "Electronics and Information Technology Division",
    "MHD": "Medical Equipment and Hospital Planning Division",
}


class BisPortalParser(BasePortalParser):
    """
    Parses BIS portal pages, tables, and document metadata into structured BIS dictionaries.
    """

    def can_handle(self, raw_doc: RawDocument) -> bool:
        domain = raw_doc.canonical_url.lower()
        return "bis.gov.in" in domain or "bis" in raw_doc.source_name.lower() or "IS " in raw_doc.text_content

    def parse_document(self, raw_doc: RawDocument) -> Dict[str, Any]:
        """Extract structured BIS standard dictionary."""
        # 1. If structured payload already present, return with source_url
        if raw_doc.raw_payload:
            payload = dict(raw_doc.raw_payload)
            payload.setdefault("source_url", raw_doc.source_url)
            return payload

        # 2. Check structured tables from HTML
        if raw_doc.metadata.tables:
            for table in raw_doc.metadata.tables:
                for row in table:
                    # Look for standard number column
                    for k, v in row.items():
                        if any(term in k for term in ("standard", "is_number", "doc_no", "number")):
                            is_match = _IS_PATTERN.search(str(v))
                            if is_match:
                                title = row.get("title") or row.get("col_title") or row.get("description") or raw_doc.metadata.title or "Indian Standard"
                                year_str = row.get("year") or row.get("col_year")
                                year = int(year_str) if year_str and year_str.isdigit() else None
                                status = row.get("status") or row.get("col_status") or "active"

                                return {
                                    "is_number": f"IS {is_match.group(1)}",
                                    "part": int(is_match.group(2)) if is_match.group(2) else None,
                                    "section": int(is_match.group(3)) if is_match.group(3) else None,
                                    "year": year or (int(is_match.group(4)) if is_match.group(4) else None),
                                    "title": str(title),
                                    "status": str(status),
                                    "scope": raw_doc.text_content[:1000] if raw_doc.text_content else str(title),
                                    "source_url": raw_doc.source_url,
                                }

        # 3. Fallback: Parse unstructured text and metadata
        title = raw_doc.metadata.title or "Indian Standard"
        text = raw_doc.text_content or ""

        # Search for IS Number
        is_num = "IS Unknown"
        part = None
        section = None
        year = None

        best_match = None
        for m_cand in _IS_PATTERN.finditer(text[:2000] + " " + title):
            if best_match is None:
                best_match = m_cand
            elif m_cand.group(4) and not best_match.group(4):
                best_match = m_cand

        if best_match:
            is_num = f"IS {best_match.group(1)}"
            if best_match.group(2):
                part = int(best_match.group(2))
            if best_match.group(3):
                section = int(best_match.group(3))
            if best_match.group(4):
                year = int(best_match.group(4))

        if year is None:
            # Look for 4-digit year near standard mention
            y_match = re.search(r"\b(19[5-9][0-9]|20[0-3][0-9])\b", text[:1000])
            if y_match:
                year = int(y_match.group(1))

        # Check for status
        status = "active"
        lower_text = text.lower()
        if "superseded by" in lower_text or "withdrawn" in lower_text:
            status = "superseded"
        elif "under revision" in lower_text or "wide circulation" in lower_text:
            status = "under_revision"
        elif "reaffirmed" in lower_text:
            status = "reaffirmed"

        # Committee & Division detection
        committee = None
        division = None
        c_match = _COMMITTEE_PATTERN.search(text[:1000])
        if c_match:
            committee = c_match.group(1)
            prefix = committee.split()[0]
            if prefix in _DIVISION_KEYWORDS:
                division = _DIVISION_KEYWORDS[prefix]

        return {
            "is_number": is_num,
            "part": part,
            "section": section,
            "year": year,
            "title": title,
            "status": status,
            "scope": text[:1500] if text else title,
            "technical_committee": committee,
            "division_council": division,
            "source_url": raw_doc.source_url,
        }

    def extract_multiple_standards(self, raw_doc: RawDocument) -> List[Dict[str, Any]]:
        """
        Extract multiple distinct BIS standards from a compendium, table, or multi-standard document.
        """
        results: List[Dict[str, Any]] = []
        seen_numbers: set = set()

        # 1. Check structured tables from HTML
        if raw_doc.metadata.tables:
            for table in raw_doc.metadata.tables:
                for row in table:
                    for k, v in row.items():
                        if any(term in k for term in ("standard", "is_number", "doc_no", "number", "sector")):
                            is_match = _IS_PATTERN.search(str(v))
                            if is_match:
                                is_num = f"IS {is_match.group(1)}"
                                if is_num not in seen_numbers:
                                    seen_numbers.add(is_num)
                                    title = row.get("title") or row.get("col_title") or row.get("description") or raw_doc.metadata.title or "Indian Standard"
                                    year_str = row.get("year") or row.get("col_year")
                                    year = int(year_str) if year_str and year_str.isdigit() else (int(is_match.group(4)) if is_match.group(4) else None)
                                    results.append({
                                        "is_number": is_num,
                                        "part": int(is_match.group(2)) if is_match.group(2) else None,
                                        "section": int(is_match.group(3)) if is_match.group(3) else None,
                                        "year": year,
                                        "title": str(title),
                                        "status": row.get("status", "active"),
                                        "scope": raw_doc.text_content[:500],
                                        "source_url": raw_doc.source_url,
                                    })

        # 2. Parse text lines containing standard designations
        text = raw_doc.text_content or ""
        lines = text.splitlines()
        standards_by_num: Dict[str, Dict[str, Any]] = {}

        # Add any initial results from tables into standards_by_num
        for res in results:
            standards_by_num[res["is_number"]] = res

        for i, line in enumerate(lines):
            for m in _IS_PATTERN.finditer(line):
                is_num = f"IS {m.group(1)}"
                if len(is_num) < 4:
                    continue

                line_clean = line.strip()
                title_cand = line_clean
                if len(title_cand) < 25 and i + 1 < len(lines):
                    title_cand = f"{line_clean} - {lines[i+1].strip()}"

                year = int(m.group(4)) if m.group(4) else None
                if not year:
                    y_m = re.search(r"\b(19[5-9][0-9]|20[0-3][0-9])\b", line)
                    if y_m:
                        year = int(y_m.group(1))

                # Committee & Division detection
                comm = None
                div = None
                c_match = _COMMITTEE_PATTERN.search(line)
                if c_match:
                    comm = c_match.group(1)
                    prefix = comm.split()[0]
                    if prefix in _DIVISION_KEYWORDS:
                        div = _DIVISION_KEYWORDS[prefix]

                if is_num not in standards_by_num:
                    standards_by_num[is_num] = {
                        "is_number": is_num,
                        "part": int(m.group(2)) if m.group(2) else None,
                        "section": int(m.group(3)) if m.group(3) else None,
                        "year": year,
                        "title": title_cand[:120],
                        "status": "active",
                        "scope": "\n".join(lines[max(0, i-1):min(len(lines), i+4)]),
                        "technical_committee": comm,
                        "division_council": div,
                        "source_url": raw_doc.source_url,
                    }
                else:
                    # Enrich existing record
                    curr = standards_by_num[is_num]
                    if year and not curr.get("year"):
                        curr["year"] = year
                    if comm and not curr.get("technical_committee"):
                        curr["technical_committee"] = comm
                        curr["division_council"] = div
                    if len(title_cand) > len(curr.get("title", "")):
                        curr["title"] = title_cand[:120]

        # Global committee detection fallback
        c_global = _COMMITTEE_PATTERN.search(text[:2000])
        if c_global:
            comm_g = c_global.group(1)
            div_g = _DIVISION_KEYWORDS.get(comm_g.split()[0])
            for st in standards_by_num.values():
                if not st.get("technical_committee"):
                    st["technical_committee"] = comm_g
                    st["division_council"] = div_g

        final_list = list(standards_by_num.values())
        if not final_list:
            final_list.append(self.parse_document(raw_doc))

        return final_list
