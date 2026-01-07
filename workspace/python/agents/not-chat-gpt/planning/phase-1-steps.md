# Phase 1: 實作步驟拆解

本文件基於 `phase-1-goal.md` 的規劃，將 Phase 1 的目標拆解為更詳細、可執行的開發步驟。

---

## Week 1: 核心 Agent 建構

**目標**: 建立一個具備多輪對話、狀態管理、安全防護與思考模式切換能力的基礎對話 Agent，並完全使用 `adk api_server` 提供服務。

### 1.1 環境設定與專案初始化

- [x] 建立 `not-chat-gpt` 專案根目錄。
- [x] 根據 `phase-1-goal.md` 的規劃，建立完整的專案目錄結構 (backend, frontend, tests, docs, etc.)。
- [x] 初始化 Python 虛擬環境 (`python -m venv .venv`)。
- [x] 建立 `backend/requirements.txt` 並記錄已安裝的套件。
- [x] 安裝套件 `pip install -r backend/requirements.txt`

#### 1.2 基礎 Agent 實作 (參考 Day 16: hello-agent)

- [x] 在 `backend/agents/conversation_agent.py` 中，建立繼承自 `adk.Agent` 的 `ConversationAgent`。
- [x] 在 Agent 中定義一個 `Root` method，用於接收並回應使用者輸入。
- [x] 啟動內建 API 伺服器 `adk api_server backend/agents`。
- [x] 使用 `curl` 或 `requests` 函式庫，透過標準的 `/run` 端點來測試 Agent 的基本回應。

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

#### 1.3 Session State Management (參考 Day 17: personal-tutor)

- [ ] 在 `ConversationAgent` 中定義一個 `ToolContext`，用來儲存和傳遞對話歷史 (`history`)。
- [ ] 修改 Agent 的 `Root` method，使其能夠從 `ToolContext` 中讀取先前的對話，並在回應後將新的對話內容更新回去。
- [ ] **(修改)** 使用 `adk api_server` 內建的 `POST /apps/{appName}/users/{userId}/sessions/{sessionId}` 端點來建立和管理會話，並在呼叫 `/run` 時傳入 `sessionId`。
- [ ] 測試多輪對話

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

  # 第三輪
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
                  "text": "我的興趣是什麼？"
              }
          ]
      }
  }'
```

#### 1.4 思考模式切換 (參考 Day 20: strategic-solver)

- [ ] 建立 `backend/config/mode_config.py`，定義不同的 `ThinkingConfig`。
- [ ] 在 `ConversationAgent` 中引入 `adk.BuiltInPlanner`。
- [ ] **(修改)** 修改 `Root` method，使其可以根據傳入 `ToolContext` 或會話狀態中的 `mode` 參數，動態切換 Agent 的 `ThinkingConfig`。

#### 1.6 簡易 CLI 測試

- [ ] 建立一個 `scripts/cli_tester.py` 腳本。
- [ ] **(修改)** 該腳本透過 `requests` 函式庫呼叫由 `adk api_server` 提供的 `/run` API，並在終端機中進行多輪對話測試。

---

### Week 2: 串流與持久化

#### 2.1 SSE 串流回應 (參考 Day 23: streaming-agent)

- [ ] **(修改)** 修改 `ConversationAgent` 的 `Root` method，使其成為一個 `generator` (使用 `yield`) 來串流式地回傳 LLM 的回應區塊。
- [ ] **(修改)** `adk api_server` 會自動偵測到 `generator` 並以串流方式回應。更新 `scripts/cli_tester.py` 以處理串流回應。

#### 2.3 會話管理 API

- [ ] **(移除)** 不再需要自訂會話管理 API。
- [ ] **(新增)** 熟悉並使用 `adk api_server` 提供的會話管理端點 (例如 `POST /apps/.../sessions/...`)。

#### 2.4 測試框架與基礎測試

- [ ] 設定 `pytest` 測試環境。
- [ ] 建立 `tests/unit/test_agent.py`，為 `ConversationAgent` 的核心邏輯撰寫單元測試。
- [ ] **(修改)** 建立 `tests/integration/test_api.py`，使用 `requests` 函式庫對運行中的 `adk api_server` 執行整合測試，驗證 `/run` 和會話管理端點的正確性。移除 `TestClient` 的使用。

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
