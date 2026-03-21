# BAO § 131b — Registrierkassenpflicht & Kalte-Hände-Regelung (AT)

> **Norm:** Bundesabgabenordnung § 131b, BGBl. I Nr. 194/1961 idgF
> **Quelle:** [RIS](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=10003940)
> **Stand:** 2026-03-21

---

## Registrierkassenpflicht

> § 131b. (1) [...] Betriebe haben alle **Bareinnahmen** zum Zweck der Losungsermittlung einzeln mit Hilfe einer **elektronischen Registrierkasse** [...] zu erfassen, wenn
> der Jahresumsatz des Betriebes **15.000 Euro** und
> die Barumsätze des Betriebes **7.500 Euro** übersteigen.

## Kalte-Hände-Regelung (Outdoor-Befreiung)

> (3a) Absatz 1 [...] gilt **nicht** für Umsätze, die von einem **im Freien betriebenen Unternehmen** oder an einem solchen Standort [...] getätigt werden, wenn die jeweiligen Umsätze aus dieser Tätigkeit den Betrag von **45.000 Euro (netto) jährlich** nicht übersteigen.

### Wichtig: Nur Freiluft-Umsätze!

Die 45.000 EUR-Grenze gilt **ausschließlich** für die Umsätze, die im Freien getätigt werden (Wochenmarkt, Feldverkauf). Sie bezieht sich **nicht** auf den Gesamtumsatz des Unternehmens. Der Landwirt kann 500.000 EUR Gesamtumsatz haben — solange seine Markt-Umsätze unter 45k bleiben, ist er am Markt befreit.

---

## Belegerteilungspflicht

> § 132a. (1) Wer Barzahlungen entgegennimmt, hat einen **Beleg** zu erstellen und dem Zahlenden auszufolgen.

Die Belegerteilungspflicht gilt **immer** ab der ersten Registrierkassenpflicht — aber die Kalte-Hände-Regelung befreit gleichzeitig auch von der Belegerteilung für die Freiluft-Umsätze.

---

## Zusammenfassung

| Schwellwert | Pflicht | Quelle |
|---|---|---|
| > 15.000 EUR Jahresumsatz UND > 7.500 EUR bar | Registrierkasse | BAO § 131b (1) |
| > 45.000 EUR netto Freiluft-Umsatz (ab 2026) | Registrierkasse auch am Markt | BAO § 131b (3a) |
| Unter 45k Freiluft | Weder Kasse noch Beleg am Markt | BAO § 131b (3a) |

---

## Bedeutung für den Hub

Der Hub konfiguriert über `compliance.yaml`, ob ein Bon-Druck ausgelöst wird. In AT kann der Landwirt am Markt unter 45k EUR netto ohne Bon verkaufen. Überschreitet er die Grenze, muss der Odoo POS RKSV-konforme Belege erzeugen.
