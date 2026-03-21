"""Tests for the scale session state machine."""
from __future__ import annotations

import pytest

from app.state_machine import ScaleSessionManager, ScaleState


def test_normal_lifecycle():
    sm = ScaleSessionManager()
    assert sm.state == ScaleState.IDLE

    sm.begin_plu_selection("kartoffeln_lose", 101)
    assert sm.state == ScaleState.PLU_SELECTING

    sm.mark_ready()
    assert sm.state == ScaleState.READY_TO_WEIGH

    sm.lock_sale()
    assert sm.state == ScaleState.SALE_LOCKED

    sm.finalize()
    assert sm.state == ScaleState.IDLE
    assert sm.active is None


def test_cannot_lock_from_idle():
    sm = ScaleSessionManager()
    with pytest.raises(RuntimeError):
        sm.lock_sale()


def test_cannot_select_during_locked():
    sm = ScaleSessionManager()
    sm.begin_plu_selection("a", 1)
    sm.mark_ready()
    sm.lock_sale()
    with pytest.raises(RuntimeError):
        sm.begin_plu_selection("b", 2)


def test_reset_clears_state():
    sm = ScaleSessionManager()
    sm.begin_plu_selection("a", 1)
    sm.mark_ready()
    sm.fail()
    assert sm.state == ScaleState.ERROR
    sm.reset()
    assert sm.state == ScaleState.IDLE


def test_reselect_from_ready():
    sm = ScaleSessionManager()
    sm.begin_plu_selection("a", 1)
    sm.mark_ready()
    sm.begin_plu_selection("b", 2)
    assert sm.active is not None
    assert sm.active.plu == 2


def test_snapshot():
    sm = ScaleSessionManager()
    snap = sm.snapshot()
    assert snap["state"] == "IDLE"
    assert snap["plu"] is None

    sm.begin_plu_selection("eggs", 42)
    snap = sm.snapshot()
    assert snap["state"] == "PLU_SELECTING"
    assert snap["plu"] == 42
