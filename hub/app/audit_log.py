"""
GroundUp Scale Hub – Append-Only Hash-Chained Audit Log

Every event (PLU selection, sale ingest, label render, config change)
is written as a JSONL line with a SHA-256 hash chain.  The log is
designed to be tamper-evident: altering any entry breaks the chain.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


class AuditLog:
    """Append-only, hash-chained JSONL audit log."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._prev_hash = self._read_last_hash()

    # -- public ---------------------------------------------------------------

    def append(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            entry: dict[str, Any] = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "event": event_type,
                "payload": payload,
                "prev_hash": self._prev_hash,
            }
            canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
            entry_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            entry["entry_hash"] = entry_hash
            self._prev_hash = entry_hash

            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

            return entry

    def verify_chain(self) -> tuple[bool, int]:
        """Walk the log and verify every hash link. Returns (ok, line_count)."""
        if not self._path.exists():
            return True, 0
        prev = "0" * 64
        count = 0
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if record["prev_hash"] != prev:
                    return False, count
                stored_hash = record.pop("entry_hash")
                canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
                computed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
                if computed != stored_hash:
                    return False, count
                prev = stored_hash
                record["entry_hash"] = stored_hash
                count += 1
        return True, count

    # -- private --------------------------------------------------------------

    def _read_last_hash(self) -> str:
        if not self._path.exists():
            return "0" * 64
        try:
            with self._path.open("rb") as fh:
                try:
                    fh.seek(-8192, os.SEEK_END)
                except OSError:
                    fh.seek(0)
                lines = fh.readlines()
            if not lines:
                return "0" * 64
            last = json.loads(lines[-1].decode("utf-8"))
            return str(last["entry_hash"])
        except (json.JSONDecodeError, KeyError):
            return "0" * 64
