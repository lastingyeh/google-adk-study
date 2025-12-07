# 範例政策文件

本目錄包含用於教學 37：企業合規與政策導航器 (Enterprise Compliance & Policy Navigator) 的範例政策文件。

## 概覽

這些文件作為 File Search 整合教學的範例，展示如何使用 Google 的 Gemini File Search API 上傳、索引和搜尋公司政策。

---

## 包含的文件

### 1. code_of_conduct.md (行為準則)

**來源**: Contributor Covenant 2.0
**授權**: Creative Commons Attribution 4.0 International (CC BY 4.0)
**連結**: https://www.contributor-covenant.org/

**描述**: 改編自廣泛採用的 Contributor Covenant 的專業行為準則文件。此政策建立了社群標準、被禁止的行為以及職場行為的執行程序。

**使用案例**: 展示 File Search 如何在組織內尋找並執行行為準則標準。

**關鍵章節**:
- 社群承諾與標準
- 可接受與不可接受行為的範例
- 執行責任與指導方針
- 範圍與歸屬

---

### 2. hr_handbook.md (人資手冊)

**來源**: 基於最佳實踐的原創範本
**授權**: Creative Commons Attribution 4.0 International (CC BY 4.0)
**描述**: 全面的 HR 員工手冊，涵蓋就業政策、福利、薪酬和職場行為。

**使用案例**: 展示 File Search 如何協助員工快速找到 HR 問題的答案（休假天數、福利、入職等）。

**關鍵章節**:
- 隨意僱傭 (At-will employment)
- 平等就業機會
- 工作時間與遠端工作
- 薪酬與薪資單
- 福利（健康保險、401k、人壽保險、殘疾保險）
- 有薪假（休假、事假、病假）
- 國定假日
- 職場行為與服裝儀容
- 反騷擾政策
- 溝通指導方針

**教學應用**:
- 查詢："我有幾天特休？"
- 查詢："我有什麼福利？"
- 查詢："遠端工作政策是什麼？"

---

### 3. it_security_policy.md (IT 安全政策)

**來源**: SANS Institute Security Policy Templates (改編)
**授權**: 公眾使用需註明出處
**原始來源**: https://www.sans.org/information-security-policy/

**描述**: 涵蓋資訊分類、存取控制、資料保護、端點安全和事件回應程序的 IT 安全政策。

**使用案例**: 展示 File Search 如何協助員工了解安全需求與 IT 合規程序。

**關鍵章節**:
- 資訊分類
- 存取控制與驗證
- 密碼政策
- 資料保護與加密
- 備份與復原
- 端點安全
- 網路與無線安全
- 軟體與修補程式管理
- 漏洞管理
- 第三方與供應商管理
- 事件回應程序
- 可接受使用政策
- 安全意識培訓
- 遠端工作安全

**教學應用**:
- 查詢："密碼要求是什麼？"
- 查詢："我要如何報告安全事件？"
- 查詢："撿到 USB 隨身碟該怎麼辦？"
- 查詢："我可以用個人手機處理公務嗎？"

---

### 4. remote_work_policy.md (遠端工作政策)

**來源**: 基於最佳實踐的原創範本
**授權**: Creative Commons Attribution 4.0 International (CC BY 4.0)
**描述**: 全面的遠端工作政策，涵蓋資格、核准流程、安全需求和績效預期。

**使用案例**: 展示 File Search 如何回答員工關於遠端工作安排與合規需求的問題。

**關鍵章節**:
- 遠端工作資格與類型
- 申請與核准流程
- 核心時間與可用性
- 工作空間與設備需求
- 安全與保密
- 溝通與協作
- 績效管理
- 辦公室存取
- 差旅與搬遷指導方針
- 休假政策
- 設備歸還程序
- 常見問題 (FAQ)

**教學應用**:
- 查詢："我有資格遠端工作嗎？"
- 查詢："遠端工作的核心時間是什麼？"
- 查詢："在家工作需要使用 VPN 嗎？"
- 查詢："我可以去其他國家邊旅遊邊工作嗎？"

---

## 在教學 37 中使用這些文件

### 步驟 1：上傳文件到 File Search Store

```python
from google import genai

client = genai.Client(api_key='your-api-key')

# 建立 store
hr_store = client.file_search_stores.create(
    config={'display_name': 'hr-policies'}
)

# 上傳範例政策
policies = [
    'code_of_conduct.md',
    'hr_handbook.md',
    'it_security_policy.md',
    'remote_work_policy.md'
]

for policy in policies:
    with open(f'sample_policies/{policy}', 'rb') as f:
        operation = client.file_search_stores.upload_to_file_search_store(
            file=f,
            file_search_store_name=hr_store.name,
            config={'display_name': policy}
        )
```

### 步驟 2：測試查詢

上傳後，測試這些查詢：

**HR 相關**:
- "我有幾天特休？"
- "我的僱傭包含哪些福利？"
- "何時放國定假日？"
- "服裝儀容規定是什麼？"

**遠端工作**:
- "我可以居家辦公嗎？"
- "核心時間是什麼？"
- "遠端工作需要 VPN 嗎？"
- "我要如何申請遠端工作？"

**安全性**:
- "密碼要求是什麼？"
- "我要如何報告安全事件？"
- "我應該加密什麼？"
- "我可以用公共 WiFi 工作嗎？"

**行為準則**:
- "什麼是騷擾？"
- "我要如何報告不當行為？"
- "執行程序是什麼？"

---

## File Search 組織的 Metadata

上傳這些文件時，請考慮使用以下 metadata：

```python
# Metadata 範例
metadata = {
    'department': 'string',        # HR, IT, All
    'policy_type': 'string',       # handbook, procedure, code_of_conduct
    'effective_date': 'date',      # YYYY-MM-DD
    'jurisdiction': 'string',      # US
    'sensitivity': 'string',       # internal, confidential
    'version': 'numeric',          # 1, 2, 3
    'owner': 'string',             # dept@company.com
    'review_cycle': 'numeric'      # Months between reviews
}

# HR 手冊範例
hr_metadata = [
    {'key': 'department', 'string_value': 'HR'},
    {'key': 'policy_type', 'string_value': 'handbook'},
    {'key': 'effective_date', 'string_value': '2025-11-08'},
    {'key': 'jurisdiction', 'string_value': 'US'},
    {'key': 'sensitivity', 'string_value': 'internal'},
    {'key': 'version', 'numeric_value': 1},
    {'key': 'owner', 'string_value': 'hr@company.com'},
    {'key': 'review_cycle', 'numeric_value': 12}
]
```

---

## 為您的組織自訂

這些文件僅作為範本和範例提供。若要將其調整為適用於您的組織：

1. **更換公司名稱**: 將所有出現的 "our company" 替換為您的實際公司名稱
2. **更新聯絡資訊**: 替換佔位符電子郵件和電話號碼
3. **自訂政策**: 修改條款以符合您的實際政策
4. **新增公司特定章節**: 包含部門程序、代碼或需求
5. **更新生效日期**: 設定適合您部署的生效日期
6. **加入您的 Logo**: 如有需要，包含公司品牌標識
7. **法律審查**: 在部署前請法律顧問審查

---

## 授權與歸屬

### Creative Commons Attribution 4.0 (CC BY 4.0)

根據 CC BY 4.0 授權的檔案可以：
- 用於商業用途
- 修改和改編
- 分發給他人
- 用於任何目的

**要求**:
- 給予原創者適當的歸屬
- 包含授權副本
- 指出是否進行了更改

### 歸屬範例

HR 手冊：
```
Original template based on best practices.
Licensed under Creative Commons Attribution 4.0 International.
https://creativecommons.org/licenses/by/4.0/
```

行為準則：
```
Adapted from Contributor Covenant 2.0
https://www.contributor-covenant.org/
Licensed under Creative Commons Attribution 4.0 International.
```

IT 安全政策：
```
Based on SANS Institute Security Policy Templates
https://www.sans.org/information-security-policy/
Adapted for tutorial purposes.
```

---

## 資源與參考資料

### Contributor Covenant
- **網站**: https://www.contributor-covenant.org/
- **GitHub**: https://github.com/ethicalsource/contributor_covenant
- **授權**: Creative Commons Attribution 4.0

### SANS Institute 安全政策
- **網站**: https://www.sans.org/information-security-policy/
- **描述**: 免費安全政策範本
- **範本**: 36+ 個隨取即用的安全政策

### Creative Commons 授權
- **網站**: https://creativecommons.org/
- **CC BY 4.0**: https://creativecommons.org/licenses/by/4.0/

### 最佳實踐參考資料
- 員工手冊：SHRM, NFIB, SBA 資源
- 遠端工作：GitLab, Automattic, Basecamp 公開資源
- 安全性：NIST, CIS, ISO 27001

---

## 法律免責聲明

這些範例文件僅供教育和教學目的使用。
它們**不是**法律建議，**不應**在生產環境中直接使用。

**在您的組織中部署任何政策之前**：

1. ✅ 請法律顧問審查所有政策
2. ✅ 確保符合適用法律和法規
3. ✅ 自訂以反映您的實際組織慣例
4. ✅ 考慮州和地方法律就業要求
5. ✅ 獲得管理層和董事會批准
6. ✅ 清楚向所有員工傳達變更
7. ✅ 維護所有政策更新的文件記錄

這些文件的建立者和提供者不對使用這些文件產生的任何法律、財務或商業後果負責。

---

## 教學進度

這些範例文件在教學 37 中全程使用：

- **第 2 部分**: 上傳文件到 File Search Store
- **第 3 部分**: 搜尋並從政策中擷取引用
- **第 4 部分**: 多代理人系統展示跨文件查詢
- **第 5 部分**: 進階功能展示政策比較和衝突檢測
- **第 6 部分**: 使用真實政策文件進行生產部署

---

## 檔案大小與詳細資訊

| 文件 | 大小 | 章節 | 字數 | 格式 |
|----------|------|----------|-------|--------|
| code_of_conduct.md | 5.1 KB | 7 | ~1,200 | Markdown |
| hr_handbook.md | 8.3 KB | 10 | ~1,800 | Markdown |
| it_security_policy.md | 9.5 KB | 13 | ~2,200 | Markdown |
| remote_work_policy.md | 13 KB | 15 | ~3,100 | Markdown |
| **總計** | **36 KB** | **45** | **~8,300** | **Markdown** |

---

## 轉換為 PDF

若要將這些 markdown 文件轉換為 PDF 以用於生產環境：

```bash
# 使用 pandoc (請先安裝：brew install pandoc)
pandoc code_of_conduct.md -o code_of_conduct.pdf
pandoc hr_handbook.md -o hr_handbook.pdf
pandoc it_security_policy.md -o it_security_policy.pdf
pandoc remote_work_policy.md -o remote_work_policy.pdf
```

然後將 PDF 檔案上傳到 File Search 以供生產使用。

---

## 問題或貢獻

關於這些範例文件的問題或對教學的貢獻：

- GitHub Issues: https://github.com/raphaelmansuy/adk_training/issues
- 教學 Repo: https://github.com/raphaelmansuy/adk_training
- 主要專案: Google ADK Training

---

**建立時間**: 2025 年 11 月 8 日
**最後更新**: 2025 年 11 月 8 日
**狀態**: 已準備好用於教學 37 實作

範例文件是 **Google ADK Training Project** 的一部分：
https://github.com/raphaelmansuy/adk_training

### 重點摘要

- **核心概念**：教學 37 (File Search) 的範例文件集。
- **關鍵文件**：行為準則 (Code of Conduct)、HR 手冊 (HR Handbook)、IT 安全政策 (IT Security Policy)、遠端工作政策 (Remote Work Policy)。
- **行動項目**：在教學過程中將這些文件上傳到 File Search Store 進行測試與驗證。
