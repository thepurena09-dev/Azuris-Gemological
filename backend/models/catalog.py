"""Catalog entities — gemstones & jewelry (Sprint 4). Models only."""

from typing import Optional

from pydantic import Field

from models.base import AuditMixin, BaseDocument, DualIdMixin, SoftDeleteMixin
from models.enums import GemstoneStatus, JewelryStatus


class Gemstone(BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin):
    """Core catalog asset (collection: `gemstones`)."""

    # Bilingual identity (flat *_id/*_en convention per media schema).
    name_id: str = Field(min_length=1, max_length=200)
    name_en: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    gemstone_type: str = Field(min_length=1, max_length=100)
    # Manual 3-letter gemstone code (admin-defined). Part of the certificate
    # number AGR-{CODE}-{SEQ}-{YY}. Empty for legacy records; required at issuance.
    gem_code: Optional[str] = Field(default=None, max_length=3)

    # Specifications
    weight_carat: float = Field(gt=0)
    color: Optional[str] = Field(default=None, max_length=100)
    transparency: Optional[str] = Field(default=None, max_length=100)
    clarity: Optional[str] = Field(default=None, max_length=100)
    cut: Optional[str] = Field(default=None, max_length=100)
    shape: Optional[str] = Field(default=None, max_length=100)
    dimensions_mm: Optional[str] = Field(default=None, max_length=100)
    origin: Optional[str] = Field(default=None, max_length=120)
    treatment: Optional[str] = Field(default=None, max_length=200)
    examiner: Optional[str] = Field(default=None, max_length=200)
    conclusion: Optional[str] = Field(default=None, max_length=500)
    # Optional per-gemstone title size for the presentation page; blank uses the automatic layout.
    presentation_title_size: Optional[float] = Field(default=None, ge=8, le=22)
    # Optional per-field certificate typography overrides. Empty means automatic sizing.
    certificate_text_sizes: dict[str, float] = Field(default_factory=dict)
    description_id: Optional[str] = None
    description_en: Optional[str] = None

    # Lifecycle & relationships (references by public uuid)
    status: GemstoneStatus = GemstoneStatus.DRAFT
    active_owner_id: Optional[str] = None      # customer uuid
    certificate_id: Optional[str] = None       # certificate uuid
    media_ids: list[str] = Field(default_factory=list)


class Jewelry(BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin):
    """Jewelry piece composed of one or more gemstones (collection: `jewelry`)."""

    name_id: str = Field(min_length=1, max_length=200)
    name_en: str = Field(min_length=1, max_length=200)
    jewelry_type: str = Field(min_length=1, max_length=100)
    material: str = Field(min_length=1, max_length=120)

    gemstone_ids: list[str] = Field(default_factory=list)  # gemstone uuids
    weight_grams: Optional[float] = Field(default=None, gt=0)
    dimensions_mm: Optional[str] = Field(default=None, max_length=100)
    description_id: Optional[str] = None
    description_en: Optional[str] = None

    status: JewelryStatus = JewelryStatus.DRAFT
    media_ids: list[str] = Field(default_factory=list)
