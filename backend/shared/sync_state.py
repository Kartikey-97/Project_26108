"""
shared/sync_state.py

Thread-safe in-memory store for BIS live sync results.
Shared between the analysis pipeline (writer) and the API endpoint (reader).
Keyed by (analysis_id, is_number) so that syncs across different analyses
don't contaminate each other in the UI.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any

_lock = threading.Lock()
# Outer key: analysis_id (str) or "_global" for pipeline auto-syncs without an analysis context
# Inner key: IS number string
_sync_registry: dict[str, dict[str, dict[str, Any]]] = {}


def record_sync_result(
    is_number: str,
    synced_at: datetime,
    changed: bool,
    errors: list[str],
    analysis_id: str | None = None,
) -> None:
    """Record the result of a BIS sync attempt for one IS number.

    analysis_id scopes the result to a specific analysis so different tabs
    don't show each other's sync data.
    """
    bucket = analysis_id or "_global"
    with _lock:
        if bucket not in _sync_registry:
            _sync_registry[bucket] = {}
        _sync_registry[bucket][is_number] = {
            "is_number": is_number,
            "synced_at": synced_at.isoformat(),
            "changed": changed,
            "errors": errors,
        }


def get_sync_status(analysis_id: str | None = None) -> dict[str, Any]:
    """
    Return a JSON-serializable snapshot of sync results for a specific analysis.

    If analysis_id is given, returns only results for that analysis.
    Falls back to the global bucket if the analysis bucket is empty.

    Always returns a valid dict with these keys — never raises:
        last_synced_at  : str | None   (ISO 8601, most recent successful sync)
        total_synced    : int
        error_count     : int
        entries         : list[dict]
    """
    with _lock:
        if analysis_id and analysis_id in _sync_registry:
            entries = list(_sync_registry[analysis_id].values())
        elif "_global" in _sync_registry:
            entries = list(_sync_registry["_global"].values())
        else:
            entries = []

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
