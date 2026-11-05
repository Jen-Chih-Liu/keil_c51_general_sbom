# Keil C51 標準 8051 (Winbond / Nuvoton W78 系列) 專案與 SBOM 生成解決方案

本專案提供針對**標準 8051 架構、無外部 BSP、僅使用標準 8051 標頭檔**（`<REG52.H>`、`<INTRINS.H>`）的 Keil C51 韌體專案範本，並實作基於建置證據（Build-Artifact Evidence）的自動化軟體物料清單（SBOM）產生器。

---

## 1. 核心背景與痛點

### 傳統 SBOM 工具在標準 8051 上的盲點
傳統 SCA / SBOM 工具（如 Syft、Trivy、cdxgen 等）主要透過掃描現代套件管理清單（如 `package.json`、`pom.xml`、`requirements.txt`、`CMakeLists.txt` 或 CMSIS-Pack）。但在標準 8051 開發中：
1. **無套件清單（Zero Manifest）**：專案通常只有 `STARTUP.A51` 與 `.c` 原始檔，直接 `#include <REG52.H>`。
2. **無外部 BSP**：不依賴任何外部廠商 SDK 或開源庫。
3. **隱性二進位相依（Implicit Binary Dependency）**：雖然工程師沒有手動加入函式庫，但 Keil Linker (`BL51.exe`) 在連結時，會依據 Memory Model（如 Small）自動將 Keil 閉源的執行期函式庫（`C51S.LIB`）與內部模組（如 `?C_INIT`、`?C?UIDIV`）打包進最終韌體。

若僅掃描原始碼目錄，一般工具只會產出**空的 SBOM**，無法滿足歐盟網路韌性法案（Cyber Resilience Act, CRA）與工業/車用安全標準對於「完整二進位組件可追溯性與 SHA-256 完整性」的合規要求。

---

## 2. 解決方案：建置證據驅動之 SBOM 提取

本工具透過解析 Keil C51 編譯與連結產物，逆向萃取 5 大類組件：

```
[Keil µVision .uvproj] ───────► 硬體目標組件 (W78E052D MCU, RAM/ROM 規格)
[Compiler .lst & 原始碼] ─────► 遞迴標頭檔組件 (C51\INC\REG52.H, INTRINS.H 與版權宣告)
[Linker .m51 Map 檔] ────────► 隱性執行期函式庫 (C51\LIB\C51S.LIB 與 ?C_INIT, ?C?UIDIV 模組)
[STARTUP.A51 & main.c] ──────► 原始碼組件 (SHA-256 雜湊值)
[Keil TOOLS.INI & .exe] ─────► 工具鏈來源 (套件 V9.61 + C51 V9.60.7.0, A51 V8.2.7.0, BL51 V6.22.4.0)
         │
         ▼
[tools/generate_c51_sbom.py]
         │
         ├──► CycloneDX v1.5 JSON  (sbom/sbom.cdx.json)
         ├──► SPDX v2.3 JSON       (sbom/sbom.spdx.json)
         └──► Markdown 稽核報告    (sbom/SBOM-REPORT.md)
```

---

## 3. 目錄結構

```
c51 sbom/
├── build_and_sbom.ps1        # 一鍵編譯與 SBOM 生成 PowerShell 腳本
├── README.md                 # 專案與技術說明文件
├── project/                  # Keil C51 韌體專案
│   ├── w78_std_8051.uvproj   # Keil µVision 專案檔 (設定 W78E052D 與 AfterMake Hook)
│   ├── src/
│   │   ├── STARTUP.A51       # Keil 8051 標準啟動碼 (提供 ?C_STARTUP)
│   │   └── main.c            # 韌體主程式 (Timer0, UART, 觸發 ?C_INIT / ?C?UIDIV)
│   ├── Listings/             # 編譯產出報表 (main.lst, STARTUP.lst, w78_std_8051.m51)
│   └── Objects/              # 執行檔與韌體映像 (w78_std_8051, w78_std_8051.hex)
├── tools/
│   └── generate_c51_sbom.py  # 零相依性 Python SBOM 產生器
├── tests/
│   └── test_sbom_generator.py# 自動化單元測試套件
└── sbom/                     # 產出的標準 SBOM 檔案
    ├── sbom.cdx.json         # CycloneDX 1.5 JSON
    ├── sbom.spdx.json        # SPDX 2.3 JSON
    └── SBOM-REPORT.md        # 易讀 Markdown 稽核摘要
```

---

## 4. 軟體安裝與環境需求 (Prerequisites)

在執行建置與產生 SBOM 之前，您的 Windows 電腦需要具備以下環境：

| 軟體工具 | 最低版本要求 | 用途 | 安裝與確認方式 |
| :--- | :--- | :--- | :--- |
| **作業系統** | Windows 10 / 11 (64-bit) | 執行 Keil 工具鏈與 PowerShell 腳本 | - |
| **Keil C51** | C51 V9.60+ (推薦 V9.61) | 提供 8051 編譯器 (`C51.exe`)、組譯器 (`A51.exe`)、連結器 (`BL51.exe`)、十六進位轉換器 (`OH51.exe`) 與標準標頭檔 | 至 [Keil 官方網站](https://www.keil.com/demo/eval/c51.htm) 下載安裝 **C51 Development Tools**（評估版或正式授權版皆可）。<br>預設安裝路徑：`C:\Keil_v5\C51` 或 `%LOCALAPPDATA%\Keil_v5\C51`。 |
| **Python** | Python 3.10+ | 執行 SBOM 提取引擎與自動化驗證 | 1. 透過官方網站下載，或使用 Windows 套件管理員指令：<br>`winget install Python.Python.3.10`<br>2. **重要**：安裝時請務必勾選 **"Add python.exe to PATH"**。<br>3. **零相依性**：本專案僅使用 Python 標準庫，**不需要執行任何 `pip install`**。 |

### 驗證安裝狀態
開啟 PowerShell 執行以下命令確認環境是否就緒：
```powershell
# 確認 Python 版本
python --version

# 確認 Keil C51 註冊表或路徑
Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Keil\Products\C51" -ErrorAction SilentlyContinue
```

---

## 5. 快速使用操作指南

本專案支援 **GUI IDE 自動觸發** 與 **無頭命令列（Headless CLI）一鍵執行** 兩種模式：

### 模式 A：Windows PowerShell 一鍵建置（推薦 CI/CD 與本機使用）
在專案根目錄開啟 PowerShell 執行：
```powershell
powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1
```
腳本將自動：
1. 自動從 Windows 註冊表或安裝路徑偵測 Keil C51 工具鏈。
2. 呼叫 `A51.exe`、`C51.exe`、`BL51.exe`、`OH51.exe` 編譯專案並輸出 `.hex` 與 `.m51`。
3. 執行 Python SBOM 產生器產出 `sbom/sbom.cdx.json`、`sbom/sbom.spdx.json` 與 `sbom/SBOM-REPORT.md`。

### 模式 B：Keil µVision GUI 整合（F7 鍵自動更新 SBOM）
1. 用 Keil µVision 開啟 `project\w78_std_8051.uvproj`。
2. 專案已在 `Options for Target -> User -> After Build/Rebuild` 中配置 `Run #1`：
   ```
   python ..\tools\generate_c51_sbom.py --project-dir .
   ```
3. 只要在 Keil IDE 內按 **F7**（Build Target），編譯完成後 Keil 會自動執行 Python 腳本更新 `sbom/` 目錄下的所有 SBOM 檔案。

### 模式 C：單獨執行 SBOM 產生器
如果已在 Keil 中編譯完成，只想重新產出 SBOM：
```powershell
python tools\generate_c51_sbom.py --project-dir project --out-dir sbom
```

---

## 6. 執行自動化測試

本專案附帶完備的單元測試，驗證 SBOM 格式、隱性庫模組解析與 SHA-256 雜湊正確性：
```powershell
python -m unittest discover -s tests
```

---

## 7. SBOM 報告範例節錄 (`sbom/SBOM-REPORT.md`)

```markdown
# Software Bill of Materials (SBOM) Report
**Project**: `w78_std_8051`
**Target MCU**: `W78E052D` (Nuvoton)
**Architecture**: Standard 8051 / 8052 Core (Zero-BSP Bare Metal)
**Memory Model**: SMALL

## 1. Deliverable Firmware Image
| Deliverable | SHA-256 Hash |
| :--- | :--- |
| **Intel HEX** | `9c9e09be28db7e94ba597e04d10d47fe315f61f55910366004c8d8a88aa203cc` |

## 2. Hardware Component (`device`)
| Component | Vendor | Specs |
| :--- | :--- | :--- |
| **W78E052D** | Nuvoton | IRAM(0x00-0xFF) IROM(0x0000-0x1FFF) CLOCK(40000000) |

## 3. Implicitly Linked Keil Runtime Libraries (`library`)
| Library | Linked Internal Modules | SHA-256 Hash | Path |
| :--- | :--- | :--- | :--- |
| **C51S.LIB** | `?C_INIT`, `?C?UIDIV`, `?C?SLCMP` | `aaf864826f6...` | `C:\...\C51\LIB\C51S.LIB` |

## 4. Standard 8051 Header Files (`file`)
| Header | Copyright / Notice | SHA-256 Hash |
| :--- | :--- | :--- |
| **REG52.H** | Copyright (c) 1988-2002 Keil Elektronik GmbH | `328f7051822...` |
| **INTRINS.H** | Copyright (c) 1988-2010 Keil Elektronik GmbH and ARM Germany GmbH | `027ed466a54...` |

## 5. Build Toolchain Provenance (`metadata.tools`)
| Tool | Suite Release | Executable Version | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| **C51.exe** | V9.61 | V9.60.7.0 | `e54096a4...` |
| **A51.exe** | V9.61 | V8.2.7.0 | `f9c791ce...` |
| **BL51.exe** | V9.61 | V6.22.4.0 | `c59a2959...` |
| **OH51.exe** | V9.61 | V2.7.0.0 | `69d3419a...` |
```
