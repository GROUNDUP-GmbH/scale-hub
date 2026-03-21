# WELMEC Guide 7.2 — Software Guide

> **Volltext:** [welmec.org/guides/7.2](https://www.welmec.org/welmec/documents/guides/7.2/)  
> **Version:** Issue 5 (2020)  
> **Anwendungsbereich:** Software in Messgeräten und Subsystemen

---

## §4.2 — Separation of Software

> Legally relevant software must be **clearly separated** from
> legally non-relevant software. The separation may be:
>
> - **Physical** (separate hardware)
> - **Logical** (separate processes, containers, partitions)
>
> A **terminal** is defined as a digital device with keys/touchscreen
> etc. that **operates the instrument** and **displays weighing results**.

**Bedeutung für das System:**
Der Hub ist physisch von der Waage getrennt (eigene Hardware).
Entscheidend: Der POS darf kein „Terminal" im Sinne von WELMEC werden.
Wenn er die Waage direkt steuern und Wägeergebnisse anzeigen würde,
wäre er ein Terminal → Teil des Messgeräts → zertifizierungspflichtig.
Deshalb: POS sendet nur `product_id`, nicht Waagen-Kommandos.

---

## §4.3 — Protection of Legally Relevant Software

> Legally relevant software shall be **secured against unauthorized
> modification**. This includes:
>
> - **Sealing** (physical or electronic)
> - **Software identification** (version display, checksum)
> - **Access control** (passwords, keys)
>
> The means of protection must be **proportionate to the risk**.

**Bedeutung für das System:**
Dies ist die Rechtsgrundlage für **Secure Boot (ADR-07)**. Obwohl der
Hub keine „legally relevant software" im engeren Sinne enthält, stützt
sich die gesamte Argumentation „Hub = nicht manipulierbar" auf genau
diese Schutzmaßnahmen. Secure Boot + dm-verity erfüllen §4.3 auf
dem höchsten Schutzniveau.

---

## §4.4 — Interfaces

### §4.4.2.1 — Requirements for Interfaces

> **(a)** Commands received via communication interfaces must **not
> inadmissibly influence** legally relevant software, device-specific
> parameters, or measurement data.
>
> **(b)** Only **documented commands** shall be effective. Commands that
> are **not documented** shall have **no effect** on legally relevant
> functions.
>
> **(c)** Interfaces that could have an **inadmissible influence** on
> legally relevant software must be **sealed or otherwise protected**.

**Bedeutung für das System:**
- **(a):** Der Hub darf über RS-232 Port A nur Konfigurationskommandos
  senden (PLU-Auswahl). Keine Befehle, die Messwerte beeinflussen.
- **(b):** Grundlage der **Allowlist** (Decision 03). Nur vordefinierte
  PLU-IDs sind erlaubt. Alles andere wird verworfen.
- **(c):** Port B ist physisch unidirektional (TX only von der Waage).
  Eine Beeinflussung über diesen Port ist hardwareseitig unmöglich.

---

## §4.5 — Software Identification and Audit Trail

> The software version must be **identifiable** (e.g., displayed or
> printable). Changes to software or parameters that affect legally
> relevant functions must be **recorded** in an **audit trail**.
>
> The audit trail must:
> - Record **who** made the change
> - Record **when** the change was made
> - Record **what** was changed
> - Be **protected against unauthorized modification**

**Bedeutung für das System:**
Direkte Rechtsgrundlage für das **Hash-verkettete Audit Log (Decision 04)**.
Jeder PLU-Upload, jede Produktauswahl, jeder Verkauf wird mit
Zeitstempel, Benutzer und Hash-Kette protokolliert. Das Log ist
append-only und durch die SHA-256-Kette gegen Manipulation geschützt.

---

## §5.3 — Non-legally Relevant Parts

> Parts of the measuring system that do **not** perform legally
> relevant functions and do **not** influence legally relevant parts
> are considered **non-legally relevant**. They do **not** need to
> fulfil the requirements of this guide.
>
> However, the **interface** between legally relevant and non-relevant
> parts must be **clearly defined** and **protected** per §4.4.

**Bedeutung für das System:**
Dies ist die **zentrale Passage** für die Einstufung des Hubs.
Der Hub ist ein „non-legally relevant part", **wenn und solange**:
1. Er keine metrologischen Funktionen ausführt (keine Messung, keine Preisberechnung)
2. Er die metrologischen Funktionen der Waage nicht beeinflusst
3. Die Schnittstelle klar definiert und geschützt ist (§4.4)

Alle drei Bedingungen werden durch die Architektur erfüllt.
