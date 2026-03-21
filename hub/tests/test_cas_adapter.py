"""Tests for the CAS ER-Plus adapter."""
from __future__ import annotations

import pytest

from app.adapters.cas_erplus import CasErPlusAdapter, CasProtocolError


@pytest.fixture
def adapter() -> CasErPlusAdapter:
    return CasErPlusAdapter()


def test_parse_valid_sale_frame(adapter: CasErPlusAdapter):
    raw = b"\x02PLU=00101;W=1.250;UP=12.00;TP=15.00\x03"
    sale = adapter.parse_sale_frame(raw)
    assert sale.plu == 101
    assert sale.weight_kg == 1.25
    assert sale.unit_price == 12.0
    assert sale.total_price == 15.0


def test_parse_frame_without_plu(adapter: CasErPlusAdapter):
    raw = b"\x02W=0.500;UP=24.50;TP=12.25\x03"
    sale = adapter.parse_sale_frame(raw)
    assert sale.plu is None
    assert sale.weight_kg == 0.5


def test_parse_malformed_frame(adapter: CasErPlusAdapter):
    raw = b"\x02GARBAGE\x03"
    with pytest.raises(CasProtocolError):
        adapter.parse_sale_frame(raw)


def test_build_select_plu(adapter: CasErPlusAdapter):
    cmd = adapter.build_select_plu_command(101)
    assert cmd[0] == 0x02
    assert cmd[-1] == 0x03
    assert b"PLU=00101" in cmd


def test_build_select_plu_rejects_zero(adapter: CasErPlusAdapter):
    with pytest.raises(CasProtocolError):
        adapter.build_select_plu_command(0)


def test_build_plu_upload(adapter: CasErPlusAdapter):
    cmd = adapter.build_plu_upload_command(
        plu=103, name="Rind Mischpaket", unit_price=18.90, gtin="09012345000103",
    )
    assert b"PLU=00103" in cmd
    assert b"NAME=Rind Mischpaket" in cmd
    assert b"UP=18.90" in cmd
    assert b"GTIN=09012345000103" in cmd
