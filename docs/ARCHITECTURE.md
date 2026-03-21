# Scale Hub — Technical Architecture

> **Status:** v2.0 · 2026-03-21
> **Maintainer:** Ground UP GmbH · FN 481220 b
> **Product Page:** [architecture.html](architecture.html) (non-technical, StoryBrand)
> **Legal Register:** [LEGAL_REGISTER.md](LEGAL_REGISTER.md)
> **Label Guide:** [LABEL_GUIDE.md](LABEL_GUIDE.md)

---

## Core Principle

**The CAS ER-Plus scale is the sole authority for weight measurement and price calculation.**

Neither the Hub nor Odoo POS may alter measurement values or compute prices. The Hub is a controlled communication interface — classified as a "non-legally relevant ancillary system" under the European Software Guide for measuring instruments (WELMEC 7.2 §5.3).

**Sources:** Directive 2014/31/EU Art. 1(2)(a) · Austrian Metrology Act (MEG) §8(1) · WELMEC 7.2 §4.2 · BEV Information Sheet on POS Systems 2023

---

## System Boundary

```
┌─────────────────────────────────────────────────────────────────────┐
│  NON-REGULATED ZONE                                                  │
│  (No certification required — WELMEC 7.2 §5.3)                      │
│                                                                      │
│  ┌──────────────┐    ┌────────────────┐    ┌──────────────────┐     │
│  │  Odoo 19     │    │  GroundUp Hub  │    │  Zebra Label     │     │
│  │  ERP / POS   │◄──►│  (Raspberry Pi) │───►│  Printer         │     │
│  │              │    │                │    │  (ZPL II)        │     │
│  │  • Products  │    │  • State Mach. │    └──────────────────┘     │
│  │  • Booking   │    │  • Audit Log   │                              │
│  │  • Receipt   │    │  • PLU Mapping │    ┌──────────────────┐     │
│  │  • Reports   │    │  • GS1 Builder │    │  Receipt Printer │     │
│  └──────────────┘    │  • HMAC Auth   │    │  (via Odoo POS)  │     │
│                      │  • Label Engine│    └──────────────────┘     │
│                      └───────┬────────┘                              │
│                              │                                       │
├──────────────────────────────┼───────────────────────────────────────┤
│  SYSTEM BOUNDARY             │  WELMEC 7.2 §4.2 · Dir. 2014/31/EU  │
├──────────────────────────────┼───────────────────────────────────────┤
│                              │                                       │
│  METROLOGICALLY REGULATED    │  Port A (↕)  Port B (↓ TX only)     │
│  (Dir. 2014/31/EU · MEG §8) │                                       │
│                      ┌───────┴────────┐                              │
│                      │  CAS ER-Plus   │                              │
│                      │                │                              │
│                      │  • Weight      │                              │
│                      │  • Price/kg    │                              │
│                      │  • Total price │                              │
│                      │  • Verification│                              │
│                      └────────────────┘                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Hardware Stack

| Component | Model | Role |
|---|---|---|
| Scale | CAS ER-Plus (RS232 x2 Comms Module) | Weighing + price calculation (certified) |
| Hub | Raspberry Pi 5 (industrial enclosure) | Communication interface + label engine |
| Label Printer | Zebra (ZPL II compatible) | Self-adhesive product labels |
| Receipt Printer | Any ESC/POS | Driven by Odoo POS, not Hub |
| Serial Adapters | 2× USB-to-RS232 | Port A (Full Duplex) + Port B (TX only) |

---

## Software Stack

| Layer | Technology |
|---|---|
| OS | Raspberry Pi OS 64-bit (dm-verity rootfs) |
| Runtime | Docker + Docker Compose |
| Application | FastAPI (Python 3.12) + Uvicorn |
| Serial I/O | PySerial |
| Label Generation | ZPL II via Jinja2 templates |
| GS1 Digital Link | Built-in encoder (AI 01/3103/10/15/21) |
| Authentication | HMAC-SHA256 (Hub ↔ Odoo) |
| Audit | JSONL + SHA-256 hash chain |
| Secure Boot | OTP-fused RSA-2048, signed bootloader, dm-verity, signed Docker images |

---

## Data Flows

| # | Flow | Direction | Content | Legal Basis |
|---|---|---|---|---|
| 1 | Product Selection | POS → Hub → Scale | `product_id` → PLU | WELMEC §4.4: documented commands only |
| 2 | Sale Data | Scale → Hub | Weight, price/kg, total | Dir. 2014/31/EU: from certified instrument |
| 3 | Sale Forwarding | Hub → Odoo POS | 1:1 unmodified | WELMEC §5.3: POS is not a terminal |
| 4 | PLU Sync | Odoo → Hub → Scale | PLU, name, price | WELMEC §4.4: controlled + logged |
| 5 | Label | Hub → Zebra | ZPL + GS1 QR + optional EAN-13 | EU FIC Reg. 1169/2011 Art. 9 |
| 6 | Audit | Hub-internal | JSONL + SHA-256 chain | WELMEC §4.5: traceability |

---

## State Machine

```
              ┌─────────┐
              │  IDLE   │ ←── PLU Sync allowed
              └────┬────┘
                   │ POS: select product
                   ▼
              ┌─────────┐
              │ LOCKED  │ ←── No config changes
              └────┬────┘
                   │ Scale: sale data received (Port B)
                   ▼
              ┌─────────┐
              │PRINTING │ ←── Label generated + printed
              └────┬────┘
                   │ Label confirmed / forwarded to POS
                   ▼
              ┌─────────┐
              │  IDLE   │
              └─────────┘
```

- PLU/price updates **only** accepted in `IDLE` state
- During `LOCKED` or `PRINTING`, configuration changes are rejected
- Every state transition is logged in the audit chain

---

## Port Architecture (RS232 x2)

The CAS ER-Plus RS232 x2 Comms Module provides two physically separate serial ports:

**Port A — Full Duplex (Configuration)**
- Direction: Hub ↔ Scale
- Purpose: PLU selection, price lookups
- Restriction: Only allowlisted `product_id` values accepted
- Timing: Only during `IDLE` state

**Port B — TX Only (Sale Data)**
- Direction: Scale → Hub
- Purpose: Transmit completed sale data
- Restriction: Hub cannot send to Port B (hardware-enforced)
- Content: Weight, PLU, price/kg, total, timestamp

Physical separation ensures that sale data flow cannot be influenced by the configuration channel. This directly addresses WELMEC §4.4.2.1(a)(b).

---

## Security Architecture

### Secure Boot (from device #1)

1. **Boot ROM:** RSA-2048 public key hash burned into CM4/Pi 5 OTP
2. **Bootloader:** Signed `boot.img` + `config.txt`
3. **Root Filesystem:** dm-verity (read-only squashfs)
4. **Application:** Signed Docker images + AppArmor profiles
5. **Updates:** A/B partition scheme + signed OTA packages

No root access in the field. Updates only via signed OTA.

### Audit Log

- Format: JSONL, one event per line
- Integrity: SHA-256 hash chain (each entry references the previous hash)
- Immutability: Append-only, no updates, no deletions
- Verification: `/audit/verify` endpoint
- Optional: Daily export + RDDL blockchain anchoring

### API Authentication

- HMAC-SHA256 between Hub and Odoo
- Per-device shared secret, rotated on OTA updates
- All API calls logged in audit chain

---

## Compliance Architecture

See [LEGAL_REGISTER.md](LEGAL_REGISTER.md) for the full legal register and architecture decisions.

### Three-Layer Model

1. **EU Layer** (`legal/eu/`): EU-wide regulations (FIC, NAWI, Traceability)
2. **National Layer** (`legal/{iso2}/`): Country-specific rules + machine-readable `compliance.yaml`
3. **Hub Runtime**: Loads `compliance.yaml` for the configured country and validates mandatory fields

### Label Profiles

See [LABEL_GUIDE.md](LABEL_GUIDE.md) for detailed scenario documentation.

Four scenarios configured per product in Odoo:

| Scenario | Label Size | Use Case |
|---|---|---|
| Loose | — (no label) | Farmers market, loose goods |
| Simple Prepack | 60 × 40 mm | Single-ingredient products, farm shop |
| Full Prepack | 80 × 60 mm | Processed products, packing station |
| Retail Prepack | 100 × 70 mm | Supermarket supply (nutrition + EAN-13 + GS1 QR) |

---

## Repository Structure (Target)

```
groundup-scale-hub/              (future standalone repo)
├── README.md
├── LICENSE
├── docs/
│   ├── architecture.html        ← Product page (StoryBrand)
│   ├── ARCHITECTURE.md          ← This document
│   ├── LEGAL_REGISTER.md        ← Legal register + architecture decisions
│   ├── LABEL_GUIDE.md           ← Label scenarios + mandatory fields
│   └── legal/                   ← Legal texts (eu/, at/, hu/, ...)
├── hub/
│   ├── app/                     ← FastAPI service
│   │   ├── main.py
│   │   ├── serial/              ← CAS adapter, port manager
│   │   └── utils/               ← ZPL, GS1, label_profiles, audit
│   ├── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
└── odoo-addon/
    └── groundup_scale_bridge/   ← Odoo module
```

Currently located at: `infrastructure/scale_hub/` (in this monorepo) and `addons/groundup_scale_bridge/` (Odoo addon).
