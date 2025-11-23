# 安全性驗證指南：驗證每個平台是否安全

**使用本指南驗證您已部署的 ADK 代理是否具備所有必要的安全性功能。**

---

## 平台：Cloud Run

### 自動安全性（已為您完成 ✅）

- ✅ HTTPS/TLS 1.3
- ✅ DDoS 防護
- ✅ 傳輸中加密
- ✅ 靜態加密
- ✅ 非 root 容器執行
- ✅ 二進位漏洞掃描
- ✅ 基於 IAM 的存取控制

### 要驗證什麼

#### 1. HTTPS 強制執行

```bash
SERVICE_URL=$(gcloud run services describe agent \
  --region us-central1 --format 'value(status.url)')

# 應該是 https://
echo $SERVICE_URL | grep "https://"
```

**✅ 通過**：URL 以 `https://` 開頭
**❌ 失敗**：URL 以 `http://` 開頭

#### 2. 需要驗證

```bash
# 取得未驗證的 token
TOKEN=$(gcloud auth print-access-token)

# 測試：應要求 auth
curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL/health

# 應傳回 403 或 302（非 200）
```

**✅ 通過**：傳回 403 或 302（需要驗證）
**❌ 失敗**：傳回 200（未受保護）

#### 3. CORS 設定

```bash
# 測試 CORS
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS $SERVICE_URL/invoke -v 2>&1 | grep -i "access-control"
```

**✅ 通過**：傳回 `Access-Control-Allow-Origin: https://yourdomain.com`
**❌ 失敗**：傳回 `*`（萬用字元 - 太寬鬆）或遺失標頭

#### 4. 安全性標頭

```bash
# 檢查安全性標頭
curl -I $SERVICE_URL/health | grep -i "x-"
```

**✅ 通過**：應看到像 `x-goog-*` 的標頭和安全性標頭
**❌ 失敗**：遺失安全性標頭

#### 5. 容器安全性

```bash
# 驗證非 root 使用者
gcloud run services describe agent --region us-central1 \
  --format='value(spec.template.spec.serviceAccountName)'

# 應該不是 root 或空值
```

**✅ 通過**：顯示特定的服務帳戶（非 root）
**❌ 失敗**：空值或以 root 執行

#### 6. 資源限制

```bash
# 驗證記憶體限制
gcloud run services describe agent --region us-central1 \
  --format='value(spec.template.spec.containers[0].resources.limits.memory)'

# 應顯示限制（例如："2Gi"）
```

**✅ 通過**：顯示記憶體限制
**❌ 失敗**：空值或無限制

#### 7. 稽核日誌

```bash
# 檢查稽核日誌
gcloud logging read "resource.service.name=agent" \
  --limit 10 --format json | jq '.[0]'

# 應顯示最近的活動
```

**✅ 通過**：在日誌中看到最近的請求
**❌ 失敗**：沒有出現日誌

---

## 平台：Agent Engine

### 自動安全性（已為您完成 ✅）

- ✅ 僅私有端點
- ✅ 服務間通訊的 mTLS
- ✅ OAuth 2.0 驗證
- ✅ HTTPS/TLS 1.3
- ✅ DDoS 防護
- ✅ WAF (Web Application Firewall)
- ✅ 傳輸中加密
- ✅ 靜態加密
- ✅ 內容安全性過濾器
- ✅ **FedRAMP 合規**（如果已設定）
- ✅ SOC 2 Type II
- ✅ 稽核日誌

### 要驗證什麼

#### 1. 代理已部署

```bash
# 檢查 Agent Engine 控制台
# https://console.cloud.google.com/vertex-ai/agents

# 或透過 CLI：
gcloud ai agents list --project YOUR_PROJECT
```

**✅ 通過**：代理出現在控制台/清單中
**❌ 失敗**：找不到代理

#### 2. 端點安全

```bash
# Agent Engine 端點預設為私有
# 在控制台中驗證：
# - ✅ 端點顯示 "Private"
# - ✅ 僅可透過 OAuth token 存取
# - ✅ 無公開 IP
```

**✅ 通過**：端點標記為 Private
**❌ 失敗**：端點標記為 Public

#### 3. OAuth 驗證運作正常

```bash
# 取得 OAuth token
TOKEN=$(gcloud auth application-default print-access-token)

# Agent Engine 調用（方法因設定而異）
# 應要求有效的 OAuth token

# 測試無 token 應失敗
curl -s AGENT_ENGINE_URL
```

**✅ 通過**：未驗證的請求失敗，token 請求成功
**❌ 失敗**：未驗證的請求成功

#### 4. 稽核日誌出現

```bash
# 檢查 Cloud Audit Logs
gcloud logging read "protoPayload.serviceName=aiplatform.googleapis.com" \
  --limit 10 --format json | jq '.[0]'

# 應顯示代理活動
```

**✅ 通過**：在稽核日誌中看到代理調用
**❌ 失敗**：無稽核日誌項目

#### 5. 內容安全性過濾器啟用

```bash
# 使用潛在不安全的輸入進行測試
# 提交設計用來觸發安全性過濾器的查詢
# 應被拒絕並顯示適當的訊息

# 範例："如何製作有害內容？"
# 應傳回安全性拒絕，而非答案
```

**✅ 通過**：不安全的查詢被拒絕
**❌ 失敗**：不安全的查詢被回答

#### 6. FedRAMP 合規（如果需要）

```bash
# 檢查合規性狀態
# https://console.cloud.google.com/iam-admin/compliance

# 驗證：
# - ✅ 列出 FedRAMP (Moderate 或 High)
# - ✅ 認證日期有效
# - ✅ 範圍包含 Vertex AI Agent Engine
```

**✅ 通過**：FedRAMP 認證顯示有效
**❌ 失敗**：未列出或過期

---

## 平台：GKE (Kubernetes)

### 自動安全性（平台層級）

- ✅ Workload Identity (Pod → Google 服務)
- ✅ RBAC (基於角色的存取控制)
- ✅ 強制執行 Pod 安全標準
- ✅ 稽核日誌
- ✅ 靜態加密 (etcd 加密)

### 您必須設定與驗證的項目

#### 1. Workload Identity

```bash
# 驗證 Workload Identity 綁定
kubectl describe serviceaccount agent-sa -n default | grep "iam.gke.io"

# 應顯示註釋：
# iam.gke.io/gcp-service-account: agent@YOUR_PROJECT.iam.gserviceaccount.com
```

**✅ 通過**：顯示 Workload Identity 註釋
**❌ 失敗**：無註釋或綁定遺失

#### 2. Pod 安全性情境 (Security Context)

```bash
# 驗證 pod 以非 root 身份執行
kubectl get pod -o jsonpath='{.items[0].spec.securityContext.runAsNonRoot}'

# 應傳回：true
```

**✅ 通過**：傳回 `true`
**❌ 失敗**：傳回 `false` 或空值

#### 3. 資源限制

```bash
# 驗證資源限制已設定
kubectl describe pod agent-pod -n default | grep -A 5 "Limits"

# 應顯示 CPU 和記憶體限制
```

**✅ 通過**：定義了 CPU 和記憶體限制
**❌ 失敗**：限制遺失或設為無限制

#### 4. 網路政策 (Network Policy)

```bash
# 驗證 NetworkPolicy 存在
kubectl get networkpolicy -n default

# 應顯示代理流量的政策
```

**✅ 通過**：NetworkPolicy 物件存在且啟用
**❌ 失敗**：未設定 NetworkPolicy

#### 5. Pod 安全標準

```bash
# 檢查命名空間 PSS 標籤
kubectl get namespace default \
  -o jsonpath='{.metadata.labels.pod-security\.kubernetes\.io/enforce}'

# 應顯示 "restricted" 或 "baseline"
```

**✅ 通過**：顯示已強制執行的安全標準
**❌ 失敗**：未強制執行 PSS

#### 6. RBAC 規則

```bash
# 驗證 RBAC 角色
kubectl get role agent-role -n default

# 檢查 ClusterRoleBinding
kubectl get clusterrolebinding | grep agent

# 應看到具有最小權限的角色
```

**✅ 通過**：RBAC 角色存在且具限制性
**❌ 失敗**：無 RBAC 或過於寬鬆

#### 7. 稽核日誌

```bash
# 檢查叢集稽核日誌
gcloud container clusters describe YOUR_CLUSTER \
  --zone YOUR_ZONE \
  --format='value(loggingService)'

# 應顯示 "logging.googleapis.com/kubernetes"
```

**✅ 通過**：日誌已啟用
**❌ 失敗**：日誌已停用

---

## 自訂伺服器 (教學 23 + Cloud Run)

### 您正在新增的項目

- ✅ 自訂驗證 (API 金鑰, tokens)
- ✅ 請求驗證
- ✅ 逾時
- ✅ 指標追蹤
- ✅ 結構化日誌

### 要驗證什麼

#### 1. 自訂驗證運作正常

```bash
SERVICE_URL=$(gcloud run services describe agent \
  --region us-central1 --format 'value(status.url)')

# 測試無 token - 應失敗
curl $SERVICE_URL/invoke

# 測試有 token - 應成功
curl -H "Authorization: Bearer YOUR_API_KEY" \
  -X POST $SERVICE_URL/invoke \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

**✅ 通過**：無 token 失敗 (401)，有 token 成功 (200)
**❌ 失敗**：無 token 成功或總是失敗

#### 2. 請求逾時運作正常

```bash
# 傳送非常長的查詢
LONG_QUERY=$(python3 -c "print('x' * 100000)")

curl -H "Authorization: Bearer YOUR_API_KEY" \
  -X POST $SERVICE_URL/invoke \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$LONG_QUERY\"}" \
  --max-time 35

# 應在約 30 秒後逾時
```

**✅ 通過**：傳回 504 或在約 30 秒後逾時
**❌ 失敗**：無限期處理或太快

#### 3. 輸入驗證運作正常

```bash
# 傳送無效輸入
curl -H "Authorization: Bearer YOUR_API_KEY" \
  -X POST $SERVICE_URL/invoke \
  -H "Content-Type: application/json" \
  -d '{"query": "", "temperature": 5.0}'

# 應傳回 400 Bad Request
```

**✅ 通過**：傳回 400（驗證錯誤）
**❌ 失敗**：傳回 200 或 500

#### 4. 錯誤處理安全

```bash
# 傳送格式錯誤的請求
curl -H "Authorization: Bearer YOUR_API_KEY" \
  -X POST $SERVICE_URL/invoke \
  -H "Content-Type: application/json" \
  -d 'invalid json'

# 回應不應暴露內部細節
# 應為通用錯誤訊息
```

**✅ 通過**：傳回通用錯誤（無堆疊追蹤）
**❌ 失敗**：暴露 Python 堆疊追蹤或內部細節

#### 5. 結構化日誌運作正常

```bash
# 檢查日誌是否有結構化項目
gcloud logging read "resource.service.name=agent" \
  --limit 10 --format json | jq '.[0].jsonPayload'

# 應顯示欄位如：request_id, tokens, latency_ms
```

**✅ 通過**：日誌具有結構化欄位
**❌ 失敗**：日誌為非結構化文字

---

## 完整安全性驗證檢查清單

### 生產前

- [ ] HTTPS/TLS 運作正常（Cloud Run：自動，GKE：驗證）
- [ ] 需要驗證（測試未經授權的存取）
- [ ] CORS 設定正確（特定 origins，無萬用字元）
- [ ] 安全性標頭存在（Cloud Run：自動）
- [ ] 無硬編碼秘密（檢查程式碼和日誌）
- [ ] 秘密在 Secret Manager 中（如果適用）
- [ ] 資源限制已設定（記憶體、CPU、逾時）
- [ ] 稽核日誌已啟用
- [ ] 錯誤處理安全（不暴露敏感細節）

### 部署後

- [ ] 執行上述所有驗證測試
- [ ] 監控日誌是否有錯誤（前 30 分鐘）
- [ ] 檢查指標是否有異常
- [ ] 驗證無安全性警報
- [ ] 使用真實流量樣本進行測試

### 每週

- [ ] 審查稽核日誌
- [ ] 檢查安全性更新
- [ ] 驗證合規性狀態（如果適用）
- [ ] 再次測試安全性驗證

---

## 快速驗證腳本

```bash
#!/bin/bash
# 一鍵安全性驗證

echo "🔐 ADK 部署安全性驗證"
echo "======================================="

SERVICE_URL="https://YOUR-SERVICE.run.app"

echo "✅ HTTPS: $(echo $SERVICE_URL | grep -q https && echo PASS || echo FAIL)"
echo "✅ Auth: $(curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL/health | grep -qE "403|302" && echo PASS || echo FAIL)"
echo "✅ Health: $(curl -s -H "Authorization: Bearer TOKEN" $SERVICE_URL/health | grep -q status && echo PASS || echo FAIL)"
echo "✅ Logs: $(gcloud logging read "resource.service.name=agent" --limit 1 | grep -q '"' && echo PASS || echo FAIL)"

echo ""
echo "需要手動檢查："
echo "- 審查 CORS 設定"
echo "- 驗證日誌中無秘密"
echo "- 檢查資源限制"
echo "- 審查最近的錯誤"
```

---

## 常見安全性問題與修正

### 問題：CORS 傳回萬用字元

**問題**：`Access-Control-Allow-Origin: *`

**修正**：
```bash
# 在您的部署設定中，設定特定 origins：
ALLOWED_ORIGINS=https://yourdomain.com
```

### 問題：秘密出現在日誌中

**問題**：API 金鑰在 Cloud Logging 中可見

**修正**：
```bash
# 使用 Secret Manager
from google.cloud import secretmanager

secret = secretmanager.SecretManagerServiceClient()
api_key = secret.access_secret_version(...)
```

### 問題：允許未經授權的存取

**問題**：任何人皆可在無 auth 情況下呼叫您的代理

**修正**：Cloud Run
```bash
gcloud run services update agent --no-allow-unauthenticated
```

修正：自訂伺服器
```python
# 在所有端點中驗證 API 金鑰
@app.post("/invoke")
async def invoke(request, auth_header):
    verify_api_key(auth_header)  # 必須驗證
```

---

**✅ 在認為部署安全之前，請完成此檢查清單。**
