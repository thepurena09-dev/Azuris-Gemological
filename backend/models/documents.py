"""Versioned document artifacts — certificates, warranties, membership cards.

Sprint 4: models only. All three carry the VersionMixin (immutable superseded
versions retained). No PDF generation or business logic here.
"""

from typing import Optional

from pydantic import Field

from models.base import (
    AuditMixin,
    BaseDocument,
    DualIdMixin,
    SoftDeleteMixin,
    VersionMixin,
)
from models.enums import CertificateStatus, MembershipCardStatus, WarrantyStatus


class Certificate(
    BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin, VersionMixin
):
    """Verifiable identity document (collection: `certificates`)."""

    certificate_number: str = Field(min_length=1, max_length=64)  # unique, human-readable
    gemstone_id: str  # gemstone uuid
    status: CertificateStatus = CertificateStatus.DRAFT

    issued_at: Optional[str] = None
    issued_by: Optional[str] = None

    # Grading data
    color_grade: Optional[str] = Field(default=None, max_length=80)
    clarity_grade: Optional[str] = Field(default=None, max_length=80)
    cut_grade: Optional[str] = Field(default=None, max_length=80)
    carat_weight: Optional[float] = Field(default=None, gt=0)
    measurements: Optional[str] = Field(default=None, max_length=120)
    comments_id: Optional[str] = None
    comments_en: Optional[str] = None

    # Links (by uuid)
    pdf_media_id: Optional[str] = None
    verification_uuid: Optional[str] = None

    # Immutable snapshot of gemstone identity at issue time (FASE 3).
    # Ensures regenerated historical PDFs / archived versions never change when
    # the live gemstone record is later edited.
    gemstone_snapshot: Optional[dict] = None

    # Immutable snapshot of the active legality + authorised signatory at issue
    # time. Editing the admin Legality record later never alters issued PDFs.
    legality_snapshot: Optional[dict] = None


class Warranty(
    BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin, VersionMixin
):
    """Per-stone warranty (collection: `warranties`)."""

    warranty_number: Optional[str] = Field(default=None, max_length=64)
    gemstone_id: str  # gemstone uuid
    status: WarrantyStatus = WarrantyStatus.ACTIVE

    terms_id: str = Field(min_length=1)
    terms_en: str = Field(min_length=1)
    period_months: int = Field(ge=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    pdf_media_id: Optional[str] = None


class MembershipCard(
    BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin, VersionMixin
):
    """Premium ownership artifact with masked identity (collection: `membership_cards`)."""

    card_number: str = Field(min_length=1, max_length=64)
    customer_id: str  # customer uuid
    masked_name: str = Field(min_length=1, max_length=200)
    status: MembershipCardStatus = MembershipCardStatus.ACTIVE
    pdf_media_id: Optional[str] = None
