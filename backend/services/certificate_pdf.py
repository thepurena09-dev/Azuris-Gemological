"""A6 landscape booklet certificate PDF — FASE 3.2 (premium visual refinement).

Exactly 2 pages of 148 x 105 mm (A6 landscape), folded vertically at 74 mm.
Page 1 = outside spread (back-cover left, front-cover right).
Page 2 = inside spread (certificate/verification left, gemstone identity right).

Royal-editorial luxury: navy-dominant front cover, ivory/beige inner pages with
navy section bars + gold accents, alternating soft-beige field rows, the official
Azuris emblem (embedded PNG) on covers + a faint emblem watermark inside. Brand
TTFs are unavailable in the environment, so the 14 standard PDF-safe fonts
(Times/Helvetica) are used with a carefully tracked hierarchy. Uses an immutable
snapshot so historical PDFs never change.
"""

import base64
import os
from io import BytesIO
from typing import Optional

import qrcode
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# --- Azuris palette ---------------------------------------------------------
NAVY = (0.051, 0.106, 0.165)      # #0D1B2A
NAVY_LT = (0.114, 0.180, 0.255)   # lighter navy (tone-on-tone)
ROYAL = (0.118, 0.310, 0.659)     # #1E4FA8
GOLD = (0.780, 0.635, 0.278)      # #C7A247
GOLD_SOFT = (0.870, 0.780, 0.560)
IVORY = (0.980, 0.976, 0.965)     # #FAF9F6
BEIGE = (0.910, 0.875, 0.812)     # #E8DFCF
BEIGE_LT = (0.957, 0.937, 0.902)  # very light beige (row zebra)
TAUPE = (0.722, 0.647, 0.541)     # #B8A58A
SLATE = (0.361, 0.435, 0.510)     # #5C6F82
GREY = (0.40, 0.40, 0.40)

PAGE_W = 148 * mm
PAGE_H = 105 * mm
FOLD_X = 74 * mm
SAFE = 5 * mm

HEAD = "Times-Roman"
HEADB = "Times-Bold"
BODY = "Helvetica"
BODYB = "Helvetica-Bold"

_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
LOGO_PATH = os.path.join(_ASSETS, "azuris-logo.png")
WATERMARK_PATH = os.path.join(_ASSETS, "azuris-watermark.png")

DISCLAIMER_ID = (
    "Sertifikat gemologi merupakan laporan hasil pemeriksaan dan identifikasi batu "
    "mulia. Sertifikat ini bukan merupakan jaminan harga, nilai investasi, kepemilikan, "
    "atau asal-usul hukum atas suatu batu."
)


def _logo(path):
    try:
        return ImageReader(path)
    except Exception:
        return None


_LOGO = _logo(LOGO_PATH)
_WM = _logo(WATERMARK_PATH)


# ---------------------------------------------------------------- primitives
def _qr_image(url: str) -> ImageReader:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(13, 27, 42), back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def _draw_logo(c, reader, cx, cy, size):
    if reader is None:
        return
    try:
        iw, ih = reader.getSize()
        ratio = size / max(iw, ih)
        dw, dh = iw * ratio, ih * ratio
        c.drawImage(reader, cx - dw / 2, cy - dh / 2, width=dw, height=dh, mask="auto")
    except Exception:
        pass


def _tracked(c, x, y, text, font, size, color, tracking=0.0, center=None):
    c.setFont(font, size)
    c.setFillColorRGB(*color)
    if center is not None:
        total = sum(c.stringWidth(ch, font, size) for ch in text) + tracking * (len(text) - 1)
        x = center - total / 2
    cx = x
    for ch in text:
        c.drawString(cx, y, ch)
        cx += c.stringWidth(ch, font, size) + tracking
    return cx


def _pattern(c, x0, x1, y0, y1, color=GOLD, alpha=0.05):
    """Subtle scallop/guilloche security pattern (print-safe, low opacity)."""
    c.saveState()
    c.setStrokeColorRGB(*color)
    c.setLineWidth(0.25)
    c.setStrokeAlpha(alpha)
    step = 6 * mm
    r = step * 0.62
    row = 0
    y = y0
    while y < y1 + step:
        offset = (step / 2) if row % 2 else 0
        x = x0 - step + offset
        while x < x1 + step:
            c.arc(x - r, y - r, x + r, y + r, 20, 140)
            x += step
        y += step * 0.7
        row += 1
    c.restoreState()


def _watermark(c, cx, cy, size):
    _draw_logo(c, _WM, cx, cy, size)


def _double_frame(c, x0, x1, color1=GOLD, color2=GOLD_SOFT, inset=3 * mm):
    c.saveState()
    c.setStrokeColorRGB(*color1)
    c.setLineWidth(0.9)
    c.rect(x0 + inset, inset, (x1 - x0) - 2 * inset, PAGE_H - 2 * inset)
    c.setStrokeColorRGB(*color2)
    c.setLineWidth(0.3)
    d = inset + 1.4 * mm
    c.rect(x0 + d, d, (x1 - x0) - 2 * d, PAGE_H - 2 * d)
    c.restoreState()


def _demo_stamp(c, x0, x1):
    """Diagonal SAMPLE / NOT VALID watermark over a panel (visible but non-obscuring)."""
    cx = (x0 + x1) / 2
    cy = PAGE_H / 2
    c.saveState()
    c.translate(cx, cy)
    c.rotate(30)
    # faint white halo so it stays legible on both navy and ivory panels
    c.setFillColorRGB(1, 1, 1)
    c.setFillAlpha(0.16)
    c.setFont(HEADB, 25)
    c.drawCentredString(0.6, 8 * mm - 0.6, "SAMPLE")
    c.setFillColorRGB(0.83, 0.16, 0.16)
    c.setFillAlpha(0.40)
    c.setFont(HEADB, 25)
    c.drawCentredString(0, 8 * mm, "SAMPLE")
    c.setFont(HEADB, 12)
    c.drawCentredString(0, 0.5 * mm, "PREVIEW")
    c.setFont(BODYB, 9)
    c.drawCentredString(0, -6 * mm, "NOT VALID")
    c.restoreState()


def _fold_guide(c):
    c.saveState()
    c.setStrokeColorRGB(0.78, 0.78, 0.78)
    c.setDash(1, 3)
    c.setLineWidth(0.3)
    c.line(FOLD_X, 0, FOLD_X, PAGE_H)
    c.restoreState()


def _section_bar(c, x0, x1, y, text, h=5.0 * mm):
    """Premium navy section bar with a gold accent tab and tracked ivory label."""
    c.setFillColorRGB(*NAVY)
    c.rect(x0, y - h, x1 - x0, h, fill=1, stroke=0)
    c.setFillColorRGB(*GOLD)
    c.rect(x0, y - h, 1.6 * mm, h, fill=1, stroke=0)
    _tracked(c, x0 + 3.6 * mm, y - h + 1.7 * mm, text.upper(), BODYB, 6.4, IVORY, tracking=0.7)
    return y - h - 2.6 * mm


def _wrap(c, text, font, size, max_w):
    c.setFont(font, size)
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if c.stringWidth(trial, font, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _field(c, x, w, y, label, value, val_size=7.6, zebra=False):
    if zebra:
        c.saveState()
        c.setFillColorRGB(*BEIGE_LT)
        c.rect(x - 1.5 * mm, y - 1.8 * mm, w + 3 * mm, 5.0 * mm, fill=1, stroke=0)
        c.restoreState()
    c.setFillColorRGB(*SLATE)
    c.setFont(BODYB, 5.6)
    label = label.upper()
    c.drawString(x, y, label)
    lw = c.stringWidth(label, BODYB, 5.6)
    val = str(value)
    c.setFillColorRGB(*NAVY)
    c.setFont(BODY, val_size)
    c.drawRightString(x + w, y, val)
    vw = c.stringWidth(val, BODY, val_size)
    x1 = x + w - vw - 2
    x0 = x + lw + 2
    if x1 > x0:
        c.saveState()
        c.setStrokeColorRGB(*GOLD_SOFT)
        c.setDash(0.4, 1.8)
        c.setLineWidth(0.4)
        c.line(x0, y + 0.6, x1, y + 0.6)
        c.restoreState()


def _fmt_phone(digits: str) -> str:
    d = "".join(ch for ch in (digits or "") if ch.isdigit())
    if not d:
        return ""
    if d.startswith("62") and len(d) > 5:
        rest = d[2:]
        return f"+62 {rest[:3]}-{rest[3:7]}-{rest[7:]}".rstrip("-")
    return f"+{d}"


# ---------------------------------------------------------------- panels
def _panel_front(c, x0, x1, number, year):
    # Navy-dominant luxury cover
    c.setFillColorRGB(*NAVY)
    c.rect(x0, 0, x1 - x0, PAGE_H, fill=1, stroke=0)
    _pattern(c, x0, x1, 0, PAGE_H, color=GOLD, alpha=0.06)
    _double_frame(c, x0, x1, color1=GOLD, color2=GOLD_SOFT)
    cx = (x0 + x1) / 2

    _draw_logo(c, _LOGO, cx, PAGE_H - 24 * mm, 18 * mm)

    _tracked(c, 0, PAGE_H - 42 * mm, "AZURIS", HEADB, 23, IVORY, tracking=3.0, center=cx)
    _tracked(c, 0, PAGE_H - 48 * mm, "GEMOLOGICAL", BODY, 7.5, GOLD, tracking=4.2, center=cx)

    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.7)
    c.line(cx - 15 * mm, PAGE_H - 52 * mm, cx + 15 * mm, PAGE_H - 52 * mm)

    c.setFillColorRGB(*BEIGE)
    c.setFont(HEAD, 10.5)
    c.drawCentredString(cx, PAGE_H - 60 * mm, "Gemological Certificate")
    c.setFillColorRGB(*TAUPE)
    c.setFont(HEAD, 8.5)
    c.drawCentredString(cx, PAGE_H - 65.5 * mm, "Sertifikat Gemologi")

    # certificate serial plate — compact luxury plaque (must NOT dominate AZURIS)
    plate_w, plate_h = 38 * mm, 9.5 * mm
    px, py = cx - plate_w / 2, PAGE_H - 82 * mm
    c.setFillColorRGB(*IVORY)
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.5)
    c.rect(px, py, plate_w, plate_h, fill=1, stroke=1)
    _tracked(c, 0, py + plate_h - 3.0 * mm, "NOMOR SERTIFIKAT", BODY, 3.4, TAUPE, tracking=0.8, center=cx)
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 8.5)
    c.drawCentredString(cx, py + 1.8 * mm, number)

    c.setFillColorRGB(*BEIGE)
    c.setFont(BODY, 6.0)
    c.drawCentredString(cx, py - 5.0 * mm, f"Tahun Terbit {year}" if year else "")


def _panel_back(c, x0, x1, version, website, contact):
    # Lighter ivory cover with a navy branded header band
    c.setFillColorRGB(*IVORY)
    c.rect(x0, 0, x1 - x0, PAGE_H, fill=1, stroke=0)
    _pattern(c, x0, x1, 0, PAGE_H, color=TAUPE, alpha=0.06)

    band_h = 22 * mm
    c.setFillColorRGB(*NAVY)
    c.rect(x0 + 3 * mm, PAGE_H - 3 * mm - band_h, (x1 - x0) - 6 * mm, band_h, fill=1, stroke=0)
    cx = (x0 + x1) / 2
    _draw_logo(c, _LOGO, cx, PAGE_H - 3 * mm - band_h / 2 + 1.5 * mm, 11 * mm)
    _tracked(c, 0, PAGE_H - 3 * mm - band_h + 3.6 * mm, "AZURIS GEMOLOGICAL", BODYB, 6.5, IVORY,
             tracking=1.4, center=cx)

    _double_frame(c, x0, x1, color1=GOLD, color2=GOLD_SOFT)

    inner = (x1 - x0) - 2 * (SAFE + 2 * mm)
    lx = x0 + SAFE + 2 * mm

    _tracked(c, 0, PAGE_H - band_h - 9 * mm, "KEASLIAN & VERIFIKASI", BODYB, 6.0, GOLD,
             tracking=1.2, center=cx)
    c.setFillColorRGB(*SLATE)
    stmt = (
        "Sertifikat ini diterbitkan resmi oleh Azuris Gemological dan dilengkapi kode "
        "keamanan unik serta kode QR untuk verifikasi digital keasliannya."
    )
    y = PAGE_H - band_h - 14 * mm
    for ln in _wrap(c, stmt, BODY, 6.5, inner)[:4]:
        c.setFont(BODY, 6.5)
        c.drawCentredString(cx, y, ln)
        y -= 3.6 * mm

    y -= 1.5 * mm
    c.setFillColorRGB(*NAVY)
    for s in [
        "1.  Pindai kode QR pada sertifikat, atau",
        "2.  Buka situs resmi Azuris Gemological, lalu",
        "3.  Masukkan Nomor Sertifikat & Kode Keamanan.",
    ]:
        c.setFont(BODY, 6)
        c.drawString(lx, y, s)
        y -= 3.7 * mm

    # gold divider + contact
    c.setStrokeColorRGB(*GOLD_SOFT)
    c.setLineWidth(0.4)
    c.line(lx, SAFE + 15 * mm, x1 - SAFE - 2 * mm, SAFE + 15 * mm)
    c.setFillColorRGB(*ROYAL)
    c.setFont(BODYB, 6.6)
    c.drawCentredString(cx, SAFE + 10 * mm, website or "azuris-gemological.com")
    if contact:
        c.setFillColorRGB(*SLATE)
        c.setFont(BODY, 6)
        c.drawCentredString(cx, SAFE + 6 * mm, f"WhatsApp {contact}")
    c.setFillColorRGB(*TAUPE)
    c.setFont(BODY, 5.2)
    v = f"Dokumen v{version}" if version else ""
    c.drawCentredString(cx, SAFE + 1.5 * mm, v)


def _panel_info(c, x0, x1, cert, snap, qr_reader):
    c.setFillColorRGB(*IVORY)
    c.rect(x0, 0, x1 - x0, PAGE_H, fill=1, stroke=0)
    _watermark(c, (x0 + x1) / 2, PAGE_H / 2 + 6 * mm, 46 * mm)
    x = x0 + SAFE
    w = (x1 - x0) - 2 * SAFE
    top = PAGE_H - SAFE - 1 * mm

    y = _section_bar(c, x, x1 - SAFE, top, "Sertifikat & Verifikasi")

    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 12.5)
    c.drawString(x, y - 4.5 * mm, cert["certificate_number"])
    y -= 9.5 * mm

    rows = [
        ("Tanggal Terbit", (cert.get("issued_at") or "")[:10] or "-"),
        ("Versi Dokumen", str(cert.get("version") or 1)),
        ("Status", "Aktif - Versi Terkini"),
    ]
    if snap.get("examiner"):
        rows.append(("Pemeriksa / Gemolog", snap["examiner"]))
    rows.append(("Penanda Tangan", snap.get("signatory") or "Azuris Gemological"))
    for i, (label, val) in enumerate(rows):
        _field(c, x, w, y, label, val, val_size=7.4, zebra=(i % 2 == 0))
        y -= 6.2 * mm

    # signature
    y -= 1 * mm
    c.setStrokeColorRGB(*SLATE)
    c.setLineWidth(0.4)
    c.line(x, y, x + 30 * mm, y)
    c.setFillColorRGB(*SLATE)
    c.setFont(BODY, 5)
    c.drawString(x, y - 3.2 * mm, "Tanda Tangan Berwenang")

    # disclaimer in mid whitespace
    c.setFillColorRGB(*GREY)
    dy = y - 9 * mm
    for ln in _wrap(c, DISCLAIMER_ID, BODY, 4.8, w)[:3]:
        c.setFont(BODY, 4.8)
        c.drawString(x, dy, ln)
        dy -= 3 * mm

    # QR block bottom-left
    qr_size = 24 * mm
    qy = SAFE + 1 * mm
    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.6)
    c.rect(x - 1.2 * mm, qy - 1.2 * mm, qr_size + 2.4 * mm, qr_size + 2.4 * mm, fill=1, stroke=1)
    c.drawImage(qr_reader, x, qy, width=qr_size, height=qr_size, mask="auto")
    tx = x + qr_size + 4 * mm
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 5.8)
    c.drawString(tx, qy + qr_size - 2 * mm, "VERIFIKASI DIGITAL")
    c.setFillColorRGB(*SLATE)
    c.setFont(BODY, 5.4)
    for i, ln in enumerate([
        "Pindai kode QR untuk memeriksa",
        "keaslian sertifikat secara resmi.",
        "Hanya versi terkini yang aktif;",
        "versi sebelumnya diarsipkan.",
    ]):
        c.drawString(tx, qy + qr_size - 6 * mm - i * 3.4 * mm, ln)


def _panel_gemstone(c, x0, x1, snap, photo_reader, number):
    c.setFillColorRGB(*IVORY)
    c.rect(x0, 0, x1 - x0, PAGE_H, fill=1, stroke=0)
    _watermark(c, (x0 + x1) / 2, PAGE_H / 2, 46 * mm)
    x = x0 + SAFE
    w = (x1 - x0) - 2 * SAFE
    top = PAGE_H - SAFE - 1 * mm

    y0 = _section_bar(c, x, x1 - SAFE, top, "Identitas Batu Mulia")

    # photo top-right (beige mat + gold frame, aspect preserved)
    box_w, box_h = 26 * mm, 22 * mm
    px, py = x1 - SAFE - box_w, y0 - box_h + 1 * mm
    if photo_reader is not None:
        c.setFillColorRGB(*BEIGE_LT)
        c.rect(px - 1 * mm, py - 1 * mm, box_w + 2 * mm, box_h + 2 * mm, fill=1, stroke=0)
        try:
            iw, ih = photo_reader.getSize()
            ratio = min(box_w / iw, box_h / ih)
            dw, dh = iw * ratio, ih * ratio
            c.drawImage(photo_reader, px + (box_w - dw) / 2, py + (box_h - dh) / 2,
                        width=dw, height=dh, mask="auto")
        except Exception:
            pass
        c.setStrokeColorRGB(*GOLD)
        c.setLineWidth(0.6)
        c.rect(px - 1 * mm, py - 1 * mm, box_w + 2 * mm, box_h + 2 * mm)

    pairs = [
        ("Nama", snap.get("name")),
        ("Jenis Objek", snap.get("object_type")),
        ("Spesies", snap.get("species")),
        ("Varietas", snap.get("variety")),
        ("Berat", f"{snap.get('carat')} ct" if snap.get("carat") else None),
        ("Dimensi", snap.get("dimensions")),
        ("Bentuk", snap.get("shape")),
        ("Potongan", snap.get("cut")),
        ("Warna", snap.get("color")),
        ("Transparansi", snap.get("transparency")),
        ("Kejernihan", snap.get("clarity")),
        ("Perlakuan", snap.get("treatment")),
        ("Asal", snap.get("origin")),
    ]
    pairs = [(k, v) for k, v in pairs if v not in (None, "", "None")]

    photo_bottom = py if photo_reader is not None else PAGE_H
    narrow_w = (px - x - 3 * mm) if photo_reader is not None else w
    y = y0 - 2.5 * mm
    idx = 0
    for k, v in pairs:
        full = y < photo_bottom - 1 * mm
        fw = w if full else max(narrow_w, 22 * mm)
        _field(c, x, fw, y, k, v, val_size=7.1, zebra=(full and idx % 2 == 0))
        y -= 5.6 * mm
        if full:
            idx += 1

    if snap.get("conclusion"):
        yb = _section_bar(c, x, x1 - SAFE, max(y - 1 * mm, SAFE + 15 * mm), "Kesimpulan Pemeriksaan")
        c.setFillColorRGB(*NAVY)
        for j, ln in enumerate(_wrap(c, snap["conclusion"], BODY, 6.6, w)[:2]):
            c.setFont(BODY, 6.6)
            c.drawString(x, yb - j * 3.4 * mm, ln)

    c.setFillColorRGB(*TAUPE)
    c.setFont(BODY, 5)
    c.drawRightString(x1 - SAFE, SAFE - 0.5 * mm, number)


# ============================================================================
# AGR — Azuris Gemological Research  (certificate book: exactly 2 pages, NO QR)
# ============================================================================
AGR_FULL = "Azuris Gemological Research"
AGR_ABBR = "AGR"
GOLD_DK = (0.62, 0.49, 0.16)   # darker gold for legible text on ivory

# A5 portrait book pages
A5W = 148 * mm
A5H = 210 * mm

DISCLAIMER_AGR = (
    "This report identifies and describes the gemstone examined by Azuris Gemological "
    "Research (AGR). It is not a guarantee of price, investment value, or legal ownership."
)
CERT_TITLE = "GEMSTONE IDENTIFICATION CERTIFICATE"
ISSUANCE_STATEMENT = (
    "Azuris Gemological Research certifies that the gemstone described in this report has "
    "been examined and identified in accordance with established gemological practice."
)


def _agr_monogram(c, cx, cy, r):
    """Original AGR monogram: gold ring + navy 'AGR' (not copied from any reference)."""
    c.saveState()
    c.setLineWidth(1.1)
    c.setStrokeColorRGB(*GOLD)
    c.setFillColorRGB(*NAVY)
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.setStrokeColorRGB(*GOLD_SOFT)
    c.setLineWidth(0.5)
    c.circle(cx, cy, r - 1.4, stroke=1, fill=0)
    c.setFillColorRGB(*GOLD)
    c.setFont(HEADB, r * 0.9)
    c.drawCentredString(cx, cy - r * 0.32, "AGR")
    c.restoreState()


def _agr_gem_glyph(c, cx, cy, s):
    """Subtle premium decorative element (faceted diamond outline) upper-right."""
    c.saveState()
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.6)
    c.setStrokeAlpha(0.85)
    top = cy + s
    c.line(cx - s, cy, cx, top)
    c.line(cx + s, cy, cx, top)
    c.line(cx - s, cy, cx + s, cy)
    c.line(cx - s, cy, cx, cy - s)
    c.line(cx + s, cy, cx, cy - s)
    c.line(cx - s * 0.4, cy, cx, top)
    c.line(cx + s * 0.4, cy, cx, top)
    c.restoreState()


def _agr_head(c, cx, top_y, subtitle_en, subtitle_id=None, mono_r=8 * mm):
    """Centered AGR institutional header used on both book pages."""
    _agr_monogram(c, cx, top_y - mono_r, mono_r)
    y = top_y - 2 * mono_r - 5 * mm
    _tracked(c, 0, y, AGR_ABBR, HEADB, 20, NAVY, tracking=4.5, center=cx)
    y -= 6.4 * mm
    _tracked(c, 0, y, AGR_FULL.upper(), BODYB, 7.6, GOLD_DK, tracking=2.6, center=cx)
    y -= 6 * mm
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.8)
    c.line(cx - 22 * mm, y, cx + 22 * mm, y)
    y -= 6 * mm
    c.setFillColorRGB(*NAVY)
    c.setFont(HEAD, 11)
    c.drawCentredString(cx, y, subtitle_en)
    if subtitle_id:
        y -= 4.6 * mm
        c.setFillColorRGB(*TAUPE)
        c.setFont(HEAD, 8)
        c.drawCentredString(cx, y, subtitle_id)
        y -= 1 * mm
    return y - 4 * mm


def _agr_cover(c, w=A5W, h=A5H):
    """Page 1 — premium detail-free certificate-book front cover (official logo)."""
    cx = w / 2
    c.setFillColorRGB(*IVORY)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    _pattern(c, 0, w, 0, h, color=GOLD, alpha=0.05)

    # layered ornamental frame (outer + inner rule + corner diamonds)
    _double_frame_rect(c, w, h, inset=11 * mm)

    # official Azuris logo (balanced size, preserved aspect ratio, clear space)
    _draw_logo(c, _LOGO, cx, h - 56 * mm, 44 * mm)

    _wordmark(c, cx, h - 84 * mm, size=28, tracking=6.0, color=NAVY)
    _tracked(c, 0, h - 92 * mm, AGR_FULL.upper(), BODYB, 8, GOLD_DK, tracking=3.4, center=cx)

    _tracked(c, 0, h - 116 * mm, "GEMSTONE IDENTIFICATION", HEADB, 15.5, NAVY, tracking=1.4, center=cx)
    _tracked(c, 0, h - 126 * mm, "CERTIFICATE", HEADB, 15.5, NAVY, tracking=5.0, center=cx)

    _tracked(c, 0, h - 138 * mm, "OFFICIAL GEMOLOGICAL DOCUMENT", BODY, 7, TAUPE, tracking=3.0, center=cx)

    c.setStrokeColorRGB(*GOLD_SOFT)
    c.setLineWidth(0.5)
    c.line(cx - 16 * mm, 32 * mm, cx + 16 * mm, 32 * mm)
    _diamond(c, cx, 32 * mm, 0.9 * mm, GOLD)
    _tracked(c, 0, 26 * mm, "TRUSTED GEMOLOGICAL INSTITUTION", BODY, 5.6, SLATE, tracking=2.6, center=cx)


def _agr_details(c, cert, snap, signature_reader=None):
    """Page 2 — English certificate details + legality & signature (no QR/photo)."""
    c.setFillColorRGB(*IVORY)
    c.rect(0, 0, A5W, A5H, fill=1, stroke=0)
    _watermark(c, A5W / 2, A5H / 2, 58 * mm)
    _double_frame_rect(c, A5W, A5H)
    m = 12 * mm
    x = m
    w = A5W - 2 * m
    cx = A5W / 2

    # header — official logo + institution
    _draw_logo(c, _LOGO, x + 7 * mm, A5H - 21 * mm, 15 * mm)
    c.setFillColorRGB(*NAVY)
    c.setFont(HEADB, 13)
    c.drawString(x + 17 * mm, A5H - 18 * mm, AGR_FULL)
    _tracked(c, x + 17 * mm, A5H - 23 * mm, CERT_TITLE, BODYB, 5.4, GOLD_DK, tracking=1.0)
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.9)
    c.line(x, A5H - 27 * mm, x + w, A5H - 27 * mm)

    y = A5H - 32 * mm

    # registration number plate
    c.setFillColorRGB(*BEIGE_LT)
    c.setStrokeColorRGB(*GOLD_SOFT)
    c.setLineWidth(0.6)
    c.rect(x, y - 9 * mm, w, 9 * mm, fill=1, stroke=1)
    c.setFillColorRGB(*SLATE)
    c.setFont(BODYB, 5.6)
    c.drawString(x + 3 * mm, y - 3.6 * mm, "CERTIFICATE NUMBER")
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 11)
    c.drawRightString(x + w - 3 * mm, y - 6 * mm, cert["certificate_number"])
    y -= 14 * mm

    # detail fields — full width, only present values (no invented data)
    pairs = [
        ("Gemstone Name", snap.get("name")),
        ("Object Type", snap.get("object_type")),
        ("Species", snap.get("species")),
        ("Variety", snap.get("variety")),
        ("Carat Weight", f"{snap.get('carat')} ct" if snap.get("carat") else None),
        ("Measurements", snap.get("dimensions")),
        ("Shape", snap.get("shape")),
        ("Cut", snap.get("cut")),
        ("Colour", snap.get("color")),
        ("Transparency", snap.get("transparency")),
        ("Clarity", snap.get("clarity")),
        ("Treatment", snap.get("treatment")),
        ("Origin", snap.get("origin")),
        ("Date of Issue", (cert.get("issued_at") or "")[:10] or None),
        ("Examiner", snap.get("examiner")),
    ]
    pairs = [(k, v) for k, v in pairs if v not in (None, "", "None")]

    row_h = 6.0 * mm
    for i, (k, v) in enumerate(pairs):
        _field(c, x, w, y, k, v, val_size=7.8, zebra=(i % 2 == 0))
        y -= row_h

    # comment / conclusion
    comment = snap.get("conclusion") or snap.get("notes")
    if comment:
        y -= 1 * mm
        yb = _section_bar(c, x, x + w, y, "Comment")
        c.setFillColorRGB(*NAVY)
        for ln in _wrap(c, str(comment), BODY, 7.4, w)[:2]:
            c.setFont(BODY, 7.4)
            c.drawString(x, yb, ln)
            yb -= 4.0 * mm

    # ---------------- Legality & authorised signatory (fixed bottom band) ----------------
    leg = cert.get("legality_snapshot") or {}
    by = 56 * mm
    _section_bar(c, x, x + w, by, "Legality & Authorised Signatory")

    # left column — legality / accreditation
    lw = w * 0.54
    ly = by - 8 * mm
    leg_rows = [
        ("Accreditation", leg.get("certificate_name") or leg.get("name")),
        ("Accreditation No.", leg.get("certificate_number")),
        ("Issuing Institution", leg.get("issuer")),
    ]
    if leg.get("expiry_date"):
        leg_rows.append(("Valid Until", leg.get("expiry_date")))
    leg_rows = [(k, v) for k, v in leg_rows if v not in (None, "", "None")]
    if not leg_rows:
        leg_rows = [("Issuing Institution", AGR_FULL)]
    for k, v in leg_rows:
        c.setFillColorRGB(*SLATE)
        c.setFont(BODYB, 5.2)
        c.drawString(x, ly, k.upper())
        c.setFillColorRGB(*NAVY)
        c.setFont(BODY, 7.0)
        for ln in _wrap(c, str(v), BODY, 7.0, lw)[:2]:
            ly -= 3.6 * mm
            c.drawString(x, ly, ln)
        ly -= 4.4 * mm

    # right column — authorised signatory + signature image
    rx = x + w * 0.60
    rw = x + w - rx
    sig_line_y = 27 * mm
    if signature_reader is not None:
        try:
            iw, ih = signature_reader.getSize()
            r = min(rw / iw, (13 * mm) / ih)
            dw, dh = iw * r, ih * r
            c.drawImage(signature_reader, rx + (rw - dw) / 2, sig_line_y + 1.5 * mm,
                        width=dw, height=dh, mask="auto")
        except Exception:
            pass
    c.setStrokeColorRGB(*SLATE)
    c.setLineWidth(0.5)
    c.line(rx, sig_line_y, rx + rw, sig_line_y)
    signatory = leg.get("signatory_name") or "Azuris Gemological Research"
    position = leg.get("signatory_position") or "Authorised Signatory"
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 7.2)
    c.drawCentredString(rx + rw / 2, sig_line_y - 4.2 * mm, str(signatory))
    c.setFillColorRGB(*SLATE)
    c.setFont(BODY, 5.8)
    c.drawCentredString(rx + rw / 2, sig_line_y - 8.0 * mm, str(position))

    # issuance statement + disclaimer (very bottom)
    dy = 17 * mm
    c.setFillColorRGB(*GOLD_DK)
    for ln in _wrap(c, ISSUANCE_STATEMENT, BODY, 5.4, w)[:2]:
        c.setFont(BODY, 5.4)
        c.drawCentredString(cx, dy, ln)
        dy -= 2.9 * mm
    dy -= 0.8 * mm
    c.setFillColorRGB(*GREY)
    for ln in _wrap(c, DISCLAIMER_AGR, BODY, 4.8, w)[:2]:
        c.setFont(BODY, 4.8)
        c.drawCentredString(cx, dy, ln)
        dy -= 2.7 * mm


def _diamond(c, cx, cy, r, color=GOLD):
    """Small rotated-square gold ornament (corner / flanking detail)."""
    c.saveState()
    c.translate(cx, cy)
    c.rotate(45)
    c.setFillColorRGB(*color)
    c.rect(-r, -r, 2 * r, 2 * r, fill=1, stroke=0)
    c.restoreState()


def _wordmark(c, cx, y, size=27, tracking=5.5, color=NAVY):
    """Uppercase AZURIS wordmark with a refined gold underline flanked by diamonds."""
    right = _tracked(c, 0, y, "AZURIS", HEADB, size, color, tracking=tracking, center=cx)
    half = right - cx
    ry = y - size * 0.16 * mm - 2.6 * mm
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.9)
    c.line(cx - half + 2.4 * mm, ry, cx + half - 2.4 * mm, ry)
    _diamond(c, cx - half, ry, 0.9 * mm, GOLD)
    _diamond(c, cx + half, ry, 0.9 * mm, GOLD)
    return ry


def _double_frame_rect(c, w, h, color1=GOLD, color2=GOLD_SOFT, inset=6 * mm):
    """Layered ornamental frame: heavier outer rule, thin inner rule, corner diamonds."""
    c.saveState()
    c.setStrokeColorRGB(*color1)
    c.setLineWidth(1.2)
    c.rect(inset, inset, w - 2 * inset, h - 2 * inset)
    c.setStrokeColorRGB(*color2)
    c.setLineWidth(0.4)
    d = inset + 1.6 * mm
    c.rect(d, d, w - 2 * d, h - 2 * d)
    c.restoreState()
    for (dx, dy) in ((inset, inset), (w - inset, inset), (inset, h - inset), (w - inset, h - inset)):
        _diamond(c, dx, dy, 1.1 * mm, color1)


# ---------------------------------------------------------------- build (book)
def _reader(data: Optional[bytes]) -> Optional[ImageReader]:
    if not data:
        return None
    try:
        return ImageReader(BytesIO(data))
    except Exception:
        return None


def _demo_stamp_cover(c, w, h):
    """Strong diagonal SAMPLE stamp for the (data-free) cover page."""
    c.saveState()
    c.translate(w / 2, h / 2)
    c.rotate(32)
    c.setFillColorRGB(0.83, 0.16, 0.16)
    c.setFillAlpha(0.30)
    c.setFont(HEADB, 46)
    c.drawCentredString(0, 6 * mm, "SAMPLE")
    c.setFont(BODYB, 15)
    c.drawCentredString(0, -8 * mm, "NOT A VALID CERTIFICATE")
    c.restoreState()


def _demo_soft(c, w, h):
    """Very faint diagonal SAMPLE mark that does not obscure the details page."""
    c.saveState()
    c.translate(w / 2, h / 2)
    c.rotate(35)
    c.setFillColorRGB(0.83, 0.16, 0.16)
    c.setFillAlpha(0.07)
    c.setFont(HEADB, 62)
    c.drawCentredString(0, 0, "SAMPLE")
    c.restoreState()


def _sample_ribbon(c, w, y):
    """Small SAMPLE ribbon that does not cover important content."""
    c.saveState()
    pw = 58 * mm
    c.setFillColorRGB(0.83, 0.16, 0.16)
    c.roundRect(w / 2 - pw / 2, y - 6 * mm, pw, 6 * mm, 1.5 * mm, fill=1, stroke=0)
    _tracked(c, 0, y - 4.1 * mm, "SAMPLE — NOT VALID", BODYB, 7, (1, 1, 1), tracking=1.2, center=w / 2)
    c.restoreState()


def _agr_presentation(c, cert, snap, photo_reader):
    """Page 3 — gemstone presentation: large photograph + name + type + 'From AGR'."""
    c.setFillColorRGB(*IVORY)
    c.rect(0, 0, A5W, A5H, fill=1, stroke=0)
    _pattern(c, 0, A5W, 0, A5H, color=GOLD, alpha=0.045)
    _double_frame_rect(c, A5W, A5H)
    cx = A5W / 2

    _draw_logo(c, _LOGO, cx, A5H - 24 * mm, 26 * mm)
    _tracked(c, 0, A5H - 40 * mm, "CERTIFIED GEMSTONE", BODY, 7.5, GOLD_DK, tracking=3.2, center=cx)

    box_w, box_h = 104 * mm, 90 * mm
    bx = cx - box_w / 2
    by = A5H - 50 * mm - box_h
    c.setFillColorRGB(*BEIGE_LT)
    c.rect(bx - 2 * mm, by - 2 * mm, box_w + 4 * mm, box_h + 4 * mm, fill=1, stroke=0)
    if photo_reader is not None:
        try:
            iw, ih = photo_reader.getSize()
            r = min(box_w / iw, box_h / ih)
            dw, dh = iw * r, ih * r
            c.drawImage(photo_reader, cx - dw / 2, by + (box_h - dh) / 2,
                        width=dw, height=dh, mask="auto")
        except Exception:
            pass
    else:
        c.setFillColorRGB(*TAUPE)
        c.setFont(BODY, 8)
        c.drawCentredString(cx, by + box_h / 2, "No photograph on record")
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.9)
    c.rect(bx - 2 * mm, by - 2 * mm, box_w + 4 * mm, box_h + 4 * mm)

    ty = by - 14 * mm
    name = snap.get("name") or snap.get("name_en") or snap.get("name_id") or "Gemstone"
    c.setFillColorRGB(*NAVY)
    c.setFont(HEADB, 22)
    c.drawCentredString(cx, ty, str(name))
    gtype = snap.get("variety") or snap.get("species") or snap.get("object_type")
    if gtype:
        ty -= 8 * mm
        _tracked(c, 0, ty, str(gtype).upper(), BODY, 8.5, GOLD_DK, tracking=2.4, center=cx)

    ty -= 16 * mm
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.7)
    c.line(cx - 16 * mm, ty + 5 * mm, cx + 16 * mm, ty + 5 * mm)
    c.setFillColorRGB(*NAVY)
    c.setFont(HEAD, 14)
    c.drawCentredString(cx, ty - 2 * mm, "From AGR")


def _agr_back(c, cert):
    """Page 4 — minimal back cover: small logo, date, certificate number (no QR)."""
    c.setFillColorRGB(*IVORY)
    c.rect(0, 0, A5W, A5H, fill=1, stroke=0)
    _pattern(c, 0, A5W, 0, A5H, color=GOLD, alpha=0.05)
    _double_frame_rect(c, A5W, A5H, inset=11 * mm)

    cx = A5W / 2
    my = A5H / 2
    _draw_logo(c, _LOGO, cx, my + 24 * mm, 24 * mm)
    _wordmark(c, cx, my + 4 * mm, size=16, tracking=3.2, color=NAVY)
    _tracked(c, 0, my - 3 * mm, AGR_FULL.upper(), BODYB, 6, GOLD_DK, tracking=2.6, center=cx)
    c.setFillColorRGB(*SLATE)
    c.setFont(BODYB, 5.4)
    c.drawCentredString(cx, my - 13 * mm, "CERTIFICATE NUMBER")
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 11)
    c.drawCentredString(cx, my - 18 * mm, cert["certificate_number"])

    date = (cert.get("issued_at") or "")[:10]
    if date:
        c.setFillColorRGB(*SLATE)
        c.setFont(BODYB, 5.4)
        c.drawCentredString(cx, my - 28 * mm, "DATE OF ISSUE")
        c.setFillColorRGB(*NAVY)
        c.setFont(BODY, 9)
        c.drawCentredString(cx, my - 33 * mm, date)


def build_certificate_pdf(
    cert: dict,
    photo_bytes: Optional[bytes],
    signature_bytes: Optional[bytes] = None,
    demo: bool = False,
) -> bytes:
    """Exactly FOUR A5 pages, in order:
    1) detail-free premium front cover
    2) English certificate details + legality/signature block
    3) gemstone presentation (large photograph)
    4) minimal back cover (date + number).
    No QR / barcode on any page."""
    snap = cert.get("gemstone_snapshot") or {}
    photo_reader = _reader(photo_bytes)
    signature_reader = _reader(signature_bytes)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(A5W, A5H))

    _agr_cover(c)
    if demo:
        _demo_stamp_cover(c, A5W, A5H)
    c.showPage()

    _agr_details(c, cert, snap, signature_reader)
    if demo:
        _demo_soft(c, A5W, A5H)
    c.showPage()

    _agr_presentation(c, cert, snap, photo_reader)
    if demo:
        _sample_ribbon(c, A5W, A5H - 12 * mm)
    c.showPage()

    _agr_back(c, cert)
    if demo:
        _demo_soft(c, A5W, A5H)
    c.showPage()

    c.save()
    buf.seek(0)
    return buf.read()


def decode_photo(data_b64: Optional[str]) -> Optional[bytes]:
    if not data_b64:
        return None
    try:
        return base64.b64decode(data_b64)
    except Exception:
        return None


# ---------------------------------------------------------------- front-cover preview
# Single source of truth: the verification-result cover reuses the SAME _agr_cover()
# renderer as page 1 of the booklet, so the design can never drift.
def build_front_cover_pdf(cert: dict) -> bytes:
    """One A5 page containing ONLY the certificate-book front cover (detail-free)."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(A5W, A5H))
    _agr_cover(c)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


def render_front_cover_png(cert: dict, zoom: float = 2.2) -> bytes:
    """Rasterize the shared front-cover to a crisp PNG (PyMuPDF; no system poppler)."""
    import pymupdf  # self-contained wheel

    pdf = build_front_cover_pdf(cert)
    doc = pymupdf.open(stream=pdf, filetype="pdf")
    try:
        page = doc[0]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        return pix.tobytes("png")
    finally:
        doc.close()


# ============================================================================
# AGR premium certificate CARD — one printable landscape card, WITH QR
# Layout hierarchy adapted (not copied) from the supplied card references.
# ============================================================================
CARD_W = 105 * mm
CARD_H = 66 * mm


def _card_field(c, x, w, y, label, value, size=6.8, max_lines=1,
                label_color=SLATE, value_color=IVORY, value_font=BODY):
    c.setFillColorRGB(*label_color)
    c.setFont(BODYB, 4.6)
    c.drawString(x, y, label.upper())
    c.setFillColorRGB(*value_color)
    c.setFont(value_font, size)
    val = str(value)
    all_lines = _wrap(c, val, value_font, size, w)
    lines = all_lines[:max_lines]
    if lines and len(all_lines) > max_lines:
        last = lines[-1]
        while c.stringWidth(last + "…", value_font, size) > w and len(last) > 1:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    yy = y - 3.0 * mm
    for ln in lines:
        c.drawString(x, yy, ln)
        yy -= 3.0 * mm
    return yy


def build_card_pdf(cert: dict, photo_bytes: Optional[bytes], verify_url: str, sample: bool = False) -> bytes:
    """One-page premium AGR certificate card (105 x 66 mm) — deep navy / gold / ivory."""
    snap = cert.get("gemstone_snapshot") or {}
    number = cert["certificate_number"]
    qr_reader = _qr_image(verify_url)
    photo_reader = _reader(photo_bytes)

    LABEL = (0.60, 0.66, 0.75)  # muted blue-grey supporting labels

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(CARD_W, CARD_H))

    # --- Deep navy background + subtle security detail ---
    c.setFillColorRGB(*NAVY)
    c.rect(0, 0, CARD_W, CARD_H, fill=1, stroke=0)
    _pattern(c, 0, CARD_W, 0, CARD_H, color=GOLD, alpha=0.06)

    # thin gold frame
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.7)
    c.rect(2.4 * mm, 2.4 * mm, CARD_W - 4.8 * mm, CARD_H - 4.8 * mm)
    c.setStrokeColorRGB(*GOLD_SOFT)
    c.setLineWidth(0.3)
    c.rect(3.4 * mm, 3.4 * mm, CARD_W - 6.8 * mm, CARD_H - 6.8 * mm)

    # --- Header: official logo + AZURIS serif wordmark (single baseline grid) ---
    _draw_logo(c, _LOGO, 9 * mm, CARD_H - 8 * mm, 9.5 * mm)
    c.setFillColorRGB(*IVORY)
    c.setFont(HEADB, 11)
    c.drawString(15 * mm, CARD_H - 7.2 * mm, "AZURIS")
    _tracked(c, 15 * mm, CARD_H - 10.6 * mm, AGR_FULL.upper(), BODYB, 4.0, GOLD_SOFT, tracking=1.1)
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.5)
    c.line(5.5 * mm, CARD_H - 13.2 * mm, CARD_W - 5.5 * mm, CARD_H - 13.2 * mm)

    if sample:
        cw2 = 16.5 * mm
        c.setFillColorRGB(0.78, 0.22, 0.24)
        c.roundRect(CARD_W - 5.5 * mm - cw2, CARD_H - 10.4 * mm, cw2, 4.6 * mm, 1.0 * mm, fill=1, stroke=0)
        _tracked(c, 0, CARD_H - 7.5 * mm, "SAMPLE - NOT VALID", BODYB, 4.0, (1, 1, 1),
                 tracking=0.3, center=CARD_W - 5.5 * mm - cw2 / 2)

    top = CARD_H - 16.5 * mm
    lx = 5.5 * mm

    # --- Gemstone photograph (primary focus, left) ---
    ph_w, ph_h = 40 * mm, 30 * mm
    py = top - ph_h
    c.setFillColorRGB(*NAVY_LT)
    c.rect(lx - 1 * mm, py - 1 * mm, ph_w + 2 * mm, ph_h + 2 * mm, fill=1, stroke=0)
    if photo_reader is not None:
        try:
            iw, ih = photo_reader.getSize()
            r = min(ph_w / iw, ph_h / ih)
            dw, dh = iw * r, ih * r
            c.drawImage(photo_reader, lx + (ph_w - dw) / 2, py + (ph_h - dh) / 2,
                        width=dw, height=dh, mask="auto")
        except Exception:
            pass
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.7)
    c.rect(lx - 1 * mm, py - 1 * mm, ph_w + 2 * mm, ph_h + 2 * mm)

    # --- Right column: certificate number + fields ---
    rx = lx + ph_w + 5 * mm
    rw = CARD_W - rx - 6 * mm
    fy = top
    c.setFillColorRGB(*GOLD_SOFT)
    c.setFont(BODYB, 4.2)
    c.drawString(rx, fy, "CERTIFICATE NO.")
    c.setFillColorRGB(*IVORY)
    c.setFont(BODYB, 8.4)
    c.drawString(rx, fy - 4.6 * mm, number)
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.4)
    c.line(rx, fy - 6.6 * mm, rx + rw, fy - 6.6 * mm)
    fy -= 9.0 * mm

    fy = _card_field(c, rx, rw, fy, "Gemstone", snap.get("name") or "—",
                     size=8.0, label_color=LABEL, value_color=IVORY, value_font=HEADB) - 0.6 * mm
    for label, val in [
        ("Type", snap.get("variety") or snap.get("species") or snap.get("object_type")),
        ("Origin", snap.get("origin")),
        ("Date", (cert.get("issued_at") or "")[:10]),
        ("Comment", snap.get("conclusion") or snap.get("notes")),
    ]:
        if val in (None, "", "None"):
            continue
        fy = _card_field(c, rx, rw, fy, label, val, label_color=LABEL, value_color=IVORY) - 0.4 * mm

    # --- QR (discreet, on an ivory tile so it stays scannable) ---
    qr_s = 9 * mm
    pad = 0.9 * mm
    tile = qr_s + 2 * pad
    tile_x = lx - 1 * mm            # aligned with the gemstone-photo frame left edge
    tile_y = 5.5 * mm               # inside safe print margins
    c.setFillColorRGB(*IVORY)
    c.roundRect(tile_x, tile_y, tile, tile, 0.8 * mm, fill=1, stroke=0)
    c.drawImage(qr_reader, tile_x + pad, tile_y + pad, width=qr_s, height=qr_s, mask="auto")
    tile_cy = tile_y + tile / 2
    tx = tile_x + tile + 2.6 * mm
    c.setFillColorRGB(*LABEL)
    c.setFont(BODY, 3.6)
    c.drawString(tx, tile_cy + 1.4 * mm, "Scan to verify")
    c.drawString(tx, tile_cy - 1.6 * mm, "authenticity")

    # --- Authenticity footer (aligned to the right information grid) ---
    c.setFillColorRGB(*GOLD_SOFT)
    c.setFont(BODYB, 4.4)
    c.drawRightString(CARD_W - 6 * mm, 8.4 * mm, "AUTHENTIC GEMSTONE CERTIFICATE")
    c.setFillColorRGB(*LABEL)
    c.setFont(BODY, 3.8)
    c.drawRightString(CARD_W - 6 * mm, 5.6 * mm, "Issued by Azuris Gemological Research (AGR)")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


def render_card_png(cert: dict, photo_bytes: Optional[bytes], verify_url: str, zoom: float = 3.0) -> bytes:
    import pymupdf
    pdf = build_card_pdf(cert, photo_bytes, verify_url)
    doc = pymupdf.open(stream=pdf, filetype="pdf")
    try:
        pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        return pix.tobytes("png")
    finally:
        doc.close()
