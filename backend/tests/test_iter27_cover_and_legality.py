"""Iteration 27 — cover-first verify + admin legality signatory/signature +
demo PDF previews (no DB records)."""
import io
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/") or "http://localhost:8001"
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PASSWORD = "AzurisDev@2026!"

SEED_CERT = "AGR-TST-000001-26"
NONEXIST_CERT = "AGR-ZMD-000099-26"
BAD_FORMAT = "abc"


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, r.text
    return r.json()["data"]["access_token"]


@pytest.fixture(scope="module")
def auth(token):
    return {"Authorization": f"Bearer {token}"}


# --- Public verify cover/pdf ---
class TestPublicVerify:
    def test_cover_valid_cert(self):
        r = requests.get(f"{API}/verify/cover/{SEED_CERT}", timeout=20)
        assert r.status_code == 200, f"expected 200, got {r.status_code}: {r.text[:200]}"
        assert r.headers.get("content-type", "").startswith("image/png")
        assert len(r.content) > 100

    def test_pdf_valid_cert_is_two_page_pdf(self):
        r = requests.get(f"{API}/verify/pdf/{SEED_CERT}", timeout=30)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content.startswith(b"%PDF")
        # crude count of "/Type /Page" occurrences (should include 2 pages)
        pages = r.content.count(b"/Type /Page") - r.content.count(b"/Type /Pages")
        assert pages >= 2, f"Expected >=2 pages, saw {pages}"
        # NO QR/barcode: sanity — no 'QRCode' word in PDF stream
        low = r.content.lower()
        assert b"qrcode" not in low

    def test_cover_nonexistent_returns_404(self):
        r = requests.get(f"{API}/verify/cover/{NONEXIST_CERT}", timeout=15)
        assert r.status_code == 404

    def test_cover_bad_format_returns_404(self):
        r = requests.get(f"{API}/verify/cover/{BAD_FORMAT}", timeout=15)
        assert r.status_code == 404

    def test_pdf_nonexistent_returns_404(self):
        r = requests.get(f"{API}/verify/pdf/{NONEXIST_CERT}", timeout=15)
        assert r.status_code == 404


# --- Admin demo/sample PDFs (must NOT create DB records) ---
class TestAdminSamplePreviews:
    def test_demo_preview_pdf(self, auth):
        r = requests.get(f"{API}/admin/certificates/demo-preview", headers=auth, timeout=30)
        assert r.status_code == 200, r.text[:300]
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content.startswith(b"%PDF")
        pages = r.content.count(b"/Type /Page") - r.content.count(b"/Type /Pages")
        assert pages >= 2

    def test_sample_card_pdf(self, auth):
        r = requests.get(f"{API}/admin/certificates/sample-card", headers=auth, timeout=30)
        assert r.status_code == 200, r.text[:300]
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content.startswith(b"%PDF")


# --- Admin legality: signatory + signature + single-active ---
def _tiny_png_bytes():
    # minimal valid 1x1 PNG
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
        "0000000d49444154789c6300010000000500010d0a2db40000000049454e44ae426082"
    )


class TestLegalitySignatoryAndActive:
    created = []

    def test_create_first_active(self, auth):
        body = {
            "certificate_name": "TEST_Iter27_Leg_A",
            "signatory_name": "Dr. TEST Alpha",
            "signatory_position": "Kepala Laboratorium",
            "active_for_certificates": True,
        }
        r = requests.post(f"{API}/admin/legality", json=body, headers=auth, timeout=15)
        assert r.status_code == 201, r.text
        data = r.json()["data"]
        assert data["signatory_name"] == "Dr. TEST Alpha"
        assert data["signatory_position"] == "Kepala Laboratorium"
        assert data["active_for_certificates"] is True
        TestLegalitySignatoryAndActive.created.append(data["uuid"])

    def test_signature_upload_preview_delete(self, auth):
        uid = TestLegalitySignatoryAndActive.created[0]
        files = {"file": ("sig.png", _tiny_png_bytes(), "image/png")}
        r = requests.post(f"{API}/admin/legality/{uid}/signature", headers=auth, files=files, timeout=15)
        assert r.status_code == 200, r.text
        # GET signature
        rg = requests.get(f"{API}/admin/legality/{uid}/signature", headers=auth, timeout=15)
        assert rg.status_code == 200
        assert rg.headers.get("content-type", "").startswith("image/")
        assert len(rg.content) > 50
        # DELETE
        rd = requests.delete(f"{API}/admin/legality/{uid}/signature", headers=auth, timeout=15)
        assert rd.status_code == 200
        # GET after delete → 404
        rg2 = requests.get(f"{API}/admin/legality/{uid}/signature", headers=auth, timeout=15)
        assert rg2.status_code == 404

    def test_second_active_deactivates_first(self, auth):
        body = {
            "certificate_name": "TEST_Iter27_Leg_B",
            "signatory_name": "Dr. TEST Beta",
            "signatory_position": "Gemologist",
            "active_for_certificates": True,
        }
        r = requests.post(f"{API}/admin/legality", json=body, headers=auth, timeout=15)
        assert r.status_code == 201, r.text
        newid = r.json()["data"]["uuid"]
        TestLegalitySignatoryAndActive.created.append(newid)

        # List and confirm only newest is active
        rl = requests.get(f"{API}/admin/legality", headers=auth, timeout=15)
        assert rl.status_code == 200
        items = rl.json()["data"]["items"]
        by_id = {i["uuid"]: i for i in items}
        assert by_id[newid]["active_for_certificates"] is True
        prev = TestLegalitySignatoryAndActive.created[0]
        assert by_id[prev]["active_for_certificates"] is False, "single-active not enforced"

    @classmethod
    def teardown_class(cls):
        # cleanup TEST_ records
        try:
            r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=10)
            tok = r.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {tok}"}
            for uid in cls.created:
                requests.delete(f"{API}/admin/legality/{uid}", headers=headers, timeout=10)
        except Exception as e:
            print("cleanup failed:", e)
