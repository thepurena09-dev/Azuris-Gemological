"""Customer domain endpoints — Sprint 11 (BATCH B, Core Domain Modules).

Admin registry of gemstone owners. Foundation for Ownership → Ownership
Transfer → Membership Card (built later). RBAC per the locked matrix:
- read:   CUSTOMER_READ  (ADMINISTRATOR, CUSTOMER_SERVICE, +SUPER_ADMIN)
- write:  CUSTOMER_WRITE (ADMINISTRATOR, CUSTOMER_SERVICE — non-destructive)
- delete: CUSTOMER_DELETE (ADMINISTRATOR, +SUPER_ADMIN)

No public customer endpoint. Contact/PII is never exposed publicly and never
logged. All mutations are audited via the Sprint 9 correlation-aware writer.
Routes yield raw data; the Sprint 8 middleware wraps the success envelope.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field

from auth.audit import write_audit_log
from auth.rbac import Permission, require_permission
from db.mongodb import get_database
from errors import ApiError, ErrorCode
from models.base import utcnow_iso
from models.enums import AuditAction
from models.people import Admin, Customer
from repositories.people import CustomerRepository

admin_router = APIRouter(prefix="/admin/customers", tags=["customers-admin"])

_READ = require_permission(Permission.CUSTOMER_READ)
_WRITE = require_permission(Permission.CUSTOMER_WRITE)
_DELETE = require_permission(Permission.CUSTOMER_DELETE)


class CustomerIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)
    address_id: str | None = None
    address_en: str | None = None
    privacy_consent: bool = False
    notes_id: str | None = None
    notes_en: str | None = None


class CustomerPatch(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)
    address_id: str | None = None
    address_en: str | None = None
    privacy_consent: bool | None = None
    notes_id: str | None = None
    notes_en: str | None = None


def _view(c: Customer) -> dict:
    """Admin projection. Never exposes the internal ObjectId."""
    return {
        "uuid": c.uuid,
        "full_name": c.full_name,
        "email": c.email,
        "phone": c.phone,
        "address_id": c.address_id,
        "address_en": c.address_en,
        "privacy_consent": c.privacy_consent,
        "consent_at": c.consent_at,
        "owned_gemstone_ids": c.owned_gemstone_ids,
        "notes_id": c.notes_id,
        "notes_en": c.notes_en,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
    }


def _not_found() -> ApiError:
    return ApiError(404, ErrorCode.NOT_FOUND, "Customer not found.")


@admin_router.get("")
async def list_customers(
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
    admin: Admin = Depends(_READ),
    db=Depends(get_database),
):
    filters: dict = {}
    if q:
        rx = {"$regex": q.strip(), "$options": "i"}
        filters["$or"] = [{"full_name": rx}, {"email": rx}, {"phone": rx}]
    items, total = await CustomerRepository(db).list(
        filters or None, page=page, page_size=page_size
    )
    return {
        "items": [_view(c) for c in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@admin_router.get("/{uuid}")
async def get_customer(uuid: str, admin: Admin = Depends(_READ), db=Depends(get_database)):
    c = await CustomerRepository(db).get_by_uuid(uuid)
    if c is None:
        raise _not_found()
    return _view(c)


@admin_router.post("", status_code=201)
async def create_customer(
    body: CustomerIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)
):
    data = body.model_dump()
    consent_at = utcnow_iso() if data.get("privacy_consent") else None
    customer = Customer(
        **data, consent_at=consent_at, created_by=admin.uuid, updated_by=admin.uuid
    )
    saved = await CustomerRepository(db).create(customer)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="customer", entity_id=saved.uuid,
        after={"full_name": saved.full_name, "privacy_consent": saved.privacy_consent},
    )
    return _view(saved)


@admin_router.put("/{uuid}")
async def update_customer(
    uuid: str, body: CustomerPatch, admin: Admin = Depends(_WRITE), db=Depends(get_database)
):
    repo = CustomerRepository(db)
    before = await repo.get_by_uuid(uuid)
    if before is None:
        raise _not_found()
    changes = {k: v for k, v in body.model_dump(exclude_unset=True).items()}
    # Consent history: stamp consent_at the first time consent is granted.
    if changes.get("privacy_consent") is True and not before.consent_at:
        changes["consent_at"] = utcnow_iso()
    changes["updated_by"] = admin.uuid
    changes["updated_at"] = utcnow_iso()
    await repo.update_one({"uuid": uuid}, changes)
    after = await repo.get_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="customer", entity_id=uuid,
        before={"full_name": before.full_name, "privacy_consent": before.privacy_consent},
        after={"full_name": after.full_name, "privacy_consent": after.privacy_consent},
    )
    return _view(after)


@admin_router.delete("/{uuid}")
async def delete_customer(
    uuid: str, admin: Admin = Depends(_DELETE), db=Depends(get_database)
):
    repo = CustomerRepository(db)
    c = await repo.get_by_uuid(uuid)
    if c is None:
        raise _not_found()
    await repo.soft_delete_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.DELETE,
        entity_type="customer", entity_id=uuid,
        before={"full_name": c.full_name},
    )
    return {"deleted": True}
