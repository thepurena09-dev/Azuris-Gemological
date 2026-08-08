"""Business settings endpoints — FASE 2.

Public: GET /api/settings/public (WhatsApp business contact).
Admin: GET/PUT /api/admin/settings (RBAC: SUPER_ADMIN + ADMINISTRATOR).
Single source of truth for the WhatsApp CTA number. Mutations audited.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.audit import write_audit_log
from auth.rbac import require_roles
from db.mongodb import get_database
from models.enums import AdminRole, AuditAction
from models.people import Admin
from repositories.legality import SettingsRepository
from services.whatsapp import InvalidWhatsAppNumber, normalize_whatsapp

public_router = APIRouter(prefix="/settings", tags=["settings"])
admin_router = APIRouter(prefix="/admin/settings", tags=["settings-admin"])
_ADMIN = require_roles(AdminRole.ADMINISTRATOR)


class SettingsUpdate(BaseModel):
    whatsapp_number: str | None = None
    whatsapp_label: str | None = None
    whatsapp_enabled: bool | None = None


def _public(s) -> dict:
    return {
        "whatsapp_number": s.whatsapp_number,
        "whatsapp_label": s.whatsapp_label,
        "whatsapp_enabled": s.whatsapp_enabled,
    }


@public_router.get("/public")
async def get_public_settings(db=Depends(get_database)):
    s = await SettingsRepository(db).get_or_create()
    return _public(s)


@admin_router.get("")
async def admin_get_settings(admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    s = await SettingsRepository(db).get_or_create()
    return _public(s)


@admin_router.put("")
async def admin_update_settings(
    body: SettingsUpdate, admin: Admin = Depends(_ADMIN), db=Depends(get_database)
):
    repo = SettingsRepository(db)
    before = await repo.get_or_create()

    changes: dict = {}
    if body.whatsapp_number is not None:
        try:
            changes["whatsapp_number"] = normalize_whatsapp(body.whatsapp_number)
        except InvalidWhatsAppNumber:
            raise HTTPException(status_code=400, detail="Invalid WhatsApp number")
    if body.whatsapp_label is not None:
        changes["whatsapp_label"] = body.whatsapp_label
    if body.whatsapp_enabled is not None:
        changes["whatsapp_enabled"] = body.whatsapp_enabled

    if changes.get("whatsapp_enabled", before.whatsapp_enabled) and not (
        changes.get("whatsapp_number", before.whatsapp_number)
    ):
        raise HTTPException(status_code=400, detail="WhatsApp number required when enabled")

    after = await repo.update_business(changes)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="business_settings", entity_id="business",
        before=_public(before), after=_public(after),
    )
    return _public(after)
