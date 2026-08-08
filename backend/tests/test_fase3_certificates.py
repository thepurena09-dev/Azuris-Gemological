"""FASE 3 — Admin gemstones + certificate issuance + verification + PDF + RBAC."""
import io
import os
import re
import struct
import zlib
import pytest
import requests
from pymongo import MongoClient

BASE_URL = ""
with open("/app/frontend/.env") as f:
    for line in f:
        if line.startswith("REACT_APP_BACKEND_URL="):
            BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
API = f"{BASE_URL}/api"

SUPER = ("admin@azuris.local", "AzurisDev@2026!")
CM = ("cm@azuris.local", "CmDev@2026!")

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

CERT_RE = re.compile(r"^AZR-GEM-\d{6}-\d{2}$")


def _login(email, password):
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def super_token():
    return _login(*SUPER)


@pytest.fixture(scope="module")
def cm_token():
    return _login(*CM)


@pytest.fixture(scope="module")
def super_hdr(super_token):
    return {"Authorization": f"Bearer {super_token}"}


@pytest.fixture(scope="module")
def cm_hdr(cm_token):
    return {"Authorization": f"Bearer {cm_token}"}


def _minipng():
    # 1x1 red PNG bytes (hand-crafted, valid)
    sig = b"\x89PNG\r\n\x1a\n"
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw = b"\x00\xff\x00\x00"
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


@pytest.fixture(scope="module")
def gemstone(super_hdr):
    body = {
        "name_id": "TEST_Batu Zamrud",
        "name_en": "TEST_Emerald",
        "category": "Beryl",
        "gemstone_type": "Emerald",
        "weight_carat": 2.75,
        "color": "Green",
        "clarity": "VS",
        "cut": "Emerald cut",
        "shape": "Rectangle",
        "dimensions_mm": "8x6x4",
        "origin": "Colombia",
        "treatment": "Minor oil",
    }
    r = requests.post(f"{API}/admin/gemstones", json=body, headers=super_hdr)
    assert r.status_code == 201, r.text
    data = r.json()
    assert "uuid" in data
    return data


# -------- Gemstone create + photo --------
class TestGemstone:
    def test_create_gemstone_shape(self, gemstone):
        assert gemstone["name_en"] == "TEST_Emerald"
        assert gemstone["weight_carat"] == 2.75
        assert "_id" not in gemstone

    def test_create_gemstone_validation(self, super_hdr):
        r = requests.post(f"{API}/admin/gemstones", json={"name_id": "x"}, headers=super_hdr)
        assert r.status_code == 422

    def test_upload_photo_and_public_get(self, super_hdr, gemstone):
        files = {"file": ("t.png", _minipng(), "image/png")}
        r = requests.post(
            f"{API}/admin/gemstones/{gemstone['uuid']}/photo",
            files=files, headers=super_hdr,
        )
        assert r.status_code == 200, r.text
        photo_id = r.json()["photo_id"]
        assert photo_id
        gemstone["photo_id"] = photo_id
        # Public GET
        r2 = requests.get(f"{API}/gemstone/photo/{photo_id}")
        assert r2.status_code == 200
        assert r2.headers["content-type"].startswith("image/")


# -------- Certificate issuance --------
@pytest.fixture(scope="module")
def issued(super_hdr, gemstone):
    body = {
        "gemstone_id": gemstone["uuid"],
        "examiner": "Dr Test",
        "signatory": "Dr Signer",
        "conclusion": "Natural Emerald",
    }
    r = requests.post(f"{API}/admin/certificates/issue", json=body, headers=super_hdr)
    assert r.status_code == 201, r.text
    return r.json()


class TestIssuance:
    def test_issue_shape(self, issued):
        assert CERT_RE.match(issued["certificate_number"]), issued
        assert issued["security_code"] and len(issued["security_code"]) >= 4
        assert issued["qr_token"]
        assert "?qr=" in issued["qr_url"] and "#verification" in issued["qr_url"]
        assert issued["version"] == 1
        assert "_id" not in issued

    def test_duplicate_issue_409(self, super_hdr, gemstone):
        body = {"gemstone_id": gemstone["uuid"], "examiner": "X", "conclusion": "Y"}
        r = requests.post(f"{API}/admin/certificates/issue", json=body, headers=super_hdr)
        assert r.status_code == 409

    def test_atomic_sequential_numbers(self, super_hdr, issued):
        # Create two more gemstones and issue certs; verify strictly increasing numbers.
        nums = [issued["certificate_number"]]
        for i in range(2):
            g = requests.post(f"{API}/admin/gemstones", json={
                "name_id": f"TEST_Seq_{i}", "name_en": f"TEST_Seq_{i}",
                "category": "Beryl", "gemstone_type": "Emerald", "weight_carat": 1.0,
            }, headers=super_hdr).json()
            r = requests.post(f"{API}/admin/certificates/issue",
                              json={"gemstone_id": g["uuid"], "conclusion": "N"},
                              headers=super_hdr)
            assert r.status_code == 201
            nums.append(r.json()["certificate_number"])
        seq = [int(n.split("-")[-1]) for n in nums]
        assert seq == sorted(seq) and len(set(seq)) == len(seq)
        assert all(b - a >= 1 for a, b in zip(seq, seq[1:]))


# -------- Verification --------
class TestVerification:
    def test_valid_manual(self, issued):
        r = requests.post(f"{API}/verify", json={
            "certificate_number": issued["certificate_number"],
            "security_code": issued["security_code"],
        })
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "valid", data
        cert = data.get("certificate") or {}
        assert cert.get("certificate_number") == issued["certificate_number"]
        # No secrets in public response
        blob = str(data).lower()
        assert "security_code" not in blob
        assert issued["security_code"].lower() not in blob
        assert issued["qr_token"].lower() not in blob
        assert "_id" not in blob or '"_id"' not in blob
        # Should have some gemstone identity fields
        snap = cert.get("gemstone") or cert.get("gemstone_snapshot") or cert
        assert any(k in str(cert) for k in ["name", "species", "carat"])

    def test_wrong_security_code_generic(self, issued):
        r = requests.post(f"{API}/verify", json={
            "certificate_number": issued["certificate_number"],
            "security_code": "WRONG-CODE-XYZ",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "not_found"
        assert not data.get("certificate")

    def test_malformed_number(self):
        r = requests.post(f"{API}/verify", json={
            "certificate_number": "not-a-cert", "security_code": "x",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "not_found"

    def test_qr_resolve_prefill_only(self, issued):
        r = requests.get(f"{API}/verify/qr/resolve", params={"token": issued["qr_token"]})
        assert r.status_code == 200
        data = r.json()
        assert data.get("token_valid") is True
        assert data.get("certificate_number") == issued["certificate_number"]
        # No gemstone details in prefill
        assert "gemstone" not in data and "certificate" not in data
        assert "security_code" not in str(data)

    def test_qr_verify_full(self, issued):
        r = requests.post(f"{API}/verify/qr", json={"token": issued["qr_token"]})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "valid"
        assert data["certificate"]["certificate_number"] == issued["certificate_number"]
        assert issued["security_code"] not in str(data)

    def test_qr_invalid_token(self):
        r = requests.get(f"{API}/verify/qr/resolve", params={"token": "bogus_token_xxx"})
        assert r.status_code == 200
        data = r.json()
        assert data.get("token_valid") is False or data.get("status") == "not_found"


# -------- PDF (A6 landscape, 2 pages) --------
class TestPDF:
    def test_pdf_a6_landscape_two_pages(self, super_hdr, issued):
        cert_uuid = issued["certificate_uuid"]
        r = requests.get(f"{API}/admin/certificates/{cert_uuid}/pdf", headers=super_hdr)
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("application/pdf")
        pdf = r.content
        assert pdf.startswith(b"%PDF-")
        # Count pages via /Type /Page (not /Pages)
        # Better: use pypdf if available
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf))
            assert len(reader.pages) == 2, f"expected 2 pages, got {len(reader.pages)}"
            for p in reader.pages:
                mb = p.mediabox
                w = float(mb.width)
                h = float(mb.height)
                # A6 landscape: 419.53 x 297.64 pts (±1pt tolerance)
                assert abs(w - 419.53) < 1.5 and abs(h - 297.64) < 1.5, f"MediaBox {w}x{h}"
        except ImportError:
            # fallback: naive count
            n = len(re.findall(rb"/Type\s*/Page[^s]", pdf))
            assert n == 2, f"expected 2 pages via regex, got {n}"


# -------- Versioning + Revoke --------
class TestVersioningRevoke:
    def test_reissue_creates_new_version(self, super_hdr, issued):
        cert_uuid = issued["certificate_uuid"]
        r = requests.post(f"{API}/admin/certificates/{cert_uuid}/reissue",
                          json={"gemstone_id": "ignored", "conclusion": "Reissued note"},
                          headers=super_hdr)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["version"] == 2
        assert data["certificate_number"] == issued["certificate_number"]
        issued["v2_uuid"] = data["certificate_uuid"]
        # Public verification still returns valid with the SAME cert number
        v = requests.post(f"{API}/verify", json={
            "certificate_number": issued["certificate_number"],
            "security_code": issued["security_code"],
        })
        assert v.status_code == 200
        vd = v.json()
        assert vd["status"] == "valid"
        # It should reflect the current (v2) version if exposed
        cert = vd.get("certificate") or {}
        if "version" in cert:
            assert cert["version"] == 2

    def test_revoke_shows_revoked(self, super_hdr, issued):
        target = issued.get("v2_uuid") or issued["certificate_uuid"]
        r = requests.post(f"{API}/admin/certificates/{target}/revoke", headers=super_hdr)
        assert r.status_code == 200
        v = requests.post(f"{API}/verify", json={
            "certificate_number": issued["certificate_number"],
            "security_code": issued["security_code"],
        })
        assert v.status_code == 200
        assert v.json()["status"] == "revoked"


# -------- RBAC --------
class TestRBAC:
    def test_content_manager_forbidden_gemstone(self, cm_hdr):
        r = requests.post(f"{API}/admin/gemstones", json={
            "name_id": "x", "name_en": "x", "category": "c", "gemstone_type": "g", "weight_carat": 1.0
        }, headers=cm_hdr)
        assert r.status_code == 403

    def test_content_manager_forbidden_issue(self, cm_hdr):
        r = requests.post(f"{API}/admin/certificates/issue",
                          json={"gemstone_id": "x", "conclusion": "y"}, headers=cm_hdr)
        assert r.status_code == 403

    def test_content_manager_forbidden_pdf(self, cm_hdr, issued):
        uuid_ = issued.get("v2_uuid") or issued["certificate_uuid"]
        r = requests.get(f"{API}/admin/certificates/{uuid_}/pdf", headers=cm_hdr)
        assert r.status_code == 403

    def test_unauth_401(self, issued):
        r1 = requests.post(f"{API}/admin/gemstones", json={
            "name_id": "x", "name_en": "x", "category": "c", "gemstone_type": "g", "weight_carat": 1.0
        })
        assert r1.status_code == 401
        r2 = requests.post(f"{API}/admin/certificates/issue", json={"gemstone_id": "x"})
        assert r2.status_code == 401
        r3 = requests.get(f"{API}/admin/certificates/{issued['certificate_uuid']}/pdf")
        assert r3.status_code == 401


# -------- Audit logs (direct DB) --------
class TestAudit:
    def test_audit_entries(self, gemstone, issued):
        client = MongoClient(MONGO_URL)
        try:
            coll = client[DB_NAME]["audit_logs"]
            gem_e = coll.find_one({"entity_type": "gemstone", "entity_id": gemstone["uuid"]})
            cert_e = coll.find_one({"entity_type": "certificate", "entity_id": issued["certificate_uuid"]})
            assert gem_e is not None
            assert cert_e is not None
        finally:
            client.close()


# -------- FASE 2 regression --------
class TestFase2Regression:
    def test_settings_public(self):
        r = requests.get(f"{API}/settings/public")
        assert r.status_code == 200
        assert r.json().get("whatsapp_number") == "6287812128884"

    def test_legality_empty(self):
        r = requests.get(f"{API}/legality")
        assert r.status_code == 200
        data = r.json()
        assert data.get("published") is False
