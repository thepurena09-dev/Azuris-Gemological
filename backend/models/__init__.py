"""Domain models package — Sprint 4.

Central export point for all locked entity models. Collection name mapping:
    admins              -> Admin
    customers           -> Customer
    gemstones           -> Gemstone
    jewelry             -> Jewelry
    certificates        -> Certificate
    warranties          -> Warranty
    ownership_transfers -> OwnershipTransfer
    verification_tokens -> VerificationToken
    membership_cards    -> MembershipCard
    media               -> Media
    site_content        -> SiteContent
    audit_logs          -> AuditLog
    verification_logs   -> VerificationLog
    security_logs       -> SecurityLog
"""

from models.base import (
    AuditMixin,
    BaseDocument,
    DualIdMixin,
    PyObjectId,
    SoftDeleteMixin,
    VersionMixin,
    new_uuid,
    utcnow_iso,
)
from models.catalog import Gemstone, Jewelry
from models.cms import SiteContent
from models.documents import Certificate, MembershipCard, Warranty
from models.logs import AuditLog, SecurityLog, VerificationLog
from models.media import Media
from models.ownership import OwnershipTransfer, VerificationToken
from models.people import Admin, Customer

# collection name -> model class
COLLECTION_MODELS: dict[str, type[BaseDocument]] = {
    "admins": Admin,
    "customers": Customer,
    "gemstones": Gemstone,
    "jewelry": Jewelry,
    "certificates": Certificate,
    "warranties": Warranty,
    "ownership_transfers": OwnershipTransfer,
    "verification_tokens": VerificationToken,
    "membership_cards": MembershipCard,
    "media": Media,
    "site_content": SiteContent,
    "audit_logs": AuditLog,
    "verification_logs": VerificationLog,
    "security_logs": SecurityLog,
}

__all__ = [
    "PyObjectId",
    "BaseDocument",
    "DualIdMixin",
    "AuditMixin",
    "SoftDeleteMixin",
    "VersionMixin",
    "new_uuid",
    "utcnow_iso",
    "Admin",
    "Customer",
    "Gemstone",
    "Jewelry",
    "Certificate",
    "Warranty",
    "OwnershipTransfer",
    "VerificationToken",
    "MembershipCard",
    "Media",
    "SiteContent",
    "AuditLog",
    "VerificationLog",
    "SecurityLog",
    "COLLECTION_MODELS",
]
