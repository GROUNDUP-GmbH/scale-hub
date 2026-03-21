"""Label profiles for scenario-based labeling (LMIV-compliant).

Each LabelScenario maps to a LabelProfile that defines:
- Label dimensions (width_mm x height_mm)
- Which fields are mandatory / optional
- ZPL layout parameters
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LabelScenario(str, Enum):
    """Sales scenarios per LMIV / compliance.yaml."""

    LOOSE = "loose"
    SIMPLE_PREPACK = "simple_prepack"
    FULL_PREPACK = "full_prepack"
    LEH_PREPACK = "leh_prepack"


@dataclass(frozen=True)
class NutritionData:
    """Big Seven per 100g/100ml (LMIV Art. 30, Anhang XIII)."""

    energy_kj: float
    energy_kcal: float
    fat: float
    saturated_fat: float
    carbohydrates: float
    sugars: float
    protein: float
    salt: float


@dataclass(frozen=True)
class LabelProfile:
    """Defines the physical and logical layout for a label scenario."""

    scenario: LabelScenario
    width_mm: int
    height_mm: int
    mandatory_fields: tuple[str, ...]
    optional_fields: tuple[str, ...] = ()
    has_nutrition_table: bool = False
    has_ean_barcode: bool = False
    has_qr_code: bool = True
    dpi: int = 203


PROFILES: dict[LabelScenario, LabelProfile] = {
    LabelScenario.LOOSE: LabelProfile(
        scenario=LabelScenario.LOOSE,
        width_mm=60,
        height_mm=40,
        mandatory_fields=(),
        optional_fields=("product_name", "operator_name"),
        has_qr_code=False,
    ),
    LabelScenario.SIMPLE_PREPACK: LabelProfile(
        scenario=LabelScenario.SIMPLE_PREPACK,
        width_mm=60,
        height_mm=40,
        mandatory_fields=(
            "product_name",
            "net_weight",
            "unit_price",
            "total_price",
            "best_before_date",
            "operator_name",
            "operator_address",
            "origin",
            "lot_number",
        ),
        optional_fields=("storage_instructions",),
    ),
    LabelScenario.FULL_PREPACK: LabelProfile(
        scenario=LabelScenario.FULL_PREPACK,
        width_mm=80,
        height_mm=60,
        mandatory_fields=(
            "product_name",
            "ingredients",
            "allergens",
            "net_weight",
            "unit_price",
            "total_price",
            "best_before_date",
            "operator_name",
            "operator_address",
            "origin",
            "lot_number",
            "storage_instructions",
        ),
    ),
    LabelScenario.LEH_PREPACK: LabelProfile(
        scenario=LabelScenario.LEH_PREPACK,
        width_mm=100,
        height_mm=70,
        mandatory_fields=(
            "product_name",
            "ingredients",
            "allergens",
            "net_weight",
            "unit_price",
            "total_price",
            "best_before_date",
            "operator_name",
            "operator_address",
            "origin",
            "lot_number",
            "storage_instructions",
            "nutrition",
            "gtin",
        ),
        has_nutrition_table=True,
        has_ean_barcode=True,
        has_qr_code=True,
    ),
}


@dataclass
class LabelData:
    """All possible data fields for label generation."""

    scenario: LabelScenario
    product_name: str = ""
    net_weight: float = 0.0
    unit_price: float = 0.0
    total_price: float = 0.0
    best_before_date: Optional[str] = None
    operator_name: Optional[str] = None
    operator_address: Optional[str] = None
    origin: Optional[str] = None
    lot_number: Optional[str] = None
    ingredients: Optional[str] = None
    allergens: Optional[str] = None
    storage_instructions: Optional[str] = None
    nutrition: Optional[NutritionData] = None
    gtin: Optional[str] = None
    digital_link: Optional[str] = None
    currency: str = "EUR"


def get_profile(scenario: LabelScenario) -> LabelProfile:
    """Return the LabelProfile for a given scenario."""
    return PROFILES[scenario]


def validate_label_data(data: LabelData) -> list[str]:
    """Validate that all mandatory fields for the scenario are present.

    Returns a list of missing field names (empty = valid).
    """
    profile = get_profile(data.scenario)
    missing: list[str] = []

    for field_name in profile.mandatory_fields:
        value = getattr(data, field_name, None)
        if value is None or value == "" or value == 0.0:
            if field_name in ("unit_price", "total_price") and value == 0.0:
                continue
            missing.append(field_name)

    return missing
