"""Tests for ZPL label generation."""
from __future__ import annotations

from app.utils.zpl import build_zpl_label


def test_label_contains_product():
    zpl = build_zpl_label(
        product_name="Kartoffeln lose",
        weight_kg=2.34,
        unit_price=2.50,
        total_price=5.85,
        digital_link="https://groundup.bio/01/123/3103/002340",
    )
    assert "^XA" in zpl
    assert "^XZ" in zpl
    assert "Kartoffeln lose" in zpl
    assert "2.340 kg" in zpl
    assert "5.85 EUR" in zpl


def test_label_contains_qr():
    zpl = build_zpl_label(
        product_name="Test",
        weight_kg=1.0,
        unit_price=10.0,
        total_price=10.0,
        digital_link="https://example.com/01/123",
    )
    assert "^BQN" in zpl
    assert "https://example.com/01/123" in zpl


def test_label_with_lot_and_expiry():
    zpl = build_zpl_label(
        product_name="Kaese",
        weight_kg=0.5,
        unit_price=24.50,
        total_price=12.25,
        digital_link="https://groundup.bio/01/X",
        gtin="1234",
        lot="LOT42",
        expiry="260325",
    )
    assert "Charge: LOT42" in zpl
    assert "MHD: 260325" in zpl
    assert "GTIN: 1234" in zpl
