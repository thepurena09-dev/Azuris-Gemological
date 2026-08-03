"""Refresh-token store repository — Sprint 6.

Server-side record of issued refresh tokens (by `jti`) enabling rotation and
logout invalidation. Repositories are the only layer touching MongoDB.
"""

from typing import Any, Optional

from models.base import utcnow_iso
from repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository):
    collection_name = "refresh_tokens"

    def __init__(self, db: Any):
        super().__init__(db, self.collection_name)

    async def store(self, jti: str, admin_id: str, expires_at: str) -> None:
        await self.collection.insert_one(
            {
                "jti": jti,
                "admin_id": admin_id,
                "expires_at": expires_at,
                "revoked": False,
                "created_at": utcnow_iso(),
            }
        )

    async def is_active(self, jti: str) -> bool:
        doc = await self.collection.find_one({"jti": jti})
        if not doc or doc.get("revoked"):
            return False
        return doc.get("expires_at", "") > utcnow_iso()

    async def get(self, jti: str) -> Optional[dict]:
        return await self.collection.find_one({"jti": jti})

    async def revoke(self, jti: str) -> int:
        result = await self.collection.update_one(
            {"jti": jti}, {"$set": {"revoked": True, "revoked_at": utcnow_iso()}}
        )
        return result.modified_count

    async def revoke_all_for_admin(self, admin_id: str) -> int:
        result = await self.collection.update_many(
            {"admin_id": admin_id, "revoked": False},
            {"$set": {"revoked": True, "revoked_at": utcnow_iso()}},
        )
        return result.modified_count
