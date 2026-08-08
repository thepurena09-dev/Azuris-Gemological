"""Dashboard + Login Background CMS Control — visuals endpoint.

Extended for iteration_20: dashboard_bg_fit/blur + login_bg_* fields.
Self-cleaning: restores all bg fields to defaults at end.
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

NEW_FIELDS = (
    "dashboard_bg_fit", "dashboard_bg_blur",
    "login_bg_enabled", "login_bg_url", "login_bg_opacity",
    "login_bg_fit", "login_bg_blur",
)


def _unwrap(r):
    j = r.json()
    if isinstance(j, dict) and "data" in j and "success" in j:
        return j["data"]
    return j


def _login(creds):
    r = requests.post(f"{API}/auth/login", json=creds, timeout=15)
    assert r.status_code == 200, f"login {creds['email']} failed: {r.status_code} {r.text}"
    return _unwrap(r)["access_token"]


@pytest.fixture(scope="module")
def admin_token(): return _login(ADMIN)


@pytest.fixture(scope="module")
def cm_token(): return _login(CM)


@pytest.fixture(scope="module")
def cs_token(): return _login(CS)


def _h(tok): return {"Authorization": f"Bearer {tok}"}


# ---------- Public settings ----------
def test_public_settings_includes_new_bg_fields():
    r = requests.get(f"{API}/settings/public", timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    for key in NEW_FIELDS:
        assert key in d, f"missing {key} in public settings"
    assert isinstance(d["login_bg_enabled"], bool)
    assert isinstance(d["dashboard_bg_blur"], int)
    assert isinstance(d["login_bg_opacity"], int)
    assert d["dashboard_bg_fit"] in ("cover", "center")
    assert d["login_bg_fit"] in ("cover", "center")


# ---------- Admin GET returns all fields ----------
def test_admin_get_visuals_returns_new_bg_fields(admin_token):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    for key in NEW_FIELDS:
        assert key in d


# ---------- Dashboard bg fit/blur persist + clamp ----------
def test_dashboard_bg_fit_and_blur_persist_and_clamp(admin_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={
            "dashboard_bg_enabled": True,
            "dashboard_bg_url": "https://example.com/d.jpg",
            "dashboard_bg_fit": "center",
            "dashboard_bg_blur": 50,  # clamp -> 12
            "dashboard_bg_opacity": 15,
        },
        headers=_h(admin_token),
        timeout=15,
    )
    assert r.status_code == 200, r.text
    d = _unwrap(r)
    assert d["dashboard_bg_fit"] == "center"
    assert d["dashboard_bg_blur"] == 12
    assert d["dashboard_bg_opacity"] == 15

    # invalid fit -> cover
    r2 = requests.put(
        f"{API}/admin/settings/visuals",
        json={"dashboard_bg_fit": "weird"},
        headers=_h(admin_token), timeout=15,
    )
    assert r2.status_code == 200
    assert _unwrap(r2)["dashboard_bg_fit"] == "cover"


def test_dashboard_bg_blur_low_clamp(admin_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={"dashboard_bg_blur": -5},
        headers=_h(admin_token), timeout=15,
    )
    assert r.status_code == 200
    assert _unwrap(r)["dashboard_bg_blur"] == 0


# ---------- Login bg persist + clamp ----------
def test_login_bg_persist_and_clamp(admin_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={
            "login_bg_enabled": True,
            "login_bg_url": "https://example.com/login.jpg",
            "login_bg_opacity": 99,  # clamp -> 24
            "login_bg_fit": "center",
            "login_bg_blur": 8,
        },
        headers=_h(admin_token), timeout=15,
    )
    assert r.status_code == 200, r.text
    d = _unwrap(r)
    assert d["login_bg_enabled"] is True
    assert d["login_bg_url"] == "https://example.com/login.jpg"
    assert d["login_bg_opacity"] == 24
    assert d["login_bg_fit"] == "center"
    assert d["login_bg_blur"] == 8

    # Persistence via public
    rp = requests.get(f"{API}/settings/public", timeout=15)
    dp = _unwrap(rp)
    assert dp["login_bg_enabled"] is True
    assert dp["login_bg_opacity"] == 24
    assert dp["login_bg_fit"] == "center"

    # Low clamps
    r2 = requests.put(
        f"{API}/admin/settings/visuals",
        json={"login_bg_opacity": 1, "login_bg_blur": 99, "login_bg_fit": "xx"},
        headers=_h(admin_token), timeout=15,
    )
    d2 = _unwrap(r2)
    assert d2["login_bg_opacity"] == 4
    assert d2["login_bg_blur"] == 12
    assert d2["login_bg_fit"] == "cover"


# ---------- RBAC ----------
def test_content_manager_can_put_new_fields(cm_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={"login_bg_fit": "cover", "dashboard_bg_blur": 3},
        headers=_h(cm_token), timeout=15,
    )
    assert r.status_code == 200, r.text
    d = _unwrap(r)
    assert d["dashboard_bg_blur"] == 3


def test_customer_service_get_ok_put_403(cs_token):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(cs_token), timeout=15)
    assert r.status_code == 200
    r2 = requests.put(
        f"{API}/admin/settings/visuals",
        json={"login_bg_blur": 5},
        headers=_h(cs_token), timeout=15,
    )
    assert r2.status_code == 403


def test_unauthenticated_put_returns_401():
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={"login_bg_blur": 5},
        timeout=15,
    )
    assert r.status_code == 401


# ---------- Safety / freeze ----------
def test_safety_certificate_counter_and_business_collections(admin_token):
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
            "dashboard_bg_fit": "cover",
            "dashboard_bg_blur": 0,
            "login_bg_enabled": False,
            "login_bg_url": "",
            "login_bg_opacity": 10,
            "login_bg_fit": "cover",
            "login_bg_blur": 0,
        },
        headers=_h(admin_token), timeout=15,
    )
    assert r.status_code == 200
    d = _unwrap(r)
    assert d["dashboard_bg_enabled"] is False
    assert d["dashboard_bg_url"] == ""
    assert d["dashboard_bg_opacity"] == 10
    assert d["dashboard_bg_fit"] == "cover"
    assert d["dashboard_bg_blur"] == 0
    assert d["login_bg_enabled"] is False
    assert d["login_bg_url"] == ""
    assert d["login_bg_opacity"] == 10
    assert d["login_bg_fit"] == "cover"
    assert d["login_bg_blur"] == 0
