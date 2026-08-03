"""Document repositories — certificate, warranty, membership card (Sprint 5)."""

from typing import Optional

from models.documents import Certificate, MembershipCard, Warranty
from repositories.domain import DomainRepository


class CertificateRepository(DomainRepository[Certificate]):
    model = Certificate
    collection_name = "certificates"

    async def get_by_number(self, certificate_number: str) -> Optional[Certificate]:
        doc = await self.find_one({"certificate_number": certificate_number})
        return self.model.from_mongo(doc)

    async def get_current_for_gemstone(
        self, gemstone_uuid: str
    ) -> Optional[Certificate]:
        doc = await self.find_one({"gemstone_id": gemstone_uuid, "is_current": True})
        return self.model.from_mongo(doc)


class WarrantyRepository(DomainRepository[Warranty]):
    model = Warranty
    collection_name = "warranties"

    async def get_current_for_gemstone(
        self, gemstone_uuid: str
    ) -> Optional[Warranty]:
        doc = await self.find_one({"gemstone_id": gemstone_uuid, "is_current": True})
        return self.model.from_mongo(doc)


class MembershipCardRepository(DomainRepository[MembershipCard]):
    model = MembershipCard
    collection_name = "membership_cards"

    async def get_current_for_customer(
        self, customer_uuid: str
    ) -> Optional[MembershipCard]:
        doc = await self.find_one({"customer_id": customer_uuid, "is_current": True})
        return self.model.from_mongo(doc)
