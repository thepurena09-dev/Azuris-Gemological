"""Warranty domain endpoints — BATCH C, Sprint 19 (Post-Certification).

Per-stone warranty terms & coverage. REUSE-FIRST: reuses the Sprint 4 `Warranty`
model, Sprint 5 `WarrantyRepository`, the versioning spine (one `is_current`
version; superseded retained immutably), audit writer, and RBAC.

Lifecycle (BUSINESS_RULES_LOCK §4): active → (expired | void). No path back to
active — term corrections create a NEW version (reissue). A warranty is always
bound to exactly one gemstone; one current version per stone.

RBAC (locked matrix): read=WARRANTY_READ, write=WARRANTY_WRITE, delete=WARRANTY_DELETE.
Routes yield raw data; the Sprint 8 middleware wraps the success envelope.
"""

from __future__ import annotations

import calendar
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth.audit import write_audit_log
from auth.rbac import Permission, require_permission
from db.mongodb import get_database
from errors import ApiError, ErrorCode
from models.base import utcnow_iso
from models.documents import Warranty
from models.enums import AuditAction, WarrantyStatus
from models.people import Admin
from repositories.catalog import GemstoneRepository
from repositories.counter import CounterRepository
from repositories.documents import WarrantyRepository

admin_router = APIRouter(prefix="/admin/warranties", tags=["warranties-admin"])

_READ = require_permission(Permission.WARRANTY_READ)
_WRITE = require_permission(Permission.WARRANTY_WRITE)
_DELETE = require_permission(Permission.WARRANTY_DELETE)

# Locked lifecycle (BUSINESS_RULES_LOCK §4).
_TRANSITIONS: dict[str, set[str]] = {
    WarrantyStatus.ACTIVE.value: {WarrantyStatus.EXPIRED.value, WarrantyStatus.VOID.value},
    WarrantyStatus.EXPIRED.value: set(),
    WarrantyStatus.VOID.value: set(),
}


class WarrantyIn(BaseModel):
    gemstone_id: str
    terms_id: str = Field(min_length=1)
    terms_en: str = Field(min_length=1)
    period_months: int = Field(ge=0)
    start_date: str | None = None
    end_date: str | None = None


class WarrantyReissueIn(BaseModel):
    terms_id: str = Field(min_length=1)
    terms_en: str = Field(min_length=1)
    period_months: int = Field(ge=0)
    start_date: str | None = None
    end_date: str | None = None


class StatusIn(BaseModel):
    status: WarrantyStatus


def _add_months(d: datetime, months: int) -> datetime:
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    return d.replace(year=y, month=m, day=day)


def _derive_end_date(start_date: str | None, period_months: int, end_date: str | None) -> str | None:
    if end_date:
        return end_date
    if not start_date:
        return None
    try:
        d = datetime.fromisoformat(start_date[:10])
    except ValueError:
        return None
    return _add_months(d, period_months).date().isoformat()


def _view(w: Warranty) -> dict:
    return {
        "uuid": w.uuid,
        "warranty_number": w.warranty_number,
        "gemstone_id": w.gemstone_id,
        "status": w.status,
        "terms_id": w.terms_id,
        "terms_en": w.terms_en,
        "period_months": w.period_months,
        "start_date": w.start_date,
        "end_date": w.end_date,
        "version": w.version,
        "is_current": w.is_current,
        "pdf_media_id": w.pdf_media_id,
        "created_at": w.created_at,
        "updated_at": w.updated_at,
    }


def _not_found() -> ApiError:
    return ApiError(404, ErrorCode.NOT_FOUND, "Warranty not found.")


async def _require_gemstone(db, gemstone_id: str) -> None:
    if await GemstoneRepository(db).get_by_uuid(gemstone_id) is None:
        raise ApiError(400, ErrorCode.BAD_REQUEST, f"Referenced gemstone not found: {gemstone_id}.")


@admin_router.get("")
async def list_warranties(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    gemstone_id: str | None = None,
    current_only: bool = False,
    admin: Admin = Depends(_READ),
    db=Depends(get_database),
):
    filters: dict = {}
    if status:
        filters["status"] = status
    if gemstone_id:
        filters["gemstone_id"] = gemstone_id
    if current_only:
        filters["is_current"] = True
    items, total = await WarrantyRepository(db).list(filters or None, page=page, page_size=page_size)
    return {"items": [_view(w) for w in items], "total": total, "page": page, "page_size": page_size}


@admin_router.get("/{uuid}")
async def get_warranty(uuid: str, admin: Admin = Depends(_READ), db=Depends(get_database)):
    w = await WarrantyRepository(db).get_by_uuid(uuid)
    if w is None:
        raise _not_found()
    return _view(w)


@admin_router.post("", status_code=201)
async def create_warranty(body: WarrantyIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    await _require_gemstone(db, body.gemstone_id)
    repo = WarrantyRepository(db)
    # One current warranty version per stone (BUSINESS_RULES §4).
    if await repo.get_current_for_gemstone(body.gemstone_id) is not None:
        raise ApiError(409, ErrorCode.CONFLICT, "Gemstone already has an active warranty (use reissue).")
    number = await CounterRepository(db).next_warranty_number()
    end_date = _derive_end_date(body.start_date, body.period_months, body.end_date)
    warranty = Warranty(
        warranty_number=number,
        gemstone_id=body.gemstone_id,
        status=WarrantyStatus.ACTIVE,
        terms_id=body.terms_id,
        terms_en=body.terms_en,
        period_months=body.period_months,
        start_date=body.start_date,
        end_date=end_date,
        version=1,
        is_current=True,
        created_version_by=admin.uuid,
        created_by=admin.uuid,
        updated_by=admin.uuid,
    )
    saved = await repo.create(warranty)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="warranty", entity_id=saved.uuid,
        after={"warranty_number": number, "gemstone_id": saved.gemstone_id, "status": "active"},
    )
    return _view(saved)


@admin_router.post("/{uuid}/reissue")
async def reissue_warranty(uuid: str, body: WarrantyReissueIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    repo = WarrantyRepository(db)
    old = await repo.get_by_uuid(uuid)
    if old is None:
        raise _not_found()
    # Archive current, then insert new version (roll back the flip on failure).
    await repo.update_one({"uuid": old.uuid}, {"is_current": False})
    end_date = _derive_end_date(body.start_date, body.period_months, body.end_date)
    new = Warranty(
        warranty_number=old.warranty_number,
        gemstone_id=old.gemstone_id,
        status=WarrantyStatus.ACTIVE,
        terms_id=body.terms_id,
        terms_en=body.terms_en,
        period_months=body.period_months,
        start_date=body.start_date,
        end_date=end_date,
        version=old.version + 1,
        is_current=True,
        created_version_by=admin.uuid,
        created_by=admin.uuid,
        updated_by=admin.uuid,
    )
    try:
        saved = await repo.create(new)
    except Exception:
        await repo.update_one({"uuid": old.uuid}, {"is_current": True})
        raise
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.VERSION_CREATE,
        entity_type="warranty", entity_id=saved.uuid,
        after={"warranty_number": old.warranty_number, "version": new.version},
    )
    return _view(saved)


@admin_router.post("/{uuid}/status")
async def set_warranty_status(uuid: str, body: StatusIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    repo = WarrantyRepository(db)
    w = await repo.get_by_uuid(uuid)
    if w is None:
        raise _not_found()
    target = body.status.value if hasattr(body.status, "value") else str(body.status)
    if target != w.status and target not in _TRANSITIONS.get(w.status, set()):
        raise ApiError(409, ErrorCode.CONFLICT, f"Invalid status transition: {w.status} → {target}.")
    await repo.update_one({"uuid": uuid}, {"status": target, "updated_by": admin.uuid, "updated_at": utcnow_iso()})
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="warranty", entity_id=uuid, before={"status": w.status}, after={"status": target},
    )
    return _view(await repo.get_by_uuid(uuid))


@admin_router.delete("/{uuid}")
async def delete_warranty(uuid: str, admin: Admin = Depends(_DELETE), db=Depends(get_database)):
    repo = WarrantyRepository(db)
    w = await repo.get_by_uuid(uuid)
    if w is None:
        raise _not_found()
    await repo.soft_delete_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.DELETE,
        entity_type="warranty", entity_id=uuid, before={"warranty_number": w.warranty_number},
    )
    return {"deleted": True}
