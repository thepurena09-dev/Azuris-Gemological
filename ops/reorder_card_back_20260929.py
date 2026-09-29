#!/usr/bin/env python3
"""Reorder only the active Azuris card-back identity block."""
from datetime import datetime
from pathlib import Path
import py_compile

p = Path("backend/services/certificate_pdf.py")
s = p.read_text()
a = s.find("def build_card_pdf(")
b = s.find("\ndef render_card_png(", a)
if a < 0 or b < 0:
    raise SystemExit("STOP: Card renderer not found")
card = s[a:b]
start = card.find("# BACK — centered identity and unobstructed signature")
end = card.find("# Signature has a clear area", start)
if start < 0 or end < 0:
    raise SystemExit("STOP: active back identity block not found; no changes")
block = card[start:end]
if "CARD_H - 28.0 * mm" in block:
    print("ALREADY PATCHED")
    raise SystemExit(0)
pairs = [
    ("CARD_H - 6.8 * mm", "CARD_H - 32.0 * mm"),
    ("CARD_H - 10.3 * mm", "CARD_H - 28.0 * mm"),
    ("_draw_logo(c, _LOGO, cx, CARD_H - 21.2 * mm, 14.0 * mm)",
     "_draw_logo(c, _LOGO, cx, CARD_H - 11.5 * mm, 13.5 * mm)"),
    ("draw_agr_3d(0, CARD_H - 33.0 * mm, 13.0, center=cx)",
     "draw_agr_3d(0, CARD_H - 21.5 * mm, 13.0, center=cx)"),
]
for old, new in pairs:
    if block.count(old) != 1:
        raise SystemExit("STOP: expected layout coordinate missing; no changes: " + old)
    block = block.replace(old, new, 1)
# Company name first in the middle, website below it.
company = block.index("    _tracked(\n        c, 0, CARD_H - 28.0 * mm,")
website = block.index("    _tracked(\n        c, 0, CARD_H - 32.0 * mm,")
if not website < company:
    raise SystemExit("STOP: identity order changed; no changes")
first = block.index("    _tracked(", block.index("# Centered identity"))
logo = block.index("    _draw_logo(", company)
site_call = block[website:company]
company_call = block[company:logo]
block = block[:first] + company_call + site_call + block[logo:]
block = block.replace("BODYB, 4.0, GOLD_SOFT", "BODYB, 4.6, GOLD_SOFT", 1)
block = block.replace("BODYB, 3.3, GOLD_SOFT", "BODYB, 3.8, GOLD_SOFT", 1)
new_card = card[:start] + block + card[end:]
new_source = s[:a] + new_card + s[b:]
backup = p.with_name("certificate_pdf.py.backup-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
backup.write_text(s)
p.write_text(new_source)
try:
    py_compile.compile(str(p), doraise=True)
except Exception:
    p.write_text(s)
    raise SystemExit("STOP: syntax failed; original restored")
print("PATCH OK. Backup:", backup)
