"""
kshiraj/ingestion/parsers/cppp_parser.py

Portal parser for Central Public Procurement Portal (CPPP) tenders, notices, and specifications.
Extracts tender ID, organization, technical requirements, closing dates, and referenced standards.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from shared.utils import get_logger
from kshiraj.ingestion.models import RawDocument
from kshiraj.ingestion.parsers.base_parser import BasePortalParser

logger = get_logger(__name__)

_TENDER_ID_PATTERN = re.compile(r"\b(?:Tender\s*(?:Notice\s*No|Reference|Number|Ref|ID|No))\s*[:\-]?\s*([A-Za-z0-9_\-\/]+)\b", re.IGNORECASE)
_IS_PATTERN = re.compile(r"\bIS\s*([0-9]{2,6})\b", re.IGNORECASE)
_CLOSING_DATE_PATTERN = re.compile(r"\b(?:Closing|Submission|Due)\s*Date\s*[:\-]?\s*([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+[12][0-9]{3}|[0-9]{4}-[0-9]{2}-[0-9]{2})\b", re.IGNORECASE)


class CpppPortalParser(BasePortalParser):
    """
    Parses CPPP HTML tables, notice pages, and tender PDFs into structured tender payloads.
    """

    def can_handle(self, raw_doc: RawDocument) -> bool:
        domain = raw_doc.canonical_url.lower()
        return "eprocure.gov.in" in domain or "cppp" in raw_doc.source_name.lower() or "tender" in raw_doc.text_content.lower()

    def parse_document(self, raw_doc: RawDocument) -> Dict[str, Any]:
        """Extract structured CPPP tender payload."""
        if raw_doc.raw_payload:
            payload = dict(raw_doc.raw_payload)
            payload.setdefault("source_url", raw_doc.source_url)
            return payload

        title = raw_doc.metadata.title or "Public Procurement Tender Notice"
        text = raw_doc.text_content or ""

        # Extract Tender ID
        tender_id = "TENDER_NOTICE"
        t_match = _TENDER_ID_PATTERN.search(title + " " + text[:1000])
        if t_match:
            tender_id = t_match.group(1).strip()

        # Extract Authority
        authority = raw_doc.metadata.author or "Central Public Procurement Portal (CPPP)"
        if "CPWD" in text:
            authority = "Central Public Works Department (CPWD)"
        elif "NHAI" in text:
            authority = "National Highways Authority of India (NHAI)"
        elif "Railways" in text:
            authority = "Ministry of Railways"
        elif "MES" in text:
            authority = "Military Engineer Services (MES)"

        # Extract Referenced Standards
        ref_standards = []
        for is_m in _IS_PATTERN.finditer(text):
            std_str = f"IS {is_m.group(1)}"
            if std_str not in ref_standards:
                ref_standards.append(std_str)

        # Extract Closing Date
        closing_date = None
        c_match = _CLOSING_DATE_PATTERN.search(text)
        if c_match:
            closing_date = c_match.group(1)

        # Check for clauses in text
        clauses = []
        for line in text.splitlines():
            line_s = line.strip()
            if any(std in line_s for std in ref_standards) and len(line_s) > 20:
                clauses.append(line_s)

        return {
            "tender_id": tender_id,
            "title": title,
            "procuring_authority": authority,
            "closing_date": closing_date,
            "technical_specification": text if text else title,
            "referenced_standards": ref_standards,
            "clauses": clauses[:10] if clauses else None,
            "source_url": raw_doc.source_url,
        }
