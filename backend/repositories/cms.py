"""CMS repository (Sprint 5)."""

from typing import Optional

from models.cms import SiteContent
from repositories.domain import DomainRepository


class SiteContentRepository(DomainRepository[SiteContent]):
    model = SiteContent
    collection_name = "site_content"

    async def get_by_key(self, key: str) -> Optional[SiteContent]:
        doc = await self.find_one({"key": key})
        return self.model.from_mongo(doc)
