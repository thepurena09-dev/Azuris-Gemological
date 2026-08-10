"""Legality CMS endpoints — FASE 2.

Public: GET /api/legality (published only), GET /api/legality/document/{uuid}.
Admin: /api/admin/legality CRUD + publish/unpublish + document upload.
RBAC enforced server-side (SUPER_ADMIN + ADMINISTRATOR mutate). All mutations
are audited (append-only). No fake data is created.
"""

import base64

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from auth.audit import write_audit_log
from auth.rbac import require_roles
from db.mongodb import get_database
from models.base import utcnow_iso
from models.enums import AdminRole, AuditAction
from models.legality import LegalityCredential, LegalityDocument
from models.people import Admin
from repositories.legality import LegalityDocumentRepository, LegalityRepository

public_router = APIRouter(prefix="/legality", tags=["legality"])
admin_router = APIRouter(prefix="/admin/legality", tags=["legality-admin"])

MAX_DOC_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
SIGNATURE_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_SIGNATURE_BYTES = 5 * 1024 * 1024
_ADMIN = require_roles(AdminRole.ADMINISTRATOR)  # SUPER_ADMIN implicitly allowed


async def _ensure_single_active(repo, keep_uuid: str) -> None:
    """Only one legality record may be active for new certificates at a time."""
    others, _ = await repo.list(page=1, page_size=100)
    for o in others:
        if o.uuid != keep_uuid and o.active_for_certificates:
            await repo.update_one({"uuid": o.uuid}, {"active_for_certificates": False})


def _public_view(rec: LegalityCredential) -> dict:
    data = {
        "certificate_name": rec.certificate_name,
        "holder_name": rec.holder_name,
        "certificate_number": rec.certificate_number,
        "issuer": rec.issuer,
        "issue_date": rec.issue_date,
        "expiry_date": rec.expiry_date,
        "status": rec.status,
        "short_description": rec.short_description,
        "public_download_allowed": rec.public_download_allowed,
        "updated_at": rec.updated_at,
    }
    if rec.document_id:
        data["document_url"] = f"/api/legality/document/{rec.document_id}"
        data["document_content_type"] = rec.document_content_type
    return {k: v for k, v in data.items() if v is not None}


def _admin_view(rec: LegalityCredential) -> dict:
    view = _public_view(rec)
    view.update(
        {
            "uuid": rec.uuid,
            "publication_status": rec.publication_status,
            "published_at": rec.published_at,
            "document_id": rec.document_id,
            "document_filename": rec.document_filename,
            "signatory_name": rec.signatory_name,
            "signatory_position": rec.signatory_position,
            "signature_document_id": rec.signature_document_id,
            "active_for_certificates": rec.active_for_certificates,
        }
    )
    if rec.signature_document_id:
        view["signature_url"] = f"/api/admin/legality/{rec.uuid}/signature"
    view = {k: v for k, v in view.items() if v is not None}
    # booleans must survive the None-filter
    view["active_for_certificates"] = bool(rec.active_for_certificates)
    return view


# ---------- PUBLIC ----------
@public_router.get("")
async def get_public_legality(db=Depends(get_database)):
    rec = await LegalityRepository(db).get_published()
    if rec is None:
        return {"published": False}
    return {"published": True, "credential": _public_view(rec)}


@public_router.get("/document/{doc_uuid}")
async def get_legality_document(doc_uuid: str, db=Depends(get_database)):
    published = await LegalityRepository(db).get_published()
    if published is None or published.document_id != doc_uuid:
        raise HTTPException(status_code=404, detail="Not found")
    doc = await LegalityDocumentRepository(db).get_by_uuid(doc_uuid)
    if doc is None:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(content=base64.b64decode(doc.data_b64), media_type=doc.content_type)


# ---------- ADMIN ----------
class LegalityUpsert(BaseModel):
    certificate_name: str = Field(min_length=1, max_length=200)
    holder_name: str | None = None
    certificate_number: str | None = None
    issuer: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None
    status: str = "aktif"
    short_description: str | None = None
    public_download_allowed: bool = False
    signatory_name: str | None = None
    signatory_position: str | None = None
    active_for_certificates: bool = False


@admin_router.get("")
async def admin_list_legality(admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    repo = LegalityRepository(db)
    items, _ = await repo.list(page=1, page_size=50)
    return {"items": [_admin_view(i) for i in items]}


@admin_router.post("", status_code=status.HTTP_201_CREATED)
async def admin_create_legality(
    body: LegalityUpsert, admin: Admin = Depends(_ADMIN), db=Depends(get_database)
):
    repo = LegalityRepository(db)
    rec = LegalityCredential(**body.model_dump(), created_by=admin.uuid, updated_by=admin.uuid)
    saved = await repo.create(rec)
    if saved.active_for_certificates:
        await _ensure_single_active(repo, saved.uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="legality_credential", entity_id=saved.uuid, after=_admin_view(saved),
    )
    return _admin_view(await repo.get_by_uuid(saved.uuid))


@admin_router.put("/{uuid}")
async def admin_update_legality(
    uuid: str, body: LegalityUpsert, admin: Admin = Depends(_ADMIN), db=Depends(get_database)
):
    repo = LegalityRepository(db)
    before = await repo.get_by_uuid(uuid)
    if before is None:
        raise HTTPException(status_code=404, detail="Not found")
    changes = {**body.model_dump(), "updated_by": admin.uuid, "updated_at": utcnow_iso()}
    await repo.update_one({"uuid": uuid}, changes)
    if body.active_for_certificates:
        await _ensure_single_active(repo, uuid)
    after = await repo.get_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="legality_credential", entity_id=uuid,
        before=_admin_view(before), after=_admin_view(after),
    )
    return _admin_view(after)


@admin_router.post("/{uuid}/publish")
async def admin_publish(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    repo = LegalityRepository(db)
    rec = await repo.get_by_uuid(uuid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Not found")
    # Single published credential: unpublish others first.
    others, _ = await repo.list(page=1, page_size=50)
    for o in others:
        if o.uuid != uuid and o.publication_status == "published":
            await repo.update_one({"uuid": o.uuid}, {"publication_status": "draft"})
    await repo.update_one(
        {"uuid": uuid},
        {"publication_status": "published", "published_at": utcnow_iso(), "updated_by": admin.uuid},
    )
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="legality_credential", entity_id=uuid, after={"publication_status": "published"},
    )
    return _admin_view(await repo.get_by_uuid(uuid))


@admin_router.post("/{uuid}/unpublish")
async def admin_unpublish(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    repo = LegalityRepository(db)
    rec = await repo.get_by_uuid(uuid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Not found")
    await repo.update_one({"uuid": uuid}, {"publication_status": "draft", "updated_by": admin.uuid})
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="legality_credential", entity_id=uuid, after={"publication_status": "draft"},
    )
    return _admin_view(await repo.get_by_uuid(uuid))


@admin_router.delete("/{uuid}")
async def admin_delete(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    repo = LegalityRepository(db)
    rec = await repo.get_by_uuid(uuid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Not found")
    await repo.soft_delete_by_uuid(uuid)
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.DELETE,
        entity_type="legality_credential", entity_id=uuid, before=_admin_view(rec),
    )
    return {"success": True}


@admin_router.post("/{uuid}/document")
async def admin_upload_document(
    uuid: str, file: UploadFile = File(...), admin: Admin = Depends(_ADMIN), db=Depends(get_database)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    raw = await file.read()
    if len(raw) == 0 or len(raw) > MAX_DOC_BYTES:
        raise HTTPException(status_code=400, detail="File too large or empty")
    repo = LegalityRepository(db)
    rec = await repo.get_by_uuid(uuid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Not found")
    doc = LegalityDocument(
        content_type=file.content_type,
        filename=file.filename or "document",
        size=len(raw),
        data_b64=base64.b64encode(raw).decode("ascii"),
    )
    saved = await LegalityDocumentRepository(db).create(doc)
    await repo.update_one(
        {"uuid": uuid},
        {
            "document_id": saved.uuid,
            "document_filename": doc.filename,
            "document_content_type": doc.content_type,
            "updated_by": admin.uuid,
            "updated_at": utcnow_iso(),
        },
    )
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="legality_credential", entity_id=uuid, after={"document_id": saved.uuid},
    )
    return {"document_id": saved.uuid, "document_url": f"/api/legality/document/{saved.uuid}"}


@admin_router.post("/{uuid}/signature")
async def admin_upload_signature(
    uuid: str, file: UploadFile = File(...), admin: Admin = Depends(_ADMIN), db=Depends(get_database)
):
    if file.content_type not in SIGNATURE_TYPES:
        raise HTTPException(status_code=400, detail="Signature must be PNG, JPEG, or WebP")
    raw = await file.read()
    if len(raw) == 0 or len(raw) > MAX_SIGNATURE_BYTES:
        raise HTTPException(status_code=400, detail="Signature file too large or empty")
    repo = LegalityRepository(db)
    rec = await repo.get_by_uuid(uuid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Not found")
    # Immutable copy: always create a NEW document (never overwrite an old one so
    # already-issued certificate snapshots keep resolving to a stable image).
    doc = LegalityDocument(
        content_type=file.content_type,
        filename=file.filename or "signature",
        size=len(raw),
        data_b64=base64.b64encode(raw).decode("ascii"),
    )
    saved = await LegalityDocumentRepository(db).create(doc)
    await repo.update_one(
        {"uuid": uuid},
        {"signature_document_id": saved.uuid, "updated_by": admin.uuid, "updated_at": utcnow_iso()},
    )
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="legality_credential", entity_id=uuid, after={"signature_document_id": saved.uuid},
    )
    return {"signature_document_id": saved.uuid, "signature_url": f"/api/admin/legality/{uuid}/signature"}


@admin_router.get("/{uuid}/signature")
async def admin_get_signature(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    rec = await LegalityRepository(db).get_by_uuid(uuid)
    if rec is None or not rec.signature_document_id:
        raise HTTPException(status_code=404, detail="Not found")
    doc = await LegalityDocumentRepository(db).get_by_uuid(rec.signature_document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(content=base64.b64decode(doc.data_b64), media_type=doc.content_type)


@admin_router.delete("/{uuid}/signature")
async def admin_remove_signature(uuid: str, admin: Admin = Depends(_ADMIN), db=Depends(get_database)):
    repo = LegalityRepository(db)
    rec = await repo.get_by_uuid(uuid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Not found")
    # Detach only (keep the stored image immutable for any issued snapshots).
    await repo.update_one({"uuid": uuid}, {"signature_document_id": None, "updated_by": admin.uuid})
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.UPDATE,
        entity_type="legality_credential", entity_id=uuid, after={"signature_document_id": None},
    )
    return {"success": True}
