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
Full spec: `/app/design_guidelines.json`. **Refinement v3 → Royal Editorial (RC1 redesign, 2026-06):**
Pure white / warm-white `#FAF9F6` surfaces, **Deep Navy `#0D1B2A`** text & primary buttons, **Royal Blue
`#1E4FA8`** accent (links/active/charts), **Champagne Gold `#C7A247`** sparing accent, `#E7E7E7` borders,
14px rounded corners, soft shadows, no glassmorphism/gradients. Fonts: Playfair Display + Inter. Editorial
two-column hero (content left, bright diamond photography right). Admin: Deep Navy sidebar + gold active +
white topbar + premium cards. Visual-only; routing/components/API/logic unchanged. (Reference image was not
attached to the job; executed from the detailed written direction.)

---

## Progress Log

### Sprint 7 — RBAC & Authorization Guards ✅ (2026-06, validated via assertion script + API)
- `auth/rbac.py`: `Permission` enum (31 perms), least-privilege `ROLE_PERMISSIONS` matrix for the 4 locked roles
  (SUPER_ADMIN = all implicitly), `permissions_for`/`has_permission`, and guard factories
  `require_roles(...)` / `require_permission(..., require_all=)` layered on `get_current_admin`.
- **Default deny**: unknown role → empty perms; unauthorized → generic **403** (`errors.forbidden`).
- `GET /api/auth/permissions`: RBAC introspection (caller's role + resolved permissions) — no business CRUD/endpoints added.
- Verified allow/deny per role for `require_roles` & `require_permission`, SUPER_ADMIN bypass, invalid-role deny.
- **Hardening revisions:** `JWT_SECRET` has no default (missing → app fails to start); dev seed now requires
  `ADMIN_PASSWORD` from env and aborts if absent (no hardcoded password).

### Sprint 6 — Authentication Foundation ✅ (2026-06, verified 12/12 backend)
- Admin-only JWT auth (Bearer/JSON): `POST /api/auth/login|refresh|logout`, `GET /api/auth/me`.
- **Argon2id** password hashing (`auth/security.py`); hashes never returned.
- Access (15m) + refresh (7d) tokens (`auth/jwt_handler.py`, HS256); **refresh rotation** + server-side
  store (`repositories/auth.py`, `refresh_tokens` collection) → logout & rotation invalidate refresh tokens.
- `get_current_admin` dependency (`auth/dependencies.py`); generic 401 (`errors.py`) — no user enumeration.
- All auth events → `security_logs` (login_success/login_fail/logout/token_refresh); IPs hashed, no secrets.
- Dev-only seed `scripts/seed_admin.py` (SUPER_ADMIN admin@azuris.local; refuses ENVIRONMENT=production).
- JWT settings added to config/.env; `models.enums.SecurityEventType` gained `LOGOUT`.
- No customer/public login, OAuth, email verification, password reset, MFA, or module authorization (Sprint 7).

### Sprint 5 — Repository Layer Foundation ✅ (2026-06, validated against test DB)
- `repositories/domain.py`: generic `DomainRepository[T]` (extends Sprint 3 `BaseRepository`) with model
  translation (from_mongo/to_mongo), create/get_by_uuid/get_by_id, list (pagination+filter+sort),
  update_by_uuid, soft_delete_by_uuid; `AppendOnlyRepository` for logs (update/delete raise).
- Per-domain repositories for all 14 collections (catalog, people, documents, ownership, media, cms, logs).
- `repositories/counter.py` + `counters` unique(name,year) index: **atomic** certificate numbers via
  `find_one_and_update`+`$inc` → `AZR-GEM-YYYY-000001` (never counts docs, never reuses). Verified unique &
  gap-free under 50 concurrent calls.
- Repositories are the only layer touching Mongo. No endpoints/auth/business logic/UI.

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
- **P0 next:** Sprint 8 — Global Error Handling & Response Envelope (unified success/error/validation
  envelopes + middleware; standardized codes; internal errors never leak). Will formalize `errors.py`.
- Sprint 3 DB layer (Motor + indexes + init) · Sprint 4 domain models (dual-id/audit/versioning) ·
  Sprint 5 repositories · Sprint 6 JWT auth · Sprint 7 RBAC guards · Sprint 8 response envelope ·
  Sprint 9 logging (audit/verification/security) · Sprint 10 storage+media · Sprints 11–30 business modules,
  verification portal, PDFs/QR, ownership, CMS, public site, admin dashboard, analytics, QA/launch.

## Known Notes (deferred)
- server.py uses deprecated `@app.on_event`; migrate to lifespan handler in a later sprint.
- CORS credentialed wildcard to be fixed in Sprint 2/6.

## Client Revision — FASE 3.2 (Azuris Logo Integration + Premium Certificate Redesign, 2026-06, validated 11/11 BE + 5/5 FE)
Visual/branding only. NO changes to issuance/verification/counter/numbering/versioning/RBAC/audit/BUSINESS_RULES_LOCK.
- **Logo asset:** official Azuris emblem (transparent gold faceted-gem monogram) autocropped → `frontend/public/azuris-logo.png` + `backend/assets/azuris-logo.png` + faint `backend/assets/azuris-watermark.png` (alpha ~9%). Reusable `frontend/src/components/common/Logo.tsx`.
- **Website logo integration:** Header brand, Footer, Homepage hero (slide 1), Legalitas hero, Login (left panel), Admin sidebar + topbar avatar, and favicon/apple-touch-icon (`public/index.html`). test-ids: azuris-logo, hero-logo, footer-logo, legality-logo, login-logo, admin-logo.
- **Certificate PDF redesign (`services/certificate_pdf.py`):** richer royal-editorial palette — added Beige `#E8DFCF`, Taupe `#B8A58A`, Slate `#5C6F82` alongside Navy/Royal/Gold/Ivory. **Front cover = navy-dominant** (real gold logo, ivory AZURIS + gold GEMOLOGICAL tracked, gold divider, ivory number plate w/ gold border, tone-on-tone gold scallop pattern, double gold frame). **Back cover = ivory** with navy branded header band (logo + wordmark), gold accents, authenticity + 3-step verification, website (royal) + WhatsApp (from centralized settings), gold divider. **Inside pages** = ivory with faint logo **watermark**, **navy section bars with gold accent tab + ivory tracked labels**, **zebra soft-beige field rows**, dotted-gold leaders, gemstone photo in beige mat + gold frame (aspect preserved, collapses cleanly with fewer/no fields), gold-framed QR. Structure LOCKED & re-verified: 2 pages, 148×105mm, fold 74mm, ≥5mm safe.
- **Validation (testing_agent iteration_8):** BE 11/11 (PDF 200/2-page A6, QR decodes to `<base>/?qr=<token>#verification`, manual+QR verify valid, security_code/qr_token never in public responses; regressions verify not_found/settings 6287812128884/legality empty). FE 5/5 logos visible, asset HTTP 200, 0 JS errors, admin redirect OK. MANDATORY cleanup ran → counter restored **last_number=14** (next real number **AZR-GEM-2026-000015**), DB clean (certs=0, gems=0). PUBLIC_BASE_URL still unset → set before first production certificate.


## Client Revision — FASE 3.1 (A6 Certificate Visual Refinement, 2026-06, validated 11/11 backend)
Visual-only refinement of `services/certificate_pdf.py` (+ read-only WhatsApp fetch in the PDF endpoint of
`api/certificates.py`). NO changes to issuance/verification/counter/numbering/versioning/RBAC/audit. BUSINESS_RULES_LOCK.md unchanged.
- Original Azuris visual system: warm-white dominant, champagne-gold **section header bars**, navy typography,
  royal-blue sparingly. New **faceted round-brilliant emblem** (vector, original — no GRA IP), **dotted-leader
  field rows** (label · leader · right-aligned value), subtle **scallop/guilloché security pattern** (low-opacity,
  print-safe), double gold frame, refined front cover (emblem + tracked AZURIS/GEMOLOGICAL + certificate-number
  plate + issue year), refined back cover (light champagne block, authenticity statement, 3-step verification,
  website + centralized WhatsApp from settings, doc version). Inside-left: SERTIFIKAT & VERIFIKASI bar, prominent
  number, meta rows, signature line, disclaimer (moved into mid whitespace — inside safe area), large high-contrast
  QR with quiet zone + instructions. Inside-right: IDENTITAS BATU MULIA bar, gemstone photo (aspect preserved,
  gold frame) with fields wrapping around it, KESIMPULAN PEMERIKSAAN bar; optional fields collapse cleanly (full
  width when no photo). Fonts: standard PDF-safe Times/Helvetica (no brand TTFs in env) — hierarchy via size/weight/
  tracking/caps.
- Structure LOCKED & re-verified: exactly 2 pages, 148×105 mm (419.53×297.64 pt), fold 74 mm, ≥5 mm safe areas,
  outside spread (back-left/front-right), inside spread (info-left/gemstone-right).
- Validation (testing_agent iteration_7, 11/11): PDF 200/application-pdf, 2 pages A6, QR decodes to
  `<base>/?qr=<token>#verification` (pyzbar), manual + QR verify return valid, security_code/qr_token never in public
  responses; regressions green (verify not_found, qr resolve invalid, settings public 6287812128884, legality empty).
  MANDATORY cleanup ran: test cert/gemstone removed, counter restored to **last_number=14** → next real number
  **AZR-GEM-2026-000015**. DB go-live-clean (certs=0, gems=0). PUBLIC_BASE_URL unset → QR uses preview host fallback;
  **set PUBLIC_BASE_URL before first production certificate.**


## Client Revision — FASE 3 (Certificate Issuance + Gemstone + Security Code + QR + A6 PDF, 2026-06, validated 22/22)
Incremental on FASE 1/2. Reused locked atomic counter, existing Certificate/Gemstone/VerificationToken models,
RBAC, audit, base+domain repos. Added deps: `reportlab`, `qrcode[pil]` (PDF+QR; genuinely required). No auth/JWT/
RBAC/counter/numbering/masking changes. No destructive migration. No fake cert/gemstone/owner data left in DB.

### Gemstone entry + certificate issuance (admin)
- `api/certificates.py` (admin_router `/api/admin/...`, public_router `/api/gemstone/...`), `services/issuance.py`,
  `services/security.py`. RBAC `require_roles(ADMINISTRATOR)` (SUPER_ADMIN implicit); CONTENT_MANAGER/unauth blocked.
- Gemstone CRUD: `POST/GET/PUT /api/admin/gemstones`, `POST /api/admin/gemstones/{uuid}/photo` (image ≤8MB, base64 in
  `gemstone_photos`; served publicly at `GET /api/gemstone/photo/{uuid}`; aspect ratio preserved in UI+PDF).
- Issue: `POST /api/admin/certificates/issue {gemstone_id, examiner?, conclusion?, ...}` → atomic number via
  `CounterRepository.next_certificate_number()` (locked `AZR-GEM-YYYY-000001`), creates Certificate(status ISSUED,
  version 1, is_current), generates **security_code** (`gen_security_code`, unambiguous alphabet, NOT derived from
  number) + **opaque QR token** (`secrets.token_urlsafe(32)`), creates VerificationToken, links gemstone
  (status VERIFIED), writes immutable `gemstone_snapshot` on the certificate. Returns number + **security_code shown
  ONCE** + qr_token + qr_url. Duplicate issuance for a gemstone that already has a cert → 409.
- Reissue: `POST /api/admin/certificates/{uuid}/reissue` → version+1, same number, archives old (is_current=false),
  QR token persists (repointed). Revoke: `POST /api/admin/certificates/{uuid}/revoke` → status revoked.

### Certificate numbering / versioning
- Server-side atomic, never computed on FE. Non-reusable (deletes/revokes/archives do NOT free numbers; counter kept
  at 14 after test cleanup). Public verification exposes only the current (is_current) version; archived versions
  restricted. **Index fix:** replaced global-unique `uq_certificate_number` with `uq_certificate_number_version`
  (compound unique number+version) + `uq_certificate_number_current` (partial unique on `is_current:true`) so multi-
  version + single-current is enforced. Reissue rolls back the is_current flip on insert failure (no corrupt state).

### Security code + QR + verification (connected to FASE 2)
- Manual: cert number + security code (exact match) required; wrong pair / malformed → generic `not_found`
  (anti-enumeration + rate limit retained). QR: `GET /api/verify/qr/resolve?token=` → prefill number only (no
  details); `POST /api/verify/qr` → full permitted details only after explicit user action. Security code, QR token,
  and Mongo/internal IDs NEVER returned in public responses. Owner via locked masking (null now — no ownership flow).
- `_build_public_certificate` reads the immutable `gemstone_snapshot` (species/variety/carat/dimensions/shape/cut/
  color/transparency/clarity/treatment/origin/photo_url/conclusion) so historical PDFs/versions never change.

### Digital certificate (frontend)
- `VerificationForm.tsx` renders VALID result with gemstone photo + identity; other statuses show archived/revoked/
  not_found safely. Admin UI `pages/admin/CertificatesPage.tsx` (+/admin/certificates, nav+route): gemstone form +
  photo upload, issue (shows security code once + qr_url), certificate list with Download PDF + Revoke. i18n id/en
  `adminCert.*` added. `lib/api.ts` streams the PDF with auth then opens as blob.

### A6 booklet PDF (`services/certificate_pdf.py`)
- Exactly 2 pages, true A6 landscape 148×105 mm (MediaBox 419.53×297.64 pt — verified via pypdf). Fold at 74 mm,
  ≥5 mm safe margins. Page 1 outside spread (back cover LEFT, front cover RIGHT); Page 2 inside spread (certificate/
  verification info LEFT with large high-contrast QR + number, gemstone identity RIGHT with photo). Snapshot-based.
  Brand fonts unavailable in env → Times/Helvetica embedded (standard) as safe substitutes. QR encodes only the
  opaque verification URL (`PUBLIC_BASE_URL` env, default = preview host).
- **Printing:** A6 Landscape 148×105 mm, duplex, Actual Size / 100% (no Fit-to-Page), flip on SHORT edge for
  landscape duplex, fold vertically at center; page1=outside, page2=inside. Verify back panel not upside-down.

### RBAC / Audit
- All issuance/gemstone/cert mutations server-side RBAC (CONTENT_MANAGER→403, unauth→401, verified). Audit entries
  (append-only) written for gemstone create/update, certificate create/version_create/status_change, pdf generation.

### Go-live status
- **WhatsApp:** actual persisted `/api/settings/public` = **6287812128884** (confirmed against real setting, not the
  prompt); admin-editable at `/admin/settings`; no old placeholder in frontend. **Legalitas CMS:** ready — `{published:
  false}` empty state; real Azuris legal document to be uploaded MANUALLY by admin later (no fake data created).
- **Testing:** testing_agent 22/22 backend green (iteration_6 after fix); frontend E2E verified (login→issue→
  verify→PDF/revoke); `tsc --noEmit` clean. Reusable suite `/app/backend/tests/test_fase3_certificates.py`.

### Known limitations
- No ownership/customer assignment flow → owner_masked null (masking logic present & tested).
- Public gemstone photo endpoint serves any photo doc by uuid (photos are meant to be public; low risk).
- `PUBLIC_BASE_URL` defaults to preview host if env unset — set it for production QR URLs.
- Brand fonts (Playfair/Inter) substituted by Times/Helvetica in PDF (no TTFs in env).
- **BUSINESS_RULES_LOCK.md: UNCHANGED.**

## Client Revision — FASE 2 (Backend Verification + Legality CMS/Admin + WhatsApp Settings, 2026-06, validated)
Incremental on FASE 1. Reused existing FastAPI/Mongo/Pydantic/JWT/RBAC/audit/base+domain repos. No new
dependencies. **No auth/JWT/RBAC/certificate-counter/numbering/owner-masking/version-visibility changes.**
No destructive migration. No fake certificate/gemstone/owner/legality data left in DB.

### Verification (public, real backend)
- `services/verification.py` + `api/verify.py`. Locked priority QR→SecurityCode→Certificate→Gemstone→Owner.
- Manual: `POST /api/verify` requires BOTH certificate_number (regex `^AZR-GEM-\d{4}-\d{6}$`, validated FE+BE) and
  security_code (exact match). Generic non-enumerable outcomes: valid|archived|revoked|not_found. Malformed → not_found.
- QR: opaque token. `GET /api/verify/qr/resolve?token=` returns only `{token_valid, certificate_number?}` (prefill, NO
  details). `POST /api/verify/qr {token}` returns permitted details only after user action. Token/Mongo IDs/security
  codes never in URL or response. Minimal in-memory per-IP rate limiter (20/60s) as anti-enumeration.
- Public response omits empty fields (exclude_none); owner via locked masking (`mask_owner_name`); current version only.
- NOTE: certificate issuance is FASE 3 → no certificates exist yet, so verification legitimately returns not_found
  (real endpoint, no fake success). Success/detail rendering is coded and ready for FASE 3 data.
- VerificationLog written (method, result, masked cert number, sha256(ip)). Security code never returned/logged.

### Legality CMS/Admin
- `models/legality.py` (LegalityCredential + LegalityDocument), `repositories/legality.py`, `api/legality.py`.
- Public: `GET /api/legality` (published only; drafts never public); `GET /api/legality/document/{uuid}` streams bytes
  only when the referenced record is published. Mongo `_id` never exposed (uuid + projected views).
- Admin `/api/admin/legality`: list/create/update/publish/unpublish/delete + document upload (multipart, base64 in
  `legality_documents`, ≤10MB, image/* + pdf). Single published credential (publish unpublishes others).
- Document stored in Mongo (minimal secure storage; no external object storage / no DAM). Served with original bytes
  (aspect ratio preserved in FE viewer; image inline, pdf via iframe).

### WhatsApp business settings (admin-managed, centralized)
- `models/settings.py` (BusinessSettings single-doc `site_settings` key=business), `services/whatsapp.py`, `api/settings.py`.
- Default/canonical number **6287812128884**. Public `GET /api/settings/public`; admin GET/PUT `/api/admin/settings`.
- Normalization: strip spaces/dashes/parens, remove `+`, leading `0`→`62`, reject letters, len 8–15. Verified:
  `08999888777`→`628999888777`, `+62 878-1212-8884`→`6287812128884`, letters→400.
- FE single source of truth: `lib/settings.tsx` `BusinessSettingsProvider`/`useBusiness()` (fallback 6287812128884 in
  ONE place). All public WhatsApp CTA (HomePage contact) read it; admin save → `refresh()` → CTA updates without code
  change. Old placeholder `6281200000000` removed from frontend.

### RBAC (server-side enforced)
- Legality + settings mutations: `require_roles(AdminRole.ADMINISTRATOR)` (SUPER_ADMIN implicitly allowed).
- Verified: unauth→401; CONTENT_MANAGER→403; SUPER_ADMIN→200. CONTENT_MANAGER is **view-would-be** but since no
  field-level restriction architecture exists, it is conservatively restricted from all mutations (spec forbids letting
  it alter critical fields when field-level perms are absent). **Proposed change (not implemented):** field-level perms
  to let CONTENT_MANAGER edit presentation only.

### Audit
- `auth/audit.py` `write_audit_log` → existing append-only `audit_logs`. Records create/update/publish/unpublish/delete/
  document-upload (legality) and settings update, with actor/role/before/after (no secrets). Verified entries written.

### Frontend admin wiring (was placeholder before)
- `lib/api.ts` (token fetch), `lib/auth.tsx` (AuthProvider/useAuth, real `/api/auth/login`, tokens in localStorage,
  `/api/auth/me` bootstrap), `RequireAuth` guard in `App.tsx`. Real `LoginPage`. Admin pages
  `pages/admin/LegalityAdminPage.tsx` (+/admin/legalitas) and `SettingsPage.tsx` (+/admin/settings). AdminLayout nav +
  logout. i18n keys added (id/en): verifyResult, auth, adminNav, adminLegality, adminSettings.
- **API URL fix:** `config.apiUrl()` already prepends `/api`; `lib/api.ts` uses `appConfig.api.baseUrl + path` (path
  already includes `/api`) to avoid double `/api/api` prefix.

### Validated
- Backend curl: verify manual/qr not_found, malformed→not_found, settings default+normalization+letters-400, legality
  draft-not-public→publish→public, RBAC 401/403/200, audit entries, cleanup.
- Frontend screenshots: login→admin legalitas create+publish, public /legalitas shows published + "Terverifikasi dan
  Aktif" badge, settings WA change (08999888777→628999888777) propagates to public contact CTA, manual verify real
  call → "Tidak Dapat Diverifikasi". tsc --noEmit clean.

### Known limitations / pending
- Verification returns not_found until FASE 3 seeds real certificates (by design; no fake data).
- Doc storage is base64-in-Mongo (fine for single legality doc); revisit if large media needed.
- FASE 3 NOT started: certificate issuance + gemstone entry + A6 PDF booklet + QR generation.
- **BUSINESS_RULES_LOCK.md: UNCHANGED.**


Repositioned public site from gemstone catalog/shop → gemological certification & verification platform.
Frontend-only; **no backend/API/DB changes**, no locked business rules changed, no destructive migration,
no fake certificate/gemstone/legality data introduced.
- **Homepage** (`HomePage.tsx` rewrite): hero **carousel with exactly 3 slides** (Empat Pilar Batu Mulia /
  Berlian & Rubi / Safir & Zamrud) via new `components/home/HeroCarousel.tsx` (embla-carousel-react, already
  installed — no new dep): autoplay 6s, prev/next arrows, dots, mobile swipe (embla drag), ArrowLeft/Right
  keyboard, pause on hover/focus, `prefers-reduced-motion` disables autoplay, fixed slide min-height (no layout
  shift). Section order after hero: `#verification` → Proses Sertifikasi (`#proses`) → Mengapa Memilih Azuris →
  Standar Pemeriksaan → Legalitas & Kredibilitas teaser → Hubungi Azuris/WhatsApp (`#kontak`).
- **Verification (primary focus)**: `components/home/VerificationForm.tsx` — No. Sertifikat + Kode Keamanan +
  Verifikasi. Frontend format validation `^AZR-GEM-\d{4}-\d{6}$`. **No backend yet → neutral "Layanan Verifikasi
  Sedang Dipersiapkan" state; NO fake VALID/INVALID.** Single integration point (setTimeout stub) marked for FASE 2.
- **Public catalog removed**: catalog nav/links/product cards/price/WhatsApp-purchase CTA removed from public site.
  Legacy routes redirect (no data/model deleted): `/catalog`, `/catalog/gemstones`, `/catalog/jewelry` → `/`;
  `/verification` → `/#verification`. `CatalogPage.tsx`, `GemstonesPage.tsx`, `JewelryPage.tsx`,
  `VerificationPage.tsx`, `data/sampleGemstones.ts` kept on disk but no longer routed publicly.
- **New public nav** (`Header.tsx` + `Footer.tsx`): Beranda · Verifikasi Sertifikat (`/#verification`) ·
  Proses Sertifikasi (`/#proses`) · Legalitas (`/legalitas`) · Tentang Azuris · Hubungi Kami · ID/EN.
  Homepage hash-scroll effect (respects reduced-motion). Footer dev "Sprint" text replaced with positioning phrase.
- **New page `/legalitas`** (`pages/public/LegalityPage.tsx`): premium certificate-focused layout, hero + CTA
  "Verifikasi Sertifikat Batu" → `/#verification`, **premium empty/placeholder viewer** ("Dokumen Belum
  Dipublikasikan" — no fake doc/number/issuer/status), commitment copy + disclaimer (exact requested copy).
- **i18n**: added `home.slides`, `verify`, `process`, `why`, `standards`, `legalityTeaser`, `contact`, `legality`
  keys + nav (process/legality) to existing ID(default)/EN system (`i18n/locales/id.ts`, `en.ts`). No 2nd i18n system.
- **Copywriting**: certification/verification vocabulary; no price/sale/investment/marketplace claims.
- **testids**: hero-carousel/prev/next/dots, verify.section/form/cert-input/code-input/submit/result,
  legality.page/viewer/cta-verify, nav-process/nav-legality.
- **Validated (screenshots)**: 3 slides + autoplay, EN/ID toggle, catalog+verification redirects, verification
  format-error + neutral unavailable state, /legalitas placeholder, no horizontal overflow, `tsc --noEmit` clean.
- **NOT done (FASE 2/3, awaiting instruction)**: backend verification API + QR opaque token, legality CMS +
  admin `/admin/legalitas` + media/storage, certificate issuance + gemstone entry + A6 PDF booklet + QR.
- **KNOWN LIMITATIONS**: verification & legality not wired to real data until FASE 2/3; WhatsApp contact number
  is placeholder `6281200000000` (replace before launch); screenshot tool enforces 1920px viewport so 360px was
  verified via responsive Tailwind classes + overflow check, not a true 360px render.
- **BUSINESS_RULES_LOCK.md: UNCHANGED.**

## UI Refinements (RC1 — visual only, business logic FROZEN at Sprint 7)
- 2026-06: Sharpened hero marble-vein texture (new Calacatta gold+charcoal image, opacity 90% +
  contrast/saturate boost, softened white gradient) and turned "Preview" into a solid gold button.
- 2026-06: Added DEMO sample gemstone catalog on `CatalogPage.tsx` (frontend only, for client review).
  6 sample stones in `src/data/sampleGemstones.ts` (bilingual name/cut/color/origin, cert numbers
  AZR-GEM-2026-000101..106, no prices). Type filter chips + WhatsApp CTA (wa.me) + per-card verify link.
  Emerald image AI-generated for premium look. New i18n `catalog.*` keys (id/en); testids: catalog-filters,
  catalog-grid, catalog-sample-notice, catalog-filter-<key>, catalog-card-<id>, catalog-whatsapp-<id>,
  catalog-verify-<id>. NOTE: WhatsApp number is a placeholder (6281200000000) — replace before launch.

- 2026-06: HomePage hero redesigned to a balanced two-column editorial layout (copy left, framed
  sapphire image right) — fixes empty/blank left space on ultra-wide screens.
- 2026-06: Added a physical "Preview" button (CTA row + floating card on the image) that opens a
  certificate preview modal showing a generated luxury sample certificate (`CERT_PREVIEW_IMAGE`).
  Modal is a local `useState` overlay (avoids untyped .jsx Dialog in .tsx). New i18n keys:
  home.preview / previewBadge / previewTitle / previewSubtitle. New testids: cta-preview,
  certificate-preview-modal, certificate-preview-image, certificate-preview-close.
