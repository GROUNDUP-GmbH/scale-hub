"""Transaction state machine (REQ-SW-06, Decision 06).

Controls the lifecycle of a single weighing transaction.
PLU sync is only allowed in IDLE state — blocked during active
transactions (protective interface requirement).

States:
    IDLE -> WEIGHING -> PRINTING -> IDLE
    Any  -> ERROR (on failure, auto-recovers via timeout)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from time import monotonic
from typing import Optional


class ScaleState(str, Enum):
    IDLE = "IDLE"
    WEIGHING = "WEIGHING"
    PRINTING = "PRINTING"
    ERROR = "ERROR"


@dataclass
class ActiveTransaction:
    product_id: str
    plu: int
    started_at: float = field(default_factory=monotonic)


class StateMachine:
    """Thread-safe state machine for one scale transaction at a time.

    Enforces WELMEC 7.2 §4.4.2.1(a): no configuration changes
    during active measurement.
    """

    TIMEOUT_S = 120.0

    def __init__(self) -> None:
        self._lock = Lock()
        self._state = ScaleState.IDLE
        self._tx: Optional[ActiveTransaction] = None

    @property
    def state(self) -> ScaleState:
        with self._lock:
            self._auto_timeout()
            return self._state

    @property
    def transaction(self) -> Optional[ActiveTransaction]:
        return self._tx

    def is_idle(self) -> bool:
        return self.state == ScaleState.IDLE

    def begin_weighing(self, product_id: str, plu: int) -> None:
        with self._lock:
            self._auto_timeout()
            if self._state != ScaleState.IDLE:
                raise RuntimeError(
                    f"Cannot start weighing in state {self._state.value}"
                )
            self._tx = ActiveTransaction(product_id=product_id, plu=plu)
            self._state = ScaleState.WEIGHING

    def begin_printing(self) -> None:
        with self._lock:
            if self._state != ScaleState.WEIGHING:
                raise RuntimeError(
                    f"Cannot print in state {self._state.value}"
                )
            self._state = ScaleState.PRINTING

    def finalize(self) -> None:
        with self._lock:
            self._tx = None
            self._state = ScaleState.IDLE

    def fail(self, reason: str = "") -> None:
        with self._lock:
            self._state = ScaleState.ERROR

    def reset(self) -> None:
        with self._lock:
            self._tx = None
            self._state = ScaleState.IDLE

    def snapshot(self) -> dict:
        with self._lock:
            self._auto_timeout()
            return {
                "state": self._state.value,
                "product_id": self._tx.product_id if self._tx else None,
                "plu": self._tx.plu if self._tx else None,
            }

    def _auto_timeout(self) -> None:
        if (
            self._tx
            and self._state != ScaleState.IDLE
            and (monotonic() - self._tx.started_at) > self.TIMEOUT_S
        ):
            self._tx = None
            self._state = ScaleState.IDLE
