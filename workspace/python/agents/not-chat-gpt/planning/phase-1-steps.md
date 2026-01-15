# Phase 1: 基礎對話系統實作步驟

本文件基於 `planning.md` 的規劃，將 Phase 1 的目標拆解為更詳細、可執行的開發步驟。

---

## 📋 Phase 1 目標概述

**時程**: Week 1 - Week 2.5 (約 2.5 週)

**核心目標**: 建立具備多輪對話、狀態管理、思考模式切換、安全防護與知識庫整合的基礎 AI 對話系統。

**技術棧**: Google ADK + Gemini 2.0 Flash + SQLite + Gemini File Search API

**成功標準**:

- ✅ 基本對話功能完整運作
- ✅ 思考模式切換正常
- ✅ 安全防護機制生效  
- ✅ RAG 文檔問答功能可用
- ✅ CLI 測試工具完成

---

## Week 1: 核心 Agent 建構

**目標**: 建立具備多輪對話、狀態管理、思考模式切換能力的基礎 Agent 系統。

### 1.1 環境設定與專案初始化

- [x] 建立 `not-chat-gpt` 專案根目錄
- [x] 根據 `planning.md` 建立完整的專案目錄結構
- [x] 初始化 Python 虛擬環境 (`python -m venv .venv`)
- [x] 建立 `backend/requirements.txt` 並安裝套件
- [x] 配置開發環境

### 1.2 基礎 Agent 實作 (參考 Day 16: hello-agent)

- [x] 在 `backend/agents/conversation_agent/agent.py` 中建立 `ConversationAgent`
- [x] 實作基本的對話回應功能
- [x] 啟動 ADK API 伺服器 `adk api_server backend/agents`
- [x] 使用 `/run` 端點測試 Agent 基本回應

  ```bash
  # Create a new session
  curl --location 'http://localhost:8000/apps/conversation_agent/users/u_123/sessions/s_123' \
  --header 'Content-Type: application/json' \
  --data '{"key1": "value1", "key2": 42}'

  # Send a query
  curl --location 'http://localhost:8000/run' \
  --header 'Content-Type: application/json' \
  --data '{
      "appName": "conversation_agent",
      "userId": "u_123",
      "sessionId": "s_123",
      "newMessage": {
          "role": "user",
          "parts": [
              {
                  "text": "Hey whats the weather in new york today"
              }
          ]
      }
  }'
  ```

### 1.3 Session State Management (參考 Day 17: personal-tutor)

- [x] 實作 ToolContext 狀態管理
- [x] 建立使用者資訊記憶功能 (remember_user_info, get_user_info)
- [x] 整合 ADK 內建會話管理端點
- [x] 測試多輪對話與上下文記憶

```bash
  # Create a new session
  curl --location 'http://localhost:8000/apps/conversation_agent/users/u_123/sessions/s_123' \
  --header 'Content-Type: application/json' \
  --data '{"key1": "value1", "key2": 42}'

  # 第一輪
  curl --location 'http://localhost:8000/run' \
  --header 'Content-Type: application/json' \
  --data '{
      "appName": "conversation_agent",
      "userId": "u_123",
      "sessionId": "s_123",
      "newMessage": {
          "role": "user",
          "parts": [
              {
                  "text": "Hi, 我是 Chris, 是一名資深工程師, 喜歡跑步."
              }
          ]
      }
  }'

  # 第二輪
  curl --location 'http://localhost:8000/run' \
  --header 'Content-Type: application/json' \
  --data '{
      "appName": "conversation_agent",
      "userId": "u_123",
      "sessionId": "s_123",
      "newMessage": {
          "role": "user",
          "parts": [
              {
                  "text": "我是誰?"
              }
          ]
      }
  }'
```

### 1.4 Orchestrator 架構實作 (參考 Day 12: Planners and Thinking)

- [x] **(架構設計)** 採用 Orchestrator + Sub-Agents 模式
- [x] 建立 `conversation_agent/agent.py` (一般對話模式)
- [x] 建立 `strategic_planner_agent/agent.py` (策略規劃模式，使用 BuiltInPlanner)
- [x] 實作 `agent.py` 作為主要協調器 (OrchestratorAgent)
- [x] 實作意圖分析與任務委派邏輯 (#think 指令檢測)
- [x] 測試模式切換功能

#### 測試案例驗證

**測試用意**: 驗證 Orchestrator 能正確路由到不同的 Sub-Agent，並確保狀態管理與模式切換功能正常運作。

```bash
# 使用 make dev 或 make dev-web 進行以下測試

# 測試 1: 狀態記憶功能 (ConversationAgent)
輸入: "Hi, 我是 Chris, 是一名資深工程師, 喜歡跑步."
預期: 一般對話模式，記住使用者資訊，友善回應

# 測試 2: 記憶回憶功能 (ConversationAgent + 狀態檢索)
輸入: "我是誰"
預期: 成功回憶先前儲存的資訊：Chris, 資深工程師, 喜歡跑步

# 測試 3: 模式切換功能 (Strategic Planner Agent)
輸入: "幫我規劃三個月後的長馬訓練課程 #think"
預期: 
- 檢測到 #think 關鍵字
- 路由到 strategic_planner_agent
- 顯示結構化思維過程 (<PLANNING>, <REASONING>, <ACTION>)
- 提供系統性的訓練計畫
```

**驗證要點**:

1. **路由正確性**: `#think` 觸發策略規劃模式，無 `#think` 使用對話模式
2. **狀態持續性**: Sub-Agent 間能共享使用者狀態資訊
3. **回應格式**: Strategic Planner 產生結構化的規劃輸出
4. **上下文整合**: 規劃內容能結合使用者背景（跑步愛好者）

### 1.5 安全防護層實作 (參考 Day 18: content-moderator)

- [x] 建立 `backend/guardrails/` 模組
- [x] 實作 PII 偵測
- [x] 測試基本安全防護功能

### 1.6 CLI 測試驗證

- [x] 使用 `make dev` 指令測試基本對話功能
- [x] 測試模式切換功能 (輸入包含 `#think` 的訊息)
- [x] 測試多輪對話與狀態記憶
- [x] 測試安全防護觸發情境 (輸入敏感資訊)

```bash
# 啟動 CLI 測試 (推薦)
make dev
# 等同於：uv run adk run backend/agents
# 優勢：無需手動 activate 虛擬環境，uv 自動管理

# 或啟動 Web 介面測試
make dev-web  
# 等同於：uv run adk web backend
# 開啟 http://localhost:8000 進行測試

# 測試項目：
# 1. 基本對話：「Hello, how are you?」
# 2. 狀態記憶：「我是 Chris」→「我是誰？」
# 3. 模式切換：「#think 如何提升程式碼品質？」
# 4. 安全防護：輸入包含 PII 的內容
```

---

## Week 2: 串流與持久化

**目標**: 實現串流回應、對話持久化與測試框架。

### 2.1 串流回應測試 (內建 ADK 串流 API)

**重要發現**: ADK 內建完整的串流支援生態，包含三種模式！

#### ADK 內建串流端點

- **`/run`**: 標準 HTTP (同步回應)
- **`/run_sse`**: Server-Sent Events (單向串流)  
- **`/run_live`**: WebSocket (雙向串流，支援即時互動)

#### 測試串流功能

- [x] **測試 SSE 串流端點**：

  ```bash
  # 啟動 API 伺服器
  adk api_server backend/agents
  
  # 測試 SSE 串流 (curl)
  curl -N --location 'http://localhost:8000/run_sse' \
  --header 'Content-Type: application/json' \
  --data '{
      "app_name": "agents",
      "user_id": "u_123", 
      "session_id": "s_123",
      "new_message": {
          "role": "user",
          "parts": [{"text": "寫一首關於程式設計的長詩，包含10個段落"}]
      },
      "streaming": true
  }'
  ```

- [x] **測試 Web 界面串流** (推薦)：

  ```bash
  make dev-web  # 啟動 adk web
  # 訪問 http://localhost:8000
  # 輸入長回應請求，觀察即時打字效果
  ```

- [ ] **WebSocket 串流測試** (進階)：

  ```bash
  # Web 界面自動支援 WebSocket 雙向通訊
  # 可測試即時互動和打斷功能
  ```

#### 驗證要點

- **即時顯示**: 文字逐步出現，無需等待完整回應
- **流暢性**: 長回應的串流表現
- **錯誤處理**: 網路中斷時的重連機制
- **格式正確**: SSE 事件格式符合規範

**CLI 模式說明**: `adk run` 因終端機限制不支援視覺串流效果，但邏輯上仍可配置串流模式。主要測試建議使用 Web 界面。

### 2.2 對話持久化升級 (Redis Session 快取層)

**目標**: 從 ADK 內建 SQLite 升級到 Redis 快取層，提升會話管理效能與可擴展性。

#### Redis Session 實作

- [x] **Docker Redis 環境設定**：

  ```bash
  # docker-compose.yml 新增 Redis 服務
  services:
    redis-adk-not-chat-gpt:
      image: redis:7-alpine
      ports:
        - "6379:6379"
      volumes:
        - redis_data:/data
      command: redis-server --appendonly yes
  
  volumes:
    redis_data:
  ```

- [x] **Redis 依賴安裝**：

  ```bash
  # 使用 uv 安裝 Redis 依賴
  uv add redis
  ```

- [x] **實作 RedisSessionService**：
  - ✅ 建立 `service/redis_session_service.py`
  - ✅ 實作 ADK `BaseSessionService` 介面
  - ✅ 整合 Redis 連接與錯誤處理
  - ✅ 實作會話 TTL 管理 (24小時過期)
  - ✅ 完整的 CRUD 操作 (create, get, list, delete)
  - ✅ append_event 方法實作狀態持久化

- [x] **環境變數配置**：

  ```bash
  # .env.example
  REDIS_URL=redis://localhost:6379/0
  SESSION_TTL=3600  # Redis TTL in seconds
  ```

- [x] **Agent 整合設定** (參考 custom-session-agent 範例)：
  - 在 `backend/main.py` 建立 RedisSessionService 工廠函式
  - 註冊 Redis session service 到 ADK 服務註冊表
  - 實作服務初始化邏輯，支援 URI 參數傳遞
  - 設定預設的降級策略 (Redis 無法連接時使用內建服務)

- [x] **使用命令列參數測試**：

  ```bash
  # 使用 Redis session service 啟動
  uv run backend/main.py web backend --session_service_uri=redis://localhost:6379
  
  # 驗證 Redis 連接狀態
  # 在 Web UI 中測試多輪對話，確認會話狀態儲存在 Redis
  # 重啟伺服器後檢查會話是否保持
  ```

- [x] **Redis Session 測試與驗證**：

  ```bash
  # 啟動 Redis
  docker-compose up redis -d
  
  # 測試會話管理功能
  # 驗證項目:
  # 1. 會話建立與檢索
  # 2. 狀態數據持久化
  # 3. ADK Server 重啟後數據恢復
  ```

- [x] **Makefile 指令擴展**：

  ```bash
  # 新增 make 指令
  make redis-up       # 啟動 Redis 服務
  make redis-down     # 停止 Redis 服務
  make dev-main       # 透過 main.py 註冊服務後再呼叫 adk cli
  ```

---

## Week 2.5: Agentic RAG 知識庫整合 📚

**目標**: 整合 Gemini File Search API，實現文檔問答功能。

### 2.5.1 Gemini File Search 整合 (參考 Day 45: policy-navigator)

- [ ] 安裝 Google AI Python SDK (`pip install google-generativeai`)
- [ ] 建立 `backend/services/document_service.py`
- [ ] 封裝 File API 操作 (upload, list, get, delete)
- [ ] 在 ConversationAgent 中整合 `file_search` 工具
- [ ] 測試文檔上傳與索引功能

### 2.5.2 文檔管理 API

- [ ] 建立文檔管理端點：
  - `POST /documents/upload`: 檔案上傳
  - `GET /documents`: 文檔列表
  - `DELETE /documents/{file_id}`: 文檔刪除
- [ ] 支援多種檔案格式 (PDF/Word/Markdown/TXT)
- [ ] 實作檔案元資料管理

### 2.5.3 引用來源追蹤 (Citations)

- [ ] 修改 Agent 回應處理，檢查 `citation_metadata`
- [ ] 格式化引用資訊顯示 (包含頁碼)
- [ ] 更新 API 回應格式包含引用資訊
- [ ] 測試多文檔聯合查詢功能

### 2.5.4 RAG 評估測試

- [ ] 建立 `tests/evaluation/eval_set_rag.json` RAG 測試集
- [ ] 實作 RAG 品質評估腳本
- [ ] 測試引用來源準確性
- [ ] 效能基準測試 (查詢延遲、準確率)

---

## 📊 Phase 1 里程碑檢查點

### Week 1 完成標準

- ✅ 基本對話功能運作
- ✅ 多輪上下文記憶正常
- ✅ Orchestrator 路由機制生效
- ✅ 安全防護機制運作
- ✅ CLI 測試工具可用

### Week 2 完成標準

- ✅ 串流回應穩定
- ✅ 對話歷史持久化完成
- ✅ 測試框架建立
- ✅ 單元測試覆蓋率 > 70%
- ✅ 整合測試通過

### Week 2.5 完成標準

- ✅ RAG 文檔問答功能完成
- ✅ 文檔管理 API 運作
- ✅ 引用來源正確顯示
- ✅ RAG 測試覆蓋率 > 80%
- ✅ 效能指標達標 (查詢 < 3s)

---

## 🎯 Phase 1 優先級說明

**P0 (必須完成)**:

- 基礎對話與狀態管理 (1.1-1.3)
- Orchestrator 路由機制 (1.4)
- 串流回應 (2.1)
- RAG 核心功能 (2.5.1-2.5.2)

**P1 (重要功能)**:

- 安全防護層 (1.5)
- 對話持久化 (2.2)
- 引用來源追蹤 (2.5.3)

**P2 (優化功能)**:

- CLI 測試驗證 (1.6) - 使用 make 指令簡化操作
- 完整測試框架 (2.3)
- RAG 評估測試 (2.5.4)

---

## 📋 技術債務追蹤

### 已知限制

1. **SQLite 單機限制**: 生產環境需遷移至 PostgreSQL + Redis
2. **缺乏使用者管理**: 目前僅支援單使用者場景
3. **無錯誤重試機制**: API 失敗時缺乏自動重試
4. **內存使用優化**: 長對話可能導致內存增長

### 技術升級路徑 (Phase 2)

1. **資料庫遷移**: SQLite → PostgreSQL + Redis
2. **監控整合**: 加入 OpenTelemetry
3. **部署優化**: Docker + Cloud Run
4. **前端開發**: React UI

---

## 🔗 Phase 間的銜接

### Phase 1 → Phase 2 交付物

- ✅ 可運作的對話 Agent (CLI 測試)
- ✅ RAG 文檔問答功能
- ✅ 基礎測試覆蓋
- ✅ API 設計文檔
- ✅ SQLite 資料 schema

### Phase 2 期待

- 工具整合 (Google Search, Code Execution)
- React Web UI
- 使用者體驗優化
- 進階 RAG 功能

此設計確保 Phase 1 能獨立交付一個完整的 MVP 系統，同時為後續 Phase 奠定堅實基礎。
