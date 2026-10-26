---
layout: "post"
title: "86box virtual hardware configuration for Linux-1994"
date: "2026-08-04"
---

> 86box configuration for 1999 - 2000 PC configuration for Linux (slackware Linux 4.0), medium or low end but well supported, specify processor socket, video, sound,

For a **1999–2000 Linux workstation** running **Slackware Linux 4.0 (kernel 2.2.x)**, I'd optimize for **excellent XFree86 support**, stable IDE drivers, OSS sound, and networking rather than raw gaming performance.

## Recommended Configuration (Medium End)

| Component | Recommendation | Why |
|-----------|----------------|-----|
| **CPU Socket** | **Slot 1 (Intel 440BX)** | Rock-solid Linux support, very common in 1999 |
| **CPU** | Pentium II 350 MHz (Deschutes) | Fast but period-correct |
| **RAM** | 128 MB SDRAM | Plenty for KDE/GNOME 1.x |
| **Chipset** | Intel 440BX | One of the best supported chipsets |
| **Video** | **S3 Trio3D/2X** or **S3 Trio64V+** | Outstanding XFree86 support |
| **Sound** | Ensoniq AudioPCI ES1370/1371 | Native OSS driver, painless |
| **Network** | Intel EtherExpress Pro/100 (82559) | eepro100 driver, excellent |
| **Storage** | IDE controller (Intel PIIX4) | Native Linux support |
| **Hard Disk** | 4–8 GB IDE | Typical size |
| **CD-ROM** | 24x IDE ATAPI | Standard |

This is probably what I'd build for everyday Linux use.

---

## Lower-end Configuration

Perfect for Slackware 4.0.

| Component | Choice |
|-----------|--------|
| Socket | Socket 7 |
| CPU | Pentium MMX 233 MHz |
| RAM | 64 MB |
| Video | S3 Trio64V+ |
| Sound | Sound Blaster 16 ISA |
| NIC | AMD PCnet-PCI II |
| HDD | 2 GB |

---

# Video Card

For Linux in 1999 there was essentially one answer:

### ★ S3 Trio64V+

Pros

- flawless VESA
- excellent XFree86 support
- stable
- accelerated X
- nearly every distribution worked out of the box

If available in 86Box I'd also consider

- S3 Trio3D/2X
- ATI Mach64

I'd avoid

- NVIDIA RIVA (immature Linux drivers)
- 3dfx (great for games, not necessary for Linux desktop)

The S3 Trio family remains one of the safest choices for Linux guests in 86Box, and is frequently recommended by the community for period operating systems. citeturn0search0turn0reddit20

---

# Sound

Best choices:

### Ensoniq AudioPCI ES1370

Pros

- OSS support
- PCI
- no ISA headaches
- good PCM playback

Driver:
```
es1370
```

Alternative:

- Sound Blaster 16 ISA
- ESS Solo-1

Avoid:

- Creative Live! (EMU10K1 wasn't mature until later)

---

# Network

Intel Pro/100

Driver:

```
eepro100
```

Alternative:

AMD PCnet

```
pcnet32
```

Both work beautifully.

---

# Motherboard

Intel 440BX

Examples commonly found in 86Box:

- ASUS P2B
- ABIT BX6
- Intel SE440BX

440BX was arguably the best Linux chipset of the era.

---

# Disk

IDE only.

Linux 2.2 has excellent IDE support.

Suggested:

- Quantum Fireball
- IBM Deskstar
- Western Digital Caviar

4–8 GB is realistic.

---

# Slackware 4.0 Software

Typical desktop:

- Linux kernel 2.2.x
- XFree86 3.3.3 / 3.3.5
- KDE 1.x
- FVWM95
- AfterStep
- Netscape 4.7
- GCC 2.95
- Emacs 20
- Vim 5.x

---

# My Favorite Configuration

This feels like the machine a Linux enthusiast might have built around late 1999:

| Component | Hardware |
|-----------|----------|
| Motherboard | Intel 440BX (ASUS P2B class) |
| Socket | Slot 1 |
| CPU | Pentium II 350 MHz |
| RAM | 128 MB |
| Video | **S3 Trio64V+ (4 MB)** |
| Sound | **Ensoniq AudioPCI ES1370** |
| Network | Intel Pro/100 |
| HDD | 6 GB IDE |
| CD-ROM | 24x ATAPI |
| Mouse | PS/2 |
| Floppy | 1.44 MB |

This configuration is extremely well supported by Linux 2.2, requires minimal manual driver configuration, and closely reflects the kind of dependable hardware many Linux users favored in 1999–2000. The 440BX chipset, S3 graphics, and AudioPCI combination offers an excellent balance of compatibility and authenticity.

these are the PCI adapters available:

- AMD PCnet-FAST III
- AMD PCnet-PCI II
- DECchip 21040
- DECchip 21140
- DECchip 21143
- Realtek RTL8029AS
- Realtek RTL8139C+
- SMC EPIC/100

For **Slackware Linux 4.0 (1999, kernel 2.2.x)** I'd rank them like this:

| Rank | Adapter | Linux Driver | Recommendation |
|------|---------|--------------|----------------|
| ⭐⭐⭐⭐⭐ | **DECchip 21140 "Tulip FasterNet"** | `tulip` | Best choice |
| ⭐⭐⭐⭐⭐ | **DECchip 21143 "Tulip"** | `tulip` | Also excellent |
| ⭐⭐⭐⭐☆ | **AMD PCnet-FAST III** | `pcnet32` | Very good |
| ⭐⭐⭐⭐☆ | **AMD PCnet-PCI II** | `pcnet32` | Very good |
| ⭐⭐⭐⭐☆ | **Realtek RTL8029AS** | `ne2k-pci` | Excellent compatibility |
| ⭐⭐⭐☆☆ | **RTL8139C+** | `8139too` | More of a 2000–2002 era card |
| ⭐⭐☆☆☆ | **SMC EPIC/100** | `epic100` | Works but less common |

### For a period-correct Linux workstation

I'd use

> **[PCI] DECchip 21143 "Tulip"**

or

> **[PCI] DECchip 21140 "Tulip FasterNet"**

The Tulip family was extremely well regarded in the Linux community of the late 1990s. Donald Becker's `tulip` driver was one of the most mature and reliable Ethernet drivers of the era, and many distributions—including Slackware 4.0—supported it out of the box.

### If you want "it just works"

Choose

```
Mode: SLiRP
Adapter: [PCI] DECchip 21143 "Tulip"
```

Slackware should detect it automatically.

---

## My complete 86Box Linux 1999 build

| Component | Recommendation |
|-----------|----------------|
| Machine | Intel 440BX motherboard |
| CPU | Pentium II 350 MHz |
| RAM | 128 MB |
| Video | S3 Trio3D/2X (or Trio64V+) |
| Sound | Ensoniq AudioPCI ES1371 |
| Network | **DECchip 21143 Tulip** |
| HDD | 6 GB IDE |
| CD-ROM | 24× ATAPI |
| Mouse | PS/2 |

This configuration is very representative of what a Linux enthusiast or developer might have assembled in 1999: Intel chipset, S3 graphics, Tulip networking, and Ensoniq AudioPCI were all known for excellent Linux support with minimal configuration.

## ATAPI CD-ROM type ##

For a **1999–2000 Linux PC**, I'd emulate a very ordinary IDE CD-ROM drive. Linux 2.2's `ide-cd` driver works with virtually any standards-compliant ATAPI drive, so the exact manufacturer matters mainly for authenticity rather than compatibility.

My recommendations:

| Drive | Speed | Recommendation |
|-------|------:|----------------|
| **Toshiba XM-5702B** | 32× | ⭐ Best overall |
| **TEAC CD-532E** | 32× | Excellent |
| **Mitsumi CRMC-FX810T** | 24× | Very period-correct |
| **Pioneer DR-A24X** | 24× | Good |
| **86Box CD-ROM 1.00** | 8× | Good for maximum compatibility with older OSes |

For a Slackware 4.0 machine, I'd configure:

- **Bus:** ATAPI (IDE)
- **Channel:** Secondary Master (0:1)
- **Speed:** **24×** or **32×**
- **Type:** **Toshiba XM-5702B** (if available)

The Toshiba XM series was extremely common in late-1990s Linux workstations and was known for reliable CD-ROM access and digital audio extraction.

### Why not 52× or 72×?

Although 86Box supports drives up to 72×, such speeds are more representative of 2001–2003 hardware. citeturn0search0turn0search12

For a 1999 system:

- 24× = very common
- 32× = common
- 40× = late 1999
- 52× = mostly 2000–2001
- 72× = much later

## My complete 1999 Slackware 4.0 build

- **Motherboard:** Intel 440BX (ASUS P2B class)
- **CPU:** Pentium II 350 MHz (Slot 1)
- **RAM:** 128 MB SDRAM
- **Video:** S3 Trio3D/2X (or Trio64V+ if available)
- **Sound:** Ensoniq AudioPCI ES1371
- **Network:** DECchip 21143 "Tulip"
- **Hard disk:** 6 GB IDE (Quantum Fireball or IBM Deskstar model)
- **CD-ROM:** **Toshiba XM-5702B, ATAPI, 32×**
- **Mouse:** PS/2
- **Floppy:** 3.5" 1.44 MB

That configuration is both historically plausible and gives excellent Linux compatibility with minimal manual driver configuration.
