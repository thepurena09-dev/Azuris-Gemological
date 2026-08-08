"""Formalized error model & response envelope helpers — Sprint 8.

Single source of truth for:
- Standardized error codes (stable, machine-readable).
- The success / error response envelope shapes.
- Generic, non-leaking HTTP error factories reused across the app
  (auth uses `unauthorized`/`forbidden`; nothing here reveals internals).

The global exception handlers + response-wrapping middleware live in
`core/envelope.py` and build their payloads exclusively from this module so the
contract stays consistent everywhere.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException, status


# --------------------------------------------------------------------------- #
# Stable error codes (contract) — never leak internal details to clients.
# --------------------------------------------------------------------------- #
class ErrorCode:
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    ERROR = "ERROR"


# HTTP status -> stable code mapping (used when an HTTPException carries no code).
STATUS_CODE_MAP: dict[int, str] = {
    400: ErrorCode.BAD_REQUEST,
    401: ErrorCode.UNAUTHORIZED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    405: ErrorCode.METHOD_NOT_ALLOWED,
    409: ErrorCode.CONFLICT,
    422: ErrorCode.VALIDATION_ERROR,
    429: ErrorCode.RATE_LIMITED,
    500: ErrorCode.INTERNAL_ERROR,
    503: ErrorCode.SERVICE_UNAVAILABLE,
}


def code_for_status(status_code: int) -> str:
    return STATUS_CODE_MAP.get(status_code, ErrorCode.ERROR)


# --------------------------------------------------------------------------- #
# Envelope builders — the ONE place response shapes are defined.
# --------------------------------------------------------------------------- #
def success_envelope(data: Any, request_id: Optional[str] = None, meta_extra: Optional[dict] = None) -> dict:
    meta: dict[str, Any] = {}
    if request_id:
        meta["request_id"] = request_id
    if meta_extra:
        meta.update(meta_extra)
    return {"success": True, "data": data, "meta": meta}


def error_envelope(
    code: str,
    message: str,
    details: Optional[list] = None,
    request_id: Optional[str] = None,
) -> dict:
    error: dict[str, Any] = {"code": code, "message": message}
    if details:
        error["details"] = details
    meta: dict[str, Any] = {}
    if request_id:
        meta["request_id"] = request_id
    return {"success": False, "error": error, "meta": meta}


# --------------------------------------------------------------------------- #
# Application exception — lets services raise structured, coded errors.
# --------------------------------------------------------------------------- #
class ApiError(HTTPException):
    """HTTPException carrying a stable error code + optional field details.

    Handlers render it into the standardized error envelope. Messages must be
    safe for clients (no stack traces / internal identifiers).
    """

    def __init__(
        self,
        status_code: int,
        code: Optional[str] = None,
        message: str = "Request could not be processed.",
        details: Optional[list] = None,
        headers: Optional[dict] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.code = code or code_for_status(status_code)
        self.message = message
        self.details = details


# --------------------------------------------------------------------------- #
# Generic HTTP error factories (backward-compatible; used by auth/verify).
# --------------------------------------------------------------------------- #
def unauthorized(detail: str = "Invalid credentials") -> HTTPException:
    """Generic 401 — never reveals whether email or password was wrong."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(detail: str = "Not permitted") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
