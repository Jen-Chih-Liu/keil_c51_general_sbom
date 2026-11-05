# Explanation: How to Determine SBOM Compliance

This article explains the regulatory frameworks (US NTIA Minimum Elements, EU Cyber Resilience Act CRA, ISO/IEC 5962) used to judge SBOM compliance, specifically tailored to bare-metal embedded microcontrollers like the 8051.

---

## 1. What Makes an SBOM Compliant?

A compliant SBOM is not merely a list of files; it must be a **machine-readable**, **standardized**, and **semantically complete** document that automated vulnerability management engines (such as VEX or CVE trackers) can ingest.

Key regulatory benchmarks:
1. **US NTIA Minimum Elements**: Mandated under Executive Order 14028, establishing the baseline data fields required for an SBOM.
2. **EU Cyber Resilience Act (CRA)**: Mandates comprehensive SBOMs for all digital and hardware products entering the European Single Market.
3. **ISO/IEC 5962:2021**: The international standard recognizing SPDX.

---

## 2. NTIA's 7 Minimum Data Elements

Every compliant SBOM must cover these 7 fields:

1. **Supplier Name**: Identifies who provided the component (e.g. Nuvoton, Keil / Arm).
2. **Component Name**: The formal name of the component (e.g. `W78E052D`, `C51S.LIB`, `REG52.H`).
3. **Version**: The release version of the component.
4. **Unique Identifiers**: Standard identifiers like Package URL (PURL), CPE, or BOM-Ref.
5. **Relationships**: Clear dependency links (e.g. `DependsOn`, `Contains`, `Describes`).
6. **Author of SBOM Data**: Identifies the tool or author creating the document.
7. **Timestamp**: ISO-8601 UTC timestamp of creation.

---

## 3. Embedded Firmware Compliance Criteria

For bare-metal 8051 or embedded projects, auditors apply four specific scrutiny criteria:

### Criteria 1: Zero Tolerance for Empty SBOMs
Traditional scanners fail to find manifests in 8051 projects and output zero components. An empty SBOM fails compliance automatically.

### Criteria 2: Disclosure of Implicit Runtime Binaries
Compilers silently inject runtime libraries (`C51S.LIB`) for arithmetic and memory initialization. A compliant SBOM must disclose these closed-source binary dependencies.

### Criteria 3: Cryptographic Integrity Hashes
Firmware is distributed as Intel HEX or raw binary. The SBOM must provide SHA-256 hashes linking the deliverable binary to its component bill of materials.

### Criteria 4: Build Toolchain Provenance
In line with NIST SP 800-218 SSDF standards, the exact versions and hashes of the compiler, assembler, and linker must be documented.
