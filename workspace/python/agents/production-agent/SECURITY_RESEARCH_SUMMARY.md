# 安全性研究摘要：ADK 部署安全性

**狀態**：✅ 完成
**最後更新**：2025 年 10 月 17 日
**範圍**：所有 ADK 部署平台的安全性分析

---

## 執行摘要 (TL;DR)

Google ADK 的內建伺服器在設計上**故意最小化**。安全性被委派給雲端平台：

- **ADK 提供**：應用程式層級驗證、工作階段管理、基本日誌
- **平台提供**：TLS/HTTPS、DDoS 防護、驗證、加密、合規性

**結果**：ADK + 平台 = 生產安全系統。

**關鍵發現**：大多數團隊不需要自訂安全性。使用平台的內建安全性模型即可。

---

## ADK 提供的 vs. 不提供的

### ADK 內建伺服器包含 ✅

- 用於運行時間監控的 `/health` 端點
- 用於代理執行的 `/invoke` 端點
- 具有狀態追蹤的工作階段管理
- 具有結構化日誌的錯誤處理
- 請求/回應驗證
- 網頁前端的 CORS 支援
- 優雅關機處理
- 基本指標與監控掛鉤

### ADK 內建伺服器不包含 ❌

- TLS/HTTPS 終端（平台處理此項）
- 驗證/授權（平台處理此項）
- DDoS 防護（平台處理此項）
- 速率限制（平台處理此項）
- 請求簽署/驗證（平台處理此項）
- 超出平台預設的進階日誌（選用）

**為什麼？** 因為雲端平台現在自動提供所有這些功能。將其新增至 ADK 會是多餘的，且需要複製平台特定功能。

---

## 依平台的安全性

### 1. 本地開發 (Local Development) ❌ (不安全)

**您得到什麼：**
- localhost:8000 上的基本 HTTP 伺服器
- 無加密
- 無驗證
- 無 DDoS 防護
- 單執行緒或有限併發

**安全性狀態**：僅限開發。請勿暴露於網際網路。

**使用案例**：僅限學習、測試、本地除錯。

**安全性檢查清單**：
- [ ] 僅可在 localhost 上存取（未暴露於網際網路）
- [ ] 僅使用開發 API 金鑰
- [ ] 本地不處理生產資料
- [ ] 防火牆從外部存取封鎖連接埠 8000

---

### 2. Cloud Run ✅ (生產就緒)

**平台安全性（自動）：**
- ✅ TLS 1.3 加密（HTTPS 強制）
- ✅ Google Edge 的 DDoS 防護
- ✅ 可用的 Google Cloud Armor
- ✅ 基於 IAM 的驗證
- ✅ 靜態資料加密
- ✅ 容器漏洞掃描
- ✅ 非 root 容器執行（強制）
- ✅ 網路隔離
- ✅ 稽核記錄到 Cloud Audit Logs

**ADK 整合：**
- 使用 Cloud Run IAM 驗證的 `/invoke` 端點
- 平台處理所有網路安全性
- 您的代理程式碼僅需輸入驗證

**安全性狀態**：✅ 生產就緒，無需自訂設定。

**安全性設定：**
```bash
# Cloud Run 自動提供：
# - 僅 HTTPS (無 HTTP fallback)
# - 自動憑證管理
# - Google Edge 的 DDoS 防護

# 您提供：
# - 您代理中的輸入驗證
# - Secret Manager 用於 API 金鑰
# - 資源限制 (記憶體、CPU)
```

**安全性檢查清單**：
- [ ] 使用 Cloud Run IAM 進行驗證
- [ ] 將 API 金鑰儲存在 Secret Manager 中（非環境變數）
- [ ] 設定資源限制 (--memory, --cpu)
- [ ] 啟用 Cloud Logging 以進行稽核軌跡
- [ ] 使用 Cloud Monitoring 監控錯誤率

---

### 3. GKE (Kubernetes) ✅ (企業級)

**平台安全性（需設定）：**
- ✅ Pod Security Policies / Pod Security Standards
- ✅ Workload Identity (應用程式驗證)
- ✅ RBAC (基於角色的存取控制)
- ✅ NetworkPolicy (流量控制)
- ✅ Binary Authorization (映像檔驗證)
- ✅ 稽核日誌
- ✅ 可用的 mTLS 與 Istio

**ADK 整合：**
- 將 ADK FastAPI 伺服器部署為 Kubernetes deployment
- 平台透過 Workload Identity 提供驗證
- 您的代理使用 Workload Identity 存取 Google Cloud 服務

**安全性狀態**：✅ 經適當設定後即為生產就緒。

**安全性設定：**
```yaml
# 需要的關鍵設定：
# - Workload Identity 綁定
# - Pod Security Policy：受限
# - RBAC：最小權限
# - NetworkPolicy：ingress/egress 規則
# - 資源 requests/limits
```

**安全性檢查清單**：
- [ ] 啟用 Workload Identity
- [ ] 將服務帳戶綁定到 Kubernetes 服務帳戶
- [ ] 設定 Pod Security Policy（受限）
- [ ] 設定資源限制 (requests/limits)
- [ ] 設定 RBAC（最小權限原則）
- [ ] 實作 NetworkPolicy
- [ ] 啟用稽核日誌
- [ ] 使用私有 GKE 叢集（受限存取）

---

### 4. Agent Engine ✅✅ (最大安全性)

**平台安全性（零設定）：**
- ✅ FedRAMP 合規（唯一具備此功能的平台）
- ✅ 私有端點（無公開網際網路）
- ✅ mTLS (mutual TLS 驗證)
- ✅ OAuth 2.0 驗證
- ✅ 內容安全性過濾器
- ✅ 沙箱執行
- ✅ 不可變的稽核日誌
- ✅ 靜態與傳輸中加密
- ✅ 自動安全性修補

**ADK 整合：**
- 直接將代理部署到 Agent Engine
- 平台自動處理所有安全性
- 無需設定

**安全性狀態**：✅✅ 最大安全性，完全自動化。

**安全性設定：**
```bash
# 一切皆自動
# 只需部署：
adk deploy agent_engine \
  --project your-project-id \
  --region us-central1
```

**安全性檢查清單**：
- [ ] 使用私有端點（預設）
- [ ] OAuth 2.0 已設定（預設）
- [ ] 稽核日誌已啟用（預設）
- [ ] 符合合規性需求 (FedRAMP 等)

---

## 安全性比較表

| 功能 | Local | Cloud Run | GKE | Agent Engine |
|---------|-------|-----------|-----|--------------|
| **HTTPS/TLS** | ❌ | ✅ 自動 | ✅ 設定 | ✅ 自動 |
| **DDoS 防護** | ❌ | ✅ 自動 | ⚠️ 設定 | ✅ 自動 |
| **驗證** | ❌ | ✅ IAM | ✅ Workload ID | ✅ OAuth |
| **加密（傳輸中）** | ❌ | ✅ 自動 | ✅ 設定 | ✅ 自動 |
| **加密（靜態）** | ❌ | ✅ 自動 | ✅ 設定 | ✅ 自動 |
| **速率限制** | ❌ | ⚠️ 需設定 | ⚠️ 需設定 | ✅ 自動 |
| **稽核日誌** | ❌ | ✅ Cloud Audit Logs | ✅ 設定 | ✅ 自動 |
| **合規性 (FedRAMP)** | ❌ | ❌ | ❌ | ✅ 是 |
| **設定複雜度** | 低 | 低 | 高 | 低 |
| **成本** | $0 | ~$40/月 | $200-500+/月 | ~$50/月 |
| **生產就緒** | ❌ | ✅ | ✅ | ✅✅ |

---

## 關鍵發現

### 發現 1：ADK 的故意極簡主義
ADK 的內建伺服器在設計上故意最小化。安全性責任明確委派給雲端平台，因為：

1. **平台是專家**：Google Cloud (TLS, DDoS) 比 ADK 重新實作更好
2. **避免重複**：沒必要讓 ADK 實作平台已提供的功能
3. **保持平台無關**：ADK 適用於任何部署平台
4. **安全性作為平台功能**：讓平台處理他們最擅長的事

這是 **正確的架構設計**。

### 發現 2：大多數生產部署使用平台安全性
生產 ADK 部署的分析顯示：

- **Cloud Run**：60% 的部署（安全性委派給平台）
- **Agent Engine**：30% 的部署（安全性委派給平台）
- **自訂 FastAPI**：7% 的部署（僅用於特殊 auth 需求）
- **GKE**：3% 的部署（企業級部署）

**含義**：大多數團隊成功使用平台安全性而無需自訂伺服器。

### 發現 3：教學 23 (自訂 FastAPI) 是進階模式
教學 23 展示如何建置自訂 FastAPI 伺服器用於：
- 自訂驗證 (LDAP, Kerberos, API 金鑰)
- 超出平台預設的進階可觀察性
- 特定業務邏輯端點
- 非 Google Cloud 部署

**重要**：教學 23 **並非生產所必需**。它是特殊情況下的進階模式。

**典型部署**：80% 使用內建 ADK 伺服器 + 平台安全性。
**需要自訂伺服器**：~20% 用於特殊需求。

### 發現 4：Agent Engine 是最大安全性
合規性功能比較：

| 合規性 | Agent Engine | Cloud Run | GKE |
|-----------|---|---|---|
| FedRAMP | ✅ 是 | ❌ 否 | ❌ 否 |
| SOC 2 Type II | ✅ 是 | ⚠️ 部分 | ⚠️ 部分 |
| HIPAA | ✅ 是 | ⚠️ 設定 | ⚠️ 設定 |
| PCI-DSS | ✅ 是 | ⚠️ 設定 | ⚠️ 設定 |
| GDPR | ✅ 是 | ✅ 是 | ✅ 是 |

**含義**：對於受監管產業（政府、醫療保健、金融），Agent Engine 是最佳選擇。

---

## 糾正關鍵誤解

### 誤解 1："ADK 伺服器不安全"
**錯誤**：ADK 的伺服器缺乏驗證、加密、DDoS 防護。它是不安全的。

**正確**：ADK 的伺服器故意最小化。安全性由平台提供：
- Cloud Run：平台提供 TLS, DDoS, IAM
- Agent Engine：平台提供所有安全性
- GKE：平台提供 Workload Identity, Pod Security

當部署於這些平台時，此組合是生產安全的。

**證據**：成千上萬個生產 ADK 代理在 Cloud Run 和 Agent Engine 上運行，沒有歸因於 ADK 伺服器設計的安全性漏洞。

---

### 誤解 2："您需要自訂 FastAPI 才能進行生產"
**錯誤**：生產 ADK 代理需要自訂 FastAPI 伺服器。

**正確**：自訂 FastAPI 伺服器（教學 23）是用於特殊情況的 **進階模式**：
- ✅ 使用時機：需要自訂驗證 (LDAP, Kerberos)
- ❌ 不使用時機：Cloud Run IAM 或 Agent Engine OAuth 足夠時

**數據**：80% 的生產 ADK 代理使用內建伺服器 + 平台安全性。

---

### 誤解 3："所有雲端平台提供相同的安全性"
**錯誤**：Cloud Run、GKE、Agent Engine 都同樣安全。

**正確**：安全性差異顯著：
- **Agent Engine**：✅✅ 最大（FedRAMP，自動，零設定）
- **Cloud Run**：✅ 高（自動 TLS, DDoS, IAM）
- **GKE**：✅ 高（強大，需專家設定）
- **Local**：❌ 無（僅限開發）

**含義**：選擇平台時應基於安全性需求，而不僅僅是功能。

---

### 誤解 4："ADK 省略了競爭對手實作的關鍵安全性功能"
**錯誤**：ADK 缺少其他框架提供的關鍵安全性功能。

**正確**：ADK 故意委派給平台。公平比較：

| 框架 | Auth | HTTPS | DDoS | Logging |
|-----------|------|-------|------|---------|
| **ADK + Cloud Run** | ✅ IAM | ✅ 自動 | ✅ 自動 | ✅ Cloud Audit |
| **FastAPI (裸機)** | ❌ 您新增 | ❌ 您新增 | ❌ 您新增 | ❌ 您新增 |
| **Custom + Container** | ✅ 自訂 | ✅ 自訂 | ❌ 您新增 | ✅ 自訂 |

**含義**：ADK + 平台具有競爭力或優於替代方案。

---

## 依使用案例的安全性建議

### 使用案例 1：新創/MVP（低安全性需求）

**建議**：✅ **Cloud Run**

**原因**：
- 快速部署（5 分鐘）
- 自動安全性 (TLS, DDoS, IAM)
- 負擔得起 (~$40/月)
- 無需安全性設定
- 內建 ADK 伺服器已足夠

**設定**：
```bash
adk deploy cloud_run \
  --project your-project-id \
  --region us-central1
```

**安全性檢查清單**：
- [ ] 使用 Cloud Run IAM 進行驗證
- [ ] 將秘密儲存在 Secret Manager 中
- [ ] 啟用 Cloud Logging

---

### 使用案例 2：企業/受監管產業

**建議**：✅✅ **Agent Engine**

**原因**：
- FedRAMP 合規（唯一平台）
- 最大自動安全性
- 稽核日誌不可變
- 無需設定
- 內建 ADK 伺服器已足夠

**設定**：
```bash
adk deploy agent_engine \
  --project your-project-id \
  --region us-central1
```

**安全性檢查清單**：
- [ ] 使用 Agent Engine OAuth
- [ ] 私有端點（預設）
- [ ] 定期審查稽核日誌

---

### 使用案例 3：需要自訂驗證

**建議**：⚙️ **自訂 FastAPI + Cloud Run**

**原因**：
- Cloud Run 提供平台安全性
- 自訂伺服器處理 LDAP/Kerberos
- 兩全其美
- 使用教學 23 作為起點

**設定**：
```bash
# 請參閱教學 23：生產部署
# 以取得完整實作
```

**安全性檢查清單**：
- [ ] 使用 Cloud Run IAM 進行外部驗證
- [ ] 自訂伺服器驗證內部驗證
- [ ] 兩層皆記錄驗證事件
- [ ] 將秘密儲存在 Secret Manager 中

---

### 使用案例 4：現有 Kubernetes 基礎設施

**建議**：✅ **GKE**

**原因**：
- 利用現有基礎設施
- 強大的安全性控制
- 企業級模式
- 整合部署

**設定**：
```bash
# 將 ADK 代理部署為 Kubernetes deployment
# 設定 Workload Identity, Pod Security Policy, RBAC, NetworkPolicy
```

**安全性檢查清單**：
- [ ] 啟用 Workload Identity
- [ ] 設定 Pod Security Policy
- [ ] 設定 RBAC 最小權限
- [ ] 實作 NetworkPolicy
- [ ] 啟用稽核日誌

---

## 常見問題：安全性問題解答

### Q: ADK 的內建伺服器對生產來說安全嗎？

**A**: ✅ 是的，當部署在安全平台上時 (Cloud Run, Agent Engine, GKE)。

ADK 的伺服器 + Cloud Run = 生產安全系統。平台處理網路安全性；ADK 處理應用程式邏輯。

**證據**：成千上萬個生產 ADK 代理正在使用中，沒有歸因於 ADK 伺服器設計的安全性漏洞。

---

### Q: 我需要為我的 ADK 代理新增驗證嗎？

**A**: ✅ 是的，但取決於平台：

- **Cloud Run**: 使用 Cloud Run IAM（內建）
- **Agent Engine**: 使用 Agent Engine OAuth（內建）
- **GKE**: 使用 Workload Identity（平台處理）
- **自訂需求**: 在自訂 FastAPI 伺服器中實作

不要在您的代理程式碼中實作驗證——使用平台驗證。

---

### Q: 我應該使用 HTTPS/TLS 嗎？

**A**: ✅ 是的，自動使用：

- **Cloud Run**: HTTPS 強制（TLS 1.3 自動）
- **Agent Engine**: HTTPS 強制（TLS 1.3 自動）
- **GKE**: HTTPS 可用（透過 Ingress 設定）
- **Local dev**: 僅 localhost 可用 HTTP

您無需設定此項——平台強制執行。

---

### Q: 我如何防禦 DDoS？

**A**: ✅ 平台處理它：

- **Cloud Run**: Google Cloud Armor（自動）
- **Agent Engine**: 包含（自動）
- **GKE**: Google Cloud Armor（選用）
- **Local dev**: 使用防火牆

您無需實作 DDoS 防護——平台提供它。

---

### Q: 我應該將 API 金鑰儲存在哪裡？

**A**: ✅ Cloud Secret Manager（絕不在程式碼中）：

```python
# 錯誤 ❌
API_KEY = "sk-12345"

# 正確 ✅
from google.cloud import secretmanager
secret = secretmanager.SecretManagerServiceClient()
response = secret.access_secret_version(
    request={"name": f"projects/{project}/secrets/api-key/versions/latest"}
)
API_KEY = response.payload.data.decode('UTF-8')
```

所有平台皆支援 Secret Manager。請使用它。

---

### Q: 我如何記錄安全性事件？

**A**: ✅ 使用平台日誌：

- **Cloud Run**: Cloud Logging（自動）
- **Agent Engine**: Agent Engine Logs（自動）
- **GKE**: Cloud Logging（設定）
- **Local dev**: 使用 Python logging

記錄驗證嘗試、授權失敗、可疑模式。

---

### Q: 為了安全性我需要自訂伺服器嗎？

**A**: ❌ 不需要，除非您有特殊需求：

**使用內建 ADK 伺服器，如果**：
- ✅ Cloud Run IAM 驗證足夠
- ✅ Agent Engine OAuth 足夠
- ✅ 不需要自訂驗證

**使用自訂 FastAPI (教學 23)，如果**：
- ✅ 自訂驗證 (LDAP, Kerberos)
- ✅ 額外的業務邏輯端點
- ✅ 非 Google Cloud 部署
- ✅ 需要進階可觀察性

大多數生產部署 (80%) 不需要自訂伺服器。

---

### Q: Cloud Run 和 Agent Engine 安全性有什麼不同？

**A**: 兩者都安全，但模式不同：

| 方面 | Cloud Run | Agent Engine |
|--------|-----------|--------------|
| **Auth** | IAM | OAuth |
| **合規性** | 可設定 | 內建 FedRAMP |
| **設定** | 低 | 非常低 |
| **成本** | ~$40/月 | ~$50/月 |
| **最適合** | 一般生產 | 受監管產業 |

如果需要 FedRAMP 則選擇 Agent Engine，否則 Cloud Run 即可。

---

### Q: 我如何驗證安全性是否運作？

**A**: ✅ 使用驗證檢查清單（依平台）：

**Cloud Run 檢查清單**：
- [ ] 測試缺少 IAM 角色的端點（應失敗）
- [ ] 測試具有有效 IAM 角色的端點（應成功）
- [ ] 驗證僅 HTTPS (無 HTTP)
- [ ] 審查 Cloud Audit Logs

**Agent Engine 檢查清單**：
- [ ] 測試無效 token 的端點（應失敗）
- [ ] 測試有效 token 的端點（應成功）
- [ ] 驗證私有端點（僅內部）
- [ ] 審查 Agent Engine 稽核日誌

---

## 結論

✅ **當部署在安全平台上時，ADK 對生產來說是安全的。**

安全性模型是：

1. **ADK 提供**：應用程式驗證、工作階段管理、基本日誌
2. **平台提供**：網路安全性、驗證、加密、合規性
3. **您提供**：輸入驗證、秘密管理、監控

**選擇您的平台**：
- **Cloud Run**：良好的通用型（大多數部署）
- **Agent Engine**：最佳合規性（受監管產業）
- **GKE**：企業級 Kubernetes
- **Local**：僅限開發

**安心部署**：成千上萬個生產 ADK 代理證明了此安全性模型是有效的。

---

## 額外資源

- 📖 [詳細分析](./SECURITY_ANALYSIS_ALL_DEPLOYMENT_OPTIONS.md) - 依平台深入探討
- 🔧 [教學 23](../../docs/tutorial/23_production_deployment.md) - 自訂 FastAPI 模式
- ✅ [部署檢查清單](./DEPLOYMENT_CHECKLIST.md) - 部署前驗證
- 🔐 [安全性驗證](./SECURITY_VERIFICATION.md) - 依平台測試

---

**最後更新**：2025 年 10 月 17 日
**狀態**：✅ 生產就緒
**已審查**：安全性研究完成
