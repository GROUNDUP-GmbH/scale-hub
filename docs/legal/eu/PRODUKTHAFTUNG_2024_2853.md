# EU-Produkthaftungsrichtlinie — RL (EU) 2024/2853

## Überblick

Die neue EU-Produkthaftungsrichtlinie (2024/2853) ersetzt die alte RL 85/374/EWG
und tritt am **9. Dezember 2026** in Kraft. Sie erweitert den Haftungsrahmen
explizit auf **Software** und **KI-Systeme**.

---

## Wesentliche Änderungen gegenüber RL 85/374/EWG

### 1. Software als Produkt

> Art. 4 Nr. 1: „Produkt" umfasst alle beweglichen Sachen, **einschließlich
> Software**, auch wenn die Software in ein anderes Produkt integriert oder
> mit einem solchen verbunden ist.

**Bedeutung:** Die Hub-Software (FastAPI, Scale Adapter, Label Engine) ist
explizit ein „Produkt" im Sinne der Richtlinie.

### 2. Hersteller-Definition erweitert

> Art. 4 Nr. 11: Umfasst auch denjenigen, der ein Produkt
> **wesentlich verändert** (z.B. durch Software-Update).

**Bedeutung:** Ground UP GmbH ist als Hersteller des Hub-Gesamtprodukts
(Hardware + Software) haftbar — auch für zukünftige Updates.

### 3. Beweislast-Erleichterung

> Art. 9: Wenn der Geschädigte glaubhaft macht, dass ein Produkt
> **fehlerhaft** war und der Schaden **mit dem Fehler zusammenhängt**,
> wird der **Kausalzusammenhang vermutet**.

**Bedeutung:** Der Geschädigte muss nicht mehr exakt beweisen, dass
ein Bug im Hub den Schaden verursacht hat. Vermutung reicht.

### 4. Verjährung

> Art. 14: Ansprüche verjähren **3 Jahre** ab Kenntnis des Schadens.
> Absolute Ausschlussfrist: **25 Jahre** (statt 10 bei physischen Schäden).

---

## Relevanz für den Scale Hub

### Mögliche Haftungsszenarien

| Szenario | Risiko | Gegenmaßnahme |
|----------|--------|---------------|
| Falscher Preis auf Label | Wirtschaftlicher Schaden | Integer-Arithmetik, 3-Wege-Vergleich |
| Fehlende Allergeninformation | Gesundheitsschaden | Pflichtfeld-Validierung, Szenario-basierte Profile |
| Falsches Gewicht auf Etikett | Verbrauchertäuschung | Rohdaten-Speicherung, Consistency Hash |
| Hub-Update bricht Waagen-Komm. ab | Betriebsausfall | Certified Core (stabil), Rollback-Mechanismus |
| Fehlkonfiguriertes Land → falsche Pflichtangaben | Bußgeld für Landwirt | compliance.yaml Validierung bei Startup |

### Schutzmaßnahmen

1. **Audit Log** als Beweismittel (hash-verkettet, manipulationssicher)
2. **Consistency Hash** für jeden Verkauf (Waage ↔ Label ↔ POS)
3. **Automatische Pflichtfeld-Validierung** je nach LabelScenario + Land
4. **Versionierte Software** mit reproduzierbaren Builds (Docker Image Tags)
5. **Produkthaftpflichtversicherung** — unbedingt abschließen vor Marktstart

---

## Umsetzungsfrist

- **Bis 9. Dezember 2026** müssen alle EU-Mitgliedstaaten nationale
  Umsetzungsgesetze erlassen.
- **Ab 9. Dezember 2026** gelten die neuen Regeln für alle Produkte,
  die ab diesem Datum in Verkehr gebracht werden.
- **Timeline für Hub:** Wenn Marktstart vor Dezember 2026, gilt noch die
  alte RL 85/374/EWG. Trotzdem jetzt schon nach neuer Richtlinie designen.

---

## Quellen

- [RL (EU) 2024/2853](https://eur-lex.europa.eu/eli/dir/2024/2853/oj)
- [RL 85/374/EWG (alt)](https://eur-lex.europa.eu/eli/dir/1985/374/oj)
