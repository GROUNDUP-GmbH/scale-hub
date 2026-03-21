# GS1 Digital Link — Standard für Web-URIs auf Produkten

> **Standard:** GS1 General Specifications v24  
> **Abschnitt:** Section 4 — GS1 Digital Link URI Syntax  
> **Volltext:** [gs1.org/standards/gs1-digital-link](https://www.gs1.org/standards/gs1-digital-link)

---

## §4.1 — Grundprinzip

> A GS1 Digital Link URI is a **Web URI** that contains a GS1
> identifier. It can be encoded in a **QR Code** and resolved to
> provide product information via the web.
>
> Struktur:
> ```
> https://{domain}/{ai}/{value}/{ai}/{value}/...
> ```

---

## Relevante Application Identifiers (AIs)

| AI | Bezeichnung | Format | Beispiel |
|---|---|---|---|
| **01** | GTIN (Global Trade Item Number) | N14 | `09012345678908` |
| **3103** | Nettogewicht in kg (3 Dezimalstellen) | N6 | `001250` = 1.250 kg |
| **3102** | Nettogewicht in kg (2 Dezimalstellen) | N6 | `000125` = 1.25 kg |
| **10** | Batch-/Chargennummer | X..20 | `LOT42` |
| **15** | Mindesthaltbarkeitsdatum | N6 (JJMMTT) | `260325` = 25.03.2026 |
| **21** | Seriennummer | X..20 | `SN001` |
| **8200** | Produkt-URL (Extended Packaging URL) | X..70 | `https://groundup.bio/p/101` |

---

## §4.3 — Beispiel für variable Ware

> Für variable Ware (z.B. Fleisch, Käse, Gemüse) wird die GTIN
> mit dem Nettogewicht kombiniert:
>
> ```
> https://groundup.bio/01/09012345678908/3103/001250/10/LOT42/15/260325
> ```
>
> Auflösung:
> - GTIN: 09012345678908
> - Gewicht: 1.250 kg
> - Charge: LOT42
> - MHD: 25.03.2026

**Bedeutung für das System:**
Genau diese Struktur erzeugt der `gs1.py`-Builder im Hub.
Die URL wird als QR-Code auf das ZPL-Label gedruckt.

---

## §4.5 — QR Code Data Carrier

> GS1 Digital Link URIs **sollen** in einem **QR Code Model 2**
> (ISO/IEC 18004) codiert werden.
>
> Error Correction Level: mindestens **M** (15%)

**Bedeutung für das System:**
Der ZPL-Generator verwendet `^BQN,2,5` — das ist QR Model 2
mit Error Correction Level M.

---

## §4.7 — Resolver

> Ein **GS1 Digital Link Resolver** ist ein Webservice, der die
> URI entgegennimmt und den Nutzer zu einer **Zielseite** weiterleitet.
>
> Der Resolver kann je nach Kontext (Consumer, Business, Regulator)
> unterschiedliche Informationen bereitstellen.

**Bedeutung für das System:**
`https://groundup.bio/01/...` wird langfristig auf eine Landingpage
zeigen: Herkunft, Landwirt, Charge, optional Carbon-/BodenKraft-Daten.
Das ist der Consumer-Experience-Layer — vollständig außerhalb der
metrologischen Kette.
