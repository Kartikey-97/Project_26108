"""Shared utilities: logging setup, error types, datetime helpers."""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def get_logger(name: str) -> logging.Logger:
    """Return a consistently configured logger for any module."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------


class AppError(Exception):
    """Base error for all application-level exceptions."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class DocumentError(AppError):
    """Raised when document upload, validation, or extraction fails."""


class SourceAdapterError(AppError):
    """Raised when an external source adapter fails."""


class RetrievalError(AppError):
    """Raised when knowledge retrieval fails."""


class AnalysisError(AppError):
    """Raised when analysis pipeline encounters an unrecoverable error."""


# ---------------------------------------------------------------------------
# Datetime helpers
# ---------------------------------------------------------------------------


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def utcnow_iso() -> str:
    return utcnow().isoformat()
