"""Admin certificate issuance + gemstone entry endpoints — FASE 3.

RBAC: SUPER_ADMIN + ADMINISTRATOR (server-side). Public gemstone photo endpoint
serves only images referenced by an issued certificate snapshot.
All mutations reuse the existing append-only audit log.
"""

import base64

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from auth.audit import write_audit_log
from auth.rbac import Permission, require_permission, require_roles
from db.mongodb import get_database
from errors import ApiError, ErrorCode
from models.base import utcnow_iso
from models.catalog import Gemstone
from models.enums import AdminRole, AuditAction, GemstoneStatus
from models.legality import LegalityDocument
from models.people import Admin
from repositories.legality import (
    CertificateRepository,
    GemstonePhotoRepository,
    GemstoneRepository,
    SettingsRepository,
    VerificationTokenRepository,
)
from services.certificate_pdf import build_card_pdf, build_certificate_pdf, decode_photo
from services.issuance import PUBLIC_BASE_URL, issue_certificate, qr_url, reissue_certificate, revoke_certificate

admin_router = APIRouter(prefix="/admin", tags=["certificates-admin"])
public_router = APIRouter(prefix="/gemstone", tags=["gemstone-public"])
_ADMIN = require_roles(AdminRole.ADMINISTRATOR)
_GEM_READ = require_permission(Permission.GEMSTONE_READ)
_GEM_WRITE = require_permission(Permission.GEMSTONE_WRITE)
_GEM_DELETE = require_permission(Permission.GEMSTONE_DELETE)

# Locked gemstone lifecycle (BUSINESS_RULES_LOCK §1).
_GEM_TRANSITIONS: dict[str, set[str]] = {
    GemstoneStatus.DRAFT.value: {GemstoneStatus.VERIFIED.value, GemstoneStatus.ARCHIVED.value},
    GemstoneStatus.VERIFIED.value: {GemstoneStatus.PUBLISHED.value, GemstoneStatus.ARCHIVED.value},
    GemstoneStatus.PUBLISHED.value: {GemstoneStatus.TRANSFERRED.value, GemstoneStatus.ARCHIVED.value},
    GemstoneStatus.TRANSFERRED.value: {GemstoneStatus.PUBLISHED.value, GemstoneStatus.ARCHIVED.value},
    GemstoneStatus.ARCHIVED.value: {GemstoneStatus.PUBLISHED.value},
}

MAX_IMG = 8 * 1024 * 1024
IMG_TYPES = {"image/jpeg", "image/png", "image/webp"}


class GemstoneIn(BaseModel):
    name_id: str = Field(min_length=1, max_length=200)
    name_en: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    gemstone_type: str = Field(min_length=1, max_length=100)
    weight_carat: float = Field(gt=0)
    color: str | None = None
    clarity: str | None = None
    cut: str | None = None
    shape: str | None = None
    dimensions_mm: str | None = None
    origin: str | None = None
    treatment: str | None = None


class IssueIn(BaseModel):
    gemstone_id: str
    object_type: str | None = None
    transparency: str | None = None
    examiner: str | None = None
    signatory: str | None = None
    conclusion: str | None = None
    notes: str | None = None
    color_grade: str | None = None
    clarity_grade: str | None = None
    cut_grade: str | None = None
    carat_weight: float | None = None
    measurements: str | None = None


def _gem_view(g: Gemstone) -> dict:
    return {
        "uuid": g.uuid,
        "name_id": g.name_id,
        "name_en": g.name_en,
        "category": g.category,
        "gemstone_type": g.gemstone_type,
        "weight_carat": g.weight_carat,
        "color": g.color,
        "clarity": g.clarity,
        "cut": g.cut,
        "shape": g.shape,
        "dimensions_mm": g.dimensions_mm,
        "origin": g.origin,
        "treatment": g.treatment,
        "status": g.status,
        "certificate_id": g.certificate_id,
        "media_ids": g.media_ids,
        "photo_id": g.media_ids[0] if g.media_ids else None,
    }


# ---------- GEMSTONES ----------
class GemStatusIn(BaseModel):
    status: GemstoneStatus


@admin_router.get("/gemstones")
async def list_gemstones(
    page: int = 1,
    page_size: int = 100,
    status: str | None = None,
    q: str | None = None,
    admin: Admin = Depends(_GEM_READ),
    db=Depends(get_database),
):
    filters: dict = {}
    if status:
        filters["status"] = status
    if q:
        rx = {"$regex": q.strip(), "$options": "i"}
        filters["$or"] = [
            {"name_id": rx}, {"name_en": rx},
            {"gemstone_type": rx}, {"category": rx}, {"origin": rx},
        ]
    items, total = await GemstoneRepository(db).list(filters or None, page=page, page_size=page_size)
    return {"items": [_gem_view(g) for g in items], "total": total, "page": page, "page_size": page_size}


@admin_router.get("/gemstones/{uuid}")
async def get_gemstone(uuid: str, admin: Admin = Depends(_GEM_READ), db=Depends(get_database)):
    g = await GemstoneRepository(db).get_by_uuid(uuid)
    if g is None:
        raise HTTPException(status_code=404, detail="Not found")
    return _gem_view(g)


@admin_router.post("/gemstones", status_code=status.HTTP_201_CREATED)
async def create_gemstone(body: GemstoneIn, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    gem = Gemstone(**body.model_dump(), created_by=admin.uuid, updated_by=admin.uuid)
    saved = await GemstoneRepository(db).create(gem)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="gemstone", entity_id=saved.uuid, after={"name": saved.name_en},
    )
    return _gem_view(saved)


@admin_router.put("/gemstones/{uuid}")
async def update_gemstone(uuid: str, body: GemstoneIn, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    repo = GemstoneRepository(db)
    before = await repo.get_by_uuid(uuid)
    if before is None:
        raise HTTPException(status_code=404, detail="Not found")
    await repo.update_one({"uuid": uuid}, {**body.model_dump(), "updated_by": admin.uuid, "updated_at": utcnow_iso()})
    after = await repo.get_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="gemstone", entity_id=uuid, after=_gem_view(after),
    )
    return _gem_view(after)


@admin_router.post("/gemstones/{uuid}/status")
async def set_gemstone_status(
    uuid: str, body: GemStatusIn, admin: Admin = Depends(_GEM_WRITE), db=Depends(get_database)
):
    repo = GemstoneRepository(db)
    gem = await repo.get_by_uuid(uuid)
    if gem is None:
        raise HTTPException(status_code=404, detail="Not found")
    target = body.status.value if hasattr(body.status, "value") else str(body.status)
    if target != gem.status and target not in _GEM_TRANSITIONS.get(gem.status, set()):
        raise ApiError(409, ErrorCode.CONFLICT, f"Invalid status transition: {gem.status} → {target}.")
    await repo.update_one({"uuid": uuid}, {"status": target, "updated_by": admin.uuid, "updated_at": utcnow_iso()})
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="gemstone", entity_id=uuid, before={"status": gem.status}, after={"status": target},
    )
    return _gem_view(await repo.get_by_uuid(uuid))


@admin_router.delete("/gemstones/{uuid}")
async def delete_gemstone(uuid: str, admin: Admin = Depends(_GEM_DELETE), db=Depends(get_database)):
    repo = GemstoneRepository(db)
    gem = await repo.get_by_uuid(uuid)
    if gem is None:
        raise HTTPException(status_code=404, detail="Not found")
    if gem.certificate_id:
        raise ApiError(409, ErrorCode.CONFLICT, "Gemstone has an issued certificate and cannot be deleted.")
    await repo.soft_delete_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.DELETE,
        entity_type="gemstone", entity_id=uuid, before={"name": gem.name_en},
    )
    return {"deleted": True}


@admin_router.post("/gemstones/{uuid}/photo")
async def upload_photo(uuid: str, file: UploadFile = File(...), admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    if file.content_type not in IMG_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")
    raw = await file.read()
    if not raw or len(raw) > MAX_IMG:
        raise HTTPException(status_code=400, detail="Image too large or empty")
    repo = GemstoneRepository(db)
    gem = await repo.get_by_uuid(uuid)
    if gem is None:
        raise HTTPException(status_code=404, detail="Not found")
    doc = LegalityDocument(
        content_type=file.content_type, filename=file.filename or "photo",
        size=len(raw), data_b64=base64.b64encode(raw).decode("ascii"),
    )
    saved = await GemstonePhotoRepository(db).create(doc)
    # Keep the examination photo at index 0 (the certificate snapshot reads
    # media_ids[0]) while preserving any Sprint-10 media-library links.
    existing = [x for x in (gem.media_ids or []) if x != saved.uuid]
    await repo.update_one({"uuid": uuid}, {"media_ids": [saved.uuid] + existing, "updated_by": admin.uuid})
    return {"photo_id": saved.uuid, "photo_url": f"/api/gemstone/photo/{saved.uuid}"}


# ---------- CERTIFICATES ----------
# DEMO PREVIEW — stateless UI-only certificate design preview. Creates NO
# certificate/gemstone/token, never touches the counter, never reaches Mongo.
_DEMO_SNAP = {
    "name": "Natural Sapphire",
    "object_type": "Loose Gemstone",
    "species": "Corundum",
    "variety": "Sapphire",
    "carat": 2.35,
    "color": "Royal Blue",
    "clarity": "Transparent",
    "transparency": "Transparent",
    "cut": "Oval Mixed Cut",
    "shape": "Oval",
    "dimensions": "8.20 × 6.10 × 4.35 mm",
    "origin": "Demo",
    "treatment": "No indication / Demo",
    "examiner": "AZURIS GEMOLOGICAL",
    "signatory": "Azuris Gemological",
    "conclusion": "Natural Sapphire",
    "photo_id": None,
}


@admin_router.get("/certificates/demo-preview")
async def demo_certificate_preview(admin: Admin = Depends(_ADMIN)):
    cert = {
        "certificate_number": "AZR-GEM-DEMO",
        "issued_at": "",
        "version": 1,
        "gemstone_snapshot": dict(_DEMO_SNAP),
        "qr_url": "DEMO - NOT VALID",
        "website": "azuris-gemological.com",
    }
    pdf = build_certificate_pdf(cert, None, demo=True)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="AZR-GEM-DEMO.pdf"'},
    )


@admin_router.get("/certificates")
async def list_certificates(admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    items, _ = await CertificateRepository(db).list(page=1, page_size=100)
    return {
        "items": [
            {
                "uuid": c.uuid,
                "certificate_number": c.certificate_number,
                "gemstone_id": c.gemstone_id,
                "status": c.status,
                "version": c.version,
                "is_current": c.is_current,
                "issued_at": c.issued_at,
            }
            for c in items
        ]
    }


@admin_router.post("/certificates/issue", status_code=status.HTTP_201_CREATED)
async def issue(body: IssueIn, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    extra = body.model_dump(exclude={"gemstone_id"})
    return await issue_certificate(db, admin, body.gemstone_id, extra)


@admin_router.post("/certificates/{uuid}/reissue")
async def reissue(uuid: str, body: IssueIn, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    extra = body.model_dump(exclude={"gemstone_id"})
    return await reissue_certificate(db, admin, uuid, extra)


@admin_router.post("/certificates/{uuid}/revoke")
async def revoke(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    return await revoke_certificate(db, admin, uuid)


@admin_router.get("/certificates/{uuid}/pdf")
async def certificate_pdf(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    repo = CertificateRepository(db)
    cert = await repo.get_by_uuid(uuid)
    if cert is None:
        raise HTTPException(status_code=404, detail="Not found")
    vt = await VerificationTokenRepository(db).get_by_uuid(cert.verification_uuid) if cert.verification_uuid else None
    token = vt.token if vt else ""
    snap = cert.gemstone_snapshot or {}
    photo_bytes = None
    if snap.get("photo_id"):
        doc = await GemstonePhotoRepository(db).get_by_uuid(snap["photo_id"])
        if doc:
            photo_bytes = decode_photo(doc.data_b64)
    payload = {
        "certificate_number": cert.certificate_number,
        "issued_at": cert.issued_at,
        "version": cert.version,
        "gemstone_snapshot": snap,
        "qr_url": qr_url(token),
    }
    try:
        settings = await SettingsRepository(db).get_or_create()
        if settings and settings.whatsapp_enabled:
            payload["whatsapp"] = settings.whatsapp_number
    except Exception:
        pass
    pdf = build_certificate_pdf(payload, photo_bytes)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="certificate", entity_id=uuid, after={"action": "pdf_generated", "version": cert.version},
    )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{cert.certificate_number}.pdf"'},
    )


@admin_router.get("/certificates/{uuid}/card")
async def certificate_card(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    """Premium AGR certificate card (single printable page, with QR)."""
    repo = CertificateRepository(db)
    cert = await repo.get_by_uuid(uuid)
    if cert is None:
        raise HTTPException(status_code=404, detail="Not found")
    vt = await VerificationTokenRepository(db).get_by_uuid(cert.verification_uuid) if cert.verification_uuid else None
    token = vt.token if vt else ""
    verify_url = f"{PUBLIC_BASE_URL}/verify?t={token}"
    snap = cert.gemstone_snapshot or {}
    photo_bytes = None
    if snap.get("photo_id"):
        doc = await GemstonePhotoRepository(db).get_by_uuid(snap["photo_id"])
        if doc:
            photo_bytes = decode_photo(doc.data_b64)
    payload = {
        "certificate_number": cert.certificate_number,
        "issued_at": cert.issued_at,
        "version": cert.version,
        "gemstone_snapshot": snap,
    }
    pdf = build_card_pdf(payload, photo_bytes, verify_url)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{cert.certificate_number}-card.pdf"'},
    )
@public_router.get("/photo/{doc_uuid}")
async def gemstone_photo(doc_uuid: str, db=Depends(get_database)):
    doc = await GemstonePhotoRepository(db).get_by_uuid(doc_uuid)
    if doc is None:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(content=base64.b64decode(doc.data_b64), media_type=doc.content_type)
