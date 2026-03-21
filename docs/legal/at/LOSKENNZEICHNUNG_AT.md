# Loskennzeichnung (AT / EU)

> **Norm:** Richtlinie 2011/91/EU, umgesetzt durch Loskennzeichnungsverordnung (AT)
> **Quelle:** [EUR-Lex](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32011L0091)
> **Stand:** 2026-03-21

---

## Kernaussage

> Art. 1 (1): Ein Los ist die Gesamtheit von Verkaufseinheiten eines Lebensmittels, das unter **praktisch gleichen Umständen** erzeugt, hergestellt oder verpackt wurde.

> Art. 2: Die Losangabe besteht aus dem Buchstaben **„L"**, gefolgt von der **Losangabe**.

## Ausnahme

> Art. 3 (1)(b): Die Losangabe ist **nicht erforderlich**, wenn das **Mindesthaltbarkeitsdatum** [...] mindestens den **Tag und den Monat** [...] umfasst.

---

## Praxis

| Situation | Los auf Label? | Begründung |
|---|---|---|
| MHD mit Tag + Monat vorhanden | Nein (optional) | Art. 3 (1)(b) |
| MHD nur mit Monat + Jahr | **Ja, Pflicht** | Art. 2 |
| Kein MHD (z.B. Honig, Zucker) | **Ja, Pflicht** | Art. 2 |

---

## Bedeutung für den Hub

Der Hub generiert die Losnummer automatisch im Format `L{YYYYMMDD}-{SEQ}` (z.B. `L20260321-001`). In der GS1 Digital Link URI wird die Losnummer als AI 10 codiert. Wenn das MHD Tag+Monat enthält, ist die Losnummer optional aber empfohlen (für Rückverfolgbarkeit).
