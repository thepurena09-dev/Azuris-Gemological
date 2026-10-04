"""AGR card/certificate rendering overrides.

The front card uses the approved artwork as its background. Only the QR code
and Warranty ID are generated dynamically. The back uses a matching navy/blue
visual language without text, logo, or QR.
"""

import os
from io import BytesIO
from typing import Optional

import pymupdf
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from services import certificate_pdf as base


CARD_W = 105 * mm
CARD_H = 66 * mm
_ASSET_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")


def build_card_pdf(
    cert: dict,
    photo_bytes: Optional[bytes],
    verify_url: str,
    sample: bool = False,
    signature_bytes: Optional[bytes] = None,
) -> bytes:
    """Two-page AGR warranty card using the approved supplied artwork."""
    number = str(cert.get("certificate_number") or "")
    qr_reader = base._qr_image(verify_url, border=1)
    bg_path = os.path.join(_ASSET_DIR, "azuris_card_front.png")

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(CARD_W, CARD_H))

    # FRONT
    c.drawImage(
        ImageReader(bg_path),
        0,
        0,
        width=CARD_W,
        height=CARD_H,
        preserveAspectRatio=False,
        mask="auto",
    )

    qx, qy, qs = 4.15 * mm, 3.15 * mm, 18.35 * mm
    c.setFillColorRGB(1, 1, 1)
    c.rect(qx, qy, qs, qs, fill=1, stroke=0)
    c.drawImage(
        qr_reader,
        qx + 0.45 * mm,
        qy + 0.45 * mm,
        width=qs - 0.9 * mm,
        height=qs - 0.9 * mm,
        mask="auto",
    )

    c.setFillColorRGB(0.98, 0.98, 0.98)
    c.setFont(base.BODYB, 8.4)
    c.drawString(61.0 * mm, 6.0 * mm, number)

    if sample:
        base._sample_stamp(c, CARD_W * 0.73, CARD_H * 0.47, 8, 0.22, 14)

    c.showPage()

    # BACK — matching dark navy / blue design, intentionally blank of content.
    c.setFillColorRGB(0.003, 0.018, 0.055)
    c.rect(0, 0, CARD_W, CARD_H, fill=1, stroke=0)

    # Deep layered bands.
    c.setFillColorRGB(0.010, 0.052, 0.125)
    c.rect(0, 0, CARD_W, 14.0 * mm, fill=1, stroke=0)
    c.setFillColorRGB(0.006, 0.030, 0.080)
    c.rect(0, 14.0 * mm, CARD_W, 18.0 * mm, fill=1, stroke=0)

    # Luminous divider.
    c.setStrokeColorRGB(0.08, 0.46, 1.0)
    c.setLineWidth(0.8)
    c.line(0, 14.0 * mm, CARD_W, 14.0 * mm)

    # Right-side blue light arcs and diagonal highlights.
    c.saveState()
    c.setStrokeColorRGB(0.05, 0.20, 0.55)
    c.setLineWidth(0.7)
    c.arc(58 * mm, 31 * mm, 118 * mm, 90 * mm, 18, 74)
    c.arc(62 * mm, 29 * mm, 122 * mm, 92 * mm, 20, 72)
    c.setStrokeColorRGB(0.06, 0.36, 0.95)
    c.setLineWidth(0.9)
    c.line(82 * mm, 0, CARD_W, 20 * mm)
    c.line(88 * mm, 0, CARD_W, 15 * mm)
    c.restoreState()

    # Minimal left geometric accent to echo the front.
    c.saveState()
    c.setStrokeColorRGB(0.035, 0.16, 0.38)
    c.setLineWidth(0.8)
    c.line(0, 49 * mm, 8 * mm, 49 * mm)
    c.line(8 * mm, 49 * mm, 15 * mm, 42 * mm)
    c.line(15 * mm, 42 * mm, 15 * mm, 29 * mm)
    c.restoreState()

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
        for page in doc:
            for rect in page.search_for("CERTIFICATE NUMBER"):
                page.add_redact_annot(rect, fill=(0.98, 0.976, 0.965))
            page.apply_redactions()
        return doc.tobytes(garbage=4, deflate=True)
    finally:
        doc.close()


def decode_photo(data_b64):
    return base.decode_photo(data_b64)
