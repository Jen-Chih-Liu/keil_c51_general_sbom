# Explanation: Why Bare-Metal 8051 Projects Need Build-Artifact-Driven SBOMs

This article discusses why conventional Software Composition Analysis (SCA) scanners fail on bare-metal 8051 codebases, and why this project uses a build-artifact-driven reverse extraction architecture.

---

## 1. The Fundamental Blind Spot of Conventional SCA

Modern SCA tools (such as Syft, Trivy, Snyk, Black Duck, and cdxgen) were designed around modern package ecosystems. They look for explicit dependency manifests or lockfiles:
- JavaScript: `package.json`
- Python: `requirements.txt`, `Pipfile`
- Rust / Go: `Cargo.lock`, `go.mod`
- C/C++: `conan.lock`, `CMakeLists.txt`
- Arm Cortex-M: CMSIS-Pack (`.pdsc`)

### The Reality of Classical 8051 Embedded Development
In automotive auxiliary ECUs, power supplies, industrial controls, and smart meters, millions of devices run classical 8051 microcontrollers like the Winbond / Nuvoton W78 series. These projects exhibit distinct characteristics:
1. **Zero Manifests**: Projects consist only of a `.uvproj` file, `STARTUP.A51`, and several `.c` files.
2. **Zero External BSPs**: The firmware only includes standard headers like `<REG52.H>` or `<REG51.H>`.
3. **Closed Binary Runtimes**: Keil C51 provides pre-compiled runtime helper libraries (`C51S.LIB`, `C51C.LIB`, `C51L.LIB`).

When standard SCA scanners inspect such a repository, they find **zero dependencies** and output an empty SBOM.

---

## 2. False "Zero-Dependency" and Compliance Risks

Under cyber resilience regulations such as the EU Cyber Resilience Act (CRA) and US Executive Order 14028, firmware is not truly "zero-dependency":
- **Firmware Contains Third-Party Machine Code**: Even if an engineer writes no library calls, standard C semantics such as 16-bit integer division (`a / b`) or global variable initialization cause Keil `BL51` to automatically insert precompiled runtime routines from `C51S.LIB` into the final Flash binary.
- **Header File and Toolchain Vulnerabilities**: Register definitions in `REG52.H` and compiler code-generation behaviors directly affect security.
- **Lack of Traceability**: Providing only an Intel HEX file prevents auditors from verifying which compiler build or runtime library version was used.

---

## 3. The Solution: Reverse Extraction from Build Evidence

Because source directories lack manifests, the ground truth resides in the **build evidence**:

```text
[Source Scanner (Fails)]  --> No package.json --> Empty SBOM (Non-compliant)

[Build Evidence Extraction (Succeeds)]
 ├── Parse .uvproj       --> Target MCU & vendor (W78E052D)
 ├── Parse .lst & Headers --> Included standard headers & notices (REG52.H, INTRINS.H)
 ├── Parse .m51 Map file --> Implicit runtime library (C51S.LIB) & internal routines
 └── Parse TOOLS.INI     --> Toolchain suite version & binary SHA-256 hashes
      │
      ▼
 Output CycloneDX 1.5 & SPDX 2.3 SBOMs (Full Traceability & Compliance)
```

By surfacing implicit dependencies directly from linker maps and compiler listings, classic 8051 projects achieve compliance with modern supply chain security standards without requiring intrusive build system rewrites.
