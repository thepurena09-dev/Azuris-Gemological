# Azuris Gemological — Platform

Luxury gemological certification & verification platform.
**Business Blueprint v1** + **Architecture Lock v1.1** are the single source of truth.

> Current status: **Sprint 1 — Frontend & Backend Foundation** (application shell only).
> No business logic, database collections, or authentication yet.

---

## Tech Stack

| Layer     | Technology                                             |
| --------- | ------------------------------------------------------ |
| Frontend  | React 19 + **TypeScript** + Tailwind CSS + shadcn/ui   |
| Backend   | FastAPI (Python)                                       |
| Database  | MongoDB (Motor) — *introduced in Sprint 3*             |
| i18n      | Indonesian (default) + English                         |
| Icons     | @phosphor-icons/react (duotone)                        |
| Fonts     | Cormorant Garamond (display) · Outfit (body)           |

---

## Project Structure

```
/app
├── backend/
│   ├── server.py            # FastAPI entrypoint (app + CORS + /api/health)
│   ├── api/                 # API routers (health)
│   ├── core/                # config layer            (Sprint 2)
│   ├── db/                  # Mongo connection layer   (Sprint 3)
│   ├── models/              # Pydantic domain models   (Sprint 4)
│   ├── schemas/             # DTO schemas              (Sprint 4)
│   ├── repositories/        # data-access layer        (Sprint 5)
│   ├── auth/                # JWT auth + RBAC          (Sprint 6-7)
│   ├── storage/             # object storage adapter   (Sprint 10)
│   ├── services/            # business services        (Sprint 11+)
│   ├── pyproject.toml       # black / isort / mypy config
│   └── setup.cfg            # flake8 config
│
└── frontend/
    ├── tsconfig.json
    └── src/
        ├── index.tsx        # entry (providers)
        ├── App.tsx          # routing shell
        ├── config/          # app + locale config
        ├── i18n/            # LanguageProvider + locales (id/en)
        ├── layouts/         # PublicLayout · AdminLayout
        ├── components/
        │   ├── layout/      # Header · Footer · LanguageSwitcher
        │   └── common/      # PlaceholderPage
        ├── pages/
        │   ├── public/      # Home · About · Verification · Catalog · Gemstones · Jewelry · Contact
        │   ├── auth/        # Login
        │   └── admin/       # Dashboard
        └── constants/       # testIds
```

---

## Routes (Sprint 1 shell)

**Public:** `/` · `/about` · `/verification` · `/catalog` · `/catalog/gemstones` · `/catalog/jewelry` · `/contact`
**Auth:** `/login`
**Admin:** `/admin` → `/admin/dashboard`

## Backend API

- `GET /api/health` → `{ status, service, version, sprint }`

---

## Development

Services are managed by **supervisor** (do not start servers manually).

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

Lint / format (backend):

```bash
cd backend && black . && isort . && flake8 && mypy .
```

Type-check (frontend):

```bash
cd frontend && yarn tsc --noEmit
```
