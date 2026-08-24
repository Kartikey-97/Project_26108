"""
kshiraj/ingestion/parsers/dpiit_parser.py

Portal parser for DPIIT Quality Control Orders (QCO) and statutory ministry notifications.
Extracts QCO order title, gazette S.O. number, notified IS standards, and implementation dates.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from shared.utils import get_logger
from kshiraj.ingestion.models import RawDocument
from kshiraj.ingestion.parsers.base_parser import BasePortalParser

logger = get_logger(__name__)

_SO_PATTERN = re.compile(r"S\.?\s*O\.?\s*([0-9]+)\s*(?:\(([A-Za-z0-9]+)\))?", re.IGNORECASE)
_IS_PATTERN = re.compile(r"\bIS\s*([0-9]{2,6}(?:\s*[\:\-\/]\s*Part\s*[0-9]+)?(?:\s*[\:\-]?\s*[12][0-9]{3})?)\b", re.IGNORECASE)
_DATE_PATTERN = re.compile(r"\b([0-9]{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+[12][0-9]{3}|[0-9]{4}-[0-9]{2}-[0-9]{2})\b", re.IGNORECASE)


class DpiitPortalParser(BasePortalParser):
    """
    Extracts structured QCO notifications from DPIIT and ministry statutory orders.
    """

    def can_handle(self, raw_doc: RawDocument) -> bool:
        domain = raw_doc.canonical_url.lower()
        return "dpiit.gov.in" in domain or "qco" in raw_doc.source_name.lower() or "Quality Control Order" in raw_doc.text_content

    def parse_document(self, raw_doc: RawDocument) -> Dict[str, Any]:
        """Extract structured QCO dictionary payload."""
        if raw_doc.raw_payload:
            payload = dict(raw_doc.raw_payload)
            payload.setdefault("source_url", raw_doc.source_url)
            return payload

        title = raw_doc.metadata.title or "Quality Control Order"
        text = raw_doc.text_content or ""

        # Extract S.O. Number
        so_number = "S.O. Notification"
        so_match = _SO_PATTERN.search(text)
        if so_match:
            sec_suffix = f"({so_match.group(2).upper()})" if so_match.group(2) else ""
            so_number = f"S.O. {so_match.group(1)}{sec_suffix}"

        # Extract Notified IS Standard
        is_num = "Mandatory Standard"
        is_match = _IS_PATTERN.search(text)
        if is_match:
            is_num = f"IS {is_match.group(1).strip()}"

        # Extract Issuing Ministry
        ministry = "Ministry of Commerce and Industry / DPIIT"
        if "Ministry of Steel" in text:
            ministry = "Ministry of Steel"
        elif "Ministry of Heavy Industries" in text:
            ministry = "Ministry of Heavy Industries"
        elif "Ministry of Electronics" in text or "MeitY" in text:
            ministry = "Ministry of Electronics and Information Technology"
        elif "Ministry of Chemicals" in text:
            ministry = "Ministry of Chemicals and Fertilizers"

        # Effective Date
        effective_date = None
        date_match = _DATE_PATTERN.search(text)
        if date_match:
            effective_date = date_match.group(1)

        return {
            "gazette_so_number": so_number,
            "is_number": is_num,
            "title": title,
            "issuing_ministry": ministry,
            "effective_date": effective_date,
            "excerpt": text[:2000] if text else title,
            "source_url": raw_doc.source_url,
        }
