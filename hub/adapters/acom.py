"""Acom adapter — Tier 1 (RS-232 + Ethernet).

Supports Acom NETS (label printing) and Acom PC (price computing) scales.
Both support PLU programming via their respective protocols.

Interface: RS-232 and TCP/IP

Wire protocol uses STX/ETX framing with command-based structure.
Commands are ASCII text with fixed-width fields.

Sources:
  - Scale-Soft.com — Acom NETS
  - Scale-Soft.com — Acom PC
"""
from __future__ import annotations

from typing import Optional

from hub.core.types import SaleData

STX = 0x02
ETX = 0x03
ACK = 0x06
NAK = 0x15


def _lrc(data: bytes) -> int:
    """Longitudinal Redundancy Check (XOR of all bytes)."""
    result = 0
    for b in data:
        result ^= b
    return result


class AcomAdapter:
    """Tier 1 adapter for Acom NETS and Acom PC scales.

    Supports PLU upload/delete, keyboard mapping, and weight readback.
    """

    @property
    def name(self) -> str:
        return "Acom"

    @property
    def tier(self) -> int:
        return 1

    def parse_sale_frame(self, raw: bytes) -> SaleData:
        """Parse an Acom weight/sale response frame.

        Frame: STX [cmd] [data fields] LRC ETX
        Weight field: 6 digits in grams, zero-padded
        Price field: 6 digits in cents, zero-padded
        """
        if len(raw) < 5:
            raise ValueError(f"Frame too short: {len(raw)} bytes")

        if raw[0] != STX or raw[-1] != ETX:
            raise ValueError("Invalid frame delimiters")

        payload = raw[1:-2]
        expected_lrc = raw[-2]

        if _lrc(payload) != expected_lrc:
            raise ValueError(
                f"LRC mismatch: expected {expected_lrc:#04x}, "
                f"got {_lrc(payload):#04x}"
            )

        text = payload.decode("ascii", errors="replace")

        cmd = text[0] if text else ""
        data = text[1:] if len(text) > 1 else ""

        fields = data.split(",")

        weight_g = 0
        price_cents = 0
        total_cents = 0
        plu_id = None

        if len(fields) >= 1 and fields[0].strip():
            try:
                weight_g = int(fields[0].strip())
            except ValueError:
                raise ValueError(f"Cannot parse weight: '{fields[0]}'")

        if len(fields) >= 2 and fields[1].strip():
            try:
                price_cents = int(fields[1].strip())
            except ValueError:
                pass

        if len(fields) >= 3 and fields[2].strip():
            try:
                total_cents = int(fields[2].strip())
            except ValueError:
                pass

        if len(fields) >= 4 and fields[3].strip():
            try:
                plu_id = int(fields[3].strip())
            except ValueError:
                pass

        return SaleData(
            weight_g=weight_g,
            price_cents_per_kg=price_cents,
            total_cents=total_cents,
            plu_id=plu_id,
            raw_bytes=raw,
        )

    def build_select_command(self, plu: int) -> Optional[bytes]:
        """Build a PLU recall command."""
        body = f"R{plu:06d}"
        inner = body.encode("ascii")
        lrc = _lrc(inner)
        return bytes([STX]) + inner + bytes([lrc, ETX])

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
    ) -> Optional[bytes]:
        """Build a PLU write command.

        Format: STX 'W' <plu>,<name>,<price>,<shelf_life>,<tare>,
                <barcode>,<group> LRC ETX
        """
        fields = [
            str(plu),
            name[:28],
            str(price_cents_per_kg),
            "",
            "0",
            "",
            "1",
        ]
        body = "W" + ",".join(fields)
        inner = body.encode("ascii", errors="replace")
        lrc = _lrc(inner)
        return bytes([STX]) + inner + bytes([lrc, ETX])

    def build_plu_delete(self, plu: int) -> bytes:
        """Build a PLU delete command."""
        body = f"D{plu:06d}"
        inner = body.encode("ascii")
        lrc = _lrc(inner)
        return bytes([STX]) + inner + bytes([lrc, ETX])

    def build_keyboard_map(self, key_number: int, plu: int) -> bytes:
        """Build a speed-key assignment command."""
        body = f"K{key_number:03d},{plu:06d}"
        inner = body.encode("ascii")
        lrc = _lrc(inner)
        return bytes([STX]) + inner + bytes([lrc, ETX])

    def build_datetime_sync(self, year: int, month: int, day: int,
                            hour: int, minute: int, second: int) -> bytes:
        """Build a date/time synchronization command."""
        body = f"T{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}"
        inner = body.encode("ascii")
        lrc = _lrc(inner)
        return bytes([STX]) + inner + bytes([lrc, ETX])

    def build_weight_request(self) -> bytes:
        """Build a weight query command."""
        inner = b"Q"
        lrc = _lrc(inner)
        return bytes([STX]) + inner + bytes([lrc, ETX])
