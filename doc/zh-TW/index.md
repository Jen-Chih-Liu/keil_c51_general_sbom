# Keil C51 標準 8051 (W78 系列) 專案與 SBOM 文件庫

歡迎查閱本專案的技術文件庫。本文件庫嚴格遵循 **Diátaxis** 文件架構體系，依據使用者的學習目標與工作情境劃分為四個核心維度：

```
                    實踐 (Practical / Action)
                               │
            Tutorials (新手教學) │ How-To Guides (操作指南)
         學習導向：帶領新手完成首次體驗 │ 工作導向：解決具體的實務問題
                               │
── 學習 (Learning) ────────────┼──────────── 工作 (Working) ──
                               │
         Explanation (概念解說) │ Reference (技術參考)
         理解導向：剖析架構與設計原理   │ 資訊導向：精準的命令、格式與欄位規格
                               │
                    理論 (Theoretical / Knowledge)
```

---

## 1. 學習導向：實踐篇 (Tutorials)
適合第一次接觸本專案的使用者，手把手帶您建立韌體並產出第一份 SBOM：
- [新手入門教學：從零建置 W78 專案並產出第一份 SBOM](tutorials/getting-started.md)

---

## 2. 工作導向：實踐篇 (How-To Guides)
提供針對具體任務的操作步驟與處方：
- [操作指南：開發環境與必要程式安裝設定 (Keil C51 & Python)](how-to-guides/environment-setup.md)
- [操作指南：在 Keil µVision GUI 中設定按 F7 自動產生 SBOM](how-to-guides/keil-gui-integration.md)
- [操作指南：在 Windows PowerShell / CI/CD 執行無頭自動化建置](how-to-guides/cli-headless-build.md)
- [操作指南：執行 SBOM 產生器的自動化單元測試](how-to-guides/automated-testing.md)
- [操作指南：如何檢驗與驗證 SBOM 合規性 (NTIA & Schema)](how-to-guides/verify-sbom-compliance.md)

---

## 3. 工作導向：理論篇 (Reference)
提供技術規格、參數手冊與欄位對應標準：
- [技術參考：命令列工具參數與指令清單](reference/cli-reference.md)
- [技術參考：CycloneDX 1.5 與 SPDX 2.3 欄位對應規格](reference/sbom-schema-mapping.md)
- [技術參考：Keil C51 編譯產物結構與格式定義](reference/build-artifacts.md)

---

## 4. 學習導向：理論篇 (Explanation)
深入探討嵌入式 SBOM 的背景原理、設計決策與架構權衡：
- [概念解說：如何判斷軟體物料清單 (SBOM) 是否合規？(NTIA / CRA 標準)](explanation/sbom-compliance-criteria.md)
- [概念解說：為何標準 8051 專案必須採用編譯產物逆向 SBOM？](explanation/why-build-artifact-sbom.md)
- [概念解說：Keil C51 隱性執行期函式庫 (C51S.LIB) 的連結原理](explanation/implicit-c51-runtime-linking.md)
