"""Global response envelope + exception handling — Sprint 8 (+ Sprint 9 context).

Provides:
- `RequestContextMiddleware` (pure ASGI): assigns a correlation id
  (`X-Request-ID`) per request, exposes it via `request.state.request_id` AND a
  ContextVar (so log writers can stamp it), and echoes it on every response.
- `ResponseEnvelopeMiddleware`: wraps successful JSON API responses in the
  standardized success envelope `{success, data, meta}` (binary/streaming
  responses, non-`/api` paths, health, and error responses are left untouched).
- Exception handlers that render EVERY error as the standardized error envelope
  `{success, error:{code,message,details?}, meta}` — internal errors are never
  leaked to the client.

All payload shapes come from `errors.py` (single source of truth).
"""

from __future__ import annotations

import json
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from core.context import get_request_id, new_request_id, request_id_ctx
from errors import (
    ApiError,
    ErrorCode,
    code_for_status,
    error_envelope,
    success_envelope,
)

logger = logging.getLogger("azuris.envelope")

REQUEST_ID_HEADER = "X-Request-ID"


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or get_request_id() or new_request_id()


class RequestContextMiddleware:
    """Pure-ASGI correlation-id middleware.

    Pure ASGI (not BaseHTTPMiddleware) so the ContextVar set here reliably
    propagates into the endpoint task and every log writer it calls.
    """

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        raw = headers.get(b"x-request-id")
        rid = raw.decode("latin-1") if raw else new_request_id()

        scope.setdefault("state", {})
        scope["state"]["request_id"] = rid
        token = request_id_ctx.set(rid)

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                mh = MutableHeaders(scope=message)
                mh[REQUEST_ID_HEADER] = rid
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            request_id_ctx.reset(token)


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """Wrap successful JSON API responses in the success envelope.

    Skipped for: non-API paths, the health probe, error responses (>=400,
    already enveloped by the handlers), and any non-JSON media type
    (PDF, PNG, images, streaming downloads).
    """

    def __init__(self, app, api_prefix: str = "/api") -> None:
        super().__init__(app)
        self.api_prefix = api_prefix
        self.health_path = f"{api_prefix}/health"

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        path = request.url.path
        if not path.startswith(self.api_prefix) or path == self.health_path:
            return response
        if response.status_code >= 400:
            return response
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return response

        body = b""
        async for chunk in response.body_iterator:  # type: ignore[attr-defined]
            body += chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")

        try:
            data = json.loads(body) if body else None
        except (ValueError, TypeError):
            return JSONResponse(content=None, status_code=response.status_code)

        wrapped = success_envelope(data, request_id=_request_id(request))
        new_response = JSONResponse(content=wrapped, status_code=response.status_code)
        new_response.headers[REQUEST_ID_HEADER] = _request_id(request)
        return new_response


# --------------------------------------------------------------------------- #
# Exception handlers
# --------------------------------------------------------------------------- #
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    payload = error_envelope(exc.code, exc.message, exc.details, _request_id(request))
    return JSONResponse(payload, status_code=exc.status_code, headers=exc.headers)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = exc.detail
    code = code_for_status(exc.status_code)
    details = None
    if isinstance(detail, dict):
        code = detail.get("code", code)
        message = detail.get("message", str(detail))
        details = detail.get("details")
    else:
        message = str(detail) if detail is not None else code
    payload = error_envelope(code, message, details, _request_id(request))
    return JSONResponse(payload, status_code=exc.status_code, headers=getattr(exc, "headers", None))


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(p) for p in err.get("loc", []) if p != "body"),
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        }
        for err in exc.errors()
    ]
    payload = error_envelope(
        ErrorCode.VALIDATION_ERROR,
        "One or more fields are invalid.",
        details,
        _request_id(request),
    )
    return JSONResponse(payload, status_code=422)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    rid = _request_id(request)
    # Full detail is logged server-side ONLY; the client gets a safe message.
    logger.exception("Unhandled error [request_id=%s] on %s %s", rid, request.method, request.url.path)
    payload = error_envelope(
        ErrorCode.INTERNAL_ERROR,
        "An internal error occurred. Please try again later.",
        request_id=rid,
    )
    return JSONResponse(payload, status_code=500)


def install_envelope(app: FastAPI, api_prefix: str = "/api") -> None:
    """Register the response envelope middleware + all exception handlers."""
    # add_middleware prepends: the LAST added is outer-most. RequestContext must
    # be outer (sets correlation id first) of the envelope wrapper.
    app.add_middleware(ResponseEnvelopeMiddleware, api_prefix=api_prefix)
    app.add_middleware(RequestContextMiddleware)

    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
