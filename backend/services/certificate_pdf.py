"""A6 landscape booklet certificate PDF — FASE 3.1 (visual refinement).

Exactly 2 pages of 148 x 105 mm (A6 landscape), folded vertically at 74 mm.
Page 1 = outside spread (back-cover left, front-cover right).
Page 2 = inside spread (certificate/verification left, gemstone identity right).

Original AZURIS GEMOLOGICAL visual system: warm-white dominant, champagne-gold
section bars & ornament, navy typography, royal blue used sparingly. Uses an
immutable snapshot so historical PDFs never change. Brand TTFs are unavailable in
the environment, so the 14 standard PDF-safe fonts (Times/Helvetica) are used and
a premium hierarchy is built from size / weight / spacing / capitalization.
"""

import base64
import math
from io import BytesIO
from typing import Optional

import qrcode
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

NAVY = (0.051, 0.106, 0.165)      # #0D1B2A
ROYAL = (0.118, 0.310, 0.659)     # #1E4FA8
GOLD = (0.780, 0.635, 0.278)      # #C7A247
GOLD_SOFT = (0.870, 0.780, 0.560)
WARM = (0.980, 0.976, 0.965)      # #FAF9F6
CREAM = (0.965, 0.949, 0.906)     # champagne tint block
GREY = (0.40, 0.40, 0.40)
INK = (0.13, 0.15, 0.19)

PAGE_W = 148 * mm
PAGE_H = 105 * mm
FOLD_X = 74 * mm
SAFE = 5 * mm

HEAD = "Times-Roman"
HEADB = "Times-Bold"
BODY = "Helvetica"
BODYB = "Helvetica-Bold"

DISCLAIMER_ID = (
    "Sertifikat gemologi merupakan laporan hasil pemeriksaan dan identifikasi batu "
    "mulia. Sertifikat ini bukan merupakan jaminan harga, nilai investasi, kepemilikan, "
    "atau asal-usul hukum atas suatu batu."
)


# ---------------------------------------------------------------- primitives
def _qr_image(url: str) -> ImageReader:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,  # quiet zone
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(13, 27, 42), back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def _tracked(c, x, y, text, font, size, color, tracking=0.0, center=None):
    """Draw letter-spaced text for an elegant, formal feel."""
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


def _pattern(c, x0, x1, y0, y1, alpha=0.05):
    """Subtle scallop/guilloche-inspired security pattern (print-safe, low opacity)."""
    c.saveState()
    c.setStrokeColorRGB(*GOLD)
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


def _frame(c, x0, x1, inset=3 * mm):
    """Thin double gold frame within the panel safe area."""
    c.saveState()
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.8)
    c.rect(x0 + inset, inset, (x1 - x0) - 2 * inset, PAGE_H - 2 * inset)
    c.setStrokeColorRGB(*GOLD_SOFT)
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


def _emblem(c, cx, cy, r):
    """Original Azuris faceted round-brilliant monogram (gold ring + gem facets)."""
    c.saveState()
    c.setLineJoin(1)
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.9)
    c.circle(cx, cy, r)
    c.setLineWidth(0.35)
    c.circle(cx, cy, r * 0.88)

    n = 8
    rg = r * 0.60
    girdle = [
        (cx + rg * math.cos(math.pi / 8 + i * math.pi / 4),
         cy + rg * math.sin(math.pi / 8 + i * math.pi / 4))
        for i in range(n)
    ]
    rt = rg * 0.5
    table = [
        (cx + rt * math.cos(math.pi / 8 + i * math.pi / 4),
         cy + rt * math.sin(math.pi / 8 + i * math.pi / 4))
        for i in range(n)
    ]
    c.setStrokeColorRGB(*NAVY)
    c.setLineWidth(0.6)
    p = c.beginPath()
    p.moveTo(*girdle[0])
    for pt in girdle[1:]:
        p.lineTo(*pt)
    p.close()
    c.drawPath(p)
    c.setLineWidth(0.4)
    tp = c.beginPath()
    tp.moveTo(*table[0])
    for pt in table[1:]:
        tp.lineTo(*pt)
    tp.close()
    c.drawPath(tp)
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.3)
    for i in range(n):
        c.line(table[i][0], table[i][1], girdle[i][0], girdle[i][1])
    c.restoreState()


def _section_bar(c, x0, x1, y, text, h=4.8 * mm):
    """Champagne-gold section header bar with warm-white tracked label."""
    c.setFillColorRGB(*GOLD)
    c.rect(x0, y - h, x1 - x0, h, fill=1, stroke=0)
    _tracked(c, x0 + 2.5 * mm, y - h + 1.5 * mm, text.upper(), BODYB, 6.5, WARM, tracking=0.6)
    return y - h - 2.4 * mm


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


def _field(c, x, w, y, label, value, val_size=8.0):
    """Label (left) · dotted gold leader · value (right-aligned) — report style."""
    c.setFillColorRGB(*GREY)
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
    _pattern(c, x0, x1, 0, PAGE_H, alpha=0.05)
    _frame(c, x0, x1)
    cx = (x0 + x1) / 2

    _emblem(c, cx, PAGE_H - 26 * mm, 9 * mm)

    _tracked(c, 0, PAGE_H - 45 * mm, "AZURIS", HEADB, 22, NAVY, tracking=2.2, center=cx)
    _tracked(c, 0, PAGE_H - 51 * mm, "GEMOLOGICAL", BODY, 7.5, GOLD, tracking=3.6, center=cx)

    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.7)
    c.line(cx - 16 * mm, PAGE_H - 55 * mm, cx + 16 * mm, PAGE_H - 55 * mm)

    c.setFillColorRGB(*INK)
    c.setFont(HEAD, 10.5)
    c.drawCentredString(cx, PAGE_H - 63 * mm, "Gemological Certificate")
    c.setFillColorRGB(*GREY)
    c.setFont(HEAD, 8.5)
    c.drawCentredString(cx, PAGE_H - 68.5 * mm, "Sertifikat Gemologi")

    # certificate number plate
    plate_w = 46 * mm
    plate_h = 12 * mm
    px = cx - plate_w / 2
    py = PAGE_H - 86 * mm
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.6)
    c.setFillColorRGB(*WARM)
    c.rect(px, py, plate_w, plate_h, fill=1, stroke=1)
    _tracked(c, 0, py + plate_h - 4 * mm, "NOMOR SERTIFIKAT", BODY, 4.6, GREY, tracking=0.8, center=cx)
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 11)
    c.drawCentredString(cx, py + 2.4 * mm, number)

    c.setFillColorRGB(*GREY)
    c.setFont(BODY, 6.5)
    c.drawCentredString(cx, py - 5 * mm, f"Tahun Terbit {year}" if year else "")


def _panel_back(c, x0, x1, version, website, contact):
    # light champagne block for a refined "cover" feel (not dark navy)
    c.setFillColorRGB(*CREAM)
    c.rect(x0 + 3 * mm, 3 * mm, (x1 - x0) - 6 * mm, PAGE_H - 6 * mm, fill=1, stroke=0)
    _pattern(c, x0, x1, 0, PAGE_H, alpha=0.06)
    _frame(c, x0, x1)
    cx = (x0 + x1) / 2
    inner = (x1 - x0) - 2 * (SAFE + 2 * mm)
    lx = x0 + SAFE + 2 * mm

    _emblem(c, cx, PAGE_H - 20 * mm, 6.5 * mm)
    _tracked(c, 0, PAGE_H - 32 * mm, "AZURIS GEMOLOGICAL", BODYB, 8, NAVY, tracking=1.2, center=cx)

    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.5)
    c.line(cx - 12 * mm, PAGE_H - 36 * mm, cx + 12 * mm, PAGE_H - 36 * mm)

    _tracked(c, 0, PAGE_H - 42 * mm, "KEASLIAN & VERIFIKASI", BODYB, 5.6, GOLD, tracking=1.0, center=cx)
    c.setFillColorRGB(*GREY)
    stmt = (
        "Sertifikat ini diterbitkan resmi oleh Azuris Gemological dan dilengkapi kode "
        "keamanan unik serta kode QR untuk verifikasi digital keasliannya."
    )
    y = PAGE_H - 47 * mm
    for ln in _wrap(c, stmt, BODY, 6.5, inner)[:4]:
        c.setFont(BODY, 6.5)
        c.drawCentredString(cx, y, ln)
        y -= 3.6 * mm

    steps = [
        "1.  Pindai kode QR pada sertifikat, atau",
        "2.  Buka situs resmi Azuris Gemological, lalu",
        "3.  Masukkan Nomor Sertifikat & Kode Keamanan.",
    ]
    y -= 2 * mm
    c.setFillColorRGB(*NAVY)
    for s in steps:
        c.setFont(BODY, 6)
        c.drawString(lx, y, s)
        y -= 3.6 * mm

    # contact block
    c.setFillColorRGB(*ROYAL)
    c.setFont(BODYB, 6.5)
    c.drawCentredString(cx, SAFE + 14 * mm, website or "azuris-gemological.com")
    if contact:
        c.setFillColorRGB(*GREY)
        c.setFont(BODY, 6)
        c.drawCentredString(cx, SAFE + 10 * mm, f"WhatsApp {contact}")

    c.setFillColorRGB(*GREY)
    c.setFont(BODY, 5.2)
    v = f"Dokumen v{version}" if version else ""
    c.drawCentredString(cx, SAFE + 3 * mm, f"{v}   Azuris Gemological".strip())


def _panel_info(c, x0, x1, cert, snap, qr_reader):
    _pattern(c, x0, x1, PAGE_H - 12 * mm, PAGE_H, alpha=0.04)
    x = x0 + SAFE
    w = (x1 - x0) - 2 * SAFE
    top = PAGE_H - SAFE - 1 * mm

    y = _section_bar(c, x, x1 - SAFE, top, "Sertifikat & Verifikasi")

    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 12)
    c.drawString(x, y - 4 * mm, cert["certificate_number"])
    y -= 9 * mm

    rows = [
        ("Tanggal Terbit", (cert.get("issued_at") or "")[:10] or "-"),
        ("Versi Dokumen", str(cert.get("version") or 1)),
        ("Status", "Aktif — Versi Terkini"),
    ]
    if snap.get("examiner"):
        rows.append(("Pemeriksa / Gemolog", snap["examiner"]))
    rows.append(("Penanda Tangan", snap.get("signatory") or "Azuris Gemological"))
    for label, val in rows:
        _field(c, x, w, y, label, val, val_size=7.6)
        y -= 6.2 * mm

    # authorized signature line
    y -= 1 * mm
    c.setStrokeColorRGB(*GREY)
    c.setLineWidth(0.4)
    c.line(x, y, x + 30 * mm, y)
    c.setFillColorRGB(*GREY)
    c.setFont(BODY, 5)
    c.drawString(x, y - 3.2 * mm, "Tanda Tangan Berwenang")

    # disclaimer (placed in the mid whitespace, well inside the safe area)
    c.setFillColorRGB(*GREY)
    dy = y - 9 * mm
    for ln in _wrap(c, DISCLAIMER_ID, BODY, 4.8, w)[:3]:
        c.setFont(BODY, 4.8)
        c.drawString(x, dy, ln)
        dy -= 3 * mm

    # QR block bottom
    qr_size = 24 * mm
    qy = SAFE + 1 * mm
    c.setStrokeColorRGB(*GOLD_SOFT)
    c.setLineWidth(0.4)
    c.rect(x - 0.6 * mm, qy - 0.6 * mm, qr_size + 1.2 * mm, qr_size + 1.2 * mm)
    c.drawImage(qr_reader, x, qy, width=qr_size, height=qr_size, mask="auto")
    tx = x + qr_size + 3.5 * mm
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 5.6)
    c.drawString(tx, qy + qr_size - 2 * mm, "VERIFIKASI DIGITAL")
    c.setFillColorRGB(*GREY)
    c.setFont(BODY, 5.4)
    for i, ln in enumerate([
        "Pindai kode QR untuk memeriksa",
        "keaslian sertifikat secara resmi.",
        "Hanya versi terkini yang aktif;",
        "versi sebelumnya diarsipkan.",
    ]):
        c.drawString(tx, qy + qr_size - 6 * mm - i * 3.4 * mm, ln)


def _panel_gemstone(c, x0, x1, snap, photo_reader, number):
    _pattern(c, x0, x1, PAGE_H - 12 * mm, PAGE_H, alpha=0.04)
    x = x0 + SAFE
    w = (x1 - x0) - 2 * SAFE
    top = PAGE_H - SAFE - 1 * mm

    y0 = _section_bar(c, x, x1 - SAFE, top, "Identitas Batu Mulia")

    # photo top-right (aspect preserved)
    box_w, box_h = 26 * mm, 22 * mm
    px, py = x1 - SAFE - box_w, y0 - box_h + 1 * mm
    if photo_reader is not None:
        try:
            iw, ih = photo_reader.getSize()
            ratio = min(box_w / iw, box_h / ih)
            dw, dh = iw * ratio, ih * ratio
            c.drawImage(photo_reader, px + (box_w - dw) / 2, py + (box_h - dh) / 2,
                        width=dw, height=dh, mask="auto")
        except Exception:
            pass
        c.setStrokeColorRGB(*GOLD)
        c.setLineWidth(0.5)
        c.rect(px, py, box_w, box_h)

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

    # First rows sit to the LEFT of the photo (narrow), then full width once below photo.
    photo_bottom = py if photo_reader is not None else PAGE_H
    narrow_w = (px - x - 2 * mm) if photo_reader is not None else w
    y = y0 - 2 * mm
    for k, v in pairs:
        full = y < photo_bottom - 1 * mm
        fw = w if full else max(narrow_w, 22 * mm)
        _field(c, x, fw, y, k, v, val_size=7.2)
        y -= 5.6 * mm

    # conclusion
    if snap.get("conclusion"):
        yb = _section_bar(c, x, x1 - SAFE, max(y - 1 * mm, SAFE + 15 * mm), "Kesimpulan Pemeriksaan")
        c.setFillColorRGB(*NAVY)
        for j, ln in enumerate(_wrap(c, snap["conclusion"], BODY, 6.6, w)[:2]):
            c.setFont(BODY, 6.6)
            c.drawString(x, yb - j * 3.4 * mm, ln)

    c.setFillColorRGB(*GREY)
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
    c.setFillColorRGB(*WARM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    _panel_back(c, 0, FOLD_X, cert.get("version"), website, contact)
    _panel_front(c, FOLD_X, PAGE_W, number, year)
    _fold_guide(c)
    c.showPage()

    # Page 2 — inside spread: info (left) | gemstone (right)
    c.setFillColorRGB(*WARM)
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
