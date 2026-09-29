#!/usr/bin/env python3
"""Use the complete official AGR/AZURIS lockup on the active card back only."""

from datetime import datetime
from pathlib import Path
import py_compile


source_path = Path("backend/services/certificate_pdf.py")
card_logo_path = Path("backend/assets/azuris-logo.png")

if not source_path.is_file():
    raise SystemExit("STOP: certificate renderer not found; no changes")
if not card_logo_path.is_file():
    raise SystemExit("STOP: complete AGR/AZURIS logo asset not found; no changes")

source = source_path.read_text()

card_logo_path_line = (
    'CARD_BACK_LOGO_PATH = os.path.join(_ASSETS, "azuris-logo.png")'
)
card_logo_reader_line = "_CARD_BACK_LOGO = _logo(CARD_BACK_LOGO_PATH)"

if card_logo_path_line not in source:
    logo_path_lines = [
        line for line in source.splitlines()
        if line.startswith("LOGO_PATH = os.path.join(_ASSETS,")
    ]
    if len(logo_path_lines) != 1:
        raise SystemExit("STOP: logo path anchor is not unique; no changes")
    logo_path_line = logo_path_lines[0]
    source = source.replace(
        logo_path_line,
        logo_path_line + "\n" + card_logo_path_line,
        1,
    )

if card_logo_reader_line not in source:
    logo_reader_line = "_LOGO = _logo(LOGO_PATH)"
    if source.count(logo_reader_line) != 1:
        raise SystemExit("STOP: logo reader anchor is not unique; no changes")
    source = source.replace(
        logo_reader_line,
        logo_reader_line + "\n" + card_logo_reader_line,
        1,
    )

card_start = source.find("def build_card_pdf(")
card_end = source.find("\ndef render_card_png(", card_start)
if card_start < 0 or card_end < 0:
    raise SystemExit("STOP: Card renderer not found; no changes")

card = source[card_start:card_end]
back_marker = "# BACK"
signature_marker = "# Signature has a clear area"
back_start = card.find(back_marker)
back_end = card.find(signature_marker, back_start)
if back_start < 0 or back_end < 0:
    raise SystemExit("STOP: active Card-back block not found; no changes")

back = card[back_start:back_end]
if "_draw_logo(c, _CARD_BACK_LOGO," in back:
    print("ALREADY PATCHED")
    raise SystemExit(0)

old_logo_call = "_draw_logo(c, _LOGO, cx, CARD_H - 11.5 * mm, 13.5 * mm)"
new_logo_call = (
    "_draw_logo(c, _CARD_BACK_LOGO, cx, CARD_H - 11.5 * mm, 13.5 * mm)"
)
if back.count(old_logo_call) != 1:
    raise SystemExit("STOP: active Card-back logo call differs; no changes")

back = back.replace(old_logo_call, new_logo_call, 1)
new_card = card[:back_start] + back + card[back_end:]
new_source = source[:card_start] + new_card + source[card_end:]

backup = source_path.with_name(
    "certificate_pdf.py.backup-" + datetime.now().strftime("%Y%m%d-%H%M%S")
)
backup.write_text(source_path.read_text())
source_path.write_text(new_source)

try:
    py_compile.compile(str(source_path), doraise=True)
except Exception as exc:
    source_path.write_text(backup.read_text())
    raise SystemExit(f"STOP: syntax failed; original restored: {exc}")

print("PATCH OK. Backup:", backup)
print("Card back now uses:", card_logo_path)
