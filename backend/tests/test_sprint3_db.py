"""Sprint 3 tests: database health integration, repository foundation, index bootstrap."""
import os
import subprocess
import sys

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


# --- Database health integration ---
def test_health_reports_database_connected():
    resp = requests.get(f"{BASE_URL}/api/health", timeout=15)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok", f"status must be ok, got {data}"
    assert data.get("service") == "azuris-platform"
    assert data.get("version") == "0.1.0"
    assert data.get("sprint") == 3
    assert data.get("environment") == "development"
    assert data.get("database") == "connected"


# --- Repository foundation import ---
def test_base_repository_import_and_methods():
    sys.path.insert(0, "/app/backend")
    from repositories.base import BaseRepository  # noqa: WPS433
    for m in ("find_one", "find_many", "count", "insert_one", "update_one", "soft_delete"):
        assert hasattr(BaseRepository, m), f"BaseRepository missing method {m}"


# --- Index bootstrap idempotency ---
EXPECTED_COLLECTIONS = {
    "admins", "customers", "gemstones", "jewelry", "certificates", "warranties",
    "ownership_transfers", "verification_tokens", "membership_cards", "media",
    "site_content", "audit_logs", "verification_logs", "security_logs",
}


@pytest.mark.parametrize("run", [1, 2])
def test_init_db_script_is_idempotent(run):
    result = subprocess.run(
        [sys.executable, "-m", "scripts.init_db"],
        cwd="/app/backend",
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"init_db failed (run {run}): {result.stderr}"
    out = result.stdout
    for coll in EXPECTED_COLLECTIONS:
        assert coll in out, f"Collection {coll} missing in run {run} output:\n{out}"
