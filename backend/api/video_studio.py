"""Video Studio — AI Web Feature Walkthrough Video Generator (PHASE A).

ISOLATED, ADDITIVE module. Does NOT touch any frozen business collection, model,
or endpoint. Provides the web audit, feature map, 90s content blueprint, and an
editable scene-based script + coverage/timing validation. Voice-over, screen
recording and MP4 render are PHASE B (not implemented here).

RBAC: SUPER_ADMIN + ADMINISTRATOR (reuses existing role guards).
Storage: single Mongo doc in the isolated `video_studio_projects` collection.
Routes yield raw data; the global Sprint 8 middleware wraps the success envelope.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth.rbac import require_roles
from db.mongodb import get_database
from models.enums import AdminRole
from models.people import Admin
from services.video_studio_data import (
    ADMIN_NAV,
    BLUEPRINT,
    FEATURE_MAP,
    PAGES,
    PUBLIC_NAV,
    default_project,
)

admin_router = APIRouter(prefix="/admin/video-studio", tags=["video-studio-admin"])

_GUARD = require_roles(AdminRole.ADMINISTRATOR)
_COLLECTION = "video_studio_projects"
_DOC_ID = "default"


# --------------------------------------------------------------------------- #
# Schemas (permissive — the editor sends whole scenes back)                    #
# --------------------------------------------------------------------------- #

class SceneIn(BaseModel):
    id: str
    index: int
    segment: str = ""
    start: float
    end: float
    narration: str = ""
    subtitle: str = ""
    visual: str = ""
    action: str = ""
    feature: str = ""
    benefit: str = ""
    route: str = ""
    record_targets: list[str] = Field(default_factory=list)
    covers: list[str] = Field(default_factory=list)
    status: str = "draft"


class ProjectUpdate(BaseModel):
    title: str | None = None
    scenes: list[SceneIn]


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #

def _clean(doc: dict) -> dict:
    doc = dict(doc)
    doc.pop("_id", None)
    return doc


async def _load_or_seed(db) -> dict:
    doc = await db[_COLLECTION].find_one({"_id": _DOC_ID})
    if not doc:
        seed = default_project()
        seed["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db[_COLLECTION].replace_one({"_id": _DOC_ID}, seed, upsert=True)
        doc = seed
    return doc


def _word_count(scenes: list[dict]) -> int:
    return sum(len((s.get("narration") or "").split()) for s in scenes)


def validate_project(project: dict) -> dict:
    scenes = sorted(project.get("scenes", []), key=lambda s: s.get("start", 0))
    checks: list[dict] = []

    def add(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    # Duration
    if scenes:
        total = max(s["end"] for s in scenes) - min(s["start"] for s in scenes)
    else:
        total = 0.0
    add("duration_90s", abs(total - 90.0) <= 1.5, f"Total {total:.1f}s (target 90 ± 1.5s)")

    # Contiguity — no gaps / overlaps
    gaps = []
    for a, b in zip(scenes, scenes[1:]):
        if abs(a["end"] - b["start"]) > 0.05:
            gaps.append(f"{a['id']}→{b['id']} ({a['end']:.1f}s vs {b['start']:.1f}s)")
    add("timeline_contiguous", not gaps, "Tidak ada celah/tumpang tindih." if not gaps else "; ".join(gaps))

    # Word count
    wc = _word_count(scenes)
    add("word_count", 200 <= wc <= 230, f"{wc} kata (target 210–225).")

    # Every scene has narration + visual + route
    incomplete = [s["id"] for s in scenes if not (s.get("narration") and s.get("visual") and s.get("route"))]
    add("scenes_complete", not incomplete, "Semua scene lengkap." if not incomplete else "Kurang: " + ", ".join(incomplete))

    # Feature coverage — every feature in the map appears in at least one scene
    covered = {fid for s in scenes for fid in s.get("covers", [])}
    all_ids = {f["id"] for f in FEATURE_MAP}
    missing = sorted(all_ids - covered)
    missing_labels = [f["feature"] for f in FEATURE_MAP if f["id"] in missing]
    add("feature_coverage", not missing,
        "Semua fitur ter-cover." if not missing else "Belum ter-cover: " + ", ".join(missing_labels))

    # CTA ends before/at video end
    cta = [s for s in scenes if s.get("segment") == "CTA"]
    add("cta_present", bool(cta), "Ada segmen CTA." if cta else "Segmen CTA belum ada.")

    passed = sum(1 for c in checks if c["pass"])
    return {
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "ok": passed == len(checks),
        "word_count": wc,
        "duration_sec": round(total, 1),
        "covered_features": sorted(covered),
        "missing_features": missing,
    }


# --------------------------------------------------------------------------- #
# Endpoints                                                                    #
# --------------------------------------------------------------------------- #

@admin_router.get("/audit")
async def get_audit(admin: Admin = Depends(_GUARD)):
    """PHASE 1+2 — verified web audit + feature map (read-only)."""
    return {
        "pages": PAGES,
        "navigation": {"public": PUBLIC_NAV, "admin": ADMIN_NAV},
        "feature_map": FEATURE_MAP,
        "blueprint": BLUEPRINT,
        "counts": {"pages": len(PAGES), "features": len(FEATURE_MAP)},
    }


@admin_router.get("/project")
async def get_project(admin: Admin = Depends(_GUARD), db=Depends(get_database)):
    """PHASE 3+4+5 — current editable script/scene project (seeds default once)."""
    doc = await _load_or_seed(db)
    return _clean(doc)


@admin_router.put("/project")
async def save_project(
    body: ProjectUpdate, admin: Admin = Depends(_GUARD), db=Depends(get_database)
):
    """Save edited scenes (modular — the editor sends the full scene list back)."""
    current = await _load_or_seed(db)
    scenes = [s.model_dump() for s in sorted(body.scenes, key=lambda s: s.index)]
    current["scenes"] = scenes
    if body.title is not None:
        current["title"] = body.title
    current["version"] = int(current.get("version", 1)) + 1
    current["updated_at"] = datetime.now(timezone.utc).isoformat()
    current["_id"] = _DOC_ID
    await db[_COLLECTION].replace_one({"_id": _DOC_ID}, current, upsert=True)
    return _clean(current)


@admin_router.post("/project/reset")
async def reset_project(admin: Admin = Depends(_GUARD), db=Depends(get_database)):
    """Restore the default (verified) walkthrough script."""
    seed = default_project()
    seed["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db[_COLLECTION].replace_one({"_id": _DOC_ID}, seed, upsert=True)
    return _clean(seed)


@admin_router.get("/validate")
async def validate(admin: Admin = Depends(_GUARD), db=Depends(get_database)):
    """PHASE 11 (partial) — sync/coverage/timing validation of the current script."""
    doc = await _load_or_seed(db)
    return validate_project(doc)
