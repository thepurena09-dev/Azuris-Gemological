"""Log DTOs — read-only responses (Sprint 4).

Append-only collections are surfaced (read) in a later sprint; these response
shapes contain only safe, non-secret fields.
"""

from typing import Any, Optional

from pydantic import BaseModel

from models.enums import (
    AuditAction,
    SecurityEventType,
    VerificationMethod,
    VerificationResult,
)


class AuditLogResponse(BaseModel):
    id: Optional[str] = None
    uuid: str
    actor_id: Optional[str] = None
    actor_role: Optional[str] = None
    action: AuditAction
    entity_type: str
    entity_id: Optional[str] = None
    before: Optional[dict[str, Any]] = None
    after: Optional[dict[str, Any]] = None
    correlation_id: Optional[str] = None
    created_at: str


class VerificationLogResponse(BaseModel):
    id: Optional[str] = None
    uuid: str
    method: VerificationMethod
    result: VerificationResult
    gemstone_id: Optional[str] = None
    certificate_number_masked: Optional[str] = None
    ip_hash: Optional[str] = None
    user_agent: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: str


class SecurityLogResponse(BaseModel):
    id: Optional[str] = None
    uuid: str
    event_type: SecurityEventType
    actor_id: Optional[str] = None
    success: bool
    ip_hash: Optional[str] = None
    user_agent: Optional[str] = None
    detail: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: str
