"""
kshiraj/ingestion/pdf_extractor.py

Government PDF document extractor.
Extracts page-by-page text, table layouts, and document metadata.
Identifies image-only or scanned PDFs and marks them as OCR_REQUIRED without hard failures.
"""

from __future__ import annotations

import hashlib
import io
import re
from typing import Any, Dict, List, Optional

from shared.models import EvidenceSourceType
from shared.utils import get_logger, utcnow
from kshiraj.ingestion.frontier import normalize_url
from kshiraj.ingestion.models import ExtractionStatus, PageMetadata, RawDocument

logger = get_logger(__name__)


class PdfExtractor:
    """
    Extracts text and structural metadata from PDF byte streams.
    """

    MIN_CHARS_PER_PAGE_THRESHOLD = 40  # Minimum characters to distinguish text vs scanned PDF

    def extract_document(
        self,
        pdf_bytes: bytes,
        source_url: str,
        source_name: str = "Government PDF Document",
        source_type: EvidenceSourceType = EvidenceSourceType.OTHER_GOVERNMENT,
    ) -> RawDocument:
        """
        Parse raw PDF bytes and produce a structured RawDocument.
        """
        content_hash = hashlib.sha256(pdf_bytes).hexdigest() if pdf_bytes else ""

        if not pdf_bytes:
            return RawDocument(
                source_url=source_url,
                canonical_url=normalize_url(source_url),
                source_name=source_name,
                source_type=source_type,
                mime_type="application/pdf",
                content_hash=content_hash,
                text_content="",
                extraction_status=ExtractionStatus.EMPTY,
                retrieved_at=utcnow(),
            )

        # Try pdfplumber first
        page_texts: Dict[int, str] = {}
        metadata_dict: Dict[str, Any] = {}
        total_pages = 0
        extraction_status = ExtractionStatus.SUCCESS

        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                total_pages = len(pdf.pages)
                metadata_dict = dict(pdf.metadata or {})

                for idx, page in enumerate(pdf.pages):
                    page_num = idx + 1
                    try:
                        text = page.extract_text() or ""
                        page_texts[page_num] = text.strip()
                    except Exception as p_err:
                        logger.debug("Failed extracting text from PDF page %s: %s", page_num, p_err)
                        page_texts[page_num] = ""

        except ImportError:
            # Fallback to pypdf if pdfplumber not present
            try:
                import pypdf

                reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                total_pages = len(reader.pages)
                if reader.metadata:
                    metadata_dict = {str(k): str(v) for k, v in reader.metadata.items()}

                for idx, page in enumerate(reader.pages):
                    page_num = idx + 1
                    text = page.extract_text() or ""
                    page_texts[page_num] = text.strip()

            except Exception as pypdf_err:
                logger.error("pypdf extraction failed for %s: %s", source_url, pypdf_err)
                extraction_status = ExtractionStatus.MALFORMED

        except Exception as exc:
            logger.error("PDF extraction error for %s: %s", source_url, exc)
            extraction_status = ExtractionStatus.MALFORMED

        full_text = "\n\n".join(t for t in page_texts.values() if t).strip()

        # Check if the PDF is scanned / image-only (requires OCR)
        if total_pages > 0:
            avg_chars = len(full_text) / max(1, total_pages)
            if avg_chars < self.MIN_CHARS_PER_PAGE_THRESHOLD:
                logger.info(
                    "PDF %s has %s pages but only %s chars (avg %.1f chars/page). Classifying as OCR_REQUIRED.",
                    source_url, total_pages, len(full_text), avg_chars
                )
                extraction_status = ExtractionStatus.OCR_REQUIRED

        page_meta = PageMetadata(
            title=metadata_dict.get("Title") or metadata_dict.get("/Title"),
            author=metadata_dict.get("Author") or metadata_dict.get("/Author"),
            published_date=metadata_dict.get("CreationDate") or metadata_dict.get("/CreationDate"),
            custom_metadata=metadata_dict,
        )

        return RawDocument(
            source_url=source_url,
            canonical_url=normalize_url(source_url),
            source_name=source_name,
            source_type=source_type,
            mime_type="application/pdf",
            content_hash=content_hash,
            content_length=len(pdf_bytes),
            text_content=full_text,
            page_texts=page_texts,
            page_count=max(1, total_pages),
            metadata=page_meta,
            extraction_status=extraction_status,
            retrieved_at=utcnow(),
        )
