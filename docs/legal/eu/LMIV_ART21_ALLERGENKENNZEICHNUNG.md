# LMIV Art. 21 — Allergenkennzeichnung (Hervorhebung)

## Verordnung (EU) Nr. 1169/2011, Art. 21 + Anhang II

---

## Kernbestimmung

> Art. 21 Abs. 1: Die in Anhang II genannten Stoffe oder Erzeugnisse
> müssen in der Zutatenliste durch einen **Schriftsatz** hervorgehoben
> werden, der sich von dem der übrigen Zutaten **deutlich abhebt**,
> z.B. durch **Schriftart, Stil oder Hintergrundfarbe**.

> Fehlt ein Zutatenverzeichnis, so umfasst die Angabe das Wort „Enthält",
> gefolgt von der Bezeichnung des Stoffs oder Erzeugnisses gemäß Anhang II.

---

## Anhang II — Die 14 Hauptallergene

| Nr. | Allergen | Beispiele |
|-----|----------|-----------|
| 1 | Glutenhaltiges Getreide | Weizen, Roggen, Gerste, Hafer, Dinkel |
| 2 | Krebstiere | Garnelen, Krabben, Hummer |
| 3 | Eier | Hühnereier, alle Ei-Derivate |
| 4 | Fisch | Alle Fischarten |
| 5 | Erdnüsse | Erdnüsse, Erdnussöl |
| 6 | Sojabohnen | Soja, Sojalecithin |
| 7 | Milch (Laktose) | Milch, Butter, Käse, Molke |
| 8 | Schalenfrüchte | Mandeln, Haselnüsse, Walnüsse, Cashew, Pistazien, etc. |
| 9 | Sellerie | Sellerie, Selleriesalz |
| 10 | Senf | Senf, Senfpulver |
| 11 | Sesamsamen | Sesam, Sesamöl |
| 12 | Schwefeldioxid/Sulphite | > 10 mg/kg oder mg/l (als SO₂) |
| 13 | Lupinen | Lupinenbohnen, Lupinenmehl |
| 14 | Weichtiere | Schnecken, Muscheln, Tintenfisch |

---

## Hervorhebungspflicht — Technische Umsetzung

### Erlaubte Hervorhebungsmethoden

Die LMIV schreibt **keine** spezifische Methode vor, sondern verlangt
„deutliches Abheben". Gängige Methoden:

| Methode | Beispiel | Empfohlen? |
|---------|----------|-----------|
| **GROSSBUCHSTABEN** | Weizenmehl, **MILCH**, Salz | ✅ Sehr verbreitet |
| **Fettdruck** | Weizenmehl, **Milch**, Salz | ✅ Gut lesbar |
| Unterstreichung | Weizenmehl, <u>Milch</u>, Salz | ⚠️ Weniger verbreitet |
| Hintergrundfarbe | Weizenmehl, [Milch], Salz | ⚠️ Im Druck schwierig |

### Empfehlung für ZPL-Labels

**GROSSBUCHSTABEN** sind die einfachste und zuverlässigste Methode
im Thermotransferdruck:

```
Zutaten: Weizenmehl, MILCH, Zucker, EIER, Salz, SENF
```

Fettdruck ist in ZPL-Fonts nur eingeschränkt verfügbar. GROSSBUCHSTABEN
funktionieren mit jeder Schriftart.

---

## Bedeutung für den Hub / Label Engine

### Anforderungen

1. **Allergene müssen in der Zutatenliste identifiziert sein**
   - Odoo-Produktstammdaten: Feld `allergens` (Liste der Anhang-II-Nummern)
   - Odoo-Produktstammdaten: Feld `ingredients` (Freitext Zutatenliste)

2. **Automatische Hervorhebung in der Label Engine**
   - Die ZPL-Engine muss Allergene in der Zutatenliste erkennen und
     automatisch in GROSSBUCHSTABEN umwandeln.
   - Matching auf Basis der Anhang-II-Stoff-Liste (mehrsprachig).

3. **Validierung**
   - Wenn `ingredients` vorhanden, aber `allergens` leer →
     Warnung (nicht blockierend, da allergenfreie Produkte existieren).
   - Wenn `allergens` vorhanden, aber kein Match in `ingredients` →
     Fehler (Allergen deklariert, aber nicht im Zutatenverzeichnis).

### Szenario-spezifisch

| Szenario | Allergenkennzeichnung |
|----------|----------------------|
| LOOSE | Mündlich + Aushang (AT: Allergen-VO); auf Label optional |
| SIMPLE_PREPACK | Pflicht in Zutatenliste, hervorgehoben |
| FULL_PREPACK | Pflicht in Zutatenliste, hervorgehoben |
| LEH_PREPACK | Pflicht in Zutatenliste, hervorgehoben |

---

## Nationale Besonderheiten

### Österreich — Allergeninformationsverordnung

Zusätzlich zur LMIV:
- Bei **loser Ware** (Marktstand, Hofladen): mündliche Information erlaubt,
  wenn ein **geschulter Mitarbeiter** anwesend ist.
- Alternativ: **Schriftlicher Aushang** mit Allergen-Codes (A–N).
- Details: → `at/ALLERGENINFO_VO_AT.md`

---

## Quellen

- [LMIV Art. 21](https://eur-lex.europa.eu/eli/reg/2011/1169/art_21/oj)
- [LMIV Anhang II](https://eur-lex.europa.eu/eli/reg/2011/1169/ann_II/oj)
- [Allergeninformationsverordnung (AT)](https://www.ris.bka.gv.at/eli/bgbl/II/2014/175)
