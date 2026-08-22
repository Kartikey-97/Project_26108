"""POST /api/v1/documents/upload — upload a tender document for processing."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from kartikey.document_processing.validator import validate_upload
from kartikey.document_processing.storage import save_document
from kartikey.document_processing.extractor import extract_text
from shared.contracts import UploadDocumentResponse
from shared.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_SIZE_MB = 20


@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document(file: UploadFile) -> UploadDocumentResponse:
    """
    Upload a tender document (PDF or DOCX).

    Returns a document_id that can be passed to POST /analyses.
    Text extraction happens synchronously here so the analysis pipeline
    can reference already-extracted text.
    """
    content = await file.read()

    validate_upload(filename=file.filename or "", content=content, max_mb=MAX_SIZE_MB)

    document_id = str(uuid.uuid4())
    path = await save_document(document_id=document_id, filename=file.filename or "", content=content)
    text = extract_text(path=path, content_type=file.content_type or "")

    logger.info("Document uploaded: %s (%d bytes, id=%s)", file.filename, len(content), document_id)

    return UploadDocumentResponse(
        document_id=document_id,
        filename=file.filename or "",
        size_bytes=len(content),
        message="Document uploaded and text extracted successfully.",
    )
