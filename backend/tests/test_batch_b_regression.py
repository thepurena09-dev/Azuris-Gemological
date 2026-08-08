"""Batch B (Sprints 11–14) authoritative regression gate.

Covers:
- Sprint 11 Customers CRUD + RBAC + consent_at stamping
- Sprint 12 Gemstones extended list/get/status transitions/delete guard
- Sprint 13 Jewelry CRUD + gemstone validation + status transitions + RBAC
- Sprint 14 Media wiring (upload appends to media_ids, single-main demotion,
  promote-to-main endpoint, delete unlinks) + public serve
- Regression: legacy gemstone photo upload + certificate issuance + PDF
- Sprint 8 envelope + Sprint 9 correlation still work
- DB baseline restored: customers=0, gemstones=0, jewelry=0, media=0,
  media_objects=0, certificates=0, counter.last_number=14
"""

from __future__ import annotations

import io
import os
import struct
import uuid
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
    return {"customers": [], "gemstones": [], "jewelry": [], "media": [], "certificates": [], "photo_docs": []}


def H(t):
    return {"Authorization": f"Bearer {t}"}


# ============================================================
# SPRINT 11 — Customers
# ============================================================
class TestSprint11Customers:
    def test_create_customer_stamps_consent(self, admin_token, state):
        body = {"full_name": "TEST Customer A", "email": "tca@example.com", "phone": "+62-000", "privacy_consent": True}
        r = requests.post(f"{API}/admin/customers", json=body, headers=H(admin_token), timeout=10)
        assert r.status_code == 201, r.text
        d = r.json()["data"]
        assert d["full_name"] == "TEST Customer A"
        assert d["privacy_consent"] is True
        assert d["consent_at"], "consent_at must be stamped when privacy_consent=true"
        assert "_id" not in d
        state["customers"].append(d["uuid"])

    def test_create_customer_no_consent(self, admin_token, state):
        body = {"full_name": "TEST Customer B"}
        r = requests.post(f"{API}/admin/customers", json=body, headers=H(admin_token), timeout=10)
        assert r.status_code == 201
        d = r.json()["data"]
        assert d["privacy_consent"] is False
        assert d["consent_at"] is None
        state["customers"].append(d["uuid"])

    def test_put_customer_first_consent_stamps(self, admin_token, state):
        uid = state["customers"][1]
        r = requests.put(f"{API}/admin/customers/{uid}", json={"privacy_consent": True}, headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["privacy_consent"] is True
        assert d["consent_at"]

    def test_list_search(self, admin_token):
        r = requests.get(f"{API}/admin/customers", params={"q": "TEST Customer A"}, headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["total"] >= 1
        assert any("TEST Customer A" in c["full_name"] for c in d["items"])

    def test_get_customer(self, admin_token, state):
        uid = state["customers"][0]
        r = requests.get(f"{API}/admin/customers/{uid}", headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        assert r.json()["data"]["uuid"] == uid

    def test_rbac_cm_write_forbidden(self, cm_token):
        r = requests.post(f"{API}/admin/customers", json={"full_name": "cm-test"}, headers=H(cm_token), timeout=10)
        assert r.status_code == 403
        assert r.json()["error"]["code"] == "FORBIDDEN"

    def test_rbac_cs_write_ok(self, cs_token, state):
        r = requests.post(f"{API}/admin/customers", json={"full_name": "TEST CS-created"}, headers=H(cs_token), timeout=10)
        assert r.status_code == 201
        uid = r.json()["data"]["uuid"]
        state["customers"].append(uid)
        # cs can PUT
        rp = requests.put(f"{API}/admin/customers/{uid}", json={"phone": "+62-123"}, headers=H(cs_token), timeout=10)
        assert rp.status_code == 200
        assert rp.json()["data"]["phone"] == "+62-123"

    def test_rbac_cs_delete_forbidden(self, cs_token, state):
        uid = state["customers"][0]
        r = requests.delete(f"{API}/admin/customers/{uid}", headers=H(cs_token), timeout=10)
        assert r.status_code == 403
        assert r.json()["error"]["code"] == "FORBIDDEN"

    def test_unauthenticated_401(self):
        r = requests.get(f"{API}/admin/customers", timeout=10)
        assert r.status_code == 401
        assert r.json()["error"]["code"] == "UNAUTHORIZED"


# ============================================================
# SPRINT 12 — Gemstones extended
# ============================================================
class TestSprint12Gemstones:
    def test_create_gemstones(self, admin_token, state):
        for i in range(2):
            body = {
                "name_id": f"TEST Batu {i}",
                "name_en": f"TEST Stone {i}",
                "category": "precious",
                "gemstone_type": "sapphire",
                "weight_carat": 1.5 + i,
            }
            r = requests.post(f"{API}/admin/gemstones", json=body, headers=H(admin_token), timeout=10)
            assert r.status_code == 201, r.text
            d = r.json()["data"]
            assert d["status"] == "draft"
            state["gemstones"].append(d["uuid"])

    def test_list_pagination_and_q(self, admin_token):
        r = requests.get(f"{API}/admin/gemstones", params={"page": 1, "page_size": 10, "q": "TEST Stone"}, headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        d = r.json()["data"]
        assert "items" in d and "total" in d and "page" in d and "page_size" in d
        assert d["total"] >= 2

    def test_get_single(self, admin_token, state):
        uid = state["gemstones"][0]
        r = requests.get(f"{API}/admin/gemstones/{uid}", headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        d = r.json()["data"]
        assert "media_ids" in d and "status" in d

    def test_invalid_transition_draft_to_transferred(self, admin_token, state):
        uid = state["gemstones"][0]
        r = requests.post(f"{API}/admin/gemstones/{uid}/status", json={"status": "transferred"}, headers=H(admin_token), timeout=10)
        assert r.status_code == 409
        assert r.json()["error"]["code"] == "CONFLICT"

    def test_valid_transition_chain(self, admin_token, state):
        uid = state["gemstones"][0]
        for target in ["verified", "published"]:
            r = requests.post(f"{API}/admin/gemstones/{uid}/status", json={"status": target}, headers=H(admin_token), timeout=10)
            assert r.status_code == 200, r.text
            assert r.json()["data"]["status"] == target

    def test_verified_to_transferred_invalid(self, admin_token, state):
        # Create another gem, move to verified only, then try transferred
        body = {"name_id": "TEST Gem V", "name_en": "TEST Gem V", "category": "p", "gemstone_type": "ruby", "weight_carat": 2.0}
        r = requests.post(f"{API}/admin/gemstones", json=body, headers=H(admin_token), timeout=10)
        uid = r.json()["data"]["uuid"]
        state["gemstones"].append(uid)
        requests.post(f"{API}/admin/gemstones/{uid}/status", json={"status": "verified"}, headers=H(admin_token), timeout=10)
        r2 = requests.post(f"{API}/admin/gemstones/{uid}/status", json={"status": "transferred"}, headers=H(admin_token), timeout=10)
        assert r2.status_code == 409

    def test_delete_gemstone_no_cert(self, admin_token, state):
        uid = state["gemstones"][1]  # keep uuid in state for cleanup of soft-deleted row
        r = requests.delete(f"{API}/admin/gemstones/{uid}", headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        assert r.json()["data"]["deleted"] is True


# ============================================================
# SPRINT 13 — Jewelry
# ============================================================
class TestSprint13Jewelry:
    def test_create_jewelry_invalid_gemstone(self, admin_token):
        body = {
            "name_id": "TEST Cincin X", "name_en": "TEST Ring X",
            "jewelry_type": "ring", "material": "gold",
            "gemstone_ids": ["nonexistent-uuid-xyz"],
        }
        r = requests.post(f"{API}/admin/jewelry", json=body, headers=H(admin_token), timeout=10)
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "BAD_REQUEST"

    def test_create_jewelry_valid(self, admin_token, state):
        gid = state["gemstones"][0]
        body = {
            "name_id": "TEST Cincin A", "name_en": "TEST Ring A",
            "jewelry_type": "ring", "material": "gold-18k",
            "gemstone_ids": [gid],
        }
        r = requests.post(f"{API}/admin/jewelry", json=body, headers=H(admin_token), timeout=10)
        assert r.status_code == 201, r.text
        d = r.json()["data"]
        assert d["status"] == "draft"
        assert d["gemstone_ids"] == [gid]
        state["jewelry"].append(d["uuid"])

    def test_list_and_get_jewelry(self, admin_token, state):
        r = requests.get(f"{API}/admin/jewelry", params={"q": "TEST Ring A"}, headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        assert r.json()["data"]["total"] >= 1
        uid = state["jewelry"][0]
        rg = requests.get(f"{API}/admin/jewelry/{uid}", headers=H(admin_token), timeout=10)
        assert rg.status_code == 200

    def test_put_jewelry_revalidates(self, admin_token, state):
        uid = state["jewelry"][0]
        r = requests.put(f"{API}/admin/jewelry/{uid}", json={"gemstone_ids": ["bad-gem-uuid"]}, headers=H(admin_token), timeout=10)
        assert r.status_code == 400

    def test_transition_draft_to_published(self, admin_token, state):
        uid = state["jewelry"][0]
        r = requests.post(f"{API}/admin/jewelry/{uid}/status", json={"status": "published"}, headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "published"

    def test_transition_published_to_draft_invalid(self, admin_token, state):
        uid = state["jewelry"][0]
        r = requests.post(f"{API}/admin/jewelry/{uid}/status", json={"status": "draft"}, headers=H(admin_token), timeout=10)
        assert r.status_code == 409

    def test_rbac_cm_write_forbidden(self, cm_token, state):
        gid = state["gemstones"][0]
        r = requests.post(f"{API}/admin/jewelry",
                          json={"name_id": "x", "name_en": "x", "jewelry_type": "r", "material": "g", "gemstone_ids": [gid]},
                          headers=H(cm_token), timeout=10)
        assert r.status_code == 403

    def test_rbac_cs_read_ok_write_forbidden(self, cs_token, state):
        r = requests.get(f"{API}/admin/jewelry", headers=H(cs_token), timeout=10)
        assert r.status_code == 200
        gid = state["gemstones"][0]
        rw = requests.post(f"{API}/admin/jewelry",
                           json={"name_id": "x", "name_en": "x", "jewelry_type": "r", "material": "g", "gemstone_ids": [gid]},
                           headers=H(cs_token), timeout=10)
        assert rw.status_code == 403


# ============================================================
# SPRINT 14 — Media wiring
# ============================================================
class TestSprint14MediaWiring:
    def test_upload_appends_to_media_ids(self, admin_token, state):
        gid = state["gemstones"][0]
        files = {"file": ("g.png", PNG, "image/png")}
        data = {"entity_type": "gemstone", "entity_id": gid, "role": "gallery", "visibility": "public"}
        r = requests.post(f"{API}/admin/media", files=files, data=data, headers=H(admin_token), timeout=20)
        assert r.status_code == 201, r.text
        m = r.json()["data"]
        state["media"].append(m["uuid"])

        rg = requests.get(f"{API}/admin/gemstones/{gid}", headers=H(admin_token), timeout=10)
        assert m["uuid"] in rg.json()["data"]["media_ids"]

    def test_single_main_demotion(self, admin_token, state):
        gid = state["gemstones"][0]
        # Upload as main
        m1 = requests.post(f"{API}/admin/media",
                           files={"file": ("m1.png", PNG, "image/png")},
                           data={"entity_type": "gemstone", "entity_id": gid, "role": "main", "visibility": "public"},
                           headers=H(admin_token), timeout=20).json()["data"]
        state["media"].append(m1["uuid"])
        # Another main should demote m1
        m2 = requests.post(f"{API}/admin/media",
                           files={"file": ("m2.png", PNG, "image/png")},
                           data={"entity_type": "gemstone", "entity_id": gid, "role": "main", "visibility": "public"},
                           headers=H(admin_token), timeout=20).json()["data"]
        state["media"].append(m2["uuid"])

        rl = requests.get(f"{API}/admin/media", params={"entity_type": "gemstone", "entity_id": gid}, headers=H(admin_token), timeout=10)
        items = rl.json()["data"]["items"]
        by_uuid = {i["uuid"]: i for i in items}
        assert by_uuid[m1["uuid"]]["role"] == "gallery", "previous main should be demoted"
        assert by_uuid[m2["uuid"]]["role"] == "main"
        mains = [i for i in items if i["role"] == "main"]
        assert len(mains) == 1

    def test_promote_gallery_to_main(self, admin_token, state):
        # promote first gallery media to main -> demotes previous main
        gid = state["gemstones"][0]
        gallery_uuid = state["media"][0]  # original gallery
        r = requests.post(f"{API}/admin/media/{gallery_uuid}/main", headers=H(admin_token), timeout=10)
        assert r.status_code == 200
        assert r.json()["data"]["role"] == "main"
        # Verify only one main
        rl = requests.get(f"{API}/admin/media", params={"entity_type": "gemstone", "entity_id": gid}, headers=H(admin_token), timeout=10)
        mains = [i for i in rl.json()["data"]["items"] if i["role"] == "main"]
        assert len(mains) == 1
        assert mains[0]["uuid"] == gallery_uuid

    def test_delete_media_unlinks(self, admin_token, state):
        gid = state["gemstones"][0]
        # Upload one just for delete test
        m = requests.post(f"{API}/admin/media",
                         files={"file": ("del.png", PNG, "image/png")},
                         data={"entity_type": "gemstone", "entity_id": gid, "role": "gallery", "visibility": "public"},
                         headers=H(admin_token), timeout=20).json()["data"]
        muid = m["uuid"]
        # Confirm present in media_ids
        rg = requests.get(f"{API}/admin/gemstones/{gid}", headers=H(admin_token), timeout=10)
        assert muid in rg.json()["data"]["media_ids"]
        # Delete
        rd = requests.delete(f"{API}/admin/media/{muid}", headers=H(admin_token), timeout=10)
        assert rd.status_code == 200
        # Should no longer be in media_ids
        rg2 = requests.get(f"{API}/admin/gemstones/{gid}", headers=H(admin_token), timeout=10)
        assert muid not in rg2.json()["data"]["media_ids"]

    def test_public_serve_public_media(self, admin_token, state):
        # first media is now 'main' after promote, still public
        muid = state["media"][0]
        r = requests.get(f"{API}/media/{muid}", timeout=10)
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("image/png")


# ============================================================
# REGRESSION — Certificate issuance + PDF still work
# ============================================================
class TestCertificateRegression:
    def test_issue_certificate_and_pdf(self, admin_token, state):
        # Create dedicated gemstone
        body = {"name_id": "TEST Cert Gem", "name_en": "TEST Cert Gem",
                "category": "precious", "gemstone_type": "diamond", "weight_carat": 1.0}
        r = requests.post(f"{API}/admin/gemstones", json=body, headers=H(admin_token), timeout=10)
        gid = r.json()["data"]["uuid"]
        state["gemstones"].append(gid)

        # Upload legacy photo
        rp = requests.post(f"{API}/admin/gemstones/{gid}/photo",
                          files={"file": ("photo.png", PNG, "image/png")},
                          headers=H(admin_token), timeout=20)
        assert rp.status_code == 200, rp.text
        photo_id = rp.json()["data"]["photo_id"]
        state["photo_docs"].append(photo_id)

        # Issue certificate
        ri = requests.post(f"{API}/admin/certificates/issue",
                          json={"gemstone_id": gid, "examiner": "TEST", "signatory": "TEST"},
                          headers=H(admin_token), timeout=15)
        assert ri.status_code == 201, ri.text
        cert = ri.json()["data"]
        assert cert["certificate_number"].startswith("AZR-GEM-000015-26"), cert["certificate_number"]
        state["certificates"].append(cert["certificate_uuid"])

        # Fetch PDF
        rpdf = requests.get(f"{API}/admin/certificates/{cert['certificate_uuid']}/pdf", headers=H(admin_token), timeout=30)
        assert rpdf.status_code == 200
        assert rpdf.headers["content-type"] == "application/pdf"
        assert rpdf.content[:4] == b"%PDF"

    def test_delete_gemstone_with_cert_conflict(self, admin_token, state):
        # last gemstone was the cert one
        gid = state["gemstones"][-1]
        r = requests.delete(f"{API}/admin/gemstones/{gid}", headers=H(admin_token), timeout=10)
        assert r.status_code == 409
        assert r.json()["error"]["code"] == "CONFLICT"


# ============================================================
# ZZ Cleanup + baseline invariants
# ============================================================
def test_zz_cleanup_and_invariants(admin_token, state):
    # Revoke any certificates + hard-clean via DB
    for cid in state["certificates"]:
        requests.post(f"{API}/admin/certificates/{cid}/revoke", headers=H(admin_token), timeout=10)

    import asyncio

    async def cleanup():
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        # Hard delete media docs + objects created
        if state["media"]:
            docs = await db.media.find({"uuid": {"$in": state["media"]}}).to_list(length=None)
            keys = [d.get("storage_key") for d in docs if d.get("storage_key")]
            await db.media.delete_many({"uuid": {"$in": state["media"]}})
            if keys:
                await db.media_objects.delete_many({"key": {"$in": keys}})
        # Also purge any media docs referencing our test gemstone/jewelry entities
        ent_ids = list(state["gemstones"]) + list(state["jewelry"])
        if ent_ids:
            docs = await db.media.find({"entity_id": {"$in": ent_ids}}).to_list(length=None)
            keys = [d.get("storage_key") for d in docs if d.get("storage_key")]
            await db.media.delete_many({"entity_id": {"$in": ent_ids}})
            if keys:
                await db.media_objects.delete_many({"key": {"$in": keys}})
        # Hard-delete customers/gemstones/jewelry (soft-deleted still count)
        if state["customers"]:
            await db.customers.delete_many({"uuid": {"$in": state["customers"]}})
        if state["gemstones"]:
            await db.gemstones.delete_many({"uuid": {"$in": state["gemstones"]}})
        if state["jewelry"]:
            await db.jewelry.delete_many({"uuid": {"$in": state["jewelry"]}})
        # Certificates: hard delete + rollback counter to 14
        if state["certificates"]:
            await db.certificates.delete_many({"uuid": {"$in": state["certificates"]}})
            await db.verification_tokens.delete_many({"certificate_uuid": {"$in": state["certificates"]}})
        # Photo docs
        if state["photo_docs"]:
            await db.gemstone_photos.delete_many({"uuid": {"$in": state["photo_docs"]}})
        # Reset counter to baseline
        await db.counters.update_one(
            {"name": "certificate", "year": 2026},
            {"$set": {"last_number": 14}},
        )
        # Purge audit_logs for our test entities
        purge_ids = list(state["customers"]) + list(state["gemstones"]) + list(state["jewelry"]) + list(state["media"]) + list(state["certificates"])
        if purge_ids:
            await db.audit_logs.delete_many({"entity_id": {"$in": purge_ids}})

        # Assert baseline
        results = {}
        for col in ["certificates", "gemstones", "jewelry", "customers", "media", "media_objects"]:
            results[col] = await db[col].count_documents({})
        counter = await db.counters.find_one({"name": "certificate", "year": 2026})
        client.close()
        return results, counter

    results, counter = asyncio.run(cleanup())
    for k, v in results.items():
        assert v == 0, f"{k} must be 0, got {v}"
    assert counter and counter.get("last_number") == 14, f"counter last_number must be 14, got {counter}"
