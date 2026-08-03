"""Authentication endpoints — Sprint 6 (admin portal only).

Endpoints (all under /api/auth):
  POST /login    -> issue access + refresh (rotating) tokens
  POST /refresh  -> rotate refresh token, issue new access token
  POST /logout   -> invalidate refresh token(s)
  GET  /me       -> current admin (no secrets)

Bearer/JSON transport (no cookies this sprint — frontend integration is later).
Generic errors only; every event is written to security_logs.
"""

import jwt
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from auth.dependencies import get_current_admin
from auth.jwt_handler import (
    REFRESH_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from auth.security import verify_password
from auth.security_logs import write_security_log
from db.mongodb import get_database
from errors import unauthorized
from models.base import utcnow_iso
from models.enums import SecurityEventType
from models.people import Admin
from repositories.auth import RefreshTokenRepository
from repositories.people import AdminRepository
from schemas.people import AdminResponse

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------- request/response DTOs ----------
class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
    all_devices: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    admin: AdminResponse


class AccessResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


async def _issue_tokens(db, admin: Admin) -> tuple[str, str]:
    access = create_access_token(admin)
    refresh, jti, expires_at = create_refresh_token(admin)
    await RefreshTokenRepository(db).store(jti, admin.uuid, expires_at)
    return access, refresh


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db=Depends(get_database)):
    email = body.email.lower().strip()
    admin = await AdminRepository(db).get_by_email(email)

    if not admin or not admin.is_active or not verify_password(
        body.password, admin.password_hash
    ):
        await write_security_log(
            db,
            SecurityEventType.LOGIN_FAIL,
            request=request,
            actor_id=admin.uuid if admin else None,
            success=False,
            detail="login_failed",
        )
        raise unauthorized()

    now = utcnow_iso()
    await AdminRepository(db).update_by_uuid(
        admin.uuid, {"last_login": now, "last_activity": now}
    )
    access, refresh = await _issue_tokens(db, admin)
    await write_security_log(
        db, SecurityEventType.LOGIN_SUCCESS, request=request, actor_id=admin.uuid
    )
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        admin=AdminResponse(**admin.model_dump()),
    )


@router.post("/refresh", response_model=AccessResponse)
async def refresh(body: RefreshRequest, request: Request, db=Depends(get_database)):
    try:
        payload = decode_token(body.refresh_token)
    except jwt.InvalidTokenError:
        raise unauthorized()
    if payload.get("type") != REFRESH_TYPE:
        raise unauthorized()

    jti = payload.get("jti", "")
    admin_id = payload.get("sub", "")
    store = RefreshTokenRepository(db)
    if not await store.is_active(jti):
        raise unauthorized()

    admin = await AdminRepository(db).get_by_uuid(admin_id)
    if not admin or not admin.is_active:
        raise unauthorized()

    # Rotation: revoke the presented refresh token, issue a fresh pair.
    await store.revoke(jti)
    access, new_refresh = await _issue_tokens(db, admin)
    await AdminRepository(db).update_by_uuid(
        admin.uuid, {"last_activity": utcnow_iso()}
    )
    await write_security_log(
        db, SecurityEventType.TOKEN_REFRESH, request=request, actor_id=admin.uuid
    )
    return AccessResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db=Depends(get_database),
):
    store = RefreshTokenRepository(db)
    if body.all_devices:
        await store.revoke_all_for_admin(admin.uuid)
    elif body.refresh_token:
        try:
            payload = decode_token(body.refresh_token)
            if payload.get("sub") == admin.uuid and payload.get("jti"):
                await store.revoke(payload["jti"])
        except jwt.InvalidTokenError:
            pass  # generic: logout always succeeds for the authenticated admin
    else:
        await store.revoke_all_for_admin(admin.uuid)

    await write_security_log(
        db, SecurityEventType.LOGOUT, request=request, actor_id=admin.uuid
    )
    return {"success": True}


@router.get("/me", response_model=AdminResponse)
async def me(admin: Admin = Depends(get_current_admin)):
    return AdminResponse(**admin.model_dump())


class PermissionsResponse(BaseModel):
    role: str
    permissions: list[str]


@router.get("/permissions", response_model=PermissionsResponse)
async def my_permissions(admin: Admin = Depends(get_current_admin)):
    """Role validation / RBAC introspection for the authenticated admin.

    Returns the caller's role and resolved permission set (SUPER_ADMIN => all).
    Not a business feature — lets the future admin UI hide unauthorized actions.
    """
    from auth.rbac import ALL_PERMISSIONS, permissions_for
    from models.enums import AdminRole as _Role

    if admin.role == _Role.SUPER_ADMIN.value:
        perms = ALL_PERMISSIONS
    else:
        perms = permissions_for(admin.role)
    return PermissionsResponse(
        role=admin.role, permissions=sorted(p.value for p in perms)
    )
