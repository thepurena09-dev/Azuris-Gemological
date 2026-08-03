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

---

## Progress Log

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
- **P0 next:** Sprint 2 — Configuration & Environment Layer (Pydantic Settings, CORS hardening,
  frontend config/, .env templates). Note: revisit `CORS_ORIGINS='*'` + `allow_credentials=True` here.
- Sprint 3 DB layer (Motor + indexes + init) · Sprint 4 domain models (dual-id/audit/versioning) ·
  Sprint 5 repositories · Sprint 6 JWT auth · Sprint 7 RBAC guards · Sprint 8 response envelope ·
  Sprint 9 logging (audit/verification/security) · Sprint 10 storage+media · Sprints 11–30 business modules,
  verification portal, PDFs/QR, ownership, CMS, public site, admin dashboard, analytics, QA/launch.

## Known Notes (deferred)
- server.py uses deprecated `@app.on_event`; migrate to lifespan handler in a later sprint.
- CORS credentialed wildcard to be fixed in Sprint 2/6.
