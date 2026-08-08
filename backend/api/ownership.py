"""Ownership & Ownership Transfer endpoints — BATCH C, Sprints 20-22.

Authoritative Customer ↔ Gemstone ownership relationship + non-destructive
history + the trusted transfer workflow. REUSE-FIRST: reuses the Sprint 4
`OwnershipTransfer` model, Sprint 5 repositories, audit/security writers, RBAC,
and the ownership service (which owns the mutation rules).

Ownership only changes via an explicit workflow — NEVER from verification / QR /
security code. Contact PII (email/phone/address) is never exposed here.

RBAC (locked matrix): read=OWNERSHIP_READ, write=OWNERSHIP_WRITE.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from auth.audit import write_audit_log
from auth.rbac import Permission, require_permission
from db.mongodb import get_database
from errors import ApiError, ErrorCode
from models.base import utcnow_iso
from models.enums import AuditAction, TransferStatus
from models.ownership import OwnershipTransfer
from models.people import Admin
from repositories.catalog import GemstoneRepository
from repositories.ownership import OwnershipTransferRepository
from repositories.people import CustomerRepository
from services.ownership import assign_initial_owner, cancel_transfer, complete_transfer
from services.verification import mask_owner_name

admin_router = APIRouter(prefix="/admin/ownership", tags=["ownership-admin"])

_READ = require_permission(Permission.OWNERSHIP_READ)
_WRITE = require_permission(Permission.OWNERSHIP_WRITE)


class AssignIn(BaseModel):
    gemstone_id: str
    owner_id: str


class TransferIn(BaseModel):
    gemstone_id: str
    new_owner_id: str
    transfer_date: str | None = None
    proof_media_id: str | None = None
    notes_id: str | None = None
    notes_en: str | None = None


class TransferPatch(BaseModel):
    new_owner_id: str | None = None
    transfer_date: str | None = None
    proof_media_id: str | None = None
    notes_id: str | None = None
    notes_en: str | None = None


def _transfer_view(t: OwnershipTransfer) -> dict:
    return {
        "uuid": t.uuid,
        "gemstone_id": t.gemstone_id,
        "previous_owner_id": t.previous_owner_id,
        "new_owner_id": t.new_owner_id,
        "transfer_date": t.transfer_date,
        "status": t.status,
        "proof_media_id": t.proof_media_id,
        "security_code_rotated": t.security_code_rotated,
        "processed_by": t.processed_by,
        "notes_id": t.notes_id,
        "notes_en": t.notes_en,
        "created_at": t.created_at,
        "updated_at": t.updated_at,
    }


async def _owner_summary(db, owner_uuid: str | None) -> dict | None:
    if not owner_uuid:
        return None
    c = await CustomerRepository(db).get_by_uuid(owner_uuid)
    if c is None:
        return None
    # No contact PII (email/phone/address) — ownership context is owner-identity only.
    return {"uuid": c.uuid, "full_name": c.full_name, "masked_name": mask_owner_name(c.full_name)}


# ---------- Current ownership + history ----------
@admin_router.get("/gemstone/{gemstone_uuid}")
async def gemstone_ownership(gemstone_uuid: str, admin: Admin = Depends(_READ), db=Depends(get_database)):
    gem = await GemstoneRepository(db).get_by_uuid(gemstone_uuid)
    if gem is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Gemstone not found.")
    transfers, _ = await OwnershipTransferRepository(db).list(
        {"gemstone_id": gemstone_uuid}, page=1, page_size=200, sort_by="created_at", sort_dir=1
    )
    history = [_transfer_view(t) for t in transfers if t.status == TransferStatus.COMPLETED.value]
    return {
        "gemstone_id": gemstone_uuid,
        "gemstone_status": gem.status,
        "current_owner": await _owner_summary(db, gem.active_owner_id),
        "history": history,
        "pending_transfer": next(
            (_transfer_view(t) for t in transfers if t.status == TransferStatus.PENDING.value), None
        ),
    }


@admin_router.post("/assign", status_code=201)
async def assign_owner(body: AssignIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    return await assign_initial_owner(db, admin, body.gemstone_id, body.owner_id)


# ---------- Transfers ----------
@admin_router.get("/transfers")
async def list_transfers(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    gemstone_id: str | None = None,
    admin: Admin = Depends(_READ),
    db=Depends(get_database),
):
    filters: dict = {}
    if status:
        filters["status"] = status
    if gemstone_id:
        filters["gemstone_id"] = gemstone_id
    items, total = await OwnershipTransferRepository(db).list(filters or None, page=page, page_size=page_size)
    return {"items": [_transfer_view(t) for t in items], "total": total, "page": page, "page_size": page_size}


@admin_router.get("/transfers/{uuid}")
async def get_transfer(uuid: str, admin: Admin = Depends(_READ), db=Depends(get_database)):
    t = await OwnershipTransferRepository(db).get_by_uuid(uuid)
    if t is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Transfer not found.")
    return _transfer_view(t)


@admin_router.post("/transfers", status_code=201)
async def create_transfer(body: TransferIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    repo = OwnershipTransferRepository(db)
    gem = await GemstoneRepository(db).get_by_uuid(body.gemstone_id)
    if gem is None:
        raise ApiError(400, ErrorCode.BAD_REQUEST, "Referenced gemstone not found.")
    if await CustomerRepository(db).get_by_uuid(body.new_owner_id) is None:
        raise ApiError(400, ErrorCode.BAD_REQUEST, "Recipient (customer) not found.")
    if gem.active_owner_id and body.new_owner_id == gem.active_owner_id:
        raise ApiError(400, ErrorCode.BAD_REQUEST, "New owner must differ from the current owner.")
    # Only one pending transfer per gemstone at a time (BUSINESS_RULES §5).
    if await repo.get_pending_for_gemstone(body.gemstone_id) is not None:
        raise ApiError(409, ErrorCode.CONFLICT, "A pending transfer already exists for this gemstone.")

    tr = OwnershipTransfer(
        gemstone_id=body.gemstone_id,
        new_owner_id=body.new_owner_id,
        previous_owner_id=gem.active_owner_id,
        transfer_date=body.transfer_date,
        status=TransferStatus.PENDING,
        proof_media_id=body.proof_media_id,
        notes_id=body.notes_id,
        notes_en=body.notes_en,
        created_by=admin.uuid,
        updated_by=admin.uuid,
    )
    saved = await repo.create(tr)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="ownership_transfer", entity_id=saved.uuid,
        after={"gemstone_id": saved.gemstone_id, "new_owner_id": saved.new_owner_id, "status": "pending"},
    )
    return _transfer_view(saved)


@admin_router.put("/transfers/{uuid}")
async def update_transfer(uuid: str, body: TransferPatch, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    repo = OwnershipTransferRepository(db)
    tr = await repo.get_by_uuid(uuid)
    if tr is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Transfer not found.")
    if tr.status != TransferStatus.PENDING.value:
        raise ApiError(409, ErrorCode.CONFLICT, "Only a pending transfer can be edited.")
    changes = {k: v for k, v in body.model_dump(exclude_unset=True).items()}
    if changes.get("new_owner_id") and await CustomerRepository(db).get_by_uuid(changes["new_owner_id"]) is None:
        raise ApiError(400, ErrorCode.BAD_REQUEST, "Recipient (customer) not found.")
    changes["updated_by"] = admin.uuid
    changes["updated_at"] = utcnow_iso()
    await repo.update_one({"uuid": uuid}, changes)
    return _transfer_view(await repo.get_by_uuid(uuid))


@admin_router.post("/transfers/{uuid}/complete")
async def complete(uuid: str, request: Request, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    return await complete_transfer(db, admin, uuid, request=request)


@admin_router.post("/transfers/{uuid}/cancel")
async def cancel(uuid: str, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    return await cancel_transfer(db, admin, uuid)
