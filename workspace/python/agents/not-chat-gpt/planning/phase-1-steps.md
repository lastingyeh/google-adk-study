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

### 1.5 安全防護層實作 (參考 Day 18: content-moderator)

- [ ] 建立 `backend/guardrails/` 模組
- [ ] 實作 `SafetyCallbacks` (AgentCallbacks 子類)
- [ ] 建立內容審核機制 (content_moderator.py)
- [ ] 實作 PII 偵測 (pii_detector.py)
- [ ] 建立意圖分類器 (intent_classifier.py)
- [ ] 整合審計日誌 (audit_logger.py)
- [ ] 測試安全防護功能

### 1.6 CLI 測試工具

- [ ] 建立 `scripts/cli_tester.py` 腳本
- [ ] 支援 HTTP API 呼叫與多輪對話測試
- [ ] 加入模式切換測試 (`--mode strategic`)
- [ ] 測試安全防護觸發情境

---

## Week 2: 串流與持久化

**目標**: 實現串流回應、對話持久化與測試框架。

### 2.1 串流回應實作 (參考 Day 23: streaming-agent)

- [ ] 修改 Agent methods 支援 generator (yield)
- [ ] 實作 SSE 串流回應
- [ ] 更新 CLI 測試工具支援串流處理
- [ ] 測試串流回應效能與穩定性

### 2.2 對話持久化 (參考 Day 58: custom-session-agent)

- [ ] 設計 SQLite 對話歷史 schema
- [ ] 實作 `SessionService` 類別
- [ ] 建立對話管理 API (create/load/list/delete sessions)
- [ ] 整合 ADK Session State 持久化
- [ ] 測試對話歷史儲存與載入

### 2.3 測試框架建立 (參考 Day 19: support-agent)

- [ ] 配置 pytest 測試環境
- [ ] 建立 `tests/unit/test_agent.py` 單元測試
- [ ] 建立 `tests/integration/test_api.py` 整合測試
- [ ] 建立 `tests/evaluation/eval_set.json` 評估數據集
- [ ] 實作 AgentEvaluator 品質測試
- [ ] 建立 Guardrails 安全性測試

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

- CLI 測試工具 (1.6)
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
