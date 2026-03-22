"""Tests for hub.adapters.cas_lp — CAS LP Tier 1 adapter."""
import struct

import pytest
from hub.adapters.cas_lp import CasLpAdapter, _lrc, _encode_bcd, _decode_bcd, CMD_STATUS_QUERY, STX, ETX


class TestCasLpHelpers:
    def test_lrc(self):
        assert _lrc(b"\x01\x02\x03") == 0x01 ^ 0x02 ^ 0x03

    def test_encode_bcd(self):
        assert _encode_bcd(123456, 3) == bytes([0x12, 0x34, 0x56])

    def test_decode_bcd(self):
        assert _decode_bcd(bytes([0x12, 0x34, 0x56])) == 123456


class TestCasLpAdapter:
    def setup_method(self):
        self.adapter = CasLpAdapter()

    def test_tier_and_name(self):
        assert self.adapter.tier == 1
        assert self.adapter.name == "CAS LP"

    def test_parse_sale_frame(self):
        plu_id = 42
        weight_g = 1250
        price_cents = 2490
        total_cents = 3113

        data = struct.pack(">H", plu_id) + \
               struct.pack(">I", weight_g)[1:] + \
               struct.pack(">I", price_cents) + \
               struct.pack(">I", total_cents) + \
               bytes([0x53])

        payload = bytes([CMD_STATUS_QUERY]) + data
        lrc = _lrc(payload)
        frame = bytes([STX]) + payload + bytes([lrc, ETX])

        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 1250
        assert sale.price_cents_per_kg == 2490
        assert sale.total_cents == 3113
        assert sale.plu_id == 42

    def test_parse_short_frame_raises(self):
        with pytest.raises(ValueError, match="too short"):
            self.adapter.parse_sale_frame(b"\x02\x03")

    def test_parse_bad_lrc_raises(self):
        payload = bytes([CMD_STATUS_QUERY]) + b"\x00" * 14
        bad_lrc = 0xFF
        frame = bytes([STX]) + payload + bytes([bad_lrc, ETX])
        with pytest.raises(ValueError, match="LRC mismatch"):
            self.adapter.parse_sale_frame(frame)

    def test_build_select_command(self):
        cmd = self.adapter.build_select_command(42)
        assert cmd is not None
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_plu_upload(self):
        cmd = self.adapter.build_plu_upload(1, "Rindfleisch", 1890)
        assert cmd is not None
        assert cmd[0] == STX
        assert cmd[-1] == ETX
        assert len(cmd) > 83

    def test_build_plu_delete(self):
        cmd = self.adapter.build_plu_delete(42)
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_status_query(self):
        cmd = self.adapter.build_status_query()
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_datetime_sync(self):
        cmd = self.adapter.build_datetime_sync(2026, 3, 22, 14, 30, 0)
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_keyboard_map(self):
        cmd = self.adapter.build_keyboard_map(1, 42)
        assert cmd[0] == STX
        assert cmd[-1] == ETX
