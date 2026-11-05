# Reference: CycloneDX 1.5 & SPDX 2.3 Field Mapping Specification

This document defines how Keil C51 firmware elements map to international standard SBOM schemas (CycloneDX v1.5 and SPDX v2.3).

---

## 1. Component Mapping Table

| Physical Element | Description | CycloneDX 1.5 Mapping | SPDX 2.3 Mapping |
| :--- | :--- | :--- | :--- |
| **Firmware Image (`.hex`)** | The deliverable Intel HEX binary | `metadata.component` (type: `application`) | `packages` (SPDXID: `SPDXRef-Package-FirmwareHex`) |
| **Microcontroller (`W78E052D`)** | Target 8051 silicon device | `components[]` (type: `device`) | `packages` (SPDXID: `SPDXRef-Package-MCU`) |
| **Implicit Library (`C51S.LIB`)** | Keil Small model runtime library | `components[]` (type: `library`) | `packages` (SPDXID: `SPDXRef-Package-Lib-0`) |
| **Standard Header (`REG52.H`)** | Keil 8051 register definition header | `components[]` (type: `file`) | `files` (SPDXID: `SPDXRef-File-Header-0`) |
| **Source Code (`main.c`, `STARTUP.A51`)** | Application source and startup code | `components[]` (type: `file`) | `files` (SPDXID: `SPDXRef-File-Source-0`) |
| **Build Tools (`C51.exe` etc.)** | Compiler, assembler, linker tools | `metadata.tools.components[]` (type: `application`) | `creationInfo.creators[]` |

---

## 2. CycloneDX v1.5 Schema Highlights

### Root Firmware Component (`metadata.component`)
```json
{
  "type": "application",
  "bom-ref": "pkg:generic/firmware/w78_std_8051@1.0.0",
  "name": "w78_std_8051",
  "version": "1.0.0",
  "description": "Intel HEX Firmware for W78E052D (Winbond / Nuvoton W78 series)",
  "hashes": [
    {"alg": "SHA256", "content": "9c9e09be28db..."},
    {"alg": "MD5", "content": "9b1248a..."}
  ]
}
```

### Implicit Runtime Library Component (`C51S.LIB`)
Includes properties detailing internally linked modules:
```json
{
  "type": "library",
  "bom-ref": "pkg:library/keil/c51s.lib@aaf86482",
  "name": "C51S.LIB",
  "version": "V9.61",
  "description": "Keil C51 SMALL Model Runtime Library (implicitly linked by BL51)",
  "hashes": [
    {"alg": "SHA256", "content": "aaf864826f6..."}
  ],
  "properties": [
    {"name": "file:path", "value": "C:\\...\\C51\\LIB\\C51S.LIB"},
    {"name": "keil:linked_module", "value": "?C_INIT"},
    {"name": "keil:linked_module", "value": "?C?UIDIV"},
    {"name": "keil:linked_module", "value": "?C?SLCMP"}
  ]
}
```

### Toolchain Provenance (`metadata.tools`)
Tracks both the suite release and specific executable versions:
```json
{
  "tools": {
    "components": [
      {
        "type": "application",
        "name": "C51.exe",
        "version": "V9.60.7.0",
        "hashes": [{"alg": "SHA256", "content": "e54096a46086..."}]
      },
      {
        "type": "application",
        "name": "BL51.exe",
        "version": "V6.22.4.0",
        "hashes": [{"alg": "SHA256", "content": "c59a29594f72..."}]
      }
    ]
  }
}
```

---

## 3. SPDX v2.3 Schema Highlights

### Relationships (`relationships`)
- The firmware image depends on the target hardware MCU:
  ```json
  {"spdxElementId": "SPDXRef-Package-FirmwareHex", "relationshipType": "DEPENDS_ON", "relatedSpdxElement": "SPDXRef-Package-MCU"}
  ```
- The firmware image depends on the implicit runtime library:
  ```json
  {"spdxElementId": "SPDXRef-Package-FirmwareHex", "relationshipType": "DEPENDS_ON", "relatedSpdxElement": "SPDXRef-Package-Lib-0"}
  ```
- The firmware image contains application source and header files:
  ```json
  {"spdxElementId": "SPDXRef-Package-FirmwareHex", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-Header-0"}
  ```

---

## 4. Cryptographic Hash Algorithms & Target Specification

The SBOM generator strictly complies with NIST FIPS 180-4, NTIA Minimum Elements, CycloneDX 1.5, and SPDX 2.3 by computing cryptographic hashes for all binary assets, source files, and build tools.

### A. Supported Hash Algorithms

| Algorithm | Hex Length | Standard / Reference | Purpose & Scope |
| :--- | :--- | :--- | :--- |
| **SHA-256** | 64 characters | NIST FIPS 180-4 / NTIA / CRA | **Primary Compliance Hash**. Used for binary integrity, anti-tampering, and CVE matching. |
| **SHA-1** | 40 characters | FIPS 180-1 | Auxiliary hash for backward compatibility with legacy SCA engines and Git references. |
| **MD5** | 32 characters | RFC 1321 | Legacy checksum for rapid artifact comparison. |

### B. Targets of Hash Computation

The SBOM generator calculates SHA-256, SHA-1, and MD5 hashes for 5 categories of physical assets:

1. **Firmware Deliverable**:
   - `project/Objects/w78_std_8051.hex` (Intel HEX flash image)
2. **Implicit Runtime Library**:
   - `C51\LIB\C51S.LIB` (Keil Small model precompiled library)
3. **Standard 8051 Headers**:
   - `C51\INC\REG52.H` (Standard 8052 SFR register definitions)
   - `C51\INC\INTRINS.H` (Built-in intrinsic macro routines)
4. **Source & Startup Files**:
   - `project/src/main.c` (Application C code)
   - `project/src/STARTUP.A51` (8051 assembly bootstrap)
5. **Build Toolchain Executables**:
   - `C51\BIN\C51.exe` (C51 C Compiler)
   - `C51\BIN\A51.exe` (A51 Macro Assembler)
   - `C51\BIN\BL51.exe` (BL51 Banked Linker)
   - `C51\BIN\OH51.exe` (OH51 Object to HEX Converter)

### C. Hash Representation in Generated SBOMs

- **CycloneDX 1.5 JSON (`sbom.cdx.json`)**:
  Stored under `hashes[]` with `alg: "SHA256"` (or `"SHA1"`, `"MD5"`) and `content: "<hash>"`.
- **SPDX 2.3 JSON (`sbom.spdx.json`)**:
  Stored under `checksums[]` with `algorithm: "SHA256"` and `checksumValue: "<hash>"`.
- **Markdown Report (`SBOM-REPORT.md`)**:
  Displayed as dedicated `SHA-256 Hash` columns across summary tables.
