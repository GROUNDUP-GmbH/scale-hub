"""MASSA-K adapter — Tier 1 (RS-232 + Ethernet).

Supports MASSA-K ВПМ (VPM, label printing), ВП (VP, label printing),
and basic MASSA-K weight-only scales.

ВПМ/ВП models: Tier 1 (full PLU upload)
Basic models: Tier 2 (weight read only)

Interface: RS-232 and Ethernet TCP/IP

Wire protocol uses STX/ETX framing with binary commands.
PLU records support: number, name, price, shelf life, barcode format,
  tare, ingredients, special messages.

Up to 20,000 PLU capacity on ВПМ models.

Sources:
  - Scale-Soft.com — МАССА-К ВПМ
  - Scale-Soft.com — МАССА-К ВП
  - Scale-Soft.com — МАССА-К (basic)
"""
from __future__ import annotations

import struct
from typing import Optional

from hub.core.types import SaleData

STX = 0x02
ETX = 0x03
ACK = 0x06
NAK = 0x15

CMD_PLU_WRITE = 0x30
CMD_PLU_DELETE = 0x31
CMD_INGREDIENT_WRITE = 0x32
CMD_MESSAGE_WRITE = 0x33
CMD_KEYBOARD_WRITE = 0x34
CMD_DATETIME_WRITE = 0x35
CMD_WEIGHT_REQUEST = 0x36
CMD_STATUS_QUERY = 0x37


def _crc16(data: bytes) -> int:
    """CRC-16 checksum (MASSA-K variant)."""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


class MassaKAdapter:
    """Tier 1 adapter for MASSA-K ВПМ/ВП label printing scales.

    For basic MASSA-K scales (weight-only), use MassaKBasicAdapter.
    """

    def __init__(self, host: str = "", port: int = 5001):
        self._host = host
        self._port = port

    @property
    def name(self) -> str:
        return "MASSA-K VPM"

    @property
    def tier(self) -> int:
        return 1

    def parse_sale_frame(self, raw: bytes) -> SaleData:
        """Parse a MASSA-K weight/sale response.

        Frame: STX [cmd] [data] [CRC16-LE] ETX
        Data format varies by command response.
        """
        if len(raw) < 6:
            raise ValueError(f"Frame too short: {len(raw)} bytes")

        if raw[0] != STX or raw[-1] != ETX:
            raise ValueError("Invalid frame delimiters")

        payload = raw[1:-3]
        crc_bytes = raw[-3:-1]
        expected_crc = struct.unpack("<H", crc_bytes)[0]
        actual_crc = _crc16(payload)

        if actual_crc != expected_crc:
            raise ValueError(
                f"CRC mismatch: expected {expected_crc:#06x}, "
                f"got {actual_crc:#06x}"
            )

        cmd = payload[0]
        data = payload[1:]

        if len(data) < 8:
            raise ValueError(f"Data too short for sale frame: {len(data)} bytes")

        weight_g = struct.unpack("<I", data[0:4])[0]
        price_cents = struct.unpack("<I", data[4:8])[0]
        total_cents = 0
        plu_id = None

        if len(data) >= 12:
            total_cents = struct.unpack("<I", data[8:12])[0]
        if len(data) >= 14:
            plu_id = struct.unpack("<H", data[12:14])[0]
            if plu_id == 0:
                plu_id = None

        return SaleData(
            weight_g=weight_g,
            price_cents_per_kg=price_cents,
            total_cents=total_cents,
            plu_id=plu_id,
            raw_bytes=raw,
        )

    def build_select_command(self, plu: int) -> Optional[bytes]:
        """Build a PLU recall command."""
        data = struct.pack("<H", plu)
        return self._build_frame(CMD_STATUS_QUERY, data)

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
    ) -> Optional[bytes]:
        """Build a PLU write command.

        Record structure:
          PLU number (2 bytes LE)
          Name (40 bytes, CP1251 encoded, null-padded)
          Price in cents/kg (4 bytes LE)
          Shelf life in hours (2 bytes LE)
          Tare in grams (2 bytes LE)
          Barcode format (1 byte)
        """
        record = bytearray(51)
        struct.pack_into("<H", record, 0, plu)

        name_bytes = name.encode("cp1251", errors="replace")[:40]
        record[2 : 2 + len(name_bytes)] = name_bytes

        struct.pack_into("<I", record, 42, price_cents_per_kg)

        struct.pack_into("<H", record, 46, 0)
        struct.pack_into("<H", record, 48, 0)
        record[50] = 0x01

        return self._build_frame(CMD_PLU_WRITE, bytes(record))

    def build_plu_delete(self, plu: int) -> bytes:
        """Build a PLU delete command."""
        data = struct.pack("<H", plu)
        return self._build_frame(CMD_PLU_DELETE, data)

    def build_ingredient_upload(self, ingredient_id: int, text: str) -> bytes:
        """Build an ingredient text upload command."""
        text_bytes = text.encode("cp1251", errors="replace")[:200]
        data = struct.pack("<H", ingredient_id) + text_bytes
        return self._build_frame(CMD_INGREDIENT_WRITE, data)

    def build_message_upload(self, message_id: int, text: str) -> bytes:
        """Build a special message upload command."""
        text_bytes = text.encode("cp1251", errors="replace")[:200]
        data = struct.pack("<H", message_id) + text_bytes
        return self._build_frame(CMD_MESSAGE_WRITE, data)

    def build_keyboard_map(self, key_number: int, plu: int) -> bytes:
        """Build a speed-key assignment command."""
        data = struct.pack("<BH", key_number, plu)
        return self._build_frame(CMD_KEYBOARD_WRITE, data)

    def build_datetime_sync(self, year: int, month: int, day: int,
                            hour: int, minute: int, second: int) -> bytes:
        """Build a date/time synchronization command."""
        data = struct.pack("<HBBBBB", year, month, day, hour, minute, second)
        return self._build_frame(CMD_DATETIME_WRITE, data)

    def build_weight_request(self) -> bytes:
        """Build a weight query command."""
        return self._build_frame(CMD_WEIGHT_REQUEST, b"")

    def _build_frame(self, cmd: int, data: bytes) -> bytes:
        """Build a MASSA-K protocol frame: STX + cmd + data + CRC16-LE + ETX."""
        payload = bytes([cmd]) + data
        crc = _crc16(payload)
        crc_bytes = struct.pack("<H", crc)
        return bytes([STX]) + payload + crc_bytes + bytes([ETX])


class MassaKBasicAdapter:
    """Tier 2 adapter for basic MASSA-K scales (weight-only, no PLU upload)."""

    @property
    def name(self) -> str:
        return "MASSA-K Basic"

    @property
    def tier(self) -> int:
        return 2

    def parse_sale_frame(self, raw: bytes) -> SaleData:
        """Parse a basic MASSA-K weight response (weight only, no price)."""
        if len(raw) < 6:
            raise ValueError(f"Frame too short: {len(raw)} bytes")

        if raw[0] != STX or raw[-1] != ETX:
            raise ValueError("Invalid frame delimiters")

        payload = raw[1:-3]
        crc_bytes = raw[-3:-1]
        expected_crc = struct.unpack("<H", crc_bytes)[0]
        actual_crc = _crc16(payload)

        if actual_crc != expected_crc:
            raise ValueError(
                f"CRC mismatch: expected {expected_crc:#06x}, "
                f"got {actual_crc:#06x}"
            )

        data = payload[1:]
        if len(data) < 4:
            raise ValueError(f"Data too short: {len(data)} bytes")

        weight_g = struct.unpack("<I", data[0:4])[0]

        return SaleData(
            weight_g=weight_g,
            price_cents_per_kg=0,
            total_cents=0,
            raw_bytes=raw,
        )

    def build_select_command(self, plu: int) -> Optional[bytes]:
        return None

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
    ) -> Optional[bytes]:
        return None
