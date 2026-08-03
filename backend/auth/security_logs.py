"""Security event logging helper — Sprint 6.

Writes auth events to `security_logs` (append-only). Never records secrets,
tokens, passwords, or unmasked PII. IPs are stored hashed.
"""

import hashlib
from typing import Any, Optional

from fastapi import Request

from models.enums import SecurityEventType
from models.logs import SecurityLog
from repositories.logs import SecurityLogRepository


def hash_ip(ip: Optional[str]) -> Optional[str]:
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


def client_context(request: Request) -> tuple[Optional[str], Optional[str]]:
    ip = request.client.host if request and request.client else None
    ua = request.headers.get("user-agent") if request else None
    return hash_ip(ip), ua


async def write_security_log(
    db: Any,
    event_type: SecurityEventType,
    *,
    request: Optional[Request] = None,
    actor_id: Optional[str] = None,
    success: bool = True,
    detail: Optional[str] = None,
) -> None:
    ip_hash, user_agent = client_context(request) if request else (None, None)
    log = SecurityLog(
        event_type=event_type,
        actor_id=actor_id,
        success=success,
        ip_hash=ip_hash,
        user_agent=user_agent,
        detail=detail,
    )
    await SecurityLogRepository(db).create(log)
