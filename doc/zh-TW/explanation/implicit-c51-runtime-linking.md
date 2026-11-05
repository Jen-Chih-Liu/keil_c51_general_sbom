# 概念解說：Keil C51 隱性執行期函式庫 (C51S.LIB) 的連結原理

本篇概念解說深入剖析 Keil C51 連結器（`BL51.exe` / `LX51.exe`）在背景默默執行的「隱性函式庫連結機制」，以及在不同 C 語言語意下，哪些內部模組會被自動引入最終韌體。

---

## 1. 記憶體模型與標準函式庫家族

Keil C51 依據 8051 特殊的 Harvard 記憶體架構（DATA、IDATA、XDATA、PDATA、CODE），設計了對應不同記憶體模型（Memory Model）的預先編譯函式庫：

| 記憶體模型 | 預設變數配置空間 | 對應之 Keil 隱性函式庫 |
| :--- | :--- | :--- |
| **Small** | 內部 RAM (DATA, 0x00~0x7F / 0xFF) | **`C51S.LIB`** |
| **Compact** | 外部 RAM 分頁 (PDATA, 256B) | **`C51C.LIB`** |
| **Large** | 外部 RAM (XDATA, 64KB) | **`C51L.LIB`** |

在我們的 W78E052D 專案中，因為採用 Small 記憶體模型，因此連結器會自動選用 `C51S.LIB`。

---

## 2. `STARTUP.OBJ` 與 `?C_STARTUP` 的歸屬問題

在設計 SBOM 產生器時，一個關鍵的細節是：**啟動碼（Startup Code）到底是來自使用者專案，還是來自 `C51S.LIB`？**

### 實測現象
- **情況 A（專案包含 `STARTUP.A51`）**：
  Keil 組譯器將 `STARTUP.A51` 組譯為 `STARTUP.OBJ`。在 `.m51` 報表中會出現：
  ```text
  INPUT MODULES INCLUDED:
    PROJECT\OBJECTS\STARTUP.OBJ (?C_STARTUP)
  ```
  這表示 `?C_STARTUP` 模組是由專案自身的原始碼提供的，屬於 `file` 組件。
- **情況 B（專案未包含 `STARTUP.A51`）**：
  若工程師未在專案中加入 `STARTUP.A51`，連結器會在缺少進入點時，從 `C51S.LIB` 裡拉出預設編譯好的 `?C_STARTUP` 模組：
  ```text
  INPUT MODULES INCLUDED:
    C:\...\C51\LIB\C51S.LIB (?C_STARTUP)
  ```

本專案在範例中選擇了**情況 A**（標準實務作法：將 `STARTUP.A51` 納入版控以便調整暫存器清零範圍），因此 SBOM 產生器必須精確判斷模組的來源檔案是專案 `.OBJ` 還是系統 `.LIB`。

---

## 3. 什麼語法會觸發 `C51S.LIB` 內部常式？

當專案已自帶 `STARTUP.OBJ` 時，如果 `main.c` 寫得非常精簡（例如只有無窮迴圈 `while(1);` 且無全域變數），`BL51` 甚至可能不需要從 `C51S.LIB` 載入任何模組。

但在真實嵌入式系統中，以下 C 語言語意會自然觸發執行期函式庫：

### 1. 全域變數初始化 ── 觸發 `?C_INIT`
8051 硬體開機時 RAM 中的資料是隨機的。當您在 C 語言中宣告：
```c
volatile unsigned int g_tick_counter = 1000;
```
編譯器會將初值 `1000` 存放在 CODE Flash 中，並在進入 `main()` 前由 `?C_INIT` 常式將該初值拷貝到 DATA RAM 變數位址。因此 `BL51` 會自動從 `C51S.LIB` 載入 `(?C_INIT)`。

### 2. 16 位元除法 / 取餘數 ── 觸發 `?C?UIDIV`
經典 8051 硬體指令集僅有 8 位元乘除法指令（`MUL AB`、`DIV AB`）。當程式碼執行 16 位元無號整數除法：
```c
computed_val = g_tick_counter / g_divider;
```
8051 無法靠單一指令完成，必須由軟體演算法多重迴圈計算。Keil 編譯器會發出對 `?C?UIDIV` 常式的呼叫，因此 `BL51` 會自動從 `C51S.LIB` 載入 `(?C?UIDIV)`。

### 3. 符號比較 ── 觸發 `?C?SLCMP`
處理有號整數或長整數比較時，同樣會自動由 `C51S.LIB` 提供輔助比較運算。

---

## 4. SBOM 產生的核心價值

透過解析 `.m51` 的 `INPUT MODULES INCLUDED` 區段：
- 我們不僅能證明最終韌體確實依賴了外部二進位庫 `C51S.LIB`。
- 更能具體列出究竟是哪些底層常式（`?C_INIT`、`?C?UIDIV`）被編譯進客戶的晶片之中，並計算 `C51S.LIB` 的 SHA-256 雜湊值。

這為標準 8051 韌體提供了前所未有的二進位等級可解釋性與供應鏈安全保障。
