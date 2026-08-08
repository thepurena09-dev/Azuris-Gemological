"""Media management endpoints — Sprint 10.

Admin (RBAC ADMINISTRATOR / SUPER_ADMIN): upload, list, delete, and serve any
media (incl. private). Public: serve PUBLIC media only. Binary bytes are stored
via the object-storage adapter; metadata lives in the `media` collection.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from auth.audit import write_audit_log
from auth.rbac import require_roles
from db.mongodb import get_database
from errors import ApiError, ErrorCode
from models.enums import AdminRole, AuditAction, MediaEntityType, MediaRole, MediaVisibility
from models.media import Media
from models.people import Admin
from repositories.media import MediaRepository
from services.media import (
    ALLOWED_TYPES,
    MAX_MEDIA_BYTES,
    delete_media,
    get_media_binary,
    store_media,
)

admin_router = APIRouter(prefix="/admin/media", tags=["media-admin"])
public_router = APIRouter(prefix="/media", tags=["media-public"])
_ADMIN = require_roles(AdminRole.ADMINISTRATOR)


def _media_view(m: Media) -> dict:
    return {
        "uuid": m.uuid,
        "entity_type": m.entity_type,
        "entity_id": m.entity_id,
        "role": m.role,
        "visibility": m.visibility,
        "mime_type": m.mime_type,
        "size_bytes": m.size_bytes,
        "width": m.width,
        "height": m.height,
        "alt_text_id": m.alt_text_id,
        "alt_text_en": m.alt_text_en,
        "url": m.original_url,
        "created_at": m.created_at,
    }


def _enum_or_400(enum_cls, value, field: str):
    try:
        return enum_cls(value)
    except ValueError:
        raise ApiError(
            status.HTTP_400_BAD_REQUEST,
            ErrorCode.BAD_REQUEST,
            f"Invalid {field}.",
        )


# ---------- ADMIN ----------
@admin_router.post("", status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    entity_type: str = Form(...),
    entity_id: str = Form(...),
    role: str = Form(MediaRole.GALLERY.value),
    visibility: str = Form(MediaVisibility.PUBLIC.value),
    alt_text_id: str | None = Form(None),
    alt_text_en: str | None = Form(None),
    admin: Admin = Depends(_ADMIN),
    db=Depends(get_database),
):
    if file.content_type not in ALLOWED_TYPES:
        raise ApiError(status.HTTP_400_BAD_REQUEST, ErrorCode.BAD_REQUEST, "Unsupported media type.")
    raw = await file.read()
    if not raw or len(raw) > MAX_MEDIA_BYTES:
        raise ApiError(status.HTTP_400_BAD_REQUEST, ErrorCode.BAD_REQUEST, "File is empty or too large.")

    et = _enum_or_400(MediaEntityType, entity_type, "entity_type")
    ro = _enum_or_400(MediaRole, role, "role")
    vis = _enum_or_400(MediaVisibility, visibility, "visibility")

    media = await store_media(
        db,
        entity_type=et,
        entity_id=entity_id,
        role=ro,
        visibility=vis,
        filename=file.filename or "upload",
        content_type=file.content_type,
        data=raw,
        alt_text_id=alt_text_id,
        alt_text_en=alt_text_en,
        actor_id=admin.uuid,
    )
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="media", entity_id=media.uuid,
        after={"entity_type": et.value, "entity_id": entity_id, "role": ro.value, "visibility": vis.value},
    )
    return _media_view(media)


@admin_router.get("")
async def list_media(
    entity_type: str | None = None,
    entity_id: str | None = None,
    admin: Admin = Depends(_ADMIN),
    db=Depends(get_database),
):
    filters: dict = {}
    if entity_type:
        filters["entity_type"] = _enum_or_400(MediaEntityType, entity_type, "entity_type").value
    if entity_id:
        filters["entity_id"] = entity_id
    items, total = await MediaRepository(db).list(filters or None, page=1, page_size=200)
    return {"items": [_media_view(m) for m in items], "total": total}


@admin_router.get("/{uuid}/raw")
async def serve_media_admin(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    media = await MediaRepository(db).get_by_uuid(uuid)
    if media is None:
        raise HTTPException(status_code=404, detail="Not found")
    result = await get_media_binary(db, media)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    data, content_type = result
    return Response(content=data, media_type=content_type)


@admin_router.delete("/{uuid}")
async def remove_media(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    media = await MediaRepository(db).get_by_uuid(uuid)
    if media is None:
        raise HTTPException(status_code=404, detail="Not found")
    await delete_media(db, media)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.DELETE,
        entity_type="media", entity_id=uuid,
    )
    return {"deleted": True}


# ---------- PUBLIC ----------
@public_router.get("/{uuid}")
async def serve_media_public(uuid: str, db=Depends(get_database)):
    media = await MediaRepository(db).get_by_uuid(uuid)
    # Private / missing / soft-deleted all surface as a generic 404 (no leak).
    if media is None or media.visibility == MediaVisibility.PRIVATE.value:
        raise HTTPException(status_code=404, detail="Not found")
    result = await get_media_binary(db, media)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    data, content_type = result
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )
