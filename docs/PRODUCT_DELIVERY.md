# Scale Hub — Produktisierung & Auslieferung

**Version:** 1.0 — 22. März 2026
**Bezug:** [SECURE_BOOT.md](SECURE_BOOT.md), [CERTIFICATION_CHECKLIST.md](CERTIFICATION_CHECKLIST.md)

---

## 1. Physisches Produkt: Was wird geliefert?

### 1.1 Bill of Materials (BOM)

| # | Komponente | Spezifikation | Kosten (ca.) |
|---|-----------|---------------|-------------|
| 1 | Raspberry Pi 5 | 4 GB RAM, BCM2712 | € 62 |
| 2 | Offizielles Pi 5 Gehäuse | Raspberry Pi Case (rot/weiß) mit Lüfter | € 10 |
| 3 | microSD-Karte | Samsung EVO Plus 32 GB, Class 10 | € 12 |
| 4 | USB-C Netzteil | Official Pi 5 27W (5V/5A) | € 12 |
| 5 | Ethernet-Kabel | Cat5e, 2m, RJ45 | € 5 |
| 6 | Tamper-Evident Siegel (2x) | Holographisch, VOID, serialisiert | € 1 |
| 7 | Quick Start Card | Laminierte Kurzanleitung mit QR-Code | € 1 |
| 8 | Verpackung | Karton mit Ground UP Branding | € 3 |
| **Gesamt** | | | **~ € 106** |

### 1.2 Optionales Zubehör

| Komponente | Wann nötig? | Kosten |
|-----------|-------------|--------|
| RS-232 USB-Adapter (FTDI) | Für serielle Waagen (CAS ER, LP, etc.) | € 15 |
| USB-RS232 Kabel | Alternative zum Adapter | € 12 |
| NXP SE050 Development Kit | Für Hardware-Audit-Signierung (Phase 2) | € 35 |
| PoE HAT | Power-over-Ethernet (kein extra Netzteil) | € 20 |

---

## 2. Software: Was ist vorinstalliert?

### 2.1 Basis-Image (jedes Gerät)

```
┌─────────────────────────────────────────────────────┐
│  Ground UP Scale Hub OS (basierend auf Raspberry Pi OS Lite 64-bit)  │
├─────────────────────────────────────────────────────┤
│  Certified Core (immer installiert, read-only)      │
│  ├── hub/core/types.py          Integer-Typen       │
│  ├── hub/core/sale_processor.py  Preisberechnung    │
│  ├── hub/core/audit_log.py      Hash-Chain-Log      │
│  ├── hub/core/sealed_config.py  HMAC-gesiegelte Cfg │
│  ├── hub/core/state_machine.py  Transaktions-FSM    │
│  ├── hub/core/serial_port.py    RS-232 Treiber      │
│  └── hub/core/version.py        SW-Identifikation   │
├─────────────────────────────────────────────────────┤
│  Periphery (immer installiert, updatebar)           │
│  ├── hub/periphery/api.py       FastAPI Server      │
│  ├── hub/periphery/label_engine.py  Etiketten       │
│  └── hub/periphery/gs1.py       GS1 Digital Link    │
├─────────────────────────────────────────────────────┤
│  Adapter Registry (modular, OTA-steuerbar)          │
│  ├── hub/adapters/base.py       ScaleAdapter Proto  │
│  └── hub/adapters/*.py          Alle 8 Adapter      │
├─────────────────────────────────────────────────────┤
│  System                                              │
│  ├── RAUC (A/B OTA Update Client)                   │
│  ├── Docker CE (für isolierte Dienste)              │
│  ├── NetworkManager (Ethernet + optional WLAN)      │
│  └── systemd (Service Management)                   │
└─────────────────────────────────────────────────────┘
```

### 2.2 Adapter-Strategie: Alle vorinstalliert, selektiv aktiviert

**Entscheidung:** Alle 8 Adapter werden im Image **ausgeliefert**, aber nur die
konfigurierten Adapter werden **geladen**. Gründe:

1. **Kein OTA nötig** für Adapter-Wechsel — nur Config-Änderung
2. **Gesamtgröße** aller Adapter: < 200 KB — irrelevant
3. **Kein Sicherheitsrisiko** — Adapter ohne Verbindung sind inaktiv
4. **Einfacheres Testing** — ein Image für alle Kunden

```yaml
# config.yaml — Adapter werden nur geladen wenn hier konfiguriert
scales:
  - name: "Meine DIGI"
    adapter: digi_sm          # ← Nur dieser Adapter wird geladen
    connection:
      type: ethernet
      host: "192.168.1.50"
      port: 3001
```

### 2.3 Was per OTA aktualisiert wird

| Komponente | OTA-updatebar? | Wie? |
|-----------|---------------|------|
| Certified Core | Ja (signiertes A/B-Update) | Ganzes Rootfs-Update via RAUC |
| Periphery | Ja (signiertes A/B-Update) | Ganzes Rootfs-Update via RAUC |
| Adapter | Ja (als Teil des Rootfs) | Ganzes Rootfs-Update via RAUC |
| Config (Waagen, Odoo-URL) | Ja (separate Data-Partition) | API-Aufruf oder Odoo-Push |
| Linux Kernel | Ja (signiertes A/B-Update) | Teil des RAUC-Bundles |
| Bootloader | Nein (OTP-gesiegelt) | Nur bei Hardware-Tausch |

---

## 3. Physisches Siegel (Tamper-Evident)

### 3.1 Warum?

WELMEC 7.2 §4 und EN 45501 Annex D fordern bei metrological relevanten Geräten
den **Schutz vor unbefugtem Zugriff** auf Hardware und Software-Parameter.
Auch wenn der Hub in Tier 1 (Waage rechnet) nicht zwingend ein Eichsiegel
braucht, erhöht ein physisches Siegel die **rechtliche Verteidigungsfähigkeit**
erheblich — und ist für Tier 0 (Hub rechnet) **verpflichtend**.

### 3.2 Siegel-Spezifikation

| Eigenschaft | Spezifikation |
|-------------|---------------|
| **Typ** | Holographisches VOID-Siegel (selbstzerstörend) |
| **Material** | Polyester, tamper-evident, nicht rückstandsfrei |
| **Effekt** | Bei Ablösung: sichtbares "VOID" / "OPENED" Muster |
| **Serialisierung** | Fortlaufende Nummer + QR-Code → Hub-Datenbank |
| **Größe** | 25mm × 15mm (oval) |
| **Aufschrift** | `GROUND UP · SEALED · SN:XXXXX · groundup.farm/verify` |
| **Temperaturbereich** | −40°C bis +120°C |
| **Zertifizierung** | RoHS, REACH-konform |
| **Lieferant** | z.B. Intertronix TamperMax oder lokaler Hersteller |

### 3.3 Siegel-Platzierung (2 Stück pro Gerät)

```
┌─────────────────────────────────────┐
│     Pi 5 Official Case (Draufsicht) │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Oberschale (rot)             │  │
│  │                               │  │
│  │       [Lüftungsgitter]        │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Unterschale (weiß)           │  │
│  │                               │  │
│  │  ┌──────────┐                 │  │
│  │  │ SIEGEL 1 │ ← Überbrückt   │  │
│  │  │ SN:00001 │   Ober- und    │  │
│  │  └──────────┘   Unterschale   │  │
│  │                 (Gehäuse-     │  │
│  │                  Öffnung      │  │
│  │                  erkennbar)   │  │
│  └───────────────────────────────┘  │
│                                     │
│  Seitenansicht (SD-Karten-Slot):    │
│  ┌─────┬────────┬─────────────────┐ │
│  │     │ [SD]   │                 │ │
│  │     │SIEGEL 2│                 │ │
│  │     │SN:00002│                 │ │
│  └─────┴────────┴─────────────────┘ │
│         ↑ Überdeckt SD-Karten-Slot   │
│           (Entnahme = Siegel-Bruch)  │
└─────────────────────────────────────┘
```

**Siegel 1 — Gehäuse:** Überbrückt die Fuge zwischen Ober- und Unterschale.
Jedes Öffnen des Gehäuses zerstört das Siegel sichtbar (VOID-Muster).

**Siegel 2 — SD-Slot:** Überdeckt den microSD-Karten-Einschub. Entnahme
oder Tausch der SD-Karte ist ohne Siegel-Bruch nicht möglich.

### 3.4 Siegel-Verifikation

Jede Siegel-Seriennummer wird bei der Produktion in der Hub-Datenbank
(Odoo) registriert:

```
Hub SN: GU-HUB-2026-00042
├── Siegel 1 (Gehäuse): SEAL-2026-A-00083
├── Siegel 2 (SD-Slot): SEAL-2026-A-00084
├── Produktion: 2026-03-22
├── Software-Version: 1.0.0-rc1
└── Auslieferung an: Osttirol Genuss GmbH
```

**Verifikations-URL:** `https://groundup.farm/verify/SEAL-2026-A-00083`
→ Zeigt: Ist das Siegel echt? Zu welchem Hub gehört es? Status?

---

## 4. Software-Siegel (WELMEC 7.2 konform)

### 4.1 Die 5 WELMEC-Prinzipien und ihre Umsetzung

| WELMEC-Prinzip | Anforderung | Hub-Umsetzung |
|---------------|-------------|---------------|
| **Authenticity** | Software-Herkunft prüfbar | Secure Boot (OTP → signierter Bootloader → dm-verity Rootfs) |
| **Integrity** | Manipulation erkennbar | dm-verity Hash-Baum über gesamtes Rootfs |
| **Traceability** | Änderungen nachvollziehbar | Audit Log (hash-chained, append-only) |
| **Identification** | Jede Änderung = neue Version | `hub/core/version.py` → SHA256-Hash des Certified Core |
| **Robustness** | Schutz gegen externe Einflüsse | Read-only Rootfs, AppArmor, kein Root-Login |

### 4.2 Software-Identifikation (der "digitale Siegel")

Der Hub berechnet beim Boot einen **Software-Identifikationswert**:

```python
# hub/core/version.py (bereits implementiert)
# Berechnet SHA256 über alle Dateien im Certified Core
#
# Dieser Hash ist das "Software-Siegel" im Sinne von WELMEC 7.2 §4.5
# Er ändert sich bei JEDER Änderung am Certified Core
```

**Anzeige:** Der Software-ID-Hash wird angezeigt über:
- Hub API: `GET /api/v1/version` → JSON mit Hash
- Hub Display (wenn vorhanden): Permanent sichtbar
- Audit Log: In jeder Log-Zeile als Prefix

**Prüfung durch Eichbeamten:**
1. Beamter ruft `GET /api/v1/version` auf
2. Vergleicht Hash mit dem im Type Examination Certificate hinterlegten Wert
3. Stimmt überein → Software ist unverändert

### 4.3 Secure Boot Chain (Pi 5)

```
┌──────────────────────────────────────────────────────┐
│  Boot ROM (Mask ROM im BCM2712, unveränderbar)       │
│  └─→ Prüft RSA-2048 Signatur via OTP Key Hash       │
│                                                       │
│  Signierter Bootloader (boot_a / boot_b)             │
│  └─→ Prüft Signatur von Kernel + Device Tree         │
│                                                       │
│  Signierter Kernel                                    │
│  └─→ dm-verity Root Hash in Kernel-Cmdline            │
│                                                       │
│  Read-Only Rootfs (dm-verity verifiziert)             │
│  └─→ Scale Hub Software (Certified Core + Adapters)   │
│                                                       │
│  Data-Partition (RW, LUKS-verschlüsselt)              │
│  └─→ config.yaml, Audit Logs, Sealed Config           │
└──────────────────────────────────────────────────────┘
```

**Ergebnis:** Kein Bit auf dem gesamten System kann verändert werden, ohne
dass entweder der Boot fehlschlägt (Secure Boot) oder der Hash sich ändert
(dm-verity / Software-ID).

---

## 5. OTA-Update-System (RAUC)

### 5.1 Warum RAUC?

| Kriterium | RAUC | Thistle | Mender | Eigenbau |
|-----------|------|---------|--------|----------|
| Open Source | Ja (LGPL-2.1) | Nein | Teils | — |
| Pi 5 Support | Ja (Bootlin verifiziert) | Ja | Experimentell | — |
| A/B Partitioning | Ja | Ja | Ja | Aufwändig |
| dm-verity Integration | Ja (Bundle-Format "verity") | Nein | Nein | Aufwändig |
| Signierung | X.509 Zertifikate | Proprietär | Proprietär | — |
| Rollback | Automatisch (Boot-Fail) | Ja | Ja | — |
| Downgrade-Schutz | Ja (min-bundle-version) | Ja | Ja | — |
| Kosten | € 0 | €€€ | €€ | Entwicklungszeit |

### 5.2 Partitions-Layout (SD-Karte, 32 GB)

```
mmcblk0 (32 GB microSD)
├── p1: boot_a     (256 MB, FAT32, signiert)        ← Aktiv
├── p2: boot_b     (256 MB, FAT32, signiert)        ← Standby
├── p3: rootfs_a   (4 GB, ext4/squashfs, dm-verity) ← Aktiv
├── p4: rootfs_b   (4 GB, ext4/squashfs, dm-verity) ← Standby
├── p5: data       (8 GB, ext4, LUKS-verschlüsselt) ← Persistent
│   ├── config.yaml
│   ├── audit_logs/
│   ├── sealed_config.json
│   └── rauc/       (Update-Status, Slot-Marker)
└── p6: recovery   (512 MB, read-only, Notfall)
    Restlicher Platz: unpartitioniert (Reserve)
```

### 5.3 Update-Ablauf

```
1. Hub prüft periodisch (oder via Odoo-Push):
   GET https://updates.groundup.farm/scale-hub/latest.json
   → { "version": "1.1.0", "url": "...", "sha256": "..." }

2. Download des RAUC-Bundles (signiert):
   scale-hub-1.1.0.raucb (~50-100 MB)

3. RAUC verifiziert:
   a) Bundle-Signatur (X.509 gegen eingebetteten Keyring)
   b) Kompatibilitäts-String ("groundup-scale-hub")
   c) min-bundle-version (kein Downgrade möglich)

4. Installation auf Standby-Slot:
   boot_b + rootfs_b werden überschrieben

5. dm-verity Hash wird geprüft

6. Slot-Status: boot_b markiert als "good" + "primary"

7. Reboot → System startet von boot_b + rootfs_b

8. Health-Check:
   - Hub-API erreichbar? ✓
   - Waagen verbunden? ✓
   - Audit-Log schreibbar? ✓
   → Wenn ALLE ✓: Slot als "confirmed" markieren
   → Wenn EINER ✗: Automatischer Rollback zu boot_a + rootfs_a

9. Audit Log: UPDATE_APPLIED { from: "1.0.0", to: "1.1.0", hash: "..." }
```

### 5.4 Was ein Update beinhalten kann

| Inhalt | Beispiel |
|--------|---------|
| Neuer Adapter | z.B. `bizerba.py` für Bizerba-Waagen |
| Bugfix im Core | z.B. Rundungsfehler in `sale_processor.py` |
| Neue Periphery-Funktion | z.B. QR-Code auf Etikett |
| Kernel-Update | Sicherheitspatch |
| System-Bibliotheken | Python-Version, OpenSSL |
| Neue Länder-Compliance | z.B. `docs/legal/de/compliance.yaml` |

### 5.5 Was ein Update NICHT ändern kann

| Bereich | Warum nicht? |
|---------|-------------|
| Boot-Signing-Key | OTP (einmal programmiert, unveränderbar) |
| Kunden-Config (Waagen-IPs, Odoo-URL) | Data-Partition (persistent, nicht überschrieben) |
| Audit Logs | Data-Partition (persistent, append-only) |
| Sealed Config HMAC-Secret | Data-Partition (per-Gerät, nie im Image) |

---

## 6. Provisioning-Pipeline (Produktion)

### 6.1 Werkzeuge

| Tool | Zweck |
|------|-------|
| `rpi-sb-provisioner` | Raspberry Pi Secure Boot Provisioning (~3 Min/Gerät) |
| `rpi-image-gen` | Custom OS-Image mit Scale Hub Software |
| `rauc` | Bundle-Erstellung + Signierung |
| YubiHSM 2 | Hardware Security Module für Signing Key |

### 6.2 Produktions-Ablauf (pro Gerät)

```
┌─────────────────────────────────────────────────────────────┐
│  SCHRITT 1: Image flashen (~5 Min)                         │
│                                                             │
│  Provisioning-PC                                            │
│  ├── Flash Scale Hub Image auf microSD                      │
│  ├── Generiere einzigartiges HMAC-Secret                    │
│  ├── Generiere einzigartige Geräte-ID (GU-HUB-YYYY-NNNNN) │
│  └── Schreibe Config auf Data-Partition                     │
└─────────────────────────────────┬───────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────┐
│  SCHRITT 2: Secure Boot Provisioning (~3 Min)              │
│                                                             │
│  rpi-sb-provisioner                                         │
│  ├── Programmiere OTP mit Ground UP Public Key Hash         │
│  ├── Signiere Boot-Partition mit YubiHSM                    │
│  └── Verifiziere: Gerät bootet nur signierte Images         │
└─────────────────────────────────┬───────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────┐
│  SCHRITT 3: Smoke Test (~2 Min)                            │
│                                                             │
│  Automatisierter Test:                                      │
│  ├── Boot erfolgreich?                                      │
│  ├── API erreichbar? (GET /api/v1/version)                  │
│  ├── Software-ID korrekt?                                   │
│  ├── Audit Log funktioniert?                                │
│  └── Loopback-Test (simulierte Waage)?                      │
└─────────────────────────────────┬───────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────┐
│  SCHRITT 4: Versiegeln + Verpacken (~2 Min)                │
│                                                             │
│  ├── Pi in offizielles Gehäuse einbauen                     │
│  ├── Siegel 1 auf Gehäuse-Fuge kleben (SN registrieren)    │
│  ├── SD-Karte einsetzen                                     │
│  ├── Siegel 2 über SD-Slot kleben (SN registrieren)        │
│  ├── Quick Start Card beilegen                              │
│  ├── Netzteil + Ethernet-Kabel beilegen                     │
│  └── Versandkarton versiegeln                               │
└─────────────────────────────────┬───────────────────────────┘
                                  │
│  SCHRITT 5: Registration (~1 Min)                          │
│                                                             │
│  In Odoo (Ground UP CRM):                                   │
│  ├── Gerät anlegen (SN, MAC, Software-Version)              │
│  ├── Siegel-Nummern verknüpfen                              │
│  ├── Kundenzuordnung                                        │
│  └── Garantie-Start-Datum setzen                            │
│                                                             │
│  Gesamt pro Gerät: ~13 Minuten                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Qualitätskontrolle

| Prüfung | Automatisch? | Kriterium |
|---------|-------------|-----------|
| Secure Boot aktiv | Ja | OTP-Readback = erwarteter Key-Hash |
| Software-ID | Ja | SHA256 = Release-Hash |
| API-Health | Ja | HTTP 200 auf `/api/v1/health` |
| Audit Log Integrity | Ja | Hash-Chain verifizierbar |
| Siegel korrekt platziert | Nein (visuell) | Keine Blasen, korrekte Position |
| Verpackung vollständig | Nein (visuell) | Checkliste |

---

## 7. Kunden-Onboarding (nach Lieferung)

### 7.1 Quick Start (5 Minuten)

```
1. Hub auspacken (Siegel NICHT entfernen!)
2. Ethernet-Kabel → Switch (gleiches Netz wie Waage)
3. USB-C Netzteil einstecken
4. Hub startet automatisch (LED blinkt grün)
5. Im Browser: http://scale-hub.local (oder IP)
6. Setup-Wizard:
   a) Odoo-URL eingeben
   b) API-Key eingeben (aus Odoo)
   c) Waage(n) konfigurieren (IP, Adapter-Typ)
7. "Verbinden" → Hub findet Waage(n)
8. Fertig
```

### 7.2 Remote-Onboarding (für Ground UP Support)

```
1. Kunde schließt Hub an (Schritte 1-4)
2. Hub meldet sich automatisch bei updates.groundup.farm
3. Ground UP konfiguriert Waagen remote über Odoo
4. Config wird per OTA auf Hub gepusht
5. Hub verbindet sich mit Waagen
6. Ground UP verifiziert remote: alles grün
```

---

## 8. Siegel-Bruch: Was passiert?

### 8.1 Legitime Gründe für Siegel-Bruch

| Grund | Ablauf |
|-------|--------|
| Hardware-Defekt (SD-Karte, Lüfter) | Ground UP Reparatur-Service, neues Siegel |
| Hardware-Upgrade (z.B. SE050 nachrüsten) | Ground UP installiert, neues Siegel |
| Entsorgung / Rückgabe | Kunde bricht Siegel, Hub wird deregistriert |

### 8.2 Re-Sealing nach Reparatur

1. Altes Siegel in Datenbank als "BROKEN" markieren (mit Grund)
2. Reparatur durchführen
3. Smoke Test wiederholen (alle Prüfungen)
4. Neues Siegel aufbringen (neue SN)
5. Neues Siegel in Datenbank registrieren
6. Audit Log: `RESEAL { old_seal: "...", new_seal: "...", reason: "..." }`

### 8.3 Unbefugter Siegel-Bruch

Wenn ein Kunde ein gebrochenes Siegel meldet, ohne Reparatur angefordert
zu haben:
1. Hub-Status prüfen (Software-ID, Audit Log)
2. Wenn Software-ID unverändert → wahrscheinlich nur physische Neugier
3. Wenn Software-ID geändert → Manipulation, Hub muss neu provisioniert werden
4. In jedem Fall: neues Siegel erst nach Verifizierung

---

## 9. Kosten-Zusammenfassung

### 9.1 Pro Gerät (Stückzahl 1)

| Posten | Kosten |
|--------|--------|
| Hardware (BOM §1.1) | € 106 |
| Arbeitszeit Provisioning (~13 Min) | € 15 |
| **Herstellungskosten** | **€ 121** |
| Marge (50%) | € 60 |
| **Verkaufspreis (VK netto)** | **€ 181** |

### 9.2 Pro Gerät (Stückzahl 50+)

| Posten | Kosten |
|--------|--------|
| Hardware (BOM, Mengenrabatt) | € 85 |
| Arbeitszeit Provisioning | € 10 |
| **Herstellungskosten** | **€ 95** |
| Marge (60%) | € 57 |
| **Verkaufspreis (VK netto)** | **€ 152** |

### 9.3 Einmalige Setup-Kosten

| Posten | Kosten | Anmerkung |
|--------|--------|-----------|
| YubiHSM 2 | € 650 | Hardware Security Module |
| Siegel-Erstbestellung (1.000 Stk) | € 150 | Customized, serialisiert |
| CI/CD Pipeline (GitHub Actions) | € 0 | Open Source |
| Image-Build-Pipeline | € 0 | Yocto/Buildroot, einmalig |
| Gesamt Einmalig | **€ 800** | |

---

## 10. Referenzen

- [Raspberry Pi Secure Boot Provisioner](https://github.com/raspberrypi/rpi-sb-provisioner)
- [RAUC — Robust Auto-Update Controller](https://rauc.readthedocs.io/)
- [Bootlin: RAUC on Raspberry Pi 5](https://bootlin.com/blog/safe-updates-using-rauc-on-raspberry-pi-5/)
- [Raspberry Pi rpi-image-gen](https://raspberrypi.github.io/rpi-image-gen/)
- [WELMEC Guide 7.2 (2024)](https://www.welmec.org/)
- [EN 45501 — Metrological aspects of non-automatic weighing instruments](https://www.beuth.de/en/standard/din-en-45501/358440893)
- [Intertronix Tamper-Evident Labels](https://intertronixlabels.com/)

---

*Ground UP GmbH — Iglasegasse 21-23, A-1190 Wien*
