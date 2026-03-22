"""Sale processor — the heart of the Certified Core (REQ-SW-02).

Handles the metrologically relevant data path:
  Scale bytes -> Adapter -> SaleData -> Consistency check -> Audit log

Integer-only arithmetic throughout (Decision 13).
"""
from __future__ import annotations

import hashlib
import logging
from typing import Optional

from .audit_log import AuditLog
from .state_machine import StateMachine, ScaleState
from .types import SaleData

logger = logging.getLogger(__name__)


def compute_price(weight_g: int, price_cents_per_kg: int) -> int:
    """Integer price calculation (REQ-T0-01).

    Uses truncating integer division matching EN 45501 Annex A.
    For Tier 0 (Hub calculates price) this IS the metrological calculation.
    For Tier 1/2 (scale calculates price) this is used for verification only.
    """
    if weight_g < 0 or price_cents_per_kg < 0:
        raise ValueError("Negative input")
    return (weight_g * price_cents_per_kg + 500) // 1000


def consistency_hash(sale: SaleData, timestamp: str) -> str:
    """SHA-256 consistency hash for three-way verification (Decision 13).

    Embedded in audit log, label QR, and POS payload.
    """
    data = (
        f"{sale.weight_g}:{sale.price_cents_per_kg}:{sale.total_cents}"
        f":{sale.plu_id}:{timestamp}"
    )
    return hashlib.sha256(data.encode("ascii")).hexdigest()


class SaleProcessor:
    """Processes incoming sale data from any scale adapter.

    This is the central metrological component. It:
    1. Validates the sale data
    2. Verifies price consistency (scale total vs. Hub calculation)
    3. Writes to audit log
    4. Returns the verified SaleData for further processing
    """

    PRICE_TOLERANCE_CENTS = 1

    def __init__(self, audit: AuditLog, state: StateMachine) -> None:
        self._audit = audit
        self._state = state

    def process_sale(self, sale: SaleData) -> dict:
        """Process a completed sale from the scale.

        Returns a dict with the sale data + consistency hash + audit reference.
        Raises RuntimeError if state machine rejects the sale.
        """
        if self._state.state != ScaleState.WEIGHING:
            self._audit.append("sale_rejected", {
                "reason": f"unexpected state: {self._state.state.value}",
                "weight_g": sale.weight_g,
            })
            raise RuntimeError(
                f"Cannot process sale in state {self._state.state.value}"
            )

        expected_total = compute_price(sale.weight_g, sale.price_cents_per_kg)
        price_diff = abs(sale.total_cents - expected_total)
        if price_diff > self.PRICE_TOLERANCE_CENTS:
            self._audit.append("price_mismatch", {
                "scale_total_cents": sale.total_cents,
                "hub_total_cents": expected_total,
                "diff_cents": price_diff,
                "weight_g": sale.weight_g,
                "price_cents_per_kg": sale.price_cents_per_kg,
            })
            self._state.fail("price mismatch")
            raise ValueError(
                f"Price mismatch: scale={sale.total_cents}c, "
                f"hub={expected_total}c, diff={price_diff}c"
            )

        self._state.begin_printing()

        entry = self._audit.append("sale_completed", {
            "weight_g": sale.weight_g,
            "price_cents_per_kg": sale.price_cents_per_kg,
            "total_cents": sale.total_cents,
            "plu_id": sale.plu_id,
            "tare_g": sale.tare_g,
            "raw_hex": sale.raw_bytes.hex() if sale.raw_bytes else "",
        })

        c_hash = consistency_hash(sale, entry["ts"])

        return {
            "weight_g": sale.weight_g,
            "price_cents_per_kg": sale.price_cents_per_kg,
            "total_cents": sale.total_cents,
            "plu_id": sale.plu_id,
            "tare_g": sale.tare_g,
            "consistency_hash": c_hash,
            "audit_seq": entry["seq"],
            "audit_hash": entry["entry_hash"],
            "timestamp": entry["ts"],
        }
