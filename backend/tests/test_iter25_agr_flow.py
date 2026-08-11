"""Iteration 25 — AGR-focused regression.

Verifies: admin login, admin certificate 2-page PDF + card PDF, public
/api/verify/pdf/{number} (2 pages, no QR), /api/verify/qr token flow,
and issue flow (create gemstone + issue certificate).
"""
import io
import os
import re
import time

import pytest
import requests

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    from PyPDF2 import PdfReader  # type: ignore

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://gemstone-cert-1.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PW = "AzurisDev@2026!"
KNOWN_CERT = "AZR-GEM-000015-26"
KNOWN_TOKEN = "_xruGvliF1ltxRJr_-nOyId7lGhnh9ZaKeA4GHwZ_AM"


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PW}, timeout=30)
    assert r.status_code == 200, r.text
    body = r.json()
    data = body.get("data", body)
    tok = data.get("access_token")
    assert tok, body
    return tok


@pytest.fixture(scope="module")
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- Auth ----------
def test_admin_login():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PW}, timeout=30)
    assert r.status_code == 200
    d = r.json().get("data", r.json())
    assert d.get("access_token")
    assert d.get("admin", {}).get("email") == ADMIN_EMAIL


# ---------- Public QR verify ----------
def test_verify_qr_valid_token():
    r = requests.post(f"{BASE_URL}/api/verify/qr", json={"token": KNOWN_TOKEN}, timeout=30)
    assert r.status_code == 200, r.text
    d = r.json().get("data", r.json())
    # Contains gemstone info
    assert d.get("status") in ("ok", "valid", "verified") or d.get("certificate")
    body_str = str(d).lower()
    assert "azr-gem" in body_str or "gemstone" in body_str


def test_verify_qr_invalid_token():
    r = requests.post(f"{BASE_URL}/api/verify/qr", json={"token": "bogus_invalid_token"}, timeout=30)
    # Should still return 200 with not_found status (generic)
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        d = r.json().get("data", r.json())
        assert d.get("status") in ("not_found", "invalid", "error") or d.get("certificate") is None


# ---------- Public number-search PDF ----------
def test_public_pdf_valid_number_is_two_pages_no_qr():
    r = requests.get(f"{BASE_URL}/api/verify/pdf/{KNOWN_CERT}", timeout=30)
    assert r.status_code == 200, r.text[:200]
    assert r.headers.get("content-type", "").startswith("application/pdf")
    reader = PdfReader(io.BytesIO(r.content))
    assert len(reader.pages) == 2, f"Expected 2 pages, got {len(reader.pages)}"
    # Page 2 must contain 'From AGR'
    p2_text = reader.pages[1].extract_text() or ""
    assert "From AGR" in p2_text, f"'From AGR' not on page 2: {p2_text[:300]}"
    # No embedded images (QR/barcode) on any page
    total_images = 0
    for p in reader.pages:
        try:
            total_images += len(list(p.images))
        except Exception:
            pass
    assert total_images == 0, f"Expected 0 images, found {total_images}"


def test_public_pdf_invalid_format_404():
    r = requests.get(f"{BASE_URL}/api/verify/pdf/NOT-A-NUMBER", timeout=30)
    assert r.status_code == 404


def test_public_pdf_unknown_number_404():
    r = requests.get(f"{BASE_URL}/api/verify/pdf/AZR-GEM-999999-99", timeout=30)
    assert r.status_code == 404


# ---------- Admin certificate PDF + Card ----------
def _find_cert_uuid(headers, number):
    r = requests.get(f"{BASE_URL}/api/admin/certificates?page=1&page_size=100", headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    d = r.json().get("data", r.json())
    items = d.get("items") or d.get("results") or d if isinstance(d, list) else d.get("items", [])
    for it in items:
        if it.get("certificate_number") == number:
            return it.get("uuid") or it.get("id")
    return None


def test_admin_pdf_endpoint(auth_headers):
    uid = _find_cert_uuid(auth_headers, KNOWN_CERT)
    assert uid, f"Certificate {KNOWN_CERT} not found in admin list"
    r = requests.get(f"{BASE_URL}/api/admin/certificates/{uid}/pdf", headers=auth_headers, timeout=30)
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("application/pdf")
    reader = PdfReader(io.BytesIO(r.content))
    assert len(reader.pages) == 2


def test_admin_card_endpoint(auth_headers):
    uid = _find_cert_uuid(auth_headers, KNOWN_CERT)
    assert uid
    r = requests.get(f"{BASE_URL}/api/admin/certificates/{uid}/card", headers=auth_headers, timeout=30)
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("application/pdf")
    reader = PdfReader(io.BytesIO(r.content))
    assert len(reader.pages) == 1
    # Card has QR image
    total_images = 0
    for p in reader.pages:
        try:
            total_images += len(list(p.images))
        except Exception:
            pass
    assert total_images >= 1, "Card should contain QR image"


# ---------- End-to-end issue flow (creates ONE gemstone+cert) ----------
def test_create_gemstone_and_issue_cert(auth_headers):
    ts = int(time.time())
    payload = {
        "name_id": f"TEST_Batu_{ts}",
        "name_en": f"TEST_Gem_{ts}",
        "category": "precious",
        "gemstone_type": "sapphire",
        "weight_carat": 1.23,
        "color": "blue",
        "clarity": "VS",
        "cut": "oval",
        "shape": "oval",
        "origin": "Sri Lanka",
        "treatment": "none",
    }
    r = requests.post(f"{BASE_URL}/api/admin/gemstones", json=payload, headers=auth_headers, timeout=30)
    assert r.status_code in (200, 201), r.text
    d = r.json().get("data", r.json())
    gem_uuid = d.get("uuid") or d.get("id")
    assert gem_uuid, d

    # Issue certificate
    r2 = requests.post(
        f"{BASE_URL}/api/admin/certificates/issue",
        json={"gemstone_id": gem_uuid},
        headers=auth_headers,
        timeout=30,
    )
    assert r2.status_code in (200, 201), r2.text
    d2 = r2.json().get("data", r2.json())
    number = d2.get("certificate_number")
    assert number and re.match(r"^AZR-GEM-\d{6}-\d{2}$", number), d2
    cert_uid = d2.get("certificate_uuid") or d2.get("uuid") or d2.get("id")
    assert cert_uid

    # Fetch pdf + card + public pdf
    rp = requests.get(f"{BASE_URL}/api/admin/certificates/{cert_uid}/pdf", headers=auth_headers, timeout=30)
    assert rp.status_code == 200
    rc = requests.get(f"{BASE_URL}/api/admin/certificates/{cert_uid}/card", headers=auth_headers, timeout=30)
    assert rc.status_code == 200
    rpub = requests.get(f"{BASE_URL}/api/verify/pdf/{number}", timeout=30)
    assert rpub.status_code == 200
