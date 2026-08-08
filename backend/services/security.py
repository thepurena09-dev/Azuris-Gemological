"""Server-side secrets for certificate verification — FASE 3.

Security code: exact-match manual code, unpredictable, NOT derived from the
certificate number. QR token: high-entropy opaque value (not any DB id).
"""

import secrets

# Unambiguous alphabet (no 0/O/1/I) for a human-typable security code.
_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def gen_security_code(length: int = 8) -> str:
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))


def gen_qr_token() -> str:
    # ~43 chars, URL-safe, cryptographically unpredictable, not a DB id.
    return secrets.token_urlsafe(32)
