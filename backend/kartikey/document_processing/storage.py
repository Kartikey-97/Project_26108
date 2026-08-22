"""
Document storage — save uploaded files to local disk.

For MVP: files are stored under ./uploads/{document_id}/
For production: swap with S3/GCS by implementing the same interface.
"""

from __future__ import annotations

import os
from pathlib import Path

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "./uploads"))


async def save_document(document_id: str, filename: str, content: bytes) -> Path:
    """
    Persist raw document bytes.

    Returns the path to the saved file.
    """
    doc_dir = UPLOAD_DIR / document_id
    doc_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(filename).name   # strip any directory traversal
    file_path = doc_dir / safe_filename
    file_path.write_bytes(content)
    return file_path
