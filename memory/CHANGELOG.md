# Azuris Gemological — CHANGELOG (fork continuation)

## 2026-06 — AGR CLIENT-REVIEW FREEZE revision (Preview only, NOT deployed)
Validated: testing_agent iteration_30 — backend 5/5 PASS, frontend 100%. Data freeze intact
(certificate counter last_number=15 UNCHANGED — reactivated AGR-RBY-000015-26 from a prior
session; no new issuance, no persisted sample data). tsc clean.

- **Public navigation restyled** (`components/layout/Header.tsx`): removed bordered/boxed/raised
  button containers; desktop nav is now borderless bold (font-semibold) uppercase text with
  balanced tracking + consistent gaps, a restrained embossed text-shadow, gold color + animated
  underline on hover/active, and a visible keyboard focus ring. Mobile menu = plain text links
  with gold hover/focus (no boxes). Logo + language selector alignment preserved.
- **Certificate PDF Page 1 cover** (`services/certificate_pdf.py` `_agr_cover` + new `_cover_frame`):
  full deep-navy cover matching the reference — layered thin gold rules + continuous gold guilloche
  ribbon, centred emblem, navy AZURIS plaque (gold outline + "AZURIS GEMOLOGICAL RESEARCH"), gold
  title hierarchy (GEMSTONE IDENTIFICATION / CERTIFICATE / OFFICIAL GEMOLOGICAL DOCUMENT /
  TRUSTED GEMOLOGICAL INSTITUTION). No gemstone data/number/QR/signature on the cover.
- **Certificate PDF Page 3** (`_agr_presentation`): oversized landscape photo replaced with a
  smaller centred PORTRAIT container (74×78 mm ≈ 56% width / 37% height), contain-fit (aspect
  preserved, never cropped), thin navy outer rule + ivory mat, rebalanced whitespace. Content
  unchanged (CERTIFIED GEMSTONE / photo / English name / type / From AGR). Pages 2 & 4 untouched.
- **Certificate card visual shell** (`build_card_pdf` + new `_card_geo`): rounded deep-navy card
  shell (clipped roundRect) with a subtle low-contrast angular geometric security pattern and a
  restrained double gold rounded edge. All card content/QR/verification destination and the exact
  105×66 mm size preserved.
- **Admin Legality guidance** (`pages/admin/LegalityAdminPage.tsx`): added a non-persistent
  Indonesian info panel (`legality-info-panel`) explaining legality_snapshot behaviour, and a
  clearly labelled example panel "CONTOH PENGISIAN — BUKAN LEGALITAS RESMI". Instructional only —
  does not prefill/save/create any record. Existing form/upload/snapshot workflow unchanged.
- **PDF preview bug fix** (`pages/admin/CertificatesPage.tsx` demo modal + `pages/public/VerifyPage.tsx`
  modal): root cause = Chrome aborts a `blob:` PDF loaded in an `<iframe>` (net::ERR_ABORTED →
  "Halaman ini telah diblokir oleh Chrome"). Replaced the iframe with `<object type="application/pdf">`
  + a graceful fallback (message + open-in-new-tab "Buka PDF" link) so real Chrome renders the
  4-page PDF inline and browsers without a PDF plugin still get a working open/download path.
  No new endpoint, no auth/security weakening, no PDF-content change.
- **Obsolete membership CMS block removed** (`pages/admin/VisualsPage.tsx`): the "KEANGGOTAAN
  BERANDA" SectionCard + its fields + masked card preview + unused imports removed. Other CMS
  sections (login/process images, promo slide, backgrounds, home gems) intact.
- **Labels**: active certificate labels confirmed 4-page (ID "Sertifikat (4 Halaman)" / EN
  "4-Page Certificate"); stale "2-page" code comments corrected. Added dedicated i18n fallback
  strings (`pdfFallback`/`openPdf`) for the /verify PDF `<object>` fallback.

### CLIENT-REVIEW FREEZE (awaiting client confirmation)
Frozen areas: public navigation visual, certificate Page 1 & Page 3, protected Page 2 & Page 4,
certificate-card visual shell, Legality guidance, PDF-preview implementation, active admin design.
Do not modify frozen areas later unless the user writes: `UNLOCK CLIENT REVIEW: [change]`.
