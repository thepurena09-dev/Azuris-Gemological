"""Tests for the admin certificate DEMO PREVIEW endpoint (stateless, zero DB mutation).

Verifies:
  * GET /api/admin/certificates/demo-preview requires auth (401 anon)
  * Returns application/pdf, valid PDF magic bytes
  * PDF contains "AZR-GEM-DEMO" and does NOT contain the genuine next number "AZR-GEM-000015-26"
  * PDF has 2 pages of A6 landscape (MediaBox ~ 419.5 x 297.6 pt)
  * DB SAFETY: counter stays last_number=14 and collections certificates/gemstones/customers/verification_tokens remain 0
  * Existing genuine issuance list endpoints still respond (without mutating DB)
"""
import os
import re
import asyncio
import pytest
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/") if os.environ.get("REACT_APP_BACKEND_URL") else "https://azuris-preview-build.preview.emergentagent.com"
# Read frontend .env to be safe
with open("/app/frontend/.env") as f:
    for ln in f:
        if ln.startswith("REACT_APP_BACKEND_URL"):
            BASE_URL = ln.split("=", 1)[1].strip().rstrip("/")

API = f"{BASE_URL}/api"
ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PASSWORD = "AzurisDev@2026!"

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    data = r.json()
    tok = (data.get("data") or data).get("access_token") or data.get("access_token")
    assert tok, f"no access_token in {data}"
    return tok


@pytest.fixture(scope="module")
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _snapshot():
    async def _run():
        c = AsyncIOMotorClient(MONGO_URL)
        db = c[DB_NAME]
        snap = {}
        for name in ["certificates", "gemstones", "customers", "verification_tokens"]:
            snap[name] = await db[name].count_documents({})
        counter = await db["counters"].find_one({"name": "certificate"})
        snap["counter_last_number"] = counter["last_number"] if counter else None
        snap["counter_year"] = counter["year"] if counter else None
        c.close()
        return snap
    return asyncio.get_event_loop().run_until_complete(_run()) if False else asyncio.run(_run())


def test_baseline_clean_db():
    snap = _snapshot()
    assert snap["counter_last_number"] == 14, f"baseline counter must be 14: {snap}"
    for k in ["certificates", "gemstones", "customers", "verification_tokens"]:
        assert snap[k] == 0, f"baseline {k} must be 0, got {snap[k]}"


def test_demo_preview_requires_auth():
    r = requests.get(f"{API}/admin/certificates/demo-preview", timeout=30)
    assert r.status_code == 401, f"expected 401 unauth, got {r.status_code}"


def test_demo_preview_returns_valid_pdf(auth_headers):
    r = requests.get(f"{API}/admin/certificates/demo-preview", headers=auth_headers, timeout=60)
    assert r.status_code == 200, f"status {r.status_code} body={r.text[:300]}"
    assert r.headers.get("content-type", "").startswith("application/pdf"), r.headers
    pdf = r.content
    assert pdf[:4] == b"%PDF", "not a valid PDF"

    # Extract text via PyMuPDF (streams are FlateDecode-compressed by ReportLab)
    import pymupdf
    doc = pymupdf.open(stream=pdf, filetype="pdf")
    try:
        assert doc.page_count == 2, f"expected 2 pages, got {doc.page_count}"
        all_text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
        # MediaBox — A6 landscape ~419.5 x 297.6 pt
        for i in range(doc.page_count):
            rect = doc[i].rect
            assert 418 < rect.width < 421 and 296 < rect.height < 299, \
                f"page {i} MediaBox not A6 landscape: {rect.width}x{rect.height}"
    finally:
        doc.close()

    assert "AZR-GEM-DEMO" in all_text, f"cert number not found in extracted text: {all_text[:400]}"
    assert "AZR-GEM-000015-26" not in all_text, "PDF text must NOT contain the genuine next number"
    # DEMO watermark present
    assert "DEMO" in all_text and ("PREVIEW" in all_text or "NOT VALID" in all_text), \
        f"DEMO watermark not found in text: {all_text[:400]}"


def test_demo_preview_no_db_mutation(auth_headers):
    before = _snapshot()
    # hit demo endpoint multiple times
    for _ in range(3):
        r = requests.get(f"{API}/admin/certificates/demo-preview", headers=auth_headers, timeout=60)
        assert r.status_code == 200
    after = _snapshot()
    assert before == after, f"DB mutated by demo endpoint!\nbefore={before}\nafter={after}"
    assert after["counter_last_number"] == 14
    for k in ["certificates", "gemstones", "customers", "verification_tokens"]:
        assert after[k] == 0


def test_existing_endpoints_respond(auth_headers):
    # list certificates
    r = requests.get(f"{API}/admin/certificates", headers=auth_headers, timeout=30)
    assert r.status_code == 200
    body = r.json()
    items = (body.get("data") or body).get("items")
    assert items == []
    # list gemstones
    r = requests.get(f"{API}/admin/gemstones", headers=auth_headers, timeout=30)
    assert r.status_code == 200
    # issue endpoint exists — call with invalid uuid → not-500; must be 4xx
    r = requests.post(
        f"{API}/admin/certificates/issue",
        headers={**auth_headers, "Content-Type": "application/json"},
        json={"gemstone_id": "00000000-0000-0000-0000-000000000000"},
        timeout=30,
    )
    assert r.status_code in (400, 404, 409, 422), f"unexpected: {r.status_code} {r.text[:300]}"
    # verify baseline preserved (issue rejected → no mutation)
    snap = _snapshot()
    assert snap["counter_last_number"] == 14
    assert snap["certificates"] == 0
