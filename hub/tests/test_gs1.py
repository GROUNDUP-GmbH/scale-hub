"""Tests for GS1 Digital Link builder."""
from __future__ import annotations

from datetime import date

from app.utils.gs1 import build_digital_link, encode_date_ai, encode_weight_ai


def test_encode_weight():
    ai, val = encode_weight_ai(1.25)
    assert ai == "3103"
    assert val == "001250"


def test_encode_weight_zero():
    _, val = encode_weight_ai(0.001)
    assert val == "000001"


def test_encode_date_from_date():
    result = encode_date_ai(date(2026, 3, 25))
    assert result == "260325"


def test_encode_date_from_iso_string():
    result = encode_date_ai("2026-03-25")
    assert result == "260325"


def test_encode_date_passthrough_yymmdd():
    assert encode_date_ai("260325") == "260325"


def test_build_full_link():
    link = build_digital_link(
        base_url="https://groundup.bio",
        gtin="09012345678908",
        weight_kg=1.25,
        lot="LOT42",
        expiry="2026-03-25",
    )
    assert link == "https://groundup.bio/01/09012345678908/3103/001250/10/LOT42/15/260325"


def test_build_link_without_optional():
    link = build_digital_link(
        base_url="https://groundup.bio",
        gtin="09012345678908",
        weight_kg=0.5,
    )
    assert link == "https://groundup.bio/01/09012345678908/3103/000500"
