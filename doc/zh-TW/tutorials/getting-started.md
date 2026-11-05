# 新手入門教學：從零建置 W78 專案並產出第一份 SBOM

本教學旨在帶領您在 Windows 環境下，從零開始編譯針對 Winbond / Nuvoton W78 系列（`W78E052D`）的標準 8051 韌體，並自動產出合規的 CycloneDX 與 SPDX 軟體物料清單（SBOM）。

---

## 學習目標

完成本教學後，您將會：
1. 了解專案的目錄結構與核心檔案角色。
2. 透過一鍵建置腳本完成無頭（Headless）編譯與連結。
3. 取得並檢視產出的 `sbom.cdx.json`、`sbom.spdx.json` 與 `SBOM-REPORT.md`。

---

## 前置條件

在開始之前，請確保您的環境具備：
- **作業系統**：Windows 10 / 11 64-bit。
- **Keil C51**：已安裝 Keil µVision 與 C51 編譯工具鏈（例如版本 V9.61）。
- **Python**：已安裝 Python 3.10+，且已將 `python` 加入系統 PATH（零 pip 依賴）。

> **詳細安裝指引**：若尚未安裝以上軟體，請參閱 [操作指南：開發環境與必要程式安裝設定](../how-to-guides/environment-setup.md)。

---

## 步驟一：檢查專案檔案與結構

在終端機中切換至專案根目錄，檢視關鍵檔案：
```powershell
Get-ChildItem -Path .
```

您將看到以下主要組成：
- `project/`：包含標準 8051 韌體原始碼 (`src/main.c`)、啟動碼 (`src/STARTUP.A51`) 與 Keil 專案檔 (`w78_std_8051.uvproj`)。
- `tools/generate_c51_sbom.py`：純 Python 實作的 SBOM 產生工具。
- `build_and_sbom.ps1`：一鍵自動化建置與 SBOM 生成腳本。

---

## 步驟二：執行一鍵建置流程

開啟 PowerShell（以一般使用者權限即可），執行根目錄的建置腳本：

```powershell
powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1
```

### 預期終端輸出

執行過程中，腳本將自動執行以下動作並輸出日誌：
1. **偵測 Keil C51 工具鏈**：從 Windows 註冊表或預設路徑定位 `C51.exe`、`A51.exe`、`BL51.exe`、`OH51.exe`。
2. **組譯啟動碼**：呼叫 `A51.exe` 組譯 `src\STARTUP.A51`，產出 `Objects\STARTUP.obj`。
3. **編譯主程式**：呼叫 `C51.exe` 編譯 `src\main.c`，產出 `Objects\main.obj`。
4. **連結與記憶體配置**：呼叫 `BL51.exe` 進行連結，自動載入執行期庫 `C51S.LIB`，產出 `Objects\w78_std_8051` 與 `Listings\w78_std_8051.m51`。
5. **產生 Intel HEX**：呼叫 `OH51.exe` 產出最終二進位燒錄檔 `Objects\w78_std_8051.hex`。
6. **解析建置產物產出 SBOM**：執行 `generate_c51_sbom.py`，並輸出完成訊息：

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

## 步驟三：檢驗產出的 SBOM 檔案

建置完成後，檢查 `sbom/` 目錄：
```powershell
Get-ChildItem -Path .\sbom
```

您將看到三個不同格式的 SBOM 產物：
1. **`sbom/SBOM-REPORT.md`**：易讀的 Markdown 報告。使用文字編輯器開啟，確認表格已列出：
   - 目標 MCU：`W78E052D`
   - 隱性連結庫：`C51S.LIB`（含內部模組 `?C_INIT`、`?C?UIDIV`）
   - 標準標頭檔：`REG52.H`、`INTRINS.H` 及其 SHA-256 雜湊
   - 建置工具鏈：`C51.exe` (V9.60.7.0)、`A51.exe` (V8.2.7.0)、`BL51.exe` (V6.22.4.0)
2. **`sbom/sbom.cdx.json`**：標準 CycloneDX v1.5 JSON，供企業 SCA 系統或相依性管理平台匯入。
3. **`sbom/sbom.spdx.json`**：標準 SPDX v2.3 JSON，供合規稽核與開源授權驗證。

---

## 下一步

恭喜！您已成功完成標準 8051 專案的首次建置並產出了完整的韌體 SBOM。

接下來您可以閱讀：
- [操作指南：在 Keil µVision GUI 中設定按 F7 自動產生 SBOM](../how-to-guides/keil-gui-integration.md) 了解如何融入日常 IDE 開發。
- [概念解說：為何標準 8051 專案必須採用編譯產物逆向 SBOM？](../explanation/why-build-artifact-sbom.md) 深入了解其背後的資安合規與架構機制。
