# Scale Hub — Label Guide

> **Status:** v1.0 · 2026-03-21
> **Product Page:** [architecture.html](architecture.html)
> **Technical Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
> **Legal Register:** [LEGAL_REGISTER.md](LEGAL_REGISTER.md)

---

## Overview

The Scale Hub supports four labeling scenarios. Each product in Odoo is assigned to one scenario. The Hub automatically validates mandatory fields and generates the correct label — or no label at all.

If mandatory fields are missing, the Hub rejects the print request (HTTP 422) before a wrong label can be printed.

---

## Scenarios at a Glance

### 1. Farmers Market — Loose Goods

**When:** Selling unpackaged produce directly to the customer (market stand, farm gate).

**What happens:**
- The scale displays weight and price — that's the legally binding information
- No label is printed
- Allergen information is given verbally (in Austria; written in some other EU countries)
- Optionally: a receipt from the POS system

**Mandatory label fields:** None (no label)

**Legal basis:** EU Food Information Regulation (1169/2011) Art. 44 — member states regulate loose goods individually. Austrian allergen regulation allows verbal communication.

---

### 2. Farm Shop — Simple Prepack

**When:** Single-ingredient products sold pre-packaged: honey, fruit, vegetables, eggs, cheese wheels.

**Label size:** 60 × 40 mm

**What's on the label:**
- Product name
- Net weight
- Price (per kg and total)
- Best before date
- Country / region of origin
- Producer name and address
- Lot number
- QR code (links to product page or shop)

**What's NOT required:**
- Ingredient list (single-ingredient products are exempt)
- Nutrition declaration (direct sellers with <2M annual turnover are exempt under Annex V Nr. 19)

**Legal basis:** EU FIC Reg. 1169/2011 Art. 9 · Annex V Nr. 19 (nutrition exemption) · GS1 Digital Link

---

### 3. Packing Station — Full Prepack

**When:** Processed or multi-ingredient products: jam, juice, spreads, dried herbs, sauces, smoked meat.

**Label size:** 80 × 60 mm

**What's on the label:**
- Everything from Simple Prepack, plus:
- Full ingredient list (in descending order of weight)
- Allergens highlighted in bold (EU FIC Art. 21)
- Storage instructions ("Keep refrigerated after opening")
- QR code

**What's NOT required:**
- Nutrition declaration (if direct seller with <2M turnover)
- EAN barcode (not needed for direct sales)

**Legal basis:** EU FIC Reg. 1169/2011 Art. 9, 18, 21 · Annex V Nr. 19

---

### 4. Retail Supply — Retail Prepack

**When:** Supplying supermarkets (Spar, Billa, Hofer, ADEG, Lidl, etc.) or selling through retail channels.

**Label size:** 100 × 70 mm

**What's on the label:**
- Everything from Full Prepack, plus:
- **Nutrition declaration** ("Big Seven"): energy (kJ/kcal), fat, saturated fat, carbohydrates, sugars, protein, salt — per 100g
- **EAN-13 barcode** (for retailer cash registers)
- **GS1 Digital Link QR code** (for traceability and consumer info)
- Lot number (mandatory for retailer traceability)

**Why nutrition is mandatory here:** The Annex V Nr. 19 exemption applies only to direct sales by the manufacturer. Once a product enters the retail supply chain, the full nutrition declaration is required.

**Dual Barcode Strategy:** Both EAN-13 and QR code are printed on the label. Today's supermarket scanners read EAN-13. By 2027 (GS1 Sunrise), QR codes will be scannable at checkout. The Hub is ready for both.

**Legal basis:** EU FIC Reg. 1169/2011 Art. 9, 30 (nutrition) · EU Reg. 178/2002 Art. 18 (traceability) · GS1 General Specifications v24

---

## Mandatory Fields by Scenario

| Field | Loose | Simple Prepack | Full Prepack | Retail Prepack |
|---|:---:|:---:|:---:|:---:|
| Product name | — | ✓ | ✓ | ✓ |
| Net weight | — | ✓ | ✓ | ✓ |
| Price | — | ✓ | ✓ | ✓ |
| Best before date | — | ✓ | ✓ | ✓ |
| Origin | — | ✓ | ✓ | ✓ |
| Producer name + address | — | ✓ | ✓ | ✓ |
| Lot number | — | ✓ | ✓ | ✓ |
| Ingredient list | — | — | ✓ | ✓ |
| Allergens (bold) | — | — | ✓ | ✓ |
| Storage instructions | — | — | ✓ | ✓ |
| Nutrition (Big Seven) | — | — | — | ✓ |
| EAN-13 barcode | — | — | — | ✓ |
| QR code (GS1 Digital Link) | — | optional | optional | ✓ |

---

## How It Works in Practice

### In Odoo

Each product in Odoo has a `label_scenario` field with four options:
- `LOOSE` — no label printed
- `SIMPLE_PREPACK` — basic label
- `FULL_PREPACK` — full label with ingredients
- `LEH_PREPACK` — retail-grade label with nutrition + EAN

The product master data also contains: origin, allergens, ingredients, shelf life, storage instructions, and (for retail) the nutrition "Big Seven" values.

### On the Hub

When a sale is completed:
1. Hub receives sale data from the scale (weight, price, PLU)
2. Hub looks up the product in its local PLU map
3. Hub loads the label profile for the product's scenario
4. Hub validates all mandatory fields against the profile
5. If valid → generates ZPL and sends to the Zebra printer
6. If invalid → returns HTTP 422 with a list of missing fields

### Country-Specific Rules

The Hub loads a `compliance.yaml` for the configured country. This file defines:
- Which fields are mandatory per scenario
- How allergens must be displayed (bold, separate line, etc.)
- Whether nutrition is required for direct sellers
- Cash register thresholds and requirements
- GS1 requirements

See [legal/COMPLIANCE_MATRIX.md](legal/COMPLIANCE_MATRIX.md) for the EU-wide status.

---

## Technical Implementation

The label engine is implemented in:

- `infrastructure/scale_hub/app/utils/label_profiles.py` — scenario enum, profile definitions, validation
- `infrastructure/scale_hub/app/utils/zpl.py` — ZPL II generation with Jinja2 templates
- `infrastructure/scale_hub/app/main.py` — FastAPI endpoint `/label/zpl`
- `infrastructure/scale_hub/tests/test_label_profiles.py` — unit tests for all scenarios

The Odoo product fields are in:

- `addons/groundup_scale_bridge/models/scale_plu.py` — PLU model with LMIV fields
- `addons/groundup_scale_bridge/models/scale_device.py` — device model with `country_code`
