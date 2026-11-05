# 操作指南：在 Keil µVision GUI 中設定按 F7 自動產生 SBOM

本指南說明如何在 Keil µVision 整合開發環境（IDE）中設定 Post-Build Hook（建置後處理程序），讓工程師在按 **F7**（Build Target）或 **Rebuild** 後，IDE 會自動執行 Python 工具更新 SBOM。

---

## 適用情境

- 韌體工程師習慣在 Keil µVision GUI 介面中進行開發、編譯與模擬除錯。
- 希望在每次成功編譯產出韌體二進位檔後，目錄下的 SBOM 檔案能無縫同步更新，無需切換至終端機手動輸入指令。

---

## 操作步驟

### 步驟 1：開啟專案並進入設定頁面
1. 啟動 Keil µVision。
2. 透過選單 `Project` -> `Open Project...`，選取本專案的 `project\w78_std_8051.uvproj`。
3. 在左側 Project 導航視窗中，於 Target 名稱（`Target 1`）上點擊滑鼠右鍵，選取 **Options for Target 'Target 1'...**（或直接按快捷鍵 `Alt + F7`）。

### 步驟 2：切換至 User 命令設定分頁
1. 在彈出的 Options 視窗中，點擊上方的 **User** 標籤頁。
2. 找到 **After Build/Rebuild** 區塊。

### 步驟 3：配置 Run #1 指令
1. 勾選 **Run #1** 核取方塊。
2. 在右側文字框中輸入呼叫 Python SBOM 產生器的指令：
   ```text
   python ..\tools\generate_c51_sbom.py --project-dir .
   ```
   > **路徑提示**：因為 Keil 在執行 User 指令時的工作目錄（Working Directory）即為 `.uvproj` 所在目錄（即 `project\`），因此使用相對路徑 `..\tools\generate_c51_sbom.py` 指向腳本，並傳入 `--project-dir .`。
3. 點擊右下角的 **OK** 按鈕儲存設定。

### 步驟 4：驗證自動更新效果
1. 在 Keil µVision 中，點擊選單 `Project` -> `Build Target`（或直接按鍵盤 **F7**）。
2. 觀察下方 **Build Output** 視窗的執行日誌。編譯完成後，最後將顯示如下訊息：
   ```text
   linking...
   Program Size: data=14.0 xdata=0 code=395
   creating hex file from ".\Objects\w78_std_8051"...
   ".\Objects\w78_std_8051" - 0 Error(s), 0 Warning(s).
   User command #1: python ..\tools\generate_c51_sbom.py --project-dir .
   [*] Found Keil C51: C:\Users\tester\AppData\Local\Keil_v5\C51
   [*] Target MCU: W78E052D (Nuvoton)
   [+] Generated CycloneDX 1.5 JSON: ...\sbom\sbom.cdx.json
   [+] Generated SPDX 2.3 JSON:      ...\sbom\sbom.spdx.json
   [+] Generated Markdown Report:   ...\sbom\SBOM-REPORT.md
   [*] SBOM Generation completed successfully.
   ```
3. 檢查 `sbom/` 目錄，確認三個檔案的時間戳記已更新為最新建置時間。

---

## 常見問題與排除

### Q1：Build Output 顯示 `'python' is not recognized as an internal or external command`？
- **原因**：系統環境變數 `PATH` 中未包含 Python 的安裝路徑。
- **解決方法**：
  1. 請確認在 Windows 命令提示字元輸入 `python --version` 能正常執行。
  2. 若無，請將 Python 安裝目錄（例如 `C:\Users\username\AppData\Local\Programs\Python\Python310`）加入系統環境變數 `PATH`，並**重啟 Keil µVision** 以載入新環境變數。
  3. 或在 User #1 填入 Python 的完整絕對路徑：
     ```text
     "C:\Users\tester\AppData\Local\Programs\Python\Python310\python.exe" ..\tools\generate_c51_sbom.py --project-dir .
     ```
