"""Health endpoint.

Through Sprint 3: reports application status plus MongoDB connectivity.
Storage, auth and external-service checks are added in their later sprints.
"""

from fastapi import APIRouter

from core.config import get_settings
from db.mongodb import mongodb

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    db_ok = await mongodb.ping()
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "azuris-platform",
        "version": settings.app_version,
        "sprint": settings.sprint,
        "environment": settings.environment,
        "database": "connected" if db_ok else "disconnected",
    }
