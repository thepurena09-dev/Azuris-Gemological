"""CMS site content entity — Sprint 4. Models only."""

from typing import Optional

from pydantic import Field

from models.base import AuditMixin, BaseDocument, DualIdMixin, SoftDeleteMixin
from models.enums import SiteContentType


class SiteContent(BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin):
    """Editable presentation content (collection: `site_content`)."""

    key: str = Field(min_length=1, max_length=120)  # unique content key
    content_type: SiteContentType = SiteContentType.TEXT

    # Bilingual editable values.
    value_id: Optional[str] = None
    value_en: Optional[str] = None
    # Non-bilingual config value (e.g., WhatsApp number, media url).
    value: Optional[str] = None

    is_published: bool = True
