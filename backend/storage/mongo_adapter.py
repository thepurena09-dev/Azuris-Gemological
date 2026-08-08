"""MongoDB-backed storage adapter — Sprint 10 (default backend).

Vendor-neutral default: object binaries live in a dedicated `media_objects`
collection (separate from the `media` metadata collection). Persistent (backed
by the same MongoDB the platform already uses) and requires no external
credentials, so it works out of the box. Swappable via the storage factory.
"""

from __future__ import annotations

from typing import Optional, Tuple

from bson.binary import Binary

from storage.base import StorageAdapter


class MongoStorageAdapter(StorageAdapter):
    COLLECTION = "media_objects"

    def __init__(self, db) -> None:
        self._c = db[self.COLLECTION]
        self._index_ready = False

    async def _ensure_index(self) -> None:
        if not self._index_ready:
            await self._c.create_index("key", unique=True)
            self._index_ready = True

    async def put(self, key: str, data: bytes, content_type: str) -> None:
        await self._ensure_index()
        await self._c.update_one(
            {"key": key},
            {"$set": {"key": key, "data": Binary(data), "content_type": content_type, "size": len(data)}},
            upsert=True,
        )

    async def get(self, key: str) -> Optional[Tuple[bytes, str]]:
        doc = await self._c.find_one({"key": key})
        if not doc:
            return None
        return bytes(doc["data"]), doc.get("content_type", "application/octet-stream")

    async def delete(self, key: str) -> bool:
        result = await self._c.delete_one({"key": key})
        return result.deleted_count > 0

    async def exists(self, key: str) -> bool:
        return await self._c.count_documents({"key": key}, limit=1) > 0
