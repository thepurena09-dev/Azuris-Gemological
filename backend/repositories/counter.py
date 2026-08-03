"""Counter repository — atomic certificate-number generation (Sprint 5).

Certificate numbers follow the locked format `AZR-GEM-YYYY-000001`. The next
number is produced by an atomic `find_one_and_update` upsert with `$inc` on the
`counters` collection (unique on name+year) — never by counting documents and
never reusing a number. The counter is internal and never exposed publicly.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from pymongo import ReturnDocument

from models.base import utcnow_iso
from repositories.base import BaseRepository

CERTIFICATE_COUNTER = "certificate"
CERTIFICATE_PREFIX = "AZR-GEM"


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

    async def next_certificate_number(self, year: Optional[int] = None) -> str:
        year = year or datetime.now(timezone.utc).year
        seq = await self._next_sequence(CERTIFICATE_COUNTER, year)
        return f"{CERTIFICATE_PREFIX}-{year}-{seq:06d}"
