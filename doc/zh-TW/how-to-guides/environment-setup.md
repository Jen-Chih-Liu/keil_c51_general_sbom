# 操作指南：開發環境與必要程式安裝設定

本指南提供詳細的步驟，引導您在全新的 Windows 電腦上安裝本專案所需的所有軟體環境，包括 Keil C51 編譯工具鏈與 Python 執行環境。

---

## 1. 必要軟體清單總覽

| 軟體名稱 | 最低需求版本 | 授權類型 | 用途 |
| :--- | :--- | :--- | :--- |
| **Windows 作業系統** | Windows 10 或 Windows 11 (64-bit) | 商業授權 | 執行 Keil 與 PowerShell 自動化腳本 |
| **Keil C51 Toolchain** | C51 V9.60 或 V9.61 (推薦) | 評估版 (免費 2KB 限制) 或 正式版 | 提供 8051 編譯器、組譯器、BL51 連結器與標準標頭檔 |
| **Python** | Python 3.10 以上 (推薦 3.10 ~ 3.12) | PSF 開源授權 | 執行 SBOM 提取引擎與自動化驗證測試（零 pip 依賴） |

---

## 2. 安裝 Keil C51 工具鏈

### 步驟 A：下載安裝檔
1. 前往 Arm Keil 官方網站下載頁面：[Keil C51 Evaluation Software](https://www.keil.com/demo/eval/c51.htm)。
2. 填寫基本的聯絡資訊表單後，即可下載最新版的 `c51v961.exe`（或最新版本安裝檔，檔案大小約 100 MB）。

### 步驟 B：執行安裝精靈
1. 雙擊執行下載的 `c51v961.exe`。
2. 點擊 **Next** 並同意授權合約條款。
3. **選擇安裝路徑**：
   - 預設路徑通常為 `C:\Keil_v5` 或使用者 AppData 目錄。
   - 保持預設值即可。安裝程式會自動建立 `C51` 子目錄（內含 `BIN`、`INC`、`LIB` 等目錄）。
4. 點擊 **Finish** 完成安裝。

### 步驟 C：驗證 Keil C51 安裝
開啟 Windows PowerShell，執行以下指令確認安裝與登錄表資訊：
```powershell
# 檢查註冊表路徑
Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Keil\Products\C51" -ErrorAction SilentlyContinue | Select-Object Path, Version
```
若輸出類似以下資訊，即表示 Keil C51 已正確登錄：
```text
Path                                     Version
----                                     -------
C:\Users\tester\AppData\Local\Keil_v5\C51 V9.61  
```

---

## 3. 安裝 Python 環境

本專案的 SBOM 產生器與單元測試均採用 Python 3.10+ 標準庫編寫，**不需要安裝任何額外的 pip 第三方套件**。

### 方式 A：使用 Windows 套件管理員 (winget) 安裝（最推薦，一鍵完成）
在 PowerShell 中執行以下命令：
```powershell
winget install Python.Python.3.10 --override "/passive PrependPath=1"
```

### 方式 B：手動至官網下載安裝
1. 前往 [Python 官方網站下載頁面](https://www.python.org/downloads/)。
2. 下載 Python 3.10+ 的 Windows installer (64-bit)。
3. 執行安裝程式時，**務必勾選最下方的 "Add python.exe to PATH"**（將 Python 加入環境變數），然後點擊 **Install Now**。

### 驗證 Python 安裝
安裝完成後，開啟**新的** PowerShell 視窗，執行：
```powershell
python --version
```
輸出應顯示 `Python 3.10.x` 或更高版本。

---

## 4. 驗證本專案整體環境就緒

完成上述兩項軟體安裝後，請在專案根目錄執行測試命令：

```powershell
# 1. 執行一鍵建置與 SBOM 產生
powershell -ExecutionPolicy Bypass -File .\build_and_sbom.ps1

# 2. 執行自動化測試
python -m unittest discover -s tests
```

若兩個命令皆執行成功且退出碼為 0，即代表您的開發與 SBOM 產出環境已 100% 準備完成！
