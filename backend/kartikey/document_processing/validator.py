"""
Document validator.

Raises DocumentError for invalid uploads.
Does NOT touch external sources.
"""

from __future__ import annotations

from shared.utils import DocumentError

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def validate_upload(filename: str, content: bytes, max_mb: int = 20) -> None:
    """
    Validate an uploaded file before processing.

    Raises
    ------
    DocumentError
        If the file type or size is not acceptable.
    """
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentError(
            f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}",
            code="UNSUPPORTED_FILE_TYPE",
        )

    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_mb:
        raise DocumentError(
            f"File too large ({size_mb:.1f} MB). Maximum allowed: {max_mb} MB.",
            code="FILE_TOO_LARGE",
        )
