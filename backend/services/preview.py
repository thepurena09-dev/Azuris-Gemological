"""Signed, short-lived certificate-preview capability token — FASE 3.3.

The preview image endpoint is gated by an unforgeable, expiring token minted only
during a successful public verification. This prevents certificate enumeration
(sequential numbers cannot be probed) without introducing any new stored secret.
The token carries NO security_code / QR token / owner data / Mongo ObjectId.
"""

from datetime import datetime, timedelta, timezone

import jwt

from core.config import get_settings

PREVIEW_TYPE = "cert_preview"
PREVIEW_TTL_MINUTES = 20


def create_preview_token(cert_uuid: str, version: int) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": cert_uuid,
        "ver": version,
        "type": PREVIEW_TYPE,
        "iat": now,
        "exp": now + timedelta(minutes=PREVIEW_TTL_MINUTES),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_preview_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        data = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError:
        return None
    if data.get("type") != PREVIEW_TYPE or not data.get("sub"):
        return None
    return data
