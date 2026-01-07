# Phase 1: 實作步驟拆解

本文件基於 `phase-1-goal.md` 的規劃，將 Phase 1 的目標拆解為更詳細、可執行的開發步驟。

---

## Week 1: 核心 Agent 建構

**目標**: 建立一個具備多輪對話、狀態管理、安全防護與思考模式切換能力的基礎對話 Agent。

### 1.1 環境設定與專案初始化

- [ ] 建立 `not-chat-gpt` 專案根目錄。
- [ ] 根據 `phase-1-goal.md` 的規劃，建立完整的專案目錄結構 (backend, frontend, tests, docs, etc.)。
- [ ] 初始化 Python 虛擬環境 (`python -m venv .venv`) 並安裝核心依賴 (`pip install google-adk fastapi uvicorn`)。
- [ ] 建立 `backend/requirements.txt` 並記錄已安裝的套件。
- [ ] 建立 `backend/main.py` 作為 FastAPI 應用程式的進入點。

### 1.2 基礎 Agent 實作 (參考 Day 16: hello-agent)

- [ ] 在 `backend/agents/conversation_agent.py` 中，建立一個繼承自 `adk.Agent` 的 `ConversationAgent`。
- [ ] 在 Agent 中定義一個 `Root` method，用於接收並回應使用者輸入。
- [ ] 在 `backend/api/routes.py` 中建立一個 `/chat` POST 端點，用於接收請求並呼叫 `ConversationAgent`。

### 1.3 Session State Management (參考 Day 17: personal-tutor)

- [ ] 建立 `backend/services/session_service.py`，實作一個簡單的 In-Memory Session Service 來儲存對話歷史。
- [ ] 讓 `ConversationAgent` 能夠接收 `session_id`，並透過 Session Service 讀取和寫入對話狀態。
- [ ] 在 `/chat` 端點中整合 Session 管理邏輯。

### 1.4 思考模式切換 (參考 Day 20: strategic-solver)

- [ ] 建立 `backend/config/mode_config.py`，定義不同的 `ThinkingConfig` (例如：`FAST_MODE`, `STRATEGIC_MODE`)。
- [ ] 在 `ConversationAgent` 中引入 `adk.BuiltInPlanner`。
- [ ] 讓 `/chat` 端點可以接收一個 `mode` 參數，並根據該參數為 Agent 設定不同的 `ThinkingConfig`。

### 1.5 安全防護層 Guardrails (參考 Day 18: content-moderator)

- [ ] 建立 `backend/guardrails/safety_callbacks.py`，並實作一個繼承自 `adk.AgentCallbacks` 的 `SafetyCallbacks`。
- [ ] 在 `SafetyCallbacks` 中實作 `on_llm_start` 和 `on_llm_end` 方法，加入基本的日誌記錄。
- [ ] 建立 `backend/guardrails/content_moderator.py`，並在 `SafetyCallbacks` 中呼叫它，以進行內容審核（初期可為假實作）。
- [ ] 將 `SafetyCallbacks` 實例傳遞給 `ConversationAgent`。

### 1.6 簡易 CLI 測試

- [ ] 建立一個 `scripts/cli_tester.py` 腳本。
- [ ] 該腳本可以透過 `requests` 函式庫呼叫本地運行的 `/chat` API，並在終端機中進行多輪對話測試。

---

## Week 2: 串流與持久化

**目標**: 實現 SSE 串流回應，並將對話歷史從記憶體改為使用資料庫持久化。

### 2.1 SSE 串流回應 (參考 Day 23: streaming-agent)

- [ ] 建立 `backend/agents/streaming_agent.py`，或修改 `ConversationAgent` 以支援串流模式。
- [ ] 在 Agent 的 `Root` method 中，將 `stream=True` 傳遞給 LLM 呼叫。
- [ ] 在 `backend/api/routes.py` 中，建立一個 `/chat/stream` 端點，返回 FastAPI 的 `StreamingResponse`。
- [ ] 實作一個非同步生成器 (async generator) 來處理並 `yield` LLM 的串流區塊。

### 2.2 對話歷史持久化 (參考 Day 58: custom-session-agent)

- [ ] 選擇一個資料庫方案（建議初期使用 SQLite 以簡化設定）。
- [ ] 修改 `backend/services/session_service.py`，將對話歷史的儲存邏輯從 In-Memory 改為寫入 SQLite 資料庫。
- [ ] 實作 `create_session`, `get_session`, `update_session` 等與資料庫互動的函式。
- [ ] 確保 `session_id` 能正確對應到資料庫中的紀錄。

### 2.3 會話管理 API

- [ ] 在 `backend/api/routes.py` 中新增以下管理端點：
  - `POST /sessions`: 建立一個新的會話，並返回 `session_id`。
  - `GET /sessions`: 列出所有歷史會話。
  - `GET /sessions/{session_id}`: 獲取特定會話的詳細對話歷史。

### 2.4 測試框架與基礎測試

- [ ] 設定 `pytest` 測試環境，建立 `tests/` 目錄結構。
- [ ] 建立 `tests/unit/backend/test_agent.py`，為 `ConversationAgent` 的核心邏輯撰寫單元測試。
- [ ] 建立 `tests/integration/test_api.py`，使用 `TestClient` 測試 `/chat` 和 `/sessions` 系列端點的正確性。

---

## Week 2.5: 知識庫整合 (Agentic RAG)

**目標**: 整合 Gemini File Search API，實現文檔上傳、管理與 RAG 問答功能。

### 3.1 Gemini File Search 整合 (參考 Day 45: policy-navigator)

- [ ] 安裝 Google AI Python SDK (`pip install google-generativeai`)。
- [ ] 建立 `backend/services/document_service.py`，封裝 File API 的操作 (upload, list, get, delete)。
- [ ] 在 `ConversationAgent` 中整合 `adk.tool.file_search` 工具。
- [ ] 確保 Agent 在需要時能正確呼叫 File Search 工具進行 RAG。

### 3.2 文檔管理 API

- [ ] 在 `backend/api/routes.py` 中新增以下文檔管理端點：
  - `POST /documents/upload`: 處理檔案上傳，並呼叫 `document_service` 將檔案上傳至 Gemini。
  - `GET /documents`: 列出所有已上傳的文檔。
  - `DELETE /documents/{file_id}`: 刪除指定的文檔。

### 3.3 引用來源追蹤 (Citations)

- [ ] 修改 Agent 的回應處理邏輯，檢查 LLM 回應中是否包含 `citation_metadata`。
- [ ] 當偵測到引用來源時，將其格式化並附加到最終回應中。
- [ ] 修改 `/chat` 和 `/chat/stream` 端點的回應格式，使其能包含引用資訊。

### 3.4 RAG 評估測試

- [ ] 在 `tests/evaluation/` 目錄下建立 `eval_set_rag.json`，包含一組問答對和對應的參考文件。
- [ ] 建立 `tests/evaluation/test_rag_quality.py`，撰寫評估腳本，自動化執行 RAG 問答並比對結果，以評估知識庫問答的準確性。
