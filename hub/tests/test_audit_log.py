"""Tests for the append-only hash-chained audit log."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.audit_log import AuditLog


@pytest.fixture
def log_path(tmp_path: Path) -> Path:
    return tmp_path / "audit.jsonl"


def test_append_and_verify(log_path: Path):
    log = AuditLog(log_path)
    log.append("test_event", {"key": "value"})
    log.append("second_event", {"num": 42})

    ok, count = log.verify_chain()
    assert ok is True
    assert count == 2


def test_chain_detects_tampering(log_path: Path):
    log = AuditLog(log_path)
    log.append("event_1", {"a": 1})
    log.append("event_2", {"b": 2})

    lines = log_path.read_text().strip().split("\n")
    record = json.loads(lines[0])
    record["payload"]["a"] = 999
    lines[0] = json.dumps(record)
    log_path.write_text("\n".join(lines) + "\n")

    ok, _ = log.verify_chain()
    assert ok is False


def test_empty_log_verifies(log_path: Path):
    log = AuditLog(log_path)
    ok, count = log.verify_chain()
    assert ok is True
    assert count == 0


def test_entries_contain_hash_fields(log_path: Path):
    log = AuditLog(log_path)
    entry = log.append("test", {"x": 1})
    assert "entry_hash" in entry
    assert "prev_hash" in entry
    assert len(entry["entry_hash"]) == 64
