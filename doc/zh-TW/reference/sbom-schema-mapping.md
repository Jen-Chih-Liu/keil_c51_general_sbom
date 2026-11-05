# 技術參考：CycloneDX 1.5 與 SPDX 2.3 欄位對應規格

本文件定義 Keil C51 嵌入式韌體建置元素如何映射至國際標準 SBOM 規格（CycloneDX v1.5 與 SPDX v2.3）。

---

## 1. 組件類型映射架構表

| 實體組件 | 說明 | CycloneDX 1.5 對應 | SPDX 2.3 對應 |
| :--- | :--- | :--- | :--- |
| **最終韌體 (`.hex`)** | 燒錄至 MCU 的 Intel HEX 映像 | `metadata.component` (type: `application`) | `packages` (SPDXID: `SPDXRef-Package-FirmwareHex`) |
| **微控制器 (`W78E052D`)** | 目標 8051 單晶片硬體 | `components[]` (type: `device`) | `packages` (SPDXID: `SPDXRef-Package-MCU`) |
| **隱性函式庫 (`C51S.LIB`)** | Keil BL51 自動連結之執行期函式庫 | `components[]` (type: `library`) | `packages` (SPDXID: `SPDXRef-Package-Lib-0`) |
| **標準標頭檔 (`REG52.H`)** | 專案引用的標準 8051 暫存器標頭 | `components[]` (type: `file`) | `files` (SPDXID: `SPDXRef-File-Header-0`) |
| **原始碼 (`main.c`, `STARTUP.A51`)** | 韌體應用程式與啟動程式碼 | `components[]` (type: `file`) | `files` (SPDXID: `SPDXRef-File-Source-0`) |
| **建置工具 (`C51.exe` 等)** | 編譯器、組譯器、連結器 | `metadata.tools.components[]` (type: `application`) | `creationInfo.creators[]` |

---

## 2. CycloneDX v1.5 欄位細節

### A. 根韌體映像 (`metadata.component`)
```json
{
  "type": "application",
  "bom-ref": "pkg:generic/firmware/w78_std_8051@1.0.0",
  "name": "w78_std_8051",
  "version": "1.0.0",
  "description": "Intel HEX Firmware for W78E052D (Winbond / Nuvoton W78 series)",
  "hashes": [
    {"alg": "SHA256", "content": "9c9e09be28db..."},
    {"alg": "MD5", "content": "9b1248a..."}
  ]
}
```

### B. 隱性執行期函式庫 (`C51S.LIB`)
包含實際載入之內部常式模組：
```json
{
  "type": "library",
  "bom-ref": "pkg:library/keil/c51s.lib@aaf86482",
  "name": "C51S.LIB",
  "version": "V9.61",
  "description": "Keil C51 SMALL Model Runtime Library (implicitly linked by BL51)",
  "hashes": [
    {"alg": "SHA256", "content": "aaf864826f6..."}
  ],
  "properties": [
    {"name": "file:path", "value": "C:\\...\\C51\\LIB\\C51S.LIB"},
    {"name": "keil:linked_module", "value": "?C_INIT"},
    {"name": "keil:linked_module", "value": "?C?UIDIV"},
    {"name": "keil:linked_module", "value": "?C?SLCMP"}
  ]
}
```

### C. 建置工具雙軌版本 (`metadata.tools`)
同時保留套件總版本（Suite Release）與執行檔真實版本（Executable Version）：
```json
{
  "tools": {
    "components": [
      {
        "type": "application",
        "name": "C51.exe",
        "version": "V9.60.7.0",
        "hashes": [{"alg": "SHA256", "content": "e54096a46086..."}]
      },
      {
        "type": "application",
        "name": "BL51.exe",
        "version": "V6.22.4.0",
        "hashes": [{"alg": "SHA256", "content": "c59a29594f72..."}]
      }
    ]
  }
}
```

---

## 3. SPDX v2.3 欄位細節

### A. 相依性關係 (`relationships`)
- 韌體相依於硬體 MCU：
  ```json
  {"spdxElementId": "SPDXRef-Package-FirmwareHex", "relationshipType": "DEPENDS_ON", "relatedSpdxElement": "SPDXRef-Package-MCU"}
  ```
- 韌體相依於執行期函式庫：
  ```json
  {"spdxElementId": "SPDXRef-Package-FirmwareHex", "relationshipType": "DEPENDS_ON", "relatedSpdxElement": "SPDXRef-Package-Lib-0"}
  ```
- 韌體包含原始碼與標頭檔：
  ```json
  {"spdxElementId": "SPDXRef-Package-FirmwareHex", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-Header-0"}
  ```

---

## 4. 加密雜湊演算法與產出對象規格 (Cryptographic Hashes)

本專案之 SBOM 產生器遵循國際標準（NIST FIPS 180-4、NTIA、CycloneDX 1.5 及 SPDX 2.3），為專案中所有實體二進位檔、原始碼與工具鏈產出高強度加密雜湊。

### A. 產出的雜湊演算法清單

| 演算法 | 輸出格式 / 長度 | 適用規範 | 用途說明 |
| :--- | :--- | :--- | :--- |
| **SHA-256** | 64 位元十六進位字串 | NIST FIPS 180-4 / NTIA / CRA | **主要合規雜湊**。用於二進位防偽、防竄改與國際弱點資料庫（NVD / CVE）比對。 |
| **SHA-1** | 40 位元十六進位字串 | FIPS 180-1 | 輔助雜湊。用於向後相容傳統 SCA 工具與 Git Commit 比對。 |
| **MD5** | 32 位元十六進位字串 | RFC 1321 | 傳統完整性校驗碼。用於快速比對 Keil 編譯產物。 |

### B. 雜湊計算之實體對象清單

SBOM 產生器對以下 5 大類對象逐一計算並嵌入 SHA-256 / SHA-1 / MD5 雜湊：

1. **最終韌體產物 (Firmware Deliverable)**：
   - `project/Objects/w78_std_8051.hex`（Intel HEX 二進位燒錄檔）
2. **隱性執行期函式庫 (Implicit Runtime Library)**：
   - `C51\LIB\C51S.LIB`（Keil 小型記憶體模型閉源標準庫）
3. **標準 8051 標頭檔 (Standard Headers)**：
   - `C51\INC\REG52.H`（標準 8052 暫存器定義）
   - `C51\INC\INTRINS.H`（內建巨集常式標頭檔）
4. **專案原始碼與啟動碼 (Source & Startup Files)**：
   - `project/src/main.c`（韌體主程式）
   - `project/src/STARTUP.A51`（標準 8051 組合語言啟動碼）
5. **建置工具鏈可執行檔 (Build Toolchain Binaries)**：
   - `C51\BIN\C51.exe`（C51 編譯器）
   - `C51\BIN\A51.exe`（A51 組譯器）
   - `C51\BIN\BL51.exe`（BL51 連結器）
   - `C51\BIN\OH51.exe`（OH51 轉 HEX 程式）

### C. 雜湊在不同 SBOM 產物中的呈現方式

- **在 CycloneDX 1.5 JSON (`sbom.cdx.json`) 中**：
  存放於各組件的 `hashes[]` 陣列，欄位為 `alg: "SHA256"`（或 `"SHA1"`, `"MD5"`）與 `content: "<hash_string>"`。
- **在 SPDX 2.3 JSON (`sbom.spdx.json`) 中**：
  存放於各 Package 與 File 的 `checksums[]` 陣列，欄位為 `algorithm: "SHA256"` 與 `checksumValue: "<hash_string>"`。
- **在 Markdown 報告 (`SBOM-REPORT.md`) 中**：
  在各章節表格以 `SHA-256 Hash` 欄位獨立列出完整的 64 碼雜湊值。
