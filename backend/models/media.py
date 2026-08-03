"""Media metadata entity — Sprint 4.

Mirrors the metadata-rich `media` collection from Architecture Lock v1.1 §7/§4
exactly (original/optimized/thumbnail derivatives + technical metadata +
bilingual alt text + entity linkage).
"""

from typing import Optional

from pydantic import Field

from models.base import AuditMixin, BaseDocument, DualIdMixin, SoftDeleteMixin
from models.enums import MediaEntityType, MediaRole


class Media(BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin):
    """Asset with full technical metadata (collection: `media`)."""

    entity_type: MediaEntityType
    entity_id: str                      # owning entity uuid
    role: MediaRole = MediaRole.GALLERY

    original_url: str                   # source upload
    optimized_url: Optional[str] = None  # web-optimized (webp)
    thumbnail_url: Optional[str] = None  # small preview

    mime_type: str = Field(min_length=1, max_length=100)
    size_bytes: int = Field(ge=0)
    width: Optional[int] = Field(default=None, ge=0)
    height: Optional[int] = Field(default=None, ge=0)
    duration_seconds: Optional[float] = Field(default=None, ge=0)  # video only

    alt_text_id: Optional[str] = None
    alt_text_en: Optional[str] = None
