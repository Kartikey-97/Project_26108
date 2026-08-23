"""
kartikey/api/routes/documents.py

POST /api/v1/documents/upload

Accepts a PDF or DOCX tender document, validates it, extracts text,
stores it, and returns a document_id for use in POST /analyses.

The endpoint is synchronous for the extraction step because:
  - PDF text extraction is fast (< 2s for most tender documents)
  - The analysis pipeline needs extracted text to start; making extraction
    async would require a separate polling step before POST /analyses

If documents become very large or extraction proves slow in practice,
this can be moved to a background task. Do not optimise prematurely.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

from kartikey.document_processing.extractor import extract_text, scan_is_references
from kartikey.document_processing.storage import (
    get_document_metadata,
    save_document,
    save_extracted_text,
)
from kartikey.document_processing.validator import validate_upload
from shared.contracts import UploadDocumentResponse
from shared.utils import DocumentError, get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/samples/led-street-lighting")
async def get_led_street_lighting_sample() -> FileResponse:
    """Serve the bundled tender used by the demo upload flow."""
    sample_path = Path(__file__).resolve().parents[2] / "data" / "Tendernotice_1.pdf"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Bundled sample document is unavailable.")
    return FileResponse(
        sample_path,
        media_type="application/pdf",
        filename="LED_Street_Lighting_Tender.pdf",
    )


@router.post("/upload", response_model=UploadDocumentResponse, status_code=201)
async def upload_document(file: UploadFile) -> UploadDocumentResponse:
    """
    Upload a tender document (PDF or DOCX).

    Steps:
      1. Read raw bytes
      2. Validate: extension, size, magic bytes
      3. Store original file to disk
      4. Extract plain text
      5. Store extracted text alongside original
      6. Return document_id

    The returned document_id is then passed to POST /api/v1/analyses.

    Error codes returned on failure:
      EMPTY_FILENAME         — no filename provided
      INVALID_FILENAME       — path traversal attempt
      UNSUPPORTED_FILE_TYPE  — not PDF or DOCX
      FILE_TOO_LARGE         — exceeds 20 MB
      EMPTY_FILE             — 0-byte file
      INVALID_FILE_CONTENT   — magic bytes mismatch
      SCANNED_PDF            — PDF has no text layer (image-only)
      ENCRYPTED_PDF          — password-protected PDF
      EXTRACTION_FAILED      — could not parse the document
      STORAGE_WRITE_FAILED   — disk write error
    """
    content = await file.read()

    # Step 1: Validate
    validate_upload(
        filename=file.filename or "",
        content=content,
        content_type=file.content_type or "",
    )

    # Step 2: Store original file
    document_id, file_path = await save_document(
        filename=file.filename or "document",
        content=content,
        content_type=file.content_type or "",
    )

    # Step 3: Extract text (raises DocumentError on failure)
    extracted_text = extract_text(file_path)

    # Step 4: Quick IS reference scan (informational — logged, not returned in response)
    is_refs = scan_is_references(extracted_text)
    if is_refs:
        logger.info(
            "Document %s: found %d IS reference(s) in preliminary scan: %s",
            document_id,
            len(is_refs),
            [r["matched_text"] for r in is_refs[:10]],  # log first 10
        )

    # Step 5: Persist extracted text
    await save_extracted_text(document_id, extracted_text)

    return UploadDocumentResponse(
        document_id=document_id,
        filename=file.filename or "document",
        size_bytes=len(content),
        content_type=file.content_type or "",
        message=(
            f"Document uploaded and text extracted successfully. "
            f"Found {len(is_refs)} IS reference(s) in preliminary scan. "
            f"Use document_id to create an analysis."
        ),
    )
