# Azuris Gemological — PRD & Progress Ledger

## Source of Truth
- **Business Blueprint v1** + **Architecture Lock v1.1** (RBAC, dual-identifier ObjectId+UUID,
  document versioning, 3 log collections, metadata-rich media). Sprint Book: Sprints 1–30.
- Delivery model: one sprint at a time, approval-gated, no rewrite/rename of prior work.

## Product Summary
Luxury gemological certification & verification platform: premium bilingual (Indonesian default + English)
public catalog (no prices, WhatsApp CTA), certificate issuance with QR verification, public verification
portal (QR token OR cert# + security code), warranties, ownership transfers, membership cards, CMS,
and a role-aware admin dashboard.

## User Personas / Roles (RBAC — Architecture Lock §6)
- SUPER_ADMIN — full system control incl. admin management.
- ADMINISTRATOR — full operational control; no admin-account management.
- CONTENT_MANAGER — CMS, media, catalog presentation only.
- CUSTOMER_SERVICE — read-oriented + customer records, verification lookups, WhatsApp handoff.
- Public visitor — catalog browsing + verification portal.

## Tech Stack
React 19 + TypeScript + Tailwind + shadcn/ui · FastAPI · MongoDB (Motor, from Sprint 3) ·
Phosphor icons · Cormorant Garamond + Outfit fonts. Design: Luxury & Institutional Trust
(dark default, champagne-gold accents).

## Design System — LOCKED v2 (Light Luxury, approved 2026-06)
Permanent identity: **Light theme only** (no dark mode / no theme switch). White (#FFFFFF) + #F8F8F6
surfaces, #111 text / #666 secondary, #E5E5E5 borders. **Deep Emerald #0F3D3E** primary accent;
**Champagne Gold #C9A227** secondary accent (sparing). Fonts: **Playfair Display** (headings) + **Inter** (body).
Max content width 1280px, editorial spacing. Tokens live in `frontend/src/index.css` (:root) + `tailwind.config.js`.
Full spec: `/app/design_guidelines.json`. **Refinement v3 (2026-06):** bright emerald-on-white
photography, larger Playfair headings, champagne-gold hairline accents, premium squared buttons,
cleaner white navigation, warmer ivory secondary, editorial whitespace. (User-referenced image was
not attached to the job; refinement executed from the written visual direction.)

---

## Progress Log

### Sprint 4.5 — Business Rules Lock ✅ (2026-06, documentation only; updated to v1.1)
- `/app/docs/BUSINESS_RULES_LOCK.md` — permanent business rules for all 10 domains (gemstones, jewelry,
  certificates, warranties, ownership, verification, membership cards, media, public verification, admin ops):
  lifecycle, status transitions, immutable/editable fields, versioning, security, validation, audit, constraints.
- **v1.1 locks:** certificate number `AZR-GEM-YYYY-000001`; owner masking (first name 4 / last name 3, remainder `*`);
  verification priority QR→Code→Certificate→Gemstone→Owner; certificate version visibility (current public, previous archived, admin sees all).
- Enforced (not redefined) by implementation sprints 5+.

### Sprint 4 — Domain Models & Schemas ✅ (2026-06, validated via assertion script)
- `models/base.py`: `PyObjectId` (ObjectId→str), `BaseDocument` (`_id`↔`id`, from_mongo/to_mongo),
  mixins — DualId (`uuid`), Audit, SoftDelete, Version.
- `models/enums.py`: locked enums (AdminRole ×4, statuses, media roles/types, verification method/result,
  audit actions, security events).
- Entity models for all 14 collections (`models/{people,catalog,documents,ownership,media,cms,logs}.py`)
  + `COLLECTION_MODELS` map. Certificates/warranties/membership cards carry VersionMixin; logs are append-only.
- `schemas/`: Create/Update/Response DTOs for every entity + pagination. Responses never expose secrets
  (`password_hash`/`token`/`security_code`) or raw ObjectId; public projections mask PII.
- Validation confirmed: dual-id defaults, to_mongo/from_mongo round-trip, versioning defaults, field
  constraints (e.g. weight_carat>0), secret omission, media metadata. No endpoints/logic/UI (per scope).

### Sprint 3 — MongoDB Connection & DB Layer ✅ (2026-06, verified 100% backend + frontend)
- `db/mongodb.py`: async **Motor** connection manager (connect/disconnect/ping, `mongodb` singleton, `get_database`).
- `db/indexes.py`: **index bootstrap** for all 14 locked collections (dual-id unique `uuid`, unique
  `certificate_number`, unique `verification_tokens.token`, media entity link, append-only log time order).
- `db/init.py` + `scripts/init_db.py`: idempotent Mongo initialization (connect + ensure indexes).
- `repositories/base.py`: **repository foundation** — generic async `BaseRepository`
  (find/count/insert/update/soft-delete); not wired to any endpoint (Sprint 5 extends).
- `server.py`: connects DB + runs index bootstrap on startup, disconnects on shutdown (boot never blocked on DB).
- `/api/health` now integrates **DB status** → adds `database: connected|disconnected` (status degrades if ping fails).
- **Visual refinement (Design v3):** brighter emerald-on-white hero photography (removed dark/purple feeling),
  larger Playfair headings, champagne-gold hairline accents, premium squared emerald buttons, cleaner white nav,
  warmer ivory secondary, more editorial whitespace. Routing/pages/components unchanged.

### Sprint 2 — Configuration & Environment Layer ✅ (2026-06, verified 100% backend + frontend)
- Backend `core/config.py`: Pydantic **Settings** (env-driven; app metadata, environment, api_prefix,
  log_level, mongo_url, db_name, cors_origins) with `get_settings()` cache + `cors_origins_list` /
  `allow_credentials` / `is_production` properties.
- `server.py` now builds the app + CORS from Settings; **CORS hardened** (credentials disabled when origins == `*`).
- `/api/health` is config-driven → `{status, service, version, sprint:2, environment}`.
- Frontend `src/config/index.ts` expanded: env-validated `appConfig`, `apiBase`, `apiUrl()` (trailing-slash safe).
- Added `.env.example` templates (backend + frontend). No secrets hardcoded.
- **Global Light Luxury design tokens** applied (see Design System v2). a11y: `<html lang>` syncs with locale.

### Sprint 1 — Frontend & Backend Foundation ✅ (2026-06, verified 100% backend + frontend)
- Converted frontend to **TypeScript** (tsconfig, index.tsx, App.tsx; removed jsconfig.json/JS entries).
- Locked folder skeletons created (backend: api, core, db, models, schemas, repositories, auth, storage,
  services; frontend: config, i18n, layouts, components/layout, components/common, pages/{public,auth,admin}, constants).
- Routing shell: public (/ /about /verification /catalog /catalog/gemstones /catalog/jewelry /contact),
  /login, /admin → /admin/dashboard, 404.
- Bilingual shell (ID default + EN) via LanguageContext + placeholder locales (no business translations yet).
- Luxury design system applied (fonts, color CSS vars, glass header, hero).
- Backend `GET /api/health` → {status, service, version:0.1.0, sprint:1}.
- Lint/format configured (black/isort/flake8/mypy; ESLint via craco; tsc clean).

---

## Backlog (per Sprint Book, gated)
- **P0 next:** Sprint 5 — Repository Layer Foundation (extend `BaseRepository` into per-domain
  repositories using the Sprint 4 models; CRUD + soft delete + pagination/filter/sort). Only layer touching Mongo.
- Sprint 3 DB layer (Motor + indexes + init) · Sprint 4 domain models (dual-id/audit/versioning) ·
  Sprint 5 repositories · Sprint 6 JWT auth · Sprint 7 RBAC guards · Sprint 8 response envelope ·
  Sprint 9 logging (audit/verification/security) · Sprint 10 storage+media · Sprints 11–30 business modules,
  verification portal, PDFs/QR, ownership, CMS, public site, admin dashboard, analytics, QA/launch.

## Known Notes (deferred)
- server.py uses deprecated `@app.on_event`; migrate to lifespan handler in a later sprint.
- CORS credentialed wildcard to be fixed in Sprint 2/6.
