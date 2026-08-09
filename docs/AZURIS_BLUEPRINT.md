# AZURIS GEMOLOGICAL — BLUEPRINT APLIKASI
**Status:** AZURIS PRODUCTION CANDIDATE v2 — PRE-HOSTINGER MIGRATION (FROZEN)
**Tanggal blueprint:** Juni 2026
**Baseline DB:** counter sertifikat `last_number = 14` → nomor berikutnya `AZR-GEM-000015-26`; seluruh koleksi bisnis = 0.

> Dokumen ini adalah cetak biru (blueprint) menyeluruh dari platform. Bersifat dokumentasi murni — tidak mengubah kode, skema, atau logika bisnis. Sumber kebenaran tetap `BUSINESS_RULES_LOCK.md`, `PRD.md`, dan `PRODUCTION_READINESS.md`.

---

## 1. RINGKASAN PRODUK
Platform sertifikasi & verifikasi gemologis mewah (luxury) untuk **Azuris Gemological**. Fokus pada pemeriksaan / identifikasi / dokumentasi / sertifikasi / verifikasi batu mulia — **BUKAN marketplace**.

Kapabilitas inti:
- Katalog publik bilingual (Indonesia default + English), tanpa harga, CTA WhatsApp.
- Penerbitan sertifikat dengan penomoran atomik + QR + security code.
- Portal verifikasi publik (QR token ATAU nomor sertifikat + security code).
- Garansi (warranty), transfer kepemilikan, kartu keanggotaan (membership card).
- CMS (legalitas, pengaturan bisnis, kontrol visual/branding).
- Dashboard admin sadar-peran (RBAC) + analitik privat.

---

## 2. PERSONA & PERAN (RBAC — 4 peran terkunci)
| Peran | Kewenangan |
|-------|-----------|
| **SUPER_ADMIN** | Kontrol penuh termasuk manajemen akun admin. |
| **ADMINISTRATOR** | Kontrol operasional penuh; tanpa manajemen akun admin. |
| **CONTENT_MANAGER** | CMS, media, presentasi katalog saja. |
| **CUSTOMER_SERVICE** | Read-oriented + rekaman pelanggan, lookup verifikasi, handoff WhatsApp. |
| Public visitor | Browsing katalog + portal verifikasi. |

Model izin: `Permission` enum (31 izin), matriks `ROLE_PERMISSIONS` least-privilege, **default-deny** (peran tak dikenal → 0 izin), 403 generik. SUPER_ADMIN bypass implisit.

---

## 3. TECH STACK
- **Frontend:** React 19 + TypeScript + Tailwind + shadcn/ui, Phosphor icons, recharts. Fonts: Playfair Display (heading) + Inter (body).
- **Backend:** FastAPI (Python), Motor (async MongoDB).
- **Database:** MongoDB — 14 koleksi terkunci, dual-identifier (ObjectId + UUID), document versioning, 3 koleksi log append-only.
- **Auth:** JWT internal (Argon2id, access 15m + refresh 7d dengan rotasi + server-side store).
- **PDF/QR:** ReportLab (build A6 booklet), PyMuPDF (rasterisasi preview PNG), qrcode[pil].
- **Storage:** Adapter vendor-neutral (`STORAGE_BACKEND`, default `mongo`).

### Desain (LOCKED — Royal Editorial, Light only)
Putih / warm-white `#FAF9F6`; teks & tombol utama **Deep Navy `#0D1B2A`**; aksen **Royal Blue `#1E4FA8`**; aksen sekunder hemat **Champagne Gold `#C7A247`**; border `#E7E7E7`; radius 14px; soft shadow; tanpa glassmorphism/gradient. Lebar konten maks 1280px. Tanpa dark mode.

---

## 4. ARSITEKTUR KODE
```
/app/
├── backend/
│   ├── api/          auth, health, certificates, verify, customers, catalog(jewelry),
│   │                 media, warranties, ownership, membership, legality, settings, analytics
│   ├── services/     issuance, certificate_pdf, preview, security, verification,
│   │                 ownership, membership, analytics, media, whatsapp
│   ├── models/       base, enums, people, catalog, documents, ownership, media, cms, settings, logs, legality
│   ├── repositories/ base, domain, counter, + per-domain
│   ├── auth/         security(argon2id), jwt_handler, dependencies, rbac, audit, security_logs
│   ├── core/         config, envelope, context
│   ├── db/           mongodb, indexes, init
│   ├── storage/      base(ABC), mongo_adapter, factory
│   └── server.py
├── frontend/src/
│   ├── pages/public/ HomePage, About, Contact, Legality, Verification, Membership(verify), Catalog/Gemstones/Jewelry(disabled)
│   ├── pages/auth/   LoginPage
│   ├── pages/admin/  Dashboard, Certificates, Gemstones, Customers, Jewelry, Warranties,
│   │                 Ownership, Membership, Legality, Settings, Visuals
│   ├── layouts/      AdminLayout
│   ├── components/   common, layout, membership(MembershipCardVisual), ui(shadcn)
│   ├── lib/          api(unwrap/mediaUrl), settings(BusinessSettingsProvider)
│   └── i18n/locales/ id.ts, en.ts
├── docs/  BUSINESS_RULES_LOCK.md, PRODUCTION_READINESS.md, AZURIS_BLUEPRINT.md
└── memory/ PRD.md, test_credentials.md
```

Pola: Factory/Adapter (storage), Repository (satu-satunya lapisan sentuh Mongo), Append-only History (log), RBAC guard factories, Response Envelope middleware.

---

## 5. MODEL DATA (14 koleksi terkunci)
- **people:** `customers`
- **catalog:** `gemstones`, `jewelry`
- **documents:** `certificates` (VersionMixin), `warranties`, `verification_tokens`
- **ownership:** `ownership_transfers`
- **cms/media:** `media`, `media_objects`, `site_settings`, `legality`
- **membership:** `membership_cards` (VersionMixin)
- **logs (append-only):** `audit_logs`, `security_logs`, `verification_logs`
- **counters:** unik `(name, year)` — atomik.

Prinsip Mongo: setiap dokumen extend `BaseDocument` (`_id`↔`id`, `PyObjectId`), `from_mongo`/`to_mongo`, tanpa spread dict mentah. Datetime `timezone.utc`. Respons API tidak pernah mengembalikan `password_hash`/`token`/`security_code`/ObjectId; PII disamarkan.

---

## 6. PETA API (prefix `/api`)
**Auth:** `POST /auth/login|refresh|logout`, `GET /auth/me`, `GET /auth/permissions`
**Health:** `GET /health`
**Sertifikat (admin):** `GET /admin/certificates`, `POST /admin/certificates/issue`, `POST /admin/certificates/{uuid}/reissue|revoke`, `GET /admin/certificates/{uuid}/pdf`, `GET /admin/certificates/demo-preview` (stateless, watermark DEMO)
**Gemstone:** `GET/POST/PUT /admin/gemstones`, `POST /admin/gemstones/{uuid}/photo|status`, `DELETE`, publik `GET /gemstone/photo/{uuid}`
**Verifikasi (publik):** `POST /verify` (nomor + security code), `GET /verify/qr/resolve`, `POST /verify/qr`, `GET /verify/preview?t=` (PNG front cover)
**Pelanggan:** `GET/POST/PUT/DELETE /admin/customers`
**Jewelry:** `GET/POST/PUT/DELETE /admin/jewelry`, `POST /admin/jewelry/{uuid}/status`
**Media:** `POST/GET /admin/media`, `POST /admin/media/{uuid}/main`, `GET /admin/media/{uuid}/raw`, publik `GET /media/{uuid}`
**Garansi:** `GET/POST /admin/warranties` (+ lifecycle)
**Kepemilikan:** `POST /admin/ownership/assign`, `GET/POST /admin/ownership/transfers`, `POST .../{uuid}/complete|cancel`
**Membership:** admin `/admin/membership`, publik `GET /membership/verify`, `GET /membership/qr`
**Legalitas:** publik `GET /legality`, `GET /legality/document/{uuid}`; admin publish/upload
**Settings/Visual CMS:** publik `GET /settings/public`; admin `GET/PUT /admin/settings/visuals`, `POST/GET /admin/settings/visuals/media`
**Analitik:** `GET /admin/analytics/overview` (SUPER_ADMIN + ADMINISTRATOR)

Semua respons `/api` sukses dibungkus `{success, data, meta:{request_id}}`; error `{success:false, error:{code,message,details?}, meta}`; PDF/PNG/gambar tetap raw bytes. `X-Request-ID` korelasi end-to-end.

---

## 7. ATURAN BISNIS KUNCI (LOCKED — lihat BUSINESS_RULES_LOCK.md)
- **Nomor sertifikat:** `AZR-GEM-{SEQ6}-{YY}` (mis. `AZR-GEM-000015-26`). Atomik via `find_one_and_update`+`$inc`, tidak pernah dihitung dari jumlah dokumen, tidak pernah dipakai ulang (revoke/archive tidak membebaskan nomor).
- **Versioning:** reissue = versi+1, nomor sama, versi lama `is_current=false`; QR token tetap. Verifikasi publik hanya menampilkan versi current.
- **Security code:** dibuat acak (alfabet tak-ambigu), TIDAK diturunkan dari nomor, ditampilkan SEKALI, dirotasi saat transfer kepemilikan selesai.
- **QR token:** opaque `secrets.token_urlsafe(32)`, tidak pernah di URL/respons publik.
- **Owner masking:** nama depan 4 huruf / belakang 3 huruf, sisanya `*`.
- **Prioritas verifikasi:** QR → Security Code → Certificate → Gemstone → Owner.
- **Anti-enumeration:** outcome generik (valid|archived|revoked|not_found), rate limit per-IP 20/60s, IP di-sha256.
- **Kepemilikan:** hanya penyelesaian transfer yang memutasi kepemilikan; verifikasi/QR tidak pernah mengubahnya.

### Format PROVISIONAL (belum dikunci — menunggu approval klien)
- Member ID `AZR-MEM-{SEQ6}-{YY}` (counter `membership` terpisah)
- Warranty No. `AZR-WTY-{SEQ6}-{YY}` (counter `warranty` terpisah)

---

## 8. SERTIFIKAT FISIK (A6 booklet)
2 halaman, A6 landscape 148×105 mm (fold 74 mm, safe ≥5 mm). Hal 1 = spread luar (back cover kiri + front cover kanan navy-dominan, plat nomor emas kompak); Hal 2 = spread dalam (info sertifikat + QR besar kiri, identitas batu + foto kanan). Berbasis `gemstone_snapshot` imutabel. Sumber tunggal renderer dipakai ulang untuk PDF, front-cover preview, dan Demo Preview (watermark). Cetak: A6 landscape, duplex flip short-edge, 100% actual size.

---

## 9. FITUR CMS VISUAL (POST-FREEZE, reuse arsitektur — tanpa endpoint/storage baru)
Endpoint sama `GET/PUT /admin/settings/visuals` + `site_settings`:
- Background **Dashboard**, **Login**, **Homepage**: `*_bg_enabled/url/opacity(4–24)/fit(cover|center)/blur(0–12)`.
- 4 foto hero gem homepage: `home_gem_{diamond,ruby,sapphire,emerald}_url`.
- Gambar Login admin + Proses Sertifikasi + showcase Membership homepage (masked).
Live setelah Save via `BusinessSettingsProvider` (tanpa rebuild). RBAC CMS_READ/CMS_WRITE (CUSTOMER_SERVICE read-only).

---

## 10. KESIAPAN DEPLOYMENT / MIGRASI HOSTINGER
Status: **READY WITH BLOCKERS** (lihat `PRODUCTION_READINESS.md`).

Siap: React build, FastAPI requirements, index bootstrap Mongo (`init_database()`), storage adapter (`STORAGE_BACKEND`), template env (`backend/.env.example`, `frontend/.env.example`), tanpa secret di repo. Tanpa seed saat startup; skrip seed menolak `ENVIRONMENT=production`.

**BLOCKERS keputusan klien sebelum go-live:**
1. **PUBLIC_BASE_URL / domain resmi** — PRODUCTION BLOCKER (URL QR + membership; jangan menebak).
2. Approval kunci format Member ID `AZR-MEM-*`.
3. Approval kunci format Warranty No `AZR-WTY-*`.
4. Upload dokumen legalitas asli (placeholder hingga saat itu).
5. Secret produksi (JWT_SECRET asli, MONGO_URL, CORS_ORIGINS eksplisit, ENVIRONMENT=production).

Belum ada: Dockerfile/compose (dibuat saat migrasi), DNS, data asli, deploy.

---

## 11. INVARIAN FREEZE (WAJIB DIJAGA)
- `counters.certificate.last_number = 14` → berikutnya `AZR-GEM-000015-26`.
- Semua koleksi bisnis = 0 (customers, gemstones, jewelry, certificates, warranties, membership_cards, ownership_transfers, verification_tokens).
- `media` menyimpan 8 dokumen CMS pra-ada (dipertahankan).
- `BUSINESS_RULES_LOCK.md` TIDAK diubah.
- Demo Preview stateless: tidak membuat cert/token, tidak menaikkan counter, tidak muncul di verifikasi publik/analitik.

---

## 12. KREDENSIAL UJI (dev-only, bukan produksi)
Lihat `/app/memory/test_credentials.md` — mis. `admin@azuris.local` / `AzurisDev@2026!` (SUPER_ADMIN), plus akun ADMINISTRATOR/CONTENT_MANAGER/CUSTOMER_SERVICE `@azuris.local`. Tidak pernah dipakai di produksi.
