"""Software identification (REQ-SW-01, Decision 07).

Every legally relevant change produces a new version and checksum.
The checksum is computed over all files in hub/core/ at build time
and embedded as a constant. At runtime, the Hub can recompute and
compare to detect tampering.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

VERSION = "0.2.0"
BUILD_DATE = "2026-03-22"

_CORE_PACKAGE_DIR = Path(__file__).parent


def compute_core_checksum() -> str:
    """Compute SHA-256 over all .py files in hub/core/ (sorted, deterministic)."""
    h = hashlib.sha256()
    py_files = sorted(_CORE_PACKAGE_DIR.glob("*.py"))
    for f in py_files:
        h.update(f.read_bytes())
    return h.hexdigest()


CORE_SHA256 = compute_core_checksum()


def get_identification() -> dict:
    """Return the software identification as required by WELMEC 7.2 §4.1."""
    return {
        "product": "GroundUp Scale Hub",
        "manufacturer": "Ground UP GmbH",
        "version": VERSION,
        "build_date": BUILD_DATE,
        "core_sha256": CORE_SHA256,
        "core_files": sorted(f.name for f in _CORE_PACKAGE_DIR.glob("*.py")),
    }
