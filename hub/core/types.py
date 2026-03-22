"""Core data types — used across the Certified Core.

All monetary values are in integer cents, all weights in integer grams.
No floating point anywhere in the metrological data path.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True, slots=True)
class SaleData:
    """Immutable sale record — the canonical output of every scale adapter.

    Integer-only: grams and cents. This eliminates floating-point rounding
    errors and ensures bit-exact consistency across scale, label, and POS
    (REQ-SW-07, Decision 13: Three-Way Consistency).
    """

    weight_g: int
    price_cents_per_kg: int
    total_cents: int
    plu_id: Optional[int] = None
    raw_bytes: bytes = field(default=b"", repr=False)
    tare_g: int = 0

    def __post_init__(self) -> None:
        if self.weight_g < 0:
            raise ValueError(f"Negative weight: {self.weight_g}g")
        if self.total_cents < 0:
            raise ValueError(f"Negative total: {self.total_cents} cents")


@dataclass(frozen=True, slots=True)
class PluRecord:
    """A single PLU entry in the allowlist."""

    plu: int
    product_id: str
    name: str
    price_cents_per_kg: int
    gtin: Optional[str] = None
