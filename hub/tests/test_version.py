"""Tests for hub.core.version — software identification."""
from hub.core.version import VERSION, CORE_SHA256, compute_core_checksum, get_identification


class TestVersion:
    def test_version_format(self):
        parts = VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_checksum_deterministic(self):
        h1 = compute_core_checksum()
        h2 = compute_core_checksum()
        assert h1 == h2
        assert h1 == CORE_SHA256

    def test_checksum_is_sha256(self):
        assert len(CORE_SHA256) == 64
        int(CORE_SHA256, 16)  # must be valid hex

    def test_identification_fields(self):
        ident = get_identification()
        assert ident["product"] == "GroundUp Scale Hub"
        assert ident["manufacturer"] == "Ground UP GmbH"
        assert "version" in ident
        assert "core_sha256" in ident
        assert "core_files" in ident
        assert "version.py" in ident["core_files"]
