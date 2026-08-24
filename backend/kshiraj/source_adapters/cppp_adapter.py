"""
kshiraj/source_adapters/cppp_adapter.py

Adapter for CPPP / eProcure tender information.

Extracts tender specification metadata and converts into `shared.models.Evidence`
with source_type `EvidenceSourceType.CPPP_TENDER`.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from shared.models import Evidence, EvidenceSourceType
from shared.utils import SourceAdapterError, get_logger, utcnow

from kshiraj.source_adapters.base import BaseSourceAdapter

logger = get_logger(__name__)


class CpppAdapter(BaseSourceAdapter):
    """
    Ingestion adapter for CPPP (Central Public Procurement Portal) tender records.
    """

    def parse_tender_data(
        self,
        source_data: Union[Dict[str, Any], str],
        source_url: Optional[str] = None,
    ) -> List[Evidence]:
        """
        Parse CPPP tender source payload into a list of Evidence models.

        Parameters
        ----------
        source_data:
            Dictionary or JSON string representing CPPP tender metadata.
        source_url:
            Optional URL of the tender notice on eProcure portal.

        Returns
        -------
        List[Evidence]
            Constructed tender Evidence records.

        Raises
        ------
        SourceAdapterError:
            If source_data is malformed or missing key fields.
        """
        if isinstance(source_data, str):
            try:
                data = json.loads(source_data)
            except Exception as exc:
                raise SourceAdapterError(
                    f"Failed to parse CPPP JSON payload: {exc}",
                    code="INVALID_PAYLOAD",
                ) from exc
        elif isinstance(source_data, dict):
            data = source_data
        else:
            raise SourceAdapterError(
                f"Invalid CPPP source_data type: {type(source_data)}. Expected dict or JSON string.",
                code="INVALID_PAYLOAD",
            )

        if not isinstance(data, dict):
            raise SourceAdapterError(
                "CPPP source payload must be a dictionary.",
                code="INVALID_PAYLOAD",
            )

        tender_id = str(data.get("tender_id") or data.get("reference_number") or data.get("id") or "").strip()
        text_content = str(data.get("technical_specification") or data.get("text") or data.get("description") or "").strip()

        if not tender_id and not text_content:
            raise SourceAdapterError(
                "CPPP tender data missing required fields 'tender_id' and/or 'technical_specification'.",
                code="MISSING_REQUIRED_FIELDS",
            )

        url = source_url or data.get("source_url") or data.get("url")
        corrigendum_num = self.parse_int(data.get("corrigendum_number"))
        pub_date = self.parse_date(data.get("publication_date") or data.get("tender_date"))

        source_name_str = f"CPPP Tender {tender_id}" if tender_id else "CPPP Tender Specification"
        if corrigendum_num:
            source_name_str += f" Corrigendum {corrigendum_num}"

        evidence_records: List[Evidence] = []

        primary_evidence = Evidence(
            source_type=EvidenceSourceType.CPPP_TENDER,
            source_name=source_name_str,
            authority=data.get("procuring_authority") or "CPPP / eProcure",
            url=url,
            section=data.get("section") or "Technical Specifications",
            excerpt=text_content or f"Tender {tender_id} technical specification.",
            tender_id=tender_id or None,
            corrigendum_number=corrigendum_num,
            publication_date=pub_date,
            retrieval_date=utcnow(),
            confidence=1.0 if tender_id else 0.8,
        )
        evidence_records.append(primary_evidence)

        # Process additional clause items if present
        clauses = data.get("clauses") or []
        if isinstance(clauses, list):
            for idx, clause in enumerate(clauses):
                if isinstance(clause, dict):
                    clause_text = str(clause.get("text") or "").strip()
                    clause_sec = str(clause.get("clause_number") or clause.get("section") or f"Clause {idx + 1}")
                    if clause_text:
                        evidence_records.append(
                            Evidence(
                                source_type=EvidenceSourceType.CPPP_TENDER,
                                source_name=f"{source_name_str} - {clause_sec}",
                                authority=data.get("procuring_authority") or "CPPP / eProcure",
                                url=url,
                                section=clause_sec,
                                excerpt=clause_text,
                                tender_id=tender_id or None,
                                corrigendum_number=corrigendum_num,
                                publication_date=pub_date,
                                retrieval_date=utcnow(),
                                confidence=1.0,
                            )
                        )

        return evidence_records
