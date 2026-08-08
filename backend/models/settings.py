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

    # --- CMS visual controls (POST-BATCH D final UI polish) ---
    # Image URLs may reference the Media Library (public `/api/media/{uuid}`) or an
    # approved external asset URL. No binaries stored here (reuse Sprint 10/14 media).
    login_image_url: str = Field(
        default="https://images.unsplash.com/photo-1783771686998-0af6c0efec6e?crop=entropy&cs=srgb&fm=jpg&q=90&w=1400",
        max_length=1000,
    )
    login_image_alt_id: Optional[str] = Field(default="Batu safir premium", max_length=200)
    login_image_alt_en: Optional[str] = Field(default="Premium sapphire gemstone", max_length=200)

    process_image_url: str = Field(
        default="https://images.unsplash.com/photo-1628058494685-6c2f796ac24a?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        max_length=1000,
    )
    process_image_alt_id: Optional[str] = Field(default="Pemeriksaan gemologi profesional", max_length=200)
    process_image_alt_en: Optional[str] = Field(default="Professional gemological examination", max_length=200)
    process_image_show: bool = True

    membership_show: bool = True
    membership_title_id: Optional[str] = Field(default=None, max_length=160)
    membership_title_en: Optional[str] = Field(default=None, max_length=160)
    membership_desc_id: Optional[str] = Field(default=None, max_length=600)
    membership_desc_en: Optional[str] = Field(default=None, max_length=600)
    membership_cta_id: Optional[str] = Field(default=None, max_length=80)
    membership_cta_en: Optional[str] = Field(default=None, max_length=80)
    membership_link: str = Field(default="/membership", max_length=200)

    # --- Dashboard background (CMS visual control) ---
    # When custom is disabled, the admin dashboard keeps the approved marble default.
    dashboard_bg_enabled: bool = False
    dashboard_bg_url: str = Field(default="", max_length=1000)
    dashboard_bg_opacity: int = Field(default=10, ge=0, le=100)
    dashboard_bg_fit: str = Field(default="cover", max_length=10)
    dashboard_bg_blur: int = Field(default=0, ge=0, le=40)

    # --- Admin login page background (mirror of the dashboard control) ---
    login_bg_enabled: bool = False
    login_bg_url: str = Field(default="", max_length=1000)
    login_bg_opacity: int = Field(default=10, ge=0, le=100)
    login_bg_fit: str = Field(default="cover", max_length=10)
    login_bg_blur: int = Field(default=0, ge=0, le=40)

    # --- Homepage hero background (mirror of the dashboard control) ---
    home_bg_enabled: bool = False
    home_bg_url: str = Field(default="", max_length=1000)
    home_bg_opacity: int = Field(default=20, ge=0, le=100)
    home_bg_fit: str = Field(default="cover", max_length=10)
    home_bg_blur: int = Field(default=0, ge=0, le=40)

    # --- Homepage hero gemstone photos (defaults match the current design) ---
    home_gem_diamond_url: str = Field(
        default="https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        max_length=1000,
    )
    home_gem_ruby_url: str = Field(
        default="https://images.unsplash.com/photo-1705575490492-4e91fd97bbb4?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        max_length=1000,
    )
    home_gem_sapphire_url: str = Field(
        default="https://static.prod-images.emergentagent.com/jobs/0d8170c5-08d6-45ed-9937-114710780b07/images/11e5956f874718e6db198dda556242a9e59a93fb2ea1cd0b3fe0d77cc5e02724.jpeg",
        max_length=1000,
    )
    home_gem_emerald_url: str = Field(
        default="https://static.prod-images.emergentagent.com/jobs/6572b450-f0e7-4d20-83da-0f44a5e44dfd/images/8138fec9a0cfedc223c4896ebd58852071928246a1875cecdb3ce5aaebe929ad.jpeg",
        max_length=1000,
    )
