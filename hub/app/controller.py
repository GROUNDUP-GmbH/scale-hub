"""
GroundUp Scale Hub – Scale Controller

Orchestrates the entire weighing workflow:
  1. POS selects product → Hub resolves PLU → sends to scale
  2. Scale weighs, computes price, sends sale frame
  3. Hub logs, locks, forwards to POS

The controller enforces the cardinal rule:
  THE SCALE IS THE SOLE AUTHORITY FOR WEIGHT AND PRICE.
  The POS only selects products; the hub only routes.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from .adapters.cas_erplus import CasErPlusAdapter, CasProtocolError, SaleFrame
from .adapters.serial_layer import SerialWriter
from .audit_log import AuditLog
from .plu_map import PluMap
from .state_machine import ScaleSessionManager, ScaleState


def _sale_to_dict(sale: SaleFrame) -> dict[str, Any]:
    return {
        "plu": sale.plu,
        "weight_kg": sale.weight_kg,
        "unit_price": sale.unit_price,
        "total_price": sale.total_price,
        "raw_hex": sale.raw.hex() if isinstance(sale.raw, bytes) else str(sale.raw),
    }

logger = logging.getLogger(__name__)


class ScaleController:
    """
    Central controller bridging POS ↔ Hub ↔ Scale.

    Thread-safe: the state machine handles concurrency.
    """

    def __init__(
        self,
        adapter: CasErPlusAdapter,
        writer: SerialWriter,
        session: ScaleSessionManager,
        audit: AuditLog,
        plu_map: PluMap,
        publish_sale: Optional[Callable[[dict[str, Any]], None]] = None,
    ) -> None:
        self.adapter = adapter
        self.writer = writer
        self.session = session
        self.audit = audit
        self.plu_map = plu_map
        self.publish_sale = publish_sale

    # -- POS → Scale ----------------------------------------------------------

    def select_product(self, product_id: str) -> dict[str, Any]:
        """
        POS pressed a product button.
        Resolve to PLU (allowlist), send selection to scale.
        """
        entry = self.plu_map.resolve(product_id)
        self.session.begin_plu_selection(product_id=product_id, plu=entry.plu)

        cmd = self.adapter.build_select_plu_command(entry.plu)
        try:
            self.writer.write(cmd)
        except Exception as exc:
            self.session.fail(str(exc))
            self.audit.append("plu_select_failed", {
                "product_id": product_id,
                "plu": entry.plu,
                "error": str(exc),
            })
            raise

        self.audit.append("plu_selected", {
            "product_id": product_id,
            "plu": entry.plu,
            "name": entry.name,
            "command_hex": cmd.hex(),
        })

        self.session.mark_ready()

        return {
            "ok": True,
            "state": self.session.state.value,
            "product_id": product_id,
            "plu": entry.plu,
            "name": entry.name,
        }

    # -- Scale → POS ----------------------------------------------------------

    def handle_sale_frame(self, raw: bytes) -> None:
        """
        Called by the SerialReader when Port B delivers a completed sale.
        Validates, locks, logs, and forwards to POS.
        """
        try:
            sale = self.adapter.parse_sale_frame(raw)
        except CasProtocolError:
            logger.exception("Cannot parse sale frame")
            self.audit.append("sale_parse_error", {"raw_hex": raw.hex()})
            return

        active = self.session.active
        if self.session.state != ScaleState.READY_TO_WEIGH:
            self.audit.append("unexpected_sale", {
                "state": self.session.state.value,
                "frame": _sale_to_dict(sale),
            })
            return

        if not active:
            self.audit.append("sale_without_session", {"frame": _sale_to_dict(sale)})
            return

        if sale.plu is not None and sale.plu != active.plu:
            self.audit.append("plu_mismatch", {
                "expected": active.plu,
                "received": sale.plu,
                "frame": _sale_to_dict(sale),
            })
            self.session.fail("PLU mismatch")
            return

        self.session.lock_sale()

        payload = {
            "product_id": active.product_id,
            "plu": active.plu,
            "weight_kg": sale.weight_kg,
            "unit_price": sale.unit_price,
            "total_price": sale.total_price,
        }

        self.audit.append("sale_completed", payload)

        if self.publish_sale:
            try:
                self.publish_sale(payload)
            except Exception:
                logger.exception("Failed to publish sale to POS")

        self.session.finalize()

    # -- PLU Upload (Odoo → Scale config) -------------------------------------

    def upload_plu(
        self,
        plu: int,
        name: str,
        unit_price: float,
        gtin: Optional[str] = None,
    ) -> dict[str, Any]:
        """Upload/update a single PLU on the scale (configuration mode)."""
        cmd = self.adapter.build_plu_upload_command(
            plu=plu, name=name, unit_price=unit_price, gtin=gtin,
        )
        self.writer.write(cmd)

        entry = self.audit.append("plu_uploaded", {
            "plu": plu,
            "name": name,
            "unit_price": unit_price,
            "gtin": gtin,
            "command_hex": cmd.hex(),
        })
        return {"ok": True, "plu": plu, "audit_hash": entry["entry_hash"]}
