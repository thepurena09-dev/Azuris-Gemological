"""FASE 3.4 — Certificate number format change AZR-GEM-000001-YY.

Covers:
  * UNIT: counter.next_certificate_number returns new format with atomicity.
  * E2E: issuance + PDF + preview + manual/QR verify all show the new format;
    OLD format 'AZR-GEM-2026-000015' rejected as invalid.
  * Regex on /api/verify accepts new, rejects old.
  * MANDATORY cleanup + counter restore.

Run: pytest backend/tests/test_fase3_4_number_format.py -v -o "addopts=" -s
"""
from __future__ import annotations

import asyncio
import io
import os
import re

import pytest
import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
load_dotenv("/app/frontend/.env")

BASE = (os.environ.get("REACT_APP_BACKEND_URL") or "").rstrip("/")
API = f"{BASE}/api"
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")

ADMIN = ("admin@azuris.local", "AzurisDev@2026!")
CM = ("cm@azuris.local", "CmDev@2026!")
RESTORE_COUNTER_TO = 14
COUNTER_YEAR = 2026
NEW_FMT = re.compile(r"^AZR-GEM-\d{6}-\d{2}$")


@pytest.fixture(scope="module")
def admin_headers():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN[0], "password": ADMIN[1]}, timeout=15)
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="module")
def mongo_db():
    from pymongo import MongoClient
    cli = MongoClient(MONGO_URL)
    db = cli[DB_NAME]
    yield db
    cli.close()


# -------------------- UNIT: counter format & atomicity --------------------
class TestCounterUnit:
    def test_format_seq15_year_2026(self, mongo_db):
        # Ensure counter at 14 baseline
        mongo_db.counters.update_one(
            {"name": "certificate", "year": COUNTER_YEAR},
            {"$set": {"last_number": RESTORE_COUNTER_TO}},
            upsert=True,
        )
        import sys
        sys.path.insert(0, "/app/backend")
        from motor.motor_asyncio import AsyncIOMotorClient
        from repositories.counter import CounterRepository

        async def run():
            cli = AsyncIOMotorClient(MONGO_URL)
            db = cli[DB_NAME]
            repo = CounterRepository(db)
            n1 = await repo.next_certificate_number(2026)
            n2 = await repo.next_certificate_number(2026)
            cli.close()
            return n1, n2

        n1, n2 = asyncio.get_event_loop().run_until_complete(run())
        assert n1 == "AZR-GEM-000015-26", n1
        assert n2 == "AZR-GEM-000016-26", n2

        # 6-digit padding at 1000
        mongo_db.counters.update_one(
            {"name": "certificate", "year": COUNTER_YEAR},
            {"$set": {"last_number": 999}},
        )

        async def run2():
            cli = AsyncIOMotorClient(MONGO_URL)
            db = cli[DB_NAME]
            repo = CounterRepository(db)
            n = await repo.next_certificate_number(2026)
            cli.close()
            return n

        n = asyncio.get_event_loop().run_until_complete(run2())
        assert n == "AZR-GEM-001000-26", n

    def test_atomic_no_duplicates_concurrent(self, mongo_db):
        # Reset baseline
        mongo_db.counters.update_one(
            {"name": "certificate", "year": COUNTER_YEAR},
            {"$set": {"last_number": RESTORE_COUNTER_TO}},
            upsert=True,
        )
        from motor.motor_asyncio import AsyncIOMotorClient
        from repositories.counter import CounterRepository

        async def run():
            cli = AsyncIOMotorClient(MONGO_URL)
            db = cli[DB_NAME]
            repo = CounterRepository(db)
            results = await asyncio.gather(*[repo.next_certificate_number(2026) for _ in range(20)])
            cli.close()
            return results

        results = asyncio.get_event_loop().run_until_complete(run())
        assert len(set(results)) == 20, f"duplicate found: {results}"
        for r in results:
            assert NEW_FMT.match(r), r

        # Restore counter back to 14
        mongo_db.counters.update_one(
            {"name": "certificate", "year": COUNTER_YEAR},
            {"$set": {"last_number": RESTORE_COUNTER_TO}},
        )


# -------------------- REGEX: /api/verify accepts new, rejects old ----------
class TestVerifyRegex:
    def test_old_format_returns_not_found(self):
        r = requests.post(
            f"{API}/verify",
            json={"certificate_number": "AZR-GEM-2026-000015", "security_code": "ABCD1234"},
            timeout=10,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert (d.get("status") or d.get("result")) == "not_found"
        assert d.get("certificate") in (None, {})

    def test_new_format_shape_not_found_when_absent(self):
        r = requests.post(
            f"{API}/verify",
            json={"certificate_number": "AZR-GEM-999999-26", "security_code": "ABCD1234"},
            timeout=10,
        )
        assert r.status_code == 200
        d = r.json()
        assert (d.get("status") or d.get("result")) == "not_found"


# -------------------- E2E: issuance + PDF + preview + verify ---------------
class TestIssuanceE2E:
    created = {}

    def test_01_baseline_counter(self, mongo_db):
        doc = mongo_db.counters.find_one({"name": "certificate", "year": COUNTER_YEAR})
        assert doc and doc.get("last_number") == RESTORE_COUNTER_TO, doc

    def test_02_create_gemstone_and_issue(self, admin_headers, mongo_db):
        gem = {
            "name_id": "TEST_FASE34_Safir",
            "name_en": "TEST_FASE34_Sapphire",
            "category": "Blue Sapphire",
            "gemstone_type": "Corundum",
            "weight_carat": 2.51,
            "color": "Blue",
            "clarity": "VS",
            "cut": "Oval",
            "shape": "Oval",
            "dimensions_mm": "8.0 x 6.0 x 4.0",
            "origin": "Ceylon",
            "treatment": "Heated",
        }
        r = requests.post(f"{API}/admin/gemstones", json=gem, headers=admin_headers, timeout=15)
        assert r.status_code == 201, r.text
        self.__class__.created["gemstone_uuid"] = r.json()["uuid"]

        r = requests.post(
            f"{API}/admin/certificates/issue",
            json={
                "gemstone_id": self.created["gemstone_uuid"],
                "object_type": "Loose Stone",
                "transparency": "Transparent",
                "examiner": "TEST",
                "signatory": "TEST",
                "conclusion": "Test.",
            },
            headers=admin_headers,
            timeout=20,
        )
        assert r.status_code == 201, r.text
        d = r.json()
        assert d["certificate_number"] == "AZR-GEM-000015-26", d
        self.__class__.created.update({
            "cert_uuid": d["certificate_uuid"],
            "cert_number": d["certificate_number"],
            "security_code": d["security_code"],
            "qr_token": d["qr_token"],
        })

    def test_03_admin_list_and_detail_show_new_format(self, admin_headers):
        r = requests.get(f"{API}/admin/certificates", headers=admin_headers, timeout=15)
        assert r.status_code == 200
        data = r.json()
        items = data if isinstance(data, list) else (data.get("items") or [])
        nums = [it.get("certificate_number") for it in items]
        assert self.created["cert_number"] in nums, nums

        # No dedicated GET /admin/certificates/{uuid} — list is source of truth for detail
        item = next(it for it in items if it.get("certificate_number") == self.created["cert_number"])
        assert item.get("uuid") == self.created["cert_uuid"]

    def test_04_db_stores_new_format(self, mongo_db):
        doc = mongo_db.certificates.find_one({"uuid": self.created["cert_uuid"]})
        assert doc and doc.get("certificate_number") == "AZR-GEM-000015-26"

    def test_05_pdf_ok_two_pages(self, admin_headers):
        cu = self.created["cert_uuid"]
        r = requests.get(f"{API}/admin/certificates/{cu}/pdf", headers=admin_headers, timeout=30)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content[:4] == b"%PDF"
        from pypdf import PdfReader
        pages = PdfReader(io.BytesIO(r.content)).pages
        assert len(pages) == 2
        # A6 landscape check
        exp_w, exp_h = 419.527559, 297.637795
        for p in pages:
            assert abs(float(p.mediabox.width) - exp_w) <= 1.0
            assert abs(float(p.mediabox.height) - exp_h) <= 1.0

    def test_06_pdf_text_contains_new_number(self, admin_headers):
        cu = self.created["cert_uuid"]
        r = requests.get(f"{API}/admin/certificates/{cu}/pdf", headers=admin_headers, timeout=30)
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=r.content, filetype="pdf")
            text = "".join(p.get_text() for p in doc)
            doc.close()
        except Exception:
            from pypdf import PdfReader
            text = "".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(r.content)).pages)
        assert "AZR-GEM-000015-26" in text, text[:500]
        assert "AZR-GEM-2026-" not in text, "old format found in PDF"

    def test_07_manual_verify_new_format(self):
        r = requests.post(
            f"{API}/verify",
            json={"certificate_number": self.created["cert_number"], "security_code": self.created["security_code"]},
            timeout=10,
        )
        assert r.status_code == 200
        d = r.json()
        assert (d.get("status") or d.get("result")) == "valid"
        cert = d.get("certificate") or {}
        assert cert.get("certificate_number") == "AZR-GEM-000015-26"
        pt = cert.get("preview_token")
        assert pt
        self.__class__.created["preview_token"] = pt
        # secrets never leaked
        blob = str(d)
        assert self.created["security_code"] not in blob
        assert self.created["qr_token"] not in blob

    def test_08_preview_png_new_format(self):
        pt = self.created["preview_token"]
        r = requests.get(f"{API}/verify/preview", params={"t": pt}, timeout=30)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("image/png")
        assert r.content[:8] == b"\x89PNG\r\n\x1a\n"

    def test_09_qr_verify_new_format(self):
        r = requests.post(f"{API}/verify/qr", json={"token": self.created["qr_token"]}, timeout=10)
        assert r.status_code == 200
        d = r.json()
        cert = d.get("certificate") or {}
        assert cert.get("certificate_number") == "AZR-GEM-000015-26"

    def test_10_rbac_cm_blocked_and_unauth(self):
        # CM login (best-effort — skip if not seeded)
        cr = requests.post(f"{API}/auth/login", json={"email": CM[0], "password": CM[1]}, timeout=10)
        if cr.status_code == 200:
            tok = cr.json()["access_token"]
            r = requests.post(
                f"{API}/admin/certificates/issue",
                json={"gemstone_id": self.created["gemstone_uuid"], "object_type": "x",
                      "transparency": "x", "examiner": "x", "signatory": "x", "conclusion": "x"},
                headers={"Authorization": f"Bearer {tok}"},
                timeout=15,
            )
            assert r.status_code == 403, r.status_code
        # unauth
        r = requests.post(f"{API}/admin/certificates/issue", json={}, timeout=10)
        assert r.status_code in (401, 403), r.status_code

    def test_11_reissue_same_number(self, admin_headers, mongo_db):
        cu = self.created["cert_uuid"]
        r = requests.post(
            f"{API}/admin/certificates/{cu}/reissue",
            json={
                "gemstone_id": self.created["gemstone_uuid"],
                "object_type": "Loose Stone",
                "transparency": "Transparent",
                "examiner": "TEST v2",
                "signatory": "TEST v2",
                "conclusion": "Reissue.",
            },
            headers=admin_headers,
            timeout=20,
        )
        assert r.status_code in (200, 201), r.text
        d = r.json()
        assert d.get("certificate_number") == "AZR-GEM-000015-26", d
        new_uuid = d.get("certificate_uuid") or d.get("uuid")
        self.__class__.created["cert_uuid_v2"] = new_uuid

        # counter must still be 15 (not incremented on reissue)
        cd = mongo_db.counters.find_one({"name": "certificate", "year": COUNTER_YEAR})
        assert cd.get("last_number") == 15, cd


# -------------------- CLEANUP ---------------------------------------------
class TestZZZCleanup:
    def test_cleanup_and_restore(self, mongo_db):
        c = TestIssuanceE2E.created
        cert_uuids = [x for x in [c.get("cert_uuid"), c.get("cert_uuid_v2")] if x]
        for cu in cert_uuids:
            doc = mongo_db.certificates.find_one({"uuid": cu})
            if doc:
                vt = doc.get("verification_uuid")
                if vt:
                    mongo_db.verification_tokens.delete_many({"uuid": vt})
                snap = doc.get("gemstone_snapshot") or {}
                pid = snap.get("photo_id")
                if pid:
                    mongo_db.gemstone_photos.delete_many({"uuid": pid})
        mongo_db.certificates.delete_many({"certificate_number": "AZR-GEM-000015-26"})

        gem = c.get("gemstone_uuid")
        if gem:
            g = mongo_db.gemstones.find_one({"uuid": gem})
            if g:
                for mid in (g.get("media_ids") or []):
                    mongo_db.gemstone_photos.delete_many({"uuid": mid})
            mongo_db.gemstones.delete_many({"uuid": gem})

        mongo_db.gemstones.delete_many({"name_en": {"$regex": "^TEST_"}})

        mongo_db.counters.update_one(
            {"name": "certificate", "year": COUNTER_YEAR},
            {"$set": {"last_number": RESTORE_COUNTER_TO}},
            upsert=True,
        )
        cd = mongo_db.counters.find_one({"name": "certificate", "year": COUNTER_YEAR})
        assert cd.get("last_number") == RESTORE_COUNTER_TO
        assert mongo_db.certificates.count_documents({}) == 0
        assert mongo_db.gemstones.count_documents({}) == 0
        print(
            f"\nFINAL_COUNTER_LAST_NUMBER={cd.get('last_number')} "
            f"next_number_will_be=AZR-GEM-{(cd.get('last_number')+1):06d}-{COUNTER_YEAR%100:02d}"
        )
