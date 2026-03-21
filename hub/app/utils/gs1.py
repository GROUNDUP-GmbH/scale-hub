"""
GroundUp Scale Hub – GS1 Digital Link Builder

Builds GS1-conformant Digital Link URIs for product labels.
Uses Application Identifiers (AIs) per GS1 General Specifications:
  01  = GTIN
  3103 = Net weight in kg (3 implied decimals)
  10  = Batch/Lot number
  15  = Best before date (YYMMDD)
  21  = Serial number

The resulting URL can be encoded as a QR code on Zebra labels.
"""
from __future__ import annotations

from datetime import date


def encode_weight_ai(weight_kg: float) -> tuple[str, str]:
    """Encode weight as AI 3103 (grams, zero-padded to 6 digits)."""
    grams = int(round(weight_kg * 1000))
    return "3103", f"{grams:06d}"


def encode_date_ai(d: date | str | None) -> str | None:
    """Encode a date as YYMMDD for AI 15."""
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
    weight_kg: float,
    lot: str | None = None,
    expiry: date | str | None = None,
    serial: str | None = None,
) -> str:
    """
    Build a full GS1 Digital Link URI.

    Example output:
        https://groundup.bio/01/09012345678908/3103/001250/10/LOT42/15/260325
    """
    base = base_url.rstrip("/")
    ai_weight, val_weight = encode_weight_ai(weight_kg)

    path = f"{base}/01/{gtin}/{ai_weight}/{val_weight}"

    if lot:
        path += f"/10/{lot}"

    exp_str = encode_date_ai(expiry)
    if exp_str:
        path += f"/15/{exp_str}"

    if serial:
        path += f"/21/{serial}"

    return path
