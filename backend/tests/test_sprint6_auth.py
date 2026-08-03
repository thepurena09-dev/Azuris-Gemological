"""Sprint 6 Auth tests — JWT admin-only login/refresh/logout/me + security logs."""
import os
import time
import pytest
import requests
from pymongo import MongoClient

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # Fallback to reading frontend/.env for backend URL
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")

API = f"{BASE_URL}/api"
ADMIN_EMAIL = "admin@azuris.local"
ADMIN_PASSWORD = "AzurisDev@2026!"

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"


@pytest.fixture(scope="module")
def s():
    return requests.Session()


@pytest.fixture(scope="module")
def logged_in(s):
    r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()


# ---------- login ----------
class TestLogin:
    def test_login_success_shape(self, logged_in):
        data = logged_in
        assert "access_token" in data and isinstance(data["access_token"], str) and len(data["access_token"]) > 20
        assert "refresh_token" in data and isinstance(data["refresh_token"], str) and len(data["refresh_token"]) > 20
        assert data.get("token_type") == "bearer"
        admin = data.get("admin")
        assert admin, "admin object missing"
        assert admin.get("email") == ADMIN_EMAIL
        assert admin.get("role") == "SUPER_ADMIN"
        assert "password_hash" not in admin
        # Also ensure no field name suggesting password/hash is leaked
        for k in admin.keys():
            assert "password" not in k.lower(), f"leaked field {k}"

    def test_login_wrong_password(self, s):
        r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": "WRONG_pw_xxx!!"})
        assert r.status_code == 401
        assert r.json().get("detail") == "Invalid credentials"

    def test_login_unknown_email_same_generic(self, s):
        r = s.post(f"{API}/auth/login", json={"email": "nobody@azuris.local", "password": "whatever123"})
        assert r.status_code == 401
        assert r.json().get("detail") == "Invalid credentials"


# ---------- /me ----------
class TestMe:
    def test_me_ok(self, s, logged_in):
        r = s.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {logged_in['access_token']}"})
        assert r.status_code == 200, r.text
        me = r.json()
        assert me.get("email") == ADMIN_EMAIL
        assert me.get("role") == "SUPER_ADMIN"
        assert "password_hash" not in me

    def test_me_no_token(self, s):
        r = s.get(f"{API}/auth/me")
        assert r.status_code == 401

    def test_me_invalid_token(self, s):
        r = s.get(f"{API}/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
        assert r.status_code == 401


# ---------- refresh + rotation ----------
class TestRefreshRotation:
    def test_refresh_rotates_and_old_invalidated(self, s, logged_in):
        old_refresh = logged_in["refresh_token"]
        old_access = logged_in["access_token"]
        # Ensure iat differs by 1s so tokens differ deterministically
        time.sleep(1.1)
        r = s.post(f"{API}/auth/refresh", json={"refresh_token": old_refresh})
        assert r.status_code == 200, r.text
        data = r.json()
        assert "access_token" in data and data["access_token"] != old_access
        assert "refresh_token" in data and data["refresh_token"] != old_refresh

        # Reuse OLD refresh — must be rejected (rotation invalidated it)
        r2 = s.post(f"{API}/auth/refresh", json={"refresh_token": old_refresh})
        assert r2.status_code == 401

        # Save new tokens back for later tests
        logged_in["access_token"] = data["access_token"]
        logged_in["refresh_token"] = data["refresh_token"]

    def test_refresh_invalid_token(self, s):
        r = s.post(f"{API}/auth/refresh", json={"refresh_token": "invalid.token.value"})
        assert r.status_code == 401


# ---------- logout ----------
class TestLogout:
    def test_logout_requires_auth(self, s):
        r = s.post(f"{API}/auth/logout", json={"refresh_token": "abcabcabcabc"})
        assert r.status_code == 401

    def test_logout_success_then_refresh_dead(self, s):
        # Fresh session to avoid stomping other fixtures
        login = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}).json()
        access = login["access_token"]
        refresh = login["refresh_token"]

        r = s.post(
            f"{API}/auth/logout",
            headers={"Authorization": f"Bearer {access}"},
            json={"refresh_token": refresh},
        )
        assert r.status_code == 200
        assert r.json() == {"success": True}

        r2 = s.post(f"{API}/auth/refresh", json={"refresh_token": refresh})
        assert r2.status_code == 401


# ---------- password hashing + security_logs (direct DB checks) ----------
class TestDataLayer:
    def test_password_hash_is_argon2id(self):
        client = MongoClient(MONGO_URL)
        try:
            doc = client[DB_NAME]["admins"].find_one({"email": ADMIN_EMAIL})
            assert doc is not None, "seeded admin missing"
            ph = doc.get("password_hash", "")
            assert ph.startswith("$argon2id$"), f"expected argon2id hash, got {ph[:20]}"
            assert ADMIN_PASSWORD not in ph
        finally:
            client.close()

    def test_security_logs_written_and_no_secrets(self):
        # Trigger one of each event type freshly
        s = requests.Session()
        # login_success
        login = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}).json()
        # login_fail
        s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong!!"})
        # token_refresh
        ref = s.post(f"{API}/auth/refresh", json={"refresh_token": login["refresh_token"]}).json()
        # logout
        s.post(
            f"{API}/auth/logout",
            headers={"Authorization": f"Bearer {ref['access_token']}"},
            json={"refresh_token": ref["refresh_token"]},
        )

        client = MongoClient(MONGO_URL)
        try:
            coll = client[DB_NAME]["security_logs"]
            docs = list(coll.find({}).sort("_id", -1).limit(200))
            found = {d.get("event_type") for d in docs}
            for evt in ["login_success", "login_fail", "token_refresh", "logout"]:
                assert evt in found, f"missing event {evt} in {found}"

            # No plaintext password / raw token stored in any doc
            for d in docs:
                assert "password" not in d
                assert "refresh_token" not in d
                assert "access_token" not in d
                assert "token" not in d
                blob = str(d).lower()
                assert ADMIN_PASSWORD.lower() not in blob, "plaintext password leaked to logs"
        finally:
            client.close()
