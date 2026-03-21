# RKSV — Registrierkassensicherheitsverordnung (Österreich)

> **Volltext:** [RIS BGBl. II Nr. 410/2015](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20009390)  
> **Anwendung:** Elektronische Kassen in Österreich

---

## §3 — Sicherheitseinrichtung

> Jede Registrierkasse muss eine **technische Sicherheitseinrichtung**
> enthalten, die sicherstellt, dass **Manipulationen an den
> aufgezeichneten Geschäftsvorfällen** erkennbar sind.
>
> Die Sicherheitseinrichtung besteht aus:
> - einer **Signaturerstellungseinheit** (Chipkarte, HSM)
> - einem **Datenerfassungsprotokoll** (DEP)
> - der **Verkettung** der Belege (jeder Beleg enthält den
>   Signaturwert des vorigen Belegs)

**Bedeutung für das System:**
Odoo POS muss RKSV-konform sein, wenn er in Österreich betrieben wird.
Das ist eine Anforderung an **Odoo**, nicht an den Hub.
Interessant: Die RKSV-Logik (Signaturverkettung) ist konzeptionell
verwandt mit dem Hub-Audit-Log (SHA-256-Hash-Chain).

---

## §4 — Belegerteilungspflicht

> Für jeden Geschäftsvorfall ist ein **Beleg** zu erstellen und
> dem Kunden auszuhändigen.
>
> Der Beleg muss enthalten:
> - Bezeichnung des Unternehmens
> - Datum und Uhrzeit
> - Menge und handelsübliche Bezeichnung
> - **Einzelpreis** und **Gesamtbetrag**
> - Maschinenlesbare Signatur (QR-Code)

**Bedeutung für das System:**
Der Bon wird vom Odoo POS erzeugt und enthält den RKSV-QR-Code.
Die Werte (Einzelpreis, Gesamtbetrag) kommen unverändert von der
Waage über den Hub. Der POS druckt sie nur — er berechnet sie nicht.

---

## Abgrenzung Hub vs. RKSV

| Aspekt | RKSV (Odoo POS) | Hub Audit Log |
|---|---|---|
| Zweck | Steuerliche Aufzeichnung | Metrologische Nachvollziehbarkeit |
| Signatur | Chipkarte/HSM (RKSV) | SHA-256 Hash-Chain |
| Pflicht | Gesetzlich (BAO §131b) | Freiwillig (WELMEC-Empfehlung) |
| Prüfer | Finanzamt | Eichamt / Notified Body |

Die beiden Systeme sind **komplementär**, nicht redundant.
