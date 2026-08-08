"""Business settings endpoints — FASE 2 + POST-BATCH D CMS visual controls.

Public: GET /api/settings/public (WhatsApp contact + CMS visual settings).
Admin (contact): GET/PUT /api/admin/settings (RBAC: SUPER_ADMIN + ADMINISTRATOR).
Admin (CMS visuals): GET/PUT /api/admin/settings/visuals (RBAC permission CMS_READ /
CMS_WRITE — so CONTENT_MANAGER may manage presentation visuals; CUSTOMER_SERVICE
read-only). Single source of truth. All mutations audited.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response as _Response  # noqa: F401 (kept for parity)
from pydantic import BaseModel

from auth.audit import write_audit_log
from auth.rbac import Permission, require_permission, require_roles
from db.mongodb import get_database
from errors import ApiError, ErrorCode
from models.enums import AdminRole, AuditAction, MediaEntityType, MediaRole, MediaVisibility
from models.people import Admin
from repositories.legality import SettingsRepository
from repositories.media import MediaRepository
from services.media import MAX_MEDIA_BYTES, store_media
from services.whatsapp import InvalidWhatsAppNumber, normalize_whatsapp

# CMS visual images: images only (no PDF), reuse Sprint 10 storage pipeline.
_CMS_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

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
    dashboard_bg_enabled: bool | None = None
    dashboard_bg_url: str | None = None
    dashboard_bg_opacity: int | None = None
    dashboard_bg_fit: str | None = None
    dashboard_bg_blur: int | None = None
    login_bg_enabled: bool | None = None
    login_bg_url: str | None = None
    login_bg_opacity: int | None = None
    login_bg_fit: str | None = None
    login_bg_blur: int | None = None


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
        "dashboard_bg_enabled": s.dashboard_bg_enabled,
        "dashboard_bg_url": s.dashboard_bg_url,
        "dashboard_bg_opacity": s.dashboard_bg_opacity,
        "dashboard_bg_fit": s.dashboard_bg_fit,
        "dashboard_bg_blur": s.dashboard_bg_blur,
        "login_bg_enabled": s.login_bg_enabled,
        "login_bg_url": s.login_bg_url,
        "login_bg_opacity": s.login_bg_opacity,
        "login_bg_fit": s.login_bg_fit,
        "login_bg_blur": s.login_bg_blur,
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
    # Keep background appearance controls within readability-safe ranges.
    for pre in ("dashboard_bg", "login_bg"):
        ok, bk, fk = f"{pre}_opacity", f"{pre}_blur", f"{pre}_fit"
        if changes.get(ok) is not None:
            changes[ok] = max(4, min(24, int(changes[ok])))
        if changes.get(bk) is not None:
            changes[bk] = max(0, min(12, int(changes[bk])))
        if changes.get(fk) is not None and changes[fk] not in ("cover", "center"):
            changes[fk] = "cover"
    if not changes:
        return _visuals(before)
    after = await repo.update_business(changes)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="cms_visuals", entity_id="business",
        before=_visuals(before), after=_visuals(after),
    )
    return _visuals(after)


# ---------- CMS visual images (reuses Sprint 10 media/storage; CMS-scoped) ----------
@admin_router.get("/visuals/media")
async def admin_list_visual_media(
    admin: Admin = Depends(_CMS_READ), db=Depends(get_database)
):
    """List CMS-scoped images for the visual picker (reuses `media` collection)."""
    items, _ = await MediaRepository(db).list(
        {"entity_type": MediaEntityType.CMS.value}, page=1, page_size=200
    )
    return {
        "items": [
            {
                "uuid": m.uuid,
                "url": m.original_url,
                "mime_type": m.mime_type,
                "width": m.width,
                "height": m.height,
                "alt_text_id": m.alt_text_id,
                "alt_text_en": m.alt_text_en,
                "created_at": m.created_at,
            }
            for m in items
        ]
    }


@admin_router.post("/visuals/media", status_code=status.HTTP_201_CREATED)
async def admin_upload_visual_media(
    file: UploadFile = File(...),
    alt_text_id: str | None = Form(None),
    alt_text_en: str | None = Form(None),
    admin: Admin = Depends(_CMS_WRITE),
    db=Depends(get_database),
):
    """Upload a CMS visual image from the Admin (JPG/PNG/WebP). Reuses store_media."""
    if file.content_type not in _CMS_IMAGE_TYPES:
        raise ApiError(
            status.HTTP_400_BAD_REQUEST, ErrorCode.BAD_REQUEST,
            "Unsupported image type. Use JPG, PNG, or WebP.",
        )
    raw = await file.read()
    if not raw or len(raw) > MAX_MEDIA_BYTES:
        raise ApiError(
            status.HTTP_400_BAD_REQUEST, ErrorCode.BAD_REQUEST,
            "File is empty or too large.",
        )
    media = await store_media(
        db,
        entity_type=MediaEntityType.CMS,
        entity_id="site",
        role=MediaRole.GALLERY,
        visibility=MediaVisibility.PUBLIC,
        filename=file.filename or "cms-image",
        content_type=file.content_type,
        data=raw,
        alt_text_id=alt_text_id,
        alt_text_en=alt_text_en,
        actor_id=admin.uuid,
    )
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="cms_media", entity_id=media.uuid,
        after={"entity_type": "cms", "mime_type": media.mime_type},
    )
    return {"uuid": media.uuid, "url": media.original_url, "mime_type": media.mime_type}
