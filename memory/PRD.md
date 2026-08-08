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

### POST-FREEZE — BACKGROUND POSITION/BLUR + SEPARATE LOGIN BACKGROUND (2026-06)
Client follow-up on the Dashboard Background control. No new Sprint/Phase. Production Candidate stays FROZEN. Validated: testing_agent iteration_20 — `tests/test_dashboard_bg.py` 10/10 BE + FE 100%, 0 console errors; freeze preserved (counter 14, collections 0, all bg fields restored to defaults).
- **Reuses the SAME `GET/PUT /api/admin/settings/visuals` + BusinessSettings + media/storage** (no new endpoint/CMS/uploader). New fields on `site_settings`: `dashboard_bg_fit` ('cover'|'center', default cover), `dashboard_bg_blur` (0–12px, default 0); and a mirrored **login** set `login_bg_enabled`/`login_bg_url`/`login_bg_opacity` (4–24)/`login_bg_fit`/`login_bg_blur`. All exposed in public `/api/settings/public`. PUT clamps opacity 4–24, blur 0–12, fit whitelisted to cover/center (loop over both prefixes). RBAC unchanged (CMS_READ/CMS_WRITE; CS read-only 403; unauth 401).
- **Frontend**: `AdminLayout.tsx` overlay now maps fit=center→`background-size:contain` (else cover) and applies `filter: blur(px)` for custom bg. `LoginPage.tsx` gains a full-page `login-bg-overlay` (absolute, behind relative form column) shown only when `login_bg_enabled && login_bg_url`; default login unchanged (hero panel intact). `VisualsPage.tsx`: new shared `BgAppearance` (opacity+fit+blur) used by both Dashboard and the new 'Background Halaman Login' section; media picker refactored to field-based. i18n `adminVisuals.bgFit/fitCover/fitCenter/bgBlur/loginSectionBg/loginBgHint/resetLoginBg` (id/en). testids: `visuals-dashboard-fit/-blur(+-value)`, full `visuals-loginbg-*` set, `login-bg-overlay`.
- No change to analytics/certificate/QR/verification/membership/warranty/ownership/numbering logic. BUSINESS_RULES_LOCK.md UNCHANGED.

### POST-FREEZE — DASHBOARD BACKGROUND CMS CONTROL (targeted visual control, 2026-06)
Client-usability addition. No new Sprint/Phase. Production Candidate stays FROZEN. Validated: testing_agent iteration_19 — new `tests/test_dashboard_bg.py` 9/9 BE + FE 100%, 0 console errors. Freeze preserved (counter last_number=14, business collections 0, site_settings dashboard_bg_* restored to defaults).
- **Reuses existing BusinessSettings + media/storage + visual CMS + the SAME `GET/PUT /api/admin/settings/visuals` endpoint** (no new CMS/uploader/storage/settings endpoint). `models/settings.BusinessSettings` gains `dashboard_bg_enabled` (bool=False), `dashboard_bg_url` (str=''), `dashboard_bg_opacity` (int=10). `api/settings.py`: added to `VisualsUpdate` + `_visuals()` (so also in public `/api/settings/public`); PUT clamps opacity to safe **4–24**. RBAC unchanged (CMS_READ/CMS_WRITE → SUPER_ADMIN/ADMINISTRATOR/CONTENT_MANAGER write, CUSTOMER_SERVICE read-only 403; unauth 401).
- **Frontend `AdminLayout.tsx`**: admin `<main>` overlay (`data-testid=admin-bg-overlay`) reads `useBusiness().visuals`; when `dashboard_bg_enabled && dashboard_bg_url` → custom image via `mediaUrl()` at clamped opacity (0.04–0.24), else the approved **MARBLE default** (mix-blend-multiply, opacity 0.10). Live after Save (no rebuild/redeploy) via BusinessSettingsProvider public-settings load.
- **Frontend `VisualsPage.tsx`**: new 'Background Dashboard' section — enable toggle, reused `ImageControl` (preview/Upload/Choose-from-Media/URL), opacity slider (4–24 with live %), and **Reset ke Background Marble Default**. Picker slot extended to `dashboard`. i18n `adminVisuals.dashboardSection/dashboardHint/bgEnabled/bgOpacity/resetMarble` (id/en). testids: `visuals-dashboard-{enabled,preview,upload,pick,url,reset,opacity}`, `visuals-dashboard-opacity-value`, `visuals-dashboard-reset-marble`.
- No change to analytics/certificate/QR/verification/membership/warranty/ownership/numbering logic. BUSINESS_RULES_LOCK.md UNCHANGED.

### AZURIS PRODUCTION CANDIDATE v2 — PRE-HOSTINGER MIGRATION (Re-Freeze, 2026-06)
Documentation/status only. NO new feature / Sprint / Phase / schema / business-logic change. The current source (including the Certificate Demo Preview added after the v1 freeze) is now the OFFICIAL frozen baseline.
- **Baseline scope (all COMPLETE & retained):** Sprints 1–30 + 23A · FASE 3.1–3.4 · Final UI Polish + CMS Visual Control · CMS Visual RBAC fix (ADMINISTRATOR CMS_WRITE) · CMS Visual Image Picker/Upload UX · **Certificate Demo Preview (UI-only, stateless)** · current Visual & Content implementation.
- **Baseline safety (verified read-only, NO mutation):** `counters.certificate.last_number = 14` → next genuine `AZR-GEM-000015-26`. Business collections genuine = 0 (certificates, gemstones, customers, jewelry, warranties, membership_cards, ownership_transfers, verification_tokens). media collection holds 8 pre-existing CMS docs (unrelated, retained).
- **Demo preview guarantees (re-confirmed):** creates NO certificate/gemstone/customer, NO verification token, does NOT increment the counter, NOT in public verification, NOT counted as an analytics issuance. Stateless endpoint `GET /api/admin/certificates/demo-preview` only.
- **BUSINESS_RULES_LOCK.md UNCHANGED.** Provisional (still NOT locked): Member ID `AZR-MEM-{SEQ6}-{YY}`, Warranty No. `AZR-WTY-{SEQ6}-{YY}` — await client approval.
- **No scope beyond this freeze** (no Preview Data Kustom / download-share / photo mockup / other improvements) unless explicitly requested. Production deployed: NO. Hostinger deployed: NO.

### POST-FREEZE — ADMIN CERTIFICATE DEMO PREVIEW (UI-only, ZERO DB mutation, 2026-06)
Client-usability addition. No new Sprint/Phase. Production Candidate stays FROZEN. Validated: testing_agent iteration_18 — new `tests/test_cert_demo_preview.py` 5/5 BE + FE 100%, 0 console errors. DB baseline verified identical before/after (counter last_number=14, certificates/gemstones/customers/verification_tokens=0).
- **Reuses the EXISTING A6 booklet renderer** (`services/certificate_pdf.build_certificate_pdf`) — no 2nd certificate design. Added `demo: bool=False` param + `_demo_stamp()` which paints a diagonal **DEMO / PREVIEW / NOT VALID** watermark (red 0.40 alpha + faint white halo, legible on navy & ivory panels, design still assessable) on all 4 panels.
- **New stateless endpoint** `GET /api/admin/certificates/demo-preview` (`api/certificates.py`, guard `require_roles(ADMINISTRATOR)`): builds the 2-page PDF from a hardcoded `_DEMO_SNAP` fixture (Natural Sapphire / Corundum / 2.35 ct / Royal Blue / Oval Mixed Cut / 8.20×6.10×4.35 mm / examiner AZURIS GEMOLOGICAL). certificate_number = **`AZR-GEM-DEMO`** (never the genuine next `AZR-GEM-000015-26`); qr_url = inert `"DEMO - NOT VALID"`. NO Mongo access, NO counter increment, NO token/security-code, NO audit write → truly stateless. Unauth → 401.
- **Frontend `CertificatesPage.tsx`**: 'Lihat Contoh Sertifikat' button (`cert-demo-preview-btn`) in the Certificates panel (visible even with 0 certs) → opens modal (`cert-demo-modal`) with an iframe (`cert-demo-iframe`) rendering the demo PDF blob + Open-PDF (`cert-demo-open-pdf`) + Close (`cert-demo-close`). i18n `adminCert.demo*` (id/en). Genuine issuance workflow untouched.

### POST-BATCH D — CMS VISUAL IMAGE PICKER / UPLOAD UX (2026-06)
Targeted client-usability fix. No new Sprint/Phase. No business-logic/certificate/RBAC-matrix change. Validated: testing_agent iteration_17 — `tests/test_cms_visuals_media.py` 16/16 + FE 100%. Baseline restored (media=0, counter=14 → next `AZR-GEM-000015-26`).
- **Reuses Sprint 10 media/storage** (`services/media.store_media` + `media` collection + storage adapter). NEW CMS-scoped endpoints in `api/settings.py`: `POST /api/admin/settings/visuals/media` (guard `CMS_WRITE`, images jpg/png/webp only, ≤15MB, entity_type=`cms`/entity_id=`site`, audited `cms_media`) + `GET /api/admin/settings/visuals/media` (guard `CMS_READ`, picker list). No 2nd media backend/uploader.
- **Frontend `VisualsPage.tsx`**: `ImageControl` (preview + Upload from computer + Choose-from-Media modal + Reset-default + advanced URL field secondary) for Admin Login Image + Certification Process Image. `MediaPicker` modal lists CMS media. Preview updates immediately; fallback image on error; alt ID/EN retained. `lib/api.ts` `mediaUrl()` resolves relative `/api/media/..` to backend base; LoginPage + HomePage use it so uploaded images render after Save. RBAC: write roles (SUPER_ADMIN/ADMINISTRATOR/CONTENT_MANAGER) can upload/select/save; CUSTOMER_SERVICE read-only (backend 403 + frontend controls disabled presentationally).
- testids: `visuals-{login,process}-{upload,pick,reset,file,url,preview}`, `visuals-media-picker`, `visuals-picker-item`.


### AZURIS PRODUCTION CANDIDATE — PRE-HOSTINGER MIGRATION (Freeze, 2026-06)
Current build FROZEN & APPROVED as Production Candidate. No feature/design/schema/RBAC/numbering changes. Not a new Sprint/Phase.
- **Production hygiene:** no seed runs at startup (`server.py` on_startup = Mongo connect + index bootstrap only). `scripts/seed_test_roles.py` + `scripts/seed_admin.py` both `raise SystemExit` when `ENVIRONMENT=production` and never auto-run → test accounts (admin/cm/cs/adminr @azuris.local) will NOT exist in production. Test scripts remain in repo for regression.
- **Test-credential safety:** `/app/memory/test_credentials.md` is dev/test docs only — not referenced by any backend/frontend source, not served via API/frontend. Production admin credentials to be created separately (never reuse test passwords).
- **DB baseline (verified read-only, no mutation):** business collections all 0; `counters.certificate(2026).last_number=14` → next genuine `AZR-GEM-000015-26`. Counter NOT incremented.
- **Export readiness (for future Hostinger migration — NOT deployed now):** Frontend React (`frontend/package.json`), Backend FastAPI (`backend/requirements.txt`), Mongo index init (`db/indexes.py` via `init_database()`), media/storage via `STORAGE_BACKEND` (default `mongo`), env templates (`backend/.env.example`, `frontend/.env.example`), production config docs (`docs/PRODUCTION_READINESS.md`). No real secrets in repo. No Dockerfile/compose yet — to be authored at migration time (documented, not a current blocker).
- **Provisional (unchanged, not locked):** Member ID `AZR-MEM-{SEQ6}-{YY}`, Warranty No `AZR-WTY-{SEQ6}-{YY}` — await client approval. BUSINESS_RULES_LOCK.md UNCHANGED. Deployment performed: NO.


### POST-BATCH D — CLIENT-APPROVED FINAL UI POLISH + CMS VISUAL CONTROL (2026-06)
Not a new Sprint/Phase. Blueprint Sprint 1–30 + 23A stay COMPLETE. BUSINESS_RULES_LOCK.md UNCHANGED. Certificate format LOCKED `AZR-GEM-{SEQ6}-{YY}`, counter last_number=14 → next `AZR-GEM-000015-26`. Business collections baseline=0 held. Validated: testing_agent iteration_14 — new `tests/test_cms_visuals.py` 14/14 + FE 100%.

**CMS Visual Controls (audited → EXTENDED minimally on existing Settings resource; no 2nd CMS/uploader):**
- Backend: `BusinessSettings` (collection `site_settings`) extended with visual fields (login image url+alt id/en, process image url+alt id/en+show, homepage membership show/title/desc/cta id-en/link). `api/settings.py`: public `GET /api/settings/public` now returns visuals; admin `GET/PUT /api/admin/settings/visuals` guarded by permissions `CMS_READ`/`CMS_WRITE` (SUPER_ADMIN + ADMINISTRATOR + CONTENT_MANAGER write; CUSTOMER_SERVICE read-only). RBAC fix (2026-06): added `Permission.CMS_WRITE` to the ADMINISTRATOR frozenset (`auth/rbac.py`) — matches blueprint "ADMINISTRATOR = operational full except admin-account management"; existing permission architecture reused, no new role/hardcoded check. Verified testing_agent iteration_15 (19/19). New ADMINISTRATOR test account `adminr@azuris.local`. Mutations audited (entity_type `cms_visuals`). No secrets/PII exposed.
- Frontend: new `pages/admin/VisualsPage.tsx` (`/admin/visuals`, nav item `admin-nav-visuals`) — 3 sections (Admin Login Image, Certification Process Image, Homepage Membership) with previews + MASKED membership card preview. `lib/settings.tsx` exposes `visuals`. LoginPage image now CMS-driven. HomePage: process image + NEW membership showcase (reuses Sprint 23A `MembershipCardVisual`, masked `Andi Pra****` / `AZR-MEM-••••••-26`, CTA → /membership). i18n `homeMembership.*` + `adminVisuals.*` (id/en).

**4 design-system polish changes (NOT admin-editable):**
1. Dashboard marble veining refined — subtle marble overlay added to admin `<main>` (opacity ~0.10, contrast 1.25, mix-blend-multiply); readability preserved.
2. Admin sidebar logo reduced ~15% (40px → 34px), aspect/sharpness kept.
3. Admin brand→nav breathing space (brand `mb-10` + nav hairline `border-t` + `pt-8`).
4. Public navigation premium border — champagne-gold (#C7A247) 1px borders, transparent bg, subtle hover tint, warm active tint, compact radius; mobile menu gets simpler bordered version.

**Visual proof (public desktop only via preview tool):** Homepage desktop, bordered nav, certification-process CMS image, homepage membership (masked), CMS login image, membership portal — all captured. Admin Dashboard (marble/logo/spacing) + CMS Visuals page are auth-gated: the preview screenshot tool captures only the unauthenticated `page_url` load, so these were verified functionally by testing_agent iteration_14 (real login + rendering + masked identity + data-testids), not directly screenshot-capturable. No business logic/DB rule changed.


### BATCH D — CMS / Public / Analytics / QA / Security / Performance / Production / Launch (Sprints 24–30) ✅ (2026-06, validated: testing_agent iteration_13 — new `tests/test_batch_d_analytics.py` 10/10; combined authoritative gate 84/84 = batch_d 10 + A 22 + B 32 + C 20; FE dashboard render + public smoke pass; DB baseline held)
Fast-track, REUSE-FIRST, blueprint-first. No locked rule touched; BUSINESS_RULES_LOCK.md UNCHANGED. Certificate format LOCKED `AZR-GEM-{SEQ6}-{YY}`. DB baseline held (all business collections=0, counter.last_number=14 → next real cert `AZR-GEM-000015-26`). Full report: `/app/docs/PRODUCTION_READINESS.md`.

**Sprint 24 — CMS → SATISFIED EARLY.** Legality CMS (`/admin/legalitas`, draft/publish + document upload) + Business Settings (`/admin/settings`, WhatsApp) + Media library (Sprint 10/14) + bilingual i18n content. Reuses RBAC/audit/envelope/media. No page-builder (not in PRD).

**Sprint 25 — Public Website → SATISFIED EARLY.** HomePage (3-slide hero, verification, process, why, standards, legality teaser, contact), About, Contact, Legalitas, `/membership` portal. Public Catalog stays DISABLED (approved client revision — `/catalog*` redirect to `/`). Positioning = examination/identification/documentation/certification/verification (NOT marketplace).

**Sprint 26 — Public Verification + Legalitas + Bilingual → SATISFIED EARLY.** Manual (cert# + security code) + QR (opaque token) + signed preview token; latest-version visibility; format `AZR-GEM-{SEQ6}-{YY}`. Legalitas clean placeholder when no document published. Full ID/EN.

**Sprint 27 — Analytics + Admin Dashboard → COMPLETE (NEW).** `services/analytics.py` (`build_overview`, soft-delete-aware aggregations, privacy-safe) + `api/analytics.py` (`GET /api/admin/analytics/overview`, guard `require_permission(ANALYTICS_READ)` → SUPER_ADMIN + ADMINISTRATOR only; CONTENT_MANAGER/CUSTOMER_SERVICE → 403; unauth → 401). Returns ONLY aggregates: totals (9 collections), *_by_status (gemstones/certificates/warranties/transfers/memberships), verification {total, by_result, 14-day series}, admin_activity {by_action, 30d}, certificate_counter {last_number, next_number}. No PII, no secrets (security_code/qr_token/preview_token/password_hash), no ObjectId. FE `DashboardPage.tsx` (replaces coming-soon placeholder): metric cards + recharts verification-trend LineChart + status breakdown bars + navy next-certificate panel + refresh. i18n `admin.dash.*` (id/en). testids `admin-dashboard`/`dash-refresh`/`dash-metrics`/`dash-verify-chart`/`dash-loaded`. Router registered in `server.py`.

**Sprint 28 — QA → COMPLETE.** testing_agent iteration_13: 84/84 combined (per-file, hermetic). Analytics structure/RBAC/privacy verified; FE dashboard renders (all testids, next-cert `AZR-GEM-000015-26`, i18n, 0 errors); public smoke (/ 3-slide, /legalitas placeholder, /membership, /catalog→/ redirect); public verify + membership verify return generic outcomes without leaking secrets.

**Sprint 29 — Security QA + Performance QA + Responsive/A11y → COMPLETE.** JWT/Argon2id/refresh-rotation/default-deny RBAC; generic 401/403; secret/PII/ObjectId never returned; enumeration-safe verifies + per-IP rate limit (20/60s); IDOR-safe (token/RBAC-gated, public media = PUBLIC-only); safe 500 envelope + server-only stack + X-Request-ID correlation. Perf: `count_documents` + light `$group` over indexed soft-delete-aware collections, bounded 14-day series, paginated lists, raw-bytes media/PDF/preview (preview cached). Responsive breakpoints (360/390/768/1024/1440) + a11y audited via responsive classes/prior batches. Findings: no blockers.

**Sprint 30 — Production Config + Launch Readiness → READY WITH BLOCKERS.** `backend/.env.example` completed with production guidance (CORS_ORIGINS, JWT_SECRET, ADMIN seed, PUBLIC_BASE_URL, STORAGE_BACKEND) — no real secrets. `docs/PRODUCTION_READINESS.md` = sprint status, QA/security/perf summary, PRE-LAUNCH CLIENT DECISIONS, blueprint audit. No deploy / DNS / genuine data / legal upload performed.

**PRE-LAUNCH CLIENT DECISIONS / BLOCKERS:** (1) **PUBLIC_BASE_URL / official domain — PRODUCTION BLOCKER** (QR + membership URLs; preview-host fallback in `services/issuance.py`; do NOT guess); (2) Member ID `AZR-MEM-{SEQ6}-{YY}` — PROVISIONAL, client approval before lock; (3) Warranty No. `AZR-WTY-{SEQ6}-{YY}` — PROVISIONAL, client approval before lock; (4) genuine legality document upload (placeholder until then); (5) production secrets/config (real JWT_SECRET, MONGO_URL, explicit CORS_ORIGINS, ENVIRONMENT=production). **Production status: READY WITH BLOCKERS.**

**Visual proof (screenshot_tool = public desktop pages only; auth-gated/mobile/post-interaction not capturable by this tool):** Homepage desktop ✅, Legalitas placeholder ✅, Membership portal safe-state ✅. Admin dashboard/analytics + certificate-verification-success functionally verified by testing_agent iteration_13 (real login + rendering + values), not directly screenshot-capturable via the preview tool.


### BATCH C — Certification / Post-Certification / Ownership + 23A Membership (Sprints 15–23 + 23A) ✅ (2026-06, validated: hermetic `tests/test_batch_c_regression.py` 20/20; A 22/22, B 32/32, FASE3 certs 22/22, FASE3.4 16/16 — all serial `-n0`; FE smoke pass)
Fast-track, REUSE-FIRST, no locked rule touched. Certificate numbering/counter/QR/verification/security_code/owner-masking/versioning/PDF/auth UNCHANGED. BUSINESS_RULES_LOCK unchanged (no blocker). Public Catalog stays disabled. DB restored to baseline (all business collections=0, counter.last_number=14 → next real cert AZR-GEM-000015-26).

**Sprints 15–18 — Certification** → **SATISFIED EARLY** (verified by regression). Certificate Management, Issuance, Atomic Numbering (`AZR-GEM-{SEQ6}-{YY}`), Versioning, A6/Premium PDF + Logo, QR + Opaque Token + Security Code, Manual + Public Verification, Preview — all built in RC1 + FASE 3.1–3.4. Not rebuilt; re-validated (issuance, manual verify, QR verify, security-code rotation) inside the Batch C suite + FASE cert suites.

**Sprint 19 — Warranty** (`api/warranties.py`, NEW; `/api/admin/warranties`). Reuses Sprint 4 `Warranty` model + Sprint 5 `WarrantyRepository` + versioning spine + audit + RBAC. Lifecycle active→(expired|void), no reactivation; reissue = new version (same number). One active warranty per stone. Auto number `AZR-WTY-{SEQ6}-{YY}` from a SEPARATE `warranty` counter (cert counter untouched). Derives end_date from start_date+period_months. RBAC WARRANTY_READ/WRITE/DELETE.

**Sprints 20–22 — Ownership + History + Transfer** (`api/ownership.py` + `services/ownership.py`, NEW; `/api/admin/ownership`). Authoritative Customer↔Gemstone ownership via `gemstone.active_owner_id` + `customer.owned_gemstone_ids`. `assign` sets FIRST owner only (already-owned→409, must use transfer). Transfer workflow: pending→completed|cancelled, one pending/stone, validates asset/recipient/role, prevents same-owner. **Completion is the ONLY path that mutates ownership**: sets gemstone status=transferred + new owner, ROTATES security code (QR/token stable, logged SECURITY_CODE_REGENERATION), returns new code once. History = append-only completed transfers + audit; no destructive overwrite. Ownership NEVER changes from verification/QR/security-code. No contact PII exposed. RBAC OWNERSHIP_READ/WRITE.

**Sprint 23A — Membership Card** (`api/membership.py` + `services/membership.py` + FE `MembershipCardVisual`, NEW; admin `/api/admin/membership`, public `/api/membership/verify` + `/api/membership/qr`). Premium identity card (NOT payment/loyalty). Requires existing customer WITH consent (else 400). Masked identity only (locked masking), no PII/secrets. Member ID `AZR-MEM-{SEQ6}-{YY}` from SEPARATE `membership` counter — DISTINCT from cert number; format is a PROVISIONAL operational default documented here only (NOT in BUSINESS_RULES_LOCK). Versioning + status active/inactive + reissue + soft delete. Signed member-verify token (type `membership_verify`, distinct from cert QR); public token-gated member-safe verification + QR PNG (qrcode). Anti-enumeration; inactive/revoked → invalid. RBAC MEMBERSHIP_READ/WRITE (CONTENT_MANAGER has none; CUSTOMER_SERVICE read-only). FE: `/admin/membership` list/create/status/reissue + digital card modal (front/back, QR); public `/membership?t=` verify portal.

**Frontend (BATCH C):** `WarrantiesPage.tsx`, `OwnershipPage.tsx`, `MembershipPage.tsx`, `public/MembershipVerifyPage.tsx`, `components/membership/MembershipCardVisual.tsx`; routes + sidebar nav (Garansi/Kepemilikan/Kartu Anggota) + testIds + i18n (id/en). Brand: Deep Navy #0D1B2A, Champagne Gold #C7A247.


### BATCH B — Core Domain Modules (Sprints 11–14) ✅ (2026-06, validated: testing_agent iteration_12, BE 32/32 + FE 100%, 0 issues)
Fast-track master roadmap. Executed sequentially (no approval gate inside batch). REUSE-FIRST: extended existing models/schemas/repositories/audit/RBAC; no locked rule touched; certificate numbering/counter/QR/verification/security_code/owner-masking/versioning/PDF design/auth UNCHANGED. DB stayed production-clean (customers=0, gemstones=0, jewelry=0, media=0, media_objects=0, certs=0, counter.last_number=14 → next real cert AZR-GEM-000015-26).

**Sprint 11 — Customers** (`api/customers.py`, NEW; router `/api/admin/customers`)
- Admin owner registry (foundation for Ownership → Ownership Transfer → Membership Card; those NOT built now). CRUD: GET list `?page=&page_size=&q=` (regex search full_name/email/phone), GET `/{uuid}`, POST, PUT `/{uuid}`, DELETE `/{uuid}` (soft delete). Reuses `repositories/people.CustomerRepository` + existing `Customer` model/schema.
- **RBAC (permission-based, matches locked matrix):** read=`CUSTOMER_READ`, write=`CUSTOMER_WRITE`, delete=`CUSTOMER_DELETE`. CONTENT_MANAGER write→403; CUSTOMER_SERVICE write→OK, delete→403; unauth→401.
- **Consent history:** `consent_at` auto-stamped once when `privacy_consent` first becomes true (create or PUT false→true). No public customer endpoint; contact/PII never public, never logged. Responses whitelist fields (no Mongo `_id`). All mutations audited (Sprint 9 correlation-aware writer).

**Sprint 12 — Gemstones** (extended in `api/certificates.py`, non-breaking; reuses existing `GemstoneRepository`)
- Enhanced `GET /api/admin/gemstones` → `?page=&page_size=&status=&q=` returning `{items,total,page,page_size}`; read guard now `GEMSTONE_READ` (CM/CS may read). Added `GET /api/admin/gemstones/{uuid}` (view now exposes `media_ids`).
- `POST /api/admin/gemstones/{uuid}/status` — locked lifecycle transitions (draft→verified→published→transferred→published, any→archived, archived→published); invalid → 409 CONFLICT. `DELETE /api/admin/gemstones/{uuid}` — soft delete; blocked (409) if `certificate_id` set (issued certificate). Guards: status=`GEMSTONE_WRITE`, delete=`GEMSTONE_DELETE`. Audited.

**Sprint 13 — Jewelry** (`api/catalog.py`, NEW; router `/api/admin/jewelry`; reuses `repositories/catalog`)
- Data/certification domain (NOT marketplace; public catalog stays disabled). CRUD: GET list `?page=&page_size=&status=&q=`, GET `/{uuid}`, POST (validates `gemstone_ids` resolve → else 400), PUT (re-validates), `POST /{uuid}/status` (draft→published→archived, archived→published; invalid → 409), DELETE (soft).
- **RBAC:** read=`JEWELRY_READ`, write=`JEWELRY_WRITE`, delete=`JEWELRY_DELETE`. CM write→403; CS read→200, write→403. Audited (association changes recorded).

**Sprint 14 — Media Domain Wiring** (extended `api/media.py`; reuses Sprint 10 storage adapter — no second uploader)
- Authoritative media↔entity link stays on the media doc (entity_type+entity_id); `entity.media_ids` maintained as a denormalized cache for gemstone/jewelry. Upload with entity gemstone/jewelry → appends media uuid to `media_ids`; `role=main` demotes any existing main (single-main per entity, §8). `POST /api/admin/media/{uuid}/main` promotes + demotes others. `DELETE` unlinks from `media_ids`. Public/private visibility, RBAC (ADMINISTRATOR), audit preserved.
- **Certificate compatibility-safe:** legacy `gemstone_photos` + certificate PDF/preview UNCHANGED. Legacy `POST /api/admin/gemstones/{uuid}/photo` now PREPENDS the examination photo (keeps it at `media_ids[0]` for the certificate snapshot) while preserving Sprint-10 gallery links.

**Test roles:** `scripts/seed_test_roles.py` (dev-only, refuses production) seeds `cm@azuris.local`/CmDev@2026! (CONTENT_MANAGER) + `cs@azuris.local`/CsDev@2026! (CUSTOMER_SERVICE). **Admin UI:** new pages `pages/admin/{CustomersPage,GemstonesPage,JewelryPage}.tsx` + routes (`/admin/customers|gemstones|jewelry`) + AdminLayout nav; i18n id/en (`adminCustomers`/`adminGemstones`/`adminJewelry`); testids. `tsc --noEmit` clean.
- **Validation (testing_agent iteration_12):** BE 32/32 (`tests/test_batch_b_regression.py`, hermetic/self-cleaning), FE 100% (login + 3 pages render + create/delete). Authoritative regression gate now = Batch A (22) + Batch B (32) = **54 tests**, run per-file (`pytest tests/test_batch_a_regression.py`, `pytest tests/test_batch_b_regression.py`) — NEVER whole `tests/` (legacy FASE suites non-hermetic). Baseline restored: all business collections 0, counter.last_number=14.


### BATCH A — Platform Infrastructure (Sprints 8–10) ✅ (2026-06, validated: 97/97 per-suite green incl. new envelope suite 22/22)
Fast-track master roadmap. Executed sequentially; no scope reduced, no locked rule changed, DB stayed production-clean (certs=0, gems=0, media=0, counter.last_number=14 → next real cert AZR-GEM-000015-26).

**Sprint 8 — Global Error Handling & Response Envelope**
- Formalized `errors.py`: `ErrorCode` (stable codes: BAD_REQUEST/UNAUTHORIZED/FORBIDDEN/NOT_FOUND/METHOD_NOT_ALLOWED/CONFLICT/VALIDATION_ERROR/RATE_LIMITED/SERVICE_UNAVAILABLE/INTERNAL_ERROR), `STATUS_CODE_MAP`, envelope builders `success_envelope`/`error_envelope`, `ApiError` (coded HTTPException), backward-compatible `unauthorized`/`forbidden`.
- `core/envelope.py`: `install_envelope()` wires (a) `ResponseEnvelopeMiddleware` — wraps successful JSON `/api` responses as `{success:true,data,meta:{request_id}}`; EXCLUDES `/api/health`, error responses (>=400), and non-JSON media (PDF/PNG/image serves stay raw bytes); (b) exception handlers → standardized error envelope `{success:false,error:{code,message,details?},meta}`; validation 422 maps `details:[{field,message,type}]`; unhandled 500 = safe INTERNAL_ERROR (stack logged server-side ONLY, never leaked).
- **Frontend adapter (no breaking change):** `lib/api.ts` gains `unwrap()` + `ApiError`; `apiJson` now returns unwrapped `data`; direct `.json()` sites (auth login, admin settings save, verification form) route through `unwrap`. Public verification anti-enumeration + generic outcomes unchanged.

**Sprint 9 — Logging Infrastructure** (append-only audit/verification/security existed from RC1/FASE → **SATISFIED EARLY**; the net-new deliverable is correlation)
- `core/context.py`: request-id `ContextVar`. `RequestContextMiddleware` (pure-ASGI, reliable ContextVar propagation) mints/echoes `X-Request-ID` and exposes it via `request.state`.
- All three writers now stamp `correlation_id = get_request_id()`: `auth/audit.py` (audit_logs), `auth/security_logs.py` (security_logs), `services/verification.py` (verification_logs). Verified end-to-end: a client `X-Request-ID` flows into the persisted log rows. No secret/PII leakage; IPs sha256-hashed; cert numbers masked; append-only enforced (`AppendOnlyRepository`).

**Sprint 10 — Object Storage Adapter & Media Metadata**
- Vendor-neutral `storage/base.py` `StorageAdapter` ABC + locked key layout `media/{entity_type}/{entity_id}/{role}/{uuid}.{ext}`; default `storage/mongo_adapter.py` (binaries in `media_objects`, persistent, no external creds); `storage/factory.py` selects backend via `STORAGE_BACKEND` env (default `mongo`, no hardcoded vendor).
- `services/media.py`: `store_media`/`get_media_binary`/`delete_media` — ties binary (adapter) to metadata (`media` collection), enforces 15MB + type whitelist (jpeg/png/webp/pdf), captures dimensions via PIL. `models/media.py` gains `visibility` + `storage_key`; new `MediaVisibility` enum.
- `api/media.py`: admin `/api/admin/media` (POST upload multipart, GET list by entity, DELETE soft-delete+object removal, GET `/{uuid}/raw` serve any) — RBAC ADMINISTRATOR (CONTENT_MANAGER→403); public `/api/media/{uuid}` serves PUBLIC only (private/missing/deleted → generic 404, no leak). Audit logged on create/delete.

**Validation (testing_agent iteration_11 + per-suite):** Batch A regression suite `tests/test_batch_a_regression.py` 22/22. Per-suite green in isolation: health 4, sprint3_db 4, sprint6_auth 12, fase3_1 11, fase3_3 17, fase3_4 16, fase3_certificates 22, batch_a 22. Legacy suites migrated to unwrap the envelope (`J()` helper) + stale `sprint==3` assertions relaxed. **Known test-infra note:** the legacy FASE E2E suites are non-hermetic (shared certificate counter + `asyncio.get_event_loop()` reuse) so a single combined `pytest tests/` run shows cross-suite counter drift — run them one file at a time (as iterations 7–11 do); batch_a is hermetic/self-cleaning and is the authoritative gate. Test-only system libs installed for fase3_1 QR-decode: `libzbar0`, `poppler-utils` (NOT app runtime deps — app rasterizes via PyMuPDF).



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
- **P0 next (BATCH D — CMS / Public / Analytics / QA / Production / Launch, Sprints 24–30):** (BATCH A / Sprints 8–10 = COMPLETE; **BATCH B / Sprints 11–14 = COMPLETE 2026-06**; **BATCH C / Sprints 15–23 + 23A Membership = COMPLETE 2026-06**.)
- Sprint 3 DB layer (Motor + indexes + init) · Sprint 4 domain models (dual-id/audit/versioning) ·
  Sprint 5 repositories · Sprint 6 JWT auth · Sprint 7 RBAC guards · Sprint 8 response envelope ·
  Sprint 9 logging (audit/verification/security) · Sprint 10 storage+media · Sprints 11–30 business modules,
  verification portal, PDFs/QR, ownership, CMS, public site, admin dashboard, analytics, QA/launch.

## Known Notes (deferred)
- server.py uses deprecated `@app.on_event`; migrate to lifespan handler in a later sprint.
- CORS credentialed wildcard to be fixed in Sprint 2/6.

## Client Revision — FASE 3.4 (Certificate Number Format + Compact Number Plate, 2026-06, validated 44/44 BE + FE)
FINAL client revision before resuming the master roadmap. NO other business rule changed.
- **Number format (CLIENT-APPROVED business-rule revision):** OLD `AZR-GEM-YYYY-000001` (e.g. `AZR-GEM-2026-000015`)
  → NEW **`AZR-GEM-000001-YY`** (e.g. `AZR-GEM-000015-26`). 6-digit sequence + 2-digit issue year. Reason: Client
  Approved Certificate Number Format Revision — FASE 3.4. Recorded in `BUSINESS_RULES_LOCK.md` (Section A) with old→new
  + reason; every other locked rule (atomic counter, non-reuse, immutability, verification priority, QR opaque token,
  security code, versioning, owner masking, RBAC, audit, auth, visibility) UNCHANGED.
- **Backward compatibility:** DB had 0 issued certificates at revision time → new format applies from next issuance
  (`AZR-GEM-000015-26`). Historical numbers (if any existed) remain immutable; no auto-rename.
- **Single source of truth updated everywhere:** `repositories/counter.py` (generator), `api/verify.py` CERT_RE
  `^AZR-GEM-\d{6}-\d{2}$`, PDF front cover + inside spread + preview (shared `_panel_front`), admin list, manual/QR
  verify, i18n placeholder/formatError (id+en), HomePage example chip, and display-only `sampleGemstones.ts` (disabled
  catalog) — no old-format string remains.
- **Compact number plate:** front-cover plate reduced (38×9.5mm, number font 8.5, label 3.4, 0.5 gold border) so the
  serial reads like a luxury plaque and does NOT dominate `AZURIS`. Cover hierarchy preserved: Logo → AZURIS →
  GEMOLOGICAL → Gemological Certificate → Sertifikat Gemologi → Nomor Sertifikat → Tahun Terbit. Rest of FASE 3.2/3.3
  design untouched; 2-page A6 148×105mm + QR + preview intact.
- **Validation (testing_agent iteration_10):** BE **44/44** (counter unit incl. 20-concurrent atomicity + 6-digit seq +
  2-digit year; reissue keeps same number & does not re-increment; issuance/PDF/list/DB/manual+QR/preview all show
  `AZR-GEM-000015-26` with ZERO old-format occurrences; old-format input → generic not_found; RBAC/audit/versioning +
  FASE 3.1/3.3 regressions green). FE 100% (new placeholder, rejects old format, accepts new). New suite
  `tests/test_fase3_4_number_format.py`; old suites updated to new format. MANDATORY cleanup → counter restored
  **last_number=14** → next real number **AZR-GEM-000015-26**; DB clean (certs=0, gems=0).

## Roadmap / Blueprint Ledger (additive — nothing removed)
- **Sprint status:** Sprints 1–23 + 23A = COMPLETE (RC1 FROZEN; **BATCH A / 8–10 DONE**; **BATCH B / 11–14 DONE**; **BATCH C / 15–23 + 23A Membership DONE 2026-06**). **NEXT DEVELOPMENT = BATCH D — Sprints 24–30** (CMS / Public / Analytics / QA / Production / Launch), strictly in order (no skipping). Client revisions FASE 3.1→3.4 were interleaved and are all COMPLETE.
- **FASE ledger (do not merge/overwrite):** FASE 3.1 A6 Visual Refinement (COMPLETE) · FASE 3.2 Logo + Premium Redesign
  (COMPLETE) · FASE 3.3 Public Verification Front-Cover Preview (COMPLETE) · FASE 3.4 Number Format + Compact Plate (COMPLETE).
- **Membership Card:** ORIGINAL requirement (present since Sprint 3 bootstrap list; carries VersionMixin). Original PRD had
  NO dedicated sprint number → assigned additive slot **SPRINT 23A — MEMBERSHIP CARD** (FUTURE), WITHOUT shifting Sprints
  1–30. Dependency chain to honor: Customers → Ownership → Ownership Transfer → Membership Card. Scope retained for when
  its phase arrives: Azuris Membership Card, member identity + unique member id, linkage to customer/owner, membership
  status, issue date, digital card, physical-card-ready design (if in original PRD), QR/verification (if in original PRD),
  admin management, member-safe visibility, RBAC, audit history. Status: FUTURE (not built in FASE 3.4).
- **Public Catalog:** Removed from active public scope by approved client revision (routes redirect); historical blueprint
  RETAINED (status: CLIENT REVISED — do not re-enable). Sample catalog data kept for reference only.
- **Blueprint Completeness Audit (all retained, statuses):** FOUNDATION (Frontend/Backend/Config/MongoDB/Models/Repository/
  Auth/JWT/Refresh Token/Argon2id/RBAC) = COMPLETE. PLATFORM (Global Error Handling=NEXT Sprint 8, Response Envelope=NEXT,
  Audit/Verification/Security Logging=FUTURE Sprint 9, Object Storage/Media Metadata=FUTURE Sprint 10). DOMAIN
  (Customers/Gemstones/Jewelry/Media)=partially scaffolded/FUTURE. CERTIFICATION (Certificate Mgmt, Issuance, Versioning,
  PDF, Physical A6, QR, Verification Token, Manual Verification, Digital Certificate, Public Verification, Certificate
  Preview)=COMPLETE (RC1 + FASE 3.1–3.4). POST-CERTIFICATION (Warranty, Ownership, Ownership Transfer=FUTURE; Membership
  Card=FUTURE Sprint 23A). CONTENT/PUBLIC (CMS, Homepage, Legalitas, Contact, WhatsApp handoff, ID/EN bilingual)=COMPLETE/
  ongoing. OPERATIONS (Analytics, QA, Security QA, Performance QA, Production Config, Launch)=FUTURE. No Sprint 1–30 removed.


## Client Revision — FASE 3.3 (Public Verification Certificate Front-Cover Preview, 2026-06, validated 17/17 BE + FE full)
Adds a real "Pratinjau Sertifikat" (front cover) to public verification results. Rendered from the SAME generator as the
booklet (single source of truth). NO changes to issuance/verification logic/QR/opaque token/security code/numbering/
counter/versioning/RBAC/audit/BUSINESS_RULES_LOCK.
- **Single source of truth:** `services/certificate_pdf.py` gains `build_front_cover_pdf()` (1-page 74×105mm reusing the
  exact `_panel_front()` renderer) + `render_front_cover_png()` (rasterized via **PyMuPDF** — self-contained wheel, no
  system poppler). Any future front-cover design change propagates to both PDF and preview automatically.
- **Capability token:** `services/preview.py` `create/decode_preview_token` — signed JWT (HS256, JWT_SECRET), `type=cert_preview`,
  20-min TTL, payload ONLY `{sub=cert.uuid, ver, type, iat, exp}` (no security_code / qr_token / owner / ObjectId). Minted
  inside `_build_public_certificate` (try/except → never breaks verification) and returned as `certificate.preview_token`.
- **Public endpoint:** `GET /api/verify/preview?t=<token>` → `image/png` + `Cache-Control: public, max-age=900, immutable`.
  Gated by the token (no enumeration; sequential numbers can't be probed). 404 on bad/expired token OR non-current/revoked
  cert (current-version visibility enforced — archived tokens 404 after reissue). 503 on render failure. Reuses per-IP
  rate limiter (20/60s). No new secrets, no ObjectId, no bypass of manual/QR verification.
- **Frontend (`VerificationForm.tsx`):** premium **2-column** valid result (desktop) — left `PreviewCard` (ivory + gold
  border, aspect 74/105, skeleton, zoom cursor, `object-contain`) using `/api/verify/preview?t=`; right = Basic Info /
  Gemstone / Result / Owner + gemstone photo + **"Lihat Sertifikat Digital"** opening a fullscreen viewer modal. **Mobile**
  stacks status→preview→info→details→button, no overflow. **Graceful fallback** (`verify-preview-fallback`) when image fails,
  details still render. i18n id/en keys added (certificatePreview/verifiedCertificate/viewDigitalCertificate/previewUnavailable
  + section labels). test-ids: verify-preview, verify-preview-image, verify-preview-fallback, verify-view-digital,
  verify-viewer-modal, verify-viewer-close.
- **Validation (testing_agent iteration_9):** BE 17/17 (preview 200 image/png + cache header; JWT payload minimal; reissue →
  v2 previewable, v1 archived token 404; bad token 404; fake verify → no preview_token; secrets/ObjectId never leaked;
  verify independent of preview failures; counter untouched by verification). FE: desktop 2-col + mobile stacked (no
  overflow) + viewer modal + fallback + ID/EN, 0 console errors. MANDATORY cleanup → counter restored **last_number=14**
  (next real number **AZR-GEM-2026-000015**), DB clean (certs=0, gems=0, vtokens=0). `pymupdf` added to requirements.
  `BUSINESS_RULES_LOCK.md` UNCHANGED.


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
