"""Shared error helpers — generic, non-leaking auth errors (Sprint 6).

Full response-envelope + global handlers are formalized in Sprint 8; this module
provides only the generic 401/403 used by authentication.
"""

from fastapi import HTTPException, status


def unauthorized(detail: str = "Invalid credentials") -> HTTPException:
    """Generic 401 — never reveals whether email or password was wrong."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(detail: str = "Not permitted") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
