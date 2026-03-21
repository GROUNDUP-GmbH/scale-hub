# VO (EG) 178/2002 Art. 18 — Rückverfolgbarkeit

> **Norm:** Verordnung (EG) Nr. 178/2002, Artikel 18
> **Quelle:** [EUR-Lex](https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32002R0178)
> **Stand:** 2026-03-21

---

## Kernaussage

> (1) Die Rückverfolgbarkeit von Lebensmitteln [...] ist in allen Produktions-, Verarbeitungs- und Vertriebsstufen sicherzustellen.
>
> (2) Die Lebensmittel- und Futtermittelunternehmer müssen in der Lage sein, jede Person festzustellen, von der sie ein Lebensmittel [...] erhalten haben. Sie richten hierzu Systeme und Verfahren ein [...]. **["One step back"]**
>
> (3) Die Lebensmittel- und Futtermittelunternehmer müssen über Systeme und Verfahren verfügen, mit denen festgestellt werden kann, an welche Unternehmen ihre Erzeugnisse geliefert worden sind. **["One step forward"]**
>
> (4) [...] die Kennzeichnung oder Identifizierung durch einschlägige Dokumentation oder Informationen [...] zu erleichtern.

---

## Bedeutung für den Hub

Die GS1 Digital Link URI auf dem Label ermöglicht Rückverfolgbarkeit bis zur Charge:
- AI 01 (GTIN): Produkt-Identifikation
- AI 10 (Lot): Chargen-/Losnummer
- AI 21 (Serial): Optionale Serialisierung

Der Hub generiert die Losnummer automatisch (Datum + Sequenz) und speichert sie im Audit Log. Für LEH-Lieferungen ist die Chargen-Dokumentation Pflicht.
