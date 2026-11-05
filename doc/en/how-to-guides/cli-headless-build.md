# How-To: Run Headless Automated Builds in PowerShell / CI/CD

This guide explains how to execute automated, headless firmware builds and generate SBOMs in Windows PowerShell and CI/CD pipelines (e.g., GitHub Actions, GitLab CI, Jenkins).

---

## When to Use

- When building firmware on automated build servers or CI runners.
- When scripting nightly integration and compliance audits.
- When process automation requires standard exit codes (`0` for success, non-zero for failure).

---

## Quick Command

From the root of the project, execute:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1
```

If Keil is installed in a non-standard directory, specify `-KeilPath`:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1 -KeilPath "D:\Keil_v5\C51"
```

---

## Technical Design: Space-in-Path Handling

Keil BL51 linkers use legacy argument parsers that fail when comma-separated module paths contain spaces (e.g., `C:\Users\tester\Desktop\c51 sbom\...`), throwing `FATAL ERROR L204: INVALID KEYWORD`.

To guarantee robust automated builds, `build_and_sbom.ps1` switches into the `project/` directory before invoking tools using `Push-Location`:
- It passes relative paths (`src\STARTUP.A51`, `Objects\STARTUP.obj, Objects\main.obj`) to `A51`, `C51`, and `BL51`.
- It restores the working directory via `Pop-Location` in a `finally` block.
- It invokes the Python SBOM generator after a successful build.

---

## CI/CD Pipeline Configuration (GitHub Actions)

Example `.github/workflows/firmware-sbom.yml`:

```yaml
name: Build Firmware and SBOM

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Build Firmware and SBOM
        run: |
          powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1

      - name: Run Tests
        run: |
          python -m unittest discover -s tests

      - name: Upload SBOMs and Firmware
        uses: actions/upload-artifact@v4
        with:
          name: firmware-sbom-artifacts
          path: |
            project/Objects/w78_std_8051.hex
            sbom/sbom.cdx.json
            sbom/sbom.spdx.json
            sbom/SBOM-REPORT.md
```
