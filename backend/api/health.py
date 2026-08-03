"""Health endpoint — Sprint 1.

Reports only that the backend application is running. Database, storage,
auth and external-service health checks are introduced in later sprints.
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "azuris-platform",
        "version": "0.1.0",
        "sprint": 1,
    }
