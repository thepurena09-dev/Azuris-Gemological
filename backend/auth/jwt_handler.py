"""JWT access/refresh token handling — Sprint 6 (PyJWT, HS256)."""

import uuid as _uuid
from datetime import datetime, timedelta, timezone

import jwt

from core.config import get_settings
from models.people import Admin

ACCESS_TYPE = "access"
REFRESH_TYPE = "refresh"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(admin: Admin) -> str:
    settings = get_settings()
    payload = {
        "sub": admin.uuid,
        "email": admin.email,
        "role": admin.role,
        "type": ACCESS_TYPE,
        "iat": _now(),
        "exp": _now() + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(admin: Admin) -> tuple[str, str, str]:
    """Return (token, jti, expires_at_iso). jti is stored server-side."""
    settings = get_settings()
    jti = str(_uuid.uuid4())
    expires_at = _now() + timedelta(days=settings.refresh_token_days)
    payload = {
        "sub": admin.uuid,
        "jti": jti,
        "type": REFRESH_TYPE,
        "iat": _now(),
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti, expires_at.isoformat()


def decode_token(token: str) -> dict:
    """Decode & verify a token. Raises jwt.InvalidTokenError on any problem."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
