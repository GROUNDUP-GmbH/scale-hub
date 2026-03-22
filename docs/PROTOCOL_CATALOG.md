# Scale Hub — Protocol Catalog

> **Status:** v1.0 · 2026-03-22
> **Maintainer:** Ground UP GmbH · FN 481220 b
> **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
> **Legal Register:** [LEGAL_REGISTER.md](LEGAL_REGISTER.md)

---

## Overview

This document catalogs all verified scale communication protocols relevant to the Ground UP Scale Hub. Each protocol entry includes wire-level byte sequences, serial parameters, supported operations, and the source of verification.

The Hub uses an **Adapter Pattern** (see [ARCHITECTURE.md Decision 12](ARCHITECTURE.md#decision-12-scale-adapter-pattern-for-multi-vendor-support)) — each protocol family maps to one adapter module.

---

## Scale Tier Classification

| Tier | Capability | Hub Role | PLU Sync | Price Calculation | Certification |
|---|---|---|---|---|---|
| **Tier 0** | Weight only (any OIML scale) | **Price calculator** + label engine | N/A (no PLU on scale) | **Hub calculates** | **Required** (€10–25k) |
| **Tier 1** | Full bidirectional PLU protocol | PLU manager + data receiver | Automatic from Odoo | Scale calculates | Not required |
| **Tier 2** | Weight/price read-only | Data receiver + virtual printer | Not possible via protocol | Scale calculates | Not required |
| **Tier 2+** | Price send + weight receive | Price injector + data receiver | Price only (no PLU name) | Scale calculates | Not required |

**Tier 0** is the long-term target architecture (see [Option F](#option-f-hub-as-certified-price-calculator--tier-0-recommended-long-term)). It decouples the Hub from any specific scale manufacturer and reduces the farmer's entry cost to ~€400.

---

## Protocol Family 1: CAS LP (Binary PLU Protocol)

### Supported Models

| Model | Protocol Version | PLU Capacity | Interface | Market |
|---|---|---|---|---|
| CAS LP-1 | v1.5 or v1.6 | 4,000 | RS-232 (+TCP/IP opt.) | EU/AU (OIML) |
| CAS LP-II / LP-1.6 | v1.6 | 4,000 | RS-232 + TCP/IP | Worldwide |
| CAS LP-1000N/NP | v1.6 | 4,000 | RS-232 + USB | North America (NTEP) |
| CAS CL5000(J) | CL (LP-compatible) | 10,000+ | RS-232 + TCP/IP | Worldwide |

**Note:** CAS LP-II is identical to LP-1.6 in protocol terms.
Source: [cas-lp.narod.ru](https://cas-lp.narod.ru/) (LavrSoft driver documentation)

### Serial Parameters

| Parameter | Value |
|---|---|
| Baud Rate | Configurable: 2400 / 4800 / 9600 / 19200 |
| Data Bits | 8 |
| Parity | None |
| Stop Bits | 1 |
| Flow Control | None |

### PLU Data Structure (Binary)

Each PLU record is 83 bytes (0x0053):

| Offset | Size | Format | Content |
|---|---|---|---|
| `0x0000–0x0003` | 4 | Binary | PLU Number (0–4000) |
| `0x0004–0x0009` | 6 | BCD | Product Code (barcode digits) |
| `0x000A–0x0041` | 56 | ASCII | Product Name (2 lines × 28 chars) |
| `0x0042–0x0045` | 4 | Binary | Price (max 999,999 = currency subunit) |
| `0x0046–0x0048` | 3 | BCD | Shelf Life / Expiry Date |
| `0x0049–0x004A` | 2 | Binary | Tare Weight |
| `0x004B–0x0050` | 6 | — | Group Code |
| `0x0051–0x0052` | 2 | Binary | Message Number (links to message table) |

**Source:** [zipstore.ru — CAS LP Protocol](https://zipstore.ru/auxpage_1c_protocol_interface_cas_lp_scale/)

### Key Commands

| Command | Direction | Description |
|---|---|---|
| PLU Write | Hub → Scale | Upload single PLU record |
| PLU Read | Hub ← Scale | Download single PLU record |
| PLU Delete | Hub → Scale | Delete PLU by number |
| Smart-Sync | Hub ↔ Scale | Incremental update (only changed PLUs) |
| Status Query | Hub ← Scale | Scale state, current weight, price, PLU# |
| Sales Totals Read | Hub ← Scale | Weight total, amount, count per PLU |
| Sales Totals Delete | Hub → Scale | Reset sales counters |
| Date/Time Write | Hub → Scale | Synchronize clock |
| Keyboard Map R/W | Hub ↔ Scale | Assign PLUs to speed keys |
| Label Config R/W | Hub ↔ Scale | Promotional text lines, label format |

**Critical feature:** Smart-Sync allows PLU updates **while the scale is actively weighing** — the transfer pauses during a weighing operation and resumes automatically.

### Hub Adapter: `cas_lp.py`

**Classification:** Tier 1 — Full integration
**Capabilities:**
- Automatic PLU sync from Odoo (product name, price, barcode, shelf life, tare)
- Real-time weight/price/total reading
- Sales statistics download
- Speed key programming

---

## Protocol Family 2: CAS AP/ER (Simple Weight Protocol)

### Supported Models

| Model | Category | Interface | Price on RS-232 | Market |
|---|---|---|---|---|
| CAS ER-Plus | Price Computing | RS-232 (optional) | Yes (status read) | EU (OIML) |
| CAS ER Jr | Price Computing | RS-232 (optional) | Yes (status read) | EU (OIML) |
| CAS AP | Bench Scale | RS-232 | Yes (status read) | Worldwide |
| CAS AD | Bench Scale | RS-232 | No (weight only) | Worldwide |
| CAS DB | Bench Scale | RS-232 | No (weight only) | Worldwide |
| CAS EB | Bench Scale | RS-232 | No (weight only) | Worldwide |
| CAS ED | Bench Scale | RS-232 | No (weight only) | Worldwide |
| CAS HB | Bench Scale | RS-232 | No (weight only) | Worldwide |
| CAS HD | Bench Scale | RS-232 | No (weight only) | Worldwide |
| CAS PB | Bench Scale | RS-232 | No (weight only) | Worldwide |
| CAS PDC | Price Computing | RS-232 | Yes (via ECR TYPE) | Worldwide |
| CAS PDI | Price Computing | RS-232 | Yes (via ECR TYPE) | Worldwide |
| CAS SW / SWN | Bench Scale | RS-232 | No (weight only) | Worldwide |
| CAS PR LCD | Printing Scale | RS-232 | Yes (status read) | Worldwide |

**Source:** [Scale-Soft.com — CAS AP Driver](https://scale-soft.com/cas_ap.htm)

### Serial Parameters (verified for CAS PD-II, applicable to AP/ER family)

| Parameter | Value |
|---|---|
| Baud Rate | 9600 |
| Data Bits | 7 |
| Parity | Even |
| Stop Bits | 1 |
| Flow Control | None |

**Source:** [CAS PD-II Manual, ManualsLib](https://www.manualslib.com/manual/972542/Cas-Pd-Ii.html)

### Wire Protocol (from rkeeper `s_cas.dll` documentation)

**Weight Request:**

```
Hub → Scale:  ENQ (0x05)
Scale → Hub:  ACK (0x06)
Hub → Scale:  0x11
Scale → Hub:  [Status][STX][Stability][Space][Weight 7 bytes][Unit][pad][LRC][ETX]
```

**Response format (15-byte variant):**

| Byte | Content | Example |
|---|---|---|
| 1 | `0x01` or `0x81` | Status flags |
| 2 | `STX` (0x02) | Start of text |
| 3 | `S` or `U` | **S**table or **U**nstable |
| 4 | Space (0x20) | Separator |
| 5–11 | Weight with decimal | `  123.7` (7 chars, right-justified) |
| 12 | Unit char | `g` or `k` |
| 13 | Padding | — |
| 14 | LRC | XOR of bytes 3–13 |
| 15 | `ETX` (0x03) | End of text |

**Alternative response (16-byte variant):**

| Byte | Content |
|---|---|
| 5–10 | Weight with decimal (6 chars) |
| 11 | Unit char |
| 12 | Padding |
| 13 | LRC (XOR bytes 3–12) |
| 14 | `ETX` (0x03) |
| 15 | `EOT` (0x04) |

**Source:** [rkeeper RK7 Documentation — Supported Scale Drivers](https://docs.rkeeper.ru/rk7/latest/ru/podderyoivaemye-drajvery-vesov-10819223.html)

### CAS ER-Plus: RS-232 Port Usage

The ER-Plus RS-232 port is primarily designed for connecting an external CAS printer:

| Printer Option | Type | Description |
|---|---|---|
| `NON` | — | No printer connected |
| `DEP-50` | Receipt printer | CAS thermal receipt printer |
| `DLP-50` | Label printer | CAS thermal label printer |

**The Hub can act as a "virtual printer"** — presenting itself to the ER-Plus as a DEP-50/DLP-50 and capturing the transaction data stream. This is the recommended integration mode for Tier 2 scales.

**Source:** [CAS ER-Plus User Manual (PDF)](https://www.casscale.com.au/wp-content/uploads/CAS-ER-PLUS-User-Manual.pdf), Chapter 3f / Chapter 4

### ER-Plus Key Limitations

| Feature | Capability |
|---|---|
| PLU Capacity | 200 (5 direct keys + 194 indirect + 1 free price) |
| PLU Programming | Manual via keyboard only (ASCII codes) |
| PLU Upload via RS-232 | **Not supported** |
| Weight/Price Read via RS-232 | Yes (CAS AP protocol or printer data stream) |
| Networking | **Not supported** |

### Hub Adapter: `cas_er.py`

**Classification:** Tier 2 — Weight/price receive only
**Capabilities:**
- Receive weight + price data (via printer protocol or AP weight request)
- Generate labels on Zebra printer (replacing/augmenting the CAS DLP-50)
- Forward transaction to Odoo POS
- **Cannot** upload PLUs or prices to the scale

---

## Protocol Family 3: CAS CL (Extended PLU Protocol)

### Supported Models

| Model | PLU Capacity | Interface | Display |
|---|---|---|---|
| CAS CL5000(J) | 10,000+ | RS-232 + TCP/IP | Standard |
| CAS CL-3000 | 4,000 | RS-232 + TCP/IP | Standard |
| CAS CL-5200 | 10,000 | RS-232 + TCP/IP | Standard |
| CAS CL-5500 | varies | RS-232 + TCP/IP | Standard |
| CAS CL-7200 | 10,000 | RS-232 + TCP/IP + WiFi | 10.2" Touchscreen |

### Additional Capabilities (vs. LP Protocol)

| Feature | LP Protocol | CL Protocol |
|---|---|---|
| Departments | — | Read/Write/Delete |
| Groups | — | Read/Write/Delete |
| Keyboard Sets | Basic | Multiple sets |
| PLU Fields | Name (2 lines), Price, Shelf Life, Tare, Group, Message | + Department, Product Type, Fixed Weight |

**Hub Adapter:** `cas_cl.py` — **Classification:** Tier 1

**Source:** [Scale-Soft.com — CAS CL Driver](https://scale-soft.com/cas_cl.htm)

---

## Protocol Family 4: DIGI SM (Ethernet)

### Supported Models

DIGI SM series (SM-100, SM-300, SM-500, SM-5100, SM-5300, SM-6000)

### Interface

| Parameter | Value |
|---|---|
| Protocol | TCP/IP (Ethernet only) |
| RS-232 | Not used for data exchange |

### Capabilities

- PLU write/delete (number, type, name, price, shelf life, barcode prefix, tare, special messages, ingredients, label format)
- Speed key programming
- Date/time synchronization
- No sales total readback documented

### Wire Protocol (from rkeeper `s_digi.dll`)

**Weight Request:**

```
Hub → Scale:  STX W ETX
Scale → Hub:  [STX][w][3 digits][?][3 digits]...[CRC][ETX]
```

CRC = XOR of bytes 2 through n-2.

**Hub Adapter:** `digi_sm.py` — **Classification:** Tier 1

**Sources:** [Scale-Soft.com — DIGI SM Driver](https://scale-soft.com/digi_sm.htm), [rkeeper Documentation](https://docs.rkeeper.ru/rk7/latest/ru/podderyoivaemye-drajvery-vesov-10819223.html)

---

## Protocol Family 5: Mettler Toledo Tiger (RS-232 + Ethernet)

### Serial Parameters

RS-232 and TCP/IP (both supported).

### Capabilities (most feature-rich protocol documented)

- PLU CRUD (number, type, name, price, shelf life, sell-by, barcode, group code, tare number, fixed weight, tax number, message number, ingredients, price change permission, discount permission)
- Speed key programming
- Group management (number + name)
- Tare table management
- Tax rate table
- Label format configuration
- Running text / promotional messages
- Store name
- Date/time synchronization
- Barcode format configuration
- Special offers (price, name, validity period)

### Wire Protocol (from rkeeper `s_tiger.dll`)

**Weight stream (continuous):**

```
[STX][ ][ ][digit][.][digit][digit][digit][ ][k][g]...[CR][LF]
```

Example: `STX   1.234 kg CR LF` → 1.234 kg

**Hub Adapter:** `mettler_tiger.py` — **Classification:** Tier 1 (Premium)

**Sources:** [Scale-Soft.com — Mettler Toledo Tiger](https://scale-soft.com/mettler_toledo_tiger_p.htm), [rkeeper Documentation](https://docs.rkeeper.ru/rk7/latest/ru/podderyoivaemye-drajvery-vesov-10819223.html)

---

## Protocol Family 6: DIBAL EPOS TISA (Bidirectional Price)

### Wire Protocol (from rkeeper `s_dibal.dll`)

**Price injection + weight response:**

```
Hub → Scale:  '98' + [5-digit price] + [XOR] + CR + LF
Scale → Hub:  [18 bytes: '99' + '0' + 5-digit weight + ... + XOR + CR + LF]
```

Example: Hub sends price 1.23 → `98 00123 [XOR] CR LF`
Scale responds with weight → `99 0 01232 ... [XOR] CR LF`

**Hub Adapter:** `dibal.py` — **Classification:** Tier 2+ (price inject, no PLU name)

**Source:** [rkeeper Documentation](https://docs.rkeeper.ru/rk7/latest/ru/podderyoivaemye-drajvery-vesov-10819223.html)

---

## Protocol Family 7: Acom (RS-232 + Ethernet)

### Models

- **Acom NETS** — Label printing scale (RS-232 + TCP/IP)
- **Acom PC** — Price computing scale (RS-232 + TCP/IP)

Both support PLU programming via their respective protocols.

**Hub Adapter:** `acom.py` — **Classification:** Tier 1

**Source:** [Scale-Soft.com — Acom NETS](https://scale-soft.com/acom_nets.htm), [Scale-Soft.com — Acom PC](https://scale-soft.com/acom_pc.htm)

---

## Protocol Family 8: МАССА-К / Massa-K (RS-232 + Ethernet)

### Models

| Model | Category | PLU Upload | Interface |
|---|---|---|---|
| МАССА-К ВПМ | Label printing | Yes | RS-232 + TCP/IP |
| МАССА-К ВП (Ф/Т) | Label printing | Yes | RS-232 + TCP/IP |
| МАССА-К (basic) | Simple scale | No (weight only) | RS-232 |

Russian-manufactured scales, widely used in Eastern Europe. ВПМ/ВП models are Tier 1, basic models are Tier 2.

**Hub Adapter:** `massa_k.py` — **Classification:** Tier 1 (ВПМ/ВП) / Tier 2 (basic)

**Source:** [Scale-Soft.com — МАССА-К](https://scale-soft.com/massa-k_vpm.htm)

---

## Protocol Family 9: Other Verified Protocols

| Scale | Protocol | Interface | Classification | Source |
|---|---|---|---|---|
| МЕРА (Mera) | OKA / 9-byte / MW | RS-232 | Tier 1 | [Scale-Soft.com](https://scale-soft.com/mera.htm) |
| Тензо-М ТВ | Protocol 6.43 | RS-232 | Tier 1 | [Scale-Soft.com](https://scale-soft.com/tenso-m_tv.htm) |
| Ohaus NVT3201/2 | Continuous ASCII | RS-232 | Tier 2 | [rkeeper](https://docs.rkeeper.ru/rk7/latest/ru/podderyoivaemye-drajvery-vesov-10819223.html) |
| SHTRIH-SLIM 200M | Binary command | RS-232 | Tier 2 | [rkeeper](https://docs.rkeeper.ru/rk7/latest/ru/podderyoivaemye-drajvery-vesov-10819223.html) |
| KB-TBED-3000 | Continuous ASCII | RS-232 | Tier 2 | [rkeeper](https://docs.rkeeper.ru/rk7/latest/ru/podderyoivaemye-drajvery-vesov-10819223.html) |

---

## Adapter Priority for EU Direct Sales Market

| Priority | Scale Family | Tier | Why |
|---|---|---|---|
| **P0** | CAS ER-Plus | Tier 2 | Lowest cost entry, our pilot hardware |
| **P1** | CAS LP-1 / LP-II | Tier 1 | Full PLU sync, same manufacturer, EU-certified |
| **P2** | CAS CL5000 / CL5200 | Tier 1 | Larger operations, Ethernet networking |
| **P3** | DIGI SM-5300 | Tier 1 | EU-LEH market leader, Ethernet |
| **P4** | Mettler Toledo Tiger | Tier 1 | Premium segment, richest protocol |
| **P5** | DIBAL | Tier 2+ | Price inject capability, common in Spain/Portugal |

---

## Tier 2 Price Synchronization: Technical Options

When a farmer changes prices in Odoo, Tier 2 scales (CAS ER-Plus, basic bench scales) **cannot receive PLU updates via RS-232**. This section documents the available technical solutions.

### Option A: Hub Price Display (Recommended for Phase 1)

The Hub provides a **local web dashboard** (on a small HDMI or e-ink display connected to the Pi, or accessible via smartphone/tablet on the local network) showing the current Odoo price list:

```
┌─────────────────────────────────────┐
│  Preisänderungen (aktualisiert 08:15) │
│                                       │
│  PLU  Produkt           Preis/kg     │
│  ─── ─────────────────  ──────────   │
│  M1   Rindfleisch       €18.90  ✓   │
│  M2   Schweinefleisch   €12.50  ✓   │
│  M3   Lammkeule       → €24.90  ★   │ ← Changed
│  M4   Honig (500g)      €8.90   ✓   │
│                                       │
│  ★ = Neue Preise — bitte an Waage    │
│      eingeben                         │
└─────────────────────────────────────┘
```

**How it works:**
1. Farmer updates price in Odoo (ERP/POS)
2. Hub receives price update via API
3. Hub displays change notification on local dashboard
4. Hub highlights which PLUs need manual update
5. Farmer enters new price on scale keyboard
6. Hub verifies: if incoming weight × expected price/kg ≠ scale's calculated total → warning

**Advantages:**
- No additional hardware beyond a phone/tablet
- Works immediately with any Tier 2 scale
- Odoo remains the single source of truth
- Verification catches discrepancies

**Disadvantages:**
- Requires manual price entry on scale
- Human error possible (typos)

### Option B: Barcode-Triggered Price Recall

If the farmer uses **pre-printed PLU barcodes** (e.g., on a laminated card):

```
┌──────────────────────────────────────┐
│  [Scan PLU barcode or type PLU#]      │
│                                       │
│  PLU 3: Lammkeule                     │
│  Aktueller Preis in Odoo: €24.90/kg  │
│  Preis auf Waage:         €22.90/kg  │
│  ⚠ ABWEICHUNG — bitte aktualisieren  │
│                                       │
│  [Bestätigt ✓]  [Später]              │
└──────────────────────────────────────┘
```

The Hub can read a USB barcode scanner input, look up the PLU in Odoo, and display the current price. The farmer confirms or updates the scale manually.

### Option C: Scale Upgrade Path (Tier 2 → Tier 1)

For farmers who frequently change prices, the Hub can be paired with a Tier 1 scale:

| Current Scale | Upgrade To | Investment | Benefit |
|---|---|---|---|
| CAS ER-Plus (€200–400) | CAS LP-1 (€600–900) | +€400–500 | Full automatic PLU sync |
| CAS ER-Plus (€200–400) | CAS CL5200 (€1,500+) | +€1,100+ | Ethernet + 10k PLUs |

### Option D: Hub as Virtual Printer + Price Verification (Recommended for Phase 2)

The Hub acts as a **DEP-50/DLP-50 virtual printer**, receiving the ER-Plus print data stream after each weighing. It then:

1. **Captures** weight, price/kg, total from the printer data
2. **Compares** against the Odoo-stored price for that PLU
3. **Alerts** if there is a mismatch (configurable: warn or block label printing)
4. **Prints** the correct label on the Zebra printer with all LMIV-compliant fields

```
CAS ER-Plus ──[RS-232: print data]──→ Hub (virtual DEP-50)
                                         │
                                         ├── Compare with Odoo price
                                         │   └── Mismatch? → Alert on dashboard
                                         │
                                         ├── Print label on Zebra (LMIV-compliant)
                                         │
                                         └── Forward to Odoo POS
```

This is the strongest Tier 2 solution because the Hub validates every single transaction.

### Option E: External PLU Management via ES-Works / ER-Works

CAS provides **ES-Works** (also called ER-Works) software for PLU management on ER-series scales. This Windows application connects via RS-232. In theory, the Hub could implement the ES-Works protocol to upload PLUs.

**Status:** Protocol not publicly documented. Would require reverse engineering or CAS partnership. **Not recommended for Phase 1.**

### Option F: Hub as Certified Price Calculator — "Tier 0" (Recommended Long-Term)

The Hub takes over **all** price calculation. The scale becomes a pure weight sensor.

```
┌───────────────┐     ┌──────────────────────────────────────────────┐
│  ANY certified │     │  Hub (Raspberry Pi) — CERTIFIED CORE         │
│  weight scale  │     │                                              │
│                │     │  1. Receive weight_g (integer)               │
│  €50–200       │────►│  2. Look up product → price_cents_per_kg     │
│  OIML Class III│     │  3. total_cents = weight_g * price / 1000    │
│  RS-232 or USB │     │  4. Display on screen (customer-facing)      │
│                │     │  5. Print LMIV-compliant label               │
│  • Weight only │     │  6. Forward to Odoo POS                      │
│  • No PLU      │     │  7. Log in audit chain                       │
│  • No price    │     │                                              │
│  • No display  │     │  Certified Core = Steps 1–4 + 7              │
│    needed      │     │  Uncertified Periphery = Steps 5–6           │
└───────────────┘     └──────────────────────────────────────────────┘
```

**Why this is the best long-term architecture:**

1. **Maximum scale compatibility:** ANY OIML-certified weight scale works — no PLU protocol needed, no specific manufacturer, no RS-232 printer emulation hacks. Even a €50 platform scale with USB output.

2. **Single source of truth for prices:** Odoo is the ONLY place where prices live. No sync, no mismatch, no manual entry, no verification needed. Change a price in Odoo → next weighing uses the new price.

3. **Lowest farmer complexity:** The farmer only needs to: put product on scale, select product on screen (or scan barcode), confirm. No programming scales, no PLU codes, no ASCII input.

4. **Cheapest entry point:** Scale (€50–100) + Hub (€150) + Zebra printer (€200) = **€400–450 total** for a fully compliant labeling system.

5. **Full control over UX:** Weight display, product selection, price display, label preview — all on the Hub's screen. The scale is invisible infrastructure.

#### What the Hub needs for this (Development)

**Certified Core (frozen after certification, ~500 lines of code):**

| Component | Purpose | Complexity |
|---|---|---|
| `weight_reader.py` | Read stable weight from scale adapter (integer grams) | Low |
| `price_calculator.py` | `total = weight_g × price_cents_per_kg // 1000` | Trivial |
| `display_output.py` | Show weight + price on customer-facing display | Low |
| `consistency.py` | Ensure weight/price/total match across all outputs | Medium |
| `audit_writer.py` | Append-only, hash-chained JSONL log | Medium |
| `core_api.py` | Expose `GET /weight`, `POST /calculate`, `GET /verify` | Low |

Total estimated Certified Core: **~500 lines Python**, highly testable, rarely changes.

**Uncertified Periphery (freely updatable):**

| Component | Purpose | Changes often? |
|---|---|---|
| Scale adapters (CAS AP, USB HID, etc.) | Parse weight from different scales | Occasionally |
| Label engine (ZPL, GS1 QR) | Generate LMIV-compliant labels | Yes |
| Odoo sync | Product catalog, prices, PLU mapping | Yes |
| Compliance YAML loader | Country-specific label rules | Yes |
| Web dashboard | Product selection UI, operator interface | Yes |
| OTA updater | Signed updates for periphery | Rarely |

#### Certification Path

| Step | Duration | Cost | Description |
|---|---|---|---|
| 1. Core Architecture Freeze | 2 weeks | €0 | Finalize Certified Core boundary, interfaces, test suite |
| 2. Formal Test Suite | 4 weeks | €0 | 100% branch coverage on Core, property-based tests for price calc |
| 3. Documentation Package | 2 weeks | €0 | WELMEC 7.2 compliance matrix, software architecture doc, risk analysis |
| 4. Select Notified Body | 2 weeks | €0 | Contact BEV (AT) or PTB (DE) for "Prüfzeugnis" |
| 5. Pre-Assessment | 4 weeks | €2–5k | Notified Body reviews architecture + documentation |
| 6. Type Examination | 8–16 weeks | €8–20k | Formal testing of Certified Core against WELMEC 7.2 |
| 7. Certificate Issued | — | — | "Baumusterprüfbescheinigung" for Hub + scale combination |
| **Total** | **~6 months** | **€10–25k** | |

**Re-certification:** Only needed when the Certified Core changes. Periphery updates (labels, Odoo, dashboard) do NOT trigger re-certification — this is the key architectural advantage.

#### Legal Classification After Certification

| Aspect | Before Certification | After Certification |
|---|---|---|
| Hub legal status | "Non-legally relevant" (WELMEC §5.3) | "Zusatzeinrichtung" (ancillary device) with Prüfzeugnis |
| Price calculation | Scale only (Decision 01) | Hub (certified) or Scale (both valid) |
| Compatible scales | Only price-computing scales | ANY OIML Class III weight scale |
| WELMEC compliance | Argumentative (Decisions 01–07) | Formally certified |
| BEV defensibility | Good (architecture-based) | **Bulletproof** (certificate) |
| Market positioning | "Open source bridge" | **"Certified metrological system"** |

#### Customer-Facing Display Requirement

When the Hub calculates the price, the **customer must be able to see** weight, price/kg, and total — this is a legal requirement (Preisauszeichnungsgesetz, NAWI Art. 12). Options:

| Display Option | Cost | Description |
|---|---|---|
| 7" HDMI touchscreen | €30–50 | Mounted near scale, shows weight + price + product |
| 10" tablet (web app) | €100–150 | Hub serves a local web page, customer-facing |
| E-ink display | €40–60 | Low-power, always-on, perfect for outdoor markets |
| Dual-screen (operator + customer) | €80–100 | Operator selects product, customer sees result |

**Recommended:** 7" HDMI touchscreen (€35) — connects directly to Pi, no network needed, works at outdoor markets without WiFi.

#### Risk Analysis

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Certification takes longer than expected | Medium | High (delays launch) | Start with Tier 2 (no certification), add Tier 0 later |
| Certification costs more than estimated | Low | Medium | Certified Core is <500 LOC → small audit scope |
| BEV rejects architecture | Low | High | Pre-assessment (Step 5) catches issues before formal test |
| Re-certification needed on Core change | Low | Medium | Core is designed to be frozen — changes are extremely rare |
| Customer display adds complexity | Low | Low | Off-the-shelf HDMI display, no custom hardware |

### Comparison Matrix

| Option | Auto Sync | Hardware Cost | Complexity | Certification | Phase |
|---|---|---|---|---|---|
| A: Hub Price Display | Manual + verified | €0 (phone/tablet) | Low | No | **Phase 1** |
| B: Barcode Recall | Manual + assisted | €30 (USB scanner) | Medium | No | Phase 1 |
| C: Scale Upgrade | Fully automatic | €400–1,500+ | Low (new adapter) | No | Any time |
| D: Virtual Printer | Auto-verified | €0 | Medium–High | No | Phase 2 |
| E: ES-Works Protocol | Potentially auto | €0 | High (reverse eng.) | No | Future |
| **F: Hub Price Calc** | **Fully automatic** | **€35 (display)** | **Medium** | **Yes (€10–25k)** | **Phase 3** |

---

## Verification Sources

| Source | URL | Verified | Content |
|---|---|---|---|
| rkeeper RK7 — Supported Scale Drivers | [docs.rkeeper.ru](https://docs.rkeeper.ru/rk7/latest/ru/podderyoivaemye-drajvery-vesov-10819223.html) | 2026-03-22 | Byte-level protocol for CAS, DIGI, DIBAL, Mettler Toledo, Ohaus, SHTRIH, KB-TBED |
| Scale-Soft.com — Scale Drivers | [scale-soft.com](https://scale-soft.com/) | 2026-03-22 | Driver capabilities for CAS LP/CL/AP/DB-II, DIGI SM, Mettler Toledo Tiger, Acom, МАССА-К, МЕРА, Тензо-М |
| LavrSoft / cas-lp.narod.ru | [cas-lp.narod.ru](https://cas-lp.narod.ru/) | 2026-03-22 | CAS LP/CL5000 universal driver, protocol version info (v1.5/v1.6) |
| zipstore.ru — CAS LP Protocol | [zipstore.ru](https://zipstore.ru/auxpage_1c_protocol_interface_cas_lp_scale/) | 2026-03-22 | Full binary PLU data structure, commands, smart-sync |
| CAS ER-Plus User Manual | [casscale.com.au (PDF)](https://www.casscale.com.au/wp-content/uploads/CAS-ER-PLUS-User-Manual.pdf) | 2026-03-22 | RS-232 = printer port (DEP-50/DLP-50), 200 PLUs, manual programming |
| CAS PD-II Manual | [ManualsLib](https://www.manualslib.com/manual/972542/Cas-Pd-Ii.html) | 2026-03-22 | ECR serial parameters: 9600/7/E/1, TYPE 0–6 |
