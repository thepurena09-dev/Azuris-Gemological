"""Generic model-aware repository — Sprint 5.

Extends the Sprint 3 `BaseRepository` (dict-level foundation) with model
translation via `BaseDocument.from_mongo` / `to_mongo`, plus consistent
pagination / filtering / sorting. Repositories are the ONLY layer that talks to
MongoDB. No business logic lives here.
"""

from typing import Any, Generic, Optional, Type, TypeVar

from bson import ObjectId

from models.base import BaseDocument, utcnow_iso
from repositories.base import BaseRepository

T = TypeVar("T", bound=BaseDocument)


class DomainRepository(BaseRepository, Generic[T]):
    """Binds a collection to a Pydantic model and returns typed instances."""

    model: Type[T]
    collection_name: str = ""

    def __init__(self, db: Any):
        if not getattr(self, "collection_name", "") or not getattr(self, "model", None):
            raise ValueError("Subclass must set `model` and `collection_name`.")
        super().__init__(db, self.collection_name)

    async def create(self, instance: T) -> T:
        doc = instance.to_mongo()
        result = await self.collection.insert_one(doc)
        instance.id = str(result.inserted_id)
        return instance

    async def get_by_uuid(self, uuid: str) -> Optional[T]:
        doc = await self.find_one({"uuid": uuid})
        return self.model.from_mongo(doc)

    async def get_by_id(self, doc_id: str) -> Optional[T]:
        try:
            oid = ObjectId(doc_id)
        except Exception:
            return None
        doc = await self.collection.find_one(self._active_filter({"_id": oid}))
        return self.model.from_mongo(doc)

    async def list(
        self,
        filters: Optional[dict[str, Any]] = None,
        *,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_dir: int = -1,
    ) -> tuple[list[T], int]:
        page = max(page, 1)
        page_size = max(min(page_size, 200), 1)
        skip = (page - 1) * page_size
        docs = await self.find_many(
            filters, skip=skip, limit=page_size, sort_by=sort_by, sort_dir=sort_dir
        )
        total = await self.count(filters)
        items = [self.model.from_mongo(d) for d in docs]
        return [i for i in items if i is not None], total

    async def update_by_uuid(
        self, uuid: str, changes: dict[str, Any]
    ) -> Optional[T]:
        payload = {k: v for k, v in changes.items() if v is not None}
        payload["updated_at"] = utcnow_iso()
        await self.update_one({"uuid": uuid}, payload)
        return await self.get_by_uuid(uuid)

    async def soft_delete_by_uuid(self, uuid: str) -> int:
        return await self.soft_delete({"uuid": uuid})


class AppendOnlyRepository(DomainRepository[T]):
    """Log repositories: create + read only (no update / soft delete)."""

    async def update_by_uuid(self, uuid: str, changes: dict[str, Any]):  # noqa: D401
        raise NotImplementedError("Append-only collection: updates are not allowed.")

    async def soft_delete_by_uuid(self, uuid: str):  # noqa: D401
        raise NotImplementedError("Append-only collection: deletes are not allowed.")
