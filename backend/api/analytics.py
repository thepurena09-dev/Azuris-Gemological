"""Analytics endpoints — Sprint 27 (BATCH D).

Admin dashboard operational analytics. Read-only, RBAC-guarded
(`ANALYTICS_READ`; SUPER_ADMIN + ADMINISTRATOR per the locked matrix).
Returns only privacy-safe aggregates — no PII, no secrets, no ObjectIds.
Routes yield raw data; the Sprint 8 middleware wraps the success envelope.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from auth.rbac import Permission, require_permission
from db.mongodb import get_database
from models.people import Admin
from services.analytics import build_overview

admin_router = APIRouter(prefix="/admin/analytics", tags=["analytics-admin"])

_READ = require_permission(Permission.ANALYTICS_READ)


@admin_router.get("/overview")
async def analytics_overview(
    admin: Admin = Depends(_READ), db=Depends(get_database)
):
    return await build_overview(db)
