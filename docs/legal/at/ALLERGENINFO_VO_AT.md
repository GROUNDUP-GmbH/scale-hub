# Allergeninformationsverordnung (AT)

> **Norm:** BGBl. II Nr. 175/2014
> **Quelle:** [RIS](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20008870)
> **Stand:** 2026-03-21

---

## Kernaussage

> § 2. Bei nicht vorverpackten Lebensmitteln [...] kann die Information über Allergene und Unverträglichkeiten auslösende Stoffe und Erzeugnisse den Konsumentinnen und Konsumenten **mündlich** erteilt werden, sofern
> 1. an gut sichtbarer Stelle ein Hinweis angebracht ist, dass die Allergeninformation **mündlich eingeholt** werden kann, und
> 2. eine **schriftliche Dokumentation** über die in den Lebensmitteln enthaltenen Allergene vorliegt und auf **Verlangen vorgezeigt** werden kann.

> § 3. Die Personen, die Allergeninformation erteilen, müssen über eine **Schulung** verfügen.

---

## Praxis-Relevanz

| Verkaufsform | Allergen-Pflicht | Art |
|---|---|---|
| Wochenmarkt lose | Mündlich + Schild + Backup-Liste | AIV § 2 |
| Hofladen lose | Mündlich + Schild + Backup-Liste | AIV § 2 |
| Vorverpackt (alle) | Auf dem Label, **fett hervorgehoben** | LMIV Art. 21 |

---

## Bedeutung für den Hub

Für `scenario=LOOSE` muss der Hub keine Allergen-Labels drucken, aber der Landwirt muss eine schriftliche Backup-Liste haben. Der Hub kann optional eine Allergen-Übersichtsliste generieren. Für vorverpackte Szenarien werden Allergene **fett** im Zutatenverzeichnis markiert (`^AF` bold in ZPL).
