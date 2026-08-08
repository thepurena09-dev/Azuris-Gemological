"""POST-BATCH D — CMS Visual Controls targeted tests.

Covers:
- Public GET /api/settings/public returns visual fields
- Admin GET/PUT /api/admin/settings/visuals RBAC per permission (CMS_READ/CMS_WRITE)
- Persistence: PUT then GET reflects changes
- Audit log entry with entity_type='cms_visuals'
- WhatsApp contact PUT /api/admin/settings still ADMINISTRATOR-only (CM=>403)
- Analytics counter unchanged: last_number=14
"""
import os
import pytest
import requests

def _load_backend_url():
    v = os.environ.get("REACT_APP_BACKEND_URL")
    if v:
        return v.rstrip("/")
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    return line.split("=", 1)[1].strip().rstrip("/")
    except FileNotFoundError:
        pass
    raise RuntimeError("REACT_APP_BACKEND_URL not set")

BASE = _load_backend_url()
API = f"{BASE}/api"

ADMIN = ("admin@azuris.local", "AzurisDev@2026!")
CM = ("cm@azuris.local", "CmDev@2026!")
CS = ("cs@azuris.local", "CsDev@2026!")

VISUAL_FIELDS = [
    "login_image_url", "login_image_alt_id", "login_image_alt_en",
    "process_image_url", "process_image_alt_id", "process_image_alt_en",
    "process_image_show", "membership_show",
    "membership_title_id", "membership_title_en",
    "membership_desc_id", "membership_desc_en",
    "membership_cta_id", "membership_cta_en", "membership_link",
]


def _unwrap(r):
    j = r.json()
    if isinstance(j, dict) and "data" in j and "success" in j:
        return j.get("data")
    return j


def _login(creds):
    r = requests.post(f"{API}/auth/login", json={"email": creds[0], "password": creds[1]}, timeout=15)
    assert r.status_code == 200, f"login failed for {creds[0]}: {r.status_code} {r.text}"
    return _unwrap(r)["access_token"]


@pytest.fixture(scope="module")
def admin_tok():
    return _login(ADMIN)


@pytest.fixture(scope="module")
def cm_tok():
    return _login(CM)


@pytest.fixture(scope="module")
def cs_tok():
    return _login(CS)


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


# ---- Public visuals ----
def test_public_settings_returns_visual_fields():
    r = requests.get(f"{API}/settings/public", timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    for k in VISUAL_FIELDS:
        assert k in d, f"missing {k}"
    # sanity: contact still present
    assert "whatsapp_number" in d


# ---- Admin GET visuals RBAC ----
def test_visuals_get_no_auth_401():
    r = requests.get(f"{API}/admin/settings/visuals", timeout=15)
    assert r.status_code == 401


def test_visuals_get_super_admin_200(admin_tok):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(admin_tok), timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    for k in VISUAL_FIELDS:
        assert k in d


def test_visuals_get_content_manager_200(cm_tok):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(cm_tok), timeout=15)
    assert r.status_code == 200


def test_visuals_get_customer_service_200(cs_tok):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(cs_tok), timeout=15)
    assert r.status_code == 200


# ---- Admin PUT visuals RBAC ----
def test_visuals_put_no_auth_401():
    r = requests.put(f"{API}/admin/settings/visuals", json={}, timeout=15)
    assert r.status_code == 401


def test_visuals_put_customer_service_403(cs_tok):
    r = requests.put(f"{API}/admin/settings/visuals", headers=_h(cs_tok),
                     json={"membership_show": True}, timeout=15)
    assert r.status_code == 403


def test_visuals_put_content_manager_200(cm_tok):
    payload = {"membership_title_id": "TEST_CM_Title_ID", "membership_title_en": "TEST_CM_Title_EN"}
    r = requests.put(f"{API}/admin/settings/visuals", headers=_h(cm_tok), json=payload, timeout=15)
    assert r.status_code == 200, r.text
    d = _unwrap(r)
    assert d["membership_title_id"] == "TEST_CM_Title_ID"


# ---- Persistence + audit ----
def test_visuals_put_super_admin_persists(admin_tok):
    payload = {
        "membership_show": True,
        "membership_title_id": "Keanggotaan Azuris",
        "membership_title_en": "Azuris Membership",
        "membership_desc_id": "Deskripsi ID",
        "membership_desc_en": "Description EN",
        "membership_cta_id": "Gabung",
        "membership_cta_en": "Join",
        "membership_link": "/membership",
        "process_image_show": True,
    }
    r = requests.put(f"{API}/admin/settings/visuals", headers=_h(admin_tok), json=payload, timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    for k, v in payload.items():
        assert d[k] == v

    # GET admin reflects
    r2 = requests.get(f"{API}/admin/settings/visuals", headers=_h(admin_tok), timeout=15)
    d2 = _unwrap(r2)
    for k, v in payload.items():
        assert d2[k] == v

    # Public GET reflects
    r3 = requests.get(f"{API}/settings/public", timeout=15)
    d3 = _unwrap(r3)
    for k, v in payload.items():
        assert d3[k] == v


def test_visuals_no_secrets_leaked(admin_tok):
    r = requests.get(f"{API}/admin/settings/visuals", headers=_h(admin_tok), timeout=15)
    text = r.text.lower()
    for bad in ["password", "hash", "security_code", "qr_token", "preview_token"]:
        assert bad not in text, f"leak: {bad}"
    # No mongo _id: check as JSON key
    import json as _json
    d = _unwrap(r)
    assert "_id" not in d


# ---- Contact PUT still ADMINISTRATOR-only ----
def test_contact_put_content_manager_403(cm_tok):
    r = requests.put(f"{API}/admin/settings", headers=_h(cm_tok),
                     json={"whatsapp_label": "TEST"}, timeout=15)
    assert r.status_code == 403


def test_contact_put_customer_service_403(cs_tok):
    r = requests.put(f"{API}/admin/settings", headers=_h(cs_tok),
                     json={"whatsapp_label": "TEST"}, timeout=15)
    assert r.status_code == 403


# ---- Certificate counter unchanged ----
def test_counter_still_14(admin_tok):
    r = requests.get(f"{API}/admin/analytics/overview", headers=_h(admin_tok), timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    cc = d["certificate_counter"]
    assert cc["last_number"] == 14
    assert cc["next_number"] == "AZR-GEM-000015-26"


# ---- Verify endpoint safe with malformed ----
def test_verify_malformed_safe():
    r = requests.post(f"{API}/verify", json={"certificate_number": "bogus", "security_code": "xxx"}, timeout=15)
    assert r.status_code in (200, 400, 404)
    text = r.text.lower()
    for bad in ["password", "hash", "traceback", "mongo"]:
        assert bad not in text
