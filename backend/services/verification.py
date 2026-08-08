"""Public verification service — FASE 2.

Enforces the locked resolution priority QR -> Security Code -> Certificate ->
Gemstone -> Owner, generic non-leaking outcomes, locked owner masking, and
current-version-only public visibility. Secrets are never returned or logged.

NOTE: certificate issuance (data creation) is FASE 3. Until certificates exist,
verification legitimately returns a generic "not found" result — no fake data.
"""

import hashlib
from typing import Any, Optional

from models.enums import VerificationMethod, VerificationResult
from models.logs import VerificationLog
from repositories.legality import (
    CertificateRepository,
    CustomerRepositoryV2,
    GemstoneRepository,
    VerificationTokenRepository,
)
from repositories.logs import VerificationLogRepository


# ---------- locked owner masking ----------
def mask_owner_name(full_name: Optional[str]) -> Optional[str]:
    if not full_name:
        return None
    parts = full_name.split()
    if not parts:
        return None
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ""

    def reveal(token: str, n: int) -> str:
        if len(token) <= n:
            return token
        return token[:n] + "*" * (len(token) - n)

    first_masked = reveal(first, 4)
    if not last:
        return first_masked
    if len(last) <= 3:
        last_masked = last[:1] + "*" * (len(last) - 1)
    else:
        last_masked = last[:3] + "*" * (len(last) - 3)
    return f"{first_masked} {last_masked}"


def _mask_cert_number(number: Optional[str]) -> Optional[str]:
    if not number:
        return None
    if len(number) <= 6:
        return "*" * len(number)
    return number[:8] + "***"


# ---------- resolution ----------
async def _build_public_certificate(db, cert, token) -> dict[str, Any]:
    snap = cert.gemstone_snapshot or {}
    gemstone = {
        "object_type": snap.get("object_type"),
        "name": snap.get("name"),
        "species": snap.get("species"),
        "variety": snap.get("variety"),
        "carat": snap.get("carat"),
        "dimensions": snap.get("dimensions"),
        "shape": snap.get("shape"),
        "cut": snap.get("cut"),
        "color": snap.get("color"),
        "transparency": snap.get("transparency"),
        "clarity": snap.get("clarity"),
        "treatment": snap.get("treatment"),
        "origin": snap.get("origin"),
        "photo_url": f"/api/gemstone/photo/{snap.get('photo_id')}" if snap.get("photo_id") else None,
    }

    # Owner reflects the CURRENT owner (locked masking); not part of the snapshot.
    owner_masked = None
    if cert.gemstone_id:
        gem = await GemstoneRepository(db).get_by_uuid(cert.gemstone_id)
        if gem is not None and gem.active_owner_id:
            owner = await CustomerRepositoryV2(db).get_by_uuid(gem.active_owner_id)
            if owner is not None:
                owner_masked = mask_owner_name(owner.full_name)

    # Short-lived, unforgeable preview capability (FASE 3.3). Never leaks secrets;
    # failure to mint must not break verification.
    preview_token = None
    try:
        from services.preview import create_preview_token

        preview_token = create_preview_token(cert.uuid, cert.version)
    except Exception:
        preview_token = None

    return {
        "certificate_number": cert.certificate_number,
        "version": cert.version,
        "issue_date": (cert.issued_at or "")[:10] or None,
        "gemstone": {k: v for k, v in gemstone.items() if v is not None},
        "owner_masked": owner_masked,
        "examiner": snap.get("examiner"),
        "conclusion": snap.get("conclusion"),
        "notes": snap.get("notes"),
        "preview_token": preview_token,
    }


def _status_from_certificate(cert, gem) -> tuple[str, VerificationResult]:
    if cert.status == "revoked":
        return "revoked", VerificationResult.REVOKED
    if not cert.is_current:
        return "archived", VerificationResult.NOT_FOUND
    if gem is not None and gem.status == "archived":
        return "archived", VerificationResult.NOT_FOUND
    return "valid", VerificationResult.SUCCESS


async def _log(db, method, result, gemstone_id, cert_number, ip):
    log = VerificationLog(
        method=method,
        result=result,
        gemstone_id=gemstone_id,
        certificate_number_masked=_mask_cert_number(cert_number),
        ip_hash=hashlib.sha256(ip.encode()).hexdigest() if ip else None,
    )
    await VerificationLogRepository(db).create(log)


async def verify_manual(db, certificate_number: str, security_code: str, ip: Optional[str]) -> dict:
    """Manual verification: certificate number + security code (both required)."""
    cert = await CertificateRepository(db).get_current_by_number(certificate_number)
    if cert is None:
        await _log(db, VerificationMethod.MANUAL_CODE, VerificationResult.NOT_FOUND, None, certificate_number, ip)
        return {"status": "not_found", "certificate": None}

    token = await VerificationTokenRepository(db).get_active_for_certificate(cert.uuid)
    # Exact-match security code; generic outcome on mismatch (no enumeration).
    if token is None or token.security_code != security_code:
        await _log(db, VerificationMethod.MANUAL_CODE, VerificationResult.INVALID_CODE, cert.gemstone_id, certificate_number, ip)
        return {"status": "not_found", "certificate": None}

    gem = await GemstoneRepository(db).get_by_uuid(cert.gemstone_id) if cert.gemstone_id else None
    status, result = _status_from_certificate(cert, gem)
    await _log(db, VerificationMethod.MANUAL_CODE, result, cert.gemstone_id, certificate_number, ip)
    payload = await _build_public_certificate(db, cert, token) if status == "valid" else None
    return {"status": status, "certificate": payload}


async def resolve_qr(db, token_value: str) -> dict:
    """QR resolve: opaque token -> certificate number prefill only (no details)."""
    token = await VerificationTokenRepository(db).get_by_token(token_value)
    if token is None or not token.certificate_id:
        return {"token_valid": False}
    cert = await CertificateRepository(db).get_by_uuid(token.certificate_id)
    if cert is None:
        return {"token_valid": False}
    return {"token_valid": True, "certificate_number": cert.certificate_number}


async def verify_qr(db, token_value: str, ip: Optional[str]) -> dict:
    """QR verify: opaque token is the credential (locked priority #1)."""
    token = await VerificationTokenRepository(db).get_by_token(token_value)
    if token is None or not token.certificate_id:
        await _log(db, VerificationMethod.QR_TOKEN, VerificationResult.NOT_FOUND, None, None, ip)
        return {"status": "not_found", "certificate": None}
    cert = await CertificateRepository(db).get_by_uuid(token.certificate_id)
    if cert is None:
        await _log(db, VerificationMethod.QR_TOKEN, VerificationResult.NOT_FOUND, token.gemstone_id, None, ip)
        return {"status": "not_found", "certificate": None}

    gem = await GemstoneRepository(db).get_by_uuid(cert.gemstone_id) if cert.gemstone_id else None
    status, result = _status_from_certificate(cert, gem)
    await _log(db, VerificationMethod.QR_TOKEN, result, cert.gemstone_id, cert.certificate_number, ip)
    payload = await _build_public_certificate(db, cert, token) if status == "valid" else None
    return {"status": status, "certificate": payload}
