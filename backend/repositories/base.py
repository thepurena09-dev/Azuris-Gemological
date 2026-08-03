"""Repository foundation — Sprint 3.

A generic, reusable async repository base class over a single Motor collection.
This is the *foundation only*: it is not wired to any API endpoint and no domain
(business) repositories are defined yet — those arrive in Sprint 5. It exists now
so the data-access layer has a stable contract that later sprints extend without
rewrites.

Conventions:
- Soft delete via `is_deleted` / `deleted_at`.
- Reads exclude soft-deleted documents by default.
- Pagination/filter/sort helpers for consistent querying.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase


class BaseRepository:
    """Generic async data-access foundation for a single collection."""

    collection_name: str = ""

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: Optional[str] = None):
        name = collection_name or self.collection_name
        if not name:
            raise ValueError("collection_name must be provided.")
        self.collection: AsyncIOMotorCollection = db[name]

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _active_filter(self, query: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Merge a caller query with the not-soft-deleted constraint."""
        base: dict[str, Any] = {"is_deleted": {"$ne": True}}
        if query:
            base.update(query)
        return base

    async def find_one(self, query: dict[str, Any]) -> Optional[dict[str, Any]]:
        return await self.collection.find_one(self._active_filter(query))

    async def find_many(
        self,
        query: Optional[dict[str, Any]] = None,
        *,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_dir: int = -1,
    ) -> list[dict[str, Any]]:
        cursor = (
            self.collection.find(self._active_filter(query))
            .sort(sort_by, sort_dir)
            .skip(max(skip, 0))
            .limit(max(min(limit, 200), 1))
        )
        return await cursor.to_list(length=limit)

    async def count(self, query: Optional[dict[str, Any]] = None) -> int:
        return await self.collection.count_documents(self._active_filter(query))

    async def insert_one(self, document: dict[str, Any]) -> str:
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def update_one(
        self, query: dict[str, Any], changes: dict[str, Any]
    ) -> int:
        result = await self.collection.update_one(
            self._active_filter(query), {"$set": changes}
        )
        return result.modified_count

    async def soft_delete(self, query: dict[str, Any]) -> int:
        result = await self.collection.update_one(
            self._active_filter(query),
            {"$set": {"is_deleted": True, "deleted_at": self._now()}},
        )
        return result.modified_count
