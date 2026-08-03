"""Shared DTO helpers — Sprint 4.

Response models expose the public `id` (str) + `uuid` and never leak secrets
(password_hash, token, security_code) or ObjectId. Generic pagination wrapper.
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base for response DTOs (accepts model instances / dicts)."""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class AuditFields(ORMModel):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class VersionFields(ORMModel):
    version: int = 1
    is_current: bool = True
    created_version_at: Optional[str] = None
    created_version_by: Optional[str] = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)
    sort_by: str = "created_at"
    sort_dir: int = Field(default=-1, ge=-1, le=1)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
