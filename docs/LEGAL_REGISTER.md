# Scale Hub — Legal Register & Architecture Decisions

> **Status:** v4.0 · 2026-03-22
> **Maintainer:** Ground UP GmbH · FN 481220 b
> **Product Page:** [architecture.html](architecture.html)
> **Technical Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
> **Protocol Catalog:** [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md)
> **Label Guide:** [LABEL_GUIDE.md](LABEL_GUIDE.md)

---

## 1. Applicable Regulations

| Regulation | Scope | Relevance for Scale Hub |
|---|---|---|
| **Directive 2014/31/EU** (Non-automatic weighing instruments) | Defines regulated weighing instruments | CAS ER-Plus is regulated; Hub and POS are not |
| **Directive 2014/32/EU** (Measuring instruments) | Automatic weighing instruments | Does not apply — CAS ER-Plus is non-automatic |
| **Austrian Metrology Act** (MEG, BGBl. Nr. 152/1950) | National implementation of weighing regulations | Hub does not determine prices → not subject to verification |
| **WELMEC 7.2** (Software Guide for Measuring Instruments) | De facto standard for software assessment | Hub classified as "non-legally relevant" under §5.3 |
| **EN 45501** (Metrological aspects of NAWIs) | Harmonized standard for weighing instruments | CAS ER-Plus must comply; Hub does not |
| **EU Food Information Regulation** (1169/2011) | Mandatory information on food labels | Defines what must appear on each label — see [LABEL_GUIDE.md](LABEL_GUIDE.md) |
| **EU Traceability Regulation** (178/2002, Art. 18) | One step forward, one step back | QR code + lot number enable full traceability |
| **GS1 General Specifications v24** | Barcode and Digital Link standards | QR codes on labels follow GS1 Digital Link format |
| **Austrian Cash Register Regulation** (RKSV, BGBl. II Nr. 410/2015) | Tamper-proof receipts | Odoo POS must be RKSV-compliant (not the Hub) |
| **Austrian Cold Hands Rule** (BAO §131b) | Cash register exemption for outdoor markets | Below €45k net at outdoor markets → no cash register required |
| **BEV Information Sheet on POS Systems** (2023, Version 02) | When a POS system requires certification | Our architecture avoids the POS-scale direct connection that triggers certification |
| **CE Marking** (EMV 2014/30, LVD 2014/35, RED 2014/53, RoHS 2011/65) | Product safety for electronic devices | Hub needs EU Declaration of Conformity — EMV test if custom enclosure |
| **Packaging Directive** (76/211/EEC + FIC Art. 23) | Net quantity on pre-packed goods | Mandatory weight/volume display, tolerances, ℮-symbol for fixed-weight |
| **Product Liability Directive** (EU) 2024/2853 | Liability for defective products incl. software | Hub software is explicitly a "product" — audit log as forensic evidence |
| **FIC Art. 13 + Annex IV** (Min. font size) | Readability of mandatory information | x-height ≥ 1.2 mm (≥ 0.9 mm for labels < 80 cm²) |
| **FIC Art. 21 + Annex II** (Allergen highlighting) | Allergens must stand out in ingredient list | CAPS or bold in ZPL — auto-highlighting in label engine |
| **FIC Art. 30–35 + Annex XV** (Nutrition declaration) | Big Seven format and rounding rules | Mandatory for LEH_PREPACK; exempt for direct sales (Annex V Nr. 19) |
| **GDPR** (EU) 2016/679 | Protection of personal data | Operator IDs in audit log = personal data → pseudonymization |
| **WEEE Directive** 2012/19/EU | E-waste registration and take-back | Hub must be registered (ERA in AT) before placing on market |

Full legal excerpts are in [legal/](legal/) — organized by `eu/` (EU-wide) and `{iso2}/` (country-specific).

---

## 2. Architecture Decisions

Each decision documents **why** we built the Hub the way we did — and which regulation supports it.

---

### Decision 01: The Scale is the Single Source of Truth

- **Status:** Accepted
- **Context:** It would be technically possible to calculate prices in the POS or Hub. However, the European Software Guide (WELMEC 7.2 §4.2) defines a "terminal" as any digital device with input capability that operates the measuring instrument. If the POS calculates prices, it becomes a terminal — and requires certification.
- **Decision:** All price calculations happen exclusively in the certified scale. Hub and POS are pure pass-through systems.
- **Consequence:** No certification required for Hub or POS. Trade-off: discounts cannot be calculated live in the POS during a weighed sale.
- **Sources:** Directive 2014/31/EU Art. 1(2)(a) · WELMEC 7.2 §4.2 · MEG §8(1)

---

### Decision 02: Protocol-Level Command Separation (Single RS-232 Port)

- **Status:** Accepted (corrected 2026-03-22 — previously assumed dual-port, which was incorrect)
- **Context:** WELMEC §4.4.2.1 requires protection against unauthorized influence via communication interfaces. Most retail scales (CAS ER-Plus, LP, AP, etc.) have a **single optional RS-232 port**. Physical port separation is not available.
- **Decision:** Integrity is ensured through **logical separation at the protocol level**:
  1. **Allowlist** (Decision 03): Only documented, pre-approved commands are sent
  2. **State machine** (Decision 06): Configuration changes are blocked during active transactions
  3. **Audit log** (Decision 04): Every command sent and received is logged with hash chain
  4. **Secure Boot** (Decision 07): Hub software cannot be modified in the field
  5. For **Tier 2 scales** (CAS ER-Plus): The RS-232 data flow is effectively unidirectional (Scale → Hub as virtual printer), which is the strongest compliance argument
- **Consequence:** Single USB-RS232 adapter per scale. Compliance rests on the combination of Decisions 03, 04, 06, 07 rather than physical wire separation.
- **Sources:** WELMEC 7.2 §4.4.2.1(a)(b) · CAS ER-Plus User Manual (RS-232 = printer port)

---

### Decision 03: Allowlist-Only for PLU Commands

- **Status:** Accepted
- **Context:** WELMEC requires that only documented commands may be sent via interfaces; unknown commands must have no effect on legally relevant functions.
- **Decision:** The Hub only accepts `product_id` values from a pre-configured allowlist. Free PLU numbers, prices, or control commands from the POS are technically prevented.
- **Consequence:** New products must be configured in the PLU map before they can be selected.
- **Sources:** WELMEC 7.2 §4.4.2.1(b)

---

### Decision 04: Hash-Chained Append-Only Audit Log

- **Status:** Accepted
- **Context:** WELMEC requires protection of legally relevant software and measurement data, including traceability (audit trail).
- **Decision:** All events are stored as JSONL with SHA-256 hash chain. No updates, no deletions. Verification via `/audit/verify` endpoint.
- **Consequence:** Log grows monotonically. Optional: daily export + RDDL blockchain anchoring.
- **Sources:** WELMEC 7.2 §4.5

---

### Decision 05: QR Code Supplements, Never Replaces

- **Status:** Accepted
- **Context:** Both metrology law and food labeling law require that weight and price are clearly human-readable on the label.
- **Decision:** Every label always contains human-readable weight, price/kg, and total price. The QR code is additional, non-legally-binding information. For retail: EAN-13 + QR code (dual barcode strategy).
- **Sources:** GS1 Digital Link v1.6 §4 · EU FIC Regulation 1169/2011 Art. 8, 23

---

### Decision 06: PLU Sync Separated from Active Sales

- **Status:** Accepted
- **Context:** Price changes during an active sale transaction would create inconsistent data.
- **Decision:** PLU/price updates are only accepted when the Hub is in `IDLE` state. During active transactions, configuration changes are rejected.
- **Sources:** WELMEC 7.2 §4.4.2.1(a) · Directive 2014/31/EU Annex III Nr. 8.2

---

### Decision 07: Secure Boot from Device #1

- **Status:** Accepted
- **Context:** WELMEC 7.2 §4.3 requires protection of legally relevant software against unauthorized modification. The credibility of the Hub as a "non-manipulable pass-through system" depends on the impossibility of modifying its software. **Critical:** The CM4/Pi 5 OTP fuse for the boot signing key is irreversible. Devices without Secure Boot cannot be retrofitted in the field.
- **Decision:** Secure Boot is activated from the very first device:
  1. Boot ROM: RSA-2048 public key hash burned into OTP
  2. Bootloader: Signed boot.img + config.txt
  3. Root filesystem: dm-verity (read-only squashfs)
  4. Application: Signed Docker images + AppArmor profiles
  5. Updates: A/B partition scheme + signed OTA packages
- **Consequence:** Every device from unit #1 is tamper-protected. No root access in the field. Updates only via signed OTA.
- **Sources:** WELMEC 7.2 §4.3, §4.5 · Raspberry Pi CM4/Pi 5 OTP Boot Signing

---

### Decision 08: Hub Certification Not Required (Phase 1)

- **Status:** Accepted
- **Context:** Full certification costs €50–200k and takes 6–18 months. The BEV Information Sheet on POS Systems confirms: directly connecting a scale to a cash register system for price determination requires a test certificate and re-verification with every software change. Our architecture deliberately avoids this definition.
- **Decision:** Phase 1 operates without formal certification. The architecture (Decisions 01–07) + Secure Boot make the classification as "non-legally relevant" defensible.
- **Phase 2 (Market Product):** A test certificate (Hub + POS + Scale) would be a competitive advantage. Estimated effort: €50–100k + 6–12 months. Evaluation from Q4/2026 based on market feedback.
- **Sources:** WELMEC 7.2 §5.3 · BEV Information Sheet POS Systems 2023

---

### Decision 09: Scenario-Based Labeling

- **Status:** Accepted
- **Context:** The EU Food Information Regulation distinguishes between loose and pre-packaged goods. National special rules apply (e.g., Austrian "cold hands" cash register exemption, verbal vs. written allergen information). The Hub must automatically generate the correct label — or no label — for different selling situations.
- **Decision:** Four label scenarios, configured per product in Odoo:
  - **Loose** — farmers market: no label, scale displays information
  - **Simple Prepack** (60×40mm) — single-ingredient products: name, weight, price, best before, origin, producer
  - **Full Prepack** (80×60mm) — processed products: + ingredients, allergens (bold), storage instructions
  - **Retail Prepack** (100×70mm) — supermarket supply: + nutrition declaration (Big Seven), EAN-13 + GS1 Digital Link QR, lot number
- **Consequence:** The farmer selects only the product in the POS; the Hub automatically determines which label to print. Mandatory fields are validated per scenario — missing fields result in HTTP 422, no label is printed.
- **Sources:** EU FIC Reg. 1169/2011 Art. 9, 44, Annex V Nr. 19 · GS1 Sunrise 2027

See [LABEL_GUIDE.md](LABEL_GUIDE.md) for the full scenario documentation.

---

### Decision 10: Country-Specific Compliance Architecture

- **Status:** Accepted
- **Context:** The EU FIC Regulation applies EU-wide, but many details (allergen information for loose goods, cash register requirements, price display rules) are regulated nationally. For an EU-wide rollout, the Hub must be configurable per country — without code changes.
- **Decision:** Three-layer architecture:
  1. **EU Layer** (`legal/eu/`): EU law applies identically everywhere
  2. **National Layer** (`legal/{iso2}/`): Country-specific legal texts + machine-readable `compliance.yaml`
  3. **Hub Runtime**: Loads `compliance.yaml` for the configured country (`country_code` on `groundup.scale.device`) and validates mandatory fields accordingly
- **compliance.yaml schema:** Labeling (mandatory fields per scenario, allergen display, nutrition requirements), cash register (thresholds, system), metrology (authority, verification intervals), GS1, VAT rates on food.
- **Agent Monitoring:** Each YAML has `last_review` / `next_review` fields. The Jóska Compliance Agent monitors regulatory sources and creates GitHub issues when changes are detected.
- **Scope:** EU-27 + Switzerland. Austria fully researched; others as placeholders with `null` values.
- **Consequence:** New country = fill in a new `compliance.yaml` + write legal texts. No code change on the Hub required.
- **Sources:** EU FIC Reg. 1169/2011 Art. 44 · Country-specific texts in `legal/{iso2}/` · [COMPLIANCE_MATRIX.md](legal/COMPLIANCE_MATRIX.md)

---

### Decision 11: Certified Core + Uncertified Periphery

- **Status:** Proposed (Phase 2)
- **Context:** Full certification of the entire Hub (all software, label engine, compliance logic, Odoo integration) would mean re-certification with every update. This is prohibitively expensive and slow. The BEV certifies systems as "Waage im Verbund mit Kassensystem" — but only the data path between scale and POS is metrologically relevant.
- **Decision:** Split the Hub into two architectural zones:
  1. **Certified Core** (rarely changes): Serial I/O driver, data pass-through, integer validation, audit log writer, API gateway. This is the part that handles weight and price data.
  2. **Uncertified Periphery** (frequently changes): Label engine, compliance YAML loader, GS1 QR generator, Odoo sync, web dashboard. These components never touch metrologically relevant calculations.
- **Consequence:** Only the Certified Core requires re-certification on change. The periphery can be updated freely. Estimated certification cost for Core only: €10–25k (vs. €50–100k for full system).
- **Sources:** WELMEC 7.2 §5.3 · BEV POS-Systeme 2023

---

### Decision 12: Scale Adapter Pattern for Multi-Vendor Support

- **Status:** Accepted
- **Context:** The Hub must support multiple scale manufacturers (CAS, Bizerba, Mettler-Toledo, DIGI) without architectural changes. Each scale family has a different serial protocol.
- **Decision:** Each scale type implements a `ScaleAdapter` protocol with standardized methods: `parse_sale_data()`, `send_plu_select()`, `get_status()`. The Hub Core validates a generic `SaleData` structure (integer grams, integer cents) regardless of which adapter produced it.
- **Consequence:** Adding a new scale = writing one adapter module + testing. No changes to Core, label engine, or Odoo integration needed.
- **Sources:** Clean Architecture (Robert C. Martin) · WELMEC 7.2 §4.4 (interface protection applies per adapter)

---

### Decision 13: Three-Way Consistency Verification

- **Status:** Accepted
- **Context:** An auditor needs to verify that weight and price are identical across the scale display, the printed label, and the POS record. Any discrepancy — even due to rounding — is a violation.
- **Decision:** Five-layer consistency guarantee:
  1. **Raw data preservation:** Store original bytes from the scale verbatim.
  2. **Integer arithmetic only:** Grams and cents throughout — no floating point.
  3. **Pre-output comparison:** Before printing/sending, compare scale data, label payload, and POS payload. Abort on any mismatch.
  4. **Consistency hash:** SHA-256 of (weight_g, price_cents, plu_id, timestamp) embedded in audit log, label QR, and POS payload.
  5. **Verification endpoint:** `GET /verify/{sale_id}` shows all three data paths side-by-side for auditors.
- **Consequence:** Bit-exact consistency is mathematically guaranteed. Rounding errors are impossible (integer arithmetic). Hash mismatch = tampering evidence.
- **Sources:** WELMEC 7.2 §4.5 · EN 45501 §T.4.4 · BEV POS-Systeme 2023

---

### Decision 14: Scale Tier Classification and Adapter Pattern

- **Status:** Accepted
- **Context:** The Hub must support scales from multiple manufacturers with fundamentally different communication protocols — from full bidirectional PLU management (CAS LP, DIGI SM) to simple weight-read-only (CAS ER-Plus, basic bench scales). A single protocol assumption would limit market reach. Research verified 9+ distinct protocol families across 30+ scale models (see [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md)).
- **Decision:** Three-tier classification:
  - **Tier 1 — Full integration:** Scale supports PLU upload/download via RS-232 or Ethernet. Hub manages PLUs from Odoo automatically. Models: CAS LP/CL, DIGI SM, Mettler Toledo Tiger, Acom, МАССА-К ВПМ/ВП, МЕРА.
  - **Tier 2 — Weight/price read-only:** Scale has no PLU upload capability. Hub receives weight/price data (via AP protocol or virtual printer). Price changes require manual entry on scale. Models: CAS ER-Plus, CAS AP/AD/DB/EB/ED/HB/HD/PB/PDC/PDI/SW/SWN, PR LCD.
  - **Tier 2+ — Bidirectional price:** Scale accepts price injection but not PLU names. Models: DIBAL (EPOS TISA protocol).
  Each tier maps to a `ScaleAdapter` implementation with the same output interface (`SaleData` with integer grams + integer cents).
- **Consequence:** The Hub Core, label engine, and Odoo integration are tier-agnostic. Adding a new scale = one adapter module + tests. Tier limitations are transparently documented to the farmer during onboarding.
- **Sources:** [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md) · [Scale-Soft.com](https://scale-soft.com/) · [rkeeper RK7 Documentation](https://docs.rkeeper.ru/rk7/latest/ru/podderyoivaemye-drajvery-vesov-10819223.html)

---

### Decision 15: Tier 2 Price Verification and Dashboard

- **Status:** Accepted
- **Context:** When a farmer using a Tier 2 scale (e.g., CAS ER-Plus) changes a product price in Odoo, the scale does not update automatically. This creates a risk of inconsistency: Odoo says €24.90/kg, the scale still has €22.90/kg. Unlike Tier 1, there is no protocol command to sync the price. The farmer must enter prices manually — but how does the farmer know which prices changed?
- **Decision:** The Hub provides two mechanisms:
  1. **Price Change Dashboard:** A local web page (accessible via smartphone, tablet, or HDMI display) showing all pending price changes from Odoo. Changed items are highlighted with old price → new price. Farmer confirms each entry after updating the scale.
  2. **Automatic Price Verification:** After each weighing, the Hub compares the scale's price/kg (received from the print data stream) against Odoo's stored price. On mismatch:
     - **Warn mode** (default): Label prints with a visual warning, dashboard shows alert
     - **Strict mode** (optional): Label printing is blocked until the scale price matches Odoo
  The verification is logged in the audit chain regardless of mode.
- **Consequence:** Even without automatic PLU sync, the system catches every price discrepancy. The dashboard reduces the farmer's cognitive load ("What changed?"). Strict mode is recommended for LEH/retail deliveries where price accuracy is contractually required.
- **Sources:** Quality assurance best practice · EU FIC Reg. 1169/2011 Art. 8 (responsibility for correct information) · Austrian PAngV (Preisauszeichnungsgesetz)
