# LMIV Art. 13 — Mindestschriftgröße für Pflichtangaben

## Verordnung (EU) Nr. 1169/2011, Art. 13 + Anhang IV

---

## Kernbestimmung

> Art. 13 Abs. 2: Unbeschadet besonderer Unionsvorschriften für bestimmte
> Lebensmittel erscheinen die in Artikel 9 Absatz 1 aufgeführten
> verpflichtenden Angaben auf der Verpackung oder dem Etikett in einer
> Schriftgröße mit einer **x-Höhe von mindestens 1,2 mm**.

> Art. 13 Abs. 3: Bei Verpackungen oder Behältnissen, deren **größte
> Oberfläche weniger als 80 cm²** beträgt, beträgt die x-Höhe
> mindestens **0,9 mm**.

---

## x-Höhe erklärt

Die **x-Höhe** ist die Höhe des Kleinbuchstabens „x" (ohne Ober- und
Unterlängen). Dies ist **nicht** die volle Schrifthöhe.

| Schriftgröße (pt) | Ungefähre x-Höhe | Konform? (≥ 80 cm²) |
|-------------------|------------------|---------------------|
| 6 pt | ~1,0 mm | ❌ Nein |
| 7 pt | ~1,2 mm | ✅ Ja (Grenze) |
| 8 pt | ~1,4 mm | ✅ Ja |
| 9 pt | ~1,6 mm | ✅ Ja |
| 10 pt | ~1,8 mm | ✅ Ja |

**Achtung:** Die x-Höhe hängt von der **konkreten Schriftart** ab.
Arial 7 pt hat eine andere x-Höhe als Times New Roman 7 pt.

---

## Bedeutung für den Hub / Label Profiles

### Anforderungen an die Label Engine (ZPL)

1. **Mindest-Schriftgröße berechnen** basierend auf:
   - Labelfläche (Breite × Höhe)
   - x-Höhe der verwendeten ZPL-Schriftart
   - Ob die größte Oberfläche < 80 cm² ist

2. **Label Profile Erweiterung:**

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `min_font_size_pt` | int | Mindestschriftgröße in Punkten |
| `label_area_cm2` | float | Berechenbar aus Breite × Höhe |
| `small_label` | bool | True wenn < 80 cm² → 0,9 mm erlaubt |

### Typische Labelgrößen und Konformität

| Label-Format | Fläche | Mindest-x-Höhe | Empf. Schriftgröße |
|-------------|--------|----------------|-------------------|
| 60 × 40 mm | 24 cm² | 0,9 mm | ≥ 6 pt |
| 80 × 50 mm | 40 cm² | 0,9 mm | ≥ 6 pt |
| 100 × 70 mm | 70 cm² | 0,9 mm | ≥ 6 pt |
| 100 × 80 mm | 80 cm² | 1,2 mm | ≥ 7 pt |
| 100 × 150 mm | 150 cm² | 1,2 mm | ≥ 7 pt |

### ZPL-Implementierung

Die ZPL-Label-Engine muss:
- Die Labelfläche aus dem Profil berechnen
- Die Mindest-Schriftgröße als Floor-Wert setzen
- **Niemals** unter dem Floor-Wert drucken, auch wenn der Text nicht passt
- Bei Platzproblemen: Abkürzung/Mehrzeiler statt Schriftverkleinerung

---

## Ausnahmen

> Art. 13 Abs. 5: Bei Verpackungen mit einer **größten Oberfläche
> von weniger als 10 cm²** müssen nur folgende Angaben auf der
> Verpackung erscheinen:
> - Bezeichnung des Lebensmittels
> - Allergene
> - Nettofüllmenge
> - Mindesthaltbarkeitsdatum

→ Alle anderen Pflichtangaben können auf andere Weise bereitgestellt
werden (z.B. Website, Aushang).

---

## Quellen

- [LMIV Art. 13](https://eur-lex.europa.eu/eli/reg/2011/1169/art_13/oj)
- [LMIV Anhang IV](https://eur-lex.europa.eu/eli/reg/2011/1169/ann_IV/oj) (Nährstoffdeklaration — Darstellung)
