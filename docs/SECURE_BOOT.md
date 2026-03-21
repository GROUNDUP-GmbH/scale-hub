# GroundUp Scale Hub — Secure Boot Setup (CM4)

> **ADR-07: This is a Day-1 requirement, not a Phase-3 retrofit.**  
> The CM4 OTP fuse is irreversible. Devices deployed without Secure Boot
> cannot be upgraded in the field.

---

## Why Day 1

1. **OTP is one-time:** The boot signing key hash is burned into the CM4's
   One-Time Programmable memory. Once set, it cannot be changed or removed.
2. **Field devices are permanent:** A Hub shipped without Secure Boot will
   never have Secure Boot. There is no software update that can add it.
3. **Regulatory credibility:** WELMEC 7.2 §4.3 requires protection of
   legally relevant software. While the Hub is not "legally relevant" per se,
   the entire argument that it is "non-manipulable" depends on this.
4. **Cost is identical:** Setting up the signing pipeline now costs the same
   as doing it later — but covers every device from unit #1.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────┐
│  CM4 Boot Chain (each stage verifies the next)   │
│                                                  │
│  Boot ROM (mask ROM, immutable)                  │
│     ↓  verifies via OTP RSA-2048 hash            │
│  bootcode.bin / start4.elf (signed)              │
│     ↓  verifies                                  │
│  config.txt + kernel8.img (signed)               │
│     ↓  verifies                                  │
│  dm-verity root filesystem (read-only)           │
│     ↓  runs                                      │
│  Docker container (signed image)                 │
│     = Hub application                            │
└──────────────────────────────────────────────────┘
```

---

## Step-by-Step Setup

### 1. Generate Signing Key Pair

```bash
# Generate RSA-2048 private key (KEEP THIS SAFE — it signs everything)
openssl genrsa -out groundup-hub-boot.pem 2048

# Extract public key
openssl rsa -in groundup-hub-boot.pem -pubout -out groundup-hub-boot.pub

# Generate the SHA-256 hash of the public key (this goes into OTP)
openssl rsa -in groundup-hub-boot.pem -pubout -outform DER | \
  sha256sum | awk '{print $1}'
```

**Store `groundup-hub-boot.pem` in a hardware security module (HSM)
or at minimum in an encrypted vault. Loss of this key = loss of
ability to update devices.**

### 2. Program OTP on CM4

This step is **irreversible**. After this, only images signed with
the corresponding private key will boot.

```bash
# On the CM4 (via rpiboot or SSH during provisioning)

# Write the public key hash to OTP
# (uses vcmailbox — see RPi documentation for exact registers)
sudo rpi-otp-private-key -w groundup-hub-boot.pub

# Enable secure boot
sudo vcmailbox 0x00038061 8 8 0 0  # Set secure boot flag
```

**Verify before proceeding:**

```bash
# Read back OTP to confirm
sudo rpi-otp-private-key -r
# Should show your key hash
```

### 3. Sign Boot Files

```bash
# Sign the boot partition files
rpi-sign-bootcode --key groundup-hub-boot.pem \
  --boot bootcode.bin \
  --config config.txt \
  --kernel kernel8.img \
  --output signed-boot/
```

### 4. Create dm-verity Root Filesystem

```bash
# Build read-only root filesystem
mksquashfs rootfs/ rootfs.squashfs -comp zstd

# Create dm-verity hash tree
veritysetup format rootfs.squashfs rootfs.verity > verity-info.txt

# Extract root hash (goes into signed kernel cmdline)
ROOT_HASH=$(grep "Root hash:" verity-info.txt | awk '{print $3}')
echo "dm-verity root hash: $ROOT_HASH"
```

The root hash is embedded in the signed kernel command line,
creating a chain of trust from OTP → bootloader → kernel → filesystem.

### 5. A/B Partition Layout

```
mmcblk0
├── p1: boot_a (signed, active)
├── p2: boot_b (signed, standby)
├── p3: rootfs_a (dm-verity, active)
├── p4: rootfs_b (dm-verity, standby)
├── p5: data (persistent, encrypted with LUKS)
└── p6: otp-log (append-only audit partition)
```

### 6. OTA Update Process

```
1. Hub downloads signed update bundle
2. Verifies bundle signature against embedded public key
3. Writes to standby partition (B if A is active)
4. Verifies dm-verity hash of written image
5. Marks standby as "pending boot"
6. Reboots into new partition
7. If boot fails → automatic rollback to previous partition
```

---

## Key Management

| Key | Storage | Purpose | Rotation |
|---|---|---|---|
| Boot signing key | HSM / encrypted vault | Signs boot images | Never (OTP is permanent) |
| OTA signing key | CI/CD pipeline (encrypted) | Signs update bundles | Annually, key embedded in rootfs |
| HMAC secret | Hub data partition (encrypted) | API authentication | Per-device, rotatable |
| SE050 device key | NXP SE050 secure element | Audit log signing, RDDL | Never leaves chip |

---

## What This Prevents

| Attack | Prevention |
|---|---|
| Flash a modified SD card | Secure Boot rejects unsigned images |
| Modify rootfs on running device | dm-verity detects block-level changes |
| Install unauthorized software | AppArmor + read-only rootfs |
| Replace Hub application | Signed Docker images only |
| Downgrade to vulnerable version | OTA version counter in OTP |
| Extract signing keys | Keys in HSM, not on device |
| Tamper with audit log | SE050 hardware signatures (optional) |

---

## Development vs. Production

| Aspect | Development | Production |
|---|---|---|
| Secure Boot | Disabled (`GROUNDUP_MOCK_SERIAL=1`) | Enabled (OTP fused) |
| Root access | Available | Disabled |
| dm-verity | Not used | Enforcing |
| Docker images | Local build | Signed from CI/CD |
| OTA updates | Manual flash | Signed A/B OTA |

Development devices use a **separate, unfused CM4** that never goes to the field.

---

## Cost Estimate

| Item | Cost | Notes |
|---|---|---|
| HSM (YubiHSM 2) | ~€650 one-time | Stores boot signing key |
| CI/CD signing pipeline | ~€0 (GitHub Actions) | Automated signing |
| CM4 OTP programming | ~2 min per device | Part of provisioning |
| dm-verity build step | ~30s per image | Part of CI/CD |

**Total additional cost per device: ~€0** (amortized HSM over fleet)

---

## References

- [Raspberry Pi Secure Boot](https://www.raspberrypi.com/documentation/computers/config_txt.html#secure-boot)
- [dm-verity — Linux Kernel Documentation](https://docs.kernel.org/admin-guide/device-mapper/verity.html)
- WELMEC 7.2 §4.3: Protection of legally relevant software
- WELMEC 7.2 §4.5: Software identification and audit trail
