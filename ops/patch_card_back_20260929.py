#!/usr/bin/env python3
"""Safely center the active Azuris card back without touching the front."""
from datetime import datetime
from pathlib import Path
import py_compile


path = Path("backend/services/certificate_pdf.py")
source = path.read_text()
function_start = source.find("def build_card_pdf(")
function_end = source.find("\ndef render_card_png(", function_start)
if function_start < 0 or function_end < 0:
    raise SystemExit("STOP: renderer Card tidak ditemukan; file tidak diubah")

card = source[function_start:function_end]
back_heading = card.find("# BACK")
if back_heading < 0:
    raise SystemExit("STOP: tampak belakang Card tidak ditemukan; file tidak diubah")

start = card.find("    shell()\n", back_heading)
end = card.find("\n    if sample:", start)
if start < 0 or end < 0:
    raise SystemExit("STOP: batas Card belakang tidak ditemukan; file tidak diubah")

old = card[start:end]
if "# Centered identity above the emblem" in old:
    print("ALREADY PATCHED: tidak ada perubahan")
    raise SystemExit(0)
if not all(x in old for x in ("_draw_logo(", "signature_reader", "cy - 17.4 * mm")):
    raise SystemExit("STOP: struktur Card belakang berbeda; file tidak diubah")

new = '''    shell()
    cx = CARD_W / 2

    # Centered identity above the emblem.
    _tracked(
        c, 0, CARD_H - 6.8 * mm,
        "azurisgemological.com",
        BODYB, 3.3, GOLD_SOFT,
        tracking=0.7, center=cx,
    )
    _tracked(
        c, 0, CARD_H - 10.3 * mm,
        "AZURIS GEMOLOGICAL RESEARCH",
        BODYB, 4.0, GOLD_SOFT,
        tracking=0.75, center=cx,
    )

    # The AGR emblem already bundled with the active website.
    _draw_logo(c, _LOGO, cx, CARD_H - 21.2 * mm, 14.0 * mm)
    draw_agr_3d(0, CARD_H - 33.0 * mm, 13.0, center=cx)

    # No horizontal ornament passes through the Legality signature.
    if signature_reader is not None:
        try:
            iw, ih = signature_reader.getSize()
            ratio = min((30 * mm) / iw, (7.2 * mm) / ih)
            dw, dh = iw * ratio, ih * ratio
            c.drawImage(
                signature_reader,
                cx - dw / 2,
                11.7 * mm,
                width=dw,
                height=dh,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

    c.setFillColorRGB(*GOLD_SOFT)
    c.setFont(BODYB, 4.2)
    c.drawCentredString(cx, 9.0 * mm, "H.Zulfikar.se.GG")
    _tracked(
        c, 0, 6.1 * mm,
        "AUTHORISED SIGNATORY",
        BODYB, 2.8, GOLD_SOFT,
        tracking=0.6, center=cx,
    )
'''

updated_card = card[:start] + new + card[end:]
updated = source[:function_start] + updated_card + source[function_end:]
backup = path.with_name(
    "certificate_pdf.py.backup-" + datetime.now().strftime("%Y%m%d-%H%M%S")
)
backup.write_text(source)
path.write_text(updated)
try:
    py_compile.compile(str(path), doraise=True)
except Exception:
    path.write_text(source)
    raise SystemExit("STOP: sintaks gagal; file asli dipulihkan")
print("PATCH OK. Backup:", backup)
