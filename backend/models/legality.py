"""Legality credential entities — FASE 2 (Client Revision).

New public-facing legality/gemological credential managed via admin CMS.
Reuses existing base conventions (dual-id, audit, soft-delete). No secrets.
"""

from typing import Optional

from pydantic import Field

from models.base import (
    AuditMixin,
    BaseDocument,
    DualIdMixin,
    SoftDeleteMixin,
    utcnow_iso,
)


class LegalityCredential(BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin):
    """Azuris legality/credential record (collection: `legality_credentials`)."""

    certificate_name: str = Field(min_length=1, max_length=200)
    holder_name: Optional[str] = Field(default=None, max_length=200)
    certificate_number: Optional[str] = Field(default=None, max_length=120)
    issuer: Optional[str] = Field(default=None, max_length=200)
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    # aktif | tidak_aktif | kedaluwarsa | dalam_pembaruan
    status: str = Field(default="aktif", max_length=40)
    short_description: Optional[str] = None

    document_id: Optional[str] = None  # legality_documents uuid
    document_filename: Optional[str] = None
    document_content_type: Optional[str] = None
    public_download_allowed: bool = False

    # draft | published
    publication_status: str = Field(default="draft", max_length=20)
    published_at: Optional[str] = None


class LegalityDocument(BaseDocument, DualIdMixin):
    """Stored legality document bytes (collection: `legality_documents`)."""

    content_type: str
    filename: str
    size: int = Field(ge=0)
    data_b64: str
    created_at: str = Field(default_factory=utcnow_iso)
