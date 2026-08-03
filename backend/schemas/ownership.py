"""Ownership & verification DTOs — Sprint 4.

Response DTOs deliberately OMIT the secret `token` and `security_code`. Public
verification input schemas support both locked methods (QR token OR
certificate_number + security_code).
"""

from typing import Optional

from pydantic import BaseModel, Field

from models.enums import TransferStatus
from schemas.common import AuditFields


# ---------- Ownership Transfer ----------
class OwnershipTransferCreate(BaseModel):
    gemstone_id: str
    new_owner_id: str
    previous_owner_id: Optional[str] = None
    transfer_date: Optional[str] = None
    proof_media_id: Optional[str] = None
    notes_id: Optional[str] = None
    notes_en: Optional[str] = None


class OwnershipTransferUpdate(BaseModel):
    status: Optional[TransferStatus] = None
    transfer_date: Optional[str] = None
    proof_media_id: Optional[str] = None
    notes_id: Optional[str] = None
    notes_en: Optional[str] = None


class OwnershipTransferResponse(AuditFields):
    id: Optional[str] = None
    uuid: str
    gemstone_id: str
    previous_owner_id: Optional[str] = None
    new_owner_id: str
    transfer_date: Optional[str] = None
    status: TransferStatus
    proof_media_id: Optional[str] = None
    security_code_rotated: bool
    processed_by: Optional[str] = None
    notes_id: Optional[str] = None
    notes_en: Optional[str] = None


# ---------- Verification Token (admin-facing, secrets omitted) ----------
class VerificationTokenResponse(AuditFields):
    id: Optional[str] = None
    uuid: str
    gemstone_id: str
    certificate_id: Optional[str] = None
    is_active: bool
    rotated_at: Optional[str] = None
    # token & security_code are NEVER exposed.


# ---------- Public verification input (locked dual methods) ----------
class VerifyByToken(BaseModel):
    token: str = Field(min_length=16)


class VerifyByCode(BaseModel):
    certificate_number: str = Field(min_length=1, max_length=64)
    security_code: str = Field(min_length=4)


class VerificationResultResponse(BaseModel):
    """Masked, public-safe verification outcome."""

    verified: bool
    gemstone_uuid: Optional[str] = None
    gemstone_name_id: Optional[str] = None
    gemstone_name_en: Optional[str] = None
    certificate_number: Optional[str] = None
    owner_masked_name: Optional[str] = None
    message_id: str
    message_en: str
