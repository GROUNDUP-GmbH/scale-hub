"""Sealed parameter store (REQ-SW-03, Decision 07).

Metrologically relevant parameters are stored in a JSON file
protected by HMAC-SHA256. The Hub verifies the signature on
every start — boot fails on mismatch.

Parameters that are sealed:
  - PLU price map (product_id -> price_cents_per_kg)
  - Scale adapter configuration (port, baudrate, protocol)
  - Hub operating mode (tier)
"""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .types import PluRecord


@dataclass
class SealedConfig:
    """Configuration with HMAC integrity protection."""

    tier: int = 2
    scale_port: str = "/dev/ttyUSB0"
    scale_baudrate: int = 9600
    scale_bytesize: int = 8
    scale_parity: str = "N"
    scale_stopbits: int = 1
    scale_adapter: str = "cas_er"
    country_code: str = "AT"
    plu_records: list[PluRecord] = field(default_factory=list)
    event_counter: int = 0

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "tier": self.tier,
            "scale_port": self.scale_port,
            "scale_baudrate": self.scale_baudrate,
            "scale_bytesize": self.scale_bytesize,
            "scale_parity": self.scale_parity,
            "scale_stopbits": self.scale_stopbits,
            "scale_adapter": self.scale_adapter,
            "country_code": self.country_code,
            "event_counter": self.event_counter,
            "plu_records": [
                {
                    "plu": r.plu,
                    "product_id": r.product_id,
                    "name": r.name,
                    "price_cents_per_kg": r.price_cents_per_kg,
                    "gtin": r.gtin,
                }
                for r in self.plu_records
            ],
        }
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SealedConfig:
        records = [PluRecord(**r) for r in d.get("plu_records", [])]
        return cls(
            tier=d.get("tier", 2),
            scale_port=d.get("scale_port", "/dev/ttyUSB0"),
            scale_baudrate=d.get("scale_baudrate", 9600),
            scale_bytesize=d.get("scale_bytesize", 8),
            scale_parity=d.get("scale_parity", "N"),
            scale_stopbits=d.get("scale_stopbits", 1),
            scale_adapter=d.get("scale_adapter", "cas_er"),
            country_code=d.get("country_code", "AT"),
            event_counter=d.get("event_counter", 0),
            plu_records=records,
        )

    def resolve_plu(self, product_id: str) -> Optional[PluRecord]:
        for r in self.plu_records:
            if r.product_id == product_id:
                return r
        return None


class ConfigStore:
    """Load/save sealed configuration with HMAC verification."""

    def __init__(self, path: Path | str, hmac_key: str) -> None:
        self._path = Path(path)
        self._key = hmac_key.encode("utf-8")

    def save(self, config: SealedConfig) -> None:
        """Save config with HMAC signature."""
        data = config.to_dict()
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        sig = hmac.new(self._key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
        envelope = {"config": data, "hmac_sha256": sig}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8",
        )

    def load(self) -> SealedConfig:
        """Load and verify sealed config. Raises on tamper detection."""
        if not self._path.exists():
            raise FileNotFoundError(f"Sealed config not found: {self._path}")
        envelope = json.loads(self._path.read_text(encoding="utf-8"))
        data = envelope["config"]
        stored_sig = envelope["hmac_sha256"]
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        expected = hmac.new(
            self._key, canonical.encode("utf-8"), hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(stored_sig, expected):
            raise SecurityError(
                "Sealed config HMAC verification failed — possible tampering"
            )
        return SealedConfig.from_dict(data)

    def exists(self) -> bool:
        return self._path.exists()


class SecurityError(Exception):
    """Raised when sealed config integrity check fails."""
