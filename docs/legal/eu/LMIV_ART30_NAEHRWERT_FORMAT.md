# LMIV Art. 30–35 — Nährwertdeklaration (Format & Inhalt)

## Verordnung (EU) Nr. 1169/2011, Art. 30–35 + Anhang XV

---

## Art. 30 — Inhalt der Nährwertdeklaration

### Verpflichtende Angaben ("Big Seven")

> Art. 30 Abs. 1: Die verpflichtende Nährwertdeklaration umfasst:
> - Brennwert
> - Fett, davon gesättigte Fettsäuren
> - Kohlenhydrate, davon Zucker
> - Eiweiß
> - Salz

| Nährstoff | Einheit | Bezugsgröße |
|-----------|---------|-------------|
| Brennwert | kJ und kcal | je 100 g / 100 ml |
| Fett | g | je 100 g / 100 ml |
| — davon gesättigte Fettsäuren | g | je 100 g / 100 ml |
| Kohlenhydrate | g | je 100 g / 100 ml |
| — davon Zucker | g | je 100 g / 100 ml |
| Eiweiß | g | je 100 g / 100 ml |
| Salz | g | je 100 g / 100 ml |

### Freiwillige Ergänzungen (Art. 30 Abs. 2)

Zusätzlich dürfen angegeben werden:
- Einfach/mehrfach ungesättigte Fettsäuren
- Mehrwertige Alkohole, Stärke, Ballaststoffe
- Vitamine und Mineralstoffe (wenn ≥ 15 % NRV je 100 g/ml)

---

## Art. 32 — Darstellung je 100 g oder 100 ml

> Die Angabe des Brennwerts und der Nährstoffmengen erfolgt in den
> Maßeinheiten gemäß Anhang XV **je 100 g oder 100 ml**.

Optional zusätzlich: **je Portion** (mit Angabe der Portionsgröße).

---

## Art. 34 — Darstellungsformat

### Tabellenformat (Pflicht, wenn Platz vorhanden)

> Art. 34 Abs. 2: Die verpflichtende Nährwertdeklaration ist in
> **tabellarischer Form** mit untereinanderstehenden Zahlen darzustellen.
> Ist der Platz dafür nicht ausreichend, darf die Angabe in
> **Fließtextform** (hintereinander) erfolgen.

### Tabellenformat (Beispiel ZPL)

```
Nährwerte            je 100 g
─────────────────────────────
Brennwert             1465 kJ
                       350 kcal
Fett                   12,0 g
  davon gesätt. FS      5,0 g
Kohlenhydrate          48,0 g
  davon Zucker          22,0 g
Eiweiß                  8,5 g
Salz                     1,2 g
```

### Fließtextformat (bei Platzmangel)

```
Nährwerte je 100 g: Brennwert 1465 kJ / 350 kcal, Fett 12,0 g
(davon gesätt. FS 5,0 g), Kohlenhydrate 48,0 g (davon Zucker 22,0 g),
Eiweiß 8,5 g, Salz 1,2 g
```

---

## Art. 33 — Angabe je Portion

> (1) Zusätzlich zur Angabe je 100 g/ml darf der Brennwert und die
> Nährstoffmengen auch **je Portion oder je Verzehreinheit** angegeben
> werden, sofern die Portion quantifiziert und die Anzahl der Portionen
> je Packung angegeben wird.

---

## Anhang V Nr. 19 — Ausnahme für Direktvermarkter

> Lebensmittel, **einschließlich handwerklich hergestellter Lebensmittel**,
> die der Hersteller in **kleinen Mengen** direkt an den Endverbraucher
> oder an lokale Einzelhandelsgeschäfte abgibt, die die Erzeugnisse
> **unmittelbar** an den Endverbraucher abgeben.

**Bedeutung:** Landwirte im Direktverkauf (Hofladen, Marktstand) sind
von der Nährwertdeklaration **befreit** (Szenario LOOSE + SIMPLE_PREPACK).

### Wann greift die Ausnahme NICHT?

- Verkauf an LEH (Spar, Billa, Lidl) → Nährwertdeklaration **Pflicht**
- Online-Verkauf über eigenen Webshop → Nährwertdeklaration **Pflicht**
  (strittig — nationale Auslegung unterschiedlich)
- Großmengen an Gastronomie → Nährwertdeklaration **empfohlen**

---

## Bedeutung für den Hub / Label Profiles

### Label-Engine Anforderungen

1. **Tabellenformat priorisieren** — Fließtext nur als Fallback
2. **Labelfläche prüfen**: Wenn Nährtabelle nicht auf Label passt →
   Fließtextformat verwenden
3. **Big Seven als Pflichtfelder** im Szenario LEH_PREPACK
4. **Rundungsregeln** (Anhang XV):
   - Brennwert: auf volle 1 kJ / 1 kcal runden
   - Fett, KH, Eiweiß, Salz: auf 0,1 g runden
   - Gesätt. FS, Zucker: auf 0,1 g runden

### Label Profile Matrix

| Szenario | Nährwertdeklaration | Format |
|----------|-------------------|--------|
| LOOSE | Nicht erforderlich | — |
| SIMPLE_PREPACK | Nicht erforderlich (Anhang V Nr. 19) | — |
| FULL_PREPACK | Empfohlen (bei größerer Produktion) | Tabelle/Fließtext |
| LEH_PREPACK | **Pflicht** | Tabelle bevorzugt |

---

## Quellen

- [LMIV Art. 30](https://eur-lex.europa.eu/eli/reg/2011/1169/art_30/oj)
- [LMIV Art. 32](https://eur-lex.europa.eu/eli/reg/2011/1169/art_32/oj)
- [LMIV Art. 33](https://eur-lex.europa.eu/eli/reg/2011/1169/art_33/oj)
- [LMIV Art. 34](https://eur-lex.europa.eu/eli/reg/2011/1169/art_34/oj)
- [LMIV Anhang V Nr. 19](https://eur-lex.europa.eu/eli/reg/2011/1169/ann_V/oj)
- [LMIV Anhang XV](https://eur-lex.europa.eu/eli/reg/2011/1169/ann_XV/oj) (Maßeinheiten, Rundung)
