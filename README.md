# Ground UP — Scale Hub

> Legal scale-to-POS bridge for direct agricultural sales.

The Scale Hub connects certified weighing scales (CAS, Bizerba, Mettler-Toledo, DIGI) to Odoo POS and label printers — without requiring POS certification under EU metrology law.

**The scale calculates. The Hub forwards. The label is correct.**

---

## What It Does

- Receives weight and price data from a certified scale via RS-232
- Prints legally compliant labels (self-adhesive, Zebra ZPL) with GS1 Digital Link QR codes
- Forwards sale data to Odoo POS — without the POS needing metrological certification
- Manages PLU/product data from Odoo → scale (one-directional configuration)
- Maintains a tamper-proof, hash-chained audit log of all transactions

## Architecture

```
┌────────┐  RS-232 Port B   ┌──────────┐  HTTPS/JSON   ┌──────────┐
│  CAS   │ ───(TX only)───▶ │          │ ─────────────▶ │ Odoo POS │
│ ER-Plus│                   │ Scale Hub│               │          │
│        │ ◀──(Full Duplex)──│ (RPi 5)  │               │          │
└────────┘  RS-232 Port A    │          │──▶ Zebra      └──────────┘
             (PLU select)    └──────────┘   Label Printer
```

**Key principle:** The certified scale is the _single source of truth_ for weight and price. The Hub never calculates prices — it is classified as a "non-legally relevant ancillary system" under [WELMEC 7.2 §5.3](docs/legal/eu/WELMEC_7_2.md).

---

## Repository Structure

```
scale-hub/
├── hub/                        # Hub software (Python/FastAPI)
│   ├── app/
│   │   ├── main.py             # FastAPI application + API endpoints
│   │   ├── controller.py       # Transaction controller
│   │   ├── state_machine.py    # Sale lifecycle state machine
│   │   ├── plu_map.py          # PLU allowlist management
│   │   ├── audit_log.py        # Hash-chained append-only log
│   │   ├── adapters/           # Scale protocol adapters
│   │   │   ├── cas_erplus.py   # CAS ER-Plus RS-232 adapter
│   │   │   └── serial_layer.py # Serial port abstraction
│   │   └── utils/
│   │       ├── zpl.py          # ZPL II label generation
│   │       ├── label_profiles.py # Scenario-based label profiles
│   │       ├── gs1.py          # GS1 Digital Link encoding
│   │       └── hmac_auth.py    # HMAC-SHA256 API authentication
│   ├── tests/                  # Unit + integration tests
│   ├── scripts/                # Development utilities
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── odoo/                       # Odoo module (groundup_scale_bridge)
│   └── groundup_scale_bridge/
│       ├── models/             # scale.device, scale.plu, scale.log
│       ├── views/              # XML views + menu
│       └── security/           # Access control
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # Technical architecture
│   ├── CERTIFICATION_CHECKLIST.md # Hub certification requirements (Tier 0)
│   ├── LABEL_GUIDE.md          # Label scenarios (Loose → LEH)
│   ├── LEGAL_REGISTER.md       # Legal register + architecture decisions
│   ├── PRODUCT_DELIVERY.md     # Productization: BOM, seals, OTA, provisioning
│   ├── PROTOCOL_CATALOG.md     # Scale protocol reference (8 families)
│   ├── SECURE_BOOT.md          # Secure Boot implementation (Pi 5)
│   ├── architecture.html       # Product page (visual overview)
│   └── legal/                  # Legal excerpts + compliance data
│       ├── eu/                 # EU-wide regulations
│       ├── at/                 # Austria-specific
│       ├── _template/          # Template for new countries
│       ├── COMPLIANCE_MATRIX.md
│       └── README.md
│
└── .github/
    └── workflows/              # CI/CD (planned)
```

---

## Label Scenarios

The Hub automatically selects the correct label format based on the product's configured scenario:

| Scenario | Use Case | Label Size | Nutrition | Barcode |
|----------|----------|-----------|-----------|---------|
| **Loose** | Farmers market | No label | — | — |
| **Simple Prepack** | Farm shop, single-ingredient | 60 × 40 mm | Exempt | QR only |
| **Full Prepack** | Processed products | 80 × 60 mm | Exempt | QR only |
| **LEH Prepack** | Supermarket supply | 100 × 70 mm | Required | EAN-13 + QR |

See [docs/LABEL_GUIDE.md](docs/LABEL_GUIDE.md) for full details.

---

## Legal Framework

The Hub's design is guided by 13 architecture decisions documented in [docs/LEGAL_REGISTER.md](docs/LEGAL_REGISTER.md). Key regulations covered:

- **NAWI 2014/31/EU** — Weighing instrument directive
- **LMIV 1169/2011** — Food information regulation (labeling)
- **WELMEC 7.2** — Software guide for measuring instruments
- **BEV POS-Systeme 2023** — Austrian POS certification requirements
- **CE Marking** — EMV, RED, RoHS
- **GDPR** — Data protection (operator IDs)
- **WEEE 2012/19/EU** — E-waste registration
- **PLD 2024/2853** — Product liability (software as product)

Country-specific compliance data is machine-readable in `docs/legal/{iso2}/compliance.yaml`. Austria is fully researched; EU-27 + Switzerland as placeholders.

See [docs/legal/COMPLIANCE_MATRIX.md](docs/legal/COMPLIANCE_MATRIX.md) for the full matrix.

---

## Quick Start (Development)

```bash
# Clone
git clone https://github.com/GROUNDUP-GmbH/scale-hub.git
cd scale-hub/hub

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start Hub (development mode, no real serial port)
uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
```

### Docker

```bash
cd hub
docker compose up -d
```

---

## Hardware

| Component | Model | Connection |
|-----------|-------|-----------|
| Scale | CAS, DIGI, Mettler, DIBAL, Acom, MASSA-K | RS-232 or Ethernet |
| Hub | Raspberry Pi 5 (4 GB) in official case | Ethernet + USB |
| Label Printer | Zebra ZD421t (or compatible) | USB or Ethernet |
| Receipt Printer | Any ESC/POS printer | Via Odoo POS (not Hub) |

### Supported Scale Adapters (8 families)

| Adapter | Scales | Protocol | Tier |
|---------|--------|----------|------|
| `cas_er` | CAS ER-Plus, ER Jr, AP | RS-232 weight-only | Tier 0/2 |
| `cas_lp` | CAS LP-I/II, LP-1000 | RS-232 binary PLU | Tier 1 |
| `cas_cl` | CAS CL-3000/5000/7200 | RS-232 binary PLU+ | Tier 1 |
| `digi_sm` | DIGI SM-100/120/5300/6000 | Ethernet TCP/IP | Tier 1 |
| `mettler_tiger` | Mettler Toledo Tiger | Ethernet TCP/IP | Tier 1 |
| `dibal` | DIBAL G-310/325/500 | RS-232 TISA | Tier 2+ |
| `acom` | Acom NETS, PC series | Ethernet TCP/IP | Tier 1 |
| `massa_k` | MASSA-K VPM, Basic | RS-232/Ethernet | Tier 1/2 |

### Product Delivery & Sealing

Each Hub ships with:
- Pre-flashed, Secure-Boot-enabled microSD card
- 2 × tamper-evident holographic seals (case + SD slot)
- OTA updates via RAUC (A/B partitioning, signed bundles, auto-rollback)

See [docs/PRODUCT_DELIVERY.md](docs/PRODUCT_DELIVERY.md) for full BOM, provisioning pipeline, and seal specifications.

---

## Odoo Module

The `groundup_scale_bridge` module provides:

- **Scale Device** management (register Hubs, configure connection)
- **PLU Map** (product ↔ PLU mapping with LMIV fields)
- **Scale Log** (transaction log synced from Hub audit log)

Install in Odoo 19:
```bash
# Copy to Odoo addons path
cp -r odoo/groundup_scale_bridge /path/to/odoo/addons/
# Install via Odoo UI: Apps → Update Apps List → Search "Scale Bridge"
```

---

## Contributing

This is an open-source project by [Ground UP GmbH](https://groundup.farm). Contributions welcome.

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit with descriptive messages
4. Open a Pull Request

---

## License

[MIT](LICENSE)

---

## Links

- **Product Page:** [groundup.farm](https://groundup.farm)
- **Odoo Modules:** [GROUNDUP-GmbH/BodenKraft_odoo_modules](https://github.com/GROUNDUP-GmbH/BodenKraft_odoo_modules)
- **SOMA (Carbon MRV):** [GROUNDUP-GmbH/soma](https://github.com/GROUNDUP-GmbH/soma)
- **OpenAgDB:** [GROUNDUP-GmbH/OpenAgDB](https://github.com/GROUNDUP-GmbH/OpenAgDB)
