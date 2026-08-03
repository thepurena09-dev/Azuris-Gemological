"""Azuris Gemological — Backend application entrypoint.

Through Sprint 3: application shell + configuration + MongoDB data backbone.
- FastAPI app boot (metadata from Settings)
- Environment-driven CORS (spec-safe credentials handling)
- MongoDB connection lifecycle (connect + index bootstrap on startup)
- Health endpoint with database status (GET /api/health)

No authentication, no CRUD endpoints, no business modules.
"""

import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.health import router as health_router
from core.config import get_settings
from db.init import init_database
from db.mongodb import mongodb

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("azuris")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Luxury gemological certification & verification platform.",
)

# Public API routes are mounted under the configured prefix (K8s ingress: /api).
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info(
        "Azuris backend starting — env=%s, sprint=%s.",
        settings.environment,
        settings.sprint,
    )
    try:
        summary = await init_database()
        logger.info("Database ready. Indexes: %s", summary)
    except Exception as exc:  # noqa: BLE001 - never block boot on DB availability
        logger.error("Database initialization failed: %s", exc)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await mongodb.disconnect()
