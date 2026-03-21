# BEV Informationsblatt — POS-Systeme (2023)

> **Norm:** Informationsblatt für Verwender von POS-Systemen, Version 02
> **Herausgeber:** Bundesamt für Eich- und Vermessungswesen (BEV)
> **Kontakt:** Eichstellen@bev.gv.at, DI Dr. Christian Buchner MSc
> **Quelle:** BEV, GZ BMWA-96.109/0220-I/11/2007
> **Stand:** 2026-03-21

---

## Definition POS-System

> POS-Systeme im Rahmen dieses Informationsblattes bestehen zumindest aus einer **eichfähigen Waage in Verbindung mit einem Kassensystem** (POS-device).

## Voraussetzung für die Eichfähigkeit

> - Die Waage muss über eine EU-Bauartzulassung oder eine innerstaatliche Zulassung zur Eichung verfügen.
> - **Kassensystem und Software müssen über eine gültige Prüfbescheinigung verfügen.**
> - Waage und Kassensystem dürfen **nur dann verbunden werden, wenn dies auch in den entsprechenden Zulassungen und Prüfbescheinigungen vorgesehen ist.**
> - Jede Änderung der eichpflichtigen Software sowie der Austausch des PCs **erfordert eine Neueichung** des POS-Systems.
> - Der **Waagenverwender** ist für das Gesamtsystem verantwortlich.

---

## Abgrenzung: Warum der GroundUp Hub KEIN POS-System ist

| Kriterium | POS-System (BEV-Def.) | GroundUp Hub |
|---|---|---|
| Waage + Kasse verbunden | Ja, direkt | Nein — Hub dazwischen, POS hat keine Waagen-Verbindung |
| Kasse berechnet Preise | Möglich | Nein — nur Waage berechnet (Decision 01) |
| Prüfbescheinigung nötig | Ja | Nein — Hub ist kein Kassensystem |
| Software-Update = Neueichung | Ja | Nein — Hub-Updates unabhängig von Waagen-Eichung |
| Verantwortung Waagenverwender | Für Gesamtsystem | Nur für Waage (Hub = separates System) |

---

## Strategische Bedeutung

Dieses BEV-Informationsblatt bestätigt die Architekturentscheidung (Decision 08): Durch die Trennung von Waage, Hub und POS in drei unabhängige Systeme vermeiden wir die POS-System-Definition des BEV. Der Hub ist weder Waage noch Kassensystem.

**Phase 2 (Marktprodukt):** Für die Vermarktung des Hubs als eigenständiges Produkt wäre eine eigene Prüfbescheinigung für den zertifizierten Hub-Kern (Certified Core + Waage) ein Wettbewerbsvorteil. Odoo bleibt außerhalb der Zertifizierungsgrenze. Geschätzte Kosten: 10–25k EUR für den Kern, 6–12 Monate.
