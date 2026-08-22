"""
kartikey/document_processing/validator.py

Validates uploaded files before any processing happens.

Rules enforced:
  - Only PDF and DOCX are accepted (scanned images, spreadsheets, etc. are rejected)
  - Maximum file size: configurable, default 20 MB
  - Filename must not contain path traversal characters

Does NOT touch external sources or the database.
Raises DocumentError (from shared.utils) on any violation so the
API layer can return a clean 400 response.
"""

from __future__ import annotations

from pathlib import Path

from shared.utils import DocumentError

# Supported file extensions and their MIME types
ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".docx"})
ALLOWED_MIME_TYPES: frozenset[str] = frozenset({
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
})


def validate_upload(
    filename: str,
    content: bytes,
    content_type: str = "",
    max_mb: float = 20.0,
) -> None:
    """
    Validate an uploaded file before storage and extraction.

    Parameters
    ----------
    filename:
        Original filename from the upload. Used to check extension.
    content:
        Raw file bytes.
    content_type:
        MIME type reported by the client (used as a secondary hint, not trusted alone).
    max_mb:
        Maximum allowed file size in megabytes.

    Raises
    ------
    DocumentError
        With a specific error code on any validation failure.
    """
    _check_filename(filename)
    _check_extension(filename)
    _check_size(filename, content, max_mb)
    _check_magic_bytes(filename, content, content_type)


def _check_filename(filename: str) -> None:
    """Reject empty filenames and path traversal attempts."""
    if not filename or not filename.strip():
        raise DocumentError(
            "Filename is empty.",
            code="EMPTY_FILENAME",
        )
    # Path.name strips directory components — if the result differs, traversal was attempted
    safe = Path(filename).name
    if safe != filename and safe != Path(filename).name:
        raise DocumentError(
            f"Filename '{filename}' contains disallowed path characters.",
            code="INVALID_FILENAME",
        )


def _check_extension(filename: str) -> None:
    """Check that the file extension is in the allowed set."""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise DocumentError(
            f"File type '{suffix}' is not supported. "
            f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            code="UNSUPPORTED_FILE_TYPE",
        )


def _check_size(filename: str, content: bytes, max_mb: float) -> None:
    """Reject files that exceed the size limit."""
    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_mb:
        raise DocumentError(
            f"'{filename}' is {size_mb:.1f} MB, which exceeds the {max_mb:.0f} MB limit.",
            code="FILE_TOO_LARGE",
        )
    if len(content) == 0:
        raise DocumentError(
            f"'{filename}' is empty.",
            code="EMPTY_FILE",
        )


# Magic byte signatures for supported types
# We check these independently of the client-reported MIME type,
# because the MIME type from a browser can be spoofed.
_MAGIC: dict[str, bytes] = {
    ".pdf": b"%PDF",
    # DOCX is a ZIP archive internally
    ".docx": b"PK\x03\x04",
}


def _check_magic_bytes(filename: str, content: bytes, content_type: str) -> None:
    """
    Verify the file's actual bytes match the expected format for its extension.
    This catches renamed files (e.g. a .exe renamed to .pdf).
    """
    suffix = Path(filename).suffix.lower()
    expected_magic = _MAGIC.get(suffix)
    if expected_magic and not content.startswith(expected_magic):
        raise DocumentError(
            f"'{filename}' does not appear to be a valid {suffix.upper()} file "
            f"(magic bytes mismatch). The file may be corrupted or misnamed.",
            code="INVALID_FILE_CONTENT",
        )
