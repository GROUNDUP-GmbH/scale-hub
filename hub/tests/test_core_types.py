"""Tests for hub.core.types — integer-only data structures."""
import pytest
from hub.core.types import SaleData, PluRecord


class TestSaleData:
    def test_valid_sale(self):
        s = SaleData(weight_g=1250, price_cents_per_kg=2490, total_cents=3113)
        assert s.weight_g == 1250
        assert s.price_cents_per_kg == 2490
        assert s.total_cents == 3113

    def test_negative_weight_rejected(self):
        with pytest.raises(ValueError, match="Negative weight"):
            SaleData(weight_g=-1, price_cents_per_kg=100, total_cents=0)

    def test_negative_total_rejected(self):
        with pytest.raises(ValueError, match="Negative total"):
            SaleData(weight_g=100, price_cents_per_kg=100, total_cents=-1)

    def test_zero_weight_allowed(self):
        s = SaleData(weight_g=0, price_cents_per_kg=100, total_cents=0)
        assert s.weight_g == 0

    def test_immutable(self):
        s = SaleData(weight_g=500, price_cents_per_kg=100, total_cents=50)
        with pytest.raises(AttributeError):
            s.weight_g = 999  # type: ignore[misc]

    def test_with_plu_and_tare(self):
        s = SaleData(weight_g=1000, price_cents_per_kg=500, total_cents=500, plu_id=42, tare_g=50)
        assert s.plu_id == 42
        assert s.tare_g == 50


class TestPluRecord:
    def test_basic(self):
        r = PluRecord(plu=1, product_id="honey_500", name="Honig 500g", price_cents_per_kg=2490)
        assert r.plu == 1
        assert r.gtin is None
