# Reference: Command-Line Interface (CLI) Manual

This document provides technical specifications and command-line argument references for the project's build and SBOM generation tools.

---

## 1. SBOM Generator: `tools/generate_c51_sbom.py`

Pure Python 3.10+ implementation with zero external pip dependencies.

### Usage

```powershell
python tools/generate_c51_sbom.py [--project-dir DIR] [--keil-path PATH] [--out-dir DIR]
```

### Options

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--project-dir` | String (Path) | `project` | Path to the Keil C51 project directory containing `.uvproj`, `src/`, `Listings/`, and `Objects/`. |
| `--keil-path` | String (Path) | `None` (Auto-detect) | Path to the Keil C51 installation root (e.g. `C:\Users\tester\AppData\Local\Keil_v5\C51`). If omitted, detected via registry and standard paths. |
| `--out-dir` | String (Path) | `sbom` | Destination directory for generated SBOM files (created automatically if missing). |

### Exit Codes

- `0`: Extraction successful; CycloneDX, SPDX, and Markdown reports created.
- `1`: Project file or essential build evidence missing.

---

## 2. Build Pipeline Script: `build_and_sbom.ps1`

Windows PowerShell script for clean, automated builds.

### Usage

```powershell
powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1 [-KeilPath <string>]
```

### Options

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `-KeilPath` | String (Path) | `""` (Auto-detect) | Overrides the Keil C51 installation path. |

### Exit Codes

- `0`: Assembly, compilation, linking, HEX conversion, and SBOM generation all completed successfully.
- Non-zero: Build error returned by the respective toolchain executable (e.g., exit code `3` for linker error).
