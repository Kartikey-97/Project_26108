"""
kshiraj/ingestion/parsers/base_parser.py

Base interface for portal-specific HTML/PDF/JSON extractors.
Transforms raw government documents into structured payloads ready for domain adapters.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from kshiraj.ingestion.models import RawDocument


class BasePortalParser:
    """Abstract interface for portal-specific parsing logic."""

    def can_handle(self, raw_doc: RawDocument) -> bool:
        """Evaluate if this parser is appropriate for the given RawDocument."""
        raise NotImplementedError

    def parse_document(self, raw_doc: RawDocument) -> Dict[str, Any]:
        """Extract domain-specific dictionary payload from the raw document."""
        raise NotImplementedError
