"""Tests for hub.core.sealed_config — HMAC-protected parameter store."""
import json
import pytest
from hub.core.sealed_config import ConfigStore, SealedConfig, SecurityError
from hub.core.types import PluRecord


class TestSealedConfig:
    def test_roundtrip(self):
        cfg = SealedConfig(tier=2, scale_port="/dev/ttyUSB0", country_code="AT")
        d = cfg.to_dict()
        cfg2 = SealedConfig.from_dict(d)
        assert cfg2.tier == 2
        assert cfg2.country_code == "AT"

    def test_with_plu_records(self):
        records = [PluRecord(plu=1, product_id="h1", name="Honig", price_cents_per_kg=2490)]
        cfg = SealedConfig(plu_records=records)
        d = cfg.to_dict()
        cfg2 = SealedConfig.from_dict(d)
        assert len(cfg2.plu_records) == 1
        assert cfg2.plu_records[0].name == "Honig"

    def test_resolve_plu(self):
        records = [
            PluRecord(plu=1, product_id="h1", name="Honig", price_cents_per_kg=2490),
            PluRecord(plu=2, product_id="c1", name="Käse", price_cents_per_kg=3500),
        ]
        cfg = SealedConfig(plu_records=records)
        assert cfg.resolve_plu("h1") is not None
        assert cfg.resolve_plu("h1").name == "Honig"
        assert cfg.resolve_plu("unknown") is None


class TestConfigStore:
    def test_save_and_load(self, tmp_path):
        store = ConfigStore(tmp_path / "config.json", "test-key-123")
        cfg = SealedConfig(tier=0, scale_adapter="cas_er", country_code="HU")
        store.save(cfg)
        loaded = store.load()
        assert loaded.tier == 0
        assert loaded.country_code == "HU"

    def test_tamper_detection(self, tmp_path):
        path = tmp_path / "config.json"
        store = ConfigStore(path, "test-key-123")
        store.save(SealedConfig())

        data = json.loads(path.read_text())
        data["config"]["tier"] = 0  # tamper
        path.write_text(json.dumps(data))

        with pytest.raises(SecurityError, match="HMAC verification failed"):
            store.load()

    def test_wrong_key_rejected(self, tmp_path):
        path = tmp_path / "config.json"
        store1 = ConfigStore(path, "key-A")
        store1.save(SealedConfig())

        store2 = ConfigStore(path, "key-B")
        with pytest.raises(SecurityError):
            store2.load()

    def test_missing_file(self, tmp_path):
        store = ConfigStore(tmp_path / "nonexistent.json", "key")
        with pytest.raises(FileNotFoundError):
            store.load()
        assert not store.exists()
