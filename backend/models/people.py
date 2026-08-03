"""People entities — admins & customers (Sprint 4).

Models only. No auth logic, no CRUD. Secrets live only on the model
(`password_hash`) and MUST never be returned by response schemas.
"""

from typing import Optional

from pydantic import EmailStr, Field

from models.base import AuditMixin, BaseDocument, DualIdMixin, SoftDeleteMixin
from models.enums import AdminRole


class Admin(BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin):
    """Closed-access operator account (collection: `admins`)."""

    email: EmailStr
    password_hash: str
    full_name: str = Field(min_length=1, max_length=160)
    role: AdminRole = AdminRole.CUSTOMER_SERVICE
    is_active: bool = True
    last_login: Optional[str] = None
    last_activity: Optional[str] = None


class Customer(BaseDocument, DualIdMixin, AuditMixin, SoftDeleteMixin):
    """Owner registry (collection: `customers`). PII masked in public responses."""

    full_name: str = Field(min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=40)
    address_id: Optional[str] = None
    address_en: Optional[str] = None
    privacy_consent: bool = False
    consent_at: Optional[str] = None
    # History of owned gemstone references (public uuids).
    owned_gemstone_ids: list[str] = Field(default_factory=list)
    notes_id: Optional[str] = None
    notes_en: Optional[str] = None
