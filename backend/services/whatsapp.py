"""WhatsApp business-number normalization — FASE 2.

Canonical international numeric format, no `+`, spaces, dashes, or parentheses.
Indonesian leading `0` -> `62`. Letters are rejected.
"""

import re


class InvalidWhatsAppNumber(ValueError):
    pass


def normalize_whatsapp(raw: str) -> str:
    if raw is None:
        raise InvalidWhatsAppNumber("empty")
    if re.search(r"[A-Za-z]", raw):
        raise InvalidWhatsAppNumber("letters_not_allowed")
    digits = re.sub(r"[^0-9]", "", raw.replace("+", ""))
    if not digits:
        raise InvalidWhatsAppNumber("empty")
    if digits.startswith("0"):
        digits = "62" + digits[1:]
    if len(digits) < 8 or len(digits) > 15:
        raise InvalidWhatsAppNumber("malformed")
    return digits
