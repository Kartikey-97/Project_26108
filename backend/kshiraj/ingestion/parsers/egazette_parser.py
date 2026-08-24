"""
kshiraj/ingestion/parsers/egazette_parser.py

Portal parser for Gazette of India notifications (egazette.gov.in).
Extracts Gazette ID, ministry/department, subject matter, publication date, and notification types.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from shared.utils import get_logger
from kshiraj.ingestion.models import RawDocument
from kshiraj.ingestion.parsers.base_parser import BasePortalParser

logger = get_logger(__name__)

_GAZETTE_ID_PATTERN = re.compile(r"\b(CG\-[A-Z]{2}\-[EW]\-[0-9]{8}\-[0-9]+)\b")
_IS_PATTERN = re.compile(r"\bIS\s*([0-9]{2,6})\b", re.IGNORECASE)
_DATE_PATTERN = re.compile(r"\b([0-9]{1,2}\-[A-Za-z]{3}\-[12][0-9]{3}|[0-9]{4}\-[0-9]{2}\-[0-9]{2})\b")


class EgazettePortalParser(BasePortalParser):
    """
    Parses eGazette notification tables, HTML detail views, and gazette PDFs.
    """

    def can_handle(self, raw_doc: RawDocument) -> bool:
        domain = raw_doc.canonical_url.lower()
        return "egazette.gov.in" in domain or "gazette" in raw_doc.source_name.lower() or "Gazette of India" in raw_doc.text_content

    def parse_document(self, raw_doc: RawDocument) -> Dict[str, Any]:
        """Extract structured Gazette dictionary payload."""
        if raw_doc.raw_payload:
            payload = dict(raw_doc.raw_payload)
            payload.setdefault("source_url", raw_doc.source_url)
            return payload

        # Check structured HTML tables first
        if raw_doc.metadata.tables:
            for table in raw_doc.metadata.tables:
                for row in table:
                    gazette_id = None
                    ministry = None
                    subject = None
                    pub_date = None

                    for k, v in row.items():
                        v_str = str(v).strip()
                        if _GAZETTE_ID_PATTERN.search(v_str):
                            gazette_id = _GAZETTE_ID_PATTERN.search(v_str).group(1)
                        elif "ministry" in k.lower() or "ministry" in v_str.lower():
                            ministry = v_str
                        elif "subject" in k.lower() or "for publication" in v_str.lower():
                            subject = v_str
                        elif "date" in k.lower() or _DATE_PATTERN.search(v_str):
                            pub_date = v_str

                    if gazette_id:
                        is_match = _IS_PATTERN.search(str(subject or "") + " " + raw_doc.text_content)
                        return {
                            "gazette_so_number": gazette_id,
                            "is_number": f"IS {is_match.group(1)}" if is_match else "Statutory Gazette",
                            "title": subject or f"Gazette Notification {gazette_id}",
                            "issuing_ministry": ministry or "Government of India",
                            "effective_date": pub_date,
                            "excerpt": f"Gazette {gazette_id} ({ministry or 'Govt of India'}): {subject or raw_doc.text_content[:500]}",
                            "source_url": raw_doc.source_url,
                        }

        # Fallback to text parsing
        title = raw_doc.metadata.title or "Gazette of India Notification"
        text = raw_doc.text_content or ""

        gazette_id = "Gazette Notification"
        g_match = _GAZETTE_ID_PATTERN.search(title + " " + text[:1000])
        if g_match:
            gazette_id = g_match.group(1)

        is_match = _IS_PATTERN.search(text)

        return {
            "gazette_so_number": gazette_id,
            "is_number": f"IS {is_match.group(1)}" if is_match else "Mandatory Notification",
            "title": title,
            "issuing_ministry": "Directorate of Printing / Ministry of Housing & Urban Affairs",
            "effective_date": None,
            "excerpt": text[:1500] if text else title,
            "source_url": raw_doc.source_url,
        }
