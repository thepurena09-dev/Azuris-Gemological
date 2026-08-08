"""Development-only test-role seed (RBAC checks).

Ensures a CONTENT_MANAGER and a CUSTOMER_SERVICE admin exist for authorization
tests. Refuses to run when ENVIRONMENT=production. Never auto-runs at startup.

Usage:
    cd /app/backend && python -m scripts.seed_test_roles
"""

import asyncio

from auth.security import hash_password
from core.config import get_settings
from db.mongodb import mongodb
from models.enums import AdminRole
from models.people import Admin
from repositories.people import AdminRepository

_TEST_ROLES = [
    ("cm@azuris.local", "CmDev@2026!", "Azuris Content Manager", AdminRole.CONTENT_MANAGER),
    ("cs@azuris.local", "CsDev@2026!", "Azuris Customer Service", AdminRole.CUSTOMER_SERVICE),
    ("adminr@azuris.local", "AdminrDev@2026!", "Azuris Administrator", AdminRole.ADMINISTRATOR),
]


async def seed() -> None:
    settings = get_settings()
    if settings.is_production:
        raise SystemExit("Refusing to seed: ENVIRONMENT=production.")

    await mongodb.connect()
    repo = AdminRepository(mongodb.db)

    for email, password, full_name, role in _TEST_ROLES:
        email = email.lower().strip()
        existing = await repo.get_by_email(email)
        if existing is None:
            await repo.create(
                Admin(
                    email=email,
                    password_hash=hash_password(password),
                    full_name=full_name,
                    role=role,
                    is_active=True,
                    created_by="seed",
                    updated_by="seed",
                )
            )
            print(f"created {role.value}: {email}")
        else:
            await repo.update_by_uuid(
                existing.uuid,
                {"password_hash": hash_password(password), "role": role.value, "is_active": True},
            )
            print(f"updated {role.value}: {email}")

    await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(seed())
