"""Azuris Gemological — Backend application entrypoint.

Through Sprint 2: application shell + centralized configuration layer.
- FastAPI app boot (metadata from Settings)
- Environment-driven CORS (spec-safe credentials handling)
- Health endpoint (GET /api/health)

No business logic, no database collections, no authentication.
"""

import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.health import router as health_router
from core.config import get_settings

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
        "Azuris backend started — env=%s, sprint=%s, cors=%s (credentials=%s).",
        settings.environment,
        settings.sprint,
        settings.cors_origins_list,
        settings.allow_credentials,
    )
