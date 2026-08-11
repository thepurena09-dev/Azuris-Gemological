# Azuris Gemological — CHANGELOG (fork continuation)

## 2026-06 — Follow-up (client-requested, unlocks: promo slide, contact page, card background)
Self-tested (screenshots + hrefs + backend render); tsc clean; backend imports OK. Preview only.
- **Homepage promo slide** (`pages/public/HomePage.tsx`): right panel box background made transparent
  (removed the bordered `bg-primary/40` container); now displays the **sample certificate card**
  image (`/sample-card.png`, falls back to CMS `promo_image_url` if set) with a soft drop-shadow;
  description font brightened to `/80` for readability on navy.
- **Sample card static asset** (`frontend/public/sample-card.png`): rasterized from the live
  `build_card_pdf` sample fixture (AGR-ZMD-000015-26). REGENERATE this file if the card design
  changes: `cd /app/backend && python3 -c "from services import certificate_pdf as cp; import api.certificates as ac; open('/app/frontend/public/sample-card.png','wb').write(cp.render_card_png(ac._sample_cert(), ac._sample_photo_bytes(), 'https://gemstone-cert-1.preview.emergentagent.com/verify?sample=1', zoom=4.0))"`.
- **Contact Us page** (`pages/public/ContactPage.tsx`): replaced the placeholder with a real contact
  section — hero heading/subtitle + a WhatsApp button (`contact-whatsapp-btn`, uses
  `useBusiness().whatsappHref()`) + the business number. Reuses existing `contact.*` i18n.
- **Certificate card watermark/background** (`services/certificate_pdf.py` `build_card_pdf`):
  replaced the geometric line pattern with the SAME `_pattern(...GOLD, alpha=0.05)` gold-scallop
  guilloche used on the certificate cover / Page 1 — i.e. the card watermark/background is now a
  duplicate of the cover's. Rounded navy shell, gold rounded frame, all content/QR/size unchanged.
  Removed the now-unused `_card_geo` helper.

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
