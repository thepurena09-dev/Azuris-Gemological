"""Iteration 29 — Card redesign PDFs, /verify page routing, and real cert AGR-RBY-000015-26.

Non-destructive: only reads. Does NOT issue/revoke certs. Counter must remain 15.
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PASSWORD = "AzurisDev@2026!"

REAL_CERT = "AGR-RBY-000015-26"
BOGUS_CERT = "AGR-XYZ-999999-99"


@pytest.fixture(scope="module")
def auth():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, r.text
    tok = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _pdf_page_count(content: bytes) -> int:
    return content.count(b"/Type /Page") - content.count(b"/Type /Pages")


class TestCardRedesign:
    def test_sample_card_is_pdf(self, auth):
        r = requests.get(f"{API}/admin/certificates/sample-card", headers=auth, timeout=30)
        assert r.status_code == 200, r.text[:300]
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content.startswith(b"%PDF")
        assert len(r.content) > 500
        pages = _pdf_page_count(r.content)
        assert pages == 1, f"card should be 1 page, got {pages}"

    def test_demo_preview_is_4page_pdf(self, auth):
        r = requests.get(f"{API}/admin/certificates/demo-preview", headers=auth, timeout=30)
        assert r.status_code == 200, r.text[:300]
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content.startswith(b"%PDF")
        pages = _pdf_page_count(r.content)
        assert pages >= 4, f"demo preview should be >=4 pages, got {pages}"


class TestRealCertificate:
    def test_verify_cover_real_cert(self):
        r = requests.get(f"{API}/verify/cover/{REAL_CERT}", timeout=20)
        assert r.status_code == 200, f"cover returned {r.status_code}: {r.text[:200]}"
        assert r.headers.get("content-type", "").startswith("image/")
        assert len(r.content) > 100

    def test_verify_pdf_real_cert_4_pages(self):
        r = requests.get(f"{API}/verify/pdf/{REAL_CERT}", timeout=30)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content.startswith(b"%PDF")
        pages = _pdf_page_count(r.content)
        assert pages >= 4, f"expected >=4 pages, got {pages}"

    def test_admin_list_and_card(self, auth):
        r = requests.get(f"{API}/admin/certificates", headers=auth, timeout=20, params={"limit": 200})
        assert r.status_code == 200, r.text[:300]
        items = r.json()["data"]["items"]
        found = [c for c in items if c.get("certificate_number") == REAL_CERT or c.get("registration_number") == REAL_CERT]
        assert found, f"cert {REAL_CERT} not found in admin list"
        cert = found[0]
        assert cert.get("status") == "issued", f"status should be issued, got {cert.get('status')}"
        uid = cert["uuid"]

        rc = requests.get(f"{API}/admin/certificates/{uid}/card", headers=auth, timeout=30)
        assert rc.status_code == 200, rc.text[:300]
        assert rc.headers.get("content-type", "").startswith("application/pdf")
        assert rc.content.startswith(b"%PDF")
        pages = _pdf_page_count(rc.content)
        assert pages == 1, f"card should be 1 page, got {pages}"

        # QR is embedded as an image (PNG) inside the PDF — literal URL text is not extractable
        # without a QR decoder. We validate the PDF is a valid 1-page card; QR content is
        # verified by frontend flow (deep-link routing tests).
        assert len(rc.content) > 5000, "card PDF suspiciously small"


class TestQrEndpoint:
    def test_qr_bogus_token_no_crash(self):
        r = requests.post(f"{API}/verify/qr", json={"token": "BOGUS_TOKEN_XYZ"}, timeout=15)
        # Should not crash — either 404 not-found or 200 with not-found payload
        assert r.status_code in (200, 400, 404), f"unexpected {r.status_code}: {r.text[:200]}"

    def test_cover_bogus_number_404(self):
        r = requests.get(f"{API}/verify/cover/{BOGUS_CERT}", timeout=15)
        assert r.status_code == 404


class TestCounterUnchanged:
    def test_counter_still_15(self, auth):
        # counter derived from highest sequence used; check via listing and confirm max seq <= 15
        r = requests.get(f"{API}/admin/certificates", headers=auth, timeout=20, params={"limit": 500})
        assert r.status_code == 200
        items = r.json()["data"]["items"]
        max_seq = 0
        pattern = re.compile(r"AGR-[A-Z]+-(\d{6})-\d{2}")
        for c in items:
            m = pattern.match(c.get("certificate_number") or c.get("registration_number") or "")
            if m:
                max_seq = max(max_seq, int(m.group(1)))
        assert max_seq == 15, f"expected counter/max seq = 15, got {max_seq}"
