"""Certificate issuance service — FASE 3.

Orchestrates gemstone -> examination snapshot -> issue certificate with a
server-side atomic number (locked format), security code, and opaque QR token.
Reuses locked counter, existing repos, audit, and verification-token schema.
"""

import os
from typing import Optional

from fastapi import HTTPException

from auth.audit import write_audit_log
from models.base import utcnow_iso
from models.catalog import Gemstone
from models.documents import Certificate
from models.enums import AuditAction, CertificateStatus, GemstoneStatus
from models.ownership import VerificationToken
from repositories.counter import CounterRepository
from repositories.legality import (
    CertificateRepository,
    GemstoneRepository,
    VerificationTokenRepository,
)
from services.security import gen_qr_token, gen_security_code

PUBLIC_BASE_URL = os.environ.get(
    "PUBLIC_BASE_URL", "https://customer-domain-api.preview.emergentagent.com"
).rstrip("/")


def qr_url(token: str) -> str:
    return f"{PUBLIC_BASE_URL}/?qr={token}#verification"


def _snapshot(gem: Gemstone, extra: dict) -> dict:
    photo_id = gem.media_ids[0] if gem.media_ids else None
    snap = {
        "object_type": extra.get("object_type") or gem.category,
        "name": gem.name_en or gem.name_id,
        "name_id": gem.name_id,
        "name_en": gem.name_en,
        "species": gem.gemstone_type,
        "variety": gem.category,
        "carat": gem.weight_carat,
        "dimensions": gem.dimensions_mm,
        "shape": gem.shape,
        "cut": gem.cut,
        "color": gem.color,
        "transparency": extra.get("transparency"),
        "clarity": gem.clarity,
        "treatment": gem.treatment,
        "origin": gem.origin,
        "photo_id": photo_id,
        "examiner": extra.get("examiner"),
        "signatory": extra.get("signatory"),
        "conclusion": extra.get("conclusion"),
        "notes": extra.get("notes"),
    }
    return {k: v for k, v in snap.items() if v is not None}


async def issue_certificate(db, admin, gemstone_uuid: str, extra: dict) -> dict:
    gem_repo = GemstoneRepository(db)
    gem = await gem_repo.get_by_uuid(gemstone_uuid)
    if gem is None:
        raise HTTPException(status_code=404, detail="Gemstone not found")
    if gem.certificate_id:
        raise HTTPException(status_code=409, detail="Gemstone already has a certificate (use reissue)")

    number = await CounterRepository(db).next_certificate_number()
    snapshot = _snapshot(gem, extra)

    cert = Certificate(
        certificate_number=number,
        gemstone_id=gem.uuid,
        status=CertificateStatus.ISSUED,
        version=1,
        is_current=True,
        issued_at=utcnow_iso(),
        issued_by=admin.uuid,
        created_version_by=admin.uuid,
        color_grade=extra.get("color_grade"),
        clarity_grade=extra.get("clarity_grade"),
        cut_grade=extra.get("cut_grade"),
        carat_weight=extra.get("carat_weight") or gem.weight_carat,
        measurements=extra.get("measurements") or gem.dimensions_mm,
        comments_id=extra.get("conclusion"),
        comments_en=extra.get("conclusion"),
        gemstone_snapshot=snapshot,
        created_by=admin.uuid,
        updated_by=admin.uuid,
    )
    saved = await CertificateRepository(db).create(cert)

    token = gen_qr_token()
    code = gen_security_code()
    vt = VerificationToken(
        gemstone_id=gem.uuid,
        certificate_id=saved.uuid,
        token=token,
        security_code=code,
        is_active=True,
        created_by=admin.uuid,
        updated_by=admin.uuid,
    )
    saved_vt = await VerificationTokenRepository(db).create(vt)

    await CertificateRepository(db).update_one(
        {"uuid": saved.uuid}, {"verification_uuid": saved_vt.uuid}
    )
    await gem_repo.update_one(
        {"uuid": gem.uuid},
        {"certificate_id": saved.uuid, "status": GemstoneStatus.VERIFIED.value, "updated_by": admin.uuid},
    )

    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.CREATE,
        entity_type="certificate", entity_id=saved.uuid,
        after={"certificate_number": number, "gemstone_id": gem.uuid, "status": "issued"},
    )
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="gemstone", entity_id=gem.uuid, after={"status": "verified"},
    )

    return {
        "certificate_number": number,
        "certificate_uuid": saved.uuid,
        "version": 1,
        "security_code": code,  # shown ONCE to the issuing admin; never in public API
        "qr_token": token,
        "qr_url": qr_url(token),
    }


async def reissue_certificate(db, admin, cert_uuid: str, extra: dict) -> dict:
    repo = CertificateRepository(db)
    old = await repo.get_by_uuid(cert_uuid)
    if old is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    gem = await GemstoneRepository(db).get_by_uuid(old.gemstone_id)
    if gem is None:
        raise HTTPException(status_code=404, detail="Gemstone not found")

    # Archive current version first (partial-unique index allows only one current
    # per number), then insert the new version. Roll back the flip on failure so a
    # partial error never leaves the certificate without a current version.
    await repo.update_one({"uuid": old.uuid}, {"is_current": False})

    snapshot = _snapshot(gem, extra)
    new = Certificate(
        certificate_number=old.certificate_number,
        gemstone_id=old.gemstone_id,
        status=CertificateStatus.REISSUED,
        version=old.version + 1,
        is_current=True,
        issued_at=utcnow_iso(),
        issued_by=admin.uuid,
        created_version_by=admin.uuid,
        carat_weight=extra.get("carat_weight") or gem.weight_carat,
        measurements=extra.get("measurements") or gem.dimensions_mm,
        comments_id=extra.get("conclusion"),
        comments_en=extra.get("conclusion"),
        gemstone_snapshot=snapshot,
        created_by=admin.uuid,
        updated_by=admin.uuid,
    )
    try:
        saved = await repo.create(new)
    except Exception:
        await repo.update_one({"uuid": old.uuid}, {"is_current": True})
        raise

    # QR persists across versions: repoint the existing active token to the new version.
    if old.verification_uuid:
        await VerificationTokenRepository(db).update_one(
            {"uuid": old.verification_uuid}, {"certificate_id": saved.uuid}
        )
        await repo.update_one({"uuid": saved.uuid}, {"verification_uuid": old.verification_uuid})
    await GemstoneRepository(db).update_one({"uuid": old.gemstone_id}, {"certificate_id": saved.uuid})

    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.VERSION_CREATE,
        entity_type="certificate", entity_id=saved.uuid,
        after={"certificate_number": old.certificate_number, "version": new.version},
    )
    return {"certificate_uuid": saved.uuid, "version": new.version, "certificate_number": old.certificate_number}


async def revoke_certificate(db, admin, cert_uuid: str) -> dict:
    repo = CertificateRepository(db)
    cert = await repo.get_by_uuid(cert_uuid)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    await repo.update_one({"uuid": cert_uuid}, {"status": CertificateStatus.REVOKED.value})
    await write_audit_log(
        db, actor_id=admin.uuid, actor_role=admin.role, action=AuditAction.STATUS_CHANGE,
        entity_type="certificate", entity_id=cert_uuid, after={"status": "revoked"},
    )
    return {"certificate_uuid": cert_uuid, "status": "revoked"}
