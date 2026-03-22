# Scale Hub — Technical Architecture

> **Status:** v3.0 · 2026-03-22
> **Maintainer:** Ground UP GmbH · FN 481220 b
> **Product Page:** [architecture.html](architecture.html) (non-technical, StoryBrand)
> **Legal Register:** [LEGAL_REGISTER.md](LEGAL_REGISTER.md)
> **Label Guide:** [LABEL_GUIDE.md](LABEL_GUIDE.md)
> **Protocol Catalog:** [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md)

---

## Core Principle

**The certified scale is the sole authority for weight measurement and price calculation.**

Neither the Hub nor Odoo POS may alter measurement values or compute prices. The Hub is a controlled communication interface — classified as a "non-legally relevant ancillary system" under the European Software Guide for measuring instruments (WELMEC 7.2 §5.3).

The Hub supports **multiple scale families** via an Adapter Pattern (see [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md)):

| Tier | Capability | Example Scales | Hub Role |
|---|---|---|---|
| **Tier 1** | Full PLU protocol | CAS LP/CL, DIGI SM, Mettler Toledo Tiger | PLU manager + data receiver |
| **Tier 2** | Weight/price read-only | CAS ER-Plus, CAS AP, basic bench scales | Data receiver + virtual printer |
| **Tier 2+** | Price send + weight receive | DIBAL | Price injector + data receiver |

**Sources:** Directive 2014/31/EU Art. 1(2)(a) · Austrian Metrology Act (MEG) §8(1) · WELMEC 7.2 §4.2 · BEV Information Sheet on POS Systems 2023

---

## System Boundary

### Tier 1 Scale (e.g., CAS LP, DIGI SM, Mettler Toledo Tiger)

```
┌──────────────────────────────────────────────────────────────────────┐
│  NON-REGULATED ZONE  (No certification required — WELMEC 7.2 §5.3)  │
│                                                                      │
│  ┌──────────────┐    ┌────────────────┐    ┌──────────────────┐     │
│  │  Odoo 19     │    │  GroundUp Hub  │    │  Zebra Label     │     │
│  │  ERP / POS   │◄──►│  (Raspberry Pi) │───►│  Printer         │     │
│  │              │    │                │    │  (ZPL II)        │     │
│  │  • Products  │    │  • Adapter     │    └──────────────────┘     │
│  │  • Booking   │    │  • State Mach. │                              │
│  │  • Receipt   │    │  • Audit Log   │    ┌──────────────────┐     │
│  │  • Reports   │    │  • PLU Sync ↕  │    │  Receipt Printer │     │
│  └──────────────┘    │  • Label Engine│    │  (via Odoo POS)  │     │
│                      └───────┬────────┘    └──────────────────┘     │
│                              │ RS-232 / Ethernet                     │
│                              │ (bidirectional)                       │
├──────────────────────────────┼───────────────────────────────────────┤
│  SYSTEM BOUNDARY             │  WELMEC 7.2 §4.2 · Dir. 2014/31/EU  │
├──────────────────────────────┼───────────────────────────────────────┤
│  METROLOGICALLY REGULATED    │                                       │
│  (Dir. 2014/31/EU · MEG §8) │                                       │
│                      ┌───────┴────────┐                              │
│                      │  Tier 1 Scale  │  PLU upload from Hub ✓       │
│                      │  (LP/CL/DIGI)  │  Weight/price to Hub ✓       │
│                      │                │  Sales data to Hub ✓         │
│                      │  • Weight      │  Built-in label printer ✓    │
│                      │  • Price/kg    │                               │
│                      │  • Total price │                               │
│                      └────────────────┘                              │
└──────────────────────────────────────────────────────────────────────┘
```

### Tier 2 Scale (e.g., CAS ER-Plus, basic bench scales)

```
┌──────────────────────────────────────────────────────────────────────┐
│  NON-REGULATED ZONE  (No certification required — WELMEC 7.2 §5.3)  │
│                                                                      │
│  ┌──────────────┐    ┌────────────────┐    ┌──────────────────┐     │
│  │  Odoo 19     │    │  GroundUp Hub  │    │  Zebra Label     │     │
│  │  ERP / POS   │◄──►│  (Raspberry Pi) │───►│  Printer         │     │
│  │              │    │                │    │  (ZPL II)        │     │
│  │  • Products  │    │  • Adapter     │    └──────────────────┘     │
│  │  • Booking   │    │  • State Mach. │                              │
│  │  • Receipt   │    │  • Audit Log   │    ┌──────────────────┐     │
│  │  • Reports   │    │  • Price Disp. │    │  Price Dashboard  │     │
│  └──────────────┘    │  • Label Engine│    │  (Phone/Tablet/   │     │
│                      │  • Verification│    │   HDMI Display)   │     │
│                      └───────┬────────┘    └──────────────────┘     │
│                              │ RS-232                                │
│                              │ (Scale → Hub: print data / weight)    │
│                              │ (Hub → Scale: NOT supported)          │
├──────────────────────────────┼───────────────────────────────────────┤
│  SYSTEM BOUNDARY             │  WELMEC 7.2 §4.2 · Dir. 2014/31/EU  │
├──────────────────────────────┼───────────────────────────────────────┤
│  METROLOGICALLY REGULATED    │                                       │
│  (Dir. 2014/31/EU · MEG §8) │                                       │
│                      ┌───────┴────────┐                              │
│                      │  Tier 2 Scale  │  PLU upload from Hub ✗       │
│                      │  (CAS ER-Plus) │  Weight/price to Hub ✓       │
│                      │                │  Price entry: MANUAL         │
│                      │  • Weight      │  No built-in label printer   │
│                      │  • Price/kg    │                               │
│                      │  • Total price │  Hub = virtual printer       │
│                      └────────────────┘  (captures print stream)     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Hardware Stack

| Component | Model | Role |
|---|---|---|
| Scale | Any supported scale (see [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md)) | Weighing + price calculation (certified) |
| Hub | Raspberry Pi 5 (industrial enclosure) | Communication interface + label engine |
| Label Printer | Zebra (ZPL II compatible) | Self-adhesive product labels |
| Receipt Printer | Any ESC/POS | Driven by Odoo POS, not Hub |
| Serial Adapter | 1× USB-to-RS232 (per scale) | Single bidirectional port |
| Price Display | Phone/Tablet/HDMI (optional) | Tier 2 only: price change notifications |

### Reference Configurations

| Configuration | Scale | Tier | PLU Sync | Total Cost (approx.) |
|---|---|---|---|---|
| **Starter** | CAS ER-Plus | 2 | Manual (Hub-assisted) | €400–600 |
| **Standard** | CAS LP-1 | 1 | Automatic | €800–1,100 |
| **Professional** | CAS CL5200 | 1 | Automatic + Ethernet | €1,700–2,200 |
| **Enterprise** | DIGI SM-5300 | 1 | Automatic + Ethernet | €2,500+ |

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

### Tier 1 (Full PLU Protocol)

| # | Flow | Direction | Content | Legal Basis |
|---|---|---|---|---|
| 1 | Product Selection | POS → Hub → Scale | `product_id` → PLU | WELMEC §4.4: documented commands only |
| 2 | Sale Data | Scale → Hub | Weight, price/kg, total | Dir. 2014/31/EU: from certified instrument |
| 3 | Sale Forwarding | Hub → Odoo POS | 1:1 unmodified | WELMEC §5.3: POS is not a terminal |
| 4 | PLU Sync | Odoo → Hub → Scale | PLU, name, price | WELMEC §4.4: controlled + logged |
| 5 | Label | Hub → Zebra | ZPL + GS1 QR + optional EAN-13 | EU FIC Reg. 1169/2011 Art. 9 |
| 6 | Audit | Hub-internal | JSONL + SHA-256 chain | WELMEC §4.5: traceability |

### Tier 2 (Weight/Price Read-Only — e.g., CAS ER-Plus)

| # | Flow | Direction | Content | Legal Basis |
|---|---|---|---|---|
| 1 | Price Change Notification | Odoo → Hub → Dashboard | New prices for manual entry | — (operational, not metrological) |
| 2 | Sale Data (print stream) | Scale → Hub | Weight, price/kg, total (via virtual printer) | Dir. 2014/31/EU: from certified instrument |
| 3 | Price Verification | Hub-internal | Compare scale price vs. Odoo price | Quality assurance (not legally required) |
| 4 | Sale Forwarding | Hub → Odoo POS | 1:1 from scale data | WELMEC §5.3: POS is not a terminal |
| 5 | Label | Hub → Zebra | ZPL + GS1 QR + optional EAN-13 | EU FIC Reg. 1169/2011 Art. 9 |
| 6 | Audit | Hub-internal | JSONL + SHA-256 chain | WELMEC §4.5: traceability |

**Key difference:** Flow 1 and 4 are absent in Tier 2. The Hub cannot send data TO the scale. Instead, the Hub displays price changes on a local dashboard and the farmer enters them manually. Flow 3 (price verification) is a new safety net that catches human error.

---

## State Machine

### Tier 1 (Hub controls PLU selection)

```
              ┌─────────┐
              │  IDLE   │ ←── PLU Sync allowed
              └────┬────┘
                   │ POS: select product
                   ▼
              ┌─────────┐
              │ LOCKED  │ ←── No config changes
              └────┬────┘
                   │ Scale: sale data received
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

### Tier 2 (Scale controls PLU, Hub receives)

```
              ┌─────────┐
              │  IDLE   │ ←── Monitoring for print data
              └────┬────┘
                   │ Scale: print stream received (virtual printer)
                   ▼
              ┌──────────┐
              │VERIFYING │ ←── Compare price with Odoo
              └────┬─────┘
                   │ Match? → proceed / Mismatch? → alert + proceed
                   ▼
              ┌─────────┐
              │PRINTING │ ←── Zebra label generated + printed
              └────┬────┘
                   │ Forwarded to Odoo POS
                   ▼
              ┌─────────┐
              │  IDLE   │
              └─────────┘
```

- PLU/price updates **only** accepted in `IDLE` state (Tier 1)
- Tier 2 adds a `VERIFYING` state for price cross-checking
- During `LOCKED`, `VERIFYING`, or `PRINTING`, configuration changes are rejected
- Every state transition is logged in the audit chain

---

## Port Architecture (Single Bidirectional RS-232)

Each scale connects via **one RS-232 port** (or Ethernet for Tier 1 scales with TCP/IP). The Hub uses **protocol-level command separation** instead of physical port separation:

### Tier 1 (Bidirectional)

```
Hub ◄──── RS-232 / Ethernet ────► Scale
     PLU Write (Hub → Scale)
     PLU Read  (Hub ← Scale)
     Weight    (Hub ← Scale)
     Status    (Hub ← Scale)
```

- Allowlisted commands only (Decision 03)
- PLU writes blocked during active weighing (state machine)
- All commands logged in audit chain

### Tier 2 (Effectively Unidirectional)

```
Hub ◄──── RS-232 ──── Scale
     Print data  (Scale → Hub)
     Weight req. (Hub → Scale, AP protocol)
```

- Hub receives print stream (virtual DEP-50/DLP-50 printer)
- Hub can request weight via AP protocol (ENQ → 0x11 → response)
- Hub **cannot** send PLU data to the scale
- Unidirectional data flow is the strongest WELMEC compliance argument

### Integrity Guarantee

Without physical port separation, integrity is ensured through:
1. **Allowlist** (Decision 03): Only documented commands accepted
2. **State machine**: Configuration changes blocked during transactions
3. **Audit log**: Every byte sent/received is logged with timestamp
4. **Secure Boot** (Decision 07): Hub software cannot be modified

This satisfies WELMEC §4.4.2.1(a)(b) through logical rather than physical separation.

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
│   ├── PROTOCOL_CATALOG.md      ← All verified scale protocols + Tier classification
│   ├── LEGAL_REGISTER.md        ← Legal register + architecture decisions
│   ├── LABEL_GUIDE.md           ← Label scenarios + mandatory fields
│   └── legal/                   ← Legal texts (eu/, at/, hu/, ...)
├── hub/
│   ├── app/                     ← FastAPI service
│   │   ├── main.py
│   │   ├── adapters/            ← Scale adapters (one per protocol family)
│   │   │   ├── base.py          ← ScaleAdapter protocol definition
│   │   │   ├── cas_lp.py        ← CAS LP/CL binary protocol (Tier 1)
│   │   │   ├── cas_er.py        ← CAS ER/AP simple protocol (Tier 2)
│   │   │   ├── digi_sm.py       ← DIGI SM Ethernet protocol (Tier 1)
│   │   │   ├── mettler_tiger.py ← Mettler Toledo Tiger (Tier 1)
│   │   │   └── dibal.py         ← DIBAL EPOS TISA (Tier 2+)
│   │   └── utils/               ← ZPL, GS1, label_profiles, audit
│   ├── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
└── odoo-addon/
    └── groundup_scale_bridge/   ← Odoo module
```

Currently located at: `infrastructure/scale_hub/` (in this monorepo) and `addons/groundup_scale_bridge/` (Odoo addon).
