# Software Bill of Materials (SBOM) Report

**Project**: `w78_std_8051`  
**Target MCU**: `W78E052D` (Nuvoton)  
**Architecture**: Standard 8051 / 8052 Core (Zero-BSP Bare Metal)  
**Memory Model**: SMALL  
**Generated**: 2026-11-05 13:54:02  

---

## 1. Deliverable Firmware Image

| Deliverable | File Path | SHA-256 Hash |
| :--- | :--- | :--- |
| **Intel HEX** | `C:\Users\tester\Desktop\c51 sbom\project\Objects\w78_std_8051.hex` | `9c9e09be28db7e94ba597e04d10d47fe315f61f55910366004c8d8a88aa203cc` |

## 2. Hardware Component (`device`)

| Component | Vendor | Specs |
| :--- | :--- | :--- |
| **W78E052D** | Nuvoton | IRAM(0x00-0xFF) IROM(0x0000-0x1FFF) CLOCK(40000000) |

## 3. Implicitly Linked Keil Runtime Libraries (`library`)

> **Notice**: Although this project uses no external BSP, the Keil BL51 Linker automatically links C51 runtime routines into the binary.

| Library | Linked Internal Modules | SHA-256 Hash | Path |
| :--- | :--- | :--- | :--- |
| **C51S.LIB** | `?C_INIT`, `?C?UIDIV`, `?C?SLCMP` | `aaf864826f6efc6fc60cd5d4f7eb3eb885e19cfe68cebf4600ee76135d9c9cf0` | `C:\Users\tester\AppData\Local\Keil_v5\C51\LIB\C51S.LIB` |

## 4. Standard 8051 Header Files (`file`)

| Header | Resolved Include Path | Copyright / Notice | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| **REG52.H** | `C:\Users\tester\AppData\Local\Keil_v5\C51\INC\REG52.H` | -------------------------------------------------------------------------- REG52.H Header file for generic 80C52 and 80C32 microcontroller. Copyright (c) 1988-2002 Keil Elektronik GmbH and Keil Softwa | `328f70518222cc9fea6a1430103942fd4290f9e8b8028804379e011fa411ca4b` |
| **INTRINS.H** | `C:\Users\tester\AppData\Local\Keil_v5\C51\INC\INTRINS.H` | -------------------------------------------------------------------------- INTRINS.H Intrinsic functions for C51. Copyright (c) 1988-2010 Keil Elektronik GmbH and ARM Germany GmbH All rights reserved. | `027ed466a548c63680438def00fbab3dc745c83c5a9d276738b5089379479b05` |

## 5. Application Source & Startup Code (`file`)

| File Name | File Path | SHA-256 Hash |
| :--- | :--- | :--- |
| **main.c** | `C:\Users\tester\Desktop\c51 sbom\project\src\main.c` | `4616726c8ad7c114c2a13039361935188f476d62d2bd566465d0147f9873e398` |
| **STARTUP.A51** | `C:\Users\tester\Desktop\c51 sbom\project\src\STARTUP.A51` | `0298d03e409c9ecb60da335aec3d7a3eee98762c3efd9dd12eab7612c7104011` |

## 6. Build Toolchain Provenance (`metadata.tools`)

| Tool | Suite Release | Executable Version | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| **C51.exe** | V9.61 | V9.60.7.0 | `e54096a4608671427bde2fd5edf939bf8f44ad7dc79676b7e9290422f25e6ff7` |
| **A51.exe** | V9.61 | V8.2.7.0 | `f9c791ce9ef6e4ab401f2378cd5a98ddd2ab2aa8f6da77fa3993de51b152f63c` |
| **BL51.exe** | V9.61 | V6.22.4.0 | `c59a29594f728ae6714782d148985df69e538726353d045fc2329186b50441c3` |
| **OH51.exe** | V9.61 | V2.7.0.0 | `69d3419af8fa7bbfd9d38755ede9f641814390541c4cd2e6e2c3c93f87cb6a7b` |
