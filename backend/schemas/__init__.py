"""DTO schemas package — Sprint 4.

Request (Create/Update) and Response contracts for the locked entities. Response
schemas never expose secrets (password_hash, token, security_code) or raw ObjectId.
"""

from schemas.catalog import (
    GemstoneCreate,
    GemstoneResponse,
    GemstoneUpdate,
    JewelryCreate,
    JewelryResponse,
    JewelryUpdate,
)
from schemas.cms import SiteContentCreate, SiteContentResponse, SiteContentUpdate
from schemas.common import (
    AuditFields,
    PaginatedResponse,
    PaginationParams,
    VersionFields,
)
from schemas.documents import (
    CertificateCreate,
    CertificateResponse,
    CertificateUpdate,
    MembershipCardCreate,
    MembershipCardResponse,
    MembershipCardUpdate,
    WarrantyCreate,
    WarrantyResponse,
    WarrantyUpdate,
)
from schemas.logs import (
    AuditLogResponse,
    SecurityLogResponse,
    VerificationLogResponse,
)
from schemas.media import MediaCreate, MediaResponse, MediaUpdate
from schemas.ownership import (
    OwnershipTransferCreate,
    OwnershipTransferResponse,
    OwnershipTransferUpdate,
    VerificationResultResponse,
    VerificationTokenResponse,
    VerifyByCode,
    VerifyByToken,
)
from schemas.people import (
    AdminCreate,
    AdminResponse,
    AdminUpdate,
    CustomerCreate,
    CustomerPublicResponse,
    CustomerResponse,
    CustomerUpdate,
)

__all__ = [
    "AuditFields",
    "VersionFields",
    "PaginationParams",
    "PaginatedResponse",
    "GemstoneCreate",
    "GemstoneUpdate",
    "GemstoneResponse",
    "JewelryCreate",
    "JewelryUpdate",
    "JewelryResponse",
    "AdminCreate",
    "AdminUpdate",
    "AdminResponse",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerPublicResponse",
    "CertificateCreate",
    "CertificateUpdate",
    "CertificateResponse",
    "WarrantyCreate",
    "WarrantyUpdate",
    "WarrantyResponse",
    "MembershipCardCreate",
    "MembershipCardUpdate",
    "MembershipCardResponse",
    "OwnershipTransferCreate",
    "OwnershipTransferUpdate",
    "OwnershipTransferResponse",
    "VerificationTokenResponse",
    "VerifyByToken",
    "VerifyByCode",
    "VerificationResultResponse",
    "MediaCreate",
    "MediaUpdate",
    "MediaResponse",
    "SiteContentCreate",
    "SiteContentUpdate",
    "SiteContentResponse",
    "AuditLogResponse",
    "VerificationLogResponse",
    "SecurityLogResponse",
]
