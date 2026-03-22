"""Tests for hub.adapters.massa_k — MASSA-K Tier 1 + Tier 2 adapters."""
import struct

import pytest
from hub.adapters.massa_k import (
    MassaKAdapter, MassaKBasicAdapter,
    STX, ETX, _crc16,
    CMD_WEIGHT_REQUEST, CMD_STATUS_QUERY,
)


def _build_frame(cmd: int, data: bytes) -> bytes:
    """Build a test frame with correct CRC."""
    payload = bytes([cmd]) + data
    crc = _crc16(payload)
    crc_bytes = struct.pack("<H", crc)
    return bytes([STX]) + payload + crc_bytes + bytes([ETX])


class TestCrc16:
    def test_known_value(self):
        result = _crc16(b"\x00\x01\x02")
        assert isinstance(result, int)
        assert 0 <= result <= 0xFFFF

    def test_deterministic(self):
        assert _crc16(b"test") == _crc16(b"test")

    def test_different_inputs(self):
        assert _crc16(b"a") != _crc16(b"b")


class TestMassaKAdapter:
    def setup_method(self):
        self.adapter = MassaKAdapter()

    def test_tier_and_name(self):
        assert self.adapter.tier == 1
        assert self.adapter.name == "MASSA-K VPM"

    def test_parse_sale_frame(self):
        data = struct.pack("<I", 1250) + \
               struct.pack("<I", 2490) + \
               struct.pack("<I", 3113) + \
               struct.pack("<H", 42)
        frame = _build_frame(CMD_STATUS_QUERY, data)
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 1250
        assert sale.price_cents_per_kg == 2490
        assert sale.total_cents == 3113
        assert sale.plu_id == 42

    def test_parse_no_plu(self):
        data = struct.pack("<I", 500) + \
               struct.pack("<I", 1000) + \
               struct.pack("<I", 500) + \
               struct.pack("<H", 0)
        frame = _build_frame(CMD_STATUS_QUERY, data)
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.plu_id is None

    def test_parse_short_frame_raises(self):
        with pytest.raises(ValueError, match="too short"):
            self.adapter.parse_sale_frame(b"\x02\x03")

    def test_parse_bad_crc_raises(self):
        data = struct.pack("<I", 1250) + struct.pack("<I", 2490) + b"\x00" * 6
        payload = bytes([CMD_STATUS_QUERY]) + data
        bad_crc = struct.pack("<H", 0xDEAD)
        frame = bytes([STX]) + payload + bad_crc + bytes([ETX])
        with pytest.raises(ValueError, match="CRC mismatch"):
            self.adapter.parse_sale_frame(frame)

    def test_build_plu_upload(self):
        cmd = self.adapter.build_plu_upload(1, "Rindfleisch", 1890)
        assert cmd is not None
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_plu_delete(self):
        cmd = self.adapter.build_plu_delete(42)
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_ingredient_upload(self):
        cmd = self.adapter.build_ingredient_upload(1, "Rindfleisch, Salz")
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_message_upload(self):
        cmd = self.adapter.build_message_upload(1, "Bio-zertifiziert")
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_keyboard_map(self):
        cmd = self.adapter.build_keyboard_map(1, 42)
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_datetime_sync(self):
        cmd = self.adapter.build_datetime_sync(2026, 3, 22, 14, 30, 0)
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_weight_request(self):
        cmd = self.adapter.build_weight_request()
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_select_command(self):
        cmd = self.adapter.build_select_command(42)
        assert cmd is not None
        assert cmd[0] == STX
        assert cmd[-1] == ETX


class TestMassaKBasicAdapter:
    def setup_method(self):
        self.adapter = MassaKBasicAdapter()

    def test_tier_and_name(self):
        assert self.adapter.tier == 2
        assert self.adapter.name == "MASSA-K Basic"

    def test_parse_weight_only(self):
        data = struct.pack("<I", 750)
        frame = _build_frame(CMD_WEIGHT_REQUEST, data)
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 750
        assert sale.price_cents_per_kg == 0
        assert sale.total_cents == 0

    def test_no_select_command(self):
        assert self.adapter.build_select_command(1) is None

    def test_no_plu_upload(self):
        assert self.adapter.build_plu_upload(1, "Test", 100) is None
