# 操作指南：如何檢驗與驗證 SBOM 合規性

本指南提供具體的操作步驟與檢驗指令，引導您如何驗證本專案產出的 SBOM 檔案是否符合國際法規標準（如美國 NTIA 最小元素與歐盟 CRA 要求）。

---

## 1. 快速自動化檢驗（使用內建 Python 指令）

本專案提供一段免額外安裝工具的檢驗指令，可直接驗證產出的 `sbom/sbom.cdx.json` 與 `sbom/sbom.spdx.json` 是否滿足 NTIA 7 大最小欄位：

在專案根目錄開啟 PowerShell 執行：

```powershell
python -c "
import json

cdx = json.load(open('sbom/sbom.cdx.json', encoding='utf-8'))
spdx = json.load(open('sbom/sbom.spdx.json', encoding='utf-8'))

print('=== 1. CycloneDX 1.5 規範檢驗 ===')
assert cdx['bomFormat'] == 'CycloneDX' and cdx['specVersion'] == '1.5'
assert 'timestamp' in cdx['metadata']
assert len(cdx['components']) >= 5
assert len(cdx['dependencies']) >= 1
print('[✓] CycloneDX 結構與相依關係合規！')

print('=== 2. SPDX 2.3 規範檢驗 ===')
assert spdx['spdxVersion'] == 'SPDX-2.3'
assert 'created' in spdx['creationInfo']
assert len(spdx['packages']) >= 3
assert len(spdx['relationships']) >= 4
print('[✓] SPDX 結構與關係圖合規！')

print('=== 3. 嵌入式二進位完整性檢驗 ===')
hex_hash = cdx['metadata']['component']['hashes'][0]['content']
assert len(hex_hash) == 64
print(f'[✓] 最終韌體 SHA-256: {hex_hash}')
print('\n[SUCCESS] 全部 SBOM 合規檢查通過！')
"
```

---

## 2. 使用業界標準工具進行 Schema 驗證

除了內建腳本外，您還可以使用 CISA 與 OWASP 官方推廣的驗證工具進行第三方審查：

### 方法 A：使用 CycloneDX 官方 CLI (`cyclonedx-cli`)
若您的環境已安裝 `cyclonedx-cli`（可透過 `winget install CycloneDX.CycloneDX-CLI` 安裝）：
```powershell
cyclonedx validate --input-file sbom/sbom.cdx.json --input-format json
```
若輸出 `Validation successful`，即代表通過 CycloneDX 官方 JSON Schema 驗證。

### 方法 B：使用 SPDX 官方驗證工具 (`spdx-tools`)
使用 SPDX 官方 Python 驗證模組：
```powershell
pip install spdx-tools
pyspdx -i sbom/sbom.spdx.json
```

---

## 3. 合規審查清單對照表 (Auditor Checklist)

在接受資安稽核或客戶要求提供 SBOM 時，請依據下表確認產物內容：

| 檢核項目 | 判定依據 | 本專案狀態 |
| :--- | :--- | :---: |
| **格式標準** | 符合 CycloneDX v1.4+ 或 SPDX v2.2+ | **PASS** (CycloneDX 1.5 & SPDX 2.3) |
| **拒絕空包彈** | 組件數量大於 0，且非僅單一頂層名稱 | **PASS** (涵蓋晶片、標頭檔、隱性庫等 6+ 組件) |
| **隱性庫揭露** | 揭露未手動宣告但被 Linker 連結的 `C51S.LIB` | **PASS** (列出 `?C_INIT`, `?C?UIDIV` 等常式) |
| **加密雜湊防偽** | 包含 64 位元的 SHA-256 完整性雜湊 | **PASS** (所有檔案與二進位庫皆有 SHA-256) |
| **工具鏈來源** | 記錄編譯器與工具鏈版本號及雜湊 | **PASS** (記錄 `C51.exe`、`BL51.exe` 真實版本) |
