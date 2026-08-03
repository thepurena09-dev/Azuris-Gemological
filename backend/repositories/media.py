"""Media repository (Sprint 5)."""

from typing import Any

from models.enums import MediaEntityType
from models.media import Media
from repositories.domain import DomainRepository


class MediaRepository(DomainRepository[Media]):
    model = Media
    collection_name = "media"

    async def list_for_entity(
        self, entity_type: MediaEntityType, entity_id: str, **kwargs: Any
    ):
        return await self.list(
            {"entity_type": entity_type.value, "entity_id": entity_id}, **kwargs
        )
