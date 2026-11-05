# 操作指南：執行 SBOM 產生器的自動化單元測試

本指南說明如何執行本專案的自動化測試套件，以驗證 SBOM 提取引擎在解析 Keil 專案檔、編譯產物（Listing / Map）、遞迴標頭檔及工具鏈雜湊時的精確性與合規性。

---

## 適用情境

- 修改了 `tools/generate_c51_sbom.py` 提取邏輯後，需要進行迴歸測試。
- 在 CI/CD 流程中進行自動化測試防線阻擋。
- 更換了 Keil C51 版本或不同型號的 8051 MCU 專案，驗證提取引擎能否正常運作。

---

## 執行測試步驟

在專案根目錄下，執行 Python 內建的 `unittest` 模組：

```powershell
python -m unittest discover -s tests
```

### 預期終端輸出

```text
........
----------------------------------------------------------------------
Ran 8 tests in 0.025s

OK
```

---

## 測試案例清單與驗證目標

測試套件定義於 [`tests/test_sbom_generator.py`](file:///C:/Users/tester/Desktop/c51%20sbom/tests/test_sbom_generator.py)，包含 8 項針對性驗證：

| 測試案例 | 驗證目標 |
| :--- | :--- |
| `test_01_keil_c51_detected` | 驗證能透過 Windows 註冊表或預設路徑正確定位 Keil C51 安裝目錄及 `C51.exe`。 |
| `test_02_parse_uvproj` | 驗證 `.uvproj` 解析器能正確提取 Target Device（`W78E052D`）、Vendor（`Nuvoton`）以及 `AfterMake` 是否啟用。 |
| `test_03_parse_m51_runtime_library` | 驗證從 `.m51` 連結報表中精確識別 `C51S.LIB`，並提取內部載入模組 `?C_INIT` 與 `?C?UIDIV`，同時區分自訂模組 `STARTUP.OBJ (?C_STARTUP)`。 |
| `test_04_header_recursive_resolution` | 驗證沿 `C51\INC` 搜尋路徑遞迴解析標準標頭檔（`REG52.H`、`INTRINS.H`），並計算出 64 位元的 SHA-256 雜湊。 |
| `test_05_tools_ini_and_dual_versions` | 驗證工具鏈雙軌版本記錄：正確讀取 `TOOLS.INI` 套件發行版 `V9.61`，並從 `.lst` / `.m51` 萃取 `C51.exe`（V9.60.7.0）與 `A51.exe`（V8.2.7.0）真實執行檔版本。 |
| `test_06_cyclonedx_sbom_format` | 驗證產出的 `sbom.cdx.json` 符合 CycloneDX 1.5 結構，包含 `device`、`library`、`file` 組件與 `dependencies` 相依樹。 |
| `test_07_spdx_sbom_format` | 驗證產出的 `sbom.spdx.json` 符合 SPDX 2.3 結構，包含 Package、File 與 Relationship 定義。 |
| `test_08_markdown_report_content` | 驗證產出的 `SBOM-REPORT.md` 包含完整的晶片規格、雜湊值與表格內容。 |

---

## 疑難排解

### 若測試失敗：`AssertionError: 'C51S.LIB' not found in libraries`
- **原因**：可能尚未執行編譯，或 `project/Listings/w78_std_8051.m51` 檔案不存在或為舊檔案。
- **排除方式**：先執行一次 `powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1` 完成建置後，再重新執行單元測試。
