"""SQLite persistence for analysis jobs and their assembled results."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path

from shared.models import Analysis


class AnalysisRepository:
    """Persist complete Analysis models without coupling the pipeline to an ORM."""

    def __init__(self, database_path: str) -> None:
        self.path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_sync(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC)"
            )

    async def initialize(self) -> None:
        await asyncio.to_thread(self._initialize_sync)

    def _save_sync(self, analysis: Analysis) -> None:
        payload = json.dumps(analysis.model_dump(mode="json"), separators=(",", ":"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO analyses(id, status, created_at, updated_at, payload)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status=excluded.status,
                    updated_at=excluded.updated_at,
                    payload=excluded.payload
                """,
                (
                    analysis.id,
                    analysis.status.value,
                    analysis.created_at.isoformat(),
                    analysis.updated_at.isoformat(),
                    payload,
                ),
            )

    async def save(self, analysis: Analysis) -> None:
        await asyncio.to_thread(self._save_sync, analysis)

    def _get_sync(self, analysis_id: str) -> Analysis | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM analyses WHERE id = ?", (analysis_id,)
            ).fetchone()
        return Analysis.model_validate_json(row["payload"]) if row else None

    async def get(self, analysis_id: str) -> Analysis | None:
        return await asyncio.to_thread(self._get_sync, analysis_id)

    def _list_sync(self, limit: int | None = None) -> list[Analysis]:
        query = "SELECT payload FROM analyses ORDER BY created_at DESC"
        params: tuple[int, ...] = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [Analysis.model_validate_json(row["payload"]) for row in rows]

    async def list(self, limit: int | None = None) -> list[Analysis]:
        return await asyncio.to_thread(self._list_sync, limit)
