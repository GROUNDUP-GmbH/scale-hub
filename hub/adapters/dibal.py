"""DIBAL EPOS TISA adapter — Tier 2+ (bidirectional price injection).

Supports DIBAL G-310, G-325, and other DIBAL scales with TISA protocol.
The TISA protocol allows the Hub to SEND a price to the scale and RECEIVE
the weight back. The scale then calculates the total. This is Tier 2+
because we can inject the price but not full PLU data (name, barcode, etc.).

Wire protocol (from rkeeper s_dibal.dll):
  Price injection + weight response:
    Hub → Scale:  '98' + [5-digit price] + [XOR] + CR + LF
    Scale → Hub:  [18 bytes: '99' + '0' + 5-digit weight + ... + XOR + CR + LF]

  Price format: 5 digits, right-justified, zero-padded (in cents)
    Example: price €1.23 → '00123'

  Weight format: 5 digits, right-justified, zero-padded (in grams)
    Example: weight 1.232 kg → '01232'

Sources:
  - rkeeper RK7 — s_dibal.dll documentation
"""
from __future__ import annotations

from typing import Optional

from hub.core.types import SaleData

CR = 0x0D
LF = 0x0A


def _xor_checksum(data: bytes) -> int:
    """XOR checksum of all bytes."""
    result = 0
    for b in data:
        result ^= b
    return result


class DibalTisaAdapter:
    """Tier 2+ adapter for DIBAL scales with EPOS TISA protocol.

    Can inject prices from Odoo and receive weight data back.
    Cannot upload PLU names, barcodes, or other product data.
    """

    @property
    def name(self) -> str:
        return "DIBAL TISA"

    @property
    def tier(self) -> int:
        return 3  # Tier 2+ encoded as 3

    def parse_sale_frame(self, raw: bytes) -> SaleData:
        """Parse a DIBAL TISA weight response.

        Response format (18 bytes):
          '99' + '0' + [5-digit weight in grams] + [5-digit price in cents]
          + [XOR] + CR + LF

        The scale sends this after receiving a price injection command.
        """
        text = raw.decode("ascii", errors="replace").strip()

        if not text.startswith("99"):
            raise ValueError(f"Expected '99' prefix, got '{text[:2]}'")

        if len(text) < 13:
            raise ValueError(f"Response too short: {len(text)} chars")

        status = text[2]
        weight_str = text[3:8]
        price_str = text[8:13]

        try:
            weight_g = int(weight_str)
        except ValueError:
            raise ValueError(f"Cannot parse weight: '{weight_str}'")

        try:
            price_cents = int(price_str)
        except ValueError:
            raise ValueError(f"Cannot parse price: '{price_str}'")

        total_cents = 0
        if weight_g > 0 and price_cents > 0:
            total_cents = (weight_g * price_cents + 500) // 1000

        return SaleData(
            weight_g=weight_g,
            price_cents_per_kg=price_cents,
            total_cents=total_cents,
            raw_bytes=raw,
        )

    def build_select_command(self, plu: int) -> Optional[bytes]:
        return None

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
    ) -> Optional[bytes]:
        return None

    def build_price_inject(self, price_cents_per_kg: int) -> bytes:
        """Build a price injection command (TISA protocol).

        Format: '98' + [5-digit price in cents/kg] + [XOR] + CR + LF
        Example: price €12.50/kg → '9801250' + XOR + CR + LF
        """
        price_str = f"{price_cents_per_kg:05d}"
        body = f"98{price_str}"
        body_bytes = body.encode("ascii")
        xor = _xor_checksum(body_bytes)
        return body_bytes + bytes([xor, CR, LF])

    def build_weight_request(self, price_cents_per_kg: int = 0) -> bytes:
        """Request weight by injecting current price (TISA requires price to respond).

        If price is 0, sends '9800000' which some scales interpret as
        a simple weight request.
        """
        return self.build_price_inject(price_cents_per_kg)
