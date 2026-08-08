"""Repositories for FASE 2 domains — legality, settings, verification lookups.

Thin DomainRepository subclasses; the ONLY layer touching Mongo. No business
logic here (that lives in services / routers).
"""

from typing import Optional

from models.base import utcnow_iso
from models.catalog import Gemstone
from models.documents import Certificate
from models.legality import LegalityCredential, LegalityDocument
from models.ownership import VerificationToken
from models.people import Customer
from models.settings import BusinessSettings
from repositories.domain import DomainRepository


class LegalityRepository(DomainRepository[LegalityCredential]):
    model = LegalityCredential
    collection_name = "legality_credentials"

    async def get_published(self) -> Optional[LegalityCredential]:
        doc = await self.find_one({"publication_status": "published"})
        return self.model.from_mongo(doc)


class LegalityDocumentRepository(DomainRepository[LegalityDocument]):
    model = LegalityDocument
    collection_name = "legality_documents"


class SettingsRepository(DomainRepository[BusinessSettings]):
    model = BusinessSettings
    collection_name = "site_settings"

    async def get_or_create(self) -> BusinessSettings:
        doc = await self.find_one({"key": "business"})
        if doc:
            return self.model.from_mongo(doc)
        return await self.create(BusinessSettings())

    async def update_business(self, changes: dict) -> BusinessSettings:
        await self.get_or_create()
        payload = {k: v for k, v in changes.items() if v is not None}
        payload["updated_at"] = utcnow_iso()
        await self.update_one({"key": "business"}, payload)
        return await self.get_or_create()


class CertificateRepository(DomainRepository[Certificate]):
    model = Certificate
    collection_name = "certificates"

    async def get_current_by_number(self, number: str) -> Optional[Certificate]:
        doc = await self.find_one({"certificate_number": number, "is_current": True})
        return self.model.from_mongo(doc)


class GemstoneRepository(DomainRepository[Gemstone]):
    model = Gemstone
    collection_name = "gemstones"


class VerificationTokenRepository(DomainRepository[VerificationToken]):
    model = VerificationToken
    collection_name = "verification_tokens"

    async def get_by_token(self, token: str) -> Optional[VerificationToken]:
        doc = await self.find_one({"token": token, "is_active": True})
        return self.model.from_mongo(doc)

    async def get_active_for_certificate(
        self, certificate_uuid: str
    ) -> Optional[VerificationToken]:
        doc = await self.find_one(
            {"certificate_id": certificate_uuid, "is_active": True}
        )
        return self.model.from_mongo(doc)


class CustomerRepositoryV2(DomainRepository[Customer]):
    model = Customer
    collection_name = "customers"
