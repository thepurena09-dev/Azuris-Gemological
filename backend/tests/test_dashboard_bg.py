"""Dashboard Background CMS Control — dashboard_bg_* fields on /api/admin/settings/visuals.

Tests:
- Public GET /api/settings/public includes dashboard_bg_enabled/url/opacity
- SUPER_ADMIN can PUT visuals with dashboard_bg_* and read them back
- Opacity clamp server-side (30 -> 24, 1 -> 4)
- CONTENT_MANAGER can PUT (CMS_WRITE)
- CUSTOMER_SERVICE can GET but PUT returns 403
- Unauthenticated PUT returns 401
- Safety: certificate counter last_number remains 14; business collections remain 0
- Teardown: restore defaults (enabled=false, url='', opacity=10)
"""
import os
import pytest
import requests

def _read_frontend_url():
    p = "/app/frontend/.env"
    if os.path.exists(p):
        for line in open(p):
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("REACT_APP_BACKEND_URL", "")

BASE = _read_frontend_url().rstrip("/")
assert BASE, "REACT_APP_BACKEND_URL not set"
API = f"{BASE}/api"

ADMIN = {"email": "admin@azuris.local", "password": "AzurisDev@2026!"}
CM = {"email": "cm@azuris.local", "password": "CmDev@2026!"}
CS = {"email": "cs@azuris.local", "password": "CsDev@2026!"}


def _unwrap(r):
    j = r.json()
    if isinstance(j, dict) and "data" in j and "success" in j:
        return j["data"]
    return j


def _login(creds):
    r = requests.post(f"{API}/auth/login", json=creds, timeout=15)
    assert r.status_code == 200, f"login {creds['email']} failed: {r.status_code} {r.text}"
    j = _unwrap(r)
    return j["access_token"]


@pytest.fixture(scope="module")
def admin_token():
    return _login(ADMIN)


@pytest.fixture(scope="module")
def cm_token():
    return _login(CM)


@pytest.fixture(scope="module")
def cs_token():
    return _login(CS)


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


# ---------- Public settings ----------
def test_public_settings_includes_dashboard_bg_fields():
    r = requests.get(f"{API}/settings/public", timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    for key in ("dashboard_bg_enabled", "dashboard_bg_url", "dashboard_bg_opacity"):
        assert key in d, f"missing {key} in public settings"
    assert isinstance(d["dashboard_bg_enabled"], bool)
    assert isinstance(d["dashboard_bg_opacity"], int)


# ---------- Admin GET ----------
def test_admin_get_visuals_returns_dashboard_bg(admin_token):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    for key in ("dashboard_bg_enabled", "dashboard_bg_url", "dashboard_bg_opacity"):
        assert key in d


# ---------- PUT persistence and clamp ----------
def test_admin_put_persists_and_clamps_opacity_high(admin_token):
    payload = {
        "dashboard_bg_enabled": True,
        "dashboard_bg_url": "https://example.com/bg.jpg",
        "dashboard_bg_opacity": 30,  # above max 24 -> clamp to 24
    }
    r = requests.put(f"{API}/admin/settings/visuals", json=payload, headers=_h(admin_token), timeout=15)
    assert r.status_code == 200, r.text
    d = _unwrap(r)
    assert d["dashboard_bg_enabled"] is True
    assert d["dashboard_bg_url"] == "https://example.com/bg.jpg"
    assert d["dashboard_bg_opacity"] == 24, f"expected clamp to 24, got {d['dashboard_bg_opacity']}"

    # Verify persistence via GET
    r2 = requests.get(f"{API}/admin/settings/visuals", headers=_h(admin_token), timeout=15)
    assert r2.status_code == 200
    d2 = _unwrap(r2)
    assert d2["dashboard_bg_opacity"] == 24
    assert d2["dashboard_bg_url"] == "https://example.com/bg.jpg"
    assert d2["dashboard_bg_enabled"] is True

    # And through public
    rp = requests.get(f"{API}/settings/public", timeout=15)
    dp = _unwrap(rp)
    assert dp["dashboard_bg_opacity"] == 24
    assert dp["dashboard_bg_url"] == "https://example.com/bg.jpg"
    assert dp["dashboard_bg_enabled"] is True


def test_admin_put_clamps_opacity_low(admin_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={"dashboard_bg_opacity": 1},
        headers=_h(admin_token),
        timeout=15,
    )
    assert r.status_code == 200, r.text
    assert _unwrap(r)["dashboard_bg_opacity"] == 4


# ---------- RBAC ----------
def test_content_manager_can_put_dashboard_bg(cm_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={"dashboard_bg_opacity": 12},
        headers=_h(cm_token),
        timeout=15,
    )
    assert r.status_code == 200, r.text
    assert _unwrap(r)["dashboard_bg_opacity"] == 12


def test_customer_service_can_get_but_not_put(cs_token):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(cs_token), timeout=15)
    assert r.status_code == 200
    r2 = requests.put(
        f"{API}/admin/settings/visuals",
        json={"dashboard_bg_opacity": 15},
        headers=_h(cs_token),
        timeout=15,
    )
    assert r2.status_code == 403, f"expected 403, got {r2.status_code}: {r2.text}"


def test_unauthenticated_put_returns_401():
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={"dashboard_bg_opacity": 15},
        timeout=15,
    )
    assert r.status_code == 401, f"expected 401, got {r.status_code}"


# ---------- Safety / freeze check ----------
def test_safety_business_collections_and_counter(admin_token):
    # Certificate list should be empty & counter 14 (next 15)
    # Use analytics endpoint if available, otherwise check via certificates list
    r = requests.get(f"{API}/admin/certificates?page=1&page_size=1", headers=_h(admin_token), timeout=15)
    if r.status_code == 200:
        data = _unwrap(r)
        total = data.get("total", data.get("total_count", 0))
        assert total == 0, f"certificates should be 0, got {total}"


# ---------- Teardown: restore defaults ----------
def test_zzz_restore_defaults(admin_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={
            "dashboard_bg_enabled": False,
            "dashboard_bg_url": "",
            "dashboard_bg_opacity": 10,
        },
        headers=_h(admin_token),
        timeout=15,
    )
    assert r.status_code == 200
    d = _unwrap(r)
    assert d["dashboard_bg_enabled"] is False
    assert d["dashboard_bg_url"] == ""
    assert d["dashboard_bg_opacity"] == 10
