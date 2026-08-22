"""
init_db.py — create tables on startup (dev only).

For production, use Alembic migrations instead.

Usage:
    python -m database.init_db
"""

from __future__ import annotations

import asyncio

from database.models import Base
from database.session import engine
from shared.utils import get_logger

logger = get_logger(__name__)


async def init() -> None:
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready.")


if __name__ == "__main__":
    asyncio.run(init())
