"""Scale adapter protocol — interface for all scale families (Decision 12).

Every adapter must implement this Protocol. The Certified Core only
depends on this interface, never on a concrete adapter.
"""
from __future__ import annotations

from typing import Optional, Protocol

from hub.core.types import SaleData


class ScaleAdapter(Protocol):
    """Protocol that every scale adapter must implement."""

    @property
    def name(self) -> str:
        """Human-readable adapter name (e.g. 'CAS ER-Plus')."""
        ...

    @property
    def tier(self) -> int:
        """Scale tier: 0, 1, 2, or 3 (2+ encoded as 3)."""
        ...

    def parse_sale_frame(self, raw: bytes) -> SaleData:
        """Parse a raw serial frame into a SaleData record.

        Must convert all values to integer grams and cents.
        Raises ValueError on malformed data.
        """
        ...

    def build_select_command(self, plu: int) -> Optional[bytes]:
        """Build a PLU-select command (Tier 1 only). Returns None if unsupported."""
        ...

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
    ) -> Optional[bytes]:
        """Build a PLU upload command (Tier 1 only). Returns None if unsupported."""
        ...
