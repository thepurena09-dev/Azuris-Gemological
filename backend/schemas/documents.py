"""Document DTOs — certificate, warranty, membership card (Sprint 4)."""

from typing import Optional

from pydantic import BaseModel, Field

from models.enums import CertificateStatus, MembershipCardStatus, WarrantyStatus
from schemas.common import AuditFields, VersionFields


# ---------- Certificate ----------
class CertificateCreate(BaseModel):
    certificate_number: str = Field(min_length=1, max_length=64)
    gemstone_id: str
    color_grade: Optional[str] = None
    clarity_grade: Optional[str] = None
    cut_grade: Optional[str] = None
    carat_weight: Optional[float] = Field(default=None, gt=0)
    measurements: Optional[str] = None
    comments_id: Optional[str] = None
    comments_en: Optional[str] = None


class CertificateUpdate(BaseModel):
    status: Optional[CertificateStatus] = None
    color_grade: Optional[str] = None
    clarity_grade: Optional[str] = None
    cut_grade: Optional[str] = None
    carat_weight: Optional[float] = Field(default=None, gt=0)
    measurements: Optional[str] = None
    comments_id: Optional[str] = None
    comments_en: Optional[str] = None
    pdf_media_id: Optional[str] = None


class CertificateResponse(AuditFields, VersionFields):
    id: Optional[str] = None
    uuid: str
    certificate_number: str
    gemstone_id: str
    status: CertificateStatus
    issued_at: Optional[str] = None
    issued_by: Optional[str] = None
    color_grade: Optional[str] = None
    clarity_grade: Optional[str] = None
    cut_grade: Optional[str] = None
    carat_weight: Optional[float] = None
    measurements: Optional[str] = None
    comments_id: Optional[str] = None
    comments_en: Optional[str] = None
    pdf_media_id: Optional[str] = None
    verification_uuid: Optional[str] = None


# ---------- Warranty ----------
class WarrantyCreate(BaseModel):
    gemstone_id: str
    warranty_number: Optional[str] = None
    terms_id: str = Field(min_length=1)
    terms_en: str = Field(min_length=1)
    period_months: int = Field(ge=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class WarrantyUpdate(BaseModel):
    status: Optional[WarrantyStatus] = None
    terms_id: Optional[str] = None
    terms_en: Optional[str] = None
    period_months: Optional[int] = Field(default=None, ge=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    pdf_media_id: Optional[str] = None


class WarrantyResponse(AuditFields, VersionFields):
    id: Optional[str] = None
    uuid: str
    warranty_number: Optional[str] = None
    gemstone_id: str
    status: WarrantyStatus
    terms_id: str
    terms_en: str
    period_months: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    pdf_media_id: Optional[str] = None


# ---------- Membership Card ----------
class MembershipCardCreate(BaseModel):
    card_number: str = Field(min_length=1, max_length=64)
    customer_id: str
    masked_name: str = Field(min_length=1, max_length=200)


class MembershipCardUpdate(BaseModel):
    status: Optional[MembershipCardStatus] = None
    masked_name: Optional[str] = None
    pdf_media_id: Optional[str] = None


class MembershipCardResponse(AuditFields, VersionFields):
    id: Optional[str] = None
    uuid: str
    card_number: str
    customer_id: str
    masked_name: str
    status: MembershipCardStatus
    pdf_media_id: Optional[str] = None
