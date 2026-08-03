"""Centralized application configuration — Sprint 2.

Environment-driven settings via Pydantic Settings. No secrets are hardcoded;
every value is sourced from environment variables / the backend .env file.
Business subsystems (DB usage, auth, storage) are configured in later sprints
but their env contracts can be declared here as they are introduced.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Typed application settings loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application metadata ---
    app_name: str = "Azuris Gemological Platform API"
    app_version: str = "0.1.0"
    sprint: int = 2
    environment: str = "development"  # development | staging | production
    api_prefix: str = "/api"
    log_level: str = "INFO"

    # --- Database (connection layer implemented in Sprint 3) ---
    mongo_url: str
    db_name: str

    # --- CORS ---
    cors_origins: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse the comma-separated CORS origins into a clean list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allow_credentials(self) -> bool:
        """Per the CORS spec, credentials cannot be combined with the '*'
        wildcard. Enable credentials only when explicit origins are configured.
        """
        return self.cors_origins_list != ["*"]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (single instance per process)."""
    return Settings()
