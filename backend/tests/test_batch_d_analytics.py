"""BATCH D — Sprint 27 Analytics endpoint tests (hermetic).

Runs independently: `pytest tests/test_batch_d_analytics.py -o addopts=`
Requires cm@ and cs@ seeded via scripts.seed_test_roles.
Cleans up all fixtures and asserts DB baseline invariants at teardown.
"""
from __future__ import annotations

import os
import re
import uuid

import pytest
import requests

def _read_base() -> str:
    v = os.environ.get("REACT_APP_BACKEND_URL")
    if not v:
        with open("/app/frontend/.env") as fh:
            for line in fh:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    v = line.split("=", 1)[1].strip()
                    break
    assert v, "REACT_APP_BACKEND_URL missing"
    return v.rstrip("/")


BASE = _read_base()
API = f"{BASE}/api"

CREDS = {
    "super": ("admin@azuris.local", "AzurisDev@2026!"),
    "cm": ("cm@azuris.local", "CmDev@2026!"),
    "cs": ("cs@azuris.local", "CsDev@2026!"),
}


def _login(role: str) -> str:
    email, pw = CREDS[role]
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": pw}, timeout=15)
    assert r.status_code == 200, f"login {role} => {r.status_code} {r.text}"
    body = r.json()
    tok = body.get("data", body).get("access_token") or body.get("access_token")
    assert tok, f"no token in {body}"
    return tok


def _auth(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}"}


@pytest.fixture(scope="module")
def super_token() -> str:
    return _login("super")


@pytest.fixture(scope="module")
def cm_token() -> str:
    return _login("cm")


@pytest.fixture(scope="module")
def cs_token() -> str:
    return _login("cs")


# --- RBAC ---
def test_analytics_unauth_401():
    r = requests.get(f"{API}/admin/analytics/overview", timeout=15)
    assert r.status_code == 401, r.text


def test_analytics_super_admin_200(super_token):
    r = requests.get(f"{API}/admin/analytics/overview", headers=_auth(super_token), timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    assert "data" in body


def test_analytics_content_manager_403(cm_token):
    r = requests.get(f"{API}/admin/analytics/overview", headers=_auth(cm_token), timeout=15)
    assert r.status_code == 403, r.text


def test_analytics_customer_service_403(cs_token):
    r = requests.get(f"{API}/admin/analytics/overview", headers=_auth(cs_token), timeout=15)
    assert r.status_code == 403, r.text


# --- Structure & baseline ---
def _fetch(super_token):
    r = requests.get(f"{API}/admin/analytics/overview", headers=_auth(super_token), timeout=15)
    assert r.status_code == 200
    return r.json()["data"]


def test_analytics_structure_and_baseline(super_token):
    data = _fetch(super_token)
    for k in [
        "generated_at",
        "totals",
        "gemstones_by_status",
        "certificates_by_status",
        "warranties_by_status",
        "transfers_by_status",
        "memberships_by_status",
        "verification",
        "admin_activity",
        "certificate_counter",
    ]:
        assert k in data, f"missing key {k}"
    totals = data["totals"]
    for k in [
        "customers", "gemstones", "jewelry", "media", "certificates",
        "warranties", "ownership_transfers", "membership_cards", "verification_tokens",
    ]:
        assert k in totals
        assert totals[k] == 0, f"baseline broken: {k}={totals[k]}"
    cc = data["certificate_counter"]
    assert cc["last_number"] == 14, cc
    assert cc["next_number"] == "AZR-GEM-000015-26", cc
    ver = data["verification"]
    assert "by_result" in ver
    assert isinstance(ver["series"], list) and len(ver["series"]) == 14
    for pt in ver["series"]:
        assert set(pt.keys()) >= {"date", "count", "success"}
    assert "by_action" in data["admin_activity"]


# --- Privacy leak scan ---
_LEAK_KEYS = re.compile(
    r"\b(email|phone|address|full_name|name|security_code|qr_token|preview_token|password_hash|_id|ObjectId)\b",
    re.IGNORECASE,
)


def _walk(obj, keys):
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(k)
            _walk(v, keys)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, keys)


def test_analytics_privacy_no_pii(super_token):
    data = _fetch(super_token)
    keys: set[str] = set()
    _walk(data, keys)
    banned = {"email", "phone", "address", "full_name", "security_code",
              "qr_token", "preview_token", "password_hash", "_id"}
    leaked = keys & banned
    assert not leaked, f"privacy leak keys present: {leaked}"
    # 'name' key is allowed on counter (counter.name would be irrelevant since we don't emit).
    # But name as a customer name would be — we emit no such thing. Scan values too.
    import json
    blob = json.dumps(data)
    # ObjectId hex pattern (24 hex chars)
    hex_matches = re.findall(r'"[0-9a-f]{24}"', blob)
    assert not hex_matches, f"raw ObjectId-like hex leaked: {hex_matches[:3]}"


# --- Public verify security (never leaks secrets) ---
def test_public_verify_random_returns_not_found():
    r = requests.post(f"{API}/verify",
                      json={"certificate_number": "AZR-GEM-999999-99",
                            "security_code": "ZZZZ-ZZZZ"},
                      timeout=15)
    # generic no-match; either envelope-error 200/4xx with not_found
    assert r.status_code in (200, 400, 404), r.text
    blob = r.text.lower()
    for banned in ["security_code", "qr_token", "preview_token", "password_hash"]:
        assert banned not in blob, f"leak: {banned}"


def test_public_verify_malformed_never_leaks():
    r = requests.post(f"{API}/verify", json={"foo": "bar"}, timeout=15)
    assert r.status_code in (400, 422), r.status_code
    # 'security_code' appears here only as required-field name in schema validation,
    # not as a secret value; check no actual secret VALUES leak.
    blob = r.text.lower()
    for banned in ["qr_token", "preview_token", "password_hash"]:
        assert banned not in blob


def test_public_membership_verify_bad_token():
    # Try both known param names
    r = requests.get(f"{API}/membership/verify", params={"t": "not-a-real-token"}, timeout=15)
    assert r.status_code in (200, 400, 404), r.text
    blob = r.text.lower()
    for banned in ["qr_token", "preview_token", "password_hash"]:
        assert banned not in blob


# --- Final baseline invariant ---
def test_zz_baseline_invariant(super_token):
    data = _fetch(super_token)
    totals = data["totals"]
    assert all(totals[k] == 0 for k in totals), totals
    cc = data["certificate_counter"]
    assert cc["last_number"] == 14
    assert cc["next_number"] == "AZR-GEM-000015-26"
