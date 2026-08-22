"""
shared/utils/__init__.py

Shared utilities used across the entire backend.

Contents:
  - get_logger()      consistent structured logger for any module
  - AppError          base exception class
  - DocumentError     file upload / extraction failures
  - SourceAdapterError  external source fetch failures
  - RetrievalError    knowledge retrieval failures
  - AnalysisError     analysis pipeline failures
  - utcnow()          timezone-aware UTC datetime
  - utcnow_iso()      ISO-8601 string
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Return a consistently configured logger.

    Usage:
        logger = get_logger(__name__)
        logger.info("Analysis %s started", analysis_id)
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger


# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------

class AppError(Exception):
    """
    Base class for all application-level errors.

    Always include a machine-readable `code` so the API layer can produce
    consistent error responses without pattern-matching on message strings.
    """

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"


class DocumentError(AppError):
    """Raised when document upload, validation, or text extraction fails."""


class SourceAdapterError(AppError):
    """Raised when an external source adapter (BIS, CPPP, QCO, etc.) fails."""


class RetrievalError(AppError):
    """Raised when knowledge/standards retrieval fails."""


class AnalysisError(AppError):
    """Raised when the analysis pipeline hits an unrecoverable error."""


# ---------------------------------------------------------------------------
# Datetime helpers
# ---------------------------------------------------------------------------

def utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(tz=timezone.utc)


def utcnow_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return utcnow().isoformat()
