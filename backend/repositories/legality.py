"""Repositories for FASE 2 domains â€” legality, settings, verification lookups.

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


class GemstonePhotoRepository(DomainRepository[LegalityDocument]):
    model = LegalityDocument
    collection_name = "gemstone_photos"


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

    async def list_published(self, page: int, page_size: int) -> dict:
        pipeline = [
            {"$match": self._active_filter({"is_current": True, "status": {"$ne": "revoked"}})},
            {"$lookup": {"from": "gemstones", "localField": "gemstone_id", "foreignField": "uuid", "as": "gem"}},
            {"$unwind": "$gem"},
            {"$match": {"gem.status": "published", "gem.is_deleted": {"$ne": True}, "$expr": {"$eq": ["$gem.certificate_id", "$uuid"]}}},
            {"$sort": {"created_at": -1, "uuid": 1}},
            {"$facet": {
                "items": [
                    {"$skip": (page - 1) * page_size}, {"$limit": page_size},
                    {"$project": {"_id": 0, "uuid": 1, "certificate_number": 1, "gemstone_id": 1,
                                  "status": 1, "version": 1, "is_current": 1, "issued_at": 1,
                                  "gemstone_name": "$gem.name_en", "gemstone_type": "$gem.gemstone_type", "origin": "$gem.origin"}},
                ],
                "total": [{"$count": "count"}],
            }},
        ]
        rows = await self.collection.aggregate(pipeline).to_list(length=1)
        row = rows[0] if rows else {"items": [], "total": []}
        return {"items": row["items"], "total": row["total"][0]["count"] if row["total"] else 0,
                "page": page, "page_size": page_size}

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
