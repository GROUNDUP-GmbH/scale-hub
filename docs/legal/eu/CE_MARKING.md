# CE-Kennzeichnung — Relevante Richtlinien für den Scale Hub

## Überblick

Der Scale Hub (Raspberry Pi + Software in Gehäuse) ist ein elektronisches Gerät,
das in der EU in Verkehr gebracht wird. Folgende Richtlinien erfordern eine
CE-Konformitätserklärung:

---

## 1. EMV-Richtlinie 2014/30/EU — Elektromagnetische Verträglichkeit

### Anwendungsbereich

> Jedes Gerät, das elektromagnetische Störungen verursachen kann oder
> dessen Betrieb durch solche Störungen beeinträchtigt werden könnte.

### Anforderungen für den Hub

| Prüfung | Norm | Was wird geprüft |
|---------|------|------------------|
| Störaussendung (Emission) | EN 55032 | Elektromagn. Abstrahlung |
| Störfestigkeit (Immunity) | EN 55035 | Resistenz gegen externe Störungen |
| Oberschwingungen | EN 61000-3-2 | Netzrückwirkung |
| Flicker | EN 61000-3-3 | Spannungsschwankungen |

### Bedeutung für das System

- Der Hub enthält einen Raspberry Pi, RS-232-Adapter und ggf. PoE-HAT.
- Wenn ein **bereits CE-zertifiziertes** Raspberry Pi in einem **unmodifizierten**
  Zustand verwendet wird, reicht eine **vereinfachte Konformitätsbewertung**.
- **Achtung:** Ein eigenes Gehäuse oder zusätzliche Platinen (HATs) können eine
  **eigene EMV-Prüfung** erfordern.
- Geschätzte Kosten für EMV-Prüfung im akkreditierten Labor: **2.000–5.000 EUR**.

---

## 2. Niederspannungsrichtlinie 2014/35/EU (LVD)

### Anwendungsbereich

> Elektrische Betriebsmittel zur Verwendung bei einer Nennspannung
> zwischen 50 und 1000 V Wechselstrom oder 75 und 1500 V Gleichstrom.

### Bedeutung für das System

- Der Raspberry Pi arbeitet mit **5V DC** (über USB-C oder PoE).
- **Unter 50V AC / 75V DC** → LVD gilt **nicht direkt**.
- Allerdings: Das **Netzteil** (230V AC → 5V DC) muss LVD-konform sein.
- **Empfehlung:** Nur CE-zertifizierte Netzteile verwenden (z.B. offizielles
  Raspberry Pi Netzteil). Dann keine eigene LVD-Prüfung nötig.

---

## 3. Funkanlagen-Richtlinie 2014/53/EU (RED)

### Anwendungsbereich

> Geräte, die Funkwellen aussenden oder empfangen (Frequenzen unter 3000 GHz).

### Bedeutung für das System

- **Raspberry Pi 4/5** hat **eingebautes WLAN und Bluetooth** → RED relevant.
- **Aber:** Der Raspberry Pi ist bereits **RED-zertifiziert** durch den Hersteller.
- Solange wir den Funk-Teil **nicht modifizieren** (keine externe Antenne, kein
  Firmware-Mod der Funkchips), gilt die **Hersteller-Zertifizierung**.
- Eigene RED-Prüfung **nur** nötig, wenn wir ein zusätzliches Funkmodul
  (z.B. LoRa, NB-IoT) hinzufügen.

---

## 4. RoHS-Richtlinie 2011/65/EU

### Anwendungsbereich

> Beschränkung der Verwendung bestimmter gefährlicher Stoffe in Elektro-
> und Elektronikgeräten (Blei, Quecksilber, Cadmium, Cr(VI), PBB, PBDE,
> DEHP, BBP, DBP, DIBP).

### Bedeutung für das System

- Der Raspberry Pi und alle Standardkomponenten sind **RoHS-konform**.
- **Eigene Pflicht:** Wenn wir ein Endprodukt (Hub im Gehäuse) in Verkehr
  bringen, müssen wir eine **RoHS-Konformitätserklärung** ausstellen.
- In der Praxis: Lieferantenerklärungen (Declarations of Conformity) aller
  Komponentenhersteller sammeln und aufbewahren.

---

## Zusammenfassung für den Scale Hub

| Richtlinie | Relevant? | Eigene Prüfung nötig? | Kosten |
|------------|-----------|----------------------|--------|
| EMV 2014/30/EU | Ja | Ja, wenn eigenes Gehäuse/HAT | 2.000–5.000 EUR |
| LVD 2014/35/EU | Nein (unter 75V DC) | Nein, CE-Netzteil verwenden | 0 EUR |
| RED 2014/53/EU | Ja (WLAN/BT) | Nein, Pi ist zertifiziert | 0 EUR |
| RoHS 2011/65/EU | Ja | Nur Erklärung + Lieferantendoku | ~500 EUR |

### Erforderliche Dokumente

1. **EU-Konformitätserklärung** (Declaration of Conformity) — Pflicht
2. **Technische Dokumentation** (Technical File) — 10 Jahre aufbewahren
3. **CE-Kennzeichen** auf Gerät oder Verpackung — sichtbar, lesbar, dauerhaft

### Verantwortlicher

Der **Hersteller** (= Ground UP GmbH als Inverkehrbringer) ist verantwortlich
für die Konformitätserklärung, auch wenn Komponenten zugekauft werden.

---

## Quellen

- [EMV-Richtlinie 2014/30/EU](https://eur-lex.europa.eu/eli/dir/2014/30/oj)
- [Niederspannungsrichtlinie 2014/35/EU](https://eur-lex.europa.eu/eli/dir/2014/35/oj)
- [RED 2014/53/EU](https://eur-lex.europa.eu/eli/dir/2014/53/oj)
- [RoHS 2011/65/EU](https://eur-lex.europa.eu/eli/dir/2011/65/oj)
