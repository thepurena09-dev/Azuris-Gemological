"""AGR card/certificate rendering overrides.

The front card uses the exact user-supplied artwork as its background. Only the
QR code and Warranty ID are generated dynamically. The back stays plain.
"""

import base64
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
_CARD_FRONT_B64 = os.path.join(_ASSET_DIR, "card_front_reference_small.jpg.b64")


def _card_front_reader():
    """Load the approved front artwork stored as base64 text in the repo."""
    with open(_CARD_FRONT_B64, "r", encoding="ascii") as f:
        raw = base64.b64decode(f.read().strip())
    return ImageReader(BytesIO(raw))


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

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(CARD_W, CARD_H))

    # FRONT: exact supplied card artwork, scaled edge-to-edge.
    c.drawImage(
        _card_front_reader(),
        0,
        0,
        width=CARD_W,
        height=CARD_H,
        preserveAspectRatio=False,
        mask="auto",
    )

    # Replace the QR artwork with the certificate-specific verification QR.
    # Coordinates are matched to the white QR square in the supplied reference.
    qx, qy, qs = 4.65 * mm, 4.55 * mm, 17.65 * mm
    c.setFillColorRGB(1, 1, 1)
    c.rect(qx, qy, qs, qs, fill=1, stroke=0)
    c.drawImage(qr_reader, qx, qy, width=qs, height=qs, mask="auto")

    # The supplied artwork intentionally leaves this field blank.
    # Insert only the live certificate/warranty ID.
    c.setFillColorRGB(0.98, 0.98, 0.98)
    c.setFont(base.BODYB, 8.1)
    c.drawString(61.5 * mm, 6.6 * mm, number)

    if sample:
        base._sample_stamp(c, CARD_W * 0.73, CARD_H * 0.47, 8, 0.22, 14)

    c.showPage()

    # BACK: plain dark navy/black as requested.
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
        for page in doc:
            for rect in page.search_for("CERTIFICATE NUMBER"):
                page.add_redact_annot(rect, fill=(0.98, 0.976, 0.965))
            page.apply_redactions()
        return doc.tobytes(garbage=4, deflate=True)
    finally:
        doc.close()


def decode_photo(data_b64):
    return base.decode_photo(data_b64)
