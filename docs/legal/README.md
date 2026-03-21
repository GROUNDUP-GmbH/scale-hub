# Scale Hub — Rechtstext-Auszüge (Legal Excerpts)

> **Maintained by:** Ground UP GmbH + Jóska Compliance Agent
> **Schema Version:** 1.0
> **Stand:** 2026-03-21

---

## Architektur: EU-Recht → Nationales Recht

```
docs/scale_hub/legal/
├── COMPLIANCE_MATRIX.md         ← Übersicht: Alle Länder × Alle Themen
├── README.md                    ← Dieses Dokument
│
├── eu/                          ← EU-weit gültig (Verordnungen, Richtlinien, Standards)
│   ├── LMIV_1169_2011.md       Lebensmittelinformations-VO (Basis)
│   ├── LMIV_ART9_PFLICHTANGABEN.md    Pflichtangaben vorverpackt
│   ├── LMIV_ART44_LOSE_WARE.md       Lose Ware + nationale Kompetenz
│   ├── LMIV_ART8_VERANTWORTLICHKEIT.md   Wer haftet
│   ├── LMIV_ANHANG_V_NR19.md         Nährwert-Ausnahme Direktvermarktung
│   ├── VO_178_2002_RUECKVERFOLGBARKEIT.md   Rückverfolgbarkeit
│   ├── NAWI_2014_31_EU.md       Nichtselbsttätige Waagen
│   ├── WELMEC_7_2.md            Software Guide
│   ├── EN_45501.md              Metrologie NAWI
│   └── GS1_DIGITAL_LINK.md     GS1 Standards
│
├── at/                          ← Österreich (voll recherchiert)
│   ├── compliance.yaml          Maschinenlesbare Compliance-Daten
│   ├── RKSV_AT.md               Registrierkassen-Sicherheitsverordnung
│   ├── MEG_AT.md                Maß- und Eichgesetz
│   ├── ALLERGENINFO_VO_AT.md    Allergeninformationsverordnung
│   ├── BAO_131B_KALTE_HAENDE.md Registrierkassenpflicht + Kalte Hände
│   ├── PREISAUSZEICHNUNG_AT.md  Preisauszeichnungsgesetz
│   ├── LOSKENNZEICHNUNG_AT.md   Loskennzeichnung
│   └── BEV_POS_SYSTEME_2023.md  BEV Informationsblatt POS-Systeme
│
├── hu/                          ← Ungarn (Platzhalter + bekannte Fakten)
│   ├── compliance.yaml
│   └── README.md
│
├── {be,bg,ch,cy,cz,de,...}/     ← Alle EU-27 + CH (Platzhalter)
│   ├── compliance.yaml
│   └── README.md
│
└── _template/                   ← Template für neue Länder
    ├── compliance.yaml
    └── README.md
```

## Warum hier und nicht nur als Referenz?

1. **Nachprüfbarkeit:** Ein Prüfer (BEV, Notified Body) kann sofort sehen, welche Textpassage unsere Architekturentscheidung begründet.
2. **Versionierung:** Git-History zeigt, auf welchen Rechtsstand sich eine bestimmte Architektur-Version bezieht.
3. **Unabhängigkeit:** Keine externen Links nötig, die brechen könnten.
4. **Maschinenlesbar:** `compliance.yaml` pro Land wird vom Hub zur Laufzeit geladen und vom Agent automatisch geprüft.

## Agent-Monitoring

Jede `compliance.yaml` enthält `last_review` und `next_review` Felder. Der Jóska Compliance Agent (`regulatory-watch` Skill) prüft regelmäßig:
- Ob `next_review` überschritten ist
- Ob Quell-URLs sich geändert haben
- Ob neue EUR-Lex Amendments vorliegen

Bei Änderungen: Agent aktualisiert `compliance.yaml` + erstellt GitHub Issue.

## Quellen-Links (Stand 2026-03-21)

- [EUR-Lex: VO (EU) 1169/2011 (LMIV)](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32011R1169)
- [EUR-Lex: VO (EG) 178/2002](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32002R0178)
- [EUR-Lex: RL 2014/31/EU (NAWI)](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32014L0031)
- [EUR-Lex: RL 2014/32/EU (MID)](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32014L0032)
- [RIS: MEG](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=10011249)
- [RIS: RKSV](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20009390)
- [WELMEC Guide 7.2 (PDF)](https://www.welmec.org/welmec/documents/guides/7.2/)
- [GS1 Digital Link Standard](https://www.gs1.org/standards/gs1-digital-link)
- [GS1 Austria](https://www.gs1.at/)

## Hinweis

Diese Auszüge ersetzen **nicht** das Studium der Volltexte. Sie dienen als Arbeitshilfe und Nachweisdokumentation. Bei Widersprüchen gilt immer der amtlich veröffentlichte Volltext.
