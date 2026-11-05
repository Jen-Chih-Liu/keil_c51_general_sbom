# How-To: Development Environment & Prerequisites Setup

This guide walks you through installing and configuring all necessary software components on a clean Windows machine to build the 8051 firmware and generate SBOMs.

---

## 1. Prerequisites Overview

| Software | Minimum Version | License | Purpose |
| :--- | :--- | :--- | :--- |
| **Windows OS** | Windows 10 or 11 (64-bit) | Commercial | Host OS for running Keil toolchain and PowerShell |
| **Keil C51 Toolchain** | C51 V9.60 or V9.61 (Recommended) | Evaluation (Free 2KB limit) or Licensed | Provides `C51.exe`, `A51.exe`, `BL51.exe`, `OH51.exe`, and standard 8051 headers |
| **Python** | Python 3.10+ (3.10 ~ 3.12 recommended) | Open Source (PSF) | Runs the SBOM extraction engine and automated unit tests (Zero pip dependencies) |

---

## 2. Installing Keil C51 Toolchain

### Step A: Download the Installer
1. Navigate to the official Arm Keil download page: [Keil C51 Evaluation Software](https://www.keil.com/demo/eval/c51.htm).
2. Complete the brief contact form to download `c51v961.exe` (~100 MB).

### Step B: Run the Setup Wizard
1. Double-click `c51v961.exe`.
2. Follow the setup wizard and accept the license agreement.
3. Keep the default installation directory (typically `C:\Keil_v5` or under `%LOCALAPPDATA%\Keil_v5`).
4. Complete the installation.

### Step C: Verify Keil C51 Installation
Open Windows PowerShell and check the registry key:
```powershell
Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Keil\Products\C51" -ErrorAction SilentlyContinue | Select-Object Path, Version
```
Expected output:
```text
Path                                     Version
----                                     -------
C:\Users\tester\AppData\Local\Keil_v5\C51 V9.61  
```

---

## 3. Installing Python

The SBOM generator uses Python 3.10+ standard libraries only; **no additional pip packages are required**.

### Option A: Via Windows Package Manager (`winget` - Recommended)
Run the following in PowerShell:
```powershell
winget install Python.Python.3.10 --override "/passive PrependPath=1"
```

### Option B: Manual Installation from Python.org
1. Visit [Python.org Downloads](https://www.python.org/downloads/).
2. Download the Windows installer (64-bit).
3. In the installer, **ensure you check the box "Add python.exe to PATH"**, then click **Install Now**.

### Verify Python Installation
Open a **new** PowerShell window and run:
```powershell
python --version
```
It should display `Python 3.10.x` or newer.

---

## 4. End-to-End Environment Verification

Once both tools are installed, test the environment by running:

```powershell
# 1. Run headless build and SBOM pipeline
powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1

# 2. Run unit tests
python -m unittest discover -s tests
```

If both commands return exit code `0`, your environment is fully configured and ready!
