"""
GroundUp Scale Hub – CAS ER-Plus RS-232 Adapter

Handles bidirectional communication with CAS ER-Plus via RS-232.
The ER-Plus uses the RS232 x2 Comms Module:
  - Port A (Full Duplex): PLU selection, configuration
  - Port B (Transmit Only): completed sale data from scale

IMPORTANT: The exact binary protocol depends on the specific ER-Plus
firmware version. This adapter uses documented CAS ECR/OPOS frame
structures. Finalize with real serial captures from your device.

Frame format (CAS ECR protocol, documented):
  STX (0x02) + data fields + ETX (0x03)

Data elements per CAS ECR/OPOS documentation:
  - Weight (6 bytes, implied 3 decimals)
  - Unit Price (7 bytes, implied 2 decimals)
  - Total Price (8 bytes, implied 2 decimals)
  - PLU number (variable)
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Optional

STX = 0x02
ETX = 0x03


@dataclass(slots=True, frozen=True)
class SaleFrame:
    plu: Optional[int]
    weight_kg: float
    unit_price: float
    total_price: float
    raw: bytes


class CasProtocolError(Exception):
    pass


class CasErPlusAdapter:
    """
    Parse incoming sale frames (Port B, TX-only from scale)
    and build outgoing PLU-select commands (Port A, Full Duplex).
    """

    # -- incoming: parse sale data from scale ---------------------------------

    def parse_sale_frame(self, raw: bytes) -> SaleFrame:
        """
        Parse a CAS ECR-style frame.

        Expected wire format (ASCII between STX/ETX):
            PLU=nnn;W=d.ddd;UP=d.dd;TP=d.dd

        This is the development/capture format. Replace with your
        device's actual frame structure after serial capture.
        """
        text = raw.decode("ascii", errors="replace")
        text = text.replace(chr(STX), "").replace(chr(ETX), "").strip()

        fields: dict[str, str] = {}
        for segment in text.split(";"):
            if "=" in segment:
                key, val = segment.split("=", 1)
                fields[key.strip().upper()] = val.strip()

        try:
            weight = float(fields["W"])
            unit_price = float(fields["UP"])
            total_price = float(fields["TP"])
        except (KeyError, ValueError) as exc:
            raise CasProtocolError(f"Malformed sale frame: {text!r}") from exc

        plu = int(fields["PLU"]) if fields.get("PLU") else None

        return SaleFrame(
            plu=plu,
            weight_kg=weight,
            unit_price=unit_price,
            total_price=total_price,
            raw=raw,
        )

    # -- outgoing: send PLU selection to scale --------------------------------

    def build_select_plu_command(self, plu: int) -> bytes:
        """
        Build a PLU-select command for Port A.

        Per CAS documentation the ER-Plus accepts PLU recall commands
        over RS-232 in ECR mode. The exact encoding depends on firmware;
        this uses the commonly documented ASCII envelope.
        """
        if plu <= 0 or plu > 99999:
            raise CasProtocolError(f"PLU must be 1–99999, got {plu}")
        payload = f"PLU={plu:05d}"
        return bytes([STX]) + payload.encode("ascii") + bytes([ETX])

    def build_plu_upload_command(
        self,
        plu: int,
        name: str,
        unit_price: float,
        gtin: Optional[str] = None,
    ) -> bytes:
        """
        Build a PLU data upload frame for Port A (configuration mode).
        Used for syncing PLU prices from Odoo → scale.
        """
        if plu <= 0 or plu > 99999:
            raise CasProtocolError(f"PLU must be 1–99999, got {plu}")
        name_truncated = name[:28]
        parts = [f"PLU={plu:05d}", f"NAME={name_truncated}", f"UP={unit_price:.2f}"]
        if gtin:
            parts.append(f"GTIN={gtin}")
        payload = ";".join(parts)
        return bytes([STX]) + payload.encode("ascii") + bytes([ETX])
