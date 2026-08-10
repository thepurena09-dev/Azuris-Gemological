"""Counter repository — atomic certificate-number generation (Sprint 5).

Certificate numbers follow the client-approved format `AZR-GEM-000001-YY`
(FASE 3.4; sequence 6-digit, then 2-digit issue year). The next number is
produced by an atomic `find_one_and_update` upsert with `$inc` on the `counters`
collection (unique on name+year) — never by counting documents and never reusing
a number. The counter is internal and never exposed publicly.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from pymongo import ReturnDocument

from models.base import utcnow_iso
from repositories.base import BaseRepository

CERTIFICATE_COUNTER = "certificate"
CERTIFICATE_PREFIX = "AGR"

# BATCH C operational number sources (separate counters — the certificate
# counter is never touched). Formats are provisional operational defaults
# (documented in the PRD ledger, NOT locked in BUSINESS_RULES_LOCK).
WARRANTY_COUNTER = "warranty"
WARRANTY_PREFIX = "AZR-WTY"
MEMBERSHIP_COUNTER = "membership"
MEMBERSHIP_PREFIX = "AZR-MEM"


class CounterRepository(BaseRepository):
    """Owns the `counters` collection. Repositories-only Mongo access."""

    collection_name = "counters"

    def __init__(self, db: Any):
        super().__init__(db, self.collection_name)

    async def _next_sequence(self, name: str, year: int) -> int:
        doc = await self.collection.find_one_and_update(
            {"name": name, "year": year},
            {"$inc": {"last_number": 1}, "$set": {"updated_at": utcnow_iso()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return int(doc["last_number"])

    async def next_certificate_number(self, code: str, year: Optional[int] = None) -> str:
        """Global atomic sequence. Number = AGR-{CODE}-{SEQ:06d}-{YY}.

        One global certificate counter is used for ALL gemstone codes (never a
        per-code counter). `code` is the admin-defined 3-letter gemstone code.
        """
        year = year or datetime.now(timezone.utc).year
        seq = await self._next_sequence(CERTIFICATE_COUNTER, year)
        return f"{CERTIFICATE_PREFIX}-{code}-{seq:06d}-{year % 100:02d}"

    async def next_warranty_number(self, year: Optional[int] = None) -> str:
        year = year or datetime.now(timezone.utc).year
        seq = await self._next_sequence(WARRANTY_COUNTER, year)
        return f"{WARRANTY_PREFIX}-{seq:06d}-{year % 100:02d}"

    async def next_membership_number(self, year: Optional[int] = None) -> str:
        year = year or datetime.now(timezone.utc).year
        seq = await self._next_sequence(MEMBERSHIP_COUNTER, year)
        return f"{MEMBERSHIP_PREFIX}-{seq:06d}-{year % 100:02d}"
