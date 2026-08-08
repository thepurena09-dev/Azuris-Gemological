"""Storage adapter factory — Sprint 10.

Selects the backend from the `STORAGE_BACKEND` env var (default: `mongo`). No
vendor is hardcoded into business code; adding a new backend means registering
it here only.
"""

from __future__ import annotations

import os

from storage.base import StorageAdapter
from storage.mongo_adapter import MongoStorageAdapter


def get_storage_adapter(db) -> StorageAdapter:
    backend = os.environ.get("STORAGE_BACKEND", "mongo").lower()
    if backend == "mongo":
        return MongoStorageAdapter(db)
    raise ValueError(f"Unsupported STORAGE_BACKEND: {backend!r}")
