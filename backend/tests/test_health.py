"""Sprint 1 health endpoint tests."""
import os
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://azuris-sprint-book.preview.emergentagent.com").rstrip("/")


def test_health_endpoint_returns_expected_payload():
    resp = requests.get(f"{BASE_URL}/api/health", timeout=15)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "azuris-platform"
    assert data.get("version") == "0.1.0"
    assert data.get("sprint") == 1


def test_unknown_api_route_returns_404():
    resp = requests.get(f"{BASE_URL}/api/does-not-exist", timeout=15)
    assert resp.status_code == 404
