from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


# backend/models/catalog.py
path = Path("backend/models/catalog.py")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    '    presentation_title_size: Optional[float] = Field(default=None, ge=8, le=22)\n    description_id: Optional[str] = None\n',
    '    presentation_title_size: Optional[float] = Field(default=None, ge=8, le=22)\n    # Optional per-field certificate typography overrides. Empty means automatic sizing.\n    certificate_text_sizes: dict[str, float] = Field(default_factory=dict)\n    description_id: Optional[str] = None\n',
    "catalog",
)
path.write_text(text, encoding="utf-8")

# backend/api/certificates.py
path = Path("backend/api/certificates.py")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    '    presentation_title_size: float | None = Field(default=None, ge=8, le=22)\n\n    @field_validator("gem_code")\n',
    '''    presentation_title_size: float | None = Field(default=None, ge=8, le=22)\n    certificate_text_sizes: dict[str, float] = Field(default_factory=dict)\n\n    @field_validator("certificate_text_sizes")\n    @classmethod\n    def _validate_text_sizes(cls, value: dict[str, float]) -> dict[str, float]:\n        limits = {\n            "name": (8.0, 22.0),\n            "category": (5.0, 12.0),\n            "species": (5.0, 12.0),\n            "dimensions": (5.0, 12.0),\n            "origin": (5.0, 12.0),\n            "treatment": (5.0, 12.0),\n        }\n        out: dict[str, float] = {}\n        for key, raw in (value or {}).items():\n            if key not in limits:\n                continue\n            size = float(raw)\n            lo, hi = limits[key]\n            if not lo <= size <= hi:\n                raise ValueError(f"{key} text size must be between {lo:g} and {hi:g} pt.")\n            out[key] = round(size, 1)\n        return out\n\n    @field_validator("gem_code")\n''',
    "api-validator",
)
text = replace_once(
    text,
    '        "presentation_title_size": g.presentation_title_size,\n        "status": g.status,\n',
    '        "presentation_title_size": g.presentation_title_size,\n        "certificate_text_sizes": g.certificate_text_sizes or {},\n        "status": g.status,\n',
    "api-view",
)
text = replace_once(
    text,
    '    await repo.update_one({"uuid": uuid}, {**body.model_dump(), "updated_by": admin.uuid, "updated_at": utcnow_iso()})\n    after = await repo.get_by_uuid(uuid)\n',
    '''    await repo.update_one({"uuid": uuid}, {**body.model_dump(), "updated_by": admin.uuid, "updated_at": utcnow_iso()})\n    # Identity data stays frozen in the issuance snapshot. Typography is a\n    # presentation preference, so keep only these display overrides in sync for\n    # an already-issued certificate.\n    if before.certificate_id:\n        await CertificateRepository(db).update_one(\n            {"uuid": before.certificate_id},\n            {\n                "gemstone_snapshot.certificate_text_sizes": body.certificate_text_sizes or {},\n                "gemstone_snapshot.presentation_title_size": body.presentation_title_size,\n                "updated_by": admin.uuid,\n                "updated_at": utcnow_iso(),\n            },\n        )\n    after = await repo.get_by_uuid(uuid)\n''',
    "api-sync",
)
path.write_text(text, encoding="utf-8")

# backend/services/issuance.py
path = Path("backend/services/issuance.py")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    '        "presentation_title_size": gem.presentation_title_size,\n        "notes": extra.get("notes"),\n',
    '        "presentation_title_size": gem.presentation_title_size,\n        "certificate_text_sizes": dict(gem.certificate_text_sizes or {}),\n        "notes": extra.get("notes"),\n',
    "issuance",
)
path.write_text(text, encoding="utf-8")

# backend/services/certificate_pdf.py
path = Path("backend/services/certificate_pdf.py")
text = path.read_text(encoding="utf-8")
old = '''    # detail fields — full width, only present values (English preferred, no invented data)\n    pairs = [\n        ("Gemstone Name", snap.get("name_en") or snap.get("name")),\n        ("Object Type", snap.get("object_type")),\n        ("Species", snap.get("species")),\n        ("Variety", snap.get("variety")),\n        ("Carat Weight", f"{snap.get('carat')} ct" if snap.get("carat") else None),\n        ("Measurements", snap.get("dimensions")),\n        ("Shape", snap.get("shape")),\n        ("Cut", snap.get("cut")),\n        ("Colour", snap.get("color")),\n        ("Transparency", snap.get("transparency")),\n        ("Treatment", snap.get("treatment")),\n        ("Origin", snap.get("origin")),\n        ("Date of Issue", (cert.get("issued_at") or "")[:10] or None),\n    ]\n    pairs = [(k, v) for k, v in pairs if v not in (None, "", "None")]\n\n    row_h = 5.8 * mm\n    for i, (k, v) in enumerate(pairs):\n        _field(c, x, w, y, k, v, val_size=7.8, zebra=(i % 2 == 0))\n        y -= row_h\n'''
new = '''    # detail fields — full width, only present values (English preferred, no invented data)\n    text_sizes = snap.get("certificate_text_sizes") or {}\n\n    def detail_size(key: str, default: float = 7.8) -> float:\n        try:\n            return max(5.0, min(12.0, float(text_sizes.get(key, default))))\n        except (TypeError, ValueError):\n            return default\n\n    pairs = [\n        ("name", "Gemstone Name", snap.get("name_en") or snap.get("name")),\n        ("category", "Object Type", snap.get("object_type")),\n        ("species", "Species", snap.get("species")),\n        ("category", "Variety", snap.get("variety")),\n        (None, "Carat Weight", f"{snap.get('carat')} ct" if snap.get("carat") else None),\n        ("dimensions", "Measurements", snap.get("dimensions")),\n        (None, "Shape", snap.get("shape")),\n        (None, "Cut", snap.get("cut")),\n        (None, "Colour", snap.get("color")),\n        (None, "Transparency", snap.get("transparency")),\n        ("treatment", "Treatment", snap.get("treatment")),\n        ("origin", "Origin", snap.get("origin")),\n        (None, "Date of Issue", (cert.get("issued_at") or "")[:10] or None),\n    ]\n    pairs = [(size_key, k, v) for size_key, k, v in pairs if v not in (None, "", "None")]\n\n    row_h = 5.8 * mm\n    for i, (size_key, k, v) in enumerate(pairs):\n        size = detail_size(size_key) if size_key else 7.8\n        _field(c, x, w, y, k, v, val_size=size, zebra=(i % 2 == 0))\n        y -= row_h\n'''
text = replace_once(text, old, new, "pdf-details")
text = replace_once(
    text,
    '    configured_size = snap.get("presentation_title_size")\n',
    '    text_sizes = snap.get("certificate_text_sizes") or {}\n    configured_size = text_sizes.get("name", snap.get("presentation_title_size"))\n',
    "pdf-title-source",
)
text = replace_once(
    text,
    '    font_size = configured_size if configured_size is not None else 22.0\n',
    '    font_size = configured_size if configured_size is not None else (14.0 if len(name_text) >= 20 else 22.0)\n',
    "pdf-auto-long-name",
)
text = replace_once(
    text,
    '        _tracked(c, 0, ty, str(gtype).upper(), BODY, 8.5, GOLD_DK, tracking=2.4, center=cx)\n',
    '''        try:\n            type_size = max(5.0, min(12.0, float(text_sizes.get("category", 8.5))))\n        except (TypeError, ValueError):\n            type_size = 8.5\n        _tracked(c, 0, ty, str(gtype).upper(), BODY, type_size, GOLD_DK, tracking=2.4, center=cx)\n''',
    "pdf-category-size",
)
path.write_text(text, encoding="utf-8")

# Replace admin page with the staged version.
source = Path("scripts/GemstonesPage_text_sizes.tsx")
target = Path("frontend/src/pages/admin/GemstonesPage.tsx")
target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
print("TEXT_SIZE_PATCH_APPLIED")
