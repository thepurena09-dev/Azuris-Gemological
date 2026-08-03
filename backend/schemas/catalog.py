"""Catalog DTOs — gemstones & jewelry (Sprint 4)."""

from typing import Optional

from pydantic import BaseModel, Field

from models.enums import GemstoneStatus, JewelryStatus
from schemas.common import AuditFields


# ---------- Gemstone ----------
class GemstoneCreate(BaseModel):
    name_id: str = Field(min_length=1, max_length=200)
    name_en: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    gemstone_type: str = Field(min_length=1, max_length=100)
    weight_carat: float = Field(gt=0)
    color: Optional[str] = None
    clarity: Optional[str] = None
    cut: Optional[str] = None
    shape: Optional[str] = None
    dimensions_mm: Optional[str] = None
    origin: Optional[str] = None
    treatment: Optional[str] = None
    description_id: Optional[str] = None
    description_en: Optional[str] = None
    media_ids: list[str] = Field(default_factory=list)


class GemstoneUpdate(BaseModel):
    name_id: Optional[str] = Field(default=None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(default=None, min_length=1, max_length=200)
    category: Optional[str] = None
    gemstone_type: Optional[str] = None
    weight_carat: Optional[float] = Field(default=None, gt=0)
    color: Optional[str] = None
    clarity: Optional[str] = None
    cut: Optional[str] = None
    shape: Optional[str] = None
    dimensions_mm: Optional[str] = None
    origin: Optional[str] = None
    treatment: Optional[str] = None
    description_id: Optional[str] = None
    description_en: Optional[str] = None
    status: Optional[GemstoneStatus] = None
    active_owner_id: Optional[str] = None
    certificate_id: Optional[str] = None
    media_ids: Optional[list[str]] = None


class GemstoneResponse(AuditFields):
    id: Optional[str] = None
    uuid: str
    name_id: str
    name_en: str
    category: str
    gemstone_type: str
    weight_carat: float
    color: Optional[str] = None
    clarity: Optional[str] = None
    cut: Optional[str] = None
    shape: Optional[str] = None
    dimensions_mm: Optional[str] = None
    origin: Optional[str] = None
    treatment: Optional[str] = None
    description_id: Optional[str] = None
    description_en: Optional[str] = None
    status: GemstoneStatus
    active_owner_id: Optional[str] = None
    certificate_id: Optional[str] = None
    media_ids: list[str] = Field(default_factory=list)


# ---------- Jewelry ----------
class JewelryCreate(BaseModel):
    name_id: str = Field(min_length=1, max_length=200)
    name_en: str = Field(min_length=1, max_length=200)
    jewelry_type: str = Field(min_length=1, max_length=100)
    material: str = Field(min_length=1, max_length=120)
    gemstone_ids: list[str] = Field(default_factory=list)
    weight_grams: Optional[float] = Field(default=None, gt=0)
    dimensions_mm: Optional[str] = None
    description_id: Optional[str] = None
    description_en: Optional[str] = None
    media_ids: list[str] = Field(default_factory=list)


class JewelryUpdate(BaseModel):
    name_id: Optional[str] = None
    name_en: Optional[str] = None
    jewelry_type: Optional[str] = None
    material: Optional[str] = None
    gemstone_ids: Optional[list[str]] = None
    weight_grams: Optional[float] = Field(default=None, gt=0)
    dimensions_mm: Optional[str] = None
    description_id: Optional[str] = None
    description_en: Optional[str] = None
    status: Optional[JewelryStatus] = None
    media_ids: Optional[list[str]] = None


class JewelryResponse(AuditFields):
    id: Optional[str] = None
    uuid: str
    name_id: str
    name_en: str
    jewelry_type: str
    material: str
    gemstone_ids: list[str] = Field(default_factory=list)
    weight_grams: Optional[float] = None
    dimensions_mm: Optional[str] = None
    description_id: Optional[str] = None
    description_en: Optional[str] = None
    status: JewelryStatus
    media_ids: list[str] = Field(default_factory=list)
