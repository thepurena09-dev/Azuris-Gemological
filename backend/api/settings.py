"""Business settings endpoints — FASE 2 + POST-BATCH D CMS visual controls.

Public: GET /api/settings/public (WhatsApp contact + CMS visual settings).
Admin (contact): GET/PUT /api/admin/settings (RBAC: SUPER_ADMIN + ADMINISTRATOR).
Admin (CMS visuals): GET/PUT /api/admin/settings/visuals (RBAC permission CMS_READ /
CMS_WRITE — so CONTENT_MANAGER may manage presentation visuals; CUSTOMER_SERVICE
read-only). Single source of truth. All mutations audited.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.audit import write_audit_log
from auth.rbac import Permission, require_permission, require_roles
from db.mongodb import get_database
from models.enums import AdminRole, AuditAction
from models.people import Admin
from repositories.legality import SettingsRepository
from services.whatsapp import InvalidWhatsAppNumber, normalize_whatsapp

public_router = APIRouter(prefix="/settings", tags=["settings"])
admin_router = APIRouter(prefix="/admin/settings", tags=["settings-admin"])
_ADMIN = require_roles(AdminRole.ADMINISTRATOR)
_CMS_READ = require_permission(Permission.CMS_READ)
_CMS_WRITE = require_permission(Permission.CMS_WRITE)


class SettingsUpdate(BaseModel):
    whatsapp_number: str | None = None
    whatsapp_label: str | None = None
    whatsapp_enabled: bool | None = None


class VisualsUpdate(BaseModel):
    login_image_url: str | None = None
    login_image_alt_id: str | None = None
    login_image_alt_en: str | None = None
    process_image_url: str | None = None
    process_image_alt_id: str | None = None
    process_image_alt_en: str | None = None
    process_image_show: bool | None = None
    membership_show: bool | None = None
    membership_title_id: str | None = None
    membership_title_en: str | None = None
    membership_desc_id: str | None = None
    membership_desc_en: str | None = None
    membership_cta_id: str | None = None
    membership_cta_en: str | None = None
    membership_link: str | None = None


def _contact(s) -> dict:
    return {
        "whatsapp_number": s.whatsapp_number,
        "whatsapp_label": s.whatsapp_label,
        "whatsapp_enabled": s.whatsapp_enabled,
    }


def _visuals(s) -> dict:
    return {
        "login_image_url": s.login_image_url,
        "login_image_alt_id": s.login_image_alt_id,
        "login_image_alt_en": s.login_image_alt_en,
        "process_image_url": s.process_image_url,
        "process_image_alt_id": s.process_image_alt_id,
        "process_image_alt_en": s.process_image_alt_en,
        "process_image_show": s.process_image_show,
        "membership_show": s.membership_show,
        "membership_title_id": s.membership_title_id,
        "membership_title_en": s.membership_title_en,
        "membership_desc_id": s.membership_desc_id,
        "membership_desc_en": s.membership_desc_en,
        "membership_cta_id": s.membership_cta_id,
        "membership_cta_en": s.membership_cta_en,
        "membership_link": s.membership_link,
    }


def _public(s) -> dict:
    return {**_contact(s), **_visuals(s)}


@public_router.get("/public")
async def get_public_settings(db=Depends(get_database)):
    s = await SettingsRepository(db).get_or_create()
    return _public(s)


@admin_router.get("")
async def admin_get_settings(admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    s = await SettingsRepository(db).get_or_create()
    return _contact(s)


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
        before=_contact(before), after=_contact(after),
    )
    return _contact(after)


@admin_router.get("/visuals")
async def admin_get_visuals(admin: Admin = Depends(_CMS_READ), db=Depends(get_database)):
    s = await SettingsRepository(db).get_or_create()
    return _visuals(s)


@admin_router.put("/visuals")
async def admin_update_visuals(
    body: VisualsUpdate, admin: Admin = Depends(_CMS_WRITE), db=Depends(get_database)
):
    repo = SettingsRepository(db)
    before = await repo.get_or_create()
    changes = {k: v for k, v in body.model_dump(exclude_unset=True).items()}
    if not changes:
        return _visuals(before)
    after = await repo.update_business(changes)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="cms_visuals", entity_id="business",
        before=_visuals(before), after=_visuals(after),
    )
    return _visuals(after)
