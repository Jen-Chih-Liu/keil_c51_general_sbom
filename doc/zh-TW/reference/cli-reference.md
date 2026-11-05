# 技術參考：命令列工具參數與指令清單

本文件提供專案中自動化腳本及 SBOM 產生器的命令列介面（CLI）技術規格與參數說明。

---

## 1. SBOM 產生器：`tools/generate_c51_sbom.py`

純 Python 實作（支援 Python 3.10+，零第三方套件相依）。

### 語法

```powershell
python tools/generate_c51_sbom.py [--project-dir DIR] [--keil-path PATH] [--out-dir DIR]
```

### 參數規格

| 參數 | 型態 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- |
| `--project-dir` | 字串 (路徑) | `project` | Keil 專案所在目錄，目錄下需包含 `.uvproj`、`src/`、`Listings/`、`Objects/`。 |
| `--keil-path` | 字串 (路徑) | `None` (自動偵測) | Keil C51 安裝根目錄（例如 `C:\Users\tester\AppData\Local\Keil_v5\C51`）。若未指定，工具將依序查詢 Windows 登錄表與標準預設路徑。 |
| `--out-dir` | 字串 (路徑) | `sbom` | 產出的 SBOM 檔案存放目錄（若目錄不存在將自動建立）。 |

### 返回碼 (Exit Code)

- `0`：解析建置產物成功，且成功產出 CycloneDX、SPDX 與 Markdown 報告。
- `1`：在 `--project-dir` 下找不到 `.uvproj` 專案檔或關鍵建置產物遺失。

---

## 2. 一鍵建置腳本：`build_and_sbom.ps1`

Windows PowerShell 批次自動化執行腳本。

### 語法

```powershell
powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1 [-KeilPath <string>]
```

### 參數規格

| 參數 | 型態 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- |
| `-KeilPath` | 字串 (路徑) | `""` (自動偵測) | 覆寫 Keil C51 的安裝路徑。若未給定，自動由 Windows 註冊表尋找。 |

### 返回碼 (Exit Code)

- `0`：組譯、編譯、連結、轉 HEX 與 SBOM 產出全流程成功。
- 非 `0`：任一步驟編譯錯誤或退出失敗，錯誤碼為該工具鏈原生的 Exit Code（例如 BL51 連結失敗返回 `3`）。
