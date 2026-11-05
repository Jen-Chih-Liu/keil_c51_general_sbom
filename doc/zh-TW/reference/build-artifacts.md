# 技術參考：Keil C51 編譯產物結構與格式定義

本文件列出標準 Keil C51 在建置過程中產生的各類檔案，說明其內容格式以及 SBOM 產生器如何對其進行逆向資訊萃取。

---

## 1. 專案設定檔：`w78_std_8051.uvproj`

XML 格式之 Keil µVision 專案描述檔。

- **解析重點節點**：
  - `/Project/Targets/Target/TargetOption/TargetCommonOption/Device`：目標晶片名稱（`W78E052D`）。
  - `/Project/Targets/Target/TargetOption/TargetCommonOption/Vendor`：晶片供應商名稱（`Nuvoton` / `Winbond`）。
  - `/Project/Targets/Target/TargetOption/TargetCommonOption/Cpu`：記憶體與時脈設定（`IRAM(0x00-0xFF) IROM(0x0000-0x1FFF) CLOCK(40000000)`）。
  - `/Project/Targets/Target/TargetOption/Target51/Target51Misc/MemoryModel`：記憶體模型（`0` 代表 Small）。
  - `/Project/Targets/Target/TargetOption/TargetCommonOption/AfterMake/RunUserProg1`：Post-build hook 啟用標記。

---

## 2. Linker Map 報表檔：`Listings\w78_std_8051.m51`

由 Keil 連結器 `BL51.exe` 產生的記憶體配置與模組映射清單。

- **標頭區**：記載連結器完整版本（如 `BL51 BANKED LINKER/LOCATER V6.22.4.0`）與記憶體模型（`MEMORY MODEL: SMALL`）。
- **`INPUT MODULES INCLUDED:` 區段**：
  - 純文字列表，記載所有參與最終連結的二進位目標檔與函式庫。
  - 語法格式：`檔案絕對路徑 (模組名稱)`。
  - 範例：
    ```text
    INPUT MODULES INCLUDED:
      PROJECT\OBJECTS\STARTUP.OBJ (?C_STARTUP)
      PROJECT\OBJECTS\MAIN.OBJ (MAIN)
      C:\USERS\TESTER\APPDATA\LOCAL\KEIL_V5\C51\LIB\C51S.LIB (?C_INIT)
      C:\USERS\TESTER\APPDATA\LOCAL\KEIL_V5\C51\LIB\C51S.LIB (?C?UIDIV)
      C:\USERS\TESTER\APPDATA\LOCAL\KEIL_V5\C51\LIB\C51S.LIB (?C?SLCMP)
    ```
- **SBOM 萃取邏輯**：
  - 若路徑副檔名為 `.LIB`，識別為隱性執行期庫（`library`），將括號內名稱蒐集為 `keil:linked_module`。
  - 若路徑副檔名為 `.OBJ`，識別為專案自身模組，與 `src/` 進行對應。

---

## 3. Compiler / Assembler Listing 檔：`Listings\*.lst`

由 `C51.exe` 與 `A51.exe` 編譯原始碼時產生的單一檔案清單。

- **`main.lst` 標頭**：
  - 記載真實編譯器版本：`C51 COMPILER V9.60.7.0`。
  - 記載編譯命令列參數：`INCDIR(...)`、`OBJECT(...)` 等。
- **`STARTUP.lst` 標頭**：
  - 記載組譯器真實版本：`A51 MACRO ASSEMBLER V8.2.7.0`。

---

## 4. 工具鏈總設定檔：`TOOLS.INI`

位於 Keil 安裝根目錄（例如 `C:\Users\tester\AppData\Local\Keil_v5\TOOLS.INI`）。

- **`[C51]` 區段**：
  - `PATH`：C51 工具鏈路徑。
  - `VERSION=V9.61`：整個 Keil C51 Suite 的對外正式發布版本號。
- **SBOM 萃取邏輯**：
  - 提取 `VERSION` 作為套件層級的版本識別（`suite_version`）。

---

## 5. Intel HEX 韌體檔：`Objects\w78_std_8051.hex`

由 `OH51.exe` 將 OMF-51 二進位格式轉出的最終 ASCII 十六進位燒錄檔。

- 作為 SBOM 的根組件（Root Application Component）。
- 計算其 SHA-256、SHA-1 與 MD5 雜湊，作為最終釋出產物的防偽完整性指紋。
