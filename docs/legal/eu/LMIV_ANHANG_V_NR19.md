# LMIV Anhang V Nr. 19 — Ausnahme Nährwertdeklaration

> **Norm:** Verordnung (EU) Nr. 1169/2011, Anhang V, Nummer 19
> **Quelle:** [EUR-Lex](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32011R1169)
> **Stand:** 2026-03-21

---

## Kernaussage

> Lebensmittel, einschließlich handwerklich hergestellter Lebensmittel, die der Hersteller, der geringe Mengen von Erzeugnissen herstellt, **direkt an den Endverbraucher** oder an **lokale Einzelhandelsgeschäfte abgibt**, die die Erzeugnisse unmittelbar an den Endverbraucher abgeben.

---

## Interpretation

Die Ausnahme gilt für:
- Direktvermarktung ab Hof an Endverbraucher
- Lokale Abgabe an kleine Einzelhändler, die direkt an Endverbraucher verkaufen
- "Geringe Mengen" = nicht definiert in der LMIV; nationale Auslegung

Die Ausnahme gilt **NICHT** für:
- Belieferung von LEH-Ketten (Spar, Billa, Hofer, Lidl) — das sind keine "lokalen Einzelhandelsgeschäfte" im Sinne der Ausnahme
- Produkte unter Handelsmarke — hier gelten die vollen Anforderungen des Handelspartners
- Produkte, die über Zwischenhändler vertrieben werden

---

## Konsequenz für Label-Szenarien

| Szenario | Nährwertdeklaration | Begründung |
|---|---|---|
| LOOSE | Nicht erforderlich | Art. 44: lose Ware generell befreit |
| SIMPLE_PREPACK | **Befreit** | Anhang V Nr. 19: Direktvermarktung |
| FULL_PREPACK | **Befreit** | Anhang V Nr. 19: Direktvermarktung |
| LEH_PREPACK | **PFLICHT** | Anhang V Nr. 19 greift NICHT beim LEH |

---

## Bedeutung für den Hub

Die `compliance.yaml` steuert pro Szenario, ob `nutrition_declaration` = `required` oder `exempt`. Der Hub validiert: wenn Szenario = LEH_PREPACK und Nährwertdaten fehlen → Fehler, kein Label.
