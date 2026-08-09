"""Iteration 22 — Full end-to-end production readiness test.

Covers: public routes, verification (invalid + valid round-trip),
auth, RBAC failure modes, customers CRUD, gemstones CRUD + status,
certificate issuance + PDF + demo preview + public verify roundtrip,
warranty creation, ownership assign+transfer+complete, membership issue +
public verify, CMS visuals + settings PUT, analytics overview, response
envelope shape.

Creates real data (TEST_ prefixed) — main agent will reset baseline afterward.
"""

import os
import time
import uuid as uuidlib

import pytest
import requests

def _read_env(key):
    v = os.environ.get(key)
    if v:
        return v
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith(key + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    raise KeyError(key)

BASE = _read_env("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE}/api"

ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PASSWORD = "AzurisDev@2026!"

TAG = f"TEST_{uuidlib.uuid4().hex[:6]}"


# ---------------- fixtures ----------------
@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    data = body.get("data", body)
    tok = data.get("access_token") or data.get("token")
    assert tok, f"no token in {body}"
    return tok


@pytest.fixture(scope="module")
def H(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def state():
    return {}


def _data(r):
    j = r.json()
    return j.get("data", j)


# ---------------- Health & envelope ----------------
def test_health():
    r = requests.get(f"{API}/health", timeout=10)
    assert r.status_code == 200


def test_settings_public_envelope():
    r = requests.get(f"{API}/settings/public", timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert body.get("success") is True
    assert "data" in body and "meta" in body
    assert "request_id" in body["meta"]


# ---------------- Auth ----------------
def test_login_invalid():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong"}, timeout=10)
    assert r.status_code == 401


def test_auth_me(H):
    r = requests.get(f"{API}/auth/me", headers=H, timeout=10)
    assert r.status_code == 200
    d = _data(r)
    assert d["email"] == ADMIN_EMAIL


def test_protected_requires_token():
    r = requests.get(f"{API}/admin/customers", timeout=10)
    assert r.status_code == 401


# ---------------- Public verify (invalid) ----------------
def test_verify_invalid_number():
    r = requests.post(f"{API}/verify", json={"certificate_number": "INVALID", "security_code": "x"}, timeout=10)
    assert r.status_code == 200
    d = _data(r)
    assert d.get("status") == "not_found"


def test_verify_wellformed_but_absent():
    r = requests.post(f"{API}/verify", json={"certificate_number": "AZR-GEM-999999-99", "security_code": "nope"}, timeout=10)
    assert r.status_code == 200
    d = _data(r)
    assert d.get("status") in ("not_found", "invalid")


def test_verify_empty_validation():
    r = requests.post(f"{API}/verify", json={"certificate_number": "", "security_code": ""}, timeout=10)
    assert r.status_code in (400, 422)


def test_qr_resolve_invalid():
    r = requests.get(f"{API}/verify/qr/resolve", params={"token": "bogus"}, timeout=10)
    assert r.status_code == 200
    d = _data(r)
    assert d.get("status") in ("not_found", "invalid") or d.get("valid") is False or d.get("token_valid") is False or "certificate" in d


def test_membership_verify_invalid():
    r = requests.get(f"{API}/membership/verify", params={"t": "not-a-real-token"}, timeout=10)
    assert r.status_code == 200
    d = _data(r)
    assert d.get("valid") is False


def test_legality_public():
    r = requests.get(f"{API}/legality", timeout=10)
    assert r.status_code == 200


# ---------------- Analytics ----------------
def test_analytics_overview(H):
    r = requests.get(f"{API}/admin/analytics/overview", headers=H, timeout=15)
    assert r.status_code == 200, r.text
    d = _data(r)
    assert isinstance(d, dict)


# ---------------- Customers CRUD ----------------
def test_customer_crud(H, state):
    payload = {
        "full_name": f"{TAG} Customer",
        "email": f"{TAG.lower()}@example.com",
        "phone": "+62 812 000 0000",
        "privacy_consent": True,
    }
    r = requests.post(f"{API}/admin/customers", headers=H, json=payload, timeout=10)
    assert r.status_code == 201, r.text
    d = _data(r)
    cid = d["uuid"]
    assert d["full_name"] == payload["full_name"]
    assert d["consent_at"], "consent_at should stamp on privacy_consent=True"
    state["customer_id"] = cid

    # GET
    g = requests.get(f"{API}/admin/customers/{cid}", headers=H, timeout=10)
    assert g.status_code == 200
    assert _data(g)["full_name"] == payload["full_name"]

    # Update
    up = requests.put(f"{API}/admin/customers/{cid}", headers=H, json={"full_name": f"{TAG} Renamed"}, timeout=10)
    assert up.status_code == 200
    assert _data(up)["full_name"] == f"{TAG} Renamed"

    # 2nd customer for transfer
    r2 = requests.post(f"{API}/admin/customers", headers=H, json={
        "full_name": f"{TAG} Second", "privacy_consent": True
    }, timeout=10)
    assert r2.status_code == 201
    state["customer2_id"] = _data(r2)["uuid"]


# ---------------- Gemstones CRUD ----------------
def test_gemstone_crud(H, state):
    payload = {
        "name_id": f"{TAG} Batu",
        "name_en": f"{TAG} Gem",
        "category": "Precious",
        "gemstone_type": "Sapphire",
        "weight_carat": 2.5,
        "color": "Royal Blue",
        "clarity": "Transparent",
        "cut": "Oval Mixed",
        "shape": "Oval",
        "dimensions_mm": "8.2 x 6.1 x 4.3",
        "origin": "Ceylon",
        "treatment": "No indication",
    }
    r = requests.post(f"{API}/admin/gemstones", headers=H, json=payload, timeout=10)
    assert r.status_code == 201, r.text
    d = _data(r)
    gid = d["uuid"]
    state["gemstone_id"] = gid
    assert d["status"] == "draft"

    # status change draft -> verified
    st = requests.post(f"{API}/admin/gemstones/{gid}/status", headers=H, json={"status": "verified"}, timeout=10)
    assert st.status_code == 200, st.text
    assert _data(st)["status"] == "verified"

    # invalid transition verified -> draft => 409
    bad = requests.post(f"{API}/admin/gemstones/{gid}/status", headers=H, json={"status": "draft"}, timeout=10)
    assert bad.status_code == 409

    # list
    ls = requests.get(f"{API}/admin/gemstones?q=" + TAG, headers=H, timeout=10)
    assert ls.status_code == 200
    assert _data(ls)["total"] >= 1


# ---------------- Certificate issuance + verify roundtrip ----------------
def test_certificate_demo_preview(H):
    r = requests.get(f"{API}/admin/certificates/demo-preview", headers=H, timeout=20)
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("application/pdf")
    assert r.content[:4] == b"%PDF"


def test_issue_certificate_and_verify(H, state):
    gid = state["gemstone_id"]
    r = requests.post(f"{API}/admin/certificates/issue", headers=H, json={
        "gemstone_id": gid,
        "object_type": "Loose Gemstone",
        "examiner": "Azuris Test",
        "signatory": "Azuris Test",
        "conclusion": "Natural Sapphire",
    }, timeout=30)
    assert r.status_code == 201, r.text
    d = _data(r)
    cert_num = d.get("certificate_number")
    sec = d.get("security_code")
    assert cert_num and cert_num.startswith("AZR-GEM-"), d
    # format AZR-GEM-000015-26
    parts = cert_num.split("-")
    assert len(parts) == 4 and len(parts[2]) == 6 and len(parts[3]) == 2, cert_num
    assert sec, "security_code must be shown once"
    state["cert_number"] = cert_num
    state["cert_security"] = sec
    state["cert_uuid"] = d.get("certificate_uuid") or d.get("uuid")
    # QR present (qr_url or verification token)
    assert d.get("qr_url") or d.get("verification_token") or d.get("verification_uuid")

    # PDF (A6)
    pdf = requests.get(f"{API}/admin/certificates/{state['cert_uuid']}/pdf", headers=H, timeout=30)
    assert pdf.status_code == 200
    assert pdf.content[:4] == b"%PDF"

    # Public verify roundtrip
    v = requests.post(f"{API}/verify", json={
        "certificate_number": cert_num, "security_code": sec
    }, timeout=15)
    assert v.status_code == 200
    vd = _data(v)
    assert vd.get("status") == "valid", vd
    assert vd.get("certificate")


def test_verify_wrong_security_code(H, state):
    v = requests.post(f"{API}/verify", json={
        "certificate_number": state["cert_number"], "security_code": "WRONG-CODE"
    }, timeout=10)
    assert v.status_code == 200
    vd = _data(v)
    assert vd.get("status") != "valid"


# ---------------- Warranty ----------------
def test_warranty_create(H, state):
    r = requests.post(f"{API}/admin/warranties", headers=H, json={
        "gemstone_id": state["gemstone_id"],
        "terms_id": "Garansi 12 bulan uji.",
        "terms_en": "12 month re-examination warranty.",
        "period_months": 12,
        "start_date": "2026-01-01",
    }, timeout=15)
    assert r.status_code == 201, r.text
    d = _data(r)
    assert d["status"] == "active"
    assert d["period_months"] == 12
    assert d["end_date"] == "2027-01-01"
    state["warranty_id"] = d["uuid"]


# ---------------- Ownership: assign + transfer + complete ----------------
def test_ownership_assign_transfer_complete(H, state):
    gid = state["gemstone_id"]
    # First need PUBLISHED gemstone; move verified -> published
    st = requests.post(f"{API}/admin/gemstones/{gid}/status", headers=H, json={"status": "published"}, timeout=10)
    assert st.status_code == 200

    a = requests.post(f"{API}/admin/ownership/assign", headers=H, json={
        "gemstone_id": gid, "owner_id": state["customer_id"]
    }, timeout=15)
    assert a.status_code in (200, 201), a.text

    # Check current owner
    own = requests.get(f"{API}/admin/ownership/gemstone/{gid}", headers=H, timeout=10)
    assert own.status_code == 200
    od = _data(own)
    assert od["current_owner"]["uuid"] == state["customer_id"]

    # Create transfer to customer2
    t = requests.post(f"{API}/admin/ownership/transfers", headers=H, json={
        "gemstone_id": gid, "new_owner_id": state["customer2_id"]
    }, timeout=15)
    assert t.status_code == 201, t.text
    tid = _data(t)["uuid"]

    # Complete
    c = requests.post(f"{API}/admin/ownership/transfers/{tid}/complete", headers=H, timeout=15)
    assert c.status_code == 200, c.text

    # Verify history
    own2 = requests.get(f"{API}/admin/ownership/gemstone/{gid}", headers=H, timeout=10)
    assert own2.status_code == 200
    od2 = _data(own2)
    assert od2["current_owner"]["uuid"] == state["customer2_id"]
    assert len(od2["history"]) >= 1


# ---------------- Membership ----------------
def test_membership_issue_and_verify(H, state):
    r = requests.post(f"{API}/admin/membership", headers=H, json={
        "customer_id": state["customer_id"]
    }, timeout=15)
    assert r.status_code == 201, r.text
    d = _data(r)
    assert d["card_number"].startswith("AZR-MEM-")
    tok = d.get("verify_token")
    assert tok
    state["member_token"] = tok
    state["member_uuid"] = d["uuid"]

    v = requests.get(f"{API}/membership/verify", params={"t": tok}, timeout=10)
    assert v.status_code == 200
    vd = _data(v)
    assert vd.get("valid") is True
    assert vd.get("member_id") == d["card_number"]

    qr = requests.get(f"{API}/membership/qr", params={"t": tok}, timeout=15)
    assert qr.status_code == 200
    assert qr.headers.get("content-type", "").startswith("image/png")


# ---------------- CMS ----------------
def test_visuals_get_put(H):
    g = requests.get(f"{API}/admin/settings/visuals", headers=H, timeout=10)
    assert g.status_code == 200
    d = _data(g)
    # roundtrip PUT with same values (idempotent)
    put = requests.put(f"{API}/admin/settings/visuals", headers=H, json=d, timeout=10)
    assert put.status_code == 200


def test_settings_put_whatsapp(H):
    g = requests.get(f"{API}/admin/settings", headers=H, timeout=10)
    assert g.status_code == 200
    cur = _data(g)
    payload = {
        "whatsapp_number": cur.get("whatsapp_number") or "+62 812 000 0000",
        "whatsapp_enabled": bool(cur.get("whatsapp_enabled", False)),
    }
    p = requests.put(f"{API}/admin/settings", headers=H, json=payload, timeout=10)
    assert p.status_code == 200


# ---------------- Cleanup (best-effort) ----------------
def test_zzz_cleanup(H, state):
    # revoke certificate so gemstone status logic doesn't block anything
    # Delete membership
    if state.get("member_uuid"):
        requests.delete(f"{API}/admin/membership/{state['member_uuid']}", headers=H, timeout=10)
    # gemstone has cert -> cannot delete; leave it. Delete customers may fail if owned.
    # Delete second customer (no ownership after transfer completed customer2 owns it - skip)
    # Just note: main agent will restore baseline. No hard assertions here.
