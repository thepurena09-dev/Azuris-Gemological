"""Batch C (Sprints 15–23 + 23A) authoritative regression gate.

Covers the NEW post-certification/ownership/membership work plus the security
invariants that BATCH C touches:

- Sprint 19 Warranty: create (auto number + derived end_date), one-active-per-stone
  guard, reissue (versioning), status transitions (active→void/expired), invalid
  transition guard, delete, RBAC, warranty number never touches the cert counter.
- Sprints 20–22 Ownership + Transfer: initial assign, already-owned guard, transfer
  validations, complete (owner change + gemstone status=transferred + SECURITY CODE
  ROTATION with QR stable), cancel, one-pending guard, ownership history.
- Sprint 23A Membership Card: consent-required guard, create (masked identity +
  Member ID distinct from cert number), duplicate guard, status, reissue, public
  token-gated member-safe verification, RBAC, no-PII/no-secret leak.
- Cross-cutting: Sprint 8 envelope, Sprint 9 correlation, generic errors.

Hermetic & self-cleaning: restores baseline (all business collections 0,
certificate counter.last_number=14 → next real cert AZR-GEM-000015-26).
"""

from __future__ import annotations

import os
import struct
import zlib

import pytest
import requests
from motor.motor_asyncio import AsyncIOMotorClient


def _load_frontend_env():
    path = "/app/frontend/.env"
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip().strip('"').rstrip("/")
    return None


BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or _load_frontend_env() or "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL not configured"
API = f"{BASE_URL}/api"

ADMIN = ("admin@azuris.local", "AzurisDev@2026!")
CM = ("cm@azuris.local", "CmDev@2026!")
CS = ("cs@azuris.local", "CsDev@2026!")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


def _tiny_png() -> bytes:
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)
    raw = b"\x00" + b"\xff\x00\x00\x00\xff\x00" + b"\x00" + b"\x00\x00\xff\xff\xff\xff"
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


PNG = _tiny_png()


def _login(creds):
    r = requests.post(f"{API}/auth/login", json={"email": creds[0], "password": creds[1]}, timeout=15)
    assert r.status_code == 200, r.text
    return r.json()["data"]["access_token"]


@pytest.fixture(scope="session")
def admin_token():
    return _login(ADMIN)


@pytest.fixture(scope="session")
def cm_token():
    try:
        return _login(CM)
    except AssertionError:
        pytest.skip("CM seed missing")


@pytest.fixture(scope="session")
def cs_token():
    try:
        return _login(CS)
    except AssertionError:
        pytest.skip("CS seed missing")


@pytest.fixture(scope="session")
def state():
    return {
        "customers": [], "gemstones": [], "warranties": [], "transfers": [],
        "memberships": [], "certificates": [], "photo_docs": [],
    }


def H(t):
    return {"Authorization": f"Bearer {t}"}


def _mk_gemstone(admin_token, state, name="TEST C Gem"):
    body = {"name_id": name, "name_en": name, "category": "precious", "gemstone_type": "ruby", "weight_carat": 2.0}
    r = requests.post(f"{API}/admin/gemstones", json=body, headers=H(admin_token), timeout=10)
    assert r.status_code == 201, r.text
    gid = r.json()["data"]["uuid"]
    state["gemstones"].append(gid)
    return gid


def _mk_customer(admin_token, state, name="TEST C Owner", consent=True):
    r = requests.post(f"{API}/admin/customers", json={"full_name": name, "privacy_consent": consent}, headers=H(admin_token), timeout=10)
    assert r.status_code == 201, r.text
    uid = r.json()["data"]["uuid"]
    state["customers"].append(uid)
    return uid


# ============================================================
# SPRINT 19 — Warranty
# ============================================================
class TestSprint19Warranty:
    def test_create_auto_number_and_end_date(self, admin_token, state):
        gid = _mk_gemstone(admin_token, state, "TEST C Warranty Gem")
        body = {"gemstone_id": gid, "terms_id": "Garansi 12 bulan", "terms_en": "12 month warranty",
                "period_months": 12, "start_date": "2026-06-01"}
        r = requests.post(f"{API}/admin/warranties", json=body, headers=H(admin_token), timeout=10)
        assert r.status_code == 201, r.text
        d = r.json()["data"]
        assert d["warranty_number"].startswith("AZR-WTY-"), d["warranty_number"]
        assert d["status"] == "active"
        assert d["end_date"] == "2027-06-01", d["end_date"]
        assert d["version"] == 1 and d["is_current"] is True
        state["warranties"].append(d["uuid"])
        state["_wgem"] = gid

    def test_one_active_per_stone_conflict(self, admin_token, state):
        gid = state["_wgem"]
        body = {"gemstone_id": gid, "terms_id": "x", "terms_en": "x", "period_months": 6}
        r = requests.post(f"{API}/admin/warranties", json=body, headers=H(admin_token), timeout=10)
        assert r.status_code == 409
        assert r.json()["error"]["code"] == "CONFLICT"

    def test_reissue_creates_v2(self, admin_token, state):
        wid = state["warranties"][0]
        r = requests.post(f"{API}/admin/warranties/{wid}/reissue",
                          json={"terms_id": "revisi", "terms_en": "revised", "period_months": 24, "start_date": "2026-06-01"},
                          headers=H(admin_token), timeout=10)
        assert r.status_code == 200, r.text
        d = r.json()["data"]
        assert d["version"] == 2 and d["is_current"] is True
        assert d["end_date"] == "2028-06-01"
        state["warranties"].append(d["uuid"])

    def test_invalid_gemstone_400(self, admin_token):
        body = {"gemstone_id": "nope-uuid", "terms_id": "x", "terms_en": "x", "period_months": 1}
        r = requests.post(f"{API}/admin/warranties", json=body, headers=H(admin_token), timeout=10)
        assert r.status_code == 400

    def test_status_void_then_invalid_reactivate(self, admin_token, state):
        wid = state["warranties"][-1]  # current v2
        r = requests.post(f"{API}/admin/warranties/{wid}/status", json={"status": "void"}, headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "void"
        # void -> active is forbidden
        r2 = requests.post(f"{API}/admin/warranties/{wid}/status", json={"status": "active"}, headers=H(admin_token), timeout=10)
        assert r2.status_code == 409

    def test_list_filter_and_get(self, admin_token, state):
        gid = state["_wgem"]
        r = requests.get(f"{API}/admin/warranties", params={"gemstone_id": gid}, headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        assert r.json()["data"]["total"] >= 2
        wid = state["warranties"][0]
        rg = requests.get(f"{API}/admin/warranties/{wid}", headers=H(admin_token), timeout=10)
        assert rg.status_code == 200

    def test_rbac(self, cm_token, cs_token, admin_token, state):
        gid = state["_wgem"]
        body = {"gemstone_id": gid, "terms_id": "x", "terms_en": "x", "period_months": 1}
        assert requests.post(f"{API}/admin/warranties", json=body, headers=H(cm_token), timeout=10).status_code == 403
        # CS read allowed, write forbidden
        assert requests.get(f"{API}/admin/warranties", headers=H(cs_token), timeout=10).status_code == 200
        assert requests.post(f"{API}/admin/warranties", json=body, headers=H(cs_token), timeout=10).status_code == 403
        # unauth
        assert requests.get(f"{API}/admin/warranties", timeout=10).status_code == 401

    def test_warranty_counter_is_separate_from_cert_counter(self):
        import asyncio

        async def chk():
            c = AsyncIOMotorClient(MONGO_URL)
            db = c[DB_NAME]
            wty = await db.counters.find_one({"name": "warranty", "year": 2026})
            cert = await db.counters.find_one({"name": "certificate", "year": 2026})
            c.close()
            return wty, cert
        wty, cert = asyncio.run(chk())
        # Warranty numbers come from their OWN counter doc — the certificate
        # counter is a distinct document and is never advanced by warranties.
        assert wty and wty["last_number"] >= 1, wty
        assert cert and cert["name"] == "certificate"
        assert cert["last_number"] == 14, cert  # no cert issued yet at this point


# ============================================================
# SPRINTS 20–22 — Ownership + Transfer (with security code rotation)
# ============================================================
class TestOwnershipTransfer:
    def test_full_ownership_lifecycle(self, admin_token, state):
        gid = _mk_gemstone(admin_token, state, "TEST C Owned Gem")
        # Issue a certificate so a verification token + security code exist.
        rp = requests.post(f"{API}/admin/gemstones/{gid}/photo",
                           files={"file": ("p.png", PNG, "image/png")}, headers=H(admin_token), timeout=20)
        state["photo_docs"].append(rp.json()["data"]["photo_id"])
        ri = requests.post(f"{API}/admin/certificates/issue",
                           json={"gemstone_id": gid, "examiner": "TEST"}, headers=H(admin_token), timeout=15)
        assert ri.status_code == 201, ri.text
        cert = ri.json()["data"]
        state["certificates"].append(cert["certificate_uuid"])
        cert_no = cert["certificate_number"]
        old_code = cert["security_code"]
        qr_token = cert["qr_token"]

        c1 = _mk_customer(admin_token, state, "Alexander Wijaya")
        c2 = _mk_customer(admin_token, state, "Budi Santoso")

        # assign initial owner
        ra = requests.post(f"{API}/admin/ownership/assign", json={"gemstone_id": gid, "owner_id": c1}, headers=H(admin_token), timeout=10)
        assert ra.status_code == 201, ra.text
        # already owned -> conflict
        ra2 = requests.post(f"{API}/admin/ownership/assign", json={"gemstone_id": gid, "owner_id": c2}, headers=H(admin_token), timeout=10)
        assert ra2.status_code == 409

        # transfer validations
        assert requests.post(f"{API}/admin/ownership/transfers", json={"gemstone_id": "bad", "new_owner_id": c2}, headers=H(admin_token), timeout=10).status_code == 400
        assert requests.post(f"{API}/admin/ownership/transfers", json={"gemstone_id": gid, "new_owner_id": c1}, headers=H(admin_token), timeout=10).status_code == 400  # same owner

        # create pending transfer C1 -> C2
        rt = requests.post(f"{API}/admin/ownership/transfers", json={"gemstone_id": gid, "new_owner_id": c2}, headers=H(admin_token), timeout=10)
        assert rt.status_code == 201, rt.text
        tid = rt.json()["data"]["uuid"]
        state["transfers"].append(tid)
        assert rt.json()["data"]["previous_owner_id"] == c1

        # one pending per gemstone
        assert requests.post(f"{API}/admin/ownership/transfers", json={"gemstone_id": gid, "new_owner_id": c2}, headers=H(admin_token), timeout=10).status_code == 409

        # complete -> rotates code, gem status transferred, owner=c2
        rc = requests.post(f"{API}/admin/ownership/transfers/{tid}/complete", headers=H(admin_token), timeout=10)
        assert rc.status_code == 200, rc.text
        dc = rc.json()["data"]
        assert dc["status"] == "completed" and dc["security_code_rotated"] is True
        new_code = dc["new_security_code"]
        assert new_code and new_code != old_code

        # ownership view: owner is c2 (masked), status transferred, history has 1
        rv = requests.get(f"{API}/admin/ownership/gemstone/{gid}", headers=H(admin_token), timeout=10)
        d = rv.json()["data"]
        assert d["gemstone_status"] == "transferred"
        assert d["current_owner"]["uuid"] == c2
        assert d["current_owner"]["masked_name"] == "Budi San****"  # locked masking
        assert len(d["history"]) == 1

        # OLD security code no longer verifies (rotated); NEW code verifies; QR stable
        rold = requests.post(f"{API}/verify", json={"certificate_number": cert_no, "security_code": old_code}, timeout=10)
        assert rold.json()["data"]["status"] == "not_found"
        rnew = requests.post(f"{API}/verify", json={"certificate_number": cert_no, "security_code": new_code}, timeout=10)
        assert rnew.json()["data"]["status"] == "valid", rnew.text
        rqr = requests.post(f"{API}/verify/qr", json={"token": qr_token}, timeout=10)
        assert rqr.json()["data"]["status"] == "valid"  # QR persists across transfer

        # cannot complete again
        assert requests.post(f"{API}/admin/ownership/transfers/{tid}/complete", headers=H(admin_token), timeout=10).status_code == 409

    def test_cancel_pending_no_ownership_change(self, admin_token, state):
        gid = _mk_gemstone(admin_token, state, "TEST C Cancel Gem")
        c1 = _mk_customer(admin_token, state, "Carol Tan")
        requests.post(f"{API}/admin/ownership/assign", json={"gemstone_id": gid, "owner_id": c1}, headers=H(admin_token), timeout=10)
        c2 = _mk_customer(admin_token, state, "Dedi Kurnia")
        rt = requests.post(f"{API}/admin/ownership/transfers", json={"gemstone_id": gid, "new_owner_id": c2}, headers=H(admin_token), timeout=10)
        tid = rt.json()["data"]["uuid"]
        state["transfers"].append(tid)
        rc = requests.post(f"{API}/admin/ownership/transfers/{tid}/cancel", headers=H(admin_token), timeout=10)
        assert rc.status_code == 200 and rc.json()["data"]["status"] == "cancelled"
        # owner unchanged
        d = requests.get(f"{API}/admin/ownership/gemstone/{gid}", headers=H(admin_token), timeout=10).json()["data"]
        assert d["current_owner"]["uuid"] == c1
        assert len(d["history"]) == 0

    def test_rbac_ownership(self, cm_token, cs_token, admin_token, state):
        gid = state["gemstones"][-1]
        # CM has no ownership perms
        assert requests.get(f"{API}/admin/ownership/gemstone/{gid}", headers=H(cm_token), timeout=10).status_code == 403
        # CS read ok, write forbidden
        assert requests.get(f"{API}/admin/ownership/gemstone/{gid}", headers=H(cs_token), timeout=10).status_code == 200
        assert requests.post(f"{API}/admin/ownership/assign", json={"gemstone_id": gid, "owner_id": "x"}, headers=H(cs_token), timeout=10).status_code == 403
        assert requests.get(f"{API}/admin/ownership/transfers", timeout=10).status_code == 401


# ============================================================
# SPRINT 23A — Membership Card
# ============================================================
class TestSprint23AMembership:
    def test_consent_required(self, admin_token, state):
        uid = _mk_customer(admin_token, state, "No Consent Person", consent=False)
        r = requests.post(f"{API}/admin/membership", json={"customer_id": uid}, headers=H(admin_token), timeout=10)
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "BAD_REQUEST"

    def test_create_masked_and_member_id(self, admin_token, state):
        uid = _mk_customer(admin_token, state, "Alexander Wijaya")
        r = requests.post(f"{API}/admin/membership", json={"customer_id": uid}, headers=H(admin_token), timeout=10)
        assert r.status_code == 201, r.text
        d = r.json()["data"]
        assert d["card_number"].startswith("AZR-MEM-"), d["card_number"]
        assert not d["card_number"].startswith("AZR-GEM-")  # distinct from cert number
        assert d["masked_name"] == "Alex***** Wij***"  # locked masking
        assert d["status"] == "active"
        assert "verify_token" in d and d["verify_url"]
        state["memberships"].append(d["uuid"])
        state["_mtoken"] = d["verify_token"]
        state["_mcust"] = uid

    def test_duplicate_current_conflict(self, admin_token, state):
        uid = state["_mcust"]
        r = requests.post(f"{API}/admin/membership", json={"customer_id": uid}, headers=H(admin_token), timeout=10)
        assert r.status_code == 409

    def test_public_verify_valid_then_inactive(self, admin_token, state):
        tok = state["_mtoken"]
        r = requests.get(f"{API}/membership/verify", params={"t": tok}, timeout=10)
        d = r.json()["data"] if "data" in r.json() else r.json()
        assert d["valid"] is True and d["status"] == "active"
        assert d["member_id"].startswith("AZR-MEM-")
        assert d["member_name"] == "Alex***** Wij***"
        # no PII / secrets leaked (inspect the member-safe payload only)
        import json as _json
        blob = _json.dumps(d).lower()
        for bad in ["email", "phone", "password", "customer_id", "token"]:
            assert bad not in blob, f"leak: {bad}"
        # set inactive -> public verify valid:false
        mid = state["memberships"][0]
        requests.post(f"{API}/admin/membership/{mid}/status", json={"status": "inactive"}, headers=H(admin_token), timeout=10)
        r2 = requests.get(f"{API}/membership/verify", params={"t": tok}, timeout=10)
        d2 = r2.json()["data"] if "data" in r2.json() else r2.json()
        assert d2["valid"] is False and d2["status"] == "inactive"

    def test_bad_token_invalid(self):
        r = requests.get(f"{API}/membership/verify", params={"t": "garbage.token.here"}, timeout=10)
        d = r.json()["data"] if "data" in r.json() else r.json()
        assert d["valid"] is False

    def test_reissue_creates_v2(self, admin_token, state):
        mid = state["memberships"][0]
        r = requests.post(f"{API}/admin/membership/{mid}/reissue", headers=H(admin_token), timeout=10)
        assert r.status_code == 200, r.text
        d = r.json()["data"]
        assert d["version"] == 2 and d["is_current"] is True
        state["memberships"].append(d["uuid"])

    def test_rbac_membership(self, cm_token, cs_token, admin_token, state):
        uid = state["_mcust"]
        # CM has no membership perms at all
        assert requests.get(f"{API}/admin/membership", headers=H(cm_token), timeout=10).status_code == 403
        # CS read ok, write forbidden
        assert requests.get(f"{API}/admin/membership", headers=H(cs_token), timeout=10).status_code == 200
        assert requests.post(f"{API}/admin/membership", json={"customer_id": uid}, headers=H(cs_token), timeout=10).status_code == 403
        assert requests.get(f"{API}/admin/membership", timeout=10).status_code == 401

    def test_membership_counter_is_separate_from_cert_counter(self):
        import asyncio

        async def chk():
            c = AsyncIOMotorClient(MONGO_URL)
            db = c[DB_NAME]
            mem = await db.counters.find_one({"name": "membership", "year": 2026})
            cert = await db.counters.find_one({"name": "certificate", "year": 2026})
            c.close()
            return mem, cert
        mem, cert = asyncio.run(chk())
        # Membership Member IDs come from their OWN counter doc — distinct from the
        # certificate counter (which only moves on genuine certificate issuance).
        assert mem and mem["last_number"] >= 1, mem
        assert cert and cert["name"] == "certificate"


# ============================================================
# ZZ Cleanup + baseline invariants
# ============================================================
def test_zz_cleanup_and_invariants(admin_token, state):
    for cid in state["certificates"]:
        requests.post(f"{API}/admin/certificates/{cid}/revoke", headers=H(admin_token), timeout=10)

    import asyncio

    async def cleanup():
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        # Hermetic teardown: these business collections have a baseline of 0, so a
        # full wipe is deterministic and leaves no test residue (no cross-run drift).
        for col in ["customers", "gemstones", "gemstone_photos", "certificates",
                    "verification_tokens", "warranties", "ownership_transfers", "membership_cards"]:
            await db[col].delete_many({})
        # Reset certificate counter to baseline; remove BATCH C operational counters.
        await db.counters.update_one({"name": "certificate", "year": 2026}, {"$set": {"last_number": 14}})
        await db.counters.delete_many({"name": {"$in": ["warranty", "membership"]}})
        # Purge audit for test entities
        purge = (list(state["customers"]) + list(state["gemstones"]) + list(state["warranties"]) +
                 list(state["transfers"]) + list(state["memberships"]) + list(state["certificates"]))
        if purge:
            await db.audit_logs.delete_many({"entity_id": {"$in": purge}})

        results = {}
        for col in ["certificates", "gemstones", "jewelry", "customers", "warranties",
                    "ownership_transfers", "membership_cards", "verification_tokens", "media", "media_objects"]:
            results[col] = await db[col].count_documents({})
        counter = await db.counters.find_one({"name": "certificate", "year": 2026})
        client.close()
        return results, counter

    results, counter = asyncio.run(cleanup())
    for k, v in results.items():
        assert v == 0, f"{k} must be 0, got {v}"
    assert counter and counter.get("last_number") == 14, f"counter last_number must be 14, got {counter}"
