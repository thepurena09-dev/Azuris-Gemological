"""Operational analytics — Sprint 27 (BATCH D).

Read-only, privacy-safe aggregations for the admin dashboard. Never returns PII
(no names, emails, phones, addresses), never returns secrets (security codes, QR
tokens, preview tokens), never returns raw Mongo ObjectIds. Only aggregated
counts, status breakdowns, and safe time-series are produced.

Business collections are soft-delete aware (`is_deleted != true`). Log
collections are append-only and queried directly.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

# Soft-delete aware business collections.
_ACTIVE = {"is_deleted": {"$ne": True}}


async def _count(db: Any, coll: str, extra: dict | None = None) -> int:
    q = dict(_ACTIVE)
    if extra:
        q.update(extra)
    return await db[coll].count_documents(q)


async def _group_by(db: Any, coll: str, field: str) -> dict[str, int]:
    """Soft-delete-aware group counts keyed by `field`."""
    pipeline = [
        {"$match": _ACTIVE},
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
    ]
    out: dict[str, int] = {}
    async for row in db[coll].aggregate(pipeline):
        key = row["_id"]
        if key is None:
            key = "unknown"
        out[str(key)] = int(row["count"])
    return out


async def _log_group_by(db: Any, coll: str, field: str, since_iso: str) -> dict[str, int]:
    pipeline = [
        {"$match": {"created_at": {"$gte": since_iso}}},
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
    ]
    out: dict[str, int] = {}
    async for row in db[coll].aggregate(pipeline):
        key = row["_id"] if row["_id"] is not None else "unknown"
        out[str(key)] = int(row["count"])
    return out


async def _verification_series(db: Any, days: int, since_iso: str) -> list[dict]:
    """Daily verification totals for the trailing window (safe, no PII)."""
    pipeline = [
        {"$match": {"created_at": {"$gte": since_iso}}},
        {
            "$group": {
                "_id": {"$substrBytes": ["$created_at", 0, 10]},
                "count": {"$sum": 1},
                "success": {
                    "$sum": {"$cond": [{"$eq": ["$result", "success"]}, 1, 0]}
                },
            }
        },
    ]
    buckets: dict[str, dict] = {}
    async for row in db["verification_logs"].aggregate(pipeline):
        day = row["_id"]
        if not day:
            continue
        buckets[day] = {"count": int(row["count"]), "success": int(row["success"])}

    today = datetime.now(timezone.utc).date()
    series: list[dict] = []
    for i in range(days - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        b = buckets.get(d, {"count": 0, "success": 0})
        series.append({"date": d, "count": b["count"], "success": b["success"]})
    return series


async def _certificate_counter(db: Any) -> dict:
    year = datetime.now(timezone.utc).year
    doc = await db["counters"].find_one({"name": "certificate", "year": year})
    last = int(doc["last_number"]) if doc and "last_number" in doc else 0
    nxt = f"AZR-GEM-{last + 1:06d}-{year % 100:02d}"
    return {"last_number": last, "next_number": nxt, "year": year}


async def build_overview(db: Any) -> dict:
    now = datetime.now(timezone.utc)
    since_30 = (now - timedelta(days=30)).isoformat()
    since_14 = (now - timedelta(days=14)).isoformat()

    totals = {
        "customers": await _count(db, "customers"),
        "gemstones": await _count(db, "gemstones"),
        "jewelry": await _count(db, "jewelry"),
        "media": await _count(db, "media"),
        "certificates": await _count(db, "certificates"),
        "warranties": await _count(db, "warranties"),
        "ownership_transfers": await _count(db, "ownership_transfers"),
        "membership_cards": await _count(db, "membership_cards"),
        "verification_tokens": await _count(db, "verification_tokens"),
    }

    verification_by_result = await _log_group_by(
        db, "verification_logs", "result", since_30
    )
    audit_by_action = await _log_group_by(db, "audit_logs", "action", since_30)

    return {
        "generated_at": now.isoformat(),
        "totals": totals,
        "gemstones_by_status": await _group_by(db, "gemstones", "status"),
        "certificates_by_status": await _group_by(db, "certificates", "status"),
        "warranties_by_status": await _group_by(db, "warranties", "status"),
        "transfers_by_status": await _group_by(db, "ownership_transfers", "status"),
        "memberships_by_status": await _group_by(db, "membership_cards", "status"),
        "verification": {
            "window_days": 30,
            "total": sum(verification_by_result.values()),
            "by_result": verification_by_result,
            "series": await _verification_series(db, 14, since_14),
        },
        "admin_activity": {
            "window_days": 30,
            "total": sum(audit_by_action.values()),
            "by_action": audit_by_action,
        },
        "certificate_counter": await _certificate_counter(db),
    }
