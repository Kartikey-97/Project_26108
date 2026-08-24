"""
kartikey/document_processing/storage.py

Stores uploaded document files to disk and manages document metadata.

For MVP: files are stored under UPLOAD_DIR/{document_id}/{filename}
For production: swap out _write_bytes() to use S3/GCS by implementing
the same async interface — nothing else in the codebase changes.

Stored items per document:
  - The raw original file (e.g. tender.pdf)
  - A metadata sidecar (.meta.json) with document_id, filename, size, etc.
  - The extracted plain text (.extracted.txt) — written by extractor.py

The metadata sidecar allows retrieving document info without a database lookup,
which is useful during early development before the DB layer is integrated.
"""

from __future__ import annotations

import json
import uuid
from datetime import timezone
from pathlib import Path

from shared.config import settings
from shared.utils import DocumentError, get_logger, utcnow

logger = get_logger(__name__)


# ===========================================================================
# Public interface
# ===========================================================================

async def save_document(
    filename: str,
    content: bytes,
    content_type: str = "",
) -> tuple[str, Path]:
    """
    Persist a validated document to storage.

    Returns
    -------
    (document_id, file_path)
        document_id — UUID string, used as the reference in analyses
        file_path   — absolute path to the saved file
    """
    document_id = str(uuid.uuid4())
    safe_filename = Path(filename).name   # strip any remaining path components

    doc_dir = _doc_dir(document_id)
    doc_dir.mkdir(parents=True, exist_ok=True)

    file_path = doc_dir / safe_filename
    _write_bytes(file_path, content)

    # Write metadata sidecar
    meta = {
        "document_id": document_id,
        "filename": safe_filename,
        "size_bytes": len(content),
        "content_type": content_type,
        "stored_at": utcnow().isoformat(),
    }
    _write_bytes(doc_dir / ".meta.json", json.dumps(meta, indent=2).encode())

    logger.info(
        "Document stored: id=%s filename=%s size=%d bytes",
        document_id, safe_filename, len(content),
    )
    return document_id, file_path


async def save_extracted_text(document_id: str, text: str) -> None:
    """
    Persist the extracted plain text alongside the original document.
    Called by extractor.py after successful extraction.
    """
    doc_dir = _doc_dir(document_id)
    if not doc_dir.exists():
        raise DocumentError(
            f"Document directory for '{document_id}' not found.",
            code="DOCUMENT_NOT_FOUND",
        )
    _write_bytes(doc_dir / ".extracted.txt", text.encode("utf-8"))
    logger.debug("Extracted text saved for document %s (%d chars)", document_id, len(text))


def get_document_path(document_id: str) -> Path:
    """
    Return the path to the original document file for a given document_id.

    Raises DocumentError if the document does not exist.
    """
    doc_dir = _doc_dir(document_id)
    if not doc_dir.exists():
        raise DocumentError(
            f"Document '{document_id}' not found in storage.",
            code="DOCUMENT_NOT_FOUND",
        )
    # Find the first non-hidden file in the directory (the original document)
    files = [f for f in doc_dir.iterdir() if not f.name.startswith(".")]
    if not files:
        raise DocumentError(
            f"Document '{document_id}' directory is empty.",
            code="DOCUMENT_NOT_FOUND",
        )
    return files[0]


def get_extracted_text(document_id: str) -> str | None:
    """
    Return the previously extracted text for a document, or None if not yet extracted.
    """
    text_path = _doc_dir(document_id) / ".extracted.txt"
    if not text_path.exists():
        return None
    return text_path.read_text(encoding="utf-8")


def get_document_metadata(document_id: str) -> dict:
    """
    Return the stored metadata for a document.
    Returns empty dict if metadata file is missing.
    """
    meta_path = _doc_dir(document_id) / ".meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


# ===========================================================================
# Internal helpers
# ===========================================================================

def _doc_dir(document_id: str) -> Path:
    return Path(settings.upload_dir) / document_id


def _write_bytes(path: Path, content: bytes) -> None:
    """Write bytes to path. Raises DocumentError on I/O failure."""
    try:
        path.write_bytes(content)
    except OSError as exc:
        raise DocumentError(
            f"Failed to write file '{path}': {exc}",
            code="STORAGE_WRITE_FAILED",
        ) from exc
