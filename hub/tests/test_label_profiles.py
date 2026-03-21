"""Tests for label_profiles — scenario-based labeling."""

import pytest

from app.utils.label_profiles import (
    LabelData,
    LabelScenario,
    NutritionData,
    PROFILES,
    get_profile,
    validate_label_data,
)


class TestLabelScenario:
    def test_enum_values(self):
        assert LabelScenario.LOOSE == "loose"
        assert LabelScenario.SIMPLE_PREPACK == "simple_prepack"
        assert LabelScenario.FULL_PREPACK == "full_prepack"
        assert LabelScenario.LEH_PREPACK == "leh_prepack"

    def test_all_scenarios_have_profiles(self):
        for scenario in LabelScenario:
            assert scenario in PROFILES


class TestLabelProfile:
    def test_loose_no_mandatory_fields(self):
        profile = get_profile(LabelScenario.LOOSE)
        assert profile.mandatory_fields == ()
        assert profile.has_qr_code is False

    def test_simple_prepack_dimensions(self):
        profile = get_profile(LabelScenario.SIMPLE_PREPACK)
        assert profile.width_mm == 60
        assert profile.height_mm == 40

    def test_full_prepack_has_allergens(self):
        profile = get_profile(LabelScenario.FULL_PREPACK)
        assert "allergens" in profile.mandatory_fields
        assert "ingredients" in profile.mandatory_fields

    def test_leh_prepack_has_nutrition_and_ean(self):
        profile = get_profile(LabelScenario.LEH_PREPACK)
        assert profile.has_nutrition_table is True
        assert profile.has_ean_barcode is True
        assert profile.has_qr_code is True
        assert "nutrition" in profile.mandatory_fields
        assert "gtin" in profile.mandatory_fields
        assert profile.width_mm == 100
        assert profile.height_mm == 70


class TestValidation:
    def _base_data(self, scenario: LabelScenario, **overrides) -> LabelData:
        defaults = {
            "scenario": scenario,
            "product_name": "Bio-Apfel",
            "net_weight": 1.0,
            "unit_price": 3.50,
            "total_price": 3.50,
            "best_before_date": "2026-04-15",
            "operator_name": "Huber Hof",
            "operator_address": "Dorfstr. 1, 3100 St. Pölten",
            "origin": "Österreich, Niederösterreich",
            "lot_number": "L20260321-001",
            "ingredients": "Äpfel",
            "allergens": "keine",
            "storage_instructions": "Kühl und trocken lagern",
        }
        defaults.update(overrides)
        return LabelData(**defaults)

    def test_loose_always_valid(self):
        data = LabelData(scenario=LabelScenario.LOOSE)
        assert validate_label_data(data) == []

    def test_simple_prepack_valid(self):
        data = self._base_data(LabelScenario.SIMPLE_PREPACK)
        assert validate_label_data(data) == []

    def test_simple_prepack_missing_origin(self):
        data = self._base_data(LabelScenario.SIMPLE_PREPACK, origin=None)
        missing = validate_label_data(data)
        assert "origin" in missing

    def test_full_prepack_valid(self):
        data = self._base_data(LabelScenario.FULL_PREPACK)
        assert validate_label_data(data) == []

    def test_full_prepack_missing_allergens(self):
        data = self._base_data(LabelScenario.FULL_PREPACK, allergens=None)
        missing = validate_label_data(data)
        assert "allergens" in missing

    def test_leh_prepack_missing_nutrition(self):
        data = self._base_data(LabelScenario.LEH_PREPACK, gtin="9012345678901")
        missing = validate_label_data(data)
        assert "nutrition" in missing

    def test_leh_prepack_missing_gtin(self):
        nutrition = NutritionData(
            energy_kj=200, energy_kcal=48, fat=0.1,
            saturated_fat=0.0, carbohydrates=11.0,
            sugars=10.0, protein=0.3, salt=0.0,
        )
        data = self._base_data(
            LabelScenario.LEH_PREPACK, nutrition=nutrition, gtin=None,
        )
        missing = validate_label_data(data)
        assert "gtin" in missing

    def test_leh_prepack_fully_valid(self):
        nutrition = NutritionData(
            energy_kj=200, energy_kcal=48, fat=0.1,
            saturated_fat=0.0, carbohydrates=11.0,
            sugars=10.0, protein=0.3, salt=0.0,
        )
        data = self._base_data(
            LabelScenario.LEH_PREPACK,
            nutrition=nutrition,
            gtin="9012345678901",
        )
        assert validate_label_data(data) == []


class TestNutritionData:
    def test_big_seven_fields(self):
        nd = NutritionData(
            energy_kj=200.0, energy_kcal=48.0, fat=0.1,
            saturated_fat=0.0, carbohydrates=11.0,
            sugars=10.0, protein=0.3, salt=0.01,
        )
        assert nd.energy_kj == 200.0
        assert nd.salt == 0.01

    def test_frozen(self):
        nd = NutritionData(
            energy_kj=200.0, energy_kcal=48.0, fat=0.1,
            saturated_fat=0.0, carbohydrates=11.0,
            sugars=10.0, protein=0.3, salt=0.01,
        )
        with pytest.raises(AttributeError):
            nd.energy_kj = 999.0
