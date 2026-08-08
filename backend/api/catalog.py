"""Jewelry domain endpoints — Sprint 13 (BATCH B, Core Domain Modules).

Jewelry is a data/certification domain (NOT a marketplace; the public catalog
stays disabled per the approved client revision). A piece is composed of one or
more gemstones; referenced gemstone uuids must resolve to existing stones.

RBAC per the locked matrix:
- read:   JEWELRY_READ  (ADMINISTRATOR, CONTENT_MANAGER, CUSTOMER_SERVICE, +SUPER)
- write:  JEWELRY_WRITE (ADMINISTRATOR, +SUPER)
- delete: JEWELRY_DELETE (ADMINISTRATOR, +SUPER)

Routes yield raw data; the Sprint 8 middleware wraps the success envelope.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth.audit import write_audit_log
from auth.rbac import Permission, require_permission
from db.mongodb import get_database
from errors import ApiError, ErrorCode
from models.base import utcnow_iso
from models.catalog import Jewelry
from models.enums import AuditAction, JewelryStatus
from models.people import Admin
from repositories.catalog import GemstoneRepository, JewelryRepository

admin_router = APIRouter(prefix="/admin/jewelry", tags=["jewelry-admin"])

_READ = require_permission(Permission.JEWELRY_READ)
_WRITE = require_permission(Permission.JEWELRY_WRITE)
_DELETE = require_permission(Permission.JEWELRY_DELETE)

# Locked lifecycle (BUSINESS_RULES_LOCK §2).
_TRANSITIONS: dict[str, set[str]] = {
    JewelryStatus.DRAFT.value: {JewelryStatus.PUBLISHED.value, JewelryStatus.ARCHIVED.value},
    JewelryStatus.PUBLISHED.value: {JewelryStatus.ARCHIVED.value},
    JewelryStatus.ARCHIVED.value: {JewelryStatus.PUBLISHED.value},
}


class JewelryIn(BaseModel):
    name_id: str = Field(min_length=1, max_length=200)
    name_en: str = Field(min_length=1, max_length=200)
    jewelry_type: str = Field(min_length=1, max_length=100)
    material: str = Field(min_length=1, max_length=120)
    gemstone_ids: list[str] = Field(default_factory=list)
    weight_grams: float | None = Field(default=None, gt=0)
    dimensions_mm: str | None = None
    description_id: str | None = None
    description_en: str | None = None


class JewelryPatch(BaseModel):
    name_id: str | None = Field(default=None, min_length=1, max_length=200)
    name_en: str | None = Field(default=None, min_length=1, max_length=200)
    jewelry_type: str | None = None
    material: str | None = None
    gemstone_ids: list[str] | None = None
    weight_grams: float | None = Field(default=None, gt=0)
    dimensions_mm: str | None = None
    description_id: str | None = None
    description_en: str | None = None


class StatusIn(BaseModel):
    status: JewelryStatus


def _view(j: Jewelry) -> dict:
    return {
        "uuid": j.uuid,
        "name_id": j.name_id,
        "name_en": j.name_en,
        "jewelry_type": j.jewelry_type,
        "material": j.material,
        "gemstone_ids": j.gemstone_ids,
        "weight_grams": j.weight_grams,
        "dimensions_mm": j.dimensions_mm,
        "description_id": j.description_id,
        "description_en": j.description_en,
        "status": j.status,
        "media_ids": j.media_ids,
        "created_at": j.created_at,
        "updated_at": j.updated_at,
    }


def _not_found() -> ApiError:
    return ApiError(404, ErrorCode.NOT_FOUND, "Jewelry not found.")


async def _validate_gemstones(db, gemstone_ids: list[str]) -> None:
    repo = GemstoneRepository(db)
    for gid in gemstone_ids:
        if await repo.get_by_uuid(gid) is None:
            raise ApiError(
                400, ErrorCode.BAD_REQUEST, f"Referenced gemstone not found: {gid}."
            )


@admin_router.get("")
async def list_jewelry(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    q: str | None = None,
    admin: Admin = Depends(_READ),
    db=Depends(get_database),
):
    filters: dict = {}
    if status:
        filters["status"] = status
    if q:
        rx = {"$regex": q.strip(), "$options": "i"}
        filters["$or"] = [{"name_id": rx}, {"name_en": rx}, {"jewelry_type": rx}, {"material": rx}]
    items, total = await JewelryRepository(db).list(
        filters or None, page=page, page_size=page_size
    )
    return {"items": [_view(j) for j in items], "total": total, "page": page, "page_size": page_size}


@admin_router.get("/{uuid}")
async def get_jewelry(uuid: str, admin: Admin = Depends(_READ), db=Depends(get_database)):
    j = await JewelryRepository(db).get_by_uuid(uuid)
    if j is None:
        raise _not_found()
    return _view(j)


@admin_router.post("", status_code=201)
async def create_jewelry(body: JewelryIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    await _validate_gemstones(db, body.gemstone_ids)
    piece = Jewelry(**body.model_dump(), created_by=admin.uuid, updated_by=admin.uuid)
    saved = await JewelryRepository(db).create(piece)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="jewelry", entity_id=saved.uuid,
        after={"name": saved.name_en, "gemstone_ids": saved.gemstone_ids},
    )
    return _view(saved)


@admin_router.put("/{uuid}")
async def update_jewelry(
    uuid: str, body: JewelryPatch, admin: Admin = Depends(_WRITE), db=Depends(get_database)
):
    repo = JewelryRepository(db)
    before = await repo.get_by_uuid(uuid)
    if before is None:
        raise _not_found()
    changes = {k: v for k, v in body.model_dump(exclude_unset=True).items()}
    if "gemstone_ids" in changes and changes["gemstone_ids"] is not None:
        await _validate_gemstones(db, changes["gemstone_ids"])
    changes["updated_by"] = admin.uuid
    changes["updated_at"] = utcnow_iso()
    await repo.update_one({"uuid": uuid}, changes)
    after = await repo.get_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="jewelry", entity_id=uuid,
        before={"gemstone_ids": before.gemstone_ids},
        after={"gemstone_ids": after.gemstone_ids},
    )
    return _view(after)


@admin_router.post("/{uuid}/status")
async def set_jewelry_status(
    uuid: str, body: StatusIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)
):
    repo = JewelryRepository(db)
    j = await repo.get_by_uuid(uuid)
    if j is None:
        raise _not_found()
    target = body.status.value if hasattr(body.status, "value") else str(body.status)
    if target != j.status and target not in _TRANSITIONS.get(j.status, set()):
        raise ApiError(
            409, ErrorCode.CONFLICT, f"Invalid status transition: {j.status} → {target}."
        )
    await repo.update_one({"uuid": uuid}, {"status": target, "updated_by": admin.uuid, "updated_at": utcnow_iso()})
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="jewelry", entity_id=uuid,
        before={"status": j.status}, after={"status": target},
    )
    return _view(await repo.get_by_uuid(uuid))


@admin_router.delete("/{uuid}")
async def delete_jewelry(uuid: str, admin: Admin = Depends(_DELETE), db=Depends(get_database)):
    repo = JewelryRepository(db)
    j = await repo.get_by_uuid(uuid)
    if j is None:
        raise _not_found()
    await repo.soft_delete_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.DELETE,
        entity_type="jewelry", entity_id=uuid, before={"name": j.name_en},
    )
    return {"deleted": True}
