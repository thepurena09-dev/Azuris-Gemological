"""CMS DTOs — Sprint 4."""

from typing import Optional

from pydantic import BaseModel, Field

from models.enums import SiteContentType
from schemas.common import AuditFields


class SiteContentCreate(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    content_type: SiteContentType = SiteContentType.TEXT
    value_id: Optional[str] = None
    value_en: Optional[str] = None
    value: Optional[str] = None
    is_published: bool = True


class SiteContentUpdate(BaseModel):
    content_type: Optional[SiteContentType] = None
    value_id: Optional[str] = None
    value_en: Optional[str] = None
    value: Optional[str] = None
    is_published: Optional[bool] = None


class SiteContentResponse(AuditFields):
    id: Optional[str] = None
    uuid: str
    key: str
    content_type: SiteContentType
    value_id: Optional[str] = None
    value_en: Optional[str] = None
    value: Optional[str] = None
    is_published: bool
