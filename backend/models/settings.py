"""Business/site settings — FASE 2. Single-document configuration.

Centralized source of truth for admin-managed public contact settings
(e.g. WhatsApp business number). No secrets.
"""

from typing import Optional

from pydantic import Field

from models.base import AuditMixin, BaseDocument


class BusinessSettings(BaseDocument, AuditMixin):
    """Single-doc business settings (collection: `site_settings`, key=`business`)."""

    key: str = Field(default="business", max_length=40)
    whatsapp_number: str = Field(default="6287812128884", max_length=32)
    whatsapp_label: Optional[str] = Field(default=None, max_length=120)
    whatsapp_enabled: bool = True
