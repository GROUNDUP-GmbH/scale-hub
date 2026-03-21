"""Tests for the scale controller end-to-end flow."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.adapters.cas_erplus import CasErPlusAdapter
from app.adapters.serial_layer import MockSerialWriter
from app.audit_log import AuditLog
from app.controller import ScaleController
from app.plu_map import PluMap
from app.state_machine import ScaleSessionManager, ScaleState


@pytest.fixture
def setup(tmp_path: Path):
    audit = AuditLog(tmp_path / "audit.jsonl")
    session = ScaleSessionManager()
    adapter = CasErPlusAdapter()
    writer = MockSerialWriter()
    plu_map = PluMap()
    plu_map.load_from_dict({
        "kartoffeln_lose": {"plu": 101, "name": "Kartoffeln lose", "unit_price": 2.50},
        "eier_6er": {"plu": 102, "name": "Freilandeier 6er", "unit_price": 3.60},
    })
    sales: list[dict] = []

    ctrl = ScaleController(
        adapter=adapter,
        writer=writer,
        session=session,
        audit=audit,
        plu_map=plu_map,
        publish_sale=lambda payload: sales.append(payload),
    )
    return ctrl, session, sales, writer


def test_full_sale_cycle(setup):
    ctrl, session, sales, writer = setup

    result = ctrl.select_product("kartoffeln_lose")
    assert result["ok"] is True
    assert result["plu"] == 101
    assert session.state == ScaleState.READY_TO_WEIGH

    frame = b"\x02PLU=00101;W=2.340;UP=2.50;TP=5.85\x03"
    ctrl.handle_sale_frame(frame)

    assert session.state == ScaleState.IDLE
    assert len(sales) == 1
    assert sales[0]["weight_kg"] == 2.34
    assert sales[0]["total_price"] == 5.85


def test_unknown_product_rejected(setup):
    ctrl, *_ = setup
    with pytest.raises(ValueError, match="not in allowlist"):
        ctrl.select_product("unknown_product")


def test_plu_mismatch_triggers_error(setup):
    ctrl, session, sales, writer = setup

    ctrl.select_product("kartoffeln_lose")
    frame = b"\x02PLU=00999;W=1.000;UP=5.00;TP=5.00\x03"
    ctrl.handle_sale_frame(frame)

    assert session.state == ScaleState.ERROR
    assert len(sales) == 0


def test_upload_plu(setup):
    ctrl, *_ = setup
    result = ctrl.upload_plu(plu=201, name="Honig 250g", unit_price=8.50)
    assert result["ok"] is True
    assert result["plu"] == 201
