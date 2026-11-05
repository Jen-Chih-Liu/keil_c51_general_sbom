# ==============================================================================
# Keil C51 W78 Series Firmware Build & SBOM Generation Script
# ==============================================================================
param(
    [string]$KeilPath = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Winbond / Nuvoton W78 Series Keil C51 Build & SBOM Pipeline" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Locate Keil C51 Toolchain
if (-not $KeilPath) {
    # Check Registry
    $regPaths = @(
        "HKLM:\SOFTWARE\WOW6432Node\Keil\Products\C51",
        "HKLM:\SOFTWARE\Keil\Products\C51",
        "HKCU:\SOFTWARE\Keil\Products\C51"
    )
    foreach ($rp in $regPaths) {
        if (Test-Path $rp) {
            $val = (Get-ItemProperty -Path $rp -ErrorAction SilentlyContinue).Path
            if ($val -and (Test-Path $val)) {
                $KeilPath = $val
                break
            }
        }
    }
}

if (-not $KeilPath) {
    $candidates = @(
        "$env:LOCALAPPDATA\Keil_v5\C51",
        "C:\Users\tester\AppData\Local\Keil_v5\C51",
        "C:\Keil_v5\C51",
        "C:\Keil\C51"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) {
            $KeilPath = $c
            break
        }
    }
}

if (-not $KeilPath -or -not (Test-Path $KeilPath)) {
    Write-Error "[!] Keil C51 toolchain directory not found! Please specify with -KeilPath."
    exit 1
}

Write-Host "[*] Found Keil C51 Toolchain: $KeilPath" -ForegroundColor Green

$A51 = Join-Path $KeilPath "BIN\A51.exe"
$C51 = Join-Path $KeilPath "BIN\C51.exe"
$BL51 = Join-Path $KeilPath "BIN\BL51.exe"
$OH51 = Join-Path $KeilPath "BIN\OH51.exe"
$IncDir = Join-Path $KeilPath "INC"

# 2. Setup Directories
$ProjectDir = Join-Path $ScriptDir "project"
$ObjDir = Join-Path $ProjectDir "Objects"
$LstDir = Join-Path $ProjectDir "Listings"
$SbomDir = Join-Path $ScriptDir "sbom"

New-Item -ItemType Directory -Force -Path $ObjDir, $LstDir, $SbomDir | Out-Null

# 3. Clean previous build artifacts
Write-Host "[*] Cleaning old build artifacts..." -ForegroundColor Yellow
Remove-Item -Path "$ObjDir\*", "$LstDir\*" -Force -Recurse -ErrorAction SilentlyContinue

# Execute build from Project directory to avoid spaces in relative module arguments
Push-Location $ProjectDir
try {
    # 4. Assemble STARTUP.A51
    Write-Host "[*] Assembling STARTUP.A51..." -ForegroundColor Yellow
    & $A51 "src\STARTUP.A51" "PRINT(Listings\STARTUP.lst)" "OBJECT(Objects\STARTUP.obj)"
    if ($LASTEXITCODE -ne 0) {
        throw "A51 assembly failed with exit code $LASTEXITCODE"
    }

    # 5. Compile main.c
    Write-Host "[*] Compiling main.c..." -ForegroundColor Yellow
    & $C51 "src\main.c" "INCDIR($IncDir)" "PRINT(Listings\main.lst)" "OBJECT(Objects\main.obj)" "OPTIMIZE(8,SPEED)" "SMALL"
    if ($LASTEXITCODE -ne 0) {
        throw "C51 compilation failed with exit code $LASTEXITCODE"
    }

    # 6. Link with BL51
    Write-Host "[*] Linking modules with BL51..." -ForegroundColor Yellow
    & $BL51 "Objects\STARTUP.obj, Objects\main.obj" TO "Objects\w78_std_8051" "PRINT(Listings\w78_std_8051.m51)" "RAMSIZE(256)"
    if ($LASTEXITCODE -ne 0) {
        throw "BL51 link failed with exit code $LASTEXITCODE"
    }

    # 7. Convert OMF to Intel HEX
    Write-Host "[*] Generating Intel HEX with OH51..." -ForegroundColor Yellow
    & $OH51 "Objects\w78_std_8051" "HEXFILE(Objects\w78_std_8051.hex)"
    if ($LASTEXITCODE -ne 0) {
        throw "OH51 hex conversion failed with exit code $LASTEXITCODE"
    }

    $targetHex = Join-Path $ObjDir "w78_std_8051.hex"
    Write-Host "[+] Firmware built successfully: $targetHex" -ForegroundColor Green
}
finally {
    Pop-Location
}

# 8. Generate SBOM
Write-Host "[*] Generating CycloneDX, SPDX, and Markdown SBOM..." -ForegroundColor Yellow
$GeneratorScript = Join-Path $ScriptDir "tools\generate_c51_sbom.py"
python "$GeneratorScript" --project-dir "$ProjectDir" --out-dir "$SbomDir" --keil-path "$KeilPath"
if ($LASTEXITCODE -ne 0) {
    Write-Error "[!] SBOM generation failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Pipeline Finished! SBOM generated at: $SbomDir" -ForegroundColor Green
Write-Host "  - CycloneDX 1.5 JSON : $SbomDir\sbom.cdx.json" -ForegroundColor Green
Write-Host "  - SPDX 2.3 JSON      : $SbomDir\sbom.spdx.json" -ForegroundColor Green
Write-Host "  - Markdown Report    : $SbomDir\SBOM-REPORT.md" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
