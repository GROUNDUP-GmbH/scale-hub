# DSGVO — Datenschutzrelevanz des Scale Hub

## Verordnung (EU) 2016/679 (DSGVO)

---

## Relevanz für den Scale Hub

Der Scale Hub verarbeitet primär **Produktdaten** (PLU, Gewichte, Preise),
keine personenbezogenen Daten im engeren Sinne. Trotzdem gibt es
datenschutzrelevante Berührungspunkte.

---

## Potenzielle personenbezogene Daten

| Datentyp | Wo im System | Personenbezug | DSGVO-relevant? |
|----------|-------------|---------------|-----------------|
| PLU-Produktdaten | Hub + Waage | Nein | ❌ |
| Gewicht/Preis je Verkauf | Hub Audit Log | Nein (Sachbezug) | ❌ |
| Bediener-ID (wer hat gewogen) | Hub Audit Log | **Ja** (Mitarbeiter-ID) | ✅ |
| Kunden-ID (bei Kundenkarte/Bon) | Odoo POS → Hub | **Ja** | ✅ |
| IP-Adresse des Hub | Netzwerk-Logs | **Ja** (dynamisch) | ✅ |
| GS1 Digital Link URL | Label QR-Code | Nein (Produkt-URI) | ❌ |

---

## Relevante DSGVO-Artikel

### Art. 6 — Rechtsgrundlage der Verarbeitung

- **Art. 6 Abs. 1 lit. b:** Vertragserfüllung — Verkaufstransaktion
- **Art. 6 Abs. 1 lit. c:** Rechtliche Verpflichtung — Registrierkassenpflicht,
  Aufbewahrungspflichten (BAO §131b, 132)
- **Art. 6 Abs. 1 lit. f:** Berechtigtes Interesse — Betriebssicherheit,
  Manipulationsschutz

### Art. 5 — Grundsätze

| Grundsatz | Umsetzung im Hub |
|-----------|-----------------|
| Datenminimierung | Nur notwendige Daten im Audit Log |
| Speicherbegrenzung | Audit Log Retention Policy (7 Jahre = BAO) |
| Integrität/Vertraulichkeit | Hash-Kette, verschlüsselte Übertragung (HTTPS) |
| Transparenz | Datenschutzerklärung in Odoo (für Endkunden) |

### Art. 28 — Auftragsverarbeitung

Wenn Ground UP GmbH den Hub als **SaaS/Managed Service** betreibt
(z.B. Hub-Management für den Landwirt):
- Ground UP = **Auftragsverarbeiter** (Art. 28)
- Landwirt = **Verantwortlicher** (Art. 4 Nr. 7)
- **Auftragsverarbeitungsvertrag (AVV)** erforderlich

Wenn der Landwirt den Hub **selbst** betreibt (On-Premise):
- Kein AVV nötig (Ground UP liefert nur Software).
- Aber: Datenschutz-Dokumentation in README / Handbuch.

### Art. 30 — Verzeichnis der Verarbeitungstätigkeiten

Ground UP muss ein Verarbeitungsverzeichnis führen für:
- Hub-Audit-Log-Daten (Bediener-IDs)
- Odoo-Kundendaten (wenn über Hub verarbeitet)

### Art. 35 — Datenschutz-Folgenabschätzung (DSFA)

Eine DSFA ist **nicht** erforderlich, da:
- Keine systematische Überwachung von Personen
- Keine großflächige Verarbeitung besonderer Kategorien
- Keine automatisierte Einzelfallentscheidung

---

## Technische Maßnahmen (Art. 32)

| Maßnahme | Implementierung |
|----------|----------------|
| Verschlüsselung in Transit | HTTPS (Hub ↔ Odoo API) |
| Verschlüsselung at Rest | Disk-Verschlüsselung (Secure Boot + dm-verity) |
| Pseudonymisierung | Bediener-ID statt Klarname im Audit Log |
| Zugriffskontrolle | HMAC-Auth für Hub API, Odoo RBAC |
| Backup | Audit Log Export zu Odoo (verschlüsselt) |
| Löschkonzept | Nach BAO-Aufbewahrungsfrist (7 Jahre) |

---

## Empfehlungen

1. **Bediener-IDs pseudonymisieren** — Im Hub nur numerische IDs,
   Zuordnung Name ↔ ID nur in Odoo (unter RBAC-Schutz).
2. **Kein Kunden-Tracking über GS1 Digital Link** — QR-Code enthält
   nur Produkt-URI, keine Kunden-ID.
3. **Datenschutzerklärung** in Odoo POS für Endverbraucher bereitstellen.
4. **AVV-Template** erstellen für Landwirte, die den Hub als Managed
   Service nutzen.

---

## Quellen

- [DSGVO (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- [Art. 28 — Auftragsverarbeiter](https://eur-lex.europa.eu/eli/reg/2016/679/art_28/oj)
- [Art. 32 — Sicherheit der Verarbeitung](https://eur-lex.europa.eu/eli/reg/2016/679/art_32/oj)
