"""
shared/sync_state.py

Thread-safe in-memory store for BIS live sync results.
Shared between the analysis pipeline (writer) and the API endpoint (reader).
Single-process uvicorn MVP — GIL makes the dict reads safe without a lock,
but we use threading.Lock for correctness under any future multi-threaded scenario.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any

_lock = threading.Lock()
_sync_registry: dict[str, dict[str, Any]] = {}


def record_sync_result(
    is_number: str,
    synced_at: datetime,
    changed: bool,
    errors: list[str],
) -> None:
    """Record the result of a BIS sync attempt for one IS number."""
    with _lock:
        _sync_registry[is_number] = {
            "is_number": is_number,
            "synced_at": synced_at.isoformat(),
            "changed": changed,
            "errors": errors,
        }


def get_sync_status() -> dict[str, Any]:
    """
    Return a JSON-serializable snapshot of all sync results.

    Always returns a valid dict with these keys — never raises:
        last_synced_at  : str | None   (ISO 8601, most recent successful sync)
        total_synced    : int
        error_count     : int
        entries         : list[dict]
    """
    with _lock:
        entries = list(_sync_registry.values())

    successful = [e for e in entries if not e.get("errors")]
    last_synced_at = max(
        (e["synced_at"] for e in successful),
        default=None,
    ) if successful else None
    
    return {
        "last_synced_at": last_synced_at,
        "total_synced": len(entries),
        "error_count": sum(1 for e in entries if e.get("errors")),
        "entries": entries,
    }
