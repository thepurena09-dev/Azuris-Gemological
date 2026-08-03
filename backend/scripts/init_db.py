"""Standalone MongoDB initialization script — Sprint 3.

Usage:
    cd /app/backend && python -m scripts.init_db

Connects to MongoDB and applies the index bootstrap (idempotent).
"""

import asyncio
import logging

from db.init import init_database
from db.mongodb import mongodb

logging.basicConfig(level=logging.INFO)


async def _main() -> None:
    summary = await init_database()
    print("Index bootstrap summary:")
    for collection, count in summary.items():
        print(f"  - {collection}: {count} index(es)")
    await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(_main())
