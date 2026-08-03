"""Auth dependencies — Sprint 6.

`get_current_admin` decodes the access token (Bearer) and loads the active admin.
Generic 401 on any failure. Role authorization guards for modules arrive in
Sprint 7 (not created here).
"""

import jwt
from fastapi import Depends, Request

from auth.jwt_handler import ACCESS_TYPE, decode_token
from db.mongodb import get_database
from errors import unauthorized
from models.people import Admin
from repositories.people import AdminRepository


def _extract_bearer(request: Request) -> str:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip()
    return ""


async def get_current_admin(request: Request, db=Depends(get_database)) -> Admin:
    token = _extract_bearer(request)
    if not token:
        raise unauthorized()
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        raise unauthorized()
    if payload.get("type") != ACCESS_TYPE:
        raise unauthorized()

    admin = await AdminRepository(db).get_by_uuid(payload.get("sub", ""))
    if not admin or not admin.is_active:
        raise unauthorized()
    return admin
