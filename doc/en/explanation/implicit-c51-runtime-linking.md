# Explanation: Implicit Keil C51 Runtime Library (C51S.LIB) Linking Mechanics

This article explains how the Keil C51 linker (`BL51.exe` / `LX51.exe`) resolves implicit runtime libraries and how C language statements trigger internal library modules.

---

## 1. Memory Models and the C51 Runtime Family

The 8051 architecture uses distinct Harvard memory spaces: DATA, IDATA, XDATA, PDATA, and CODE. Keil C51 provides precompiled runtime libraries tailored to specific memory models:

| Memory Model | Default Variable Storage | Associated Implicit Library |
| :--- | :--- | :--- |
| **Small** | On-chip RAM (DATA, 128B / 256B) | **`C51S.LIB`** |
| **Compact** | Paged external RAM (PDATA, 256B) | **`C51C.LIB`** |
| **Large** | External RAM (XDATA, up to 64KB) | **`C51L.LIB`** |

In our W78E052D project, the Small model is configured, causing `BL51` to automatically select `C51S.LIB`.

---

## 2. Startup Code Provenance: `STARTUP.OBJ` vs `C51S.LIB`

A critical consideration in SBOM generation is whether startup code originates from the user's project or from the Keil library:

### Case A: Project Includes `STARTUP.A51` (This Project)
Keil compiles `STARTUP.A51` into `STARTUP.OBJ`. In `w78_std_8051.m51`:
```text
INPUT MODULES INCLUDED:
  PROJECT\OBJECTS\STARTUP.OBJ (?C_STARTUP)
```
This indicates `?C_STARTUP` originates from the project's own source code (classified as a `file` component).

### Case B: Project Omits `STARTUP.A51`
If no startup assembly is provided, `BL51` extracts the default `?C_STARTUP` from `C51S.LIB`:
```text
INPUT MODULES INCLUDED:
  C:\...\C51\LIB\C51S.LIB (?C_STARTUP)
```

The SBOM generator correctly distinguishes between user object files and runtime library packages based on file extensions in the `.m51` input list.

---

## 3. C Constructs That Trigger `C51S.LIB` Helpers

When `STARTUP.OBJ` is present, a minimalist program might not require additional routines. However, standard C features naturally pull in helper modules from `C51S.LIB`:

### 1. Global Variable Initialization (`?C_INIT`)
8051 internal RAM powers up in an undefined state. When you declare:
```c
volatile unsigned int g_tick_counter = 1000;
```
The initial value `1000` is placed in CODE ROM, and the `?C_INIT` helper routine copies it into DATA RAM before `main()` executes. `BL51` automatically links `(?C_INIT)` from `C51S.LIB`.

### 2. 16-Bit Integer Division (`?C?UIDIV`)
The 8051 instruction set only supports 8-bit division (`DIV AB`). When firmware performs:
```c
computed_val = g_tick_counter / g_divider;
```
Software division is required. The compiler generates a call to `?C?UIDIV`, prompting `BL51` to link `(?C?UIDIV)` from `C51S.LIB`.

### 3. Signed Comparison (`?C?SLCMP`)
Signed integer comparisons and boundary tests pull in signed comparison helper routines from `C51S.LIB`.

---

## 4. Value for SBOM and Compliance

By parsing the `INPUT MODULES INCLUDED` section of `.m51`:
- We prove that the binary depends on `C51S.LIB`.
- We enumerate the exact internal helper modules (`?C_INIT`, `?C?UIDIV`) embedded into the firmware.
- We compute and record the SHA-256 hash of `C51S.LIB`.

This provides granular binary provenance and transparent supply chain integrity for standard 8051 firmware.
