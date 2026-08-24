"""
kshiraj/source_adapters/bis_drafts_adapter.py

Adapter for BIS Wide Circulation Draft standards.

Converts draft standard metadata into `shared.models.Standard` (with status StandardStatus.UNDER_REVISION)
and `shared.models.Evidence` (with source_type EvidenceSourceType.BIS_WIDE_CIRCULATION_DRAFT).
Does not treat draft standards as active or final BIS Indian Standards.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple, Union

from shared.models import (
    DocumentType,
    Evidence,
    EvidenceSourceType,
    Standard,
    StandardStatus,
)
from shared.utils import SourceAdapterError, get_logger, utcnow

from kshiraj.source_adapters.base import BaseSourceAdapter

logger = get_logger(__name__)


class BisDraftsAdapter(BaseSourceAdapter):
    """
    Ingestion adapter for BIS Wide Circulation Draft standards.
    """

    def parse_draft_data(
        self,
        source_data: Union[Dict[str, Any], str],
        source_url: Optional[str] = None,
    ) -> Tuple[Standard, List[Evidence]]:
        """
        Parse raw BIS draft standard payload into Standard and Evidence models.

        Parameters
        ----------
        source_data:
            Dictionary or JSON string representing raw BIS draft payload.
        source_url:
            Optional canonical source URL.

        Returns
        -------
        Tuple[Standard, List[Evidence]]
            Draft Standard representation and attached draft Evidence record.

        Raises
        ------
        SourceAdapterError:
            If payload is malformed or missing key attributes.
        """
        if isinstance(source_data, str):
            try:
                data = json.loads(source_data)
            except Exception as exc:
                raise SourceAdapterError(
                    f"Failed to parse draft JSON payload: {exc}",
                    code="INVALID_PAYLOAD",
                ) from exc
        elif isinstance(source_data, dict):
            data = source_data
        else:
            raise SourceAdapterError(
                f"Invalid draft source_data type: {type(source_data)}. Expected dict or JSON string.",
                code="INVALID_PAYLOAD",
            )

        if not isinstance(data, dict):
            raise SourceAdapterError(
                "Draft source payload must be a dictionary.",
                code="INVALID_PAYLOAD",
            )

        draft_num = str(
            data.get("draft_number") or data.get("is_number") or data.get("number") or ""
        ).strip()
        title = str(data.get("title") or data.get("name") or "").strip()

        if not draft_num or not title:
            raise SourceAdapterError(
                "BIS draft data missing required fields 'draft_number' and/or 'title'.",
                code="MISSING_REQUIRED_FIELDS",
            )

        # Prefix with "DRAFT " if not already present
        if not draft_num.upper().startswith("DRAFT"):
            is_num_str = f"DRAFT {draft_num}"
        else:
            is_num_str = draft_num

        url = source_url or data.get("source_url") or data.get("url")

        std = Standard(
            is_number=is_num_str,
            part=data.get("part"),
            section=data.get("section"),
            year=self.parse_year(data.get("year")),
            title=title,
            scope=data.get("scope"),
            document_type=DocumentType.OTHER,
            division_council=data.get("division_council"),
            technical_committee=data.get("technical_committee"),
            status=StandardStatus.UNDER_REVISION,  # Draft standards are UNDER_REVISION
            source_url=url,
            retrieved_at=utcnow(),
        )

        draft_evidence = Evidence(
            source_type=EvidenceSourceType.BIS_WIDE_CIRCULATION_DRAFT,
            source_name=f"BIS Wide Circulation Draft {std.is_number}",
            authority="BIS",
            url=url,
            section="Draft Scope",
            excerpt=std.scope or f"Draft standard: {std.title}",
            publication_date=self.parse_date(data.get("publication_date") or data.get("draft_date")),
            retrieval_date=utcnow(),
            confidence=0.85,
        )

        return std, [draft_evidence]
