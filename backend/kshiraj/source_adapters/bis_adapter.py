"""
kshiraj/source_adapters/bis_adapter.py

Adapter for BIS (Bureau of Indian Standards) official catalog standard data.

Converts raw BIS source records into `shared.models.Standard` and `shared.models.Evidence`.
Preserves designation fields, amendments, reaffirmation, supersession, and provenance URLs.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple, Union

from shared.models import (
    Amendment,
    DocumentType,
    Evidence,
    EvidenceSourceType,
    Standard,
    StandardStatus,
)
from shared.utils import SourceAdapterError, get_logger, utcnow

from kshiraj.source_adapters.base import BaseSourceAdapter

logger = get_logger(__name__)


class BisAdapter(BaseSourceAdapter):
    """
    Ingestion adapter for official BIS Indian Standard source data.
    """

    def parse_standard_data(
        self,
        source_data: Union[Dict[str, Any], str],
        source_url: Optional[str] = None,
    ) -> Tuple[Standard, List[Evidence]]:
        """
        Parse raw BIS source data (dict or JSON string) into Standard and Evidence objects.

        Parameters
        ----------
        source_data:
            Dictionary or JSON string representing raw BIS source payload.
        source_url:
            Optional canonical source page URL.

        Returns
        -------
        Tuple[Standard, List[Evidence]]
            Constructed Standard model and backing Evidence models.

        Raises
        ------
        SourceAdapterError:
            If source_data is malformed or invalid payload structure.
        """
        if isinstance(source_data, str):
            try:
                data = json.loads(source_data)
            except Exception as exc:
                raise SourceAdapterError(
                    f"Failed to parse JSON source payload: {exc}",
                    code="INVALID_PAYLOAD",
                ) from exc
        elif isinstance(source_data, dict):
            data = source_data
        else:
            raise SourceAdapterError(
                f"Invalid source_data type: {type(source_data)}. Expected dict or JSON string.",
                code="INVALID_PAYLOAD",
            )

        if not isinstance(data, dict):
            raise SourceAdapterError(
                "Source payload must be a key-value dictionary.",
                code="INVALID_PAYLOAD",
            )

        is_num = str(data.get("is_number") or "").strip()
        title = str(data.get("title") or "").strip()

        if not is_num or not title:
            # Check fallback keys
            is_num = is_num or str(data.get("designation") or data.get("number") or "").strip()
            title = title or str(data.get("standard_title") or data.get("name") or "").strip()

        if not is_num or not title:
            raise SourceAdapterError(
                "BIS source data missing required fields 'is_number' and/or 'title'.",
                code="MISSING_REQUIRED_FIELDS",
            )

        # Parse status enum
        status_str = str(data.get("status") or "").strip().lower()
        status_enum = StandardStatus.UNKNOWN
        for member in StandardStatus:
            if member.value == status_str:
                status_enum = member
                break

        # Parse document type enum
        doc_type_str = str(data.get("document_type") or "").strip().lower()
        doc_type_enum = DocumentType.OTHER
        for member in DocumentType:
            if member.value == doc_type_str:
                doc_type_enum = member
                break

        # Parse amendments
        amendments_data = data.get("amendments") or []
        amendments: List[Amendment] = []
        if isinstance(amendments_data, list):
            for amd in amendments_data:
                if isinstance(amd, dict):
                    amd_num = self.parse_int(amd.get("amendment_number") or amd.get("number"))
                    if amd_num is not None:
                        amendments.append(
                            Amendment(
                                amendment_number=amd_num,
                                year=self.parse_year(amd.get("year")),
                                description=amd.get("description"),
                                gazette_so_number=amd.get("gazette_so_number"),
                                effective_date=self.parse_date(amd.get("effective_date")),
                                source_url=amd.get("source_url"),
                            )
                        )

        url = source_url or data.get("source_url") or data.get("url")

        std = Standard(
            is_number=is_num,
            part=data.get("part"),
            section=data.get("section"),
            year=self.parse_year(data.get("year")),
            amendments=amendments,
            title=title,
            scope=data.get("scope"),
            document_type=doc_type_enum,
            ics_code=data.get("ics_code"),
            division_council=data.get("division_council"),
            technical_committee=data.get("technical_committee"),
            status=status_enum,
            reaffirmation_year=self.parse_year(data.get("reaffirmation_year")),
            superseded_by=data.get("superseded_by"),
            transition_deadline=self.parse_date(data.get("transition_deadline")),
            withdrawal_date=self.parse_date(data.get("withdrawal_date")),
            source_url=url,
            retrieved_at=utcnow(),
        )

        evidence_list: List[Evidence] = []

        # Primary Standard evidence
        std_evidence = Evidence(
            source_type=EvidenceSourceType.BIS_STANDARD,
            source_name=f"BIS Standard {std.designation}",
            authority="BIS",
            url=url,
            section="Scope",
            excerpt=std.scope or std.title,
            publication_date=self.parse_date(data.get("publication_date")),
            retrieval_date=utcnow(),
            confidence=1.0,
        )
        evidence_list.append(std_evidence)

        # Amendment evidence
        for amd in amendments:
            amd_evidence = Evidence(
                source_type=EvidenceSourceType.BIS_AMENDMENT,
                source_name=f"BIS Amendment {amd.amendment_number} to {std.designation}",
                authority="BIS",
                url=amd.source_url or url,
                amendment_number=amd.amendment_number,
                gazette_so_number=amd.gazette_so_number,
                excerpt=amd.description or f"Amendment {amd.amendment_number} applied to {std.is_number}.",
                publication_date=amd.effective_date,
                retrieval_date=utcnow(),
                confidence=1.0,
            )
            evidence_list.append(amd_evidence)

        return std, evidence_list
