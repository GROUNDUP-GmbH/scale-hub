"""GS1 Digital Link builder (Decision 05).

Non-legally-relevant — the QR code supplements but never replaces
human-readable weight and price on the label.
"""
from __future__ import annotations

from datetime import date


def encode_weight_ai(weight_g: int) -> tuple[str, str]:
    """Encode weight as AI 3103 (grams, zero-padded to 6 digits)."""
    return "3103", f"{weight_g:06d}"


def encode_date_ai(d: date | str | None) -> str | None:
    if d is None:
        return None
    if isinstance(d, str):
        if len(d) == 6 and d.isdigit():
            return d
        d = date.fromisoformat(d)
    return d.strftime("%y%m%d")


def build_digital_link(
    *,
    base_url: str,
    gtin: str,
    weight_g: int,
    lot: str | None = None,
    expiry: date | str | None = None,
    serial: str | None = None,
) -> str:
    """Build a full GS1 Digital Link URI with integer weight."""
    base = base_url.rstrip("/")
    ai_w, val_w = encode_weight_ai(weight_g)
    path = f"{base}/01/{gtin}/{ai_w}/{val_w}"
    if lot:
        path += f"/10/{lot}"
    exp = encode_date_ai(expiry)
    if exp:
        path += f"/15/{exp}"
    if serial:
        path += f"/21/{serial}"
    return path
