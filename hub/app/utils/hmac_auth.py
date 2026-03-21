"""
GroundUp Scale Hub – HMAC Signature Verification

Verifies that incoming requests from Odoo (or any client) carry
a valid HMAC-SHA256 signature. This prevents unauthorized systems
from sending commands to the scale.
"""
from __future__ import annotations

import hashlib
import hmac


def compute_signature(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def verify_signature(secret: str, body: bytes, signature: str) -> bool:
    expected = compute_signature(secret, body)
    return hmac.compare_digest(expected, signature.strip())
