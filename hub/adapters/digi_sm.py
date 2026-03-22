"""DIGI SM adapter — Tier 1 (Ethernet TCP/IP).

Supports ALL DIGI SM-series: SM-100, SM-120, SM-300, SM-500, SM-5100,
SM-5300, SM-6000. All use the identical DIGI SM protocol over Ethernet.

Interface: Ethernet TCP/IP only (RS-232 not used for data exchange)

Wire protocol (from rkeeper s_digi.dll):
  Weight request:  Hub → Scale:  STX W ETX
  Weight response: Scale → Hub:  STX w [3 digits] ? [3 digits] ... CRC ETX
  CRC = XOR of bytes from position 2 to n-2

PLU write operations use a binary/text hybrid format over TCP.
PLU fields: number, type, name, price, shelf life, sell-by date,
  individual code, barcode prefix, tare weight, special message,
  ingredient text, barcode format, label format/font.

Sources:
  - Scale-Soft.com — DIGI SM Driver
  - rkeeper RK7 — s_digi.dll documentation
"""
from __future__ import annotations

import struct
from typing import Optional

from hub.core.types import SaleData

STX = 0x02
ETX = 0x03

CMD_WEIGHT = ord("W")
CMD_PLU_WRITE = ord("P")
CMD_PLU_DELETE = ord("D")
CMD_KEYBOARD_WRITE = ord("K")
CMD_DATETIME = ord("T")
CMD_INGREDIENT_WRITE = ord("I")
CMD_MESSAGE_WRITE = ord("M")

DEFAULT_PORT = 3001


def _crc(data: bytes) -> int:
    """XOR checksum (bytes 2 through n-2 of full frame)."""
    result = 0
    for b in data:
        result ^= b
    return result


class DigiSmAdapter:
    """Tier 1 adapter for DIGI SM-series scales (SM-100 through SM-6000).

    Communicates exclusively over Ethernet TCP/IP.
    """

    def __init__(self, host: str = "192.168.1.100", port: int = DEFAULT_PORT):
        self._host = host
        self._port = port

    @property
    def name(self) -> str:
        return "DIGI SM"

    @property
    def tier(self) -> int:
        return 1

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    def parse_sale_frame(self, raw: bytes) -> SaleData:
        """Parse a DIGI SM weight response frame.

        Frame: STX 'w' [status 3 digits] '?' [weight 3 digits] ... CRC ETX
        Weight is encoded in grams as zero-padded digits.
        """
        if len(raw) < 6:
            raise ValueError(f"Frame too short: {len(raw)} bytes")

        if raw[0] != STX or raw[-1] != ETX:
            raise ValueError("Invalid frame delimiters")

        payload = raw[1:-1]
        expected_crc = payload[-1]
        inner = payload[:-1]

        if _crc(inner) != expected_crc:
            raise ValueError(
                f"CRC mismatch: expected {expected_crc:#04x}, "
                f"got {_crc(inner):#04x}"
            )

        text = inner.decode("ascii", errors="replace")

        if not text.startswith("w"):
            raise ValueError(f"Expected 'w' response, got '{text[0]}'")

        parts = text[1:].split("?")
        if len(parts) < 2:
            raise ValueError("Missing '?' separator in weight response")

        status_str = parts[0].strip()
        weight_str = parts[1].strip()

        try:
            weight_g = int(weight_str)
        except ValueError:
            raise ValueError(f"Cannot parse weight: '{weight_str}'")

        plu_id = None
        price_cents = 0
        total_cents = 0

        if len(parts) > 2:
            extra = parts[2].strip()
            if extra:
                try:
                    price_cents = int(extra)
                except ValueError:
                    pass
        if len(parts) > 3:
            extra = parts[3].strip()
            if extra:
                try:
                    total_cents = int(extra)
                except ValueError:
                    pass
        if len(parts) > 4:
            extra = parts[4].strip()
            if extra:
                try:
                    plu_id = int(extra)
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
        """Build a PLU recall command (not typical for SM protocol).

        DIGI SM scales use keyboard presets rather than remote PLU select.
        """
        return None

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
    ) -> Optional[bytes]:
        """Build a PLU write command for DIGI SM protocol.

        Format: STX 'P' <plu_number>,<type>,<name>,<price>,<shelf_life>,
                <barcode_prefix>,<tare>,<msg_no>,<ingredient_no>,
                <label_format> CRC ETX
        """
        fields = [
            str(plu),
            "0",
            name[:40],
            str(price_cents_per_kg),
            "",
            "",
            "0",
            "0",
            "0",
            "1",
        ]
        body = ",".join(fields)
        inner = bytes([CMD_PLU_WRITE]) + body.encode("ascii", errors="replace")
        crc = _crc(inner)
        return bytes([STX]) + inner + bytes([crc, ETX])

    def build_plu_delete(self, plu: int) -> bytes:
        """Build a PLU delete command."""
        body = str(plu)
        inner = bytes([CMD_PLU_DELETE]) + body.encode("ascii")
        crc = _crc(inner)
        return bytes([STX]) + inner + bytes([crc, ETX])

    def build_weight_request(self) -> bytes:
        """Build a weight query command: STX W ETX."""
        inner = bytes([CMD_WEIGHT])
        crc = _crc(inner)
        return bytes([STX]) + inner + bytes([crc, ETX])

    def build_datetime_sync(self, year: int, month: int, day: int,
                            hour: int, minute: int, second: int) -> bytes:
        """Build a date/time synchronization command."""
        body = f"{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}"
        inner = bytes([CMD_DATETIME]) + body.encode("ascii")
        crc = _crc(inner)
        return bytes([STX]) + inner + bytes([crc, ETX])

    def build_keyboard_map(self, key_number: int, plu: int) -> bytes:
        """Build a speed-key assignment command."""
        body = f"{key_number},{plu}"
        inner = bytes([CMD_KEYBOARD_WRITE]) + body.encode("ascii")
        crc = _crc(inner)
        return bytes([STX]) + inner + bytes([crc, ETX])

    def build_ingredient_upload(self, ingredient_id: int, text: str) -> bytes:
        """Build an ingredient text upload command."""
        body = f"{ingredient_id},{text[:200]}"
        inner = bytes([CMD_INGREDIENT_WRITE]) + body.encode("ascii", errors="replace")
        crc = _crc(inner)
        return bytes([STX]) + inner + bytes([crc, ETX])

    def build_message_upload(self, message_id: int, text: str) -> bytes:
        """Build a special message upload command."""
        body = f"{message_id},{text[:200]}"
        inner = bytes([CMD_MESSAGE_WRITE]) + body.encode("ascii", errors="replace")
        crc = _crc(inner)
        return bytes([STX]) + inner + bytes([crc, ETX])
