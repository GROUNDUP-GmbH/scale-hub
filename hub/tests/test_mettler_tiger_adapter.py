"""Tests for hub.adapters.mettler_tiger — Mettler Toledo Tiger Tier 1 adapter."""
import pytest
from hub.adapters.mettler_tiger import MettlerTigerAdapter, STX, CR, LF


class TestMettlerTigerAdapter:
    def setup_method(self):
        self.adapter = MettlerTigerAdapter()

    def test_tier_and_name(self):
        assert self.adapter.tier == 1
        assert self.adapter.name == "Mettler Toledo Tiger"

    def test_parse_weight_kg(self):
        frame = bytes([STX]) + b"  1.234 kg" + bytes([CR, LF])
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 1234

    def test_parse_weight_g(self):
        frame = bytes([STX]) + b" 500 g" + bytes([CR, LF])
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 500

    def test_parse_weight_large(self):
        frame = bytes([STX]) + b" 12.500 kg" + bytes([CR, LF])
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 12500

    def test_parse_weight_zero(self):
        frame = bytes([STX]) + b"  0.000 kg" + bytes([CR, LF])
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.weight_g == 0

    def test_parse_empty_raises(self):
        frame = bytes([STX]) + b"  " + bytes([CR, LF])
        with pytest.raises(ValueError, match="Empty weight"):
            self.adapter.parse_sale_frame(frame)

    def test_parse_invalid_weight_raises(self):
        frame = bytes([STX]) + b" ABC kg" + bytes([CR, LF])
        with pytest.raises(ValueError, match="Cannot parse"):
            self.adapter.parse_sale_frame(frame)

    def test_price_and_total_are_zero(self):
        """Tiger weight stream does not include price data."""
        frame = bytes([STX]) + b"  1.234 kg" + bytes([CR, LF])
        sale = self.adapter.parse_sale_frame(frame)
        assert sale.price_cents_per_kg == 0
        assert sale.total_cents == 0

    def test_build_select_command(self):
        cmd = self.adapter.build_select_command(42)
        assert cmd is not None
        assert cmd.endswith(b"\r\n")
        assert b"PR" in cmd

    def test_build_plu_upload(self):
        cmd = self.adapter.build_plu_upload(1, "Rindfleisch Bio", 1890)
        assert cmd is not None
        assert cmd.endswith(b"\r\n")
        assert b"PW" in cmd
        assert b"Rindfleisch Bio" in cmd

    def test_build_plu_delete(self):
        cmd = self.adapter.build_plu_delete(42)
        assert cmd.endswith(b"\r\n")
        assert b"PD" in cmd

    def test_build_group_upload(self):
        cmd = self.adapter.build_group_upload(1, "Fleisch")
        assert cmd.endswith(b"\r\n")
        assert b"GW" in cmd

    def test_build_group_delete(self):
        cmd = self.adapter.build_group_delete(1)
        assert cmd.endswith(b"\r\n")

    def test_build_tare_upload(self):
        cmd = self.adapter.build_tare_upload(1, 250)
        assert cmd.endswith(b"\r\n")
        assert b"TW" in cmd

    def test_build_tax_upload(self):
        cmd = self.adapter.build_tax_upload(1, 200)
        assert cmd.endswith(b"\r\n")
        assert b"XW" in cmd

    def test_build_datetime_sync(self):
        cmd = self.adapter.build_datetime_sync(2026, 3, 22, 14, 30, 0)
        assert cmd.endswith(b"\r\n")
        assert b"DT" in cmd

    def test_build_store_name(self):
        cmd = self.adapter.build_store_name("Hofladen Berend")
        assert cmd.endswith(b"\r\n")
        assert b"SN" in cmd

    def test_build_running_text(self):
        cmd = self.adapter.build_running_text("Heute frisch!")
        assert cmd.endswith(b"\r\n")
        assert b"RT" in cmd

    def test_build_label_format(self):
        cmd = self.adapter.build_label_format(3)
        assert cmd.endswith(b"\r\n")
        assert b"LF" in cmd

    def test_build_keyboard_map(self):
        cmd = self.adapter.build_keyboard_map(1, 42)
        assert cmd.endswith(b"\r\n")
        assert b"KW" in cmd

    def test_build_special_offer(self):
        cmd = self.adapter.build_special_offer(42, 1590, "Aktion!", 7)
        assert cmd.endswith(b"\r\n")
        assert b"SO" in cmd

    def test_build_barcode_format(self):
        cmd = self.adapter.build_barcode_format(13)
        assert cmd.endswith(b"\r\n")
        assert b"BF" in cmd

    def test_build_weight_request(self):
        cmd = self.adapter.build_weight_request()
        assert cmd == b"W\r\n"
