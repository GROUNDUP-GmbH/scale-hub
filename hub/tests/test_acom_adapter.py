"""Tests for hub.adapters.acom — Acom Tier 1 adapter."""
import pytest
from hub.adapters.acom import AcomAdapter, STX, ETX, _lrc


class TestAcomHelpers:
    def test_lrc(self):
        assert _lrc(b"\x01\x02\x03") == 0x01 ^ 0x02 ^ 0x03


class TestAcomAdapter:
    def setup_method(self):
        self.adapter = AcomAdapter()

    def test_tier_and_name(self):
        assert self.adapter.tier == 1
        assert self.adapter.name == "Acom"

    def test_parse_sale_frame(self):
        data = b"S001250,002490,003113,000042"
        lrc = _lrc(data)
        frame = bytes([STX]) + data + bytes([lrc, ETX])
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 1250
        assert sale.price_cents_per_kg == 2490
        assert sale.total_cents == 3113
        assert sale.plu_id == 42

    def test_parse_weight_only(self):
        data = b"S001250"
        lrc = _lrc(data)
        frame = bytes([STX]) + data + bytes([lrc, ETX])
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 1250
        assert sale.price_cents_per_kg == 0
        assert sale.plu_id is None

    def test_parse_short_frame_raises(self):
        with pytest.raises(ValueError, match="too short"):
            self.adapter.parse_sale_frame(b"\x02\x03")

    def test_parse_bad_lrc_raises(self):
        data = b"S001250"
        frame = bytes([STX]) + data + bytes([0xFF, ETX])
        with pytest.raises(ValueError, match="LRC mismatch"):
            self.adapter.parse_sale_frame(frame)

    def test_build_select_command(self):
        cmd = self.adapter.build_select_command(42)
        assert cmd is not None
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_plu_upload(self):
        cmd = self.adapter.build_plu_upload(1, "Honig Bio", 890)
        assert cmd is not None
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_plu_delete(self):
        cmd = self.adapter.build_plu_delete(42)
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
