"""
kshiraj/source_adapters/qco_adapter.py

Adapter for Quality Control Order (QCO) gazette notifications.

Extracts mandatory QCO notification metadata and converts into `shared.models.Evidence`
with source_type `EvidenceSourceType.QCO_NOTIFICATION`.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple, Union

from shared.models import CertificationScheme, Evidence, EvidenceSourceType
from shared.utils import SourceAdapterError, get_logger, utcnow

from kshiraj.source_adapters.base import BaseSourceAdapter

logger = get_logger(__name__)


class QcoAdapter(BaseSourceAdapter):
    """
    Ingestion adapter for Quality Control Orders (QCO) issued by Indian ministries.
    """

    def parse_qco_data(
        self,
        source_data: Union[Dict[str, Any], str],
        source_url: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], List[Evidence]]:
        """
        Parse raw QCO notification payload into structured QCO metadata dictionary
        and backing Evidence models.

        Parameters
        ----------
        source_data:
            Dictionary or JSON string representing QCO notification metadata.
        source_url:
            Optional URL of the official gazette notification page.

        Returns
        -------
        Tuple[Dict[str, Any], List[Evidence]]
            Extracted QCO metadata dict and list of QCO Evidence objects.

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
                    f"Failed to parse QCO JSON payload: {exc}",
                    code="INVALID_PAYLOAD",
                ) from exc
        elif isinstance(source_data, dict):
            data = source_data
        else:
            raise SourceAdapterError(
                f"Invalid QCO source_data type: {type(source_data)}. Expected dict or JSON string.",
                code="INVALID_PAYLOAD",
            )

        if not isinstance(data, dict):
            raise SourceAdapterError(
                "QCO source payload must be a dictionary.",
                code="INVALID_PAYLOAD",
            )

        so_number = str(data.get("gazette_so_number") or data.get("so_number") or data.get("notification_number") or "").strip()
        is_num = str(data.get("is_number") or data.get("notified_standard") or "").strip()
        ministry = str(data.get("issuing_ministry") or data.get("ministry") or "Government of India").strip()

        if not so_number and not is_num:
            raise SourceAdapterError(
                "QCO notification data missing required fields 'gazette_so_number' and/or 'is_number'.",
                code="MISSING_REQUIRED_FIELDS",
            )

        # Parse certification scheme enum
        scheme_str = str(data.get("certification_scheme") or data.get("scheme") or "").strip().lower()
        scheme_enum: Optional[CertificationScheme] = None
        for member in CertificationScheme:
            if member.value == scheme_str:
                scheme_enum = member
                break

        url = source_url or data.get("source_url") or data.get("url")
        eff_date = self.parse_date(data.get("effective_date"))
        pub_date = self.parse_date(data.get("publication_date"))
        excerpt_text = str(
            data.get("excerpt")
            or data.get("mandate_text")
            or data.get("title")
            or f"QCO Notification {so_number} requiring mandatory BIS certification for {is_num}."
        ).strip()

        qco_metadata = {
            "is_number": is_num or None,
            "gazette_so_number": so_number or None,
            "issuing_ministry": ministry,
            "effective_date": eff_date,
            "publication_date": pub_date,
            "certification_scheme": scheme_enum,
            "qco_notified": True,
            "source_url": url,
        }

        qco_evidence = Evidence(
            source_type=EvidenceSourceType.QCO_NOTIFICATION,
            source_name=f"QCO Gazette Notification {so_number or is_num}",
            authority=ministry,
            url=url,
            gazette_so_number=so_number or None,
            excerpt=excerpt_text,
            publication_date=pub_date or eff_date,
            retrieval_date=utcnow(),
            confidence=1.0,
        )

        return qco_metadata, [qco_evidence]
