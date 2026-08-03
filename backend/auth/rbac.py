"""RBAC — roles, permission matrix & authorization guards (Sprint 7).

Default policy: **DENY unless explicitly allowed**. Only the four locked roles
exist. `SUPER_ADMIN` implicitly has every permission. Guards are FastAPI
`Depends` factories layered on top of `get_current_admin`. Unauthorized access
returns a generic 403. No business CRUD/endpoints are created here.
"""

from enum import Enum
from typing import Callable

from fastapi import Depends

from auth.dependencies import get_current_admin
from errors import forbidden
from models.enums import AdminRole
from models.people import Admin


class Permission(str, Enum):
    # Admin account management (SUPER_ADMIN only)
    ADMIN_READ = "admin:read"
    ADMIN_MANAGE = "admin:manage"
    # Gemstones
    GEMSTONE_READ = "gemstone:read"
    GEMSTONE_WRITE = "gemstone:write"
    GEMSTONE_DELETE = "gemstone:delete"
    # Jewelry
    JEWELRY_READ = "jewelry:read"
    JEWELRY_WRITE = "jewelry:write"
    JEWELRY_DELETE = "jewelry:delete"
    # Certificates
    CERTIFICATE_READ = "certificate:read"
    CERTIFICATE_WRITE = "certificate:write"
    CERTIFICATE_DELETE = "certificate:delete"
    # Warranties
    WARRANTY_READ = "warranty:read"
    WARRANTY_WRITE = "warranty:write"
    WARRANTY_DELETE = "warranty:delete"
    # Ownership
    OWNERSHIP_READ = "ownership:read"
    OWNERSHIP_WRITE = "ownership:write"
    # Verification (secrets/token management)
    VERIFICATION_READ = "verification:read"
    VERIFICATION_MANAGE = "verification:manage"
    # Customers
    CUSTOMER_READ = "customer:read"
    CUSTOMER_WRITE = "customer:write"
    CUSTOMER_DELETE = "customer:delete"
    # Membership cards
    MEMBERSHIP_READ = "membership:read"
    MEMBERSHIP_WRITE = "membership:write"
    # Media library
    MEDIA_READ = "media:read"
    MEDIA_WRITE = "media:write"
    MEDIA_DELETE = "media:delete"
    # CMS / presentation
    CMS_READ = "cms:read"
    CMS_WRITE = "cms:write"
    CATALOG_PRESENTATION = "catalog:presentation"
    # Logs & analytics
    LOGS_READ = "logs:read"
    ANALYTICS_READ = "analytics:read"


ALL_PERMISSIONS: frozenset[Permission] = frozenset(Permission)

# Least-privilege matrix. SUPER_ADMIN is handled implicitly (all permissions).
ROLE_PERMISSIONS: dict[AdminRole, frozenset[Permission]] = {
    AdminRole.SUPER_ADMIN: ALL_PERMISSIONS,
    AdminRole.ADMINISTRATOR: frozenset(
        {
            Permission.GEMSTONE_READ, Permission.GEMSTONE_WRITE, Permission.GEMSTONE_DELETE,
            Permission.JEWELRY_READ, Permission.JEWELRY_WRITE, Permission.JEWELRY_DELETE,
            Permission.CERTIFICATE_READ, Permission.CERTIFICATE_WRITE, Permission.CERTIFICATE_DELETE,
            Permission.WARRANTY_READ, Permission.WARRANTY_WRITE, Permission.WARRANTY_DELETE,
            Permission.OWNERSHIP_READ, Permission.OWNERSHIP_WRITE,
            Permission.VERIFICATION_READ, Permission.VERIFICATION_MANAGE,
            Permission.CUSTOMER_READ, Permission.CUSTOMER_WRITE, Permission.CUSTOMER_DELETE,
            Permission.MEMBERSHIP_READ, Permission.MEMBERSHIP_WRITE,
            Permission.MEDIA_READ, Permission.MEDIA_WRITE, Permission.MEDIA_DELETE,
            Permission.CMS_READ,
            Permission.LOGS_READ, Permission.ANALYTICS_READ,
            # No ADMIN_READ / ADMIN_MANAGE (no admin-account management).
        }
    ),
    AdminRole.CONTENT_MANAGER: frozenset(
        {
            Permission.CMS_READ, Permission.CMS_WRITE, Permission.CATALOG_PRESENTATION,
            Permission.MEDIA_READ, Permission.MEDIA_WRITE,
            Permission.GEMSTONE_READ, Permission.JEWELRY_READ,
        }
    ),
    AdminRole.CUSTOMER_SERVICE: frozenset(
        {
            Permission.CUSTOMER_READ, Permission.CUSTOMER_WRITE,  # non-destructive
            Permission.GEMSTONE_READ, Permission.JEWELRY_READ,
            Permission.CERTIFICATE_READ, Permission.WARRANTY_READ,
            Permission.OWNERSHIP_READ, Permission.VERIFICATION_READ,
            Permission.MEMBERSHIP_READ, Permission.MEDIA_READ, Permission.CMS_READ,
        }
    ),
}


def _role_from_value(role_value: str) -> AdminRole | None:
    try:
        return AdminRole(role_value)
    except ValueError:
        return None


def permissions_for(role_value: str) -> frozenset[Permission]:
    """Resolve a role's permission set. Unknown role -> empty set (deny)."""
    role = _role_from_value(role_value)
    if role is None:
        return frozenset()
    return ROLE_PERMISSIONS.get(role, frozenset())


def has_permission(role_value: str, permission: Permission) -> bool:
    if role_value == AdminRole.SUPER_ADMIN.value:
        return True
    return permission in permissions_for(role_value)


# ---------- Guard dependency factories ----------
def require_roles(*allowed: AdminRole) -> Callable:
    """Allow only the listed roles (SUPER_ADMIN always allowed)."""
    allowed_values = {r.value for r in allowed}

    async def checker(admin: Admin = Depends(get_current_admin)) -> Admin:
        if _role_from_value(admin.role) is None:
            raise forbidden()  # invalid/unknown role -> deny
        if admin.role == AdminRole.SUPER_ADMIN.value or admin.role in allowed_values:
            return admin
        raise forbidden()

    return checker


def require_permission(*required: Permission, require_all: bool = True) -> Callable:
    """Allow only admins whose role grants the required permission(s)."""

    async def checker(admin: Admin = Depends(get_current_admin)) -> Admin:
        if admin.role == AdminRole.SUPER_ADMIN.value:
            return admin
        granted = permissions_for(admin.role)
        if not granted:
            raise forbidden()
        ok = (
            all(p in granted for p in required)
            if require_all
            else any(p in granted for p in required)
        )
        if not ok:
            raise forbidden()
        return admin

    return checker
