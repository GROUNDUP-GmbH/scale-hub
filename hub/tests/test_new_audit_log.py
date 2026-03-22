"""Tests for hub.core.audit_log — hash-chained append-only log."""
from hub.core.audit_log import AuditLog


class TestAuditLog:
    def test_append_and_verify(self, tmp_path):
        log = AuditLog(tmp_path / "audit.jsonl")
        log.append("test_event", {"key": "value"})
        log.append("test_event_2", {"num": 42})

        ok, count = log.verify_chain()
        assert ok is True
        assert count == 2

    def test_empty_log_verifies(self, tmp_path):
        log = AuditLog(tmp_path / "audit.jsonl")
        ok, count = log.verify_chain()
        assert ok is True
        assert count == 0

    def test_sequence_numbers(self, tmp_path):
        log = AuditLog(tmp_path / "audit.jsonl")
        e1 = log.append("first", {})
        e2 = log.append("second", {})
        assert e1["seq"] == 1
        assert e2["seq"] == 2

    def test_tamper_detection(self, tmp_path):
        path = tmp_path / "audit.jsonl"
        log = AuditLog(path)
        log.append("event1", {"data": "original"})
        log.append("event2", {"data": "also_original"})

        lines = path.read_text().splitlines()
        lines[0] = lines[0].replace("original", "TAMPERED")
        path.write_text("\n".join(lines) + "\n")

        log2 = AuditLog(path)
        ok, count = log2.verify_chain()
        assert ok is False

    def test_recovery_after_restart(self, tmp_path):
        path = tmp_path / "audit.jsonl"
        log1 = AuditLog(path)
        log1.append("before_restart", {})
        last_hash = log1.last_hash

        log2 = AuditLog(path)
        assert log2.last_hash == last_hash
        log2.append("after_restart", {})

        ok, count = log2.verify_chain()
        assert ok is True
        assert count == 2

    def test_entry_count(self, tmp_path):
        log = AuditLog(tmp_path / "audit.jsonl")
        assert log.entry_count == 0
        log.append("e1", {})
        log.append("e2", {})
        assert log.entry_count == 2
