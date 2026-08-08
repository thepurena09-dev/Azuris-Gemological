"""Membership Card endpoints — BATCH C, Sprint 23A.

The Azuris Membership Card is a premium member IDENTITY artifact (NOT a payment /
banking / loyalty card). REUSE-FIRST: reuses the Sprint 4 `MembershipCard` model
(versioning spine), Sprint 5 `MembershipCardRepository`, locked owner masking,
audit writer, RBAC, and the Sprint 8 envelope.

Dependency chain honored: a card requires an existing Customer WITH recorded
consent (BUSINESS_RULES_LOCK §7). Card shows MASKED identity only — no PII, no
contact details, no secrets. `card_number` (Member ID) is unique, immutable, and
DISTINCT from any certificate number.

Member ID format is a PROVISIONAL operational default `AZR-MEM-{SEQ6}-{YY}`
(documented in the PRD ledger, NOT written into BUSINESS_RULES_LOCK). It uses a
separate counter — the certificate counter is never touched.

RBAC (locked matrix): read=MEMBERSHIP_READ, write=MEMBERSHIP_WRITE.
Public: token-gated verification + QR (member-safe, anti-enumeration).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel

from auth.audit import write_audit_log
from auth.rbac import Permission, require_permission
from db.mongodb import get_database
from errors import ApiError, ErrorCode
from models.base import utcnow_iso
from models.documents import MembershipCard
from models.enums import AuditAction, MembershipCardStatus
from models.people import Admin
from repositories.counter import CounterRepository
from repositories.documents import MembershipCardRepository
from repositories.people import CustomerRepository
from services.issuance import PUBLIC_BASE_URL
from services.membership import (
    create_membership_token,
    decode_membership_token,
    render_membership_qr_png,
)
from services.verification import mask_owner_name

admin_router = APIRouter(prefix="/admin/membership", tags=["membership-admin"])
public_router = APIRouter(prefix="/membership", tags=["membership-public"])

_READ = require_permission(Permission.MEMBERSHIP_READ)
_WRITE = require_permission(Permission.MEMBERSHIP_WRITE)


class MembershipIn(BaseModel):
    customer_id: str


class StatusIn(BaseModel):
    status: MembershipCardStatus


def _verify_url(token: str) -> str:
    return f"{PUBLIC_BASE_URL}/membership?t={token}"


def _view(card: MembershipCard, *, with_token: bool = False) -> dict:
    out = {
        "uuid": card.uuid,
        "card_number": card.card_number,
        "customer_id": card.customer_id,
        "masked_name": card.masked_name,
        "status": card.status,
        "version": card.version,
        "is_current": card.is_current,
        "member_since": (card.created_at or "")[:10] or None,
        "created_at": card.created_at,
        "updated_at": card.updated_at,
    }
    if with_token:
        token = create_membership_token(card.uuid, card.version)
        out["verify_token"] = token
        out["verify_url"] = _verify_url(token)
        out["qr_url"] = f"/api/membership/qr?t={token}"
    return out


def _not_found() -> ApiError:
    return ApiError(404, ErrorCode.NOT_FOUND, "Membership card not found.")


# ---------- Admin ----------
@admin_router.get("")
async def list_cards(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    customer_id: str | None = None,
    current_only: bool = False,
    admin: Admin = Depends(_READ),
    db=Depends(get_database),
):
    filters: dict = {}
    if status:
        filters["status"] = status
    if customer_id:
        filters["customer_id"] = customer_id
    if current_only:
        filters["is_current"] = True
    items, total = await MembershipCardRepository(db).list(filters or None, page=page, page_size=page_size)
    return {"items": [_view(c) for c in items], "total": total, "page": page, "page_size": page_size}


@admin_router.get("/{uuid}")
async def get_card(uuid: str, admin: Admin = Depends(_READ), db=Depends(get_database)):
    card = await MembershipCardRepository(db).get_by_uuid(uuid)
    if card is None:
        raise _not_found()
    return _view(card, with_token=True)


@admin_router.post("", status_code=201)
async def create_card(body: MembershipIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    customer = await CustomerRepository(db).get_by_uuid(body.customer_id)
    if customer is None:
        raise ApiError(400, ErrorCode.BAD_REQUEST, "Customer not found.")
    if not customer.privacy_consent:
        raise ApiError(400, ErrorCode.BAD_REQUEST, "Customer consent is required before issuing a membership card.")
    repo = MembershipCardRepository(db)
    if await repo.get_current_for_customer(body.customer_id) is not None:
        raise ApiError(409, ErrorCode.CONFLICT, "Customer already has an active membership card.")

    number = await CounterRepository(db).next_membership_number()
    card = MembershipCard(
        card_number=number,
        customer_id=body.customer_id,
        masked_name=mask_owner_name(customer.full_name) or customer.full_name,
        status=MembershipCardStatus.ACTIVE,
        version=1,
        is_current=True,
        created_version_by=admin.uuid,
        created_by=admin.uuid,
        updated_by=admin.uuid,
    )
    saved = await repo.create(card)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="membership_card", entity_id=saved.uuid,
        after={"card_number": number, "customer_id": saved.customer_id, "status": "active"},
    )
    return _view(saved, with_token=True)


@admin_router.post("/{uuid}/reissue")
async def reissue_card(uuid: str, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    repo = MembershipCardRepository(db)
    old = await repo.get_by_uuid(uuid)
    if old is None:
        raise _not_found()
    customer = await CustomerRepository(db).get_by_uuid(old.customer_id)
    masked = mask_owner_name(customer.full_name) if customer else old.masked_name
    await repo.update_one({"uuid": old.uuid}, {"is_current": False})
    new = MembershipCard(
        card_number=old.card_number,
        customer_id=old.customer_id,
        masked_name=masked or old.masked_name,
        status=MembershipCardStatus.ACTIVE,
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
        entity_type="membership_card", entity_id=saved.uuid,
        after={"card_number": old.card_number, "version": new.version},
    )
    return _view(saved, with_token=True)


@admin_router.post("/{uuid}/status")
async def set_status(uuid: str, body: StatusIn, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    repo = MembershipCardRepository(db)
    card = await repo.get_by_uuid(uuid)
    if card is None:
        raise _not_found()
    target = body.status.value if hasattr(body.status, "value") else str(body.status)
    await repo.update_one({"uuid": uuid}, {"status": target, "updated_by": admin.uuid, "updated_at": utcnow_iso()})
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="membership_card", entity_id=uuid, before={"status": card.status}, after={"status": target},
    )
    return _view(await repo.get_by_uuid(uuid))


@admin_router.delete("/{uuid}")
async def delete_card(uuid: str, admin: Admin = Depends(_WRITE), db=Depends(get_database)):
    repo = MembershipCardRepository(db)
    card = await repo.get_by_uuid(uuid)
    if card is None:
        raise _not_found()
    await repo.soft_delete_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.DELETE,
        entity_type="membership_card", entity_id=uuid, before={"card_number": card.card_number},
    )
    return {"deleted": True}


# ---------- Public (token-gated, member-safe, anti-enumeration) ----------
@public_router.get("/verify")
async def verify_membership(t: str, db=Depends(get_database)):
    data = decode_membership_token(t.strip())
    if data is None:
        return {"valid": False}
    card = await MembershipCardRepository(db).get_by_uuid(data["sub"])
    if card is None or not card.is_current:
        return {"valid": False}
    active = card.status == MembershipCardStatus.ACTIVE.value
    return {
        "valid": active,
        "status": card.status,
        "member_id": card.card_number,
        "member_name": card.masked_name,
        "member_since": (card.created_at or "")[:10] or None,
    }


@public_router.get("/qr")
async def membership_qr(t: str, db=Depends(get_database)):
    data = decode_membership_token(t.strip())
    if data is None:
        return Response(status_code=404)
    try:
        png = render_membership_qr_png(_verify_url(t.strip()))
    except Exception:
        return Response(status_code=503)
    return Response(content=png, media_type="image/png", headers={"Cache-Control": "public, max-age=900"})
