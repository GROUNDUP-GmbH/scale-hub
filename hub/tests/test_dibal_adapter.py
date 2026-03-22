"""Tests for hub.adapters.dibal — DIBAL TISA Tier 2+ adapter."""
import pytest
from hub.adapters.dibal import DibalTisaAdapter, _xor_checksum, CR, LF


class TestDibalHelpers:
    def test_xor_checksum(self):
        data = b"9801250"
        result = _xor_checksum(data)
        assert isinstance(result, int)
        assert 0 <= result <= 255


class TestDibalTisaAdapter:
    def setup_method(self):
        self.adapter = DibalTisaAdapter()

    def test_tier_and_name(self):
        assert self.adapter.tier == 3  # Tier 2+ encoded as 3
        assert self.adapter.name == "DIBAL TISA"

    def test_parse_weight_response(self):
        response = "99001250024900"
        raw = response.encode("ascii")
        sale = self.adapter.parse_sale_frame(raw)
        assert sale.weight_g == 1250
        assert sale.price_cents_per_kg == 2490

    def test_parse_total_calculation(self):
        response = "99001000010000"
        raw = response.encode("ascii")
        sale = self.adapter.parse_sale_frame(raw)
        assert sale.weight_g == 1000
        assert sale.price_cents_per_kg == 1000
        assert sale.total_cents == 1000

    def test_parse_zero_weight(self):
        response = "99000000001000"
        raw = response.encode("ascii")
        sale = self.adapter.parse_sale_frame(raw)
        assert sale.weight_g == 0
        assert sale.total_cents == 0

    def test_parse_wrong_prefix_raises(self):
        raw = b"98001250024900"
        with pytest.raises(ValueError, match="Expected '99'"):
            self.adapter.parse_sale_frame(raw)

    def test_parse_short_response_raises(self):
        raw = b"990012"
        with pytest.raises(ValueError, match="too short"):
            self.adapter.parse_sale_frame(raw)

    def test_no_select_command(self):
        assert self.adapter.build_select_command(1) is None

    def test_no_plu_upload(self):
        assert self.adapter.build_plu_upload(1, "Test", 100) is None

    def test_build_price_inject(self):
        cmd = self.adapter.build_price_inject(1250)
        assert cmd.startswith(b"98")
        assert b"01250" in cmd
        assert cmd[-2] == CR
        assert cmd[-1] == LF

    def test_build_price_inject_zero(self):
        cmd = self.adapter.build_price_inject(0)
        assert b"00000" in cmd

    def test_build_price_inject_large(self):
        cmd = self.adapter.build_price_inject(99999)
        assert b"99999" in cmd

    def test_build_weight_request(self):
        cmd = self.adapter.build_weight_request(1250)
        assert cmd.startswith(b"98")
