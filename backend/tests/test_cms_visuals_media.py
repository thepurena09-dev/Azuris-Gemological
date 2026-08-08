"""Targeted tests for POST-BATCH D Visual Media Picker/Upload feature.

Covers:
- GET  /api/admin/settings/visuals/media (RBAC: CMS_READ; 401 unauth)
- POST /api/admin/settings/visuals/media (RBAC: CMS_WRITE; 401 unauth; 403 CS; 400 non-image)
- Uploaded url servable via GET /api/media/{uuid}
- MANDATORY CLEANUP: delete uploaded media + reset visuals defaults
- Verify counter last_number=14 + media collection is empty at end
"""
import io
import os
import pytest
import requests

BASE = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE = line.split("=", 1)[1].strip().rstrip("/")
API = f"{BASE}/api"

ADMIN = ("admin@azuris.local", "AzurisDev@2026!")
ADMINR = ("adminr@azuris.local", "AdminrDev@2026!")
CM = ("cm@azuris.local", "CmDev@2026!")
CS = ("cs@azuris.local", "CsDev@2026!")

LOGIN_DEFAULT = "https://images.unsplash.com/photo-1783771686998-0af6c0efec6e?crop=entropy&cs=srgb&fm=jpg&q=90&w=1400"
PROCESS_DEFAULT = "https://images.unsplash.com/photo-1628058494685-6c2f796ac24a?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200"


def _unwrap(r):
    j = r.json()
    if isinstance(j, dict) and "data" in j and "success" in j:
        return j.get("data")
    return j


def _login(creds):
    r = requests.post(f"{API}/auth/login", json={"email": creds[0], "password": creds[1]}, timeout=15)
    assert r.status_code == 200, f"login failed {creds[0]}: {r.text}"
    return _unwrap(r)["access_token"]


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


# Minimal valid PNG (1x1 white pixel)
_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff"
    b"\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture(scope="module")
def toks():
    return {
        "admin": _login(ADMIN),
        "adminr": _login(ADMINR),
        "cm": _login(CM),
        "cs": _login(CS),
    }


# Store uploaded uuids for cleanup
_uploaded = []


# ---- LIST endpoint RBAC ----
def test_list_visuals_media_no_auth_401():
    r = requests.get(f"{API}/admin/settings/visuals/media", timeout=15)
    assert r.status_code == 401


@pytest.mark.parametrize("role", ["admin", "adminr", "cm", "cs"])
def test_list_visuals_media_cms_read_200(toks, role):
    r = requests.get(f"{API}/admin/settings/visuals/media", headers=_h(toks[role]), timeout=15)
    assert r.status_code == 200, r.text
    d = _unwrap(r)
    assert "items" in d
    assert isinstance(d["items"], list)


# ---- UPLOAD endpoint RBAC ----
def test_upload_no_auth_401():
    files = {"file": ("test.png", io.BytesIO(_PNG_BYTES), "image/png")}
    r = requests.post(f"{API}/admin/settings/visuals/media", files=files, timeout=15)
    assert r.status_code == 401


def test_upload_cs_403(toks):
    files = {"file": ("test.png", io.BytesIO(_PNG_BYTES), "image/png")}
    r = requests.post(f"{API}/admin/settings/visuals/media", headers=_h(toks["cs"]), files=files, timeout=15)
    assert r.status_code == 403


def test_upload_super_admin_201(toks):
    files = {"file": ("test.png", io.BytesIO(_PNG_BYTES), "image/png")}
    r = requests.post(f"{API}/admin/settings/visuals/media", headers=_h(toks["admin"]), files=files, timeout=15)
    assert r.status_code == 201, r.text
    d = _unwrap(r)
    assert "uuid" in d and "url" in d
    assert d["url"].startswith("/api/media/")
    _uploaded.append(d["uuid"])
    # verify servable
    r2 = requests.get(f"{BASE}{d['url']}", timeout=15)
    assert r2.status_code == 200
    assert r2.headers.get("content-type", "").startswith("image/")


def test_upload_administrator_201(toks):
    files = {"file": ("test.png", io.BytesIO(_PNG_BYTES), "image/png")}
    r = requests.post(f"{API}/admin/settings/visuals/media", headers=_h(toks["adminr"]), files=files, timeout=15)
    assert r.status_code == 201, r.text
    d = _unwrap(r)
    _uploaded.append(d["uuid"])


def test_upload_content_manager_201(toks):
    files = {"file": ("test.png", io.BytesIO(_PNG_BYTES), "image/png")}
    r = requests.post(f"{API}/admin/settings/visuals/media", headers=_h(toks["cm"]), files=files, timeout=15)
    assert r.status_code == 201, r.text
    d = _unwrap(r)
    _uploaded.append(d["uuid"])


def test_upload_non_image_400(toks):
    files = {"file": ("test.txt", io.BytesIO(b"hello world"), "text/plain")}
    r = requests.post(f"{API}/admin/settings/visuals/media", headers=_h(toks["admin"]), files=files, timeout=15)
    assert r.status_code == 400, r.text


# ---- List shows uploaded ----
def test_list_shows_uploaded(toks):
    r = requests.get(f"{API}/admin/settings/visuals/media", headers=_h(toks["admin"]), timeout=15)
    d = _unwrap(r)
    uuids = {i["uuid"] for i in d["items"]}
    for u in _uploaded:
        assert u in uuids, f"missing uploaded {u}"


# ---- CLEANUP (mandatory) ----
def test_zz_cleanup_delete_uploaded(toks):
    for u in _uploaded:
        r = requests.delete(f"{API}/admin/media/{u}", headers=_h(toks["admin"]), timeout=15)
        assert r.status_code in (200, 204), f"delete {u} failed: {r.text}"


def test_zz_cleanup_reset_visuals(toks):
    payload = {"login_image_url": LOGIN_DEFAULT, "process_image_url": PROCESS_DEFAULT}
    r = requests.put(f"{API}/admin/settings/visuals", headers=_h(toks["admin"]), json=payload, timeout=15)
    assert r.status_code == 200
    d = _unwrap(r)
    assert d["login_image_url"] == LOGIN_DEFAULT
    assert d["process_image_url"] == PROCESS_DEFAULT


def test_zz_cleanup_media_empty(toks):
    r = requests.get(f"{API}/admin/settings/visuals/media", headers=_h(toks["admin"]), timeout=15)
    d = _unwrap(r)
    assert d["items"] == [], f"media collection not empty after cleanup: {d['items']}"


def test_zz_counter_still_14(toks):
    r = requests.get(f"{API}/admin/analytics/overview", headers=_h(toks["admin"]), timeout=15)
    d = _unwrap(r)
    assert d["certificate_counter"]["last_number"] == 14
    assert d["certificate_counter"]["next_number"] == "AZR-GEM-000015-26"
