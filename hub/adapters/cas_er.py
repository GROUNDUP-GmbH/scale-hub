"""CAS ER-Plus adapter — Tier 2 (weight/price read-only).

The CAS ER-Plus has a single optional RS-232 port configured as a
virtual printer output. It sends completed sale data in ASCII format
delimited by STX/ETX. It does NOT accept PLU upload commands.

Serial parameters (CAS PD-II / ER documentation):
  9600 baud, 7 data bits, even parity, 1 stop bit

Wire protocol (sale printout, ASCII between STX/ETX):
  Fields are semicolon-separated key=value pairs.
  Example: PLU=00042;W=001250;UP=002490;TP=003113

  W  = weight in grams (integer, zero-padded 6 digits)
  UP = unit price in cents/kg (integer, zero-padded 6 digits)
  TP = total price in cents (integer, zero-padded 6 digits)
"""
from __future__ import annotations

from typing import Optional

from hub.core.types import SaleData

STX = 0x02
ETX = 0x03


class CasErAdapter:
    """Tier 2 adapter for CAS ER-Plus and compatible models."""

    @property
    def name(self) -> str:
        return "CAS ER-Plus"

    @property
    def tier(self) -> int:
        return 2

    def parse_sale_frame(self, raw: bytes) -> SaleData:
        """Parse a CAS ER-Plus sale printout frame.

        Accepts both the integer format (W=001250) and the
        decimal format (W=1.250) for backward compatibility.
        All outputs are integer grams/cents.
        """
        text = raw.decode("ascii", errors="replace")
        text = text.replace(chr(STX), "").replace(chr(ETX), "").strip()

        fields: dict[str, str] = {}
        for segment in text.split(";"):
            if "=" in segment:
                key, val = segment.split("=", 1)
                fields[key.strip().upper()] = val.strip()

        weight_g = self._parse_weight(fields.get("W", ""))
        price_cents = self._parse_cents(fields.get("UP", ""))
        total_cents = self._parse_cents(fields.get("TP", ""))
        plu = int(fields["PLU"]) if fields.get("PLU") else None

        return SaleData(
            weight_g=weight_g,
            price_cents_per_kg=price_cents,
            total_cents=total_cents,
            plu_id=plu,
            raw_bytes=raw,
        )

    def build_select_command(self, plu: int) -> Optional[bytes]:
        return None

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
    ) -> Optional[bytes]:
        return None

    @staticmethod
    def _parse_weight(val: str) -> int:
        """Parse weight field to integer grams."""
        if not val:
            raise ValueError("Missing weight field")
        if "." in val:
            return int(round(float(val) * 1000))
        return int(val)

    @staticmethod
    def _parse_cents(val: str) -> int:
        """Parse price field to integer cents."""
        if not val:
            raise ValueError("Missing price field")
        if "." in val:
            return int(round(float(val) * 100))
        return int(val)
