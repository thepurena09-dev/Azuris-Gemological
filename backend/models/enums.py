"""Shared enums & status constants — Sprint 4.

Names preserved per the Business Blueprint / Architecture Lock. All values are
lowercase snake tokens; models use `use_enum_values=True` so stored values are
the raw strings.
"""

from enum import Enum


class Language(str, Enum):
    ID = "id"
    EN = "en"


class AdminRole(str, Enum):
    """Locked RBAC roles (Architecture Lock §6)."""

    SUPER_ADMIN = "SUPER_ADMIN"
    ADMINISTRATOR = "ADMINISTRATOR"
    CONTENT_MANAGER = "CONTENT_MANAGER"
    CUSTOMER_SERVICE = "CUSTOMER_SERVICE"


class GemstoneStatus(str, Enum):
    DRAFT = "draft"
    VERIFIED = "verified"
    PUBLISHED = "published"
    TRANSFERRED = "transferred"
    ARCHIVED = "archived"


class JewelryStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CertificateStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    REISSUED = "reissued"
    REVOKED = "revoked"


class WarrantyStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    VOID = "void"


class TransferStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MembershipCardStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class MediaEntityType(str, Enum):
    GEMSTONE = "gemstone"
    JEWELRY = "jewelry"
    CERTIFICATE = "certificate"
    WARRANTY = "warranty"
    MEMBERSHIP = "membership"
    CMS = "cms"


class MediaRole(str, Enum):
    MAIN = "main"
    GALLERY = "gallery"
    VIDEO = "video"
    THUMBNAIL = "thumbnail"


class SiteContentType(str, Enum):
    TEXT = "text"
    HTML = "html"
    IMAGE = "image"
    CONFIG = "config"


class VerificationMethod(str, Enum):
    QR_TOKEN = "qr_token"
    MANUAL_CODE = "manual_code"


class VerificationResult(str, Enum):
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    INVALID_CODE = "invalid_code"
    EXPIRED = "expired"
    REVOKED = "revoked"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    STATUS_CHANGE = "status_change"
    VERSION_CREATE = "version_create"


class SecurityEventType(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAIL = "login_fail"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    TOKEN_ROTATION = "token_rotation"
    ROLE_CHANGE = "role_change"
    SECURITY_CODE_REGENERATION = "security_code_regeneration"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
