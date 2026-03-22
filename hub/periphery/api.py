"""FastAPI application — non-legally-relevant HTTP layer.

This is the Uncertified Periphery's entry point. It imports from
hub.core only via the public data types (SaleData, PluRecord)
and calls the Core's SaleProcessor / AuditLog / StateMachine.

Changes to this file do NOT require re-certification.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from hub.adapters.cas_er import CasErAdapter
from hub.core.audit_log import AuditLog
from hub.core.sale_processor import SaleProcessor
from hub.core.sealed_config import ConfigStore, SealedConfig, SecurityError
from hub.core.serial_port import MockSerialPort, SerialPort
from hub.core.state_machine import StateMachine
from hub.core.types import SaleData
from hub.core.version import get_identification

from .gs1 import build_digital_link
from .label_engine import (
    LabelRequest,
    LabelScenario,
    NutritionData,
    generate_zpl,
    validate_label_request,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("GROUNDUP_DATA_DIR", "/tmp/groundup_hub"))
HMAC_KEY = os.getenv("GROUNDUP_HMAC_KEY", "dev-secret-change-me")
USE_MOCK = os.getenv("GROUNDUP_MOCK_SERIAL", "1") == "1"
GS1_BASE = os.getenv("GROUNDUP_GS1_BASE_URL", "https://groundup.bio")

audit = AuditLog(DATA_DIR / "audit.jsonl")
state = StateMachine()
processor = SaleProcessor(audit=audit, state=state)
config_store = ConfigStore(DATA_DIR / "sealed_config.json", HMAC_KEY)

serial: SerialPort
adapter: CasErAdapter
config: SealedConfig


def _on_frame(raw: bytes) -> None:
    """Callback when the serial reader receives a complete frame."""
    try:
        sale = adapter.parse_sale_frame(raw)
        result = processor.process_sale(sale)
        logger.info("Sale processed: %dg @ %dc/kg = %dc", sale.weight_g, sale.price_cents_per_kg, sale.total_cents)
    except (ValueError, RuntimeError):
        logger.exception("Failed to process sale frame")


@asynccontextmanager
async def lifespan(_app: FastAPI):  # type: ignore[no-untyped-def]
    global serial, adapter, config

    adapter = CasErAdapter()

    if config_store.exists():
        try:
            config = config_store.load()
            logger.info("Sealed config loaded (%d PLU records)", len(config.plu_records))
        except SecurityError:
            logger.critical("SEALED CONFIG TAMPERED — refusing to start")
            raise
    else:
        config = SealedConfig()
        config_store.save(config)
        logger.info("Created default sealed config")

    if USE_MOCK:
        serial = MockSerialPort(on_frame=_on_frame)
    else:
        serial = SerialPort(
            port=config.scale_port,
            baudrate=config.scale_baudrate,
            bytesize=config.scale_bytesize,
            parity=config.scale_parity,
            stopbits=config.scale_stopbits,
            on_frame=_on_frame,
        )

    serial.open()
    serial.start_reader()

    ident = get_identification()
    audit.append("hub_started", {
        "version": ident["version"],
        "core_sha256": ident["core_sha256"],
        "mock": USE_MOCK,
        "port": config.scale_port,
        "tier": config.tier,
        "adapter": adapter.name,
        "plu_count": len(config.plu_records),
    })
    logger.info("GroundUp Scale Hub v%s started (Core SHA: %s…)", ident["version"], ident["core_sha256"][:12])

    yield

    serial.close()
    audit.append("hub_stopped", {})
    logger.info("GroundUp Scale Hub stopped")


app = FastAPI(
    title="GroundUp Scale Hub",
    description="WELMEC 7.2 compliant weighing terminal",
    version=get_identification()["version"],
    lifespan=lifespan,
)


# -- Request/Response models --------------------------------------------------

class ProductSelectRequest(BaseModel):
    product_id: str


class SaleResponse(BaseModel):
    weight_g: int
    price_cents_per_kg: int
    total_cents: int
    consistency_hash: str
    audit_seq: int


class LabelZplRequest(BaseModel):
    scenario: str = "simple_prepack"
    product_name: str
    weight_g: int = Field(gt=0)
    price_cents_per_kg: int = Field(ge=0)
    total_cents: int = Field(ge=0)
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
    consistency_hash: Optional[str] = None


# -- Endpoints ----------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "groundup-scale-hub"}


@app.get("/version")
def version() -> dict:
    ident = get_identification()
    ident["audit_entries"] = audit.entry_count
    ident["state"] = state.state.value
    return ident


@app.get("/scale/status")
def scale_status() -> dict:
    return state.snapshot()


@app.post("/scale/select-product")
def select_product(req: ProductSelectRequest) -> dict:
    record = config.resolve_plu(req.product_id)
    if record is None:
        raise HTTPException(400, f"Product '{req.product_id}' not in allowlist")
    if not state.is_idle():
        raise HTTPException(409, f"Scale busy: {state.state.value}")

    state.begin_weighing(product_id=req.product_id, plu=record.plu)

    cmd = adapter.build_select_command(record.plu)
    if cmd is not None:
        serial.write(cmd)

    audit.append("plu_selected", {
        "product_id": req.product_id,
        "plu": record.plu,
        "name": record.name,
    })
    return {"ok": True, "plu": record.plu, "name": record.name, "state": state.state.value}


@app.post("/scale/reset")
def scale_reset() -> dict:
    state.reset()
    audit.append("manual_reset", {})
    return {"ok": True, "state": "IDLE"}


@app.post("/label/zpl")
def make_label(req: LabelZplRequest) -> dict:
    try:
        scenario = LabelScenario(req.scenario)
    except ValueError:
        raise HTTPException(422, f"Invalid scenario: {req.scenario!r}")

    label = LabelRequest(
        scenario=scenario,
        product_name=req.product_name,
        weight_g=req.weight_g,
        price_cents_per_kg=req.price_cents_per_kg,
        total_cents=req.total_cents,
        currency=req.currency,
        gtin=req.gtin,
        lot=req.lot,
        expiry=req.expiry,
        origin=req.origin,
        operator_name=req.operator_name,
        operator_address=req.operator_address,
        ingredients=req.ingredients,
        allergens=req.allergens,
        storage_instructions=req.storage_instructions,
    )

    missing = validate_label_request(label)
    if missing:
        raise HTTPException(422, missing)

    if req.gtin:
        label.digital_link = build_digital_link(
            base_url=GS1_BASE, gtin=req.gtin, weight_g=req.weight_g,
            lot=req.lot, expiry=req.expiry,
        )

    label.consistency_hash = req.consistency_hash
    zpl = generate_zpl(label)

    audit.append("label_generated", {
        "product": req.product_name,
        "weight_g": req.weight_g,
        "total_cents": req.total_cents,
        "scenario": req.scenario,
    })

    state.finalize()
    return {"ok": True, "zpl": zpl, "digital_link": label.digital_link}


@app.get("/audit/verify")
def audit_verify() -> dict:
    ok, count = audit.verify_chain()
    audit.append("verification_requested", {"result": "pass" if ok else "fail", "entries": count})
    return {"ok": ok, "entries": count, "last_hash": audit.last_hash}


@app.get("/plu/list")
def plu_list() -> dict:
    return {
        "ok": True,
        "tier": config.tier,
        "products": [
            {"plu": r.plu, "product_id": r.product_id, "name": r.name,
             "price_cents_per_kg": r.price_cents_per_kg, "gtin": r.gtin}
            for r in config.plu_records
        ],
    }
