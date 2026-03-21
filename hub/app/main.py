"""
GroundUp Scale Hub – FastAPI Application

HTTP API for:
  - /scale/select-product  (POS → PLU selection on scale)
  - /scale/status          (current state machine state)
  - /scale/reset           (emergency reset)
  - /plu/update            (Odoo → upload PLU to scale)
  - /plu/list              (list current allowlist)
  - /label/zpl             (generate ZPL label with GS1 Digital Link)
  - /audit/verify          (verify hash chain integrity)
  - /health                (liveness check)
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .adapters.cas_erplus import CasErPlusAdapter
from .adapters.serial_layer import (
    MockSerialReader,
    MockSerialWriter,
    SerialReader,
    SerialWriter,
)
from .audit_log import AuditLog
from .controller import ScaleController
from .plu_map import PluMap
from .state_machine import ScaleSessionManager
from .utils.gs1 import build_digital_link
from .utils.hmac_auth import verify_signature
from .utils.label_profiles import (
    LabelData,
    LabelScenario,
    NutritionData,
    get_profile,
    validate_label_data,
)
from .utils.zpl import build_zpl_label

logger = logging.getLogger(__name__)

# -- Configuration ------------------------------------------------------------

DATA_DIR = Path(os.getenv("GROUNDUP_DATA_DIR", "/tmp/groundup_hub"))
HMAC_SECRET = os.getenv("GROUNDUP_HMAC_SECRET", "dev-secret-change-me")
PORT_A = os.getenv("GROUNDUP_PORT_A", "/dev/ttyUSB0")
PORT_B = os.getenv("GROUNDUP_PORT_B", "/dev/ttyUSB1")
BAUDRATE = int(os.getenv("GROUNDUP_BAUDRATE", "9600"))
USE_MOCK = os.getenv("GROUNDUP_MOCK_SERIAL", "1") == "1"
PLU_MAP_FILE = os.getenv("GROUNDUP_PLU_MAP", str(DATA_DIR / "plu_map.json"))
GS1_BASE_URL = os.getenv("GROUNDUP_GS1_BASE_URL", "https://groundup.bio")

# -- Shared instances ---------------------------------------------------------

audit = AuditLog(DATA_DIR / "audit_log.jsonl")
session = ScaleSessionManager()
plu_map = PluMap()
adapter = CasErPlusAdapter()

writer: SerialWriter
reader: SerialReader
controller: ScaleController


def _init_serial() -> tuple[SerialWriter, SerialReader]:
    if USE_MOCK:
        logger.info("Using MOCK serial ports (no hardware)")
        w = MockSerialWriter()
        r = MockSerialReader(on_frame=_on_sale_frame)
    else:
        w = SerialWriter(port=PORT_A, baudrate=BAUDRATE)
        r = SerialReader(port=PORT_B, baudrate=BAUDRATE, on_frame=_on_sale_frame)
    return w, r


def _on_sale_frame(raw: bytes) -> None:
    controller.handle_sale_frame(raw)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    global writer, reader, controller

    writer, reader = _init_serial()
    writer.open()
    reader.open()

    controller = ScaleController(
        adapter=adapter,
        writer=writer,
        session=session,
        audit=audit,
        plu_map=plu_map,
    )

    plu_path = Path(PLU_MAP_FILE)
    if plu_path.exists():
        count = plu_map.load_from_file(plu_path)
        logger.info("Loaded %d PLU entries from %s", count, plu_path)
    else:
        logger.warning("No PLU map at %s – starting with empty allowlist", plu_path)

    reader.start()
    audit.append("hub_started", {"mock": USE_MOCK, "port_a": PORT_A, "port_b": PORT_B})
    logger.info("GroundUp Scale Hub started")

    yield

    reader.close()
    writer.close()
    audit.append("hub_stopped", {})
    logger.info("GroundUp Scale Hub stopped")


app = FastAPI(
    title="GroundUp Scale Hub",
    description="Mobile scale bridge for CAS ER-Plus ↔ Odoo POS",
    version="0.1.0",
    lifespan=lifespan,
)


# -- Request / Response models -----------------------------------------------


class ProductSelectRequest(BaseModel):
    product_id: str


class PluUpdateRequest(BaseModel):
    plu: int = Field(gt=0, le=99999)
    name: str = Field(max_length=28)
    unit_price: float = Field(ge=0)
    gtin: Optional[str] = None


class PluBulkUpdateRequest(BaseModel):
    items: list[PluUpdateRequest]


class NutritionRequest(BaseModel):
    """Big Seven nutrition values per 100g/100ml (LMIV Art. 30)."""
    energy_kj: float = Field(ge=0)
    energy_kcal: float = Field(ge=0)
    fat: float = Field(ge=0)
    saturated_fat: float = Field(ge=0)
    carbohydrates: float = Field(ge=0)
    sugars: float = Field(ge=0)
    protein: float = Field(ge=0)
    salt: float = Field(ge=0)


class LabelRequest(BaseModel):
    """Request body for label generation — LMIV-compliant."""
    scenario: str = "simple_prepack"
    product_name: str
    gtin: Optional[str] = None
    weight_kg: float = Field(gt=0)
    unit_price: float = Field(ge=0)
    total_price: float = Field(ge=0)
    lot: Optional[str] = None
    expiry: Optional[str] = None
    currency: str = "EUR"
    # LMIV extensions
    origin: Optional[str] = None
    allergens: Optional[str] = None
    ingredients: Optional[str] = None
    operator_name: Optional[str] = None
    operator_address: Optional[str] = None
    shelf_life_days: Optional[int] = None
    storage_instructions: Optional[str] = None
    nutrition: Optional[NutritionRequest] = None
    country_code: str = "AT"


# -- Auth helper --------------------------------------------------------------


def _require_signature(body: bytes, sig: Optional[str]) -> None:
    if HMAC_SECRET == "dev-secret-change-me":
        return  # skip auth in dev mode
    if not sig:
        raise HTTPException(401, "Missing X-GroundUp-Signature header")
    if not verify_signature(HMAC_SECRET, body, sig):
        raise HTTPException(401, "Invalid signature")


# -- Endpoints ----------------------------------------------------------------


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "groundup-scale-hub"}


@app.get("/scale/status")
def scale_status() -> dict:
    return controller.session.snapshot()


@app.post("/scale/select-product")
async def select_product(req: ProductSelectRequest) -> dict:
    try:
        return controller.select_product(req.product_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except RuntimeError as exc:
        raise HTTPException(409, str(exc))


@app.post("/scale/reset")
def scale_reset() -> dict:
    controller.session.reset()
    audit.append("manual_reset", {})
    return {"ok": True, "state": "IDLE"}


@app.post("/plu/update")
async def plu_update(req: PluUpdateRequest) -> dict:
    try:
        return controller.upload_plu(
            plu=req.plu, name=req.name, unit_price=req.unit_price, gtin=req.gtin,
        )
    except Exception as exc:
        raise HTTPException(500, str(exc))


@app.post("/plu/bulk-update")
async def plu_bulk_update(req: PluBulkUpdateRequest) -> dict:
    results = []
    for item in req.items:
        try:
            r = controller.upload_plu(
                plu=item.plu, name=item.name, unit_price=item.unit_price, gtin=item.gtin,
            )
            results.append(r)
        except Exception as exc:
            results.append({"ok": False, "plu": item.plu, "error": str(exc)})
    return {"ok": True, "results": results}


@app.get("/plu/list")
def plu_list() -> dict:
    return {"ok": True, "products": plu_map.list_all()}


@app.post("/label/zpl")
async def make_label(req: LabelRequest) -> dict:
    try:
        scenario = LabelScenario(req.scenario)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=[f"invalid scenario: {req.scenario!r}"],
        )

    nutrition = (
        NutritionData(**req.nutrition.model_dump()) if req.nutrition is not None else None
    )
    label_data = LabelData(
        scenario=scenario,
        product_name=req.product_name,
        net_weight=req.weight_kg,
        unit_price=req.unit_price,
        total_price=req.total_price,
        best_before_date=req.expiry,
        operator_name=req.operator_name,
        operator_address=req.operator_address,
        origin=req.origin,
        lot_number=req.lot,
        ingredients=req.ingredients,
        allergens=req.allergens,
        storage_instructions=req.storage_instructions,
        nutrition=nutrition,
        gtin=req.gtin,
        currency=req.currency,
    )
    missing = validate_label_data(label_data)
    if missing:
        raise HTTPException(status_code=422, detail=missing)

    link = build_digital_link(
        base_url=GS1_BASE_URL,
        gtin=req.gtin or "",
        weight_kg=req.weight_kg,
        lot=req.lot,
        expiry=req.expiry,
    )
    zpl = build_zpl_label(
        product_name=req.product_name,
        weight_kg=req.weight_kg,
        unit_price=req.unit_price,
        total_price=req.total_price,
        digital_link=link,
        gtin=req.gtin,
        lot=req.lot,
        expiry=req.expiry,
        currency=req.currency,
    )
    audit.append("label_generated", {"gtin": req.gtin, "link": link})
    return {"ok": True, "digital_link": link, "zpl": zpl}


@app.get("/audit/verify")
def audit_verify() -> dict:
    ok, count = audit.verify_chain()
    return {"ok": ok, "entries": count}
