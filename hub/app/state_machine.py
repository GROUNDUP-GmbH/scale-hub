"""
GroundUp Scale Hub – Session State Machine

Controls the lifecycle of a single weighing transaction.
Ensures that the POS can only trigger PLU selection,
and the scale remains the sole authority for price computation.

States:
    IDLE → PLU_SELECTING → READY_TO_WEIGH → SALE_LOCKED → IDLE
    Any state → ERROR (on failure)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from time import monotonic
from typing import Optional


class ScaleState(str, Enum):
    IDLE = "IDLE"
    PLU_SELECTING = "PLU_SELECTING"
    READY_TO_WEIGH = "READY_TO_WEIGH"
    SALE_LOCKED = "SALE_LOCKED"
    ERROR = "ERROR"


@dataclass
class ActiveSession:
    product_id: str
    plu: int
    requested_at: float = field(default_factory=monotonic)
    sale_received_at: Optional[float] = None


class ScaleSessionManager:
    """Thread-safe state machine for one scale transaction at a time."""

    TIMEOUT_SECONDS = 120.0

    def __init__(self) -> None:
        self._lock = Lock()
        self.state = ScaleState.IDLE
        self.active: Optional[ActiveSession] = None

    # -- transitions ----------------------------------------------------------

    def begin_plu_selection(self, product_id: str, plu: int) -> None:
        with self._lock:
            self._check_timeout()
            if self.state not in {ScaleState.IDLE, ScaleState.READY_TO_WEIGH}:
                raise RuntimeError(
                    f"Cannot select PLU in state {self.state}. "
                    "Reset or wait for current transaction to complete."
                )
            self.active = ActiveSession(product_id=product_id, plu=plu)
            self.state = ScaleState.PLU_SELECTING

    def mark_ready(self) -> None:
        with self._lock:
            if self.state != ScaleState.PLU_SELECTING:
                raise RuntimeError(f"Cannot mark ready in state {self.state}")
            self.state = ScaleState.READY_TO_WEIGH

    def lock_sale(self) -> None:
        with self._lock:
            if self.state != ScaleState.READY_TO_WEIGH:
                raise RuntimeError(f"Cannot lock sale in state {self.state}")
            if self.active:
                self.active.sale_received_at = monotonic()
            self.state = ScaleState.SALE_LOCKED

    def finalize(self) -> None:
        with self._lock:
            self.active = None
            self.state = ScaleState.IDLE

    def fail(self, reason: str = "") -> None:
        with self._lock:
            self.state = ScaleState.ERROR

    def reset(self) -> None:
        with self._lock:
            self.active = None
            self.state = ScaleState.IDLE

    # -- helpers --------------------------------------------------------------

    def _check_timeout(self) -> None:
        if (
            self.active
            and self.state != ScaleState.IDLE
            and (monotonic() - self.active.requested_at) > self.TIMEOUT_SECONDS
        ):
            self.active = None
            self.state = ScaleState.IDLE

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "state": self.state.value,
                "product_id": self.active.product_id if self.active else None,
                "plu": self.active.plu if self.active else None,
            }
