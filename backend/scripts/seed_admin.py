"""Development-only admin seed — Sprint 6.

Creates (or refreshes) a single SUPER_ADMIN using ADMIN_EMAIL / ADMIN_PASSWORD.
Refuses to run when ENVIRONMENT=production. NEVER runs automatically at startup.

Usage:
    cd /app/backend && python -m scripts.seed_admin
"""

import asyncio

from auth.security import hash_password
from core.config import get_settings
from db.mongodb import mongodb
from models.enums import AdminRole
from models.people import Admin
from repositories.people import AdminRepository


async def seed() -> None:
    settings = get_settings()
    if settings.is_production:
        raise SystemExit("Refusing to seed: ENVIRONMENT=production.")
    if not settings.admin_password:
        raise SystemExit(
            "ADMIN_PASSWORD is not set. Provide it via the environment before seeding."
        )

    await mongodb.connect()
    repo = AdminRepository(mongodb.db)

    email = settings.admin_email.lower().strip()
    existing = await repo.get_by_email(email)

    if existing is None:
        admin = Admin(
            email=email,
            password_hash=hash_password(settings.admin_password),
            full_name="Azuris Super Admin",
            role=AdminRole.SUPER_ADMIN,
            is_active=True,
            created_by="seed",
            updated_by="seed",
        )
        await repo.create(admin)
        action = "created"
    else:
        await repo.update_by_uuid(
            existing.uuid,
            {
                "password_hash": hash_password(settings.admin_password),
                "role": AdminRole.SUPER_ADMIN.value,
                "is_active": True,
            },
        )
        action = "updated"

    await mongodb.disconnect()
    print(f"Dev SUPER_ADMIN {action}: {email}")


if __name__ == "__main__":
    asyncio.run(seed())
