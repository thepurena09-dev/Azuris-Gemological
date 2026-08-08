"""Object storage adapter abstraction — Sprint 10.

Vendor-neutral contract for storing/retrieving opaque binary objects. Business
code (media service) depends ONLY on this interface — never on a concrete
backend — so the storage vendor can change without touching callers.

The locked object-key layout groups objects by owning entity + role so the
folder structure is predictable across any backend:
    media/{entity_type}/{entity_id}/{role}/{media_uuid}.{ext}
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple


def build_object_key(
    entity_type: str, entity_id: str, role: str, media_uuid: str, ext: str = ""
) -> str:
    suffix = ("." + ext.lstrip(".")) if ext else ""
    return f"media/{entity_type}/{entity_id}/{role}/{media_uuid}{suffix}"


class StorageAdapter(ABC):
    """Binary object store. Metadata lives elsewhere (the `media` collection)."""

    @abstractmethod
    async def put(self, key: str, data: bytes, content_type: str) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> Optional[Tuple[bytes, str]]:
        """Return (data, content_type) or None if the key is absent."""

    @abstractmethod
    async def delete(self, key: str) -> bool: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...
