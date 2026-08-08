"""Homepage Background + Gem Photos CMS control — /admin/settings/visuals (iter 21).

Self-cleaning: restores home_bg_* + home_gem_*_url to model defaults at end.
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

HOME_BG_FIELDS = ("home_bg_enabled", "home_bg_url", "home_bg_opacity", "home_bg_fit", "home_bg_blur")
GEM_FIELDS = ("home_gem_diamond_url", "home_gem_ruby_url", "home_gem_sapphire_url", "home_gem_emerald_url")

# Model defaults (see backend/models/settings.py)
DEFAULT_HOME_BG = {
    "home_bg_enabled": False,
    "home_bg_url": "",
    "home_bg_opacity": 20,
    "home_bg_fit": "cover",
    "home_bg_blur": 0,
}
DEFAULT_GEMS = {
    "home_gem_diamond_url": "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    "home_gem_ruby_url": "https://images.unsplash.com/photo-1705575490492-4e91fd97bbb4?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    "home_gem_sapphire_url": "https://static.prod-images.emergentagent.com/jobs/0d8170c5-08d6-45ed-9937-114710780b07/images/11e5956f874718e6db198dda556242a9e59a93fb2ea1cd0b3fe0d77cc5e02724.jpeg",
    "home_gem_emerald_url": "https://static.prod-images.emergentagent.com/jobs/6572b450-f0e7-4d20-83da-0f44a5e44dfd/images/8138fec9a0cfedc223c4896ebd58852071928246a1875cecdb3ce5aaebe929ad.jpeg",
}


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
def test_public_settings_includes_home_bg_and_gems():
    r = requests.get(f"{API}/settings/public", timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    for k in HOME_BG_FIELDS + GEM_FIELDS:
        assert k in d, f"missing {k}"
    # Gem defaults non-empty
    for k in GEM_FIELDS:
        assert isinstance(d[k], str) and len(d[k]) > 0, f"{k} must be non-empty"
    assert d["home_bg_fit"] in ("cover", "center")
    assert isinstance(d["home_bg_enabled"], bool)


def test_admin_get_visuals_includes_home_fields(admin_token):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    for k in HOME_BG_FIELDS + GEM_FIELDS:
        assert k in d


# ---------- PUT persist + clamps ----------
def test_home_bg_persist_and_clamp(admin_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={
            "home_bg_enabled": True,
            "home_bg_url": "https://example.com/home.jpg",
            "home_bg_opacity": 99,   # clamp -> 24
            "home_bg_fit": "center",
            "home_bg_blur": 50,      # clamp -> 12
            "home_gem_diamond_url": "https://example.com/diamond.jpg",
        },
        headers=_h(admin_token), timeout=15,
    )
    assert r.status_code == 200, r.text
    d = _unwrap(r)
    assert d["home_bg_enabled"] is True
    assert d["home_bg_url"] == "https://example.com/home.jpg"
    assert d["home_bg_opacity"] == 24
    assert d["home_bg_fit"] == "center"
    assert d["home_bg_blur"] == 12
    assert d["home_gem_diamond_url"] == "https://example.com/diamond.jpg"

    # persistence via public
    rp = requests.get(f"{API}/settings/public", timeout=15)
    dp = _unwrap(rp)
    assert dp["home_bg_enabled"] is True
    assert dp["home_bg_opacity"] == 24
    assert dp["home_bg_fit"] == "center"
    assert dp["home_gem_diamond_url"] == "https://example.com/diamond.jpg"


def test_home_bg_low_clamps_and_invalid_fit(admin_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={"home_bg_opacity": 1, "home_bg_blur": -3, "home_bg_fit": "weird"},
        headers=_h(admin_token), timeout=15,
    )
    d = _unwrap(r)
    assert d["home_bg_opacity"] == 4
    assert d["home_bg_blur"] == 0
    assert d["home_bg_fit"] == "cover"


# ---------- RBAC ----------
def test_cm_can_put_home_fields(cm_token):
    r = requests.put(
        f"{API}/admin/settings/visuals",
        json={"home_bg_blur": 3, "home_gem_ruby_url": "https://example.com/ruby.jpg"},
        headers=_h(cm_token), timeout=15,
    )
    assert r.status_code == 200, r.text
    d = _unwrap(r)
    assert d["home_bg_blur"] == 3
    assert d["home_gem_ruby_url"] == "https://example.com/ruby.jpg"


def test_cs_get_ok_put_403(cs_token):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(cs_token), timeout=15)
    assert r.status_code == 200
    r2 = requests.put(
        f"{API}/admin/settings/visuals",
        json={"home_bg_blur": 5},
        headers=_h(cs_token), timeout=15,
    )
    assert r2.status_code == 403


def test_unauth_put_401():
    r = requests.put(f"{API}/admin/settings/visuals", json={"home_bg_blur": 5}, timeout=15)
    assert r.status_code == 401


# ---------- Safety / freeze ----------
def test_safety_certificate_counter_still_14(admin_token):
    # Certificates business collection must remain empty (counter next=15 => last_number=14).
    r = requests.get(f"{API}/admin/certificates?page=1&page_size=1", headers=_h(admin_token), timeout=15)
    if r.status_code == 200:
        data = _unwrap(r)
        total = data.get("total", data.get("total_count", 0))
        assert total == 0, f"certificates should be 0, got {total}"


# ---------- Teardown: restore defaults ----------
def test_zzz_restore_home_defaults(admin_token):
    payload = {**DEFAULT_HOME_BG, **DEFAULT_GEMS}
    r = requests.put(f"{API}/admin/settings/visuals", json=payload, headers=_h(admin_token), timeout=15)
    assert r.status_code == 200, r.text
    d = _unwrap(r)
    for k, v in payload.items():
        assert d[k] == v, f"{k}: expected {v!r}, got {d[k]!r}"
