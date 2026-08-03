"""Sprint 2 health & CORS endpoint tests."""
import os
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/") if os.environ.get("REACT_APP_BACKEND_URL") else "https://azuris-sprint-book.preview.emergentagent.com"


def test_health_endpoint_returns_expected_payload():
    resp = requests.get(f"{BASE_URL}/api/health", timeout=15)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "azuris-platform"
    assert data.get("version") == "0.1.0"
    assert data.get("sprint") == 2
    assert data.get("environment") == "development"


def test_unknown_api_route_returns_404():
    resp = requests.get(f"{BASE_URL}/api/does-not-exist", timeout=15)
    assert resp.status_code == 404


def test_cors_spec_safe_wildcard_no_credentials():
    """With CORS_ORIGINS='*', the server must NOT combine wildcard with
    Access-Control-Allow-Credentials: true (per CORS spec)."""
    resp = requests.get(
        f"{BASE_URL}/api/health",
        headers={"Origin": "https://example.com"},
        timeout=15,
    )
    assert resp.status_code == 200
    acao = resp.headers.get("access-control-allow-origin")
    acac = resp.headers.get("access-control-allow-credentials")
    # Must expose an ACAO header
    assert acao is not None, f"Missing Access-Control-Allow-Origin. Headers={dict(resp.headers)}"
    # If wildcard is used, credentials must not be 'true'
    if acao == "*":
        assert (acac or "false").lower() != "true", (
            f"Invalid CORS: '*' combined with credentials=true. ACAC={acac}"
        )


def test_cors_preflight_options():
    resp = requests.options(
        f"{BASE_URL}/api/health",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
        timeout=15,
    )
    # Starlette CORSMiddleware returns 200 for valid preflight
    assert resp.status_code in (200, 204), f"Unexpected preflight status {resp.status_code}"
    acao = resp.headers.get("access-control-allow-origin")
    acac = resp.headers.get("access-control-allow-credentials")
    assert acao is not None
    if acao == "*":
        assert (acac or "false").lower() != "true"
