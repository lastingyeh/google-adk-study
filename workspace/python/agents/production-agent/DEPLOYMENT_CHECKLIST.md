# 部署檢查清單：逐步驗證

**使用此檢查清單驗證您的 ADK 部署是否已準備好進入生產環境。**

---

## 部署前（部署之前）

### 安全性與設定
- [ ] API 金鑰儲存在 Secret Manager 中（不在 .env 或程式碼中）
- [ ] 任何地方都沒有硬編碼的憑證
- [ ] 環境變數設定正確
- [ ] CORS origins 設定為特定網域（絕不使用 `*`）
- [ ] 已啟用驗證（如果需要）
- [ ] 已設定請求逾時（建議 30秒）
- [ ] 已設定最大 token 限制
- [ ] 已定義資源限制（記憶體、CPU）

### 程式碼品質
- [ ] 程式碼已在本地審查和測試
- [ ] 所有測試通過：`pytest tests/ -v`
- [ ] 無安全性警告
- [ ] 相依套件已更新至最新
- [ ] 已實作錯誤處理

### 文件
- [ ] 已記錄部署說明
- [ ] 已記錄 API 端點
- [ ] 已記錄設定選項
- [ ] 已準備好操作手冊 (Runbooks)

---

## 部署 (Cloud Run 範例)

### 步驟 1：建置並推送映像檔

```bash
# 建置
gcloud builds submit --tag gcr.io/YOUR_PROJECT/agent

# 驗證映像檔
gcloud container images describe gcr.io/YOUR_PROJECT/agent
```

- [ ] 建置成功完成
- [ ] 映像檔已掃描漏洞（檢查 Cloud Console）
- [ ] 已啟用映像檔簽署（如果使用 Binary Authorization）

### 步驟 2：部署

```bash
gcloud run deploy agent \
  --image gcr.io/YOUR_PROJECT/agent \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --max-instances 100 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT
```

- [ ] 部署已完成
- [ ] 服務已就緒（檢查控制台）
- [ ] 無部署錯誤

### 步驟 3：設定權限

```bash
# 設定服務帳戶
gcloud run services update agent \
  --service-account agent-sa@YOUR_PROJECT.iam.gserviceaccount.com \
  --region us-central1

# 設定驗證需求
gcloud run services update agent \
  --no-allow-unauthenticated \
  --region us-central1
```

- [ ] 已指派服務帳戶
- [ ] 已設定適當的 IAM 權限
- [ ] 已要求驗證（如果需要）

---

## 部署後：驗證（必要）

### 健康檢查

```bash
# 取得服務 URL
SERVICE_URL=$(gcloud run services describe agent \
  --region us-central1 \
  --format 'value(status.url)')

# 測試健康端點
curl $SERVICE_URL/health
```

- [ ] 健康端點回應 (200 OK)
- [ ] 回應包含狀態、運行時間、請求計數
- [ ] 無錯誤回應

### 代理調用

```bash
# 測試代理調用
curl -X POST $SERVICE_URL/invoke \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello agent!", "temperature": 0.5}'
```

- [ ] 調用成功 (200 OK)
- [ ] 回應包含代理回覆
- [ ] 回應時間 < 5 秒
- [ ] 日誌中無錯誤

### 安全性驗證

```bash
# 1. 檢查 HTTPS
curl -I $SERVICE_URL/health | grep -i "https"

# 2. 測試驗證
curl $SERVICE_URL/health  # 應失敗並顯示 401 或重新導向

# 3. 檢查 CORS 標頭
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS $SERVICE_URL/invoke
```

- [ ] 已強制執行 HTTPS（無 HTTP）
- [ ] 已要求驗證（如果已設定）
- [ ] CORS 標頭存在且正確
- [ ] CORS origins 中無萬用字元 (`*`)
- [ ] 安全性標頭存在

### 監控與日誌

```bash
# 檢視最近的日誌
gcloud logging read "resource.service.name=agent" \
  --limit 10 \
  --format json | jq .

# 檢視 Cloud Monitoring 儀表板
# https://console.cloud.google.com/monitoring/dashboards
```

- [ ] 日誌出現在 Cloud Logging 中
- [ ] 日誌中無錯誤訊息
- [ ] 請求/回應模式正常
- [ ] 錯誤率 < 1%
- [ ] 延遲 < 2 秒 (p99)

### 成本驗證

```bash
# 估算成本
echo "每月估算 100 萬次請求："
echo "Cloud Run: ~\$40 (+ 儲存)"
echo "Agent Engine: ~\$50 (+ 儲存)"
```

- [ ] 成本估算已審查
- [ ] 在預算範圍內
- [ ] 已適當設定擴展限制
- [ ] 自動擴展運作正常

---

## 部署後：設定（一次性）

### 監控設定

```bash
# 建立錯誤率警報
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Agent Error Rate Alert" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

- [ ] Cloud Monitoring 已設定
- [ ] 警報已設定 (Email/PagerDuty)
- [ ] 儀表板已建立
- [ ] 日誌保留已設定

### 日誌設定

```bash
# 匯出日誌至 BigQuery（選用，用於分析）
gcloud logging sinks create agent-bigquery \
  bigquery.googleapis.com/projects/YOUR_PROJECT/datasets/agent_logs \
  --log-filter='resource.type="cloud_run_revision"'
```

- [ ] 日誌匯出已設定
- [ ] 日誌保留政策已設定
- [ ] 日誌過濾運作正常

### 擴展設定

```bash
# 審查擴展設定
gcloud run services describe agent --region us-central1
```

- [ ] 最小執行個體數已設定（如果需要）
- [ ] 最大執行個體數已適當設定
- [ ] CPU 配置正確
- [ ] 記憶體配置正確
- [ ] 併發 (Concurrency) 已設定

---

## 持續進行：每日驗證

### 每日檢查（5 分鐘）

```bash
# 檢查服務健康狀態
curl $SERVICE_URL/health | jq '.error_rate'

# 檢查最近的錯誤
gcloud logging read "resource.service.name=agent AND severity=ERROR" \
  --limit 10 \
  --recent-first
```

- [ ] 無嚴重錯誤
- [ ] 錯誤率正常
- [ ] 回應時間正常
- [ ] 無異常模式

### 每週檢查（15 分鐘）

- [ ] 審查日誌中的警告
- [ ] 檢查警報歷史記錄（是否有觸發？）
- [ ] 驗證成本在預算內
- [ ] 審查指標是否有異常

### 每月檢查（1 小時）

- [ ] 審查效能指標
- [ ] 更新監控儀表板
- [ ] 審查安全性日誌（稽核軌跡）
- [ ] 測試災難復原程序
- [ ] 如果需要，更新操作手冊

---

## 常見問題與修正

### "Service returns 401 Unauthorized" (服務傳回 401 未授權)

**原因**：
- 需要驗證但未提供
- Token 過期或無效
- 服務帳戶權限遺失

**修正**：
```bash
# 檢查是否需要驗證
gcloud run services describe agent --format='value(spec.template.spec.serviceAccountName)'

# 進行測試時，暫時允許未驗證：
gcloud run services update agent --allow-unauthenticated
```

### "High Latency (> 5 seconds)" (高延遲 > 5 秒)

**原因**：
- CPU 不足
- 請求過多（被節流）
- 代理查詢太複雜

**修正**：
```bash
# 增加 CPU
gcloud run services update agent --cpu 4

# 檢查模型載入是否緩慢
# 嘗試使用 gemini-2.0-flash 代替較大的模型
```

### "Out of Memory" (記憶體不足)

**原因**：
- 記憶體限制太低
- 大型請求
- 程式碼中記憶體洩漏

**修正**：
```bash
# 增加記憶體
gcloud run services update agent --memory 4Gi

# 檢查日誌中的記憶體問題
gcloud logging read "resource.service.name=agent AND memory" --limit 5
```

### "CORS Errors" (CORS 錯誤)

**原因**：
- CORS origin 未設定
- 前端 origin 不在允許清單中

**修正**：
```bash
# 在程式碼中更新 CORS origins
# 然後使用新設定重新部署

# 驗證 CORS 標頭
curl -H "Origin: https://yourdomain.com" \
     -X OPTIONS $SERVICE_URL/invoke -v
```

---

## 復原程序

如果出錯：

```bash
# 取得先前的修訂版
PREVIOUS=$(gcloud run revisions list \
  --service=agent \
  --region=us-central1 \
  --sort-by=^ACTIVE \
  --limit=2 \
  --format='value(name)' | tail -1)

# 復原至先前版本
gcloud run services update-traffic agent \
  --to-revisions=$PREVIOUS=100 \
  --region=us-central1
```

- [ ] 復原已完成
- [ ] 服務回應中
- [ ] 錯誤率回復正常

---

## 遷移檢查清單（如果移動到不同平台）

### Cloud Run → Agent Engine

```bash
# 1. 部署至 Agent Engine
adk deploy agent_engine \
  --project YOUR_PROJECT \
  --region us-central1

# 2. 測試 Agent Engine 部署
curl https://AGENT_ID-REGION.endpoints.PROJECT_ID.cloud.goog/health

# 3. 更新 API 用戶端端點
# 更新應用程式以使用新的 Agent Engine 端點

# 4. 監控問題
# 讓流量運行 10% 持續 30 分鐘

# 5. 將 100% 流量導向 Agent Engine
# 停用 Cloud Run

# 6. 刪除 Cloud Run 服務
gcloud run services delete agent --region us-central1
```

- [ ] 新平台已部署並驗證
- [ ] 逐步流量遷移完成
- [ ] 新環境中無錯誤
- [ ] 舊平台已停用

---

## 最終簽核

- [ ] 所有安全性檢查通過
- [ ] 健康和效能已驗證
- [ ] 監控和警報已設定
- [ ] 操作手冊已記錄
- [ ] 團隊已接受部署培訓
- [ ] 備份/復原程序已測試
- [ ] 成本估算已驗證
- [ ] **部署已準備好進入生產環境** ✅
