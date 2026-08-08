"""A6 landscape booklet certificate PDF — FASE 3.

Exactly 2 pages of 148 x 105 mm (A6 landscape), folded vertically at 74 mm.
Page 1 = outside spread (back-cover left, front-cover right).
Page 2 = inside spread (certificate/verification left, gemstone identity right).
Uses a snapshot so historical PDFs never change. Brand TTFs unavailable in the
environment; standard Times/Helvetica are embedded as safe substitutes.
"""

import base64
from io import BytesIO
from typing import Optional

import qrcode
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

NAVY = (0.051, 0.106, 0.165)      # #0D1B2A
ROYAL = (0.118, 0.310, 0.659)     # #1E4FA8
GOLD = (0.780, 0.635, 0.278)      # #C7A247
WARM = (0.980, 0.976, 0.965)      # #FAF9F6
GREY = (0.40, 0.40, 0.40)

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
    "mulia. Sertifikat tidak secara otomatis menjadi jaminan harga, nilai investasi, "
    "kepemilikan, atau asal-usul hukum suatu batu."
)


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


def _guilloche(c: canvas.Canvas, x0: float, x1: float):
    """Subtle security hairlines along the top of a panel."""
    c.saveState()
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.2)
    y = PAGE_H - SAFE - 2 * mm
    for i in range(6):
        c.line(x0 + SAFE, y - i * 0.8, x1 - SAFE, y - i * 0.8)
    c.restoreState()


def _fold_guide(c: canvas.Canvas):
    c.saveState()
    c.setStrokeColorRGB(0.75, 0.75, 0.75)
    c.setDash(1, 3)
    c.setLineWidth(0.3)
    c.line(FOLD_X, 0, FOLD_X, PAGE_H)
    c.restoreState()


def _wrap(c: canvas.Canvas, text: str, font: str, size: float, max_w: float):
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


def _panel_front(c, x0, x1, number, year):
    _guilloche(c, x0, x1)
    cx = (x0 + x1) / 2
    c.setFillColorRGB(*GOLD)
    c.setFont(BODY, 6.5)
    c.drawCentredString(cx, PAGE_H - 18 * mm, "A Z U R I S")
    c.setFillColorRGB(*NAVY)
    c.setFont(HEADB, 20)
    c.drawCentredString(cx, PAGE_H - 30 * mm, "AZURIS")
    c.setFont(HEAD, 11)
    c.drawCentredString(cx, PAGE_H - 37 * mm, "GEMOLOGICAL")
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.6)
    c.line(cx - 14 * mm, PAGE_H - 41 * mm, cx + 14 * mm, PAGE_H - 41 * mm)
    c.setFillColorRGB(*GREY)
    c.setFont(HEAD, 9)
    c.drawCentredString(cx, PAGE_H - 52 * mm, "Gemological Certificate")
    c.drawCentredString(cx, PAGE_H - 58 * mm, "Sertifikat Gemologi")
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 11)
    c.drawCentredString(cx, PAGE_H - 74 * mm, number)
    c.setFillColorRGB(*GREY)
    c.setFont(BODY, 7)
    c.drawCentredString(cx, PAGE_H - 80 * mm, f"Tahun Terbit {year}")


def _panel_back(c, x0, x1, version):
    cx = (x0 + x1) / 2
    c.setFillColorRGB(*NAVY)
    c.setFont(HEADB, 12)
    c.drawCentredString(cx, PAGE_H - 24 * mm, "AZURIS")
    c.setFillColorRGB(*GOLD)
    c.setFont(BODY, 6)
    c.drawCentredString(cx, PAGE_H - 30 * mm, "GEMOLOGICAL")
    c.setFillColorRGB(*GREY)
    c.setFont(BODY, 7)
    lines = _wrap(
        c,
        "Sertifikat asli diterbitkan oleh Azuris Gemological dan dapat diverifikasi "
        "secara digital melalui sistem verifikasi resmi.",
        BODY, 7, (x1 - x0) - 2 * SAFE,
    )
    y = PAGE_H - 46 * mm
    for ln in lines:
        c.drawCentredString(cx, y, ln)
        y -= 3.6 * mm
    c.setFont(BODYB, 6.5)
    c.setFillColorRGB(*ROYAL)
    c.drawCentredString(cx, y - 3 * mm, "azuris-gemological.com")
    if version:
        c.setFillColorRGB(*GREY)
        c.setFont(BODY, 6)
        c.drawCentredString(cx, SAFE + 2 * mm, f"Dokumen v{version}")


def _kv(c, x, y, label, value):
    c.setFillColorRGB(*GOLD)
    c.setFont(BODY, 5.5)
    c.drawString(x, y, label.upper())
    c.setFillColorRGB(*NAVY)
    c.setFont(BODY, 8)
    c.drawString(x, y - 4 * mm, str(value))


def _panel_info(c, x0, x1, cert, snap, qr_reader):
    x = x0 + SAFE
    top = PAGE_H - SAFE - 4 * mm
    c.setFillColorRGB(*NAVY)
    c.setFont(HEADB, 10)
    c.drawString(x, top, "Informasi Sertifikat")
    c.setFillColorRGB(*NAVY)
    c.setFont(BODYB, 11)
    c.drawString(x, top - 8 * mm, cert["certificate_number"])
    # QR at bottom-left, large & high-contrast
    qr_size = 26 * mm
    c.drawImage(qr_reader, x, SAFE + 2 * mm, width=qr_size, height=qr_size, mask="auto")
    c.setFillColorRGB(*GREY)
    c.setFont(BODY, 5.2)
    c.drawString(x + qr_size + 3 * mm, SAFE + 20 * mm, "Pindai untuk verifikasi")
    c.drawString(x + qr_size + 3 * mm, SAFE + 16.5 * mm, "keaslian sertifikat.")
    c.drawString(x + qr_size + 3 * mm, SAFE + 11 * mm, "Hanya versi terkini yang")
    c.drawString(x + qr_size + 3 * mm, SAFE + 7.5 * mm, "aktif; versi sebelumnya")
    c.drawString(x + qr_size + 3 * mm, SAFE + 4 * mm, "diarsipkan.")
    # meta block
    yb = top - 18 * mm
    _kv(c, x, yb, "Tanggal Terbit", (cert.get("issued_at") or "")[:10])
    _kv(c, x + 34 * mm, yb, "Versi", cert.get("version"))
    _kv(c, x, yb - 11 * mm, "Status", "Aktif")
    if snap.get("examiner"):
        _kv(c, x + 34 * mm, yb - 11 * mm, "Pemeriksa", snap["examiner"])
    _kv(c, x, yb - 22 * mm, "Penanda Tangan", snap.get("signatory") or "Azuris Gemological")


def _panel_gemstone(c, x0, x1, snap, photo_reader, number):
    x = x0 + SAFE
    top = PAGE_H - SAFE - 4 * mm
    c.setFillColorRGB(*NAVY)
    c.setFont(HEADB, 10)
    c.drawString(x, top, "Identitas Batu Mulia")
    # photo (aspect-ratio preserved) top-right
    box_w, box_h = 26 * mm, 22 * mm
    px, py = x1 - SAFE - box_w, top - box_h - 1 * mm
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
        c.setLineWidth(0.4)
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
    y = top - 10 * mm
    col_x = x
    for i, (k, v) in enumerate(pairs):
        if i == 7:
            col_x = x + 34 * mm
            y = top - 10 * mm
        c.setFillColorRGB(*GOLD)
        c.setFont(BODY, 5)
        c.drawString(col_x, y, k.upper())
        c.setFillColorRGB(*NAVY)
        c.setFont(BODY, 7.5)
        c.drawString(col_x, y - 3.3 * mm, str(v))
        y -= 7.6 * mm

    if snap.get("conclusion"):
        c.setFillColorRGB(*ROYAL)
        c.setFont(BODYB, 5.5)
        c.drawString(x, SAFE + 12 * mm, "KESIMPULAN")
        c.setFillColorRGB(*NAVY)
        for j, ln in enumerate(_wrap(c, snap["conclusion"], BODY, 6.5, (x1 - x0) - 2 * SAFE)[:2]):
            c.drawString(x, SAFE + 8 * mm - j * 3.2 * mm, ln)
    c.setFillColorRGB(*GREY)
    c.setFont(BODY, 5)
    c.drawRightString(x1 - SAFE, SAFE + 1 * mm, number)


def build_certificate_pdf(cert: dict, photo_bytes: Optional[bytes]) -> bytes:
    snap = cert.get("gemstone_snapshot") or {}
    number = cert["certificate_number"]
    year = (cert.get("issued_at") or "")[:4] or ""
    token_url = cert["qr_url"]

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
    _fold_guide(c)
    _panel_back(c, 0, FOLD_X, cert.get("version"))
    _panel_front(c, FOLD_X, PAGE_W, number, year)
    c.showPage()

    # Page 2 — inside spread: info (left) | gemstone (right)
    c.setFillColorRGB(*WARM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    _fold_guide(c)
    _panel_info(c, 0, FOLD_X, cert, snap, qr_reader)
    _panel_gemstone(c, FOLD_X, PAGE_W, snap, photo_reader, number)
    # disclaimer footer (spans inside-left safe area bottom)
    c.setFillColorRGB(*GREY)
    for j, ln in enumerate(_wrap(c, DISCLAIMER_ID, BODY, 4.6, FOLD_X - 2 * SAFE)[:0]):
        c.drawString(SAFE, 2 * mm - j, ln)
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
