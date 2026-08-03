"""Index bootstrap — Sprint 3.

Declares indexes for the locked collections (Architecture Lock v1.1), focused on
the dual-identifier strategy (unique `uuid`), unique business codes, secret tokens,
media entity links, and append-only log time ordering.

This only creates *structure* (indexes / empty collections). No documents are
written and no business logic is performed here. Domain models arrive in Sprint 4.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, IndexModel

logger = logging.getLogger("azuris.db")

# collection name -> list[IndexModel]
INDEX_SPECS: dict[str, list[IndexModel]] = {
    "admins": [
        IndexModel([("email", ASCENDING)], unique=True, name="uq_admin_email"),
    ],
    "customers": [
        IndexModel([("uuid", ASCENDING)], unique=True, name="uq_customer_uuid"),
    ],
    "gemstones": [
        IndexModel([("uuid", ASCENDING)], unique=True, name="uq_gemstone_uuid"),
        IndexModel([("status", ASCENDING)], name="ix_gemstone_status"),
    ],
    "jewelry": [
        IndexModel([("uuid", ASCENDING)], unique=True, name="uq_jewelry_uuid"),
    ],
    "certificates": [
        IndexModel([("uuid", ASCENDING)], unique=True, name="uq_certificate_uuid"),
        IndexModel(
            [("certificate_number", ASCENDING)],
            unique=True,
            name="uq_certificate_number",
        ),
    ],
    "warranties": [
        IndexModel([("uuid", ASCENDING)], unique=True, name="uq_warranty_uuid"),
    ],
    "ownership_transfers": [
        IndexModel([("uuid", ASCENDING)], unique=True, name="uq_ownership_uuid"),
    ],
    "verification_tokens": [
        IndexModel([("uuid", ASCENDING)], unique=True, name="uq_vtoken_uuid"),
        IndexModel([("token", ASCENDING)], unique=True, name="uq_vtoken_token"),
    ],
    "membership_cards": [
        IndexModel([("uuid", ASCENDING)], unique=True, name="uq_membership_uuid"),
    ],
    "media": [
        IndexModel([("uuid", ASCENDING)], unique=True, name="uq_media_uuid"),
        IndexModel(
            [("entity_type", ASCENDING), ("entity_id", ASCENDING)],
            name="ix_media_entity",
        ),
    ],
    "site_content": [
        IndexModel([("key", ASCENDING)], unique=True, name="uq_site_content_key"),
    ],
    "audit_logs": [
        IndexModel([("created_at", DESCENDING)], name="ix_audit_created_at"),
    ],
    "verification_logs": [
        IndexModel([("created_at", DESCENDING)], name="ix_vlog_created_at"),
    ],
    "security_logs": [
        IndexModel([("created_at", DESCENDING)], name="ix_slog_created_at"),
    ],
    # Atomic sequence source for certificate numbers (AZR-GEM-YYYY-000001).
    # Unique (name, year) guarantees a single counter document per year so
    # concurrent upserts increment atomically. Never exposed publicly.
    "counters": [
        IndexModel(
            [("name", ASCENDING), ("year", ASCENDING)],
            unique=True,
            name="uq_counter_name_year",
        ),
    ],
}


async def ensure_indexes(db: AsyncIOMotorDatabase) -> dict[str, int]:
    """Idempotently create all declared indexes. Returns {collection: count}."""
    summary: dict[str, int] = {}
    for collection, models in INDEX_SPECS.items():
        if not models:
            continue
        names = await db[collection].create_indexes(models)
        summary[collection] = len(names)
    logger.info("Index bootstrap complete: %s", summary)
    return summary
