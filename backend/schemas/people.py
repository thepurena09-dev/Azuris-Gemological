"""People DTOs — admin & customer (Sprint 4).

Admin responses NEVER include `password_hash`. Customer responses include a
`masked_name` variant for public/limited contexts.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from models.enums import AdminRole
from schemas.common import AuditFields


# ---------- Admin ----------
class AdminCreate(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)  # hashed by auth sprint
    full_name: str = Field(min_length=1, max_length=160)
    role: AdminRole = AdminRole.CUSTOMER_SERVICE


class AdminUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=160)
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None


class AdminResponse(AuditFields):
    id: Optional[str] = None
    uuid: str
    email: str
    full_name: str
    role: AdminRole
    is_active: bool
    last_login: Optional[str] = None
    last_activity: Optional[str] = None


# ---------- Customer ----------
class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=40)
    address_id: Optional[str] = None
    address_en: Optional[str] = None
    privacy_consent: bool = False
    notes_id: Optional[str] = None
    notes_en: Optional[str] = None


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=40)
    address_id: Optional[str] = None
    address_en: Optional[str] = None
    privacy_consent: Optional[bool] = None
    notes_id: Optional[str] = None
    notes_en: Optional[str] = None


class CustomerResponse(AuditFields):
    id: Optional[str] = None
    uuid: str
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_id: Optional[str] = None
    address_en: Optional[str] = None
    privacy_consent: bool
    consent_at: Optional[str] = None
    owned_gemstone_ids: list[str] = Field(default_factory=list)


class CustomerPublicResponse(BaseModel):
    """Masked, public-safe customer projection (no contact/PII)."""

    uuid: str
    masked_name: str
