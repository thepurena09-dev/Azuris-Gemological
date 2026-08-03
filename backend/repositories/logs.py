"""Log repositories — append-only (Sprint 5).

Create + read only; update/delete raise (enforced by AppendOnlyRepository).
"""

from models.logs import AuditLog, SecurityLog, VerificationLog
from repositories.domain import AppendOnlyRepository


class AuditLogRepository(AppendOnlyRepository[AuditLog]):
    model = AuditLog
    collection_name = "audit_logs"


class VerificationLogRepository(AppendOnlyRepository[VerificationLog]):
    model = VerificationLog
    collection_name = "verification_logs"


class SecurityLogRepository(AppendOnlyRepository[SecurityLog]):
    model = SecurityLog
    collection_name = "security_logs"
