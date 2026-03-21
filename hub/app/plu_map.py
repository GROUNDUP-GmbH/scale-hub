"""
GroundUp Scale Hub – Allowlist-based PLU Mapping

Maps Odoo product_id → CAS PLU number.
Only products in this map may be sent to the scale.
The map is populated at startup from Odoo and can be refreshed via API.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Optional


@dataclass(frozen=True)
class PluEntry:
    plu: int
    name: str
    unit_price: float
    gtin: Optional[str] = None


class PluMap:
    """Thread-safe, allowlist-only product → PLU mapping."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._map: dict[str, PluEntry] = {}

    def load_from_file(self, path: Path | str) -> int:
        """Load mapping from a JSON file. Returns number of entries loaded."""
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        with self._lock:
            self._map.clear()
            for product_id, entry in data.items():
                self._map[product_id] = PluEntry(**entry)
            return len(self._map)

    def load_from_dict(self, data: dict[str, dict]) -> int:
        with self._lock:
            self._map.clear()
            for product_id, entry in data.items():
                self._map[product_id] = PluEntry(**entry)
            return len(self._map)

    def resolve(self, product_id: str) -> PluEntry:
        with self._lock:
            entry = self._map.get(product_id)
        if entry is None:
            raise ValueError(
                f"Product '{product_id}' not in allowlist. "
                "Only pre-configured products may be sent to the scale."
            )
        return entry

    def list_all(self) -> dict[str, dict]:
        with self._lock:
            return {
                pid: {
                    "plu": e.plu,
                    "name": e.name,
                    "unit_price": e.unit_price,
                    "gtin": e.gtin,
                }
                for pid, e in self._map.items()
            }
