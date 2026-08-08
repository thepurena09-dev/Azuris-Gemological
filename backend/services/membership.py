"""Membership Card service — BATCH C, Sprint 23A.

Signed, member-safe verification token + QR rendering for the Azuris Membership
Card. The token type is DISTINCT from the certificate preview/QR domain — a
membership token can NEVER be used to verify a certificate and vice-versa.

The token carries NO PII / customer UUID / Mongo ObjectId / secrets — only the
membership card's public `uuid` + version. Verification exposes member-safe data
only (status, member id, masked name, member-since).
"""

from __future__ import annotations

import io
from datetime import datetime, timedelta, timezone

import jwt
import qrcode

from core.config import get_settings

MEMBERSHIP_TYPE = "membership_verify"
MEMBERSHIP_TTL_DAYS = 3650  # long-lived card artifact


def create_membership_token(card_uuid: str, version: int) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": card_uuid,
        "ver": version,
        "type": MEMBERSHIP_TYPE,
        "iat": now,
        "exp": now + timedelta(days=MEMBERSHIP_TTL_DAYS),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_membership_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        data = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError:
        return None
    if data.get("type") != MEMBERSHIP_TYPE or not data.get("sub"):
        return None
    return data


def render_membership_qr_png(url: str) -> bytes:
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
