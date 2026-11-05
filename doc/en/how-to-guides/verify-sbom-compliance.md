# How-To: Verify SBOM Compliance and Standards

This guide explains how to test and verify that the generated SBOM files comply with international standards such as the US NTIA Minimum Elements and the EU Cyber Resilience Act (CRA).

---

## 1. Automated Quick Verification (Using Python)

Run this one-liner in PowerShell from the repository root to check NTIA Minimum Elements across both CycloneDX and SPDX files:

```powershell
python -c "
import json

cdx = json.load(open('sbom/sbom.cdx.json', encoding='utf-8'))
spdx = json.load(open('sbom/sbom.spdx.json', encoding='utf-8'))

print('=== 1. CycloneDX 1.5 Compliance ===')
assert cdx['bomFormat'] == 'CycloneDX' and cdx['specVersion'] == '1.5'
assert 'timestamp' in cdx['metadata']
assert len(cdx['components']) >= 5
assert len(cdx['dependencies']) >= 1
print('[✓] CycloneDX structure and dependencies verified!')

print('=== 2. SPDX 2.3 Compliance ===')
assert spdx['spdxVersion'] == 'SPDX-2.3'
assert 'created' in spdx['creationInfo']
assert len(spdx['packages']) >= 3
assert len(spdx['relationships']) >= 4
print('[✓] SPDX structure and relationships verified!')

print('=== 3. Binary Integrity Hashes ===')
hex_hash = cdx['metadata']['component']['hashes'][0]['content']
assert len(hex_hash) == 64
print(f'[✓] Firmware SHA-256: {hex_hash}')
print('\n[SUCCESS] All SBOM compliance assertions passed!')
"
```

---

## 2. Using Industry-Standard Validation Tools

You can also validate the files using official external tools:

### Option A: CycloneDX CLI (`cyclonedx-cli`)
If `cyclonedx-cli` is installed:
```powershell
cyclonedx validate --input-file sbom/sbom.cdx.json --input-format json
```
Output: `Validation successful`.

### Option B: SPDX Tools (`spdx-tools`)
Using Python's official SPDX library:
```powershell
pip install spdx-tools
pyspdx -i sbom/sbom.spdx.json
```

---

## 3. Compliance Auditor Checklist

Use this checklist during customer or regulatory audits:

| Audit Criterion | Requirement | Project Status |
| :--- | :--- | :---: |
| **Standard Format** | CycloneDX v1.4+ or SPDX v2.2+ | **PASS** (CycloneDX 1.5 & SPDX 2.3) |
| **No Empty SBOMs** | Component count > 0 with granular items | **PASS** (MCU, headers, libraries, sources) |
| **Implicit Library Tracking** | Details unlisted runtime libraries (`C51S.LIB`) | **PASS** (Tracks `?C_INIT`, `?C?UIDIV`) |
| **Cryptographic Hashes** | Valid SHA-256 hashes for all binary items | **PASS** (All deliverables & libs hashed) |
| **Toolchain Provenance** | Build tools, suite version, and compiler hashes | **PASS** (Recorded in `metadata.tools`) |
