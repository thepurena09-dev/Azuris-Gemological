"""Media DTOs — Sprint 4."""

from typing import Optional

from pydantic import BaseModel, Field

from models.enums import MediaEntityType, MediaRole
from schemas.common import AuditFields


class MediaCreate(BaseModel):
    entity_type: MediaEntityType
    entity_id: str
    role: MediaRole = MediaRole.GALLERY
    original_url: str
    optimized_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    mime_type: str = Field(min_length=1, max_length=100)
    size_bytes: int = Field(ge=0)
    width: Optional[int] = Field(default=None, ge=0)
    height: Optional[int] = Field(default=None, ge=0)
    duration_seconds: Optional[float] = Field(default=None, ge=0)
    alt_text_id: Optional[str] = None
    alt_text_en: Optional[str] = None


class MediaUpdate(BaseModel):
    role: Optional[MediaRole] = None
    optimized_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    alt_text_id: Optional[str] = None
    alt_text_en: Optional[str] = None


class MediaResponse(AuditFields):
    id: Optional[str] = None
    uuid: str
    entity_type: MediaEntityType
    entity_id: str
    role: MediaRole
    original_url: str
    optimized_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    mime_type: str
    size_bytes: int
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[float] = None
    alt_text_id: Optional[str] = None
    alt_text_en: Optional[str] = None
