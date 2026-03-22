# Scale Hub

> **Ground UP GmbH** · Open Source · In Development (2026)

The Scale Hub connects a certified weighing scale to a label printer and a point-of-sale system. It ensures that every label is correct — for the farmers market, the farm shop, or the supermarket shelf — without the farmer having to know the regulations.

**→ [Product Page (architecture.html)](architecture.html)** — what the Hub does, in plain language

---

## Documentation

| Document | Audience | Content |
|---|---|---|
| [architecture.html](architecture.html) | Farmers, partners, investors | Product story, scenarios, FAQ |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Developers, contributors | System diagram, data flows, tech stack, security |
| [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md) | Developers, integrators | All verified scale protocols, Tier classification, wire-level specs |
| [LABEL_GUIDE.md](LABEL_GUIDE.md) | Developers, product managers | Label scenarios, mandatory fields, implementation |
| [LEGAL_REGISTER.md](LEGAL_REGISTER.md) | Developers, auditors, authorities | Applicable regulations, 15 architecture decisions |
| [legal/COMPLIANCE_MATRIX.md](legal/COMPLIANCE_MATRIX.md) | Compliance, product management | EU-wide compliance status per country |
| [legal/](legal/) | Legal, compliance | Full legal texts (EU + 28 countries) |

---

## Source Code

| Component | Location | Description |
|---|---|---|
| Hub (FastAPI) | `infrastructure/scale_hub/` | Python service: serial I/O, label engine, GS1, audit |
| Odoo Addon | `addons/groundup_scale_bridge/` | Product master data, PLU management, device config |
| Tests | `infrastructure/scale_hub/tests/` | Unit tests for label profiles, validation |

---

## Quick Start (Development)

```bash
cd infrastructure/scale_hub
docker compose up -d
```

The Hub exposes:
- `POST /sale` — receive sale data from scale
- `POST /label/zpl` — generate and print a label
- `POST /plu/select` — select a PLU on the scale
- `GET /audit/verify` — verify audit log integrity
- `GET /health` — health check

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full API and data flow documentation.

---

## Supported Scales

The Hub supports multiple scale families via an Adapter Pattern. See [PROTOCOL_CATALOG.md](PROTOCOL_CATALOG.md) for the full list.

| Tier | Scale Examples | PLU Sync | Status |
|---|---|---|---|
| **Tier 1** | CAS LP-1/LP-II, CAS CL5000/CL5200, DIGI SM, Mettler Toledo Tiger | Automatic from Odoo | Planned |
| **Tier 2** | CAS ER-Plus, CAS AP, basic bench scales | Manual (Hub-assisted) | **Phase 1 target** |
| **Tier 2+** | DIBAL | Price inject only | Planned |

## Hardware

- **Scale:** Any supported scale (see above)
- **Hub:** Raspberry Pi 5 (industrial enclosure, Secure Boot)
- **Label Printer:** Zebra (ZPL II compatible, self-adhesive labels)
- **Receipt Printer:** Any ESC/POS printer (driven by Odoo POS)

---

## License

Open Source — license TBD. Legal documentation in `legal/` is provided for transparency and is not licensed for redistribution without attribution.
