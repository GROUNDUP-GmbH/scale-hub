# Fertigpackungsrecht — RL 76/211/EWG + VO (EG) 1169/2011 Art. 23

## Überblick

Wenn ein Landwirt Lebensmittel **vorverpackt** (= Fertigpackung), gelten
zusätzliche Anforderungen an die **Füllmenge** und deren **Kennzeichnung**.

---

## Richtlinie 76/211/EWG — Fertigpackungen nach Gewicht oder Volumen

### Kernanforderungen

> Art. 3: Fertigpackungen müssen so hergestellt sein, dass die
> **tatsächliche Füllmenge** im Mittel nicht geringer ist als die
> **Nennfüllmenge** auf dem Etikett.

> Art. 5: Die Nennfüllmenge muss auf der Fertigpackung angegeben sein in:
> - **Gramm (g)** oder **Kilogramm (kg)** für feste Erzeugnisse
> - **Milliliter (ml)** oder **Liter (l)** für flüssige Erzeugnisse
> - Mindestschriftgröße abhängig von Nennfüllmenge (siehe Tabelle)

### Mindesttoleranzen (Minus-Toleranzen)

| Nennfüllmenge | Toleranz (absolut) | Toleranz (%) |
|---------------|-------------------|-------------|
| 5–50 g/ml | 9 % | — |
| 50–100 g/ml | — | 4,5 g/ml |
| 100–200 g/ml | 4,5 % | — |
| 200–300 g/ml | — | 9 g/ml |
| 300–500 g/ml | 3 % | — |
| 500–1000 g/ml | — | 15 g/ml |
| 1000–10.000 g/ml | 1,5 % | — |

### Schriftgrößen für Nennfüllmenge

| Nennfüllmenge | Mindesthöhe der Ziffern |
|---------------|------------------------|
| ≤ 50 g/ml | 2 mm |
| 50–200 g/ml | 3 mm |
| 200–1000 g/ml | 4 mm |
| > 1000 g/ml | 6 mm |

---

## LMIV Art. 23 — Nettofüllmenge bei Lebensmitteln

### Kernanforderungen

> (1) Die Nettofüllmenge eines Lebensmittels ist in Liter, Zentiliter,
> Milliliter, Kilogramm oder Gramm anzugeben.

> (2) Angabe der Abtropfmasse bei Lebensmitteln in Aufgussflüssigkeit.

---

## Bedeutung für das System

### Szenario SIMPLE_PREPACK und FULL_PREPACK

- Vorverpackte Produkte **müssen** die Nennfüllmenge auf dem Etikett tragen.
- Die Waage liefert die **tatsächliche Füllmenge** (Istgewicht).
- Bei **Gewichtsware** (variabler Inhalt): Istgewicht auf Etikett = korrekt.
- Bei **Nennfüllmenge** (fixer Inhalt): Der Landwirt muss sicherstellen,
  dass die Abfüllung innerhalb der Toleranzen liegt.

### Szenario LEH_PREPACK

- LEH verlangt oft **fixe Nennfüllmengen** (z.B. „250 g").
- Das Etikett muss dann das **Nenngewicht** + ℮-Zeichen zeigen.
- Das ℮-Zeichen signalisiert Konformität mit RL 76/211/EWG.
- **Hub-Validierung:** Wenn `is_fixed_weight=true`, muss das Label
  die Nennfüllmenge und das ℮-Zeichen enthalten.

### Label-Profile Anpassung

| Feld | LOOSE | SIMPLE_PREPACK | FULL_PREPACK | LEH_PREPACK |
|------|-------|---------------|-------------|-------------|
| net_weight | ✅ | ✅ | ✅ | ✅ |
| nominal_weight | — | Optional | Optional | ✅ bei Fixgewicht |
| ℮-Zeichen | — | — | Optional | ✅ bei Fixgewicht |

---

## Nationale Umsetzungen

| Land | Gesetz | Besonderheiten |
|------|--------|----------------|
| AT | Maß- und Eichgesetz (MEG) + FPVO | BEV zuständig |
| DE | Fertigpackungsverordnung (FPackV) | Eichamt zuständig |
| HU | Igazságügyi és rendészeti minisztérium rendelet | BFKH zuständig |

---

## Quellen

- [RL 76/211/EWG](https://eur-lex.europa.eu/eli/dir/1976/211/oj)
- [LMIV Art. 23](https://eur-lex.europa.eu/eli/reg/2011/1169/art_23/oj)
- [RL 2007/45/EG](https://eur-lex.europa.eu/eli/dir/2007/45/oj) (Nennfüllmengen-Vereinheitlichung)
