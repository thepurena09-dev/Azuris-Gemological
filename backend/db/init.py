"""Database initialization — Sprint 3.

Connects the Motor manager and applies the index bootstrap. Safe to run at app
startup and idempotently re-run via the standalone script (scripts/init_db.py).
"""

import logging

from db.indexes import ensure_indexes
from db.mongodb import mongodb

logger = logging.getLogger("azuris.db")


async def init_database() -> dict[str, int]:
    """Ensure the DB is connected and all indexes exist. Returns index summary."""
    if not mongodb.is_connected:
        await mongodb.connect()
    return await ensure_indexes(mongodb.db)
