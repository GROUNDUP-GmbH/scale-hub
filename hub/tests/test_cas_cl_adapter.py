"""Tests for hub.adapters.cas_cl — CAS CL Tier 1 adapter."""
import pytest
from hub.adapters.cas_cl import CasClAdapter, STX, ETX


class TestCasClAdapter:
    def setup_method(self):
        self.adapter = CasClAdapter()

    def test_tier_and_name(self):
        assert self.adapter.tier == 1
        assert self.adapter.name == "CAS CL"

    def test_inherits_lp_parsing(self):
        """CL adapter inherits LP's parse_sale_frame."""
        assert hasattr(self.adapter, "parse_sale_frame")
        assert hasattr(self.adapter, "build_status_query")

    def test_build_plu_upload_extended(self):
        cmd = self.adapter.build_plu_upload(
            plu=100, name="Bio Lammkeule", price_cents_per_kg=2490,
            department=3, group_code=10, product_type=1, fixed_weight_g=500,
        )
        assert cmd is not None
        assert cmd[0] == STX
        assert cmd[-1] == ETX
        assert len(cmd) > 99

    def test_build_department_upload(self):
        cmd = self.adapter.build_department_upload(1, "Fleisch")
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_department_delete(self):
        cmd = self.adapter.build_department_delete(1)
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_group_upload(self):
        cmd = self.adapter.build_group_upload(5, "Bio")
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_group_delete(self):
        cmd = self.adapter.build_group_delete(5)
        assert cmd[0] == STX
        assert cmd[-1] == ETX

    def test_build_keyboard_set(self):
        cmd = self.adapter.build_keyboard_set(set_id=2, key_number=5, plu=100)
        assert cmd[0] == STX
        assert cmd[-1] == ETX
