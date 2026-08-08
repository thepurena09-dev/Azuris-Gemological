"""Request-scoped context — Sprint 9.

Holds the per-request correlation id in a ContextVar so any layer (log writers,
services) can stamp it without threading `request` through every call. The id is
set by the pure-ASGI `RequestContextMiddleware` (Sprint 8) and read here.
"""

from __future__ import annotations

import contextvars
import uuid
from typing import Optional

request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)


def get_request_id() -> Optional[str]:
    return request_id_ctx.get()


def set_request_id(value: str):
    return request_id_ctx.set(value)


def new_request_id() -> str:
    return uuid.uuid4().hex
