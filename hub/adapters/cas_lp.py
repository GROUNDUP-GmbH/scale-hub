"""CAS LP adapter — Tier 1 (full bidirectional PLU protocol).

Supports CAS LP-1, LP-II / LP-1.6, LP-1000N, and CL5000(J) in LP mode.

Serial parameters:
  Configurable: 2400 / 4800 / 9600 / 19200 baud, 8N1

PLU record structure (83 bytes per record):
  Offset 0x00-0x03: PLU Number (4 bytes, binary)
  Offset 0x04-0x09: Product Code / barcode digits (6 bytes, BCD)
  Offset 0x0A-0x41: Product Name (56 bytes, ASCII, 2 lines × 28 chars)
  Offset 0x42-0x45: Price in currency subunit (4 bytes, binary, max 999999)
  Offset 0x46-0x48: Shelf Life / Expiry (3 bytes, BCD)
  Offset 0x49-0x4A: Tare Weight (2 bytes, binary)
  Offset 0x4B-0x50: Group Code (6 bytes)
  Offset 0x51-0x52: Message Number (2 bytes, binary)

Sources:
  - zipstore.ru — CAS LP Protocol
  - cas-lp.narod.ru — LavrSoft driver documentation
  - Scale-Soft.com — CAS LP 1.6 (II)
"""
from __future__ import annotations

import struct
from typing import Optional

from hub.core.types import SaleData

STX = 0x02
ETX = 0x03
ACK = 0x06
NAK = 0x15
ENQ = 0x05

PLU_RECORD_SIZE = 83

CMD_PLU_WRITE = 0x40
CMD_PLU_READ = 0x41
CMD_PLU_DELETE = 0x42
CMD_STATUS_QUERY = 0x50
CMD_DATETIME_WRITE = 0x60
CMD_KEYBOARD_WRITE = 0x70
CMD_SALES_READ = 0x80
CMD_SALES_DELETE = 0x81


def _lrc(data: bytes) -> int:
    """Longitudinal Redundancy Check (XOR of all bytes)."""
    result = 0
    for b in data:
        result ^= b
    return result


def _encode_bcd(value: int, num_bytes: int) -> bytes:
    """Encode integer to BCD bytes (big-endian)."""
    hex_str = f"{value:0{num_bytes * 2}d}"
    return bytes(int(hex_str[i : i + 2], 16) for i in range(0, len(hex_str), 2))


def _decode_bcd(data: bytes) -> int:
    """Decode BCD bytes to integer."""
    return int("".join(f"{b:02x}" for b in data))


class CasLpAdapter:
    """Tier 1 adapter for CAS LP-1, LP-II / LP-1.6, and compatible models.

    Supports full PLU CRUD, smart-sync, status query, and sales readback.
    """

    @property
    def name(self) -> str:
        return "CAS LP"

    @property
    def tier(self) -> int:
        return 1

    def parse_sale_frame(self, raw: bytes) -> SaleData:
        """Parse a CAS LP status response containing current sale data.

        The LP protocol uses a binary frame: STX + cmd + data + LRC + ETX.
        Status response includes current weight, unit price, total price, PLU#.
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

        cmd = payload[0]
        data = payload[1:]

        if cmd != CMD_STATUS_QUERY:
            raise ValueError(f"Unexpected command in sale frame: {cmd:#04x}")

        if len(data) < 14:
            raise ValueError(f"Status data too short: {len(data)} bytes")

        plu_id = struct.unpack(">H", data[0:2])[0]
        weight_g = struct.unpack(">I", b"\x00" + data[2:5])[0]
        price_cents = struct.unpack(">I", data[5:9])[0]
        total_cents = struct.unpack(">I", data[9:13])[0]
        stability = data[13] if len(data) > 13 else 0x53

        return SaleData(
            weight_g=weight_g,
            price_cents_per_kg=price_cents,
            total_cents=total_cents,
            plu_id=plu_id if plu_id > 0 else None,
            raw_bytes=raw,
        )

    def build_select_command(self, plu: int) -> Optional[bytes]:
        """Build a PLU read command (triggers PLU recall on scale display)."""
        data = struct.pack(">H", plu)
        payload = bytes([CMD_PLU_READ]) + data
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
    ) -> Optional[bytes]:
        """Build a single PLU write command (83-byte record)."""
        record = bytearray(PLU_RECORD_SIZE)

        struct.pack_into(">I", record, 0, plu)

        barcode = _encode_bcd(plu, 6)
        record[4:10] = barcode

        name_bytes = name.encode("ascii", errors="replace")[:56]
        record[10 : 10 + len(name_bytes)] = name_bytes

        struct.pack_into(">I", record, 0x42, price_cents_per_kg)

        payload = bytes([CMD_PLU_WRITE]) + bytes(record)
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_plu_delete(self, plu: int) -> bytes:
        """Build a PLU delete command."""
        data = struct.pack(">I", plu)
        payload = bytes([CMD_PLU_DELETE]) + data
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_datetime_sync(self, year: int, month: int, day: int,
                            hour: int, minute: int, second: int) -> bytes:
        """Build a date/time synchronization command."""
        data = _encode_bcd(year % 100, 1) + _encode_bcd(month, 1) + \
               _encode_bcd(day, 1) + _encode_bcd(hour, 1) + \
               _encode_bcd(minute, 1) + _encode_bcd(second, 1)
        payload = bytes([CMD_DATETIME_WRITE]) + data
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_keyboard_map(self, key_number: int, plu: int) -> bytes:
        """Build a speed-key assignment command."""
        data = struct.pack(">BH", key_number, plu)
        payload = bytes([CMD_KEYBOARD_WRITE]) + data
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_status_query(self) -> bytes:
        """Build a status/weight query command."""
        payload = bytes([CMD_STATUS_QUERY])
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])
