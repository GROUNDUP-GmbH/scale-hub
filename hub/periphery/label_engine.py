"""Label generation engine — ZPL II for Zebra printers.

Non-legally-relevant: label content is derived from SaleData
(produced by the Certified Core) but the label layout itself
is not metrologically relevant.

Supports four scenarios per Decision 09:
  - LOOSE: no label
  - SIMPLE_PREPACK: 60x40mm basic
  - FULL_PREPACK: 80x60mm with ingredients/allergens
  - LEH_PREPACK: 100x70mm with nutrition + EAN-13
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LabelScenario(str, Enum):
    LOOSE = "loose"
    SIMPLE_PREPACK = "simple_prepack"
    FULL_PREPACK = "full_prepack"
    LEH_PREPACK = "leh_prepack"


@dataclass(frozen=True)
class NutritionData:
    """Big Seven per 100g/100ml (LMIV Art. 30)."""
    energy_kj: float
    energy_kcal: float
    fat: float
    saturated_fat: float
    carbohydrates: float
    sugars: float
    protein: float
    salt: float


@dataclass
class LabelRequest:
    """All data needed to generate a label."""
    scenario: LabelScenario
    product_name: str
    weight_g: int
    price_cents_per_kg: int
    total_cents: int
    currency: str = "EUR"
    gtin: Optional[str] = None
    lot: Optional[str] = None
    expiry: Optional[str] = None
    origin: Optional[str] = None
    operator_name: Optional[str] = None
    operator_address: Optional[str] = None
    ingredients: Optional[str] = None
    allergens: Optional[str] = None
    storage_instructions: Optional[str] = None
    nutrition: Optional[NutritionData] = None
    digital_link: Optional[str] = None
    consistency_hash: Optional[str] = None


def generate_zpl(req: LabelRequest) -> str:
    """Generate ZPL II commands for a Zebra label printer."""
    if req.scenario == LabelScenario.LOOSE:
        return ""

    weight_kg = req.weight_g / 1000
    unit_price = req.price_cents_per_kg / 100
    total_price = req.total_cents / 100
    cur = req.currency

    zpl = f"""^XA
^CI28
^CF0,28
^FO30,20^FD{req.product_name[:30]}^FS
^CF0,22
^FO30,60^FDGewicht: {weight_kg:.3f} kg^FS
^FO30,90^FDPreis/kg: {unit_price:.2f} {cur}^FS
^CF0,30
^FO30,125^FDGesamt: {total_price:.2f} {cur}^FS
^CF0,18"""

    if req.origin:
        zpl += f"\n^FO30,165^FDHerkunft: {req.origin}^FS"

    y = 190
    if req.ingredients:
        zpl += f"\n^FO30,{y}^FDZutaten: {req.ingredients[:60]}^FS"
        y += 25
    if req.allergens:
        zpl += f"\n^FO30,{y}^FDAllergene: {req.allergens[:50]}^FS"
        y += 25
    if req.expiry:
        zpl += f"\n^FO30,{y}^FDMHD: {req.expiry}^FS"
        y += 25
    if req.lot:
        zpl += f"\n^FO30,{y}^FDCharge: {req.lot}^FS"
        y += 25
    if req.storage_instructions:
        zpl += f"\n^FO30,{y}^FD{req.storage_instructions[:50]}^FS"

    if req.gtin and req.scenario == LabelScenario.LEH_PREPACK:
        zpl += f"\n^FO30,280^BY2^BCN,60,Y,N^FD{req.gtin}^FS"

    if req.digital_link:
        zpl += f"\n^FO300,20^BQN,2,5\n^FDLA,{req.digital_link}^FS"

    zpl += "\n^XZ"
    return zpl


def validate_label_request(req: LabelRequest) -> list[str]:
    """Validate mandatory fields per scenario. Returns missing field names."""
    if req.scenario == LabelScenario.LOOSE:
        return []

    missing: list[str] = []
    always_required = ["product_name", "weight_g", "total_cents"]
    for f in always_required:
        if not getattr(req, f):
            missing.append(f)

    if req.scenario in (LabelScenario.FULL_PREPACK, LabelScenario.LEH_PREPACK):
        if not req.ingredients:
            missing.append("ingredients")
        if not req.allergens:
            missing.append("allergens")

    if req.scenario == LabelScenario.LEH_PREPACK:
        if not req.nutrition:
            missing.append("nutrition")
        if not req.gtin:
            missing.append("gtin")

    return missing
