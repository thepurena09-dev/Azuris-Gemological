"""Azuris Gemological — Backend application entrypoint.

Sprint 1: Application shell only.
- FastAPI app boot
- CORS configuration
- Health endpoint (GET /api/health)

No business logic, no database collections, no authentication.
Subsystems (config, db, auth, storage, business modules) are scaffolded as
empty packages and will be implemented in their respective sprints.
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import logging
import os

from api.health import router as health_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("azuris")

app = FastAPI(
    title="Azuris Gemological Platform API",
    version="0.1.0",
    description="Luxury gemological certification & verification platform.",
)

# Public API routes are mounted under the /api prefix (Kubernetes ingress rule).
app.include_router(health_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Azuris backend started (Sprint 1 — application shell).")
