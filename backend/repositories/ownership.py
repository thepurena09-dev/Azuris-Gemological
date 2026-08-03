"""Ownership & verification repositories (Sprint 5). No workflow logic here."""

from typing import Any, Optional

from models.enums import TransferStatus
from models.ownership import OwnershipTransfer, VerificationToken
from repositories.domain import DomainRepository


class OwnershipTransferRepository(DomainRepository[OwnershipTransfer]):
    model = OwnershipTransfer
    collection_name = "ownership_transfers"

    async def list_for_gemstone(self, gemstone_uuid: str, **kwargs: Any):
        return await self.list({"gemstone_id": gemstone_uuid}, **kwargs)

    async def get_pending_for_gemstone(
        self, gemstone_uuid: str
    ) -> Optional[OwnershipTransfer]:
        doc = await self.find_one(
            {"gemstone_id": gemstone_uuid, "status": TransferStatus.PENDING.value}
        )
        return self.model.from_mongo(doc)


class VerificationTokenRepository(DomainRepository[VerificationToken]):
    model = VerificationToken
    collection_name = "verification_tokens"

    async def get_by_token(self, token: str) -> Optional[VerificationToken]:
        doc = await self.find_one({"token": token, "is_active": True})
        return self.model.from_mongo(doc)

    async def get_active_for_gemstone(
        self, gemstone_uuid: str
    ) -> Optional[VerificationToken]:
        doc = await self.find_one({"gemstone_id": gemstone_uuid, "is_active": True})
        return self.model.from_mongo(doc)
