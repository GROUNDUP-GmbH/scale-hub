# LMIV Art. 9 — Pflichtangaben auf vorverpackten Lebensmitteln

> **Norm:** Verordnung (EU) Nr. 1169/2011, Artikel 9
> **Quelle:** [EUR-Lex](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32011R1169)
> **Stand:** 2026-03-21

---

## Vollständige Liste der Pflichtangaben (Art. 9 Abs. 1)

> a) die Bezeichnung des Lebensmittels;
> b) das Verzeichnis der Zutaten;
> c) alle in Anhang II aufgeführten Zutaten und Verarbeitungshilfsstoffe [...] die Allergien und Unverträglichkeiten auslösen;
> d) die Menge bestimmter Zutaten oder Klassen von Zutaten;
> e) die Nettofüllmenge des Lebensmittels;
> f) das Mindesthaltbarkeitsdatum oder das Verbrauchsdatum;
> g) gegebenenfalls besondere Anweisungen für Aufbewahrung und/oder Verwendung;
> h) der Name oder die Firma und die Anschrift des Lebensmittelunternehmers [...];
> i) das Ursprungsland oder der Herkunftsort [...];
> j) eine Gebrauchsanleitung, falls es schwierig wäre, das Lebensmittel ohne eine solche angemessen zu verwenden;
> k) für Getränke mit einem Alkoholgehalt von mehr als 1,2 Volumenprozent die Angabe des vorhandenen Alkoholgehalts;
> l) eine Nährwertdeklaration.

---

## Mapping auf Hub-Felder

| LMIV Buchstabe | Pflichtangabe | Hub-Feld | Szenario |
|---|---|---|---|
| a) | Bezeichnung | `product_name` | Alle |
| b) | Zutaten | `ingredients` | FULL_PREPACK, LEH_PREPACK |
| c) | Allergene | `allergens` | FULL_PREPACK, LEH_PREPACK |
| e) | Nettofüllmenge | `weight_kg` | Alle Prepack |
| f) | MHD | `best_before_date` (berechnet aus `shelf_life_days`) | Alle Prepack |
| g) | Aufbewahrung | `storage_instructions` | FULL_PREPACK, LEH_PREPACK |
| h) | Betrieb | `operator_name` + `operator_address` | Alle Prepack |
| i) | Herkunft | `origin` | Alle Prepack |
| l) | Nährwert | `nutrition_*` (Big Seven) | LEH_PREPACK |

---

## Bedeutung für den Hub

Der Hub muss pro Label-Szenario sicherstellen, dass alle Pflichtfelder nach Art. 9 vorhanden sind. Die `compliance.yaml` pro Land definiert, welche Felder für welches Szenario Pflicht sind. Bei fehlenden Pflichtfeldern muss der Hub die Label-Generierung ablehnen.
