"""Catalog repositories — gemstones & jewelry (Sprint 5)."""

from typing import Any

from models.catalog import Gemstone, Jewelry
from models.enums import GemstoneStatus, JewelryStatus
from repositories.domain import DomainRepository


class GemstoneRepository(DomainRepository[Gemstone]):
    model = Gemstone
    collection_name = "gemstones"

    async def list_by_status(self, status: GemstoneStatus, **kwargs: Any):
        return await self.list({"status": status.value}, **kwargs)

    async def list_published(self, **kwargs: Any):
        return await self.list_by_status(GemstoneStatus.PUBLISHED, **kwargs)


class JewelryRepository(DomainRepository[Jewelry]):
    model = Jewelry
    collection_name = "jewelry"

    async def list_published(self, **kwargs: Any):
        return await self.list({"status": JewelryStatus.PUBLISHED.value}, **kwargs)
