"""CAS CL adapter — Tier 1 (extended PLU protocol).

Supports CAS CL5000(J), CL-3000, CL-5200, CL-5500, CL-7200.
Extends the CAS LP protocol with departments, groups, and richer PLU fields.

Interface: RS-232 + TCP/IP (both supported)

Additional capabilities over LP protocol:
  - Department CRUD
  - Group CRUD
  - Multiple keyboard sets
  - Extended PLU fields: Department, Product Type, Fixed Weight

Sources:
  - Scale-Soft.com — CAS CL Driver
  - cas-lp.narod.ru — CAS CL5000 universal driver
"""
from __future__ import annotations

import struct
from typing import Optional

from hub.core.types import SaleData
from hub.adapters.cas_lp import (
    CasLpAdapter,
    STX, ETX,
    CMD_PLU_WRITE, CMD_PLU_READ, CMD_PLU_DELETE,
    CMD_STATUS_QUERY,
    PLU_RECORD_SIZE,
    _lrc, _encode_bcd,
)

CL_PLU_RECORD_SIZE = 99

CMD_DEPT_WRITE = 0x44
CMD_DEPT_DELETE = 0x45
CMD_GROUP_WRITE = 0x46
CMD_GROUP_DELETE = 0x47
CMD_KEYBOARD_SET_WRITE = 0x72


class CasClAdapter(CasLpAdapter):
    """Tier 1 adapter for CAS CL series (CL5000, CL-3000, CL-5200, etc.).

    Inherits LP protocol base and extends with department/group management
    and richer PLU record fields.
    """

    @property
    def name(self) -> str:
        return "CAS CL"

    def build_plu_upload(
        self, plu: int, name: str, price_cents_per_kg: int,
        department: int = 1,
        group_code: int = 0,
        product_type: int = 0,
        fixed_weight_g: int = 0,
    ) -> Optional[bytes]:
        """Build an extended PLU write command (99-byte CL record).

        Additional fields beyond LP protocol:
          - department (2 bytes at offset 0x53)
          - product_type (1 byte at offset 0x55)
          - fixed_weight (4 bytes at offset 0x56)
        """
        record = bytearray(CL_PLU_RECORD_SIZE)

        struct.pack_into(">I", record, 0, plu)

        barcode = _encode_bcd(plu, 6)
        record[4:10] = barcode

        name_bytes = name.encode("ascii", errors="replace")[:56]
        record[10 : 10 + len(name_bytes)] = name_bytes

        struct.pack_into(">I", record, 0x42, price_cents_per_kg)

        struct.pack_into(">H", record, 0x4B, group_code)

        struct.pack_into(">H", record, 0x53, department)
        record[0x55] = product_type & 0xFF
        struct.pack_into(">I", record, 0x56, fixed_weight_g)

        payload = bytes([CMD_PLU_WRITE]) + bytes(record)
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_department_upload(self, dept_id: int, name: str) -> bytes:
        """Build a department write command."""
        name_bytes = name.encode("ascii", errors="replace")[:28]
        data = struct.pack(">H", dept_id) + name_bytes.ljust(28, b"\x00")
        payload = bytes([CMD_DEPT_WRITE]) + data
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_department_delete(self, dept_id: int) -> bytes:
        """Build a department delete command."""
        data = struct.pack(">H", dept_id)
        payload = bytes([CMD_DEPT_DELETE]) + data
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_group_upload(self, group_id: int, name: str) -> bytes:
        """Build a group write command."""
        name_bytes = name.encode("ascii", errors="replace")[:28]
        data = struct.pack(">H", group_id) + name_bytes.ljust(28, b"\x00")
        payload = bytes([CMD_GROUP_WRITE]) + data
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_group_delete(self, group_id: int) -> bytes:
        """Build a group delete command."""
        data = struct.pack(">H", group_id)
        payload = bytes([CMD_GROUP_DELETE]) + data
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])

    def build_keyboard_set(self, set_id: int, key_number: int, plu: int) -> bytes:
        """Build a keyboard set assignment command (multiple sets supported)."""
        data = struct.pack(">BBH", set_id, key_number, plu)
        payload = bytes([CMD_KEYBOARD_SET_WRITE]) + data
        lrc = _lrc(payload)
        return bytes([STX]) + payload + bytes([lrc, ETX])
