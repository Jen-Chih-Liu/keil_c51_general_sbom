# Keil C51 Standard 8051 (W78 Series) Project & SBOM Documentation

Welcome to the technical documentation library for this project. This documentation strictly adheres to the **Diátaxis** framework, structured into four distinct modes based on user goals and learning contexts:

```
                         Practical / Action
                               │
            Tutorials           │ How-To Guides
       Learning-oriented:       │ Problem-oriented:
       First-time walkthrough   │ Practical recipes for specific tasks
                               │
── Learning ────────────────────┼──────────────────── Working ──
                               │
           Explanation          │ Reference
     Understanding-oriented:    │ Information-oriented:
     Architecture & rationale   │ Accurate technical specs & schemas
                               │
                        Theoretical / Knowledge
```

---

## 1. Learning-Oriented: Practical (Tutorials)
Ideal for newcomers wanting a guided, hands-on path to build the firmware and generate an SBOM:
- [Getting Started: Build a W78 Project & Generate Your First SBOM](tutorials/getting-started.md)

---

## 2. Working-Oriented: Practical (How-To Guides)
Step-by-step guides for solving specific real-world tasks:
- [How-To: Development Environment & Prerequisites Setup (Keil C51 & Python)](how-to-guides/environment-setup.md)
- [How-To: Configure Keil µVision to Automatically Generate SBOM on F7](how-to-guides/keil-gui-integration.md)
- [How-To: Run Headless Automated Builds in PowerShell / CI/CD](how-to-guides/cli-headless-build.md)
- [How-To: Run Automated Verification Tests for the SBOM Generator](how-to-guides/automated-testing.md)
- [How-To: Verify SBOM Compliance and Standards (NTIA & Schemas)](how-to-guides/verify-sbom-compliance.md)

---

## 3. Working-Oriented: Theoretical (Reference)
Detailed technical references, CLI parameters, and schema specifications:
- [Reference: Command-Line Interface (CLI) Manual](reference/cli-reference.md)
- [Reference: CycloneDX 1.5 & SPDX 2.3 Field Mapping Specification](reference/sbom-schema-mapping.md)
- [Reference: Keil C51 Build Artifact Formats & Structure](reference/build-artifacts.md)

---

## 4. Learning-Oriented: Theoretical (Explanation)
In-depth discussions on architecture, supply chain security, and design choices:
- [Explanation: How to Determine SBOM Compliance (NTIA / CRA Standards)](explanation/sbom-compliance-criteria.md)
- [Explanation: Why Bare-Metal 8051 Projects Need Build-Artifact-Driven SBOMs](explanation/why-build-artifact-sbom.md)
- [Explanation: Implicit Keil C51 Runtime Library (C51S.LIB) Linking Mechanics](explanation/implicit-c51-runtime-linking.md)
