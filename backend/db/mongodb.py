"""MongoDB connection manager — Sprint 3.

Async Motor client lifecycle (connect / disconnect / ping) driven by Settings.
This module is the single owner of the Motor client and database handle.
No business collections or CRUD live here.
"""

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from core.config import get_settings

logger = logging.getLogger("azuris.db")


class MongoManager:
    """Owns the Motor client + database handle for the application lifetime."""

    def __init__(self) -> None:
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        settings = get_settings()
        self._client = AsyncIOMotorClient(
            settings.mongo_url,
            uuidRepresentation="standard",
            serverSelectionTimeoutMS=5000,
        )
        self._db = self._client[settings.db_name]
        await self._client.admin.command("ping")
        logger.info("MongoDB connected (db=%s).", settings.db_name)

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed.")

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return self._db

    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._db is not None

    async def ping(self) -> bool:
        """Return True if the server responds to a ping, else False."""
        if self._client is None:
            return False
        try:
            await self._client.admin.command("ping")
            return True
        except Exception as exc:  # noqa: BLE001 - health check must never raise
            logger.warning("MongoDB ping failed: %s", exc)
            return False


# Application-wide singleton.
mongodb = MongoManager()


def get_database() -> AsyncIOMotorDatabase:
    """FastAPI-friendly accessor for the active database handle."""
    return mongodb.db
