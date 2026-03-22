"""Tests for hub.core.sale_processor — price calculation and consistency."""
import pytest
from hub.core.sale_processor import compute_price, consistency_hash, SaleProcessor
from hub.core.audit_log import AuditLog
from hub.core.state_machine import StateMachine
from hub.core.types import SaleData


class TestComputePrice:
    def test_basic_calculation(self):
        assert compute_price(1000, 1000) == 1000  # 1kg @ 10.00/kg = 10.00

    def test_fractional_weight(self):
        assert compute_price(1250, 2490) == 3113  # 1.25kg @ 24.90/kg = 31.13

    def test_zero_weight(self):
        assert compute_price(0, 5000) == 0

    def test_one_gram(self):
        assert compute_price(1, 99999) == 100  # 1g @ 999.99/kg = 1.00 (rounded)

    def test_heavy_load(self):
        assert compute_price(15000, 100) == 1500  # 15kg @ 1.00/kg = 15.00

    def test_negative_weight_rejected(self):
        with pytest.raises(ValueError):
            compute_price(-1, 100)

    def test_negative_price_rejected(self):
        with pytest.raises(ValueError):
            compute_price(100, -1)

    def test_rounding_up(self):
        # 333g @ 10.00/kg = 3.33, rounds to 3.33
        result = compute_price(333, 1000)
        assert result == 333  # (333*1000+500)//1000 = 333

    def test_rounding_boundary(self):
        # 500g @ 9.99/kg = 4.995 -> rounds to 5.00
        result = compute_price(500, 999)
        assert result == 500  # (500*999+500)//1000 = 500


class TestConsistencyHash:
    def test_deterministic(self):
        sale = SaleData(weight_g=1000, price_cents_per_kg=500, total_cents=500)
        h1 = consistency_hash(sale, "2026-03-22T10:00:00+00:00")
        h2 = consistency_hash(sale, "2026-03-22T10:00:00+00:00")
        assert h1 == h2

    def test_different_timestamps_differ(self):
        sale = SaleData(weight_g=1000, price_cents_per_kg=500, total_cents=500)
        h1 = consistency_hash(sale, "2026-03-22T10:00:00+00:00")
        h2 = consistency_hash(sale, "2026-03-22T10:00:01+00:00")
        assert h1 != h2

    def test_different_weights_differ(self):
        s1 = SaleData(weight_g=1000, price_cents_per_kg=500, total_cents=500)
        s2 = SaleData(weight_g=1001, price_cents_per_kg=500, total_cents=500)
        ts = "2026-03-22T10:00:00+00:00"
        assert consistency_hash(s1, ts) != consistency_hash(s2, ts)


class TestSaleProcessor:
    def test_process_valid_sale(self, tmp_path):
        audit = AuditLog(tmp_path / "audit.jsonl")
        sm = StateMachine()
        proc = SaleProcessor(audit=audit, state=sm)

        sm.begin_weighing("honey", 42)
        sale = SaleData(weight_g=1250, price_cents_per_kg=2490, total_cents=3113)
        result = proc.process_sale(sale)

        assert result["weight_g"] == 1250
        assert result["total_cents"] == 3113
        assert "consistency_hash" in result
        assert result["audit_seq"] > 0

    def test_reject_sale_in_idle(self, tmp_path):
        audit = AuditLog(tmp_path / "audit.jsonl")
        sm = StateMachine()
        proc = SaleProcessor(audit=audit, state=sm)

        sale = SaleData(weight_g=1000, price_cents_per_kg=500, total_cents=500)
        with pytest.raises(RuntimeError, match="Cannot process sale"):
            proc.process_sale(sale)

    def test_reject_price_mismatch(self, tmp_path):
        audit = AuditLog(tmp_path / "audit.jsonl")
        sm = StateMachine()
        proc = SaleProcessor(audit=audit, state=sm)

        sm.begin_weighing("cheese", 7)
        sale = SaleData(weight_g=1000, price_cents_per_kg=500, total_cents=999)
        with pytest.raises(ValueError, match="Price mismatch"):
            proc.process_sale(sale)
