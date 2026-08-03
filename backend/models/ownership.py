"""Ownership & verification entities — Sprint 4. Models only.

Security notes (Architecture Lock v1.1 §4):
- `verification_tokens` carry a high-entropy secret `token` (QR secret) distinct
  from the public `uuid`, plus a `security_code` used for exact-match manual
  verification. These secrets live ONLY here (never in logs).
- Ownership transfers keep the QR stable; the security code is rotated.
"""

from typing import Optional

from pydantic import Field

from models.base import AuditMixin, BaseDocument, DualIdMixin, SoftDeleteMixin
from models.enums import TransferStatus


class OwnershipTransfer(BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin):
    """Ownership lifecycle record (collection: `ownership_transfers`)."""

    gemstone_id: str  # gemstone uuid (QR persists across transfers)
    previous_owner_id: Optional[str] = None  # customer uuid
    new_owner_id: str  # customer uuid
    transfer_date: Optional[str] = None
    status: TransferStatus = TransferStatus.PENDING

    proof_media_id: Optional[str] = None       # uploaded proof document
    security_code_rotated: bool = False        # code regenerated on completion
    processed_by: Optional[str] = None         # admin id
    notes_id: Optional[str] = None
    notes_en: Optional[str] = None


class VerificationToken(BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin):
    """Verification secret record (collection: `verification_tokens`)."""

    gemstone_id: str                           # gemstone uuid
    certificate_id: Optional[str] = None       # certificate uuid
    token: str = Field(min_length=16)          # high-entropy QR secret (not the uuid)
    security_code: str = Field(min_length=4)   # exact-match manual code (secret)
    is_active: bool = True
    rotated_at: Optional[str] = None
