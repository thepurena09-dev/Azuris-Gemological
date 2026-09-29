#!/usr/bin/env python3
"""Render the supplied complete AZURIS lockup as the card-back identity."""

from datetime import datetime
from pathlib import Path
import py_compile


source_path = Path("backend/services/certificate_pdf.py")
logo_path = Path("backend/assets/azuris-logo.png")

if not source_path.is_file():
    raise SystemExit("STOP: certificate renderer not found; no changes")
if not logo_path.is_file():
    raise SystemExit("STOP: supplied AZURIS logo asset not found; no changes")

source = source_path.read_text()
card_start = source.find("def build_card_pdf(")
card_end = source.find("\ndef render_card_png(", card_start)
if card_start < 0 or card_end < 0:
    raise SystemExit("STOP: Card renderer not found; no changes")

card = source[card_start:card_end]
start_marker = "    # Company identity, centered above the emblem."
end_marker = "    # Signature has a clear area: no decorative horizontal lines."
start = card.find(start_marker)
end = card.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit("STOP: Card-back identity block not found; no changes")

replacement = '''    # Complete official AZURIS lockup supplied by the owner.
    _draw_logo(c, _CARD_BACK_LOGO, cx, CARD_H - 16.0 * mm, 28.0 * mm)
    _tracked(
        c, 0, CARD_H - 32.0 * mm,
        "azurisgemological.com",
        BODYB, 3.8, GOLD_SOFT,
        tracking=0.7, center=cx,
    )

'''

current = card[start:end]
if current == replacement:
    print("ALREADY PATCHED")
    raise SystemExit(0)

required = (
    "_draw_logo(c, _CARD_BACK_LOGO, cx, CARD_H - 11.5 * mm, 13.5 * mm)",
    "_draw_agr_3d(c, CARD_H - 21.5 * mm, 13.0, center=cx)",
    '"AZURIS GEMOLOGICAL RESEARCH"',
    '"azurisgemological.com"',
)
missing = [item for item in required if item not in current]
if missing:
    raise SystemExit("STOP: unexpected Card-back identity block; no changes")

new_card = card[:start] + replacement + card[end:]
new_source = source[:card_start] + new_card + source[card_end:]

backup = source_path.with_name(
    "certificate_pdf.py.backup-" + datetime.now().strftime("%Y%m%d-%H%M%S")
)
backup.write_text(source)
source_path.write_text(new_source)

try:
    py_compile.compile(str(source_path), doraise=True)
except Exception as exc:
    source_path.write_text(source)
    raise SystemExit(f"STOP: syntax failed; original restored: {exc}")

print("PATCH OK. Backup:", backup)
print("Card back now renders the complete supplied logo at 28 mm.")
