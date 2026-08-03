"""Health endpoint.

Reports only that the backend application is running and echoes core
configuration metadata. Database, storage, auth and external-service health
checks are introduced in their respective later sprints.
"""

from fastapi import APIRouter

from core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "azuris-platform",
        "version": settings.app_version,
        "sprint": settings.sprint,
        "environment": settings.environment,
    }
