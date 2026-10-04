"""Custom AGR card + certificate rendering overrides.

Keeps existing certificate data/workflow intact while applying the approved
warranty-card design and removing the visible CERTIFICATE NUMBER label from the
certificate back page. The actual certificate number remains unchanged.
"""

from io import BytesIO
from typing import Optional

import pymupdf
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from services import certificate_pdf as base


CARD_W = 105 * mm
CARD_H = 66 * mm


def _draw_faceted_diamond(c, cx, cy, w, h):
    """Decorative faceted diamond inspired by the approved card reference."""
    c.saveState()
    c.setStrokeColorRGB(0.72, 0.86, 1.0)
    c.setLineWidth(0.55)
    pts = [
        (cx - w * 0.50, cy + h * 0.12),
        (cx - w * 0.30, cy + h * 0.46),
        (cx + w * 0.28, cy + h * 0.45),
        (cx + w * 0.50, cy + h * 0.12),
        (cx, cy - h * 0.50),
    ]
    p = c.beginPath()
    p.moveTo(*pts[0])
    for x, y in pts[1:]:
        p.lineTo(x, y)
    p.close()
    c.setFillColorRGB(0.88, 0.94, 1.0)
    c.drawPath(p, fill=1, stroke=1)

    facets = [
        (pts[0], (cx, cy - h * 0.50)),
        (pts[1], (cx, cy - h * 0.50)),
        (pts[2], (cx, cy - h * 0.50)),
        (pts[3], (cx, cy - h * 0.50)),
        (pts[0], pts[2]),
        (pts[1], pts[3]),
        ((cx, cy + h * 0.12), (cx, cy - h * 0.50)),
    ]
    for a, b in facets:
        c.line(a[0], a[1], b[0], b[1])
    c.restoreState()


def build_card_pdf(
    cert: dict,
    photo_bytes: Optional[bytes],
    verify_url: str,
    sample: bool = False,
    signature_bytes: Optional[bytes] = None,
) -> bytes:
    """Two-page warranty card. Front follows the supplied reference; back is plain."""
    number = str(cert.get("certificate_number") or "")
    qr_reader = base._qr_image(verify_url, border=2)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(CARD_W, CARD_H))

    # FRONT -----------------------------------------------------------------
    c.setFillColorRGB(0.008, 0.018, 0.040)
    c.rect(0, 0, CARD_W, CARD_H, fill=1, stroke=0)

    # Glossy lower blue band and luminous divider.
    c.setFillColorRGB(0.015, 0.085, 0.175)
    c.rect(0, 0, CARD_W, 13.2 * mm, fill=1, stroke=0)
    c.setStrokeColorRGB(0.10, 0.46, 1.0)
    c.setLineWidth(0.75)
    c.line(0, 13.2 * mm, CARD_W, 13.2 * mm)

    # Left geometric motif.
    c.saveState()
    c.setStrokeColorRGB(0.07, 0.20, 0.43)
    c.setLineWidth(1.0)
    c.line(0, 48 * mm, 8 * mm, 48 * mm)
    c.line(8 * mm, 48 * mm, 15 * mm, 41 * mm)
    c.line(15 * mm, 41 * mm, 15 * mm, 28 * mm)
    c.line(0, 9 * mm, 8 * mm, 9 * mm)
    c.line(8 * mm, 9 * mm, 15 * mm, 16 * mm)
    c.line(15 * mm, 16 * mm, 15 * mm, 24 * mm)
    c.restoreState()

    # Upper-right blue light arcs.
    c.saveState()
    c.setStrokeColorRGB(0.08, 0.28, 0.72)
    c.setLineWidth(0.65)
    c.arc(57 * mm, 33 * mm, 111 * mm, 87 * mm, 18, 78)
    c.arc(60 * mm, 31 * mm, 115 * mm, 88 * mm, 20, 75)
    c.restoreState()

    # Decorative diamond.
    _draw_faceted_diamond(c, 88 * mm, 47 * mm, 24 * mm, 23 * mm)

    # AGR emblem.
    base._draw_logo(c, base._LOGO, CARD_W / 2, 56.2 * mm, 13.5 * mm)

    # Main brand hierarchy.
    base._tracked(c, 0, 42.2 * mm, "AZURIS", base.HEADB, 22, base.IVORY, tracking=2.2, center=CARD_W / 2)
    base._tracked(c, 0, 37.1 * mm, "GEMOLOGICAL RESEARCH", base.BODYB, 7.8, (0.08, 0.37, 0.92), tracking=1.15, center=CARD_W / 2)

    c.setFillColorRGB(*base.IVORY)
    c.setFont(base.HEAD, 6.7)
    c.drawCentredString(CARD_W / 2, 32.3 * mm, "Created by AZURIS")
    c.setFont(base.HEAD, 5.4)
    c.drawCentredString(CARD_W / 2, 28.5 * mm, "Limited Lifetime Warranty and Certificate Of Authenticity")
    c.setFont(base.HEAD, 5.8)
    c.drawCentredString(CARD_W / 2, 24.5 * mm, "REGISTER your AZURIS purchase")

    # QR / barcode block — always points to the certificate verification URL.
    qx, qy, qs = 4.1 * mm, 2.7 * mm, 18.2 * mm
    c.setFillColorRGB(1, 1, 1)
    c.rect(qx, qy, qs, qs, fill=1, stroke=0)
    c.setStrokeColorRGB(0.10, 0.45, 1.0)
    c.setLineWidth(0.65)
    c.rect(qx - 0.7 * mm, qy - 0.7 * mm, qs + 1.4 * mm, qs + 1.4 * mm, fill=0, stroke=1)
    c.drawImage(qr_reader, qx + 0.6 * mm, qy + 0.6 * mm, width=qs - 1.2 * mm, height=qs - 1.2 * mm, mask="auto")

    # Dynamic card content: ID only.
    c.setFillColorRGB(*base.IVORY)
    c.setFont(base.HEADB, 10.4)
    c.drawString(28.5 * mm, 6.1 * mm, "Warranty ID :")
    c.setFont(base.BODYB, 7.2)
    c.drawString(56.5 * mm, 6.4 * mm, number)

    if sample:
        base._sample_stamp(c, CARD_W * 0.73, CARD_H * 0.47, 8, 0.25, 14)

    c.showPage()

    # BACK ------------------------------------------------------------------
    # Intentionally plain, per approved requirement.
    c.setFillColorRGB(0.008, 0.018, 0.040)
    c.rect(0, 0, CARD_W, CARD_H, fill=1, stroke=0)
    c.showPage()

    c.save()
    buf.seek(0)
    return buf.read()


def build_certificate_pdf(
    cert: dict,
    photo_bytes: Optional[bytes],
    signature_bytes: Optional[bytes] = None,
    demo: bool = False,
) -> bytes:
    """Use the existing certificate renderer and remove only the circled label."""
    pdf = base.build_certificate_pdf(cert, photo_bytes, signature_bytes, demo)
    doc = pymupdf.open(stream=pdf, filetype="pdf")
    try:
        # The circled text is on the minimal back page. Keep the certificate ID itself.
        for page in doc:
            for rect in page.search_for("CERTIFICATE NUMBER"):
                page.add_redact_annot(rect, fill=(0.98, 0.976, 0.965))
            page.apply_redactions()
        return doc.tobytes(garbage=4, deflate=True)
    finally:
        doc.close()


def decode_photo(data_b64):
    return base.decode_photo(data_b64)
