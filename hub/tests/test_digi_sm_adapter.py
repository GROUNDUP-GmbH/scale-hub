"""Tests for hub.adapters.digi_sm — DIGI SM Tier 1 adapter."""
import pytest
from hub.adapters.digi_sm import DigiSmAdapter, STX, ETX, _crc


class TestDigiSmHelpers:
    def test_crc(self):
        data = b"w001?01250"
        assert isinstance(_crc(data), int)
        assert 0 <= _crc(data) <= 255


class TestDigiSmAdapter:
    def setup_method(self):
        self.adapter = DigiSmAdapter(host="192.168.1.100", port=3001)

    def test_tier_and_name(self):
        assert self.adapter.tier == 1
        assert self.adapter.name == "DIGI SM"

    def test_host_and_port(self):
        assert self.adapter.host == "192.168.1.100"
        assert self.adapter.port == 3001

    def test_parse_weight_frame(self):
        inner = b"w001?01250"
        crc = _crc(inner)
        frame = bytes([STX]) + inner + bytes([crc, ETX])
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 1250

    def test_parse_weight_with_price(self):
        inner = b"w001?01250?02490?03113?00042"
        crc = _crc(inner)
        frame = bytes([STX]) + inner + bytes([crc, ETX])
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 1250
        assert sale.price_cents_per_kg == 2490
        assert sale.total_cents == 3113
        assert sale.plu_id == 42

    def test_parse_short_frame_raises(self):
        with pytest.raises(ValueError, match="too short"):
            self.adapter.parse_sale_frame(b"\x02\x03")

    def test_parse_bad_crc_raises(self):
        inner = b"w001?01250"
        frame = bytes([STX]) + inner + bytes([0xFF, ETX])
        with pytest.raises(ValueError, match="CRC mismatch"):
            self.adapter.parse_sale_frame(frame)

    def test_no_select_command(self):
        assert self.adapter.build_select_command(1) is None

    def test_build_plu_upload(self):
        cmd = self.adapter.build_plu_upload(42, "Honig Bio", 890)
        assert cmd is not None
        assert cmd[0] == STX
        assert cmd[-1] == ETX
        assert b"Honig Bio" in cmd

    def test_build_plu_delete(self):
        cmd = self.adapter.build_plu_delete(42)
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_weight_request(self):
        cmd = self.adapter.build_weight_request()
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

    def test_build_ingredient_upload(self):
        cmd = self.adapter.build_ingredient_upload(1, "Rindfleisch, Salz, Pfeffer")
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_message_upload(self):
        cmd = self.adapter.build_message_upload(1, "Sonderangebot!")
        assert cmd[0] == STX
        assert cmd[-1] == ETX
