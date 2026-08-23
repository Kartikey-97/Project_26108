"""
kshiraj/ingestion/json_extractor.py

JSON and structured API payload extractor for government data endpoints.
Handles dictionary normalization, stringification for search, and provenance tracking.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Union

from shared.models import EvidenceSourceType
from shared.utils import get_logger, utcnow
from kshiraj.ingestion.frontier import normalize_url
from kshiraj.ingestion.models import ExtractionStatus, PageMetadata, RawDocument

logger = get_logger(__name__)


class JsonExtractor:
    """
    Extracts structured data from JSON responses, REST APIs, and serialized metadata.
    """

    def extract_document(
        self,
        json_data: Union[str, bytes, Dict[str, Any], List[Any]],
        source_url: str,
        source_name: str = "Government JSON Endpoint",
        source_type: EvidenceSourceType = EvidenceSourceType.OTHER_GOVERNMENT,
        content_hash: str = "",
    ) -> RawDocument:
        """
        Parse JSON content into a normalized RawDocument.
        """
        parsed_payload: Optional[Dict[str, Any]] = None
        raw_bytes: bytes = b""

        if isinstance(json_data, (dict, list)):
            try:
                raw_bytes = json.dumps(json_data, sort_keys=True, default=str).encode("utf-8")
                parsed_payload = json_data if isinstance(json_data, dict) else {"items": json_data}
            except Exception as exc:
                logger.error("Error serializing JSON object: %s", exc)
        elif isinstance(json_data, bytes):
            raw_bytes = json_data
            try:
                parsed = json.loads(json_data.decode("utf-8", errors="replace"))
                parsed_payload = parsed if isinstance(parsed, dict) else {"items": parsed}
            except Exception as exc:
                logger.error("Malformed JSON bytes for %s: %s", source_url, exc)
        elif isinstance(json_data, str):
            raw_bytes = json_data.encode("utf-8")
            try:
                parsed = json.loads(json_data)
                parsed_payload = parsed if isinstance(parsed, dict) else {"items": parsed}
            except Exception as exc:
                logger.error("Malformed JSON string for %s: %s", source_url, exc)

        if not content_hash and raw_bytes:
            content_hash = hashlib.sha256(raw_bytes).hexdigest()

        if parsed_payload is None:
            return RawDocument(
                source_url=source_url,
                canonical_url=normalize_url(source_url),
                source_name=source_name,
                source_type=source_type,
                mime_type="application/json",
                content_hash=content_hash,
                text_content="",
                raw_payload=None,
                extraction_status=ExtractionStatus.MALFORMED,
                retrieved_at=utcnow(),
            )

        # Convert dictionary to formatted human-readable text for indexing/retrieval
        text_representation = json.dumps(parsed_payload, indent=2, default=str)

        # Extract basic metadata hints if available
        title = parsed_payload.get("title") or parsed_payload.get("name") or parsed_payload.get("is_number")
        desc = parsed_payload.get("description") or parsed_payload.get("scope")

        page_meta = PageMetadata(
            title=str(title) if title else None,
            description=str(desc) if desc else None,
            custom_metadata=parsed_payload,
        )

        return RawDocument(
            source_url=source_url,
            canonical_url=normalize_url(source_url),
            source_name=source_name,
            source_type=source_type,
            mime_type="application/json",
            content_hash=content_hash,
            content_length=len(raw_bytes),
            text_content=text_representation,
            page_texts={1: text_representation},
            page_count=1,
            metadata=page_meta,
            raw_payload=parsed_payload,
            extraction_status=ExtractionStatus.SUCCESS,
            retrieved_at=utcnow(),
        )
