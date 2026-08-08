"""Audit logging helper — FASE 2. Reuses the existing append-only audit_logs.

Never records secrets, tokens, passwords, or unmasked PII in before/after.
"""

from typing import Any, Optional

from core.context import get_request_id
from models.enums import AuditAction
from models.logs import AuditLog
from repositories.logs import AuditLogRepository


async def write_audit_log(
    db: Any,
    *,
    actor_id: Optional[str],
    actor_role: Optional[str],
    action: AuditAction,
    entity_type: str,
    entity_id: Optional[str] = None,
    before: Optional[dict] = None,
    after: Optional[dict] = None,
) -> None:
    log = AuditLog(
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
        correlation_id=get_request_id(),
    )
    await AuditLogRepository(db).create(log)
