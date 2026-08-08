"""Batch A full regression — Sprint 8 (envelope) + Sprint 9 (correlation logs)
+ Sprint 10 (media adapter), plus FASE 2/3 regression through the envelope.

Business rule: DB must remain clean (certificates=0, gemstones=0, counter
last_number=14, media=0, media_objects=0). All test artefacts must be
cleaned up (media docs + verification/security logs with our correlation ids).
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

ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PW = "AzurisDev@2026!"
CM_EMAIL = "cm@azuris.local"
CM_PW = "CmDev@2026!"

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


def _tiny_png() -> bytes:
    """Deterministic 2x2 PNG (valid image_content, decodable by PIL)."""
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)  # 2x2 RGB
    raw = b"\x00" + b"\xff\x00\x00\x00\xff\x00" + b"\x00" + b"\x00\x00\xff\xff\xff\xff"
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


PNG_BYTES = _tiny_png()


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def admin_token() -> str:
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PW}, timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True, body
    return body["data"]["access_token"]


@pytest.fixture(scope="session")
def cm_token() -> str:
    r = requests.post(f"{API}/auth/login", json={"email": CM_EMAIL, "password": CM_PW}, timeout=15)
    if r.status_code != 200:
        pytest.skip("CONTENT_MANAGER seed missing")
    return r.json()["data"]["access_token"]


@pytest.fixture(scope="session")
def created_media() -> list[str]:
    """Track uuids to guarantee cleanup even if a test fails."""
    return []


@pytest.fixture(scope="session")
def correlation_ids() -> list[str]:
    return []


# --------------------------------------------------------------------------- #
# SPRINT 8 — response envelope
# --------------------------------------------------------------------------- #
class TestSprint8Envelope:
    def test_settings_public_is_wrapped(self):
        r = requests.get(f"{API}/settings/public", timeout=10)
        assert r.status_code == 200
        assert r.headers.get("X-Request-ID"), "missing X-Request-ID header"
        body = r.json()
        assert body["success"] is True
        assert "data" in body and "meta" in body
        assert body["meta"].get("request_id")
        assert body["data"].get("whatsapp_number") == "6287812128884"

    def test_health_is_not_wrapped(self):
        r = requests.get(f"{API}/health", timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "success" not in body, f"health must be raw, got {body}"
        assert "status" in body

    def test_unauthorized_admin_settings_error_envelope(self):
        r = requests.get(f"{API}/admin/settings", timeout=10)
        assert r.status_code == 401
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] == "UNAUTHORIZED"
        assert body["meta"].get("request_id")

    def test_not_found_route_envelope(self):
        r = requests.get(f"{API}/does-not-exist-xyz", timeout=10)
        assert r.status_code == 404
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] == "NOT_FOUND"

    def test_validation_error_envelope(self):
        r = requests.post(f"{API}/verify", json={}, timeout=10)
        assert r.status_code == 422
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert isinstance(body["error"]["details"], list) and body["error"]["details"]
        det = body["error"]["details"][0]
        assert set(det.keys()) >= {"field", "message", "type"}

    def test_x_request_id_echoed_from_client(self):
        rid = f"TEST-RID-{uuid.uuid4().hex[:12]}"
        r = requests.get(f"{API}/settings/public", headers={"X-Request-ID": rid}, timeout=10)
        assert r.status_code == 200
        assert r.headers.get("X-Request-ID") == rid
        assert r.json()["meta"]["request_id"] == rid


# --------------------------------------------------------------------------- #
# SPRINT 9 — correlation logging
# --------------------------------------------------------------------------- #
class TestSprint9Logging:
    def test_verify_writes_verification_log_with_correlation(self, correlation_ids):
        rid = f"TEST-VER-{uuid.uuid4().hex[:12]}"
        correlation_ids.append(rid)
        r = requests.post(
            f"{API}/verify",
            json={"certificate_number": "AZR-GEM-999999-99", "security_code": "zzz"},
            headers={"X-Request-ID": rid},
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "not_found"
        # Verify DB row via motor (async)
        import asyncio
        async def _check():
            client = AsyncIOMotorClient(MONGO_URL)
            db = client[DB_NAME]
            doc = await db.verification_logs.find_one({"correlation_id": rid})
            client.close()
            return doc
        doc = asyncio.run(_check())
        assert doc is not None, f"verification_logs row for correlation_id={rid} not found"
        # PII / secrets must not be present
        assert "security_code" not in doc
        assert "qr_token" not in doc
        assert doc.get("ip_hash") is None or len(doc["ip_hash"]) == 64  # sha256 hex
        # Cert number must be masked (or None)
        cnm = doc.get("certificate_number_masked")
        assert cnm is None or "AZR-GEM-9" not in cnm or cnm.endswith("***")

    def test_failed_login_writes_security_log_with_correlation(self, correlation_ids):
        rid = f"TEST-SEC-{uuid.uuid4().hex[:12]}"
        correlation_ids.append(rid)
        r = requests.post(
            f"{API}/auth/login",
            json={"email": ADMIN_EMAIL, "password": "wrong-password-xxx"},
            headers={"X-Request-ID": rid},
            timeout=10,
        )
        assert r.status_code == 401
        import asyncio
        async def _check():
            client = AsyncIOMotorClient(MONGO_URL)
            db = client[DB_NAME]
            doc = await db.security_logs.find_one({"correlation_id": rid})
            client.close()
            return doc
        doc = asyncio.run(_check())
        assert doc is not None
        assert doc.get("success") is False
        assert "password" not in doc
        # IP must be hashed, not plain
        if doc.get("ip_hash"):
            assert len(doc["ip_hash"]) == 64


# --------------------------------------------------------------------------- #
# SPRINT 10 — media adapter
# --------------------------------------------------------------------------- #
class TestSprint10Media:
    def test_unauthorized_upload_401(self):
        files = {"file": ("t.png", PNG_BYTES, "image/png")}
        data = {"entity_type": "gemstone", "entity_id": "TEST-x", "role": "gallery", "visibility": "public"}
        r = requests.post(f"{API}/admin/media", files=files, data=data, timeout=15)
        assert r.status_code == 401
        assert r.json()["error"]["code"] == "UNAUTHORIZED"

    def test_cm_denied_media_mutation_403(self, cm_token):
        files = {"file": ("t.png", PNG_BYTES, "image/png")}
        data = {"entity_type": "gemstone", "entity_id": "TEST-x", "role": "gallery", "visibility": "public"}
        r = requests.post(
            f"{API}/admin/media", files=files, data=data,
            headers={"Authorization": f"Bearer {cm_token}"}, timeout=15,
        )
        assert r.status_code == 403, r.text
        assert r.json()["error"]["code"] == "FORBIDDEN"

    def test_upload_public_and_serve(self, admin_token, created_media):
        files = {"file": ("pub.png", PNG_BYTES, "image/png")}
        data = {"entity_type": "gemstone", "entity_id": "TEST-BATCHA", "role": "gallery", "visibility": "public"}
        r = requests.post(
            f"{API}/admin/media", files=files, data=data,
            headers={"Authorization": f"Bearer {admin_token}"}, timeout=20,
        )
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["success"] is True
        m = body["data"]
        assert m["mime_type"] == "image/png"
        assert m["visibility"] == "public"
        assert m["width"] == 2 and m["height"] == 2
        assert m["url"].startswith("/api/media/")
        created_media.append(m["uuid"])

        # Public serve returns raw bytes with content-type image/png (NOT wrapped)
        r2 = requests.get(f"{API}/media/{m['uuid']}", timeout=15)
        assert r2.status_code == 200
        assert r2.headers["content-type"].startswith("image/png")
        assert r2.content[:8] == b"\x89PNG\r\n\x1a\n"

    def test_upload_private_hidden_from_public_but_admin_raw_ok(self, admin_token, created_media):
        files = {"file": ("priv.png", PNG_BYTES, "image/png")}
        data = {"entity_type": "gemstone", "entity_id": "TEST-BATCHA", "role": "gallery", "visibility": "private"}
        r = requests.post(
            f"{API}/admin/media", files=files, data=data,
            headers={"Authorization": f"Bearer {admin_token}"}, timeout=20,
        )
        assert r.status_code == 201
        m = r.json()["data"]
        created_media.append(m["uuid"])

        # Public must NOT serve private
        rp = requests.get(f"{API}/media/{m['uuid']}", timeout=15)
        assert rp.status_code == 404
        assert rp.json()["error"]["code"] == "NOT_FOUND"

        # Admin raw endpoint must serve it
        ra = requests.get(
            f"{API}/admin/media/{m['uuid']}/raw",
            headers={"Authorization": f"Bearer {admin_token}"}, timeout=15,
        )
        assert ra.status_code == 200
        assert ra.headers["content-type"].startswith("image/png")

    def test_list_media_by_entity(self, admin_token):
        r = requests.get(
            f"{API}/admin/media",
            params={"entity_type": "gemstone", "entity_id": "TEST-BATCHA"},
            headers={"Authorization": f"Bearer {admin_token}"}, timeout=15,
        )
        assert r.status_code == 200
        body = r.json()["data"]
        assert body["total"] >= 2
        assert all(it["entity_id"] == "TEST-BATCHA" for it in body["items"])

    def test_unsupported_content_type_400(self, admin_token):
        files = {"file": ("a.txt", b"hello", "text/plain")}
        data = {"entity_type": "gemstone", "entity_id": "TEST-BATCHA", "role": "gallery", "visibility": "public"}
        r = requests.post(
            f"{API}/admin/media", files=files, data=data,
            headers={"Authorization": f"Bearer {admin_token}"}, timeout=15,
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "BAD_REQUEST"

    def test_delete_media_then_public_404(self, admin_token, created_media):
        # Upload one specifically for deletion so cleanup accounting stays simple
        files = {"file": ("del.png", PNG_BYTES, "image/png")}
        data = {"entity_type": "gemstone", "entity_id": "TEST-BATCHA", "role": "gallery", "visibility": "public"}
        r = requests.post(
            f"{API}/admin/media", files=files, data=data,
            headers={"Authorization": f"Bearer {admin_token}"}, timeout=20,
        )
        assert r.status_code == 201
        uid = r.json()["data"]["uuid"]

        rd = requests.delete(
            f"{API}/admin/media/{uid}",
            headers={"Authorization": f"Bearer {admin_token}"}, timeout=15,
        )
        assert rd.status_code == 200
        assert rd.json()["data"]["deleted"] is True

        # Public serve must 404 after delete
        rg = requests.get(f"{API}/media/{uid}", timeout=10)
        assert rg.status_code == 404


# --------------------------------------------------------------------------- #
# FASE 2/3 regression through envelope
# --------------------------------------------------------------------------- #
class TestFaseRegression:
    def test_verify_valid_format_wrong_code(self):
        r = requests.post(
            f"{API}/verify",
            json={"certificate_number": "AZR-GEM-000015-26", "security_code": "nope"},
            timeout=10,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["data"]["status"] == "not_found"
        assert body["data"]["certificate"] is None

    def test_verify_malformed_number(self):
        r = requests.post(
            f"{API}/verify",
            json={"certificate_number": "BAD-FORMAT", "security_code": "x"},
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "not_found"

    def test_qr_resolve_bad_token(self):
        r = requests.get(f"{API}/verify/qr/resolve", params={"token": "bad"}, timeout=10)
        assert r.status_code == 200
        assert r.json()["data"]["token_valid"] is False

    def test_auth_me_via_envelope(self, admin_token):
        r = requests.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {admin_token}"}, timeout=10)
        assert r.status_code == 200
        me = r.json()["data"]
        assert me["email"] == ADMIN_EMAIL
        assert me["role"] == "SUPER_ADMIN"

    def test_auth_refresh_and_logout(self):
        r = requests.post(
            f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PW}, timeout=10,
        )
        d = r.json()["data"]
        rr = requests.post(f"{API}/auth/refresh", json={"refresh_token": d["refresh_token"]}, timeout=10)
        assert rr.status_code == 200
        d2 = rr.json()["data"]
        assert d2["access_token"]
        lo = requests.post(
            f"{API}/auth/logout",
            headers={"Authorization": f"Bearer {d2['access_token']}"},
            json={"refresh_token": d2["refresh_token"]},
            timeout=10,
        )
        assert lo.status_code == 200

    def test_legality_public_unpublished(self):
        r = requests.get(f"{API}/legality", timeout=10)
        assert r.status_code == 200
        assert r.json()["data"].get("published") is False


# --------------------------------------------------------------------------- #
# CLEANUP + baseline invariants
# --------------------------------------------------------------------------- #
def test_zz_cleanup_and_invariants(admin_token, created_media, correlation_ids):
    # Delete all media we created (idempotent)
    for uid in created_media:
        requests.delete(
            f"{API}/admin/media/{uid}",
            headers={"Authorization": f"Bearer {admin_token}"}, timeout=10,
        )

    import asyncio
    async def _cleanup_and_check():
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        # Hard-remove our test media docs + media_objects (soft-deleted docs still count)
        media_docs = await db.media.find({"entity_id": "TEST-BATCHA"}).to_list(length=None)
        keys = [m.get("storage_key") for m in media_docs if m.get("storage_key")]
        if media_docs:
            await db.media.delete_many({"entity_id": "TEST-BATCHA"})
        if keys:
            await db.media_objects.delete_many({"key": {"$in": keys}})
        # Remove test correlation-id log rows
        if correlation_ids:
            await db.verification_logs.delete_many({"correlation_id": {"$in": correlation_ids}})
            await db.security_logs.delete_many({"correlation_id": {"$in": correlation_ids}})
            await db.audit_logs.delete_many({"correlation_id": {"$in": correlation_ids}})

        # Also remove any media-audit rows created during uploads / deletes
        # (entity_type=media created/deleted during this run — safe to purge audit
        # rows targeting our test uuids only)
        if created_media:
            await db.audit_logs.delete_many({"entity_type": "media", "entity_id": {"$in": created_media}})

        # Baseline invariants
        certs = await db.certificates.count_documents({})
        gems = await db.gemstones.count_documents({})
        media_left = await db.media.count_documents({})
        objs_left = await db.media_objects.count_documents({})
        counter = await db.counters.find_one({"name": "certificate", "year": 2026}) or await db.counters.find_one({"_id": "certificate"}) or {}
        client.close()
        return certs, gems, media_left, objs_left, counter

    certs, gems, media_left, objs_left, counter = asyncio.run(_cleanup_and_check())

    assert certs == 0, f"certificates must be 0, got {certs}"
    assert gems == 0, f"gemstones must be 0, got {gems}"
    assert media_left == 0, f"media docs left: {media_left}"
    assert objs_left == 0, f"media_objects left: {objs_left}"

    # Counter shape depends on impl; support {years:{2026:{last_number:14}}} or year-scoped doc
    def _extract_last(c):
        if not c:
            return None
        if "last_number" in c:
            return c["last_number"]
        y = c.get("years") or {}
        entry = y.get("2026") or y.get(2026) or {}
        return entry.get("last_number")
    last = _extract_last(counter)
    assert last == 14, f"counter last_number must remain 14, got {last} (doc={counter})"
