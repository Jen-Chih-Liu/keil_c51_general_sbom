# Getting Started: Build a W78 Project & Generate Your First SBOM

This tutorial guides you through building a standard Winbond / Nuvoton W78 series (`W78E052D`) 8051 firmware project from scratch on Windows, and generating compliant CycloneDX and SPDX Software Bill of Materials (SBOM) documents.

---

## Learning Objectives

After completing this tutorial, you will:
1. Understand the directory structure and the role of key project files.
2. Build the bare-metal firmware using an automated headless build script.
3. Inspect and verify the generated `sbom.cdx.json`, `sbom.spdx.json`, and `SBOM-REPORT.md`.

---

## Prerequisites

Before starting, ensure your system meets the following requirements:
- **Operating System**: Windows 10 or 11 (64-bit).
- **Keil C51**: Keil µVision with C51 Toolchain installed (e.g. V9.61).
- **Python**: Python 3.10+ installed with `python` available in your system `PATH` (Zero pip dependencies).

> **Installation Guide**: For step-by-step setup instructions, see [How-To: Development Environment & Prerequisites Setup](../how-to-guides/environment-setup.md).

---

## Step 1: Inspect the Project Structure

Navigate to the project directory in a terminal and list the files:
```powershell
Get-ChildItem -Path .
```

You will see the following key components:
- `project/`: Contains the firmware source (`src/main.c`), standard startup code (`src/STARTUP.A51`), and the Keil project file (`w78_std_8051.uvproj`).
- `tools/generate_c51_sbom.py`: Standalone Python tool that extracts SBOM components from build artifacts.
- `build_and_sbom.ps1`: Automated build and SBOM generation script for Windows PowerShell.

---

## Step 2: Execute the One-Click Build Pipeline

Open PowerShell (no administrator privileges required) and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1
```

### Expected Output

The script executes the following steps and prints detailed logs:
1. **Detect Toolchain**: Automatically finds Keil C51 binaries (`C51.exe`, `A51.exe`, `BL51.exe`, `OH51.exe`) via the Windows registry or standard paths.
2. **Assemble Startup Code**: Assembles `src\STARTUP.A51` into `Objects\STARTUP.obj`.
3. **Compile Application**: Compiles `src\main.c` into `Objects\main.obj`.
4. **Link Firmware**: Links object files using `BL51.exe`, automatically pulling in the implicit runtime library `C51S.LIB`.
5. **Convert to HEX**: Converts the OMF-51 output into `Objects\w78_std_8051.hex`.
6. **Generate SBOM**: Runs `generate_c51_sbom.py` to extract components and export reports:

```text
==========================================================
  Winbond / Nuvoton W78 Series Keil C51 Build & SBOM Pipeline
==========================================================
[*] Found Keil C51 Toolchain: C:\Users\tester\AppData\Local\Keil_v5\C51
[*] Cleaning old build artifacts...
[*] Assembling STARTUP.A51...
ASSEMBLY COMPLETE.  0 WARNING(S), 0 ERROR(S)
[*] Compiling main.c...
C51 COMPILATION COMPLETE.  0 WARNING(S),  0 ERROR(S)
[*] Linking modules with BL51...
LINK/LOCATE RUN COMPLETE.  0 WARNING(S),  0 ERROR(S)
[*] Generating Intel HEX with OH51...
OBJECT TO HEX CONVERSION COMPLETED.
[+] Firmware built successfully: ...\project\Objects\w78_std_8051.hex
[*] Generating CycloneDX, SPDX, and Markdown SBOM...
[+] Generated CycloneDX 1.5 JSON: ...\sbom\sbom.cdx.json
[+] Generated SPDX 2.3 JSON:      ...\sbom\sbom.spdx.json
[+] Generated Markdown Report:   ...\sbom\SBOM-REPORT.md
==========================================================
```

---

## Step 3: Inspect the Generated SBOMs

Check the contents of the `sbom/` directory:
```powershell
Get-ChildItem -Path .\sbom
```

You will see three formats:
1. **`sbom/SBOM-REPORT.md`**: Human-readable Markdown report. Open it to inspect:
   - Target MCU: `W78E052D`
   - Implicit Library: `C51S.LIB` (modules `?C_INIT`, `?C?UIDIV`)
   - Standard Headers: `REG52.H`, `INTRINS.H` and their SHA-256 hashes
   - Toolchain Binaries: `C51.exe` (V9.60.7.0), `A51.exe` (V8.2.7.0), `BL51.exe` (V6.22.4.0)
2. **`sbom/sbom.cdx.json`**: Standard CycloneDX v1.5 JSON file ready for SCA platforms.
3. **`sbom/sbom.spdx.json`**: Standard SPDX v2.3 JSON file ready for legal and compliance audits.

---

## Next Steps

Congratulations! You have built your first bare-metal 8051 project and generated a full SBOM.

Next, you can explore:
- [How-To: Configure Keil µVision to Automatically Generate SBOM on F7](../how-to-guides/keil-gui-integration.md)
- [Explanation: Why Bare-Metal 8051 Projects Need Build-Artifact-Driven SBOMs](../explanation/why-build-artifact-sbom.md)
