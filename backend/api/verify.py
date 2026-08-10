"""Public verification endpoints — FASE 2.

Manual (certificate number + security code) and QR (opaque token) verification.
Generic, non-enumerable outcomes. Minimal in-memory rate limiting (smallest
production-ready anti-abuse; no external dependency).
"""

import re
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, Request, Response

from pydantic import BaseModel, Field

from db.mongodb import get_database
from errors import forbidden
from repositories.legality import CertificateRepository, GemstonePhotoRepository
from services.certificate_pdf import build_certificate_pdf, decode_photo, render_front_cover_png
from services.preview import decode_preview_token
from services.verification import resolve_qr, verify_manual, verify_qr

router = APIRouter(prefix="/verify", tags=["verification"])

CERT_RE = re.compile(r"^AGR-[A-Z]{3}-\d{6}-\d{2}$")

# --- minimal per-IP rate limiter (in-memory, per process) ---
_WINDOW_SECONDS = 60
_MAX_ATTEMPTS = 20
_attempts: dict[str, deque] = defaultdict(deque)


def _rate_limit(request: Request) -> None:
    ip = request.client.host if request and request.client else "unknown"
    now = time.time()
    q = _attempts[ip]
    while q and now - q[0] > _WINDOW_SECONDS:
        q.popleft()
    if len(q) >= _MAX_ATTEMPTS:
        raise forbidden("Too many attempts. Please try again later.")
    q.append(now)


class ManualVerifyRequest(BaseModel):
    certificate_number: str = Field(min_length=1, max_length=64)
    security_code: str = Field(min_length=1, max_length=64)


class QrVerifyRequest(BaseModel):
    token: str = Field(min_length=1, max_length=256)


@router.post("", response_model_exclude_none=True)
async def manual_verify(body: ManualVerifyRequest, request: Request, db=Depends(get_database)):
    _rate_limit(request)
    number = body.certificate_number.strip().upper()
    if not CERT_RE.match(number):
        # Generic outcome; do not confirm/deny record existence.
        return {"status": "not_found", "certificate": None}
    ip = request.client.host if request.client else None
    return await verify_manual(db, number, body.security_code.strip(), ip)


@router.get("/qr/resolve", response_model_exclude_none=True)
async def qr_resolve(token: str, request: Request, db=Depends(get_database)):
    _rate_limit(request)
    return await resolve_qr(db, token.strip())


@router.get("/pdf/{number}")
async def public_certificate_pdf(number: str, request: Request, db=Depends(get_database)):
    """Public: open the two-page certificate PDF by registration number (no login/code).

    Returns 404 for unknown, invalid-format, revoked, or archived certificates so the
    public UI can show a generic "Certificate not found" state (no enumeration detail).
    """
    _rate_limit(request)
    num = number.strip().upper()
    if not CERT_RE.match(num):
        return Response(status_code=404)
    cert = await CertificateRepository(db).get_current_by_number(num)
    if cert is None or cert.status == "revoked":
        return Response(status_code=404)
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
    try:
        pdf = build_certificate_pdf(payload, photo_bytes)
    except Exception:
        return Response(status_code=503)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{cert.certificate_number}.pdf"',
            "Cache-Control": "public, max-age=300",
        },
    )


@router.post("/qr", response_model_exclude_none=True)
async def qr_verify(body: QrVerifyRequest, request: Request, db=Depends(get_database)):
    _rate_limit(request)
    ip = request.client.host if request.client else None
    return await verify_qr(db, body.token.strip(), ip)


@router.get("/preview")
async def certificate_preview(t: str, request: Request, db=Depends(get_database)):
    """Public certificate front-cover preview (FASE 3.3).

    Gated by a short-lived, unforgeable preview token minted during a successful
    verification (no enumeration). Follows current-version visibility: only the
    current certificate is previewed. Rendered from the SAME front-cover generator
    as the booklet PDF. Never exposes secrets / IDs.
    """
    _rate_limit(request)
    data = decode_preview_token(t.strip())
    if data is None:
        return Response(status_code=404)
    cert = await CertificateRepository(db).get_by_uuid(data["sub"])
    # Current-version visibility: archived/non-current never override the preview.
    if cert is None or not cert.is_current or cert.status == "revoked":
        return Response(status_code=404)
    try:
        png = render_front_cover_png(
            {
                "certificate_number": cert.certificate_number,
                "issued_at": cert.issued_at,
                "version": cert.version,
            }
        )
    except Exception:
        return Response(status_code=503)
    return Response(
        content=png,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=900, immutable"},
    )
