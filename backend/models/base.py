"""Shared model foundation — Sprint 4.

Implements the locked data conventions from Architecture Lock v1.1:
- Dual identifier: internal ObjectId (`_id` -> `id`) + public `uuid` (UUID v4).
- Audit envelope: created_at/updated_at/created_by/updated_by.
- Soft delete: is_deleted/deleted_at.
- Document versioning: version/is_current/created_version_at/created_version_by.

MongoDB adherence: ObjectId is never returned raw. `PyObjectId` coerces
ObjectId -> str; `from_mongo`/`to_mongo` translate between the `_id` alias and
the public `id` field. No raw dict spreading.
"""

import uuid as _uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _coerce_object_id(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    return value


PyObjectId = Annotated[str, BeforeValidator(_coerce_object_id)]


def utcnow_iso() -> str:
    """UTC timestamp as an ISO-8601 string (never naive utcnow())."""
    return datetime.now(timezone.utc).isoformat()


def new_uuid() -> str:
    """A fresh UUID v4 as a string — the public/external business identifier."""
    return str(_uuid.uuid4())


class DualIdMixin(BaseModel):
    """Public, opaque, non-enumerable identifier exposed in URLs/QRs/refs."""

    uuid: str = Field(default_factory=new_uuid)


class AuditMixin(BaseModel):
    """Record envelope audit fields (who/when)."""

    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class SoftDeleteMixin(BaseModel):
    is_deleted: bool = False
    deleted_at: Optional[str] = None


class VersionMixin(BaseModel):
    """Versioned-artifact fields (certificates, warranties, membership cards)."""

    version: int = Field(default=1, ge=1)
    is_current: bool = True
    created_version_at: str = Field(default_factory=utcnow_iso)
    created_version_by: Optional[str] = None


class BaseDocument(BaseModel):
    """Base for all persisted documents. Maps `_id` <-> public `id: str`."""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
        extra="ignore",
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    @classmethod
    def from_mongo(cls, doc: Optional[dict[str, Any]]):
        """Build a model from a raw Mongo document (or None)."""
        if not doc:
            return None
        return cls(**doc)

    def to_mongo(self, *, exclude_none: bool = False) -> dict[str, Any]:
        """Serialize for Mongo: emit `_id` only when set (let Mongo assign it)."""
        data = self.model_dump(by_alias=True, exclude_none=exclude_none)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
