# Azuris Gemological — Sprint 4.5: BUSINESS RULES LOCK v1.1

Documentation only. No code. This document is the permanent, authoritative
specification of business behavior for every locked entity. It sits beneath the
**Business Blueprint v1** and **Architecture Lock v1.1** and must not be
contradicted by any future sprint. Implementation sprints (5+) enforce — never
redefine — these rules.

---

## ADDENDUM v1.1 — Locked Business Decisions (authoritative)

### A. Certificate Number Format (CLIENT-REVISED — FASE 3.4)
Permanent business identifier pattern: **`AZR-GEM-000001-YY`**
- `AZR-GEM` — fixed brand/product prefix.
- `000001` — zero-padded 6-digit sequence, monotonically increasing (per year).
- `YY` — 2-digit issuing year (UTC), e.g. `26` for 2026.
- Globally **unique, immutable, never reused**. Independent of `_id` and `uuid`.
- Example: `AZR-GEM-000042-26`.

> **REVISION NOTE (FASE 3.4 — Client Approved Certificate Number Format Revision):**
> - **Old:** `AZR-GEM-YYYY-000001` (e.g. `AZR-GEM-2026-000015`)
> - **New:** `AZR-GEM-000001-YY` (e.g. `AZR-GEM-000015-26`)
> - **Reason:** Client Approved Certificate Number Format Revision — FASE 3.4.
> - **Scope:** ONLY the number *format* changed. Atomic counter, per-year sequence,
>   uniqueness, non-reuse, immutability of historical numbers, and all other rules
>   below remain UNCHANGED. Historical certificates (if any) keep their original
>   number immutably; at revision time the DB contained 0 issued certificates, so
>   the new format applies from the next issuance (`AZR-GEM-000015-26`).

### B. Owner Name Masking (LOCKED)
Public displays of an owner's name are masked. Length is preserved; revealed
characters come from the **start** of each name part, remaining characters become `*`.
- **First name:** reveal the first **4** characters; mask the rest. If the first
  name is ≤ 4 characters, it is shown in full.
- **Last name:** reveal the first **3** characters; mask the rest. Edge rule: to
  never expose a full family name, if the last name is ≤ 3 characters, reveal only
  the **first 1** character and mask the remaining (length preserved).
- Only the first and last name tokens are displayed; any middle names are omitted.
- Locked examples:
  - `Alexander Wijaya` → `Alex***** Wij***`
  - `John Doe` → `John D**`
- Applies everywhere an owner is shown publicly (public verification results,
  membership cards, any public/limited projection).

### C. Verification Resolution Priority (LOCKED)
When resolving a verification request, the system follows this strict order:
1. **QR Token** (the high-entropy secret) →
2. **Security Code** (exact-match manual credential) →
3. **Certificate** (current version) →
4. **Gemstone** (subject of authenticity) →
5. **Owner** (masked display).
QR token is the primary entry point; the security code is the manual fallback;
resolution then walks certificate → gemstone → owner. A break at any level yields
a generic non-authentic result (internal precise `result` still logged).

### D. Certificate Version Visibility (LOCKED)
- The **current** version (`is_current = true`) is the **only** version shown publicly.
- **Previous versions** remain **archived** (retained, immutable) and are **not** public.
- **Admins** (per RBAC) can access **every** version, current and superseded.

---


## Global Conventions (apply to every entity unless overridden)
- **Dual identifier:** internal `_id` (ObjectId, never exposed) + public `uuid` (UUID v4, immutable once created, used in all external URLs/QRs/references).
- **Audit envelope:** `created_at`, `updated_at`, `created_by`, `updated_by` on every mutable record. `created_at`/`created_by` are immutable after creation.
- **Timestamps:** UTC, ISO-8601. Never naive local time.
- **Soft delete:** business records are soft-deleted (`is_deleted=true`, `deleted_at`); never hard-deleted. Soft-deleted records are excluded from normal reads and all public responses.
- **Default deny:** every write requires an authorized role (see Admin Operations). Public endpoints are read/verify only.
- **No secret/PII leakage:** `password_hash`, verification `token`, and `security_code` are never returned by any API or written to any log. Owner names are masked in public contexts.
- **Immutable identity fields (all entities):** `_id`, `uuid`, `created_at`, `created_by` can never change after creation.

---

## 1. Gemstones
**Purpose:** the core catalog asset and unit of authenticity.

- **Lifecycle / status transitions** (`GemstoneStatus`):
  - `draft` → `verified` → `published` → `transferred` → `archived`.
  - Allowed transitions:
    - `draft → verified` (data complete & reviewed)
    - `verified → published` (made public in catalog)
    - `published → transferred` (ownership transfer completed)
    - `transferred → published` (re-listed by new owner, optional)
    - any state → `archived` (retired; hidden from catalog, record retained)
  - Forbidden: skipping `verified` before `published`; leaving `archived` except via a new explicit reactivation decision (not automatic).
- **Immutable fields:** `uuid`. Once a certificate is issued for the stone, its core physical specs (`weight_carat`, `gemstone_type`, `category`) become **locked** — corrections require a new certificate version, not a silent edit.
- **Editable fields:** bilingual `name_id/name_en`, `description_id/en`, presentation fields (`color`, `clarity`, `cut`, `shape`, `dimensions_mm`, `origin`, `treatment`) while in `draft`; `media_ids`, `status` (per transitions), `active_owner_id` (only via Ownership engine), `certificate_id` (set once, replaced only via re-issue).
- **Versioning:** the gemstone record itself is not versioned; its authenticity documents (certificate/warranty) are.
- **Security rules:** only `published` (non-deleted) stones appear publicly; **no prices are ever stored or exposed**; public detail exposes catalog fields + masked owner only.
- **Validation:** `weight_carat > 0`; `name_id`/`name_en` required; `status` must be a valid enum value.
- **Audit:** every create/update/status-change/owner-change writes an `audit_logs` entry with before/after snapshot.
- **Business constraints:** a stone has at most one **current** certificate and one active owner at a time. A `published`/`transferred` stone must have a `verified`-or-later history.

## 2. Jewelry
**Purpose:** catalog pieces composed of one or more gemstones.

- **Lifecycle / status transitions** (`JewelryStatus`): `draft` → `published` → `archived`; `published → archived` and `archived → published` (reactivation) allowed.
- **Immutable fields:** `uuid`.
- **Editable fields:** `name_id/en`, `jewelry_type`, `material`, `gemstone_ids`, `weight_grams`, `dimensions_mm`, `description_id/en`, `media_ids`, `status`.
- **Versioning:** none (composition history captured via audit log).
- **Security rules:** no prices; only `published` pieces are public.
- **Validation:** `name_id/en`, `jewelry_type`, `material` required; `weight_grams > 0` when set; referenced `gemstone_ids` must resolve to existing gemstones.
- **Audit:** all mutations logged with association changes.
- **Business constraints:** associated stones must exist; removing a stone from a published piece is an auditable edit.

## 3. Certificates
**Purpose:** the official, verifiable identity document for a gemstone.

- **Lifecycle / status transitions** (`CertificateStatus`): `draft` → `issued` → (`reissued` | `revoked`).
  - `draft → issued`: assigns `issued_at`/`issued_by`, marks `is_current=true`, generates the PDF + verification linkage.
  - `issued → reissued`: creates a **new version** (see Versioning); the prior version becomes `is_current=false` but is retained immutably.
  - `issued/reissued → revoked`: certificate no longer verifies as authentic; public verification returns a revoked result.
- **Immutable fields:** `uuid`, `certificate_number` (globally unique, never reused, never edited), `gemstone_id`, and — per version — the grading snapshot (`color_grade`, `clarity_grade`, `cut_grade`, `carat_weight`, `measurements`) and `version`, `created_version_at`, `created_version_by`. **Issued versions are immutable.**
- **Editable fields:** only while `draft` — grading fields and bilingual `comments_id/en`. After issuance, changes require a new version.
- **Versioning rules:** `version` starts at 1; each re-issue increments `version`, sets `is_current=true` on the new version and `false` on all others; **exactly one** current version per certificate at any time. Superseded versions are retained (immutable, never deleted).
- **Security rules:** the verification link/QR references the stable public `verification_uuid`/token, not the certificate `_id`. `certificate_number` follows the client-approved format **`AZR-GEM-000001-YY`** (unique, immutable, never reused); unguessability is provided by the token, not the number.
- **Version visibility (v1.1 lock):** only the **current** version is public; **previous versions stay archived** (retained, not public); **admins can access every version**.
- **Validation:** `certificate_number` required & unique; `gemstone_id` must reference an existing (verified-or-later) stone; `carat_weight > 0` when set.
- **Audit:** issue, re-issue (version_create), and revoke are all logged with before/after and version metadata.
- **Business constraints:** a gemstone may hold multiple certificate versions over time but only one `is_current`. A revoked certificate cannot be un-revoked; a corrected document must be a new re-issue.

## 4. Warranties
**Purpose:** per-stone warranty terms and coverage.

- **Lifecycle / status transitions** (`WarrantyStatus`): `active` → (`expired` | `void`).
  - `active → expired`: reaching `end_date`.
  - `active → void`: administratively revoked (e.g., terms breached).
  - No path back to `active` from `expired`/`void`; a new warranty (new version) is created instead.
- **Immutable fields:** `uuid`, `gemstone_id`, and per-version `terms_id/en`, `period_months`, `start_date`, `version` fields. Issued warranty versions are immutable.
- **Editable fields:** `status` (per transitions), `pdf_media_id`; term corrections require a new version.
- **Versioning rules:** same model as certificates — one `is_current` version; superseded versions retained.
- **Security rules:** warranty PDFs stored per naming convention; contain no secrets.
- **Validation:** `terms_id/en` required; `period_months ≥ 0`; `end_date ≥ start_date` when both present; `gemstone_id` must exist.
- **Audit:** creation, versioning, status changes logged.
- **Business constraints:** a warranty is always bound to exactly one gemstone; one current warranty version per stone.

## 5. Ownership Transfers
**Purpose:** trusted transfer of a gemstone from one owner to another.

- **Lifecycle / status transitions** (`TransferStatus`): `pending` → (`completed` | `cancelled`).
  - `pending → completed`: records previous/new owner, sets `transfer_date`, sets gemstone `status = transferred`, updates gemstone `active_owner_id`, **rotates the security code** (`security_code_rotated=true`), and **keeps the QR/token stable**.
  - `pending → cancelled`: no ownership change.
- **Immutable fields:** `uuid`, `gemstone_id`, and — once `completed` — `previous_owner_id`, `new_owner_id`, `transfer_date`, `processed_by`. Completed transfers are immutable.
- **Editable fields:** while `pending` — `new_owner_id`, `proof_media_id`, bilingual `notes_id/en`, `transfer_date`.
- **Versioning:** none (each transfer is a discrete immutable record; the gemstone's transfer history is the ordered set of completed transfers).
- **Security rules:** the QR code and verification `token` persist across transfers (stable entry point); the `security_code` **must** be regenerated on completion (old code stops working). Code regeneration is logged in `security_logs`.
- **Validation:** `gemstone_id` and `new_owner_id` must reference existing records; `new_owner_id != previous_owner_id`; a completed transfer requires proof reference per policy.
- **Audit:** every transfer create/complete/cancel logged with before/after (owner change) in `audit_logs`; code rotation logged in `security_logs`.
- **Business constraints:** only one `pending` transfer per gemstone at a time; completion is the only path that mutates gemstone ownership.

## 6. Verification (Tokens & Security Codes)
**Purpose:** the secret material that powers authenticity checks.

- **Lifecycle:** created with the certificate/gemstone; `is_active=true`; `security_code` rotated on ownership transfer (`rotated_at` set); deactivated (`is_active=false`) only if the certificate is revoked or the stone archived.
- **Immutable fields:** `uuid`, `gemstone_id`. `token` (high-entropy QR secret) is stable across transfers and is **not** rotated by transfers.
- **Editable fields (system-only, never via public API):** `security_code` (rotated), `is_active`, `certificate_id` linkage.
- **Versioning:** none.
- **Security rules:** `token` and `security_code` are secrets — never returned by any API, never logged. `token` is distinct from `uuid` (uuid = reference, token = secret). Codes are compared by **exact match**; failures return a **generic** message (no hint whether number, code, or record was wrong).
- **Validation:** `token` length ≥ 16 (high entropy); `security_code` length ≥ 4; exactly one active token record per gemstone/certificate pairing.
- **Audit:** generation and rotation logged in `security_logs`; verification attempts logged in `verification_logs` (see Public Verification).
- **Business constraints:** unguessable, non-enumerable; rate limiting applied at the public layer (Sprint 29).

## 7. Membership Cards
**Purpose:** a premium ownership artifact for a customer.

- **Lifecycle / status transitions** (`MembershipCardStatus`): `active` ↔ `inactive` (admin controlled).
- **Immutable fields:** `uuid`, `customer_id`, `card_number` (unique), and per-version identity snapshot; issued versions immutable.
- **Editable fields:** `status`, `masked_name`, `pdf_media_id`; identity corrections create a new version.
- **Versioning rules:** versioned like certificates — one `is_current`; superseded retained.
- **Security rules:** card shows **masked identity only** (locked masking format: first name first 4 chars, last name first 3 chars, remainder `*`); no full PII, no contact details, no secrets.
- **Validation:** `card_number` required & unique; `customer_id` must exist; `masked_name` required.
- **Audit:** generation, versioning, status changes logged.
- **Business constraints:** one current card version per customer; card generation requires an existing customer with recorded consent.

## 8. Media
**Purpose:** metadata-rich assets (photography/video) for entities.

- **Lifecycle:** upload → derivative generation (original/optimized/thumbnail) → linked to an entity → soft-deleted when removed.
- **Immutable fields:** `uuid`, `entity_type`, `entity_id`, `original_url`, technical metadata captured at ingest (`mime_type`, `size_bytes`, `width`, `height`, `duration_seconds`).
- **Editable fields:** `role` (main/gallery/video/thumbnail), `optimized_url`, `thumbnail_url`, bilingual `alt_text_id/en`, gallery ordering.
- **Versioning:** none (replacement = new media record + relink).
- **Security rules:** stored per the locked Object Storage folder structure; only referenced, non-deleted media served publicly.
- **Validation:** `original_url` and `mime_type` required; `size_bytes ≥ 0`; dimensions non-negative; `duration_seconds` only for video.
- **Audit:** attach/detach/role changes logged.
- **Business constraints:** at most one `main` media per entity; a `thumbnail`/`optimized` derivative belongs to exactly one asset.

## 9. Public Verification
**Purpose:** public proof of authenticity via two locked methods.

- **Methods (exact, dual-credential):**
  1. **QR token** — resolves the stable `token` to the current authentic record.
  2. **Manual** — `certificate_number` + `security_code`, matched **exactly** together.
- **Lifecycle of a request:** receive → match → mask → respond → log (always).
- **Security rules:**
  - Generic failure messages for all negative outcomes (not_found / invalid_code / expired / revoked surface as a single "could not verify" style message to the user, while the precise `result` is stored in `verification_logs`).
  - No secrets echoed; owner name returned **masked** per the locked format (first name first 4 chars, last name first 3 chars, remainder `*`; e.g. `Alexander Wijaya → Alex***** Wij***`, `John Doe → John D**`); no prices; no PII.
  - Every attempt (success or failure) is recorded in `verification_logs` with minimal safe metadata (method, result, hashed IP, masked cert number, timestamp) — never the token or code.
  - Rate limiting + abuse protection applied (hardening sprint).
- **Validation:** token length ≥ 16; manual requires both fields; both methods require an `is_active` token and a non-revoked, non-archived subject.
- **Business constraints:** verification reflects the **current** certificate version only; revoked/archived subjects return a non-authentic result; QR remains valid across ownership transfers (code does not).

## 10. Admin Operations (RBAC)
**Purpose:** role-scoped operational control (least privilege, default deny).

- **Roles & scope** (`AdminRole`):
  - `SUPER_ADMIN` — full system control, incl. admin-account management and role changes.
  - `ADMINISTRATOR` — full operational control over gemstones, jewelry, certificates, warranties, ownership, verification; **no** admin-account management.
  - `CONTENT_MANAGER` — CMS, media library, site content, catalog presentation only.
  - `CUSTOMER_SERVICE` — read-oriented + customer records, verification lookups, WhatsApp handoff; **no destructive actions**.
- **Lifecycle:** admin account `active` ↔ `inactive` (SUPER_ADMIN only); `last_login`/`last_activity` tracked.
- **Immutable fields:** `uuid`, `email` (identity; change is a controlled operation), `created_at`.
- **Editable fields:** `full_name`, `role` (SUPER_ADMIN only), `is_active` (SUPER_ADMIN only), `password_hash` (via secure reset flow only).
- **Security rules:** passwords stored only as hashes; JWT access/refresh with rotation; invalid credentials return a generic 401; unauthorized role access returns a generic 403. All auth events (login success/fail, refresh, rotation, role change, code regeneration, suspicious activity) recorded in `security_logs`.
- **Validation:** unique `email`; password minimum length policy; role must be one of the four locked values.
- **Audit:** every admin mutation writes an `audit_logs` entry (who/what/when + before/after). Auth/security events write `security_logs`. Logs are **append-only** and never store passwords, tokens, or unmasked PII.
- **Business constraints:** at least one `SUPER_ADMIN` must always exist; a role change and admin (de)activation are SUPER_ADMIN-only and always logged.

---

## Cross-Cutting Locks (summary)
- **Immutability spine:** `_id`, `uuid`, `certificate_number`, `card_number`, issued document versions, and completed ownership transfers are immutable.
- **Versioning spine:** certificates, warranties, membership cards — one `is_current` version, superseded versions retained immutably.
- **Security spine:** exact-match verification, generic error messages, masked owner display, no prices, secrets never returned/logged, stable QR + rotating security code on transfer.
- **Audit spine:** admin mutations → `audit_logs`; public verification → `verification_logs`; auth/security → `security_logs`; all append-only, redacted.
- **Status is never skipped or reversed** except where an explicit transition above allows it.

**End of Business Rules Lock v1.1 — no code implemented. Awaiting approval to proceed with Sprint 5.**
