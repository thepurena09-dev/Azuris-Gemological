"""Repository layer package — Sprint 5.

The ONLY layer permitted to communicate with MongoDB. Exposes the generic
foundation plus one repository per locked collection, and the atomic counter.
"""

from repositories.base import BaseRepository
from repositories.catalog import GemstoneRepository, JewelryRepository
from repositories.cms import SiteContentRepository
from repositories.counter import CounterRepository
from repositories.documents import (
    CertificateRepository,
    MembershipCardRepository,
    WarrantyRepository,
)
from repositories.domain import AppendOnlyRepository, DomainRepository
from repositories.logs import (
    AuditLogRepository,
    SecurityLogRepository,
    VerificationLogRepository,
)
from repositories.media import MediaRepository
from repositories.ownership import (
    OwnershipTransferRepository,
    VerificationTokenRepository,
)
from repositories.people import AdminRepository, CustomerRepository

__all__ = [
    "BaseRepository",
    "DomainRepository",
    "AppendOnlyRepository",
    "CounterRepository",
    "GemstoneRepository",
    "JewelryRepository",
    "AdminRepository",
    "CustomerRepository",
    "CertificateRepository",
    "WarrantyRepository",
    "MembershipCardRepository",
    "OwnershipTransferRepository",
    "VerificationTokenRepository",
    "MediaRepository",
    "SiteContentRepository",
    "AuditLogRepository",
    "VerificationLogRepository",
    "SecurityLogRepository",
]
