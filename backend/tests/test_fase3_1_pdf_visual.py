"""FASE 3.1 — Visual refinement of A6 landscape booklet certificate PDF.

Scope of this iteration:
  * Regression (READ-ONLY, MUST NOT consume the atomic certificate counter):
      - POST /api/verify with fake number returns generic not_found.
      - GET /api/verify/qr/resolve with invalid token returns token_valid=false.
      - GET /api/settings/public returns whatsapp_number+enabled.
      - GET /api/legality returns unpublished/empty state.
  * PDF E2E: create one TEST_ gemstone -> issue certificate -> fetch PDF and
    validate 200/application-pdf, exactly 2 pages, each mediabox is A6-landscape
    (148 x 105 mm) within +/-1pt tolerance, and page-2 QR decodes to a URL of
    the form '<base>/?qr=<token>#verification' containing the returned qr_token.
  * Public verification of the newly-issued cert returns 'valid', QR verify
    returns valid details, and security_code/qr_token never leak publicly.
  * MANDATORY CLEANUP: delete created certificate, gemstone, verification_token,
    photo (if any) and restore counters.certificate:{year=2026}.last_number
    back to 14 so the next real cert becomes AZR-GEM-2026-000015.

All artefacts are created & then removed within this single test module.

Run:  pytest backend/tests/test_fase3_1_pdf_visual.py -v -o "addopts=" -s
NOTE: run WITHOUT pytest-xdist parallelism (`-o addopts=`) — cleanup must run
LAST after PDF E2E tests, otherwise workers race and cleanup asserts fail.
"""

from __future__ import annotations

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

ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PASSWORD = "AzurisDev@2026!"

RESTORE_COUNTER_TO = 14
COUNTER_YEAR = 2026


# --------------------------------------------------------------- fixtures
@pytest.fixture(scope="module")
def admin_headers():
    r = requests.post(
        f"{API}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    tok = r.json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


@pytest.fixture(scope="module")
def mongo_db():
    from pymongo import MongoClient
    cli = MongoClient(MONGO_URL)
    db = cli[DB_NAME]
    yield db
    cli.close()


# ============================================================ REGRESSIONS
class TestReadOnlyRegressions:
    """Must NOT consume the atomic certificate counter."""

    def test_verify_fake_number_returns_not_found(self):
        r = requests.post(
            f"{API}/verify",
            json={"certificate_number": "AZR-GEM-2026-999999", "security_code": "ABCD1234"},
            timeout=10,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        # accept either 'status' or 'result' key naming
        outcome = data.get("status") or data.get("result")
        assert outcome == "not_found", data
        assert not data.get("certificate")
        assert "security_code" not in str(data)

    def test_qr_resolve_invalid_token(self):
        r = requests.get(f"{API}/verify/qr/resolve", params={"token": "INVALIDTOKEN"}, timeout=10)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("token_valid") is False
        # no details on invalid
        assert not data.get("certificate_number")
        assert "security_code" not in str(data)

    def test_settings_public_whatsapp(self):
        r = requests.get(f"{API}/settings/public", timeout=10)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("whatsapp_number") == "6287812128884", data
        assert data.get("whatsapp_enabled") is True, data

    def test_legality_unpublished_state(self):
        r = requests.get(f"{API}/legality", timeout=10)
        assert r.status_code == 200, r.text
        data = r.json()
        # accept empty list, empty dict, or object with published=false / items=[]
        if isinstance(data, list):
            assert len(data) == 0
        elif isinstance(data, dict):
            items = data.get("items")
            if items is not None:
                assert items == [] or all(not it.get("is_published", False) for it in items)
            else:
                # single-document shape
                assert not data.get("is_published", False) or not data.get("uuid")


# ============================================================ PDF E2E
class TestPdfE2E:
    """Creates ONE test gemstone + certificate, validates PDF, then CLEANS UP."""

    created = {"gemstone_uuid": None, "cert_uuid": None, "cert_number": None,
               "security_code": None, "qr_token": None, "verification_uuid": None,
               "photo_id": None}

    def test_01_create_gemstone(self, admin_headers):
        payload = {
            "name_id": "TEST_FASE31_Safir Biru",
            "name_en": "TEST_FASE31_Blue Sapphire",
            "category": "Blue Sapphire",   # variety
            "gemstone_type": "Corundum",   # species
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
        g = r.json()
        assert g["name_en"] == payload["name_en"]
        self.__class__.created["gemstone_uuid"] = g["uuid"]

    def test_02_issue_certificate(self, admin_headers):
        gid = self.created["gemstone_uuid"]
        assert gid, "gemstone missing"
        body = {
            "gemstone_id": gid,
            "object_type": "Loose Stone",
            "transparency": "Transparent",
            "examiner": "TEST Gemologist",
            "signatory": "TEST Signatory",
            "conclusion": "Natural Blue Sapphire, heated.",
        }
        r = requests.post(f"{API}/admin/certificates/issue", json=body, headers=admin_headers, timeout=20)
        assert r.status_code == 201, r.text
        d = r.json()
        assert d["certificate_number"].startswith("AZR-GEM-2026-"), d
        assert d.get("security_code") and d.get("qr_token"), d
        self.__class__.created.update({
            "cert_uuid": d["certificate_uuid"],
            "cert_number": d["certificate_number"],
            "security_code": d["security_code"],
            "qr_token": d["qr_token"],
        })

    def test_03_pdf_binary_and_mediabox(self, admin_headers):
        cu = self.created["cert_uuid"]
        assert cu
        r = requests.get(f"{API}/admin/certificates/{cu}/pdf", headers=admin_headers, timeout=30)
        assert r.status_code == 200, r.text[:300]
        assert r.headers.get("content-type", "").startswith("application/pdf"), r.headers
        pdf_bytes = r.content
        assert pdf_bytes[:4] == b"%PDF", "not a PDF"

        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) == 2, f"expected 2 pages, got {len(reader.pages)}"

        # A6 landscape 148x105mm = 419.527559 x 297.637795 pt
        exp_w, exp_h = 419.527559, 297.637795
        tol = 1.0
        for i, page in enumerate(reader.pages):
            mb = page.mediabox
            w = float(mb.width)
            h = float(mb.height)
            assert abs(w - exp_w) <= tol, f"page {i+1} width {w} not within {tol}pt of {exp_w}"
            assert abs(h - exp_h) <= tol, f"page {i+1} height {h} not within {tol}pt of {exp_h}"

        # stash for QR test
        self.__class__.created["_pdf_bytes"] = pdf_bytes

    def test_04_qr_on_page2_decodes_to_expected_url(self):
        pdf_bytes = self.created.get("_pdf_bytes")
        assert pdf_bytes, "pdf missing"
        from pdf2image import convert_from_bytes
        from pyzbar.pyzbar import decode as zbar_decode

        images = convert_from_bytes(pdf_bytes, dpi=300)
        assert len(images) == 2
        page2 = images[1]

        results = zbar_decode(page2)
        # If QR is small, retry at higher dpi
        if not results:
            images = convert_from_bytes(pdf_bytes, dpi=450)
            page2 = images[1]
            results = zbar_decode(page2)
        assert results, "no QR decoded on page 2"

        payload = results[0].data.decode("utf-8", errors="replace")
        token = self.created["qr_token"]
        # form: <base>/?qr=<token>#verification
        m = re.match(r"^https?://[^/]+/\?qr=([A-Za-z0-9_\-]+)#verification$", payload)
        assert m, f"QR payload not in expected form: {payload!r}"
        assert m.group(1) == token, f"QR token mismatch: got {m.group(1)!r}, want {token!r}"

    def test_05_manual_verify_returns_valid(self):
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
        outcome = d.get("status") or d.get("result")
        assert outcome == "valid", d
        # public response must never leak security_code or qr_token
        blob = str(d)
        assert self.created["security_code"] not in blob, "security_code leaked in /verify!"
        assert self.created["qr_token"] not in blob, "qr_token leaked in /verify!"

    def test_06_qr_verify_returns_valid_and_no_secret_leak(self):
        r = requests.post(f"{API}/verify/qr", json={"token": self.created["qr_token"]}, timeout=10)
        assert r.status_code == 200, r.text
        d = r.json()
        outcome = d.get("status") or d.get("result")
        assert outcome == "valid" or d.get("certificate"), d
        blob = str(d)
        assert self.created["security_code"] not in blob, "security_code leaked in /verify/qr!"
        assert self.created["qr_token"] not in blob, "qr_token leaked in /verify/qr!"


# ============================================================ CLEANUP + COUNTER RESTORE
class TestZZZCleanupAndCounterRestore:
    """Runs LAST (alphabetically). Removes artefacts and restores counter to 14."""

    def test_cleanup_and_verify_state(self, mongo_db):
        created = TestPdfE2E.created
        cert_uuid = created.get("cert_uuid")
        gem_uuid = created.get("gemstone_uuid")

        # Look up + delete verification token
        if cert_uuid:
            cert_doc = mongo_db.certificates.find_one({"uuid": cert_uuid})
            if cert_doc:
                vt_uuid = cert_doc.get("verification_uuid")
                if vt_uuid:
                    mongo_db.verification_tokens.delete_many({"uuid": vt_uuid})
                snap = cert_doc.get("gemstone_snapshot") or {}
                pid = snap.get("photo_id")
                if pid:
                    mongo_db.gemstone_photos.delete_many({"uuid": pid})
            # delete ALL versions with this cert number just in case
            if cert_doc:
                mongo_db.certificates.delete_many({"certificate_number": cert_doc.get("certificate_number")})
            mongo_db.certificates.delete_many({"uuid": cert_uuid})

        if gem_uuid:
            # remove any lingering photos referenced by the gemstone
            gem_doc = mongo_db.gemstones.find_one({"uuid": gem_uuid})
            if gem_doc:
                for mid in (gem_doc.get("media_ids") or []):
                    mongo_db.gemstone_photos.delete_many({"uuid": mid})
            mongo_db.gemstones.delete_many({"uuid": gem_uuid})

        # Restore counter deterministically
        mongo_db.counters.update_one(
            {"name": "certificate", "year": COUNTER_YEAR},
            {"$set": {"last_number": RESTORE_COUNTER_TO}},
            upsert=True,
        )

        # sweep any leftover TEST_ gemstones from earlier iterations (best-effort)
        mongo_db.gemstones.delete_many({"name_en": {"$regex": "^TEST_"}})

        # Final assertions on state
        counter_doc = mongo_db.counters.find_one({"name": "certificate", "year": COUNTER_YEAR})
        assert counter_doc is not None, "counter doc missing"
        assert counter_doc.get("last_number") == RESTORE_COUNTER_TO, counter_doc

        certs_remaining = mongo_db.certificates.count_documents({})
        gems_remaining = mongo_db.gemstones.count_documents({})
        assert certs_remaining == 0, f"certificates not empty: {certs_remaining}"
        assert gems_remaining == 0, f"gemstones not empty: {gems_remaining}"

        # emit for reporter
        print(
            f"\nFINAL_COUNTER_LAST_NUMBER={counter_doc.get('last_number')} "
            f"certificates={certs_remaining} gemstones={gems_remaining} "
            f"next_number_will_be=AZR-GEM-{COUNTER_YEAR}-{(counter_doc.get('last_number') + 1):06d}"
        )
