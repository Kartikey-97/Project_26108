"""
Text extractor — convert raw document files to plain text.

Supported formats:
  - PDF  → pdfplumber (better table/column handling than PyPDF2)
  - DOCX → python-docx

Does NOT call external services or AI models.
Text cleaning/chunking is handled downstream by the AI/ML component.
"""

from __future__ import annotations

from pathlib import Path

from shared.utils import DocumentError, get_logger

logger = get_logger(__name__)


def extract_text(path: Path, content_type: str = "") -> str:
    """
    Extract plain text from a document file.

    Parameters
    ----------
    path:
        Path to the saved document.
    content_type:
        MIME type hint — used when file extension is ambiguous.

    Returns
    -------
    str
        Extracted plain text.

    Raises
    ------
    DocumentError
        If the file cannot be parsed.
    """
    suffix = path.suffix.lower()

    if suffix == ".pdf" or "pdf" in content_type:
        return _extract_pdf(path)
    if suffix == ".docx" or "wordprocessingml" in content_type:
        return _extract_docx(path)

    raise DocumentError(
        f"Cannot extract text from '{suffix}' file.",
        code="UNSUPPORTED_FILE_TYPE",
    )


def _extract_pdf(path: Path) -> str:
    try:
        import pdfplumber  # type: ignore[import-untyped]
    except ImportError as exc:
        raise DocumentError(
            "pdfplumber is not installed. Run: pip install pdfplumber",
            code="MISSING_DEPENDENCY",
        ) from exc

    pages: list[str] = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
    except Exception as exc:
        raise DocumentError(f"PDF extraction failed: {exc}", code="EXTRACTION_FAILED") from exc

    if not pages:
        raise DocumentError("PDF appears to contain no extractable text (may be scanned).", code="NO_TEXT")

    return "\n\n".join(pages)


def _extract_docx(path: Path) -> str:
    try:
        from docx import Document  # type: ignore[import-untyped]
    except ImportError as exc:
        raise DocumentError(
            "python-docx is not installed. Run: pip install python-docx",
            code="MISSING_DEPENDENCY",
        ) from exc

    try:
        doc = Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    except Exception as exc:
        raise DocumentError(f"DOCX extraction failed: {exc}", code="EXTRACTION_FAILED") from exc

    if not paragraphs:
        raise DocumentError("DOCX appears to be empty.", code="NO_TEXT")

    return "\n\n".join(paragraphs)
