"""Mettler Toledo Tiger adapter — Tier 1 (Premium, RS-232 + Ethernet).

The Tiger protocol is the most feature-rich scale protocol documented.
Supports PLU CRUD, groups, tare tables, tax rates, label formats,
promotional messages, barcode configuration, and special offers.

Wire protocol (from rkeeper s_tiger.dll):
  Weight stream (continuous ASCII):
    STX [space][space][digit].[digit][digit][digit][space]kg ... CR LF
    Example: STX   1.234 kg CR LF → 1.234 kg

  Commands use a text-based request/response protocol with CR LF termination.

Sources:
  - Scale-Soft.com — Mettler Toledo Tiger
  - rkeeper RK7 — s_tiger.dll documentation
"""
from __future__ import annotations

from typing import Optional

from hub.core.types import SaleData

STX = 0x02
CR = 0x0D
LF = 0x0A


class MettlerTigerAdapter:
    """Tier 1 adapter for Mettler Toledo Tiger series (Tiger P/S/L).

    Supports the richest PLU protocol with departments, tax tables,
    tare tables, label formats, and promotional messages.
    """

    @property
    def name(self) -> str:
        return "Mettler Toledo Tiger"

    @property
    def tier(self) -> int:
        return 1

    def parse_sale_frame(self, raw: bytes) -> SaleData:
        """Parse a Mettler Toledo Tiger continuous weight stream frame.

        Frame format: STX [spaces] [weight with decimal] [space] [unit] ... CR LF
        Example: b'\\x02  1.234 kg\\r\\n' → 1234 grams
        """
        text = raw.decode("ascii", errors="replace").strip()
        text = text.lstrip(chr(STX)).rstrip(chr(CR) + chr(LF)).strip()

        parts = text.split()
        if not parts:
            raise ValueError("Empty weight frame")

        weight_str = parts[0]
        unit = parts[1].lower() if len(parts) > 1 else "kg"

        try:
            weight_float = float(weight_str)
        except ValueError:
            raise ValueError(f"Cannot parse weight: '{weight_str}'")

        if unit == "kg":
            weight_g = int(round(weight_float * 1000))
        elif unit == "g":
            weight_g = int(round(weight_float))
        elif unit == "lb":
            weight_g = int(round(weight_float * 453.592))
        else:
            weight_g = int(round(weight_float * 1000))

        return SaleData(
            weight_g=weight_g,
            price_cents_per_kg=0,
            total_cents=0,
            raw_bytes=raw,
        )

    def build_select_command(self, plu: int) -> Optional[bytes]:
        """Build a PLU recall command."""
        return f"PR{plu:06d}\r\n".encode("ascii")

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
    ) -> Optional[bytes]:
        """Build a PLU write command.

        Tiger PLU upload format:
          PW<plu>,<type>,<name>,<price>,<shelf_life>,<sell_by>,<barcode>,
          <group>,<tare_no>,<fixed_weight>,<tax_no>,<msg_no>,<ingredients>,
          <price_change>,<discount>
        """
        fields = [
            f"PW{plu:06d}",
            "0",
            name[:40],
            str(price_cents_per_kg),
            "",
            "",
            "",
            "1",
            "0",
            "0",
            "1",
            "0",
            "",
            "1",
            "1",
        ]
        cmd = ",".join(fields) + "\r\n"
        return cmd.encode("ascii", errors="replace")

    def build_plu_delete(self, plu: int) -> bytes:
        """Build a PLU delete command."""
        return f"PD{plu:06d}\r\n".encode("ascii")

    def build_group_upload(self, group_id: int, name: str) -> bytes:
        """Build a group write command."""
        return f"GW{group_id:04d},{name[:30]}\r\n".encode("ascii", errors="replace")

    def build_group_delete(self, group_id: int) -> bytes:
        """Build a group delete command."""
        return f"GD{group_id:04d}\r\n".encode("ascii")

    def build_tare_upload(self, tare_id: int, weight_g: int) -> bytes:
        """Build a tare table entry command."""
        return f"TW{tare_id:04d},{weight_g}\r\n".encode("ascii")

    def build_tax_upload(self, tax_id: int, rate_permille: int) -> bytes:
        """Build a tax rate table entry command.

        Rate is in permille (1000 = 100.0%, 200 = 20.0%).
        """
        return f"XW{tax_id:02d},{rate_permille}\r\n".encode("ascii")

    def build_datetime_sync(self, year: int, month: int, day: int,
                            hour: int, minute: int, second: int) -> bytes:
        """Build a date/time synchronization command."""
        return f"DT{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}\r\n".encode("ascii")

    def build_store_name(self, name: str) -> bytes:
        """Build a store name write command."""
        return f"SN{name[:40]}\r\n".encode("ascii", errors="replace")

    def build_running_text(self, text: str) -> bytes:
        """Build a promotional running text command."""
        return f"RT{text[:80]}\r\n".encode("ascii", errors="replace")

    def build_label_format(self, format_id: int) -> bytes:
        """Build a label format selection command."""
        return f"LF{format_id:04d}\r\n".encode("ascii")

    def build_keyboard_map(self, key_number: int, plu: int) -> bytes:
        """Build a speed-key assignment command."""
        return f"KW{key_number:03d},{plu:06d}\r\n".encode("ascii")

    def build_special_offer(self, plu: int, offer_price: int,
                            offer_name: str, valid_days: int) -> bytes:
        """Build a special offer command."""
        return (
            f"SO{plu:06d},{offer_price},{offer_name[:30]},{valid_days}\r\n"
            .encode("ascii", errors="replace")
        )

    def build_barcode_format(self, format_code: int) -> bytes:
        """Build a barcode format configuration command."""
        return f"BF{format_code:04d}\r\n".encode("ascii")

    def build_weight_request(self) -> bytes:
        """Build a manual weight request (Tiger normally streams continuously)."""
        return b"W\r\n"
