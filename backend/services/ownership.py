"""Ownership workflow service — BATCH C, Sprints 20-22 (Post-Certification).

Two authoritative operations that MUTATE gemstone ownership:
- `assign_initial_owner`: sets the FIRST owner of an unowned gemstone (no prior
  owner). Changing an existing owner is NOT allowed here — it must go through a
  transfer (BUSINESS_RULES_LOCK §5 keeps ownership auditable & non-destructive).
- `complete_transfer`: the ONLY path that changes an existing owner. Records
  previous/new owner, sets gemstone status=transferred + active_owner_id, ROTATES
  the security code (QR/token stays stable), and appends to owner history.

Ownership history is append-only: it is the ordered set of completed transfers
plus the audit trail. No historical owner is ever overwritten without a trace.
"""

from __future__ import annotations

from fastapi import HTTPException

from auth.audit import write_audit_log
from auth.security_logs import write_security_log
from models.base import utcnow_iso
from models.enums import AuditAction, GemstoneStatus, SecurityEventType, TransferStatus
from repositories.catalog import GemstoneRepository
from repositories.ownership import OwnershipTransferRepository, VerificationTokenRepository
from repositories.people import CustomerRepository
from services.security import gen_security_code


async def _add_owned(db, customer_uuid: str, gemstone_uuid: str) -> None:
    repo = CustomerRepository(db)
    cust = await repo.get_by_uuid(customer_uuid)
    if cust is None:
        return
    owned = list(cust.owned_gemstone_ids or [])
    if gemstone_uuid not in owned:
        owned.append(gemstone_uuid)
        await repo.update_one({"uuid": customer_uuid}, {"owned_gemstone_ids": owned, "updated_at": utcnow_iso()})


async def assign_initial_owner(db, admin, gemstone_uuid: str, owner_uuid: str) -> dict:
    gem = await GemstoneRepository(db).get_by_uuid(gemstone_uuid)
    if gem is None:
        raise HTTPException(status_code=404, detail="Gemstone not found")
    if gem.active_owner_id:
        raise HTTPException(status_code=409, detail="Gemstone already has an owner (use a transfer)")
    owner = await CustomerRepository(db).get_by_uuid(owner_uuid)
    if owner is None:
        raise HTTPException(status_code=400, detail="Owner (customer) not found")

    await GemstoneRepository(db).update_one(
        {"uuid": gemstone_uuid}, {"active_owner_id": owner_uuid, "updated_by": admin.uuid, "updated_at": utcnow_iso()}
    )
    await _add_owned(db, owner_uuid, gemstone_uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="gemstone", entity_id=gemstone_uuid,
        before={"active_owner_id": None}, after={"active_owner_id": owner_uuid, "event": "initial_ownership"},
    )
    return {"gemstone_id": gemstone_uuid, "active_owner_id": owner_uuid}


async def complete_transfer(db, admin, transfer_uuid: str, request=None) -> dict:
    repo = OwnershipTransferRepository(db)
    tr = await repo.get_by_uuid(transfer_uuid)
    if tr is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    if tr.status != TransferStatus.PENDING.value:
        raise HTTPException(status_code=409, detail="Only a pending transfer can be completed")

    gem = await GemstoneRepository(db).get_by_uuid(tr.gemstone_id)
    if gem is None:
        raise HTTPException(status_code=404, detail="Gemstone not found")
    if await CustomerRepository(db).get_by_uuid(tr.new_owner_id) is None:
        raise HTTPException(status_code=400, detail="New owner (customer) not found")

    previous_owner = gem.active_owner_id
    now = utcnow_iso()

    # Rotate the security code (QR/token stays stable). Code regeneration logged.
    new_code = gen_security_code()
    vt = await VerificationTokenRepository(db).get_active_for_gemstone(tr.gemstone_id)
    if vt is not None:
        await VerificationTokenRepository(db).update_one(
            {"uuid": vt.uuid}, {"security_code": new_code, "rotated_at": now}
        )
        await write_security_log(
            db, SecurityEventType.SECURITY_CODE_REGENERATION, request=request,
            actor_id=admin.uuid, success=True, detail="ownership_transfer_completed",
        )

    # Complete the transfer record (immutable once completed).
    await repo.update_one(
        {"uuid": transfer_uuid},
        {
            "status": TransferStatus.COMPLETED.value,
            "previous_owner_id": previous_owner,
            "transfer_date": tr.transfer_date or now,
            "security_code_rotated": vt is not None,
            "processed_by": admin.uuid,
            "updated_by": admin.uuid,
            "updated_at": now,
        },
    )
    # Mutate gemstone ownership (only completion does this).
    await GemstoneRepository(db).update_one(
        {"uuid": tr.gemstone_id},
        {"active_owner_id": tr.new_owner_id, "status": GemstoneStatus.TRANSFERRED.value, "updated_by": admin.uuid, "updated_at": now},
    )
    await _add_owned(db, tr.new_owner_id, tr.gemstone_id)

    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="ownership_transfer", entity_id=transfer_uuid,
        before={"status": "pending", "owner": previous_owner},
        after={"status": "completed", "owner": tr.new_owner_id, "security_code_rotated": vt is not None},
    )
    return {
        "transfer_uuid": transfer_uuid,
        "status": "completed",
        "previous_owner_id": previous_owner,
        "new_owner_id": tr.new_owner_id,
        "security_code_rotated": vt is not None,
        "new_security_code": new_code if vt is not None else None,  # shown ONCE
    }


async def cancel_transfer(db, admin, transfer_uuid: str) -> dict:
    repo = OwnershipTransferRepository(db)
    tr = await repo.get_by_uuid(transfer_uuid)
    if tr is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    if tr.status != TransferStatus.PENDING.value:
        raise HTTPException(status_code=409, detail="Only a pending transfer can be cancelled")
    await repo.update_one(
        {"uuid": transfer_uuid},
        {"status": TransferStatus.CANCELLED.value, "processed_by": admin.uuid, "updated_by": admin.uuid, "updated_at": utcnow_iso()},
    )
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="ownership_transfer", entity_id=transfer_uuid,
        before={"status": "pending"}, after={"status": "cancelled"},
    )
    return {"transfer_uuid": transfer_uuid, "status": "cancelled"}
