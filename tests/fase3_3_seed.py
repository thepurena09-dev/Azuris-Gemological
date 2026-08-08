"""Seed & cleanup helpers for FASE 3.3 frontend Playwright run."""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
load_dotenv("/app/frontend/.env")

BASE = (os.environ.get("REACT_APP_BACKEND_URL") or "").rstrip("/")
API = f"{BASE}/api"
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")


def _admin():
    r = requests.post(f"{API}/auth/login", json={"email": "admin@azuris.local", "password": "AzurisDev@2026!"}, timeout=15)
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def seed():
    h = _admin()
    g = requests.post(f"{API}/admin/gemstones", headers=h, json={
        "name_id": "TEST_FE33_Safir",
        "name_en": "TEST_FE33_Blue Sapphire",
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
    }, timeout=15).json()
    c = requests.post(f"{API}/admin/certificates/issue", headers=h, json={
        "gemstone_id": g["uuid"],
        "object_type": "Loose Stone",
        "transparency": "Transparent",
        "examiner": "TEST Gemologist",
        "signatory": "TEST Signatory",
        "conclusion": "Natural Blue Sapphire, heated.",
    }, timeout=20).json()
    print(json.dumps({"gemstone_uuid": g["uuid"], **c}))


def cleanup():
    from pymongo import MongoClient
    cli = MongoClient(MONGO_URL)
    db = cli[DB_NAME]
    # Drop all TEST_ gemstones + associated certs/tokens
    gems = list(db.gemstones.find({"name_en": {"$regex": "^TEST_"}}))
    for g in gems:
        certs = list(db.certificates.find({"gemstone_id": g["uuid"]}))
        for c in certs:
            if c.get("verification_uuid"):
                db.verification_tokens.delete_many({"uuid": c["verification_uuid"]})
            snap = c.get("gemstone_snapshot") or {}
            if snap.get("photo_id"):
                db.gemstone_photos.delete_many({"uuid": snap["photo_id"]})
        db.certificates.delete_many({"gemstone_id": g["uuid"]})
        for mid in (g.get("media_ids") or []):
            db.gemstone_photos.delete_many({"uuid": mid})
    db.gemstones.delete_many({"name_en": {"$regex": "^TEST_"}})
    db.counters.update_one({"name": "certificate", "year": 2026}, {"$set": {"last_number": 14}}, upsert=True)
    cd = db.counters.find_one({"name": "certificate", "year": 2026})
    certs = db.certificates.count_documents({})
    gg = db.gemstones.count_documents({})
    print(json.dumps({"last_number": cd["last_number"], "certificates": certs, "gemstones": gg}))
    cli.close()


if __name__ == "__main__":
    if sys.argv[1] == "seed":
        seed()
    else:
        cleanup()
