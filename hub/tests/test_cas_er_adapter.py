"""Tests for hub.adapters.cas_er — CAS ER-Plus Tier 2 adapter."""
import pytest
from hub.adapters.cas_er import CasErAdapter


class TestCasErAdapter:
    def setup_method(self):
        self.adapter = CasErAdapter()

    def test_tier(self):
        assert self.adapter.tier == 2
        assert self.adapter.name == "CAS ER-Plus"

    def test_parse_integer_format(self):
        raw = b"\x02PLU=00042;W=001250;UP=002490;TP=003113\x03"
        sale = self.adapter.parse_sale_frame(raw)
        assert sale.weight_g == 1250
        assert sale.price_cents_per_kg == 2490
        assert sale.total_cents == 3113
        assert sale.plu_id == 42

    def test_parse_decimal_format(self):
        raw = b"\x02PLU=00042;W=1.250;UP=24.90;TP=31.13\x03"
        sale = self.adapter.parse_sale_frame(raw)
        assert sale.weight_g == 1250
        assert sale.price_cents_per_kg == 2490
        assert sale.total_cents == 3113

    def test_parse_without_plu(self):
        raw = b"\x02W=000500;UP=001000;TP=000500\x03"
        sale = self.adapter.parse_sale_frame(raw)
        assert sale.plu_id is None
        assert sale.weight_g == 500

    def test_missing_weight_raises(self):
        raw = b"\x02PLU=1;UP=100;TP=100\x03"
        with pytest.raises(ValueError):
            self.adapter.parse_sale_frame(raw)

    def test_no_plu_upload(self):
        assert self.adapter.build_select_command(1) is None
        assert self.adapter.build_plu_upload(1, "test", 100) is None

    def test_raw_bytes_preserved(self):
        raw = b"\x02W=001000;UP=000500;TP=000500\x03"
        sale = self.adapter.parse_sale_frame(raw)
        assert sale.raw_bytes == raw
