"""AGR card/certificate production overrides."""

import math
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


def build_card_pdf(cert: dict, photo_bytes: Optional[bytes], verify_url: str,
                   sample: bool = False, signature_bytes: Optional[bytes] = None) -> bytes:
    number = str(cert.get("certificate_number") or "")
    front_path = os.path.join(_ASSET_DIR, "azuris_card_front_plain_print.jpg")
    qr_reader = base._qr_image(verify_url, border=1)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(CARD_W, CARD_H))
    c.drawImage(ImageReader(front_path), 0, 0, width=CARD_W, height=CARD_H,
                preserveAspectRatio=False, mask="auto")

    # Completely cover the QR embedded in the artwork, then draw ONE live QR.
    # Slightly oversized mask prevents the old code from showing around the edges.
    mask_x, mask_y, mask_s = 3.45 * mm, 1.95 * mm, 20.9 * mm
    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(0.04, 0.27, 0.70)
    c.setLineWidth(0.55)
    c.rect(mask_x, mask_y, mask_s, mask_s, fill=1, stroke=1)

    qx, qy, qs = 4.25 * mm, 2.75 * mm, 19.3 * mm
    c.drawImage(qr_reader, qx, qy, width=qs, height=qs, mask="auto")

    # Dynamic certificate / warranty ID only.
    c.setFillColorRGB(0.98, 0.98, 0.98)
    c.setFont(base.BODYB, 8.4)
    c.drawString(61.0 * mm, 6.0 * mm, number)

    if sample:
        base._sample_stamp(c, CARD_W * 0.73, CARD_H * 0.47, 8, 0.22, 14)

    c.showPage()

    # BACK unchanged.
    back_path = os.path.join(_ASSET_DIR, "azuris_card_back_exact.png")
    c.drawImage(ImageReader(back_path), 0, 0, width=CARD_W, height=CARD_H,
                preserveAspectRatio=False, mask="auto")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


def _draw_cover(page):
    """Replace certificate page 1 with the approved navy/black AGR cover."""
    w, h = page.rect.width, page.rect.height

    # Deep navy / black background with restrained blue edge glows.
    bands = 180
    for i in range(bands):
        t0 = i / bands
        t1 = (i + 1) / bands
        tc = (t0 + t1) / 2
        glow = 0.78 * math.exp(-((tc - 0.10) / 0.13) ** 2) + 0.72 * math.exp(-((tc - 0.91) / 0.14) ** 2)
        col = (0.004 + 0.006 * glow, 0.018 + 0.055 * glow, 0.050 + 0.24 * glow)
        page.draw_rect(pymupdf.Rect(t0 * w, 0, t1 * w + 1, h), color=None, fill=col)

    gold = (0.80, 0.62, 0.20)
    gold2 = (0.95, 0.78, 0.33)
    blue = (0.04, 0.30, 0.83)


    # Outer double gold frame.
    for frac, width, color in ((0.058, 1.7, gold2), (0.071, 0.65, gold)):
        r = pymupdf.Rect(w * frac, h * frac, w * (1-frac), h * (1-frac))
        page.draw_rect(r, color=color, width=width)

    # Inner wavy / guilloche frame.
    left, right = w * 0.105, w * 0.895
    top, bottom = h * 0.087, h * 0.915
    amp = w * 0.0045
    cycles_h = 22
    cycles_v = 28
    pts = []
    n = 360
    for i in range(n+1):
        x = left + (right-left) * i/n
        y = top + amp * math.sin(2*math.pi*cycles_h*i/n)
        pts.append(pymupdf.Point(x,y))
    page.draw_polyline(pts, color=gold2, width=0.65)
    pts = []
    for i in range(n+1):
        x = left + (right-left) * i/n
        y = bottom + amp * math.sin(2*math.pi*cycles_h*i/n)
        pts.append(pymupdf.Point(x,y))
    page.draw_polyline(pts, color=gold2, width=0.65)
    pts=[]
    for i in range(n+1):
        y = top + (bottom-top) * i/n
        x = left + amp * math.sin(2*math.pi*cycles_v*i/n)
        pts.append(pymupdf.Point(x,y))
    page.draw_polyline(pts, color=gold2, width=0.65)
    pts=[]
    for i in range(n+1):
        y = top + (bottom-top) * i/n
        x = right + amp * math.sin(2*math.pi*cycles_v*i/n)
        pts.append(pymupdf.Point(x,y))
    page.draw_polyline(pts, color=gold2, width=0.65)

    # AGR emblem.
    logo_path = getattr(base, "LOGO_PATH", None)
    if logo_path and os.path.exists(logo_path):
        lr = pymupdf.Rect(w*0.405, h*0.165, w*0.595, h*0.315)
        page.insert_image(lr, filename=logo_path, keep_proportion=True, overlay=True)

    # Brand title box.
    box = pymupdf.Rect(w*0.27, h*0.345, w*0.73, h*0.445)
    page.draw_rect(box, color=gold2, width=1.1)
    page.draw_rect(pymupdf.Rect(box.x0+w*0.010, box.y0+h*0.007, box.x1-w*0.010, box.y1-h*0.007), color=gold, width=0.5)
    title_font = pymupdf.Font(fontname="tibo")
    title_fs = 24
    title_text = "AZURIS"
    title_w = title_font.text_length(title_text, fontsize=title_fs)
    page.insert_text(pymupdf.Point((w-title_w)/2, h*0.392), title_text,
                     fontname="tibo", fontsize=title_fs, color=gold2)
    page.insert_textbox(pymupdf.Rect(w*0.29,h*0.402,w*0.71,h*0.438), "AZURIS GEMOLOGICAL RESEARCH",
                        fontname="hebo", fontsize=w*0.014, color=gold2, align=1)

    # Divider and cover text.
    cy = h*0.475
    page.draw_line(pymupdf.Point(w*0.36,cy), pymupdf.Point(w*0.64,cy), color=gold, width=0.8)
    d = w*0.008
    page.draw_polyline([pymupdf.Point(w/2,cy-d),pymupdf.Point(w/2+d,cy),pymupdf.Point(w/2,cy+d),pymupdf.Point(w/2-d,cy),pymupdf.Point(w/2,cy-d)], color=gold2, width=0.8)

    page.insert_textbox(pymupdf.Rect(w*0.15,h*0.515,w*0.85,h*0.575), "GEMSTONE IDENTIFICATION",
                        fontname="tibo", fontsize=w*0.035, color=gold2, align=1)
    page.insert_textbox(pymupdf.Rect(w*0.16,h*0.645,w*0.84,h*0.69), "O F F I C I A L   G E M O L O G I C A L   D O C U M E N T",
                        fontname="hebo", fontsize=w*0.0115, color=gold2, align=1)

    cy2 = h*0.81
    page.draw_line(pymupdf.Point(w*0.39,cy2), pymupdf.Point(w*0.61,cy2), color=gold, width=0.7)
    page.draw_polyline([pymupdf.Point(w/2,cy2-d),pymupdf.Point(w/2+d,cy2),pymupdf.Point(w/2,cy2+d),pymupdf.Point(w/2-d,cy2),pymupdf.Point(w/2,cy2-d)], color=gold2, width=0.7)
    page.insert_textbox(pymupdf.Rect(w*0.17,h*0.827,w*0.83,h*0.875), "T R U S T E D   G E M O L O G I C A L   I N S T I T U T I O N",
                        fontname="hebo", fontsize=w*0.0105, color=gold2, align=1)


def build_certificate_pdf(cert: dict, photo_bytes: Optional[bytes],
                          signature_bytes: Optional[bytes] = None, demo: bool = False) -> bytes:
    pdf = base.build_certificate_pdf(cert, photo_bytes, signature_bytes, demo)
    src = pymupdf.open(stream=pdf, filetype="pdf")
    out = pymupdf.open()
    try:
        if len(src) == 0:
            return pdf
        r = src[0].rect
        p = out.new_page(width=r.width, height=r.height)
        _draw_cover(p)
        if len(src) > 1:
            out.insert_pdf(src, from_page=1, to_page=len(src)-1)

        # Preserve the existing behavior: remove only the circled label, not the number.
        for page in out:
            for rect in page.search_for("CERTIFICATE NUMBER"):
                page.add_redact_annot(rect, fill=(0.98, 0.976, 0.965))
            page.apply_redactions()
        return out.tobytes(garbage=4, deflate=True)
    finally:
        src.close()
        out.close()


def decode_photo(data_b64):
    return base.decode_photo(data_b64)

