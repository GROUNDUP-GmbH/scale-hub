"""Hash-chained append-only audit log (REQ-SW-04, Decision 04).

Every metrologically relevant event is recorded as a JSONL line with
SHA-256 hash chain. The log is tamper-evident: altering any entry
breaks the chain.

Event types (WELMEC 7.2 §4.5):
  - hub_started / hub_stopped
  - sale_completed / sale_rejected
  - parameter_changed
  - software_updated / update_failed
  - plu_selected / plu_uploaded
  - error
  - verification_requested
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


_GENESIS_HASH = "0" * 64


class AuditLog:
    """Append-only, hash-chained JSONL audit log."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._counter = 0
        self._prev_hash = self._recover_state()

    def append(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Append an event. Returns the full entry including hash.

        Uses fsync() to ensure durability even on power loss (REQ-SW-07).
        """
        with self._lock:
            self._counter += 1
            entry: dict[str, Any] = {
                "seq": self._counter,
                "ts": datetime.now(timezone.utc).isoformat(),
                "event": event_type,
                "payload": payload,
                "prev_hash": self._prev_hash,
            }
            canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
            entry_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            entry["entry_hash"] = entry_hash
            self._prev_hash = entry_hash

            fd = os.open(str(self._path), os.O_WRONLY | os.O_CREAT | os.O_APPEND)
            try:
                line = json.dumps(entry, ensure_ascii=False) + "\n"
                os.write(fd, line.encode("utf-8"))
                os.fsync(fd)
            finally:
                os.close(fd)

            return entry

    def verify_chain(self) -> tuple[bool, int]:
        """Walk the entire log and verify every hash link."""
        if not self._path.exists():
            return True, 0
        prev = _GENESIS_HASH
        count = 0
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if record.get("prev_hash") != prev:
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

    @property
    def entry_count(self) -> int:
        return self._counter

    @property
    def last_hash(self) -> str:
        return self._prev_hash

    def _recover_state(self) -> str:
        """Recover counter and last hash from existing log file."""
        if not self._path.exists():
            return _GENESIS_HASH
        try:
            with self._path.open("rb") as fh:
                try:
                    fh.seek(-16384, os.SEEK_END)
                except OSError:
                    fh.seek(0)
                lines = fh.readlines()
            if not lines:
                return _GENESIS_HASH
            last = json.loads(lines[-1].decode("utf-8"))
            self._counter = last.get("seq", 0)
            return str(last["entry_hash"])
        except (json.JSONDecodeError, KeyError):
            return _GENESIS_HASH
