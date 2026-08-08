"""FASE 3.3 — Public certificate front-cover preview.

Scope:
  * BACKEND regressions (read-only): fake number => not_found; QR resolve invalid
    token; /api/settings/public whatsapp; /api/legality unpublished/empty; no
    security_code or qr_token leakage across public verify + qr endpoints.
  * BACKEND preview E2E: create 1 TEST_ Blue Sapphire (Corundum) gemstone, issue
    a cert, POST /api/verify to get preview_token, GET /api/verify/preview?t=..
    returns 200 image/png with Cache-Control; PNG magic bytes present.
  * BACKEND preview token payload contains ONLY sub/ver/type/iat/exp — no
    security_code / qr_token / owner / _id.
  * BACKEND invalid token => 404 (no data leak).
  * BACKEND versioning: reissue -> current version becomes 2; verify returns v2
    preview_token; preview reflects v2. Old (archived) preview_token 404 because
    endpoint only serves current.
  * BACKEND robustness: verification response is complete and stable.
  * BACKEND counter untouched by verification.
  * MANDATORY CLEANUP + counter restore to 14.

Run:  pytest backend/tests/test_fase3_3_preview.py -v -o "addopts=" -s
"""

from __future__ import annotations

import os

import jwt
import pytest
import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
load_dotenv("/app/frontend/.env")

BASE = (os.environ.get("REACT_APP_BACKEND_URL") or "").rstrip("/")
API = f"{BASE}/api"
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALG = os.environ.get("JWT_ALGORITHM", "HS256")

ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PASSWORD = "AzurisDev@2026!"

RESTORE_COUNTER_TO = 14
COUNTER_YEAR = 2026

HEX24 = __import__("re").compile(r"\b[0-9a-fA-F]{24}\b")


@pytest.fixture(scope="module")
def admin_headers():
    r = requests.post(
        f"{API}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="module")
def mongo_db():
    from pymongo import MongoClient

    cli = MongoClient(MONGO_URL)
    db = cli[DB_NAME]
    yield db
    cli.close()


# --------- read-only regressions --------------------------------------
class TestReadOnlyRegressions:
    def test_verify_fake_number_returns_not_found_no_preview(self):
        r = requests.post(
            f"{API}/verify",
            json={"certificate_number": "AZR-GEM-999999-26", "security_code": "ABCD1234"},
            timeout=10,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert (d.get("status") or d.get("result")) == "not_found"
        assert d.get("certificate") in (None, {})
        blob = str(d)
        assert "preview_token" not in blob
        assert "security_code" not in blob

    def test_qr_resolve_invalid_token(self):
        r = requests.get(f"{API}/verify/qr/resolve", params={"token": "INVALIDTOKEN"}, timeout=10)
        assert r.status_code == 200
        assert r.json().get("token_valid") is False

    def test_settings_public_whatsapp(self):
        r = requests.get(f"{API}/settings/public", timeout=10)
        assert r.status_code == 200
        d = r.json()
        assert d.get("whatsapp_number") == "6287812128884"
        assert d.get("whatsapp_enabled") is True

    def test_legality_empty(self):
        r = requests.get(f"{API}/legality", timeout=10)
        assert r.status_code == 200
        data = r.json()
        if isinstance(data, list):
            assert len(data) == 0
        elif isinstance(data, dict):
            items = data.get("items")
            if items is not None:
                assert items == [] or all(not it.get("is_published") for it in items)
            else:
                assert not data.get("is_published") or not data.get("uuid")

    def test_preview_garbage_token_404(self):
        r = requests.get(f"{API}/verify/preview", params={"t": "garbage.garbage.garbage"}, timeout=10)
        assert r.status_code == 404

    def test_preview_empty_and_unsigned_404(self):
        # unsigned/expired/random tokens
        for tok in ["", "abc", "AAAA.BBBB.CCCC"]:
            r = requests.get(f"{API}/verify/preview", params={"t": tok}, timeout=10)
            assert r.status_code in (404, 422), f"got {r.status_code} for {tok!r}"


# --------- preview E2E ------------------------------------------------
class TestPreviewE2E:
    created = {
        "gemstone_uuid": None,
        "cert_uuid": None,
        "cert_number": None,
        "security_code": None,
        "qr_token": None,
        "preview_token_v1": None,
        "cert_uuid_v2": None,
        "cert_number_v2": None,
        "security_code_v2": None,
        "preview_token_v2": None,
    }

    def _counter_last_number(self, db):
        doc = db.counters.find_one({"name": "certificate", "year": COUNTER_YEAR})
        return (doc or {}).get("last_number")

    def test_01_baseline_counter(self, mongo_db):
        assert self._counter_last_number(mongo_db) == RESTORE_COUNTER_TO, (
            "PRECONDITION FAILED: counter.last_number is not 14 at start"
        )

    def test_02_create_gemstone(self, admin_headers):
        payload = {
            "name_id": "TEST_FASE33_Safir Biru",
            "name_en": "TEST_FASE33_Blue Sapphire",
            "category": "Blue Sapphire",
            "gemstone_type": "Corundum",
            "weight_carat": 3.42,
            "color": "Vivid Blue",
            "clarity": "VVS",
            "cut": "Brilliant",
            "shape": "Oval",
            "dimensions_mm": "9.10 x 7.05 x 4.80",
            "origin": "Ceylon (Sri Lanka)",
            "treatment": "Heated",
        }
        r = requests.post(f"{API}/admin/gemstones", json=payload, headers=admin_headers, timeout=15)
        assert r.status_code == 201, r.text
        self.__class__.created["gemstone_uuid"] = r.json()["uuid"]

    def test_03_issue_certificate(self, admin_headers):
        gid = self.created["gemstone_uuid"]
        r = requests.post(
            f"{API}/admin/certificates/issue",
            json={
                "gemstone_id": gid,
                "object_type": "Loose Stone",
                "transparency": "Transparent",
                "examiner": "TEST Gemologist",
                "signatory": "TEST Signatory",
                "conclusion": "Natural Blue Sapphire, heated.",
            },
            headers=admin_headers,
            timeout=20,
        )
        assert r.status_code == 201, r.text
        d = r.json()
        self.__class__.created.update({
            "cert_uuid": d["certificate_uuid"],
            "cert_number": d["certificate_number"],
            "security_code": d["security_code"],
            "qr_token": d["qr_token"],
        })

    def test_04_verify_returns_preview_token(self):
        r = requests.post(
            f"{API}/verify",
            json={
                "certificate_number": self.created["cert_number"],
                "security_code": self.created["security_code"],
            },
            timeout=10,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert (d.get("status") or d.get("result")) == "valid"
        cert = d.get("certificate") or {}
        pt = cert.get("preview_token")
        assert isinstance(pt, str) and len(pt) > 20
        self.__class__.created["preview_token_v1"] = pt

        blob = str(d)
        # No secrets leaked
        assert self.created["security_code"] not in blob
        assert self.created["qr_token"] not in blob
        # No _id / 24-hex leakage
        assert not HEX24.search(blob), f"possible ObjectId leak: {blob}"
        assert "_id" not in cert

    def test_05_preview_token_payload_minimal(self):
        pt = self.created["preview_token_v1"]
        assert JWT_SECRET, "JWT_SECRET not in env; cannot decode"
        payload = jwt.decode(pt, JWT_SECRET, algorithms=[JWT_ALG])
        assert set(payload.keys()) == {"sub", "ver", "type", "iat", "exp"}, payload
        assert payload["type"] == "cert_preview"
        assert payload["ver"] == 1
        # security_code / qr_token / owner never in payload
        assert self.created["security_code"] not in str(payload)
        assert self.created["qr_token"] not in str(payload)

    def test_06_preview_endpoint_returns_png(self):
        pt = self.created["preview_token_v1"]
        r = requests.get(f"{API}/verify/preview", params={"t": pt}, timeout=30)
        assert r.status_code == 200, r.text[:300]
        assert r.headers.get("content-type", "").startswith("image/png"), r.headers
        assert "cache-control" in {k.lower() for k in r.headers.keys()}
        assert r.content[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
        # sanity size
        assert len(r.content) > 1000

    def test_07_verify_qr_also_has_preview_token_no_leak(self):
        r = requests.post(f"{API}/verify/qr", json={"token": self.created["qr_token"]}, timeout=10)
        assert r.status_code == 200
        d = r.json()
        cert = d.get("certificate") or {}
        assert (d.get("status") or d.get("result")) == "valid"
        assert cert.get("preview_token")
        blob = str(d)
        assert self.created["security_code"] not in blob
        assert self.created["qr_token"] not in blob
        assert not HEX24.search(blob)

    def test_08_counter_unchanged_by_verification(self, mongo_db):
        # After issuance the counter should have advanced by exactly 1 (from 14 -> 15).
        # Verification calls above must NOT further increment it.
        n = self._counter_last_number(mongo_db)
        assert n == RESTORE_COUNTER_TO + 1, f"counter drift after verify: {n}"

    def test_09_reissue_and_preview_current_version(self, admin_headers, mongo_db):
        cu = self.created["cert_uuid"]
        r = requests.post(
            f"{API}/admin/certificates/{cu}/reissue",
            json={
                "gemstone_id": self.created["gemstone_uuid"],
                "object_type": "Loose Stone",
                "transparency": "Transparent",
                "examiner": "TEST Gemologist v2",
                "signatory": "TEST Signatory v2",
                "conclusion": "Natural Blue Sapphire, heated (reissue).",
            },
            headers=admin_headers,
            timeout=20,
        )
        assert r.status_code in (200, 201), r.text
        d = r.json()
        # Response contract may return the new cert doc
        new_uuid = d.get("certificate_uuid") or d.get("uuid")
        new_number = d.get("certificate_number")
        new_code = d.get("security_code")
        # reissue may not echo security_code — fetch from verification_tokens in DB
        if not new_code:
            new_cert = mongo_db.certificates.find_one({"uuid": new_uuid})
            assert new_cert, "reissued cert missing"
            vt_uuid = new_cert.get("verification_uuid")
            vt = mongo_db.verification_tokens.find_one({"uuid": vt_uuid}) if vt_uuid else None
            assert vt and vt.get("security_code"), "cannot find security_code for reissued cert"
            new_code = vt["security_code"]
        assert new_uuid and new_number and new_code, d
        self.__class__.created.update({
            "cert_uuid_v2": new_uuid,
            "cert_number_v2": new_number,
            "security_code_v2": new_code,
        })

        # Verify by same number -> version 2
        vr = requests.post(
            f"{API}/verify",
            json={"certificate_number": new_number, "security_code": new_code},
            timeout=10,
        )
        assert vr.status_code == 200, vr.text
        vd = vr.json()
        assert (vd.get("status") or vd.get("result")) == "valid"
        cert = vd.get("certificate") or {}
        assert cert.get("version") == 2, cert
        pt2 = cert.get("preview_token")
        assert pt2 and pt2 != self.created["preview_token_v1"]
        self.__class__.created["preview_token_v2"] = pt2

        # Preview reflects version 2 -> PNG 200
        pr = requests.get(f"{API}/verify/preview", params={"t": pt2}, timeout=30)
        assert pr.status_code == 200
        assert pr.content[:8] == b"\x89PNG\r\n\x1a\n"

        # Decode v2 token, ver==2
        payload = jwt.decode(pt2, JWT_SECRET, algorithms=[JWT_ALG])
        assert payload["ver"] == 2

    def test_10_archived_version_token_not_previewable(self):
        # v1 preview_token still decodes but the underlying cert is no longer
        # current -> endpoint must return 404 (not the archived version).
        pt1 = self.created["preview_token_v1"]
        r = requests.get(f"{API}/verify/preview", params={"t": pt1}, timeout=15)
        assert r.status_code == 404, f"archived cert leaked via preview: {r.status_code}"


# --------- CLEANUP ----------------------------------------------------
class TestZZZCleanupAndCounterRestore:
    def test_cleanup(self, mongo_db):
        c = TestPreviewE2E.created
        # collect all cert_uuids we know
        cert_uuids = [x for x in [c.get("cert_uuid"), c.get("cert_uuid_v2")] if x]
        cert_numbers = [x for x in [c.get("cert_number"), c.get("cert_number_v2")] if x]

        # Verification tokens on both versions
        for cu in cert_uuids:
            doc = mongo_db.certificates.find_one({"uuid": cu})
            if doc:
                vt_uuid = doc.get("verification_uuid")
                if vt_uuid:
                    mongo_db.verification_tokens.delete_many({"uuid": vt_uuid})
                snap = doc.get("gemstone_snapshot") or {}
                pid = snap.get("photo_id")
                if pid:
                    mongo_db.gemstone_photos.delete_many({"uuid": pid})

        # nuke by number (covers archived+current versions)
        for num in cert_numbers:
            mongo_db.certificates.delete_many({"certificate_number": num})
        for cu in cert_uuids:
            mongo_db.certificates.delete_many({"uuid": cu})

        # cleanup gemstone(s)
        gem = c.get("gemstone_uuid")
        if gem:
            g = mongo_db.gemstones.find_one({"uuid": gem})
            if g:
                for mid in (g.get("media_ids") or []):
                    mongo_db.gemstone_photos.delete_many({"uuid": mid})
            mongo_db.gemstones.delete_many({"uuid": gem})

        # sweep leftover TEST_
        mongo_db.gemstones.delete_many({"name_en": {"$regex": "^TEST_"}})

        # restore counter
        mongo_db.counters.update_one(
            {"name": "certificate", "year": COUNTER_YEAR},
            {"$set": {"last_number": RESTORE_COUNTER_TO}},
            upsert=True,
        )

        cd = mongo_db.counters.find_one({"name": "certificate", "year": COUNTER_YEAR})
        assert cd and cd.get("last_number") == RESTORE_COUNTER_TO, cd

        certs = mongo_db.certificates.count_documents({})
        gems = mongo_db.gemstones.count_documents({})
        assert certs == 0, f"certificates not empty: {certs}"
        assert gems == 0, f"gemstones not empty: {gems}"

        print(
            f"\nFINAL_COUNTER_LAST_NUMBER={cd.get('last_number')} "
            f"certificates={certs} gemstones={gems} "
            f"next_number_will_be=AZR-GEM-{(cd.get('last_number') + 1):06d}-{COUNTER_YEAR % 100:02d}"
        )
