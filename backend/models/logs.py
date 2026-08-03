"""Logging entities — Sprint 4 (Architecture Lock v1.1 §11).

Three append-only collections. No log ever stores passwords, tokens, or
unmasked PII. These models carry only the dual-id + created_at (append-only:
no updated_at / soft-delete / versioning).
"""

from typing import Any, Optional

from pydantic import Field

from models.base import BaseDocument, DualIdMixin, utcnow_iso
from models.enums import AuditAction, SecurityEventType, VerificationMethod, VerificationResult


class AuditLog(BaseDocument, DualIdMixin):
    """All admin mutations with before/after snapshots (collection: `audit_logs`)."""

    actor_id: Optional[str] = None
    actor_role: Optional[str] = None
    action: AuditAction
    entity_type: str = Field(min_length=1, max_length=80)
    entity_id: Optional[str] = None
    before: Optional[dict[str, Any]] = None
    after: Optional[dict[str, Any]] = None
    correlation_id: Optional[str] = None
    created_at: str = Field(default_factory=utcnow_iso)


class VerificationLog(BaseDocument, DualIdMixin):
    """Every public verification attempt (collection: `verification_logs`).

    Minimal safe metadata only — no secrets. Certificate numbers are masked and
    IPs are stored hashed.
    """

    method: VerificationMethod
    result: VerificationResult
    gemstone_id: Optional[str] = None
    certificate_number_masked: Optional[str] = None
    ip_hash: Optional[str] = None
    user_agent: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: str = Field(default_factory=utcnow_iso)


class SecurityLog(BaseDocument, DualIdMixin):
    """Auth & security events (collection: `security_logs`)."""

    event_type: SecurityEventType
    actor_id: Optional[str] = None
    success: bool = True
    ip_hash: Optional[str] = None
    user_agent: Optional[str] = None
    detail: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: str = Field(default_factory=utcnow_iso)
