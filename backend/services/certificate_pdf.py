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

    # certificate number plate (ivory on navy)
    plate_w, plate_h = 48 * mm, 12.5 * mm
    px, py = cx - plate_w / 2, PAGE_H - 84 * mm
    c.setFillColorRGB(*IVORY)
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.7)
    c.rect(px, py, plate_w, plate_h, fill=1, stroke=1)
    _tracked(c, 0, py + plate_h - 4 * mm, "NOMOR SERTIFIKAT", BODY, 4.6, TAUPE, tracking=1.0, center=cx)
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 11.5)
    c.drawCentredString(cx, py + 2.4 * mm, number)

    c.setFillColorRGB(*BEIGE)
    c.setFont(BODY, 6.5)
    c.drawCentredString(cx, py - 5.5 * mm, f"Tahun Terbit {year}" if year else "")


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


# ---------------------------------------------------------------- build
def build_certificate_pdf(cert: dict, photo_bytes: Optional[bytes]) -> bytes:
    snap = cert.get("gemstone_snapshot") or {}
    number = cert["certificate_number"]
    year = (cert.get("issued_at") or "")[:4] or ""
    token_url = cert["qr_url"]
    website = cert.get("website") or "azuris-gemological.com"
    contact = _fmt_phone(cert.get("whatsapp") or "")

    photo_reader = None
    if photo_bytes:
        try:
            photo_reader = ImageReader(BytesIO(photo_bytes))
        except Exception:
            photo_reader = None
    qr_reader = _qr_image(token_url)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))

    # Page 1 — outside spread: back (left) | front (right)
    c.setFillColorRGB(*IVORY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    _panel_back(c, 0, FOLD_X, cert.get("version"), website, contact)
    _panel_front(c, FOLD_X, PAGE_W, number, year)
    _fold_guide(c)
    c.showPage()

    # Page 2 — inside spread: info (left) | gemstone (right)
    c.setFillColorRGB(*IVORY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    _panel_info(c, 0, FOLD_X, cert, snap, qr_reader)
    _panel_gemstone(c, FOLD_X, PAGE_W, snap, photo_reader, number)
    _fold_guide(c)
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
# Single source of truth: the preview reuses the SAME _panel_front() renderer as
# the booklet, so the certificate design can never drift between PDF and preview.
def build_front_cover_pdf(cert: dict) -> bytes:
    """One-page PDF (74 x 105 mm) containing ONLY the certificate front cover."""
    number = cert["certificate_number"]
    year = (cert.get("issued_at") or "")[:4] or ""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(FOLD_X, PAGE_H))
    c.setFillColorRGB(*IVORY)
    c.rect(0, 0, FOLD_X, PAGE_H, fill=1, stroke=0)
    _panel_front(c, 0, FOLD_X, number, year)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


def render_front_cover_png(cert: dict, zoom: float = 3.0) -> bytes:
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
