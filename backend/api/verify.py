"""Public verification endpoints — FASE 2.

Manual (certificate number + security code) and QR (opaque token) verification.
Generic, non-enumerable outcomes. Minimal in-memory rate limiting (smallest
production-ready anti-abuse; no external dependency).
"""

import re
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from db.mongodb import get_database
from errors import forbidden
from services.verification import resolve_qr, verify_manual, verify_qr

router = APIRouter(prefix="/verify", tags=["verification"])

CERT_RE = re.compile(r"^AZR-GEM-\d{4}-\d{6}$")

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


@router.post("/qr", response_model_exclude_none=True)
async def qr_verify(body: QrVerifyRequest, request: Request, db=Depends(get_database)):
    _rate_limit(request)
    ip = request.client.host if request.client else None
    return await verify_qr(db, body.token.strip(), ip)
