# Scale Hub — Certification Checklist

> **Status:** v1.0 · 2026-03-22
> **Maintainer:** Ground UP GmbH · FN 481220 b
> **Scope:** Software + Documentation requirements for Hub certification as "Module" (Tier 0)
> **Legal Register:** [LEGAL_REGISTER.md](LEGAL_REGISTER.md)
> **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
> **Protocol Catalog:** [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md)

---

## Purpose

This checklist documents **everything the Hub must fulfill** to obtain a type examination certificate ("Prüfzeugnis" / Test Certificate) from a Notified Body (e.g., BEV NB 0445 in Austria, PTB in Germany).

The Hub in **Tier 0** performs price calculation (`total = weight × price/kg`) and is therefore classified as a **Module** — not a Peripheral — under the NAWI modular approach (WELMEC 2.5). This triggers testing under EN 45501:2015 Annex D and software evaluation under WELMEC 7.2.

**Focus of this document:** Software and documentation requirements only. Hardware testing (EMV, surge, temperature per EN 45501 Annex E) is performed externally by an accredited test laboratory and is not covered here.

---

## Regulatory Framework

| # | Norm / Directive | Relevant Chapter | What It Requires |
|---|---|---|---|
| **R1** | Directive 2014/31/EU | Art. 3, Annex III | Essential requirements for NAWI |
| **R2** | EN 45501:2015 | Annex D (normative) | Testing of digital data processing terminals as modules |
| **R3** | EN 45501:2015 | Annex F (normative) | Compatibility checking of modules (Hub + Scale) |
| **R4** | EN 45501:2015 | Annex G (normative) | Additional examinations for software-controlled digital devices |
| **R5** | WELMEC 7.2 v2022 | Section 4 (Type P/U) | Core software requirements: identification, sealing, interfaces, robustness, audit trail |
| **R6** | WELMEC 7.2 v2022 | Extension S | Software separation (legally relevant vs. non-legally relevant) |
| **R7** | WELMEC 7.2 v2022 | Extension D | Controlled software download / update |
| **R8** | WELMEC 7.2 v2022 | Extension L | Long-term storage of measurement data |
| **R9** | WELMEC 7.2 v2022 | Extension T | Transmission of measurement data via networks |
| **R10** | WELMEC 2.5 | Module/Peripheral definitions | Hub = Module (price-computing device) |
| **R11** | BEV FL53090108 (01/2023) | Section 2.3, 3.1, 3.2 | Technical documentation, type examination procedure |
| **R12** | VO BGBl. II Nr. 30/2016 | Anhang 1 | Austrian implementation of NAWI conformity assessment |

---

## Status Legend

| Symbol | Meaning |
|---|---|
| `[ ]` | Not started |
| `[~]` | Partially implemented or planned |
| `[x]` | Complete and verified |

---

## 1. Software Requirements (WELMEC 7.2 + EN 45501)

### REQ-SW-01: Software Identification

- **Source:** WELMEC 7.2 §4.1, §4.3 · EN 45501 Annex G
- **Architecture Decision:** [Decision 07](LEGAL_REGISTER.md#decision-07-secure-boot-from-device-1), [Decision 11](LEGAL_REGISTER.md#decision-11-certified-core--uncertified-periphery)
- **Status:** `[~]` Partially — Git-based versioning exists, CRC mechanism missing

**What is required:**

Every legally relevant software component must be identifiable at all times. The identification must include a version number and a checksum (CRC32 or SHA-256) that changes with every modification to the software. The identification must be retrievable without opening the device — either via a dedicated API endpoint, a display, or a metrological menu.

**Acceptance criteria:**

- [ ] `GET /version` endpoint returns `{version, core_crc32, core_sha256, build_date, boot_count}`
- [ ] CRC/SHA is computed over the Certified Core binary at build time and embedded as a constant
- [ ] Every Hub start logs the software identification to the audit trail (REQ-SW-04)
- [ ] Version string is visible on the customer-facing display (Tier 0) or dashboard
- [ ] A change to any file in `hub/core/` produces a different checksum — verified by CI

**Estimated effort:** ~2 days

---

### REQ-SW-02: Software Separation (Certified Core vs. Periphery)

- **Source:** WELMEC 7.2 §5.3, Extension S
- **Architecture Decision:** [Decision 11](LEGAL_REGISTER.md#decision-11-certified-core--uncertified-periphery)
- **Status:** `[~]` Architecturally planned, not implemented

**What is required:**

Clear separation between legally relevant software ("Certified Core") and non-legally relevant software ("Uncertified Periphery"). The boundary must be documented. Non-legally-relevant software must not be able to influence legally relevant functions — not through shared memory, direct function calls, or file system access.

**Certified Core scope (~500 LOC):**

- Serial I/O driver (read weight from scale)
- Price calculation (`total_cents = weight_g × price_cents_per_kg // 1000`)
- Integer validation and consistency check
- Audit log writer
- API gateway (sale data in/out)
- Sealed parameter store

**Uncertified Periphery (no size limit):**

- Label engine (ZPL generation)
- Compliance YAML loader
- GS1 QR code generator
- Odoo synchronization
- Web dashboard
- OTA update manager (except the verification step, which is in Core)

**Acceptance criteria:**

- [ ] Separate Python package `hub.core` with no imports from `hub.periphery`
- [ ] `hub.core` communicates with `hub.periphery` only via defined data structures (Pydantic models or dataclasses)
- [ ] Docker image layers: Core is a separate layer, Periphery is layered on top
- [ ] A change to Periphery code does NOT change the Core checksum (REQ-SW-01)
- [ ] Dependency analysis tool (e.g., `import-linter`) enforces the boundary in CI
- [ ] Separation is documented in a "Software Architecture Document" (for BEV submission)

**Estimated effort:** ~5 days (refactoring existing code)

---

### REQ-SW-03: Sealed Parameters (Digital Sealing)

- **Source:** WELMEC 7.2 §4.3 · EN 45501 §T.4.1
- **Architecture Decision:** [Decision 07](LEGAL_REGISTER.md#decision-07-secure-boot-from-device-1)
- **Status:** `[~]` Secure Boot planned, parameter sealing missing

**What is required:**

Metrologically relevant parameters must be protected against unauthorized modification. In traditional instruments, this is achieved with physical seals (lead seals, destructible labels). For software-based devices, digital equivalents are required: cryptographic signatures on configuration, event counters for parameter changes, and secure boot to prevent runtime manipulation.

**Parameters that must be sealed:**

| Parameter | Why |
|---|---|
| Price calculation formula | Directly determines the sale amount |
| PLU price map | Price per kg for each product |
| Rounding rules | EN 45501 Annex A rounding affects the result |
| Scale adapter configuration | Serial parameters, protocol type |
| Calibration offsets (if any) | Would affect weight reading |
| Software identification (version, CRC) | Prevents version spoofing |

**Acceptance criteria:**

- [ ] `sealed_config.json` signed with HMAC-SHA256 (key in Secure Element or OTP)
- [ ] Hub verifies signature on every start — boot fails on mismatch
- [ ] Every parameter change increments a monotonic event counter (persisted in flash)
- [ ] Event counter is included in the audit log and visible via `GET /version`
- [ ] Parameter changes are only possible via signed OTA update (REQ-SW-05)
- [ ] The sealing mechanism is documented for the BEV examiner

**Estimated effort:** ~3 days

---

### REQ-SW-04: Event Logger / Audit Trail

- **Source:** WELMEC 7.2 §4.5 · EN 45501 §T.4.5
- **Architecture Decision:** [Decision 04](LEGAL_REGISTER.md#decision-04-hash-chained-append-only-audit-log)
- **Status:** `[~]` `app/audit_log.py` exists with hash chain, needs extension

**What is required:**

Registration of all authorized changes to legally relevant software and parameters. The log must be append-only, tamper-evident (hash chain), and non-deletable from the device. It must record at minimum:

| Event Type | Data Recorded |
|---|---|
| Hub start / shutdown | Software version, CRC, event counter, timestamp |
| Parameter change | Which parameter, old value hash, new value hash, counter |
| Sale transaction | Sale ID, weight_g, price_cents_per_kg, total_cents, PLU ID, consistency hash |
| Software update | Old version → new version, success/failure, update package hash |
| Error / anomaly | Type, description, affected component |
| Verification request | Who requested, result (pass/fail) |

**Acceptance criteria:**

- [ ] JSONL format with SHA-256 hash chain (each entry includes hash of previous entry)
- [ ] `GET /audit/verify` validates the entire chain and returns pass/fail + chain length
- [ ] All 6 event types listed above are implemented
- [ ] Log survives reboot (written to persistent storage, not tmpfs)
- [ ] Log cannot be deleted or truncated from the Hub's user interface or API
- [ ] Log export (USB or network) for BEV examiner — read-only, does not modify the log
- [ ] "Prüfzahlen" (examination numbers): The examiner can trigger a test transaction and verify it appears correctly in the log

**Estimated effort:** ~2 days (extending existing `audit_log.py`)

---

### REQ-SW-05: Update Protection (Software Download)

- **Source:** WELMEC 7.2 §4.3, Extension D
- **Architecture Decision:** [Decision 07](LEGAL_REGISTER.md#decision-07-secure-boot-from-device-1)
- **Status:** `[~]` Conceptually described in `SECURE_BOOT.md`, not implemented

**What is required:**

Software updates must be controlled. The device must verify the authenticity (who signed it?) and integrity (was it modified?) of every update package before applying it. Both successful and failed update attempts must be recorded in the audit trail. Rollback to the previous version must be possible if an update fails.

**Acceptance criteria:**

- [ ] OTA update packages are signed with Ed25519 or RSA-2048 (private key held offline by Ground UP)
- [ ] Hub verifies signature before applying — rejects unsigned or tampered packages
- [ ] A/B partition scheme: update is written to inactive partition, verified, then switched
- [ ] Failed update = automatic rollback to previous partition
- [ ] Audit log records: update start, package hash, signature verification result, success/failure, new version
- [ ] The update process is documented step-by-step for the BEV examiner
- [ ] Manual rollback via physical button (e.g., hold button during boot) — documented in user manual

**Estimated effort:** ~5 days

---

### REQ-SW-06: Protective Interface

- **Source:** WELMEC 7.2 §4.4 · EN 45501 §T.4.4
- **Architecture Decision:** [Decision 03](LEGAL_REGISTER.md#decision-03-allowlist-only-for-plu-commands), [Decision 06](LEGAL_REGISTER.md#decision-06-plu-sync-separated-from-active-sales)
- **Status:** `[~]` Conceptually planned (Allowlist + State Machine), partially implemented

**What is required:**

The communication interface between Hub and scale must be protected. The interface must:
1. Ignore undefined or unknown commands (they must have no effect on legally relevant functions)
2. Only accept commands from the pre-configured allowlist
3. Block configuration changes during active measurement/sale transactions
4. Log all rejected commands

**Acceptance criteria:**

- [ ] Allowlist of permitted commands is part of `sealed_config.json` (REQ-SW-03)
- [ ] State machine enforces: `IDLE` → PLU sync allowed; `WEIGHING`/`PRINTING` → PLU sync blocked
- [ ] Unknown serial bytes are discarded and logged (not forwarded, not causing errors)
- [ ] HTTP API rejects undefined endpoints with 404 (not 500)
- [ ] Fuzz testing: random bytes on serial input do not crash the Hub or corrupt state
- [ ] The protective interface behavior is documented for the BEV examiner

**Estimated effort:** ~2 days (hardening + tests)

---

### REQ-SW-07: Robustness / Measurement Priority

- **Source:** WELMEC 7.2 §4.2 · EN 45501 Annex E (software section)
- **Architecture Decision:** New (to be added as Decision 17)
- **Status:** `[ ]` Not addressed

**What is required:**

The measurement process (reading weight, calculating price, recording the transaction) must have the highest priority. No other function (label printing, Odoo sync, dashboard rendering, OTA update) may interrupt or delay a measurement. The system must degrade gracefully under adverse conditions:

| Failure Scenario | Required Behavior |
|---|---|
| Odoo unreachable | Sale completes locally, queued for sync |
| Label printer offline | Sale completes, label queued, warning displayed |
| Network disconnected | All core functions continue (scale → Hub → audit log) |
| Power loss during transaction | Transaction either completes fully or is rolled back — no partial records |
| Scale disconnected mid-sale | Transaction aborted, logged as error, no label printed |

**Acceptance criteria:**

- [ ] Sale transaction runs in a dedicated thread/process with highest priority
- [ ] Odoo sync is asynchronous — timeout does not block sale
- [ ] Printer failure does not prevent audit log entry
- [ ] Power-loss resilience: audit log uses `fsync()` after each write
- [ ] Watchdog timer restarts the Hub if the main process hangs (>10s)
- [ ] All failure scenarios above are covered by integration tests
- [ ] Graceful degradation behavior is documented for the BEV examiner

**Estimated effort:** ~3 days

---

## 2. BEV Documentation Requirements (Module B — Type Examination)

Based on [BEV FL53090108 (01/2023)](https://bev.gv.at/dam/jcr:72782fe6-561a-4698-8596-ef0ec1c75cf3/FL53090108_Zertifizierungsbedingungen_MID_NAWID.pdf), Section 2.3 and VO BGBl. II Nr. 30/2016 Anhang 1.

### REQ-DOC-01: General Description of the Measuring Instrument

- **Source:** BEV FL53090108 §2.3 (3)(1)
- **Status:** `[~]` ARCHITECTURE.md exists but not in BEV submission format

**What to deliver:**

A formal document describing the Hub as a "digital terminal module in a weighing system" (Digitales Terminal-Modul im Waagenverbund). Must cover:

- [ ] Purpose and intended use (direct agricultural sales, farm shop, market)
- [ ] System boundary: what is the Hub, what is NOT the Hub (scale, printer, POS are separate)
- [ ] Operating principle: weight input → price calculation → label output → audit record
- [ ] User interaction model (farmer selects product, customer sees display)
- [ ] Environmental conditions (indoor, outdoor market, temperature range)
- [ ] Accuracy class and maximum capacity (inherited from connected scale)

**Estimated effort:** ~2 days

---

### REQ-DOC-02: Design Drawings, Circuit Diagrams

- **Source:** BEV FL53090108 §2.3 (3)(2)
- **Status:** `[ ]` Not started

**What to deliver:**

- [ ] Block diagram of the Hub hardware (Raspberry Pi 5, USB-RS232 adapter, HDMI display, Ethernet/WiFi, power supply)
- [ ] Wiring diagram: scale ↔ RS-232 ↔ Hub ↔ USB ↔ printer, Hub ↔ HDMI ↔ display
- [ ] Enclosure drawing with dimensions, connector positions, sealing points
- [ ] Power supply specification (5V/5A USB-C, UPS option)

**Estimated effort:** ~2 days (requires hardware design input)

---

### REQ-DOC-03: Software Flow Diagrams and Logic Diagrams

- **Source:** BEV FL53090108 §2.3 (3)(4)
- **Status:** `[~]` State machine exists as code, formal flow diagrams missing

**What to deliver:**

"General information about the software with an explanation of its characteristics and operation" — specifically:

- [ ] Boot sequence flowchart (power on → Secure Boot → integrity check → service start)
- [ ] Sale transaction flowchart (weight received → price calculated → consistency check → label printed → audit logged → POS notified)
- [ ] PLU synchronization flowchart (Odoo push → allowlist check → state check → parameter update → sealed config update)
- [ ] Software update flowchart (OTA received → signature verified → A/B partition write → verify → switch → audit log)
- [ ] Error handling flowchart (failure scenarios from REQ-SW-07)
- [ ] Software architecture diagram showing Core/Periphery boundary (REQ-SW-02)

**Estimated effort:** ~3 days

---

### REQ-DOC-04: Risk Analysis and Assessment

- **Source:** BEV FL53090108 §3.2
- **Status:** `[ ]` Not started

**What to deliver:**

A formal risk analysis covering threats to metrological integrity. Recommended format: FMEA (Failure Mode and Effects Analysis) or equivalent.

- [ ] Risk: Price calculation manipulation (attacker modifies formula or PLU prices)
  - Mitigation: Sealed parameters (REQ-SW-03), Secure Boot (REQ-SW-05)
- [ ] Risk: Software substitution (attacker replaces Hub software)
  - Mitigation: Secure Boot with OTP-fused key, signed updates (REQ-SW-05)
- [ ] Risk: Audit log tampering (attacker deletes or modifies transaction records)
  - Mitigation: Hash chain (REQ-SW-04), append-only storage, optional blockchain anchoring
- [ ] Risk: Man-in-the-middle on serial connection (fake weight data injected)
  - Mitigation: Protective interface (REQ-SW-06), consistency verification (Decision 13)
- [ ] Risk: Power loss during transaction (partial data, inconsistent state)
  - Mitigation: Atomic writes, fsync, transaction rollback (REQ-SW-07)
- [ ] Risk: Rollback attack (downgrade to older, vulnerable software version)
  - Mitigation: Monotonic version counter in Secure Element, rejected by boot verification
- [ ] Risk: Network-based attack (unauthorized API access)
  - Mitigation: HMAC authentication, local-only API binding, firewall rules

**Estimated effort:** ~3 days

---

### REQ-DOC-05: Software Examination Instructions

- **Source:** BEV FL53090108 §3.1 ("Anleitung zum Prüfen der Software")
- **Status:** `[ ]` Not started

**What to deliver:**

Step-by-step instructions for the BEV examiner to verify the Hub's metrological properties:

- [ ] How to display software identification (version, CRC) — via API, display, or menu
- [ ] How to verify the audit trail integrity (`GET /audit/verify` + manual hash chain check)
- [ ] How to inspect sealed parameters and verify their signatures
- [ ] How to trigger a test transaction and verify it in the audit log ("Prüfzahlen")
- [ ] How to verify software separation (show that Periphery changes don't affect Core CRC)
- [ ] How to simulate failure scenarios (disconnect scale, disconnect printer, kill network)
- [ ] How to verify the update process (apply a signed update, apply an unsigned update — must be rejected)
- [ ] How to verify the protective interface (send invalid serial commands — must be ignored)

**Estimated effort:** ~2 days

---

### REQ-DOC-06: Compatibility of Modules (EN 45501 Annex F)

- **Source:** EN 45501:2015 Annex F · BEV FL53090108 §3.1
- **Status:** `[ ]` Not started

**What to deliver:**

Proof that the Hub module is compatible with the connected scale module(s). The "Compatibility of Modules" form (per WELMEC Guide 2) requires:

- [ ] Hub specifications: resolution, calculation method, input range, accuracy contribution
- [ ] Scale specifications: accuracy class, Max, Min, d, e, n
- [ ] Combined system accuracy: proof that Hub does not degrade the scale's accuracy class
- [ ] List of tested/compatible scale models (reference configurations from ARCHITECTURE.md)
- [ ] For each compatible scale: serial parameters, protocol, adapter module version

**Estimated effort:** ~2 days (per scale model — start with 1-2 reference scales)

---

### REQ-DOC-07: Declaration of Conformity (Draft)

- **Source:** BEV FL53090108 Anhang 2, Anhang 3 · VO BGBl. II Nr. 30/2016
- **Status:** `[ ]` Not started

**What to deliver:**

EU Declaration of Conformity per BEV template:

- [ ] Unique identification number of the measuring instrument
- [ ] Manufacturer name and address (Ground UP GmbH, Iglasegasse 21-23, A-1190 Wien)
- [ ] Statement of sole responsibility
- [ ] Object of declaration (Scale Hub, type designation, serial number)
- [ ] List of applicable directives (2014/31/EU, 2014/30/EU EMC, 2014/35/EU LVD)
- [ ] Applied harmonized standards (EN 45501:2015, EN 61000-6-x)
- [ ] Notified Body name and identification number (BEV NB 0445)
- [ ] Place, date, signature
- [ ] German text + English translation

**Estimated effort:** ~1 day (template-based)

---

### REQ-DOC-08: CE Marking and Type Plate

- **Source:** BEV FL53090108 §3.1, Anhang 1 · Directive 2014/31/EU Art. 15
- **Status:** `[ ]` Not started

**What to deliver:**

- [ ] CE marking with Notified Body number (CE 0445)
- [ ] Type plate design: manufacturer, type designation, serial number, year of manufacture
- [ ] Marking of sealing points (where digital seals replace physical seals)
- [ ] Marking of accuracy class (inherited from scale, documented in compatibility form)
- [ ] Placement specification (where on the enclosure the plate is affixed)

**Estimated effort:** ~1 day (requires enclosure design)

---

## 3. Tier 0 Specific Requirements

These requirements apply **only** when the Hub performs price calculation (Tier 0). They are NOT required for Tier 1/2 operation where the scale computes prices.

### REQ-T0-01: Price Calculation Validation

- **Source:** EN 45501 Annex A (rounding) · Directive 2014/31/EU Annex III §2
- **Architecture Decision:** [Decision 16](LEGAL_REGISTER.md#decision-16-hub-as-certified-price-calculator--tier-0-target-architecture)
- **Status:** `[ ]` Not started

**What is required:**

The Hub's price calculation must produce results identical to a certified price-computing scale. The formula `total_cents = weight_g × price_cents_per_kg // 1000` must handle rounding correctly per EN 45501 Annex A. Integer arithmetic eliminates floating-point errors, but edge cases must be verified.

**Acceptance criteria:**

- [ ] Price calculation uses exclusively integer arithmetic (no `float`, no `Decimal`)
- [ ] Rounding rule: commercial rounding (0.5 rounds up) — matching EN 45501
- [ ] Test suite: 10,000+ random (weight, price/kg) combinations compared against a reference implementation
- [ ] Edge cases tested: 1g at €999.99/kg, 15000g at €0.01/kg, exact multiples, near-boundary values
- [ ] Result matches a certified CAS LP-II for at least 100 manual cross-checks
- [ ] The calculation is part of the Certified Core (REQ-SW-02) — no external dependencies

**Estimated effort:** ~2 days

---

### REQ-T0-02: Customer-Facing Display

- **Source:** Austrian Preisauszeichnungsgesetz (PAngV) · Directive 2014/31/EU Annex III §3
- **Architecture Decision:** [Decision 16](LEGAL_REGISTER.md#decision-16-hub-as-certified-price-calculator--tier-0-target-architecture)
- **Status:** `[ ]` Not started

**What is required:**

When the Hub calculates the price (Tier 0), the customer must be able to see the weight, unit price, and total price during the weighing process. This replaces the scale's built-in display (which only shows weight in Tier 0).

**Acceptance criteria:**

- [ ] HDMI display (7" minimum) connected to Hub, showing in real-time:
  - Net weight (in kg or g, matching scale resolution)
  - Unit price (€/kg)
  - Total price (€)
  - Product name
  - Tare weight (if applicable)
- [ ] Display updates within 200ms of weight change
- [ ] Display font size meets readability requirements (visible from 1.5m)
- [ ] Display shows "---" or blank when scale is not stable (no price shown for unstable weight)
- [ ] Display is part of the Certified Core's output — its content is logged in the audit trail

**Estimated effort:** ~3 days

---

### REQ-T0-03: Zero Tracking and Tare

- **Source:** EN 45501 §4.5 (zero-tracking), §4.6 (tare) · OIML R76
- **Architecture Decision:** [Decision 16](LEGAL_REGISTER.md#decision-16-hub-as-certified-price-calculator--tier-0-target-architecture)
- **Status:** `[ ]` Not started

**What is required:**

If the Hub is the price-calculating device, it must correctly handle the scale's zero-tracking and tare functions. The scale still performs the physical zero-tracking and tare — the Hub must correctly interpret the tare-adjusted weight data from the serial interface and use the net weight for price calculation.

**Acceptance criteria:**

- [ ] Hub reads net weight (after tare) from the scale's serial output
- [ ] Hub does NOT apply its own tare correction — the scale handles this
- [ ] If the scale protocol provides both gross and net weight, Hub uses net weight for calculation
- [ ] Tare weight is displayed on the customer display and printed on the label
- [ ] Hub rejects negative net weight (scale error or tare exceeded) — no negative prices
- [ ] Zero-tracking behavior is documented in the compatibility form (REQ-DOC-06)

**Estimated effort:** ~3 days

---

## 4. Implementation Phases

### Phase 1: Tier 2 without certification (NOW)

Build all REQ-SW-* requirements even though no formal certification is pursued. This ensures quality, creates the architecture for future certification, and makes the "non-legally-relevant" argument defensible.

| Requirement | Priority | Reason |
|---|---|---|
| REQ-SW-02 (Separation) | P0 | Foundation for all other requirements |
| REQ-SW-04 (Audit Trail) | P0 | Already partially implemented, quick win |
| REQ-SW-06 (Protective Interface) | P0 | Security-critical |
| REQ-SW-07 (Robustness) | P0 | Operational reliability |
| REQ-SW-01 (Identification) | P1 | Depends on REQ-SW-02 |
| REQ-SW-03 (Sealed Parameters) | P1 | Depends on REQ-SW-02 |
| REQ-SW-05 (Update Protection) | P2 | Requires Secure Boot infrastructure |

**Estimated Phase 1 effort:** ~22 days

### Phase 2: BEV documentation (after market validation)

| Requirement | Priority | Reason |
|---|---|---|
| REQ-DOC-03 (Flow Diagrams) | P0 | Required for BEV submission |
| REQ-DOC-04 (Risk Analysis) | P0 | Required for BEV submission |
| REQ-DOC-01 (General Description) | P1 | Required for BEV submission |
| REQ-DOC-05 (Examination Instructions) | P1 | Required for BEV submission |
| REQ-DOC-06 (Compatibility) | P1 | Required per scale model |
| REQ-DOC-02 (Circuit Diagrams) | P2 | Requires final hardware design |
| REQ-DOC-07 (Declaration) | P2 | Template-based, quick |
| REQ-DOC-08 (CE Marking) | P2 | Requires final enclosure design |

**Estimated Phase 2 effort:** ~13 days

### Phase 3: Tier 0 certification

| Requirement | Priority | Reason |
|---|---|---|
| REQ-T0-01 (Price Calculation) | P0 | Core differentiator |
| REQ-T0-02 (Customer Display) | P0 | Legal requirement for price display |
| REQ-T0-03 (Zero/Tare) | P1 | Scale protocol dependent |
| BEV submission | — | Antrag + Prüfmuster + Technische Unterlagen |

**Estimated Phase 3 effort:** ~8 days + BEV process (3-6 months)

---

## 5. Cost Estimate

| Item | Estimated Cost | Notes |
|---|---|---|
| Software development (Phase 1-3) | ~43 person-days | Internal development |
| BEV type examination fee | €3,000–8,000 | Based on BEV tariff schedule (Amtsblatt 2023) |
| BEV technical testing (PTP) | €5,000–15,000 | Depends on scope and duration |
| EMV test laboratory (external) | €3,000–8,000 | Required for CE marking, not covered in this checklist |
| Prüfmuster (test specimens) | €500–1,000 | 2-3 complete Hub units |
| **Total certification cost** | **€10,000–25,000** | Excluding internal development time |

**Note:** This estimate is for the Hub module only. The scale and printer are separately certified by their manufacturers. Re-certification of the Certified Core is required only when the Core changes — Periphery updates are free.

---

## 6. Open Questions for BEV Pre-Consultation

Before formally submitting, a pre-consultation ("Vorgespräch") with BEV is recommended. Key questions:

1. **Classification:** Does BEV agree that the Hub is a "Module" under WELMEC 2.5 (price-computing digital terminal), and that a Test Certificate per EN 45501 Annex D is the correct path?
2. **Software separation:** Does BEV accept the "Certified Core + Uncertified Periphery" model per WELMEC 7.2 Extension S, such that only Core changes trigger re-certification?
3. **Secure Boot as digital seal:** Does BEV accept OTP-fused Secure Boot + signed updates as equivalent to physical sealing (Plombierung)?
4. **Scale compatibility:** Can the Hub TC be issued with a "compatibility clause" allowing any scale with a valid TC/TAC (analogous to load cell compatibility), or must each scale model be explicitly listed?
5. **Raspberry Pi as platform:** Are there concerns about using a general-purpose SBC (Raspberry Pi 5) for a metrologically relevant module? Would an industrial SBC (e.g., RevPi) be preferred?
6. **Open source:** Does the open-source nature of the Hub software create issues for the examination (all source code is publicly visible)?

---

## References

- [LEGAL_REGISTER.md](LEGAL_REGISTER.md) — Architecture decisions and applicable regulations
- [ARCHITECTURE.md](ARCHITECTURE.md) — Technical architecture, data flows, state machine
- [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md) — Scale protocols, Tier classification, Option F analysis
- [SECURE_BOOT.md](../../infrastructure/scale_hub/SECURE_BOOT.md) — Secure Boot concept
- [BEV Certification Requirements (FL53090108)](https://bev.gv.at/dam/jcr:72782fe6-561a-4698-8596-ef0ec1c75cf3/FL53090108_Zertifizierungsbedingungen_MID_NAWID.pdf) — Official BEV document
- [WELMEC 7.2 v2015 PDF](https://www.welmec.org/welmec/documents/guides/7.2/2015/Guide_7.2_2015__Software.pdf) — Software Guide
- [UKWF: Interfaces, Printers and Peripheral Devices](https://www.ukwf.org.uk/1-3-interfaces-printers-and-peripheral-devices/) — Module vs. Peripheral definitions
