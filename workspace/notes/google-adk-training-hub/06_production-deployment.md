# Production & Deployment (生產環境與部署)

**目的**: 將 ADK Agent 部署到生產環境，並具備適當的可觀測性、擴展性和服務管理能力。

## 大綱

1.  [Deployment Environments (部署環境)](#deployment-environments)
2.  [Observability & Monitoring (可觀測性與監控)](#observability--monitoring)
3.  [Service Configuration (服務組態)](#service-configuration)
4.  [Security & Best Practices (安全性與最佳實踐)](#security--best-practices)
5.  [Performance Optimization (效能優化)](#performance-optimization)

---

## Deployment Environments (部署環境)

選擇適合您需求的部署環境：本地、無伺服器、託管或自訂。

### Local Development (本地開發)

用於快速的開發與測試。

```bash
# 快速進行開發測試
adk web agent_name

# 使用自訂組態執行
adk run agent_name --config config.yaml
```

### Cloud Run (無伺服器)

具備自動擴展、按使用量付費的特性，適合無伺服器架構。

```bash
# 部署至 Cloud Run
adk deploy cloud_run agent_name

# 服務整合: Cloud SQL, GCS, Vertex AI
```

### Vertex AI Agent Engine (託管)

適用於企業級部署，由 Google 全面託管，提供高可用性與監控。

```bash
# 企業級部署
adk deploy agent_engine agent_name
```

### GKE (Kubernetes)

提供對基礎設施的完全控制權，可自訂擴展策略。

```bash
# 自訂基礎設施
adk deploy gke agent_name
```

---

## Observability & Monitoring (可觀測性與監控)

追蹤、偵錯並優化生產環境中的 Agent 效能。

### Events (事件記錄)

記錄 Agent 生命週期中的關鍵事件。

```python
# 啟用事件日誌記錄
runner = Runner(
    event_service=LoggingEventService(level="DEBUG")
)

# 捕獲的事件:
# - AGENT_START/COMPLETE (Agent 啟動/完成)
# - TOOL_CALL_START/RESULT (工具呼叫啟動/結果)
# - LLM_REQUEST/RESPONSE (LLM 請求/回應)
# - STATE_CHANGE (狀態變更)
```

### Tracing (追蹤)

提供詳細的執行追蹤，用於分析效能瓶頸與錯誤根源。

```python
# 設定詳細的執行追蹤
runner = Runner(
    trace_service=CloudTraceService(project="my-project")
)

# 可在 Cloud Trace 控制台中查看
# - 效能瓶頸分析
# - 錯誤根本原因追溯
```

### Callbacks (回呼函式)

透過自訂回呼函式實現客製化監控。

```python
# 自訂監控函式
def monitor_agent(context, result):
    # 記錄自訂指標
    log_performance(result.execution_time)
    alert_on_errors(result.errors)

# 將回呼函式註冊到 Agent
agent = Agent(
    name="monitored_agent",
    callbacks=[monitor_agent]
)
```

### Evaluation (評估)

透過自動化測試來衡量 Agent 的品質。

```bash
# 執行自動化評估
adk eval agent_name --test-set my_tests.evalset.json

# 評估指標:
# - tool_trajectory_avg_score (工具軌跡平均分數, 0-1)
# - response_match_score (回應匹配分數, 0-1)
# - Custom LLM-as-judge metrics (自訂 LLM 評審指標)
```

---

## 💾 Service Configuration (服務組態)

設定儲存、記憶體和執行等服務。

### Development (InMemory - 記憶體模式)

開發環境預設使用記憶體服務，速度快但資料不持久。

```python
# 所有服務預設為 InMemory
runner = Runner()
```

### Production (Persistent - 持久化模式)

生產環境應使用持久化服務，確保資料的可靠性。

```python
# 設定持久化服務
runner = Runner(
    session_service=PostgresSessionService(uri="..."),
    artifact_service=GcsArtifactService(bucket="..."),
    memory_service=VertexAiMemoryBankService(project="...")
)
```

---

## 🔒 Security & Best Practices (安全性與最佳實踐)

確保生產環境的安全性與合規性。

-   **Environment Variables (環境變數)**: 絕不將密鑰提交到版本控制中。
-   **Service Accounts (服務帳號)**: 遵循最小權限原則。
-   **Input Validation (輸入驗證)**: 對所有輸入進行清理與驗證。
-   **Rate Limiting (速率限制)**: 防止服務被濫用。
-   **Error Handling (錯誤處理)**: 設計優雅的失敗處理模式。

---

## 📊 Performance Optimization (效能優化)

提升 Agent 的執行速度與成本效益。

-   **Model Selection (模型選擇)**: 根據成本與效能需求選擇合適的模型。
-   **Caching (快取)**: 重複使用昂貴的計算結果。
-   **Parallel Execution (平行執行)**: 同時處理獨立的任務。
-   **Batch Processing (批次處理)**: 將相似的請求分組處理。

---

## 🎯 Key Takeaways (重點摘要)

1.  **多種部署選項**: 本地、Cloud Run、Vertex AI、GKE。
2.  **可觀測性層次**: 事件、追蹤、回呼、評估。
3.  **服務組態**: 開發使用 InMemory，生產使用持久化服務。
4.  **安全優先**: 使用環境變數、驗證輸入、設定速率限制。
5.  **效能優化**: 優化模型、使用快取、平行執行。
