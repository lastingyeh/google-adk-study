# Phase 1

Phase 1: 基礎對話系統（Week 1-2）

## 前情提要

使用 Google ADK + Gemini 2.0 建構一個類 ChatGPT 的對話式 AI 系統，具備多輪對話、工具呼叫、串流回應、思考模式切換、圖片分析等核心功能。

### 專案結構

```text
not-chat-gpt/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── conversation_agent.py
│   │   └── streaming_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── google_search.py
│   │   ├── code_executor.py
│   │   ├── file_handler.py
│   │   └── file_search.py             # 新增：Gemini File Search RAG
│   ├── guardrails/                    # 新增：安全防護層
│   │   ├── __init__.py
│   │   ├── safety_callbacks.py        # AgentCallbacks 實作
│   │   ├── policy_engine.py           # 規範引擎
│   │   ├── content_moderator.py       # 內容審核
│   │   ├── pii_detector.py            # 敏感資訊偵測
│   │   ├── intent_classifier.py       # 意圖分類
│   │   └── audit_logger.py            # 審計日誌
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py
│   │   ├── redis_session_service.py
│   │   └── document_service.py        # 新增：文檔索引管理
│   ├── config/
│   │   ├── __init__.py
│   │   ├── mode_config.py             # 思考模式配置
│   │   └── security_config.py         # 新增：安全配置
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ConversationView.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── InputBox.tsx
│   │   │   ├── ModeSelector.tsx
│   │   │   ├── DocumentPanel.tsx      # 新增：文檔管理面板
│   │   │   └── CitationBadge.tsx      # 新增：引用來源標籤
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── unit/
│   │   ├── backend/
│   │   │   ├── test_agent.py
│   │   │   ├── test_tools.py
│   │   │   └── test_guardrails.py
│   │   └── frontend/
│   │       ├── MessageList.test.tsx
│   │       └── DocumentPanel.test.tsx
│   ├── integration/
│   │   ├── test_workflow.py
│   │   └── test_rag.py
│   ├── e2e/
│   │   ├── test_user_journey.py
│   │   └── test_api_endpoints.py
│   ├── evaluation/
│   │   ├── test_agent_quality.py
│   │   └── eval_set.json
│   ├── conftest.py
│   └── fixtures/
├── deployment/
│   ├── Dockerfile
│   └── cloudbuild.yaml
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── SECURITY.md                    # 新增：安全文件
├── planning.md (本檔案)
└── README.md
```

### 專案結構

```text
not-chat-gpt/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── conversation_agent.py
│   │   └── streaming_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── google_search.py
│   │   ├── code_executor.py
│   │   ├── file_handler.py
│   │   └── file_search.py             # 新增：Gemini File Search RAG
│   ├── guardrails/                    # 新增：安全防護層
│   │   ├── __init__.py
│   │   ├── safety_callbacks.py        # AgentCallbacks 實作
│   │   ├── policy_engine.py           # 規範引擎
│   │   ├── content_moderator.py       # 內容審核
│   │   ├── pii_detector.py            # 敏感資訊偵測
│   │   ├── intent_classifier.py       # 意圖分類
│   │   └── audit_logger.py            # 審計日誌
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py
│   │   ├── redis_session_service.py
│   │   └── document_service.py        # 新增：文檔索引管理
│   ├── config/
│   │   ├── __init__.py
│   │   ├── mode_config.py             # 思考模式配置
│   │   └── security_config.py         # 新增：安全配置
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ConversationView.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── InputBox.tsx
│   │   │   ├── ModeSelector.tsx
│   │   │   ├── DocumentPanel.tsx      # 新增：文檔管理面板
│   │   │   └── CitationBadge.tsx      # 新增：引用來源標籤
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── unit/
│   │   ├── backend/
│   │   │   ├── test_agent.py
│   │   │   ├── test_tools.py
│   │   │   └── test_guardrails.py
│   │   └── frontend/
│   │       ├── MessageList.test.tsx
│   │       └── DocumentPanel.test.tsx
│   ├── integration/
│   │   ├── test_workflow.py
│   │   └── test_rag.py
│   ├── e2e/
│   │   ├── test_user_journey.py
│   │   └── test_api_endpoints.py
│   ├── evaluation/
│   │   ├── test_agent_quality.py
│   │   └── eval_set.json
│   ├── conftest.py
│   └── fixtures/
├── deployment/
│   ├── Dockerfile
│   └── cloudbuild.yaml
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── SECURITY.md                    # 新增：安全文件
├── planning.md (本檔案)
└── README.md
```

---

### 📚 參考資源對照表

| 功能模組       | 參考 Day | 專案名稱             | 核心技術                       |
| -------------- | -------- | -------------------- | ------------------------------ |
| 基礎 Agent     | Day 16   | hello-agent          | Agent, Root                    |
| 狀態管理       | Day 17   | personal-tutor       | Session State                  |
| 安全防護       | Day 18   | content-moderator    | AgentCallbacks, Guardrails     |
| 思考模式       | Day 20   | strategic-solver     | BuiltInPlanner, ThinkingConfig |
| 串流回應       | Day 23   | streaming-agent      | SSE                            |
| Google Search  | Day 7    | grounding-agent      | Grounding                      |
| Code Execution | Day 21   | code-calculator      | BuiltInCodeExecutor            |
| 檔案處理       | Day 26   | artifact-agent       | Artifact Tool                  |
| Agentic RAG    | Day 45   | policy-navigator     | Gemini File Search             |
| Vision API     | Day 28   | vision-catalog-agent | Vision API                     |
| Redis Session  | Day 58   | custom-session-agent | BaseSessionService             |
| 監控           | Day 47   | math-agent-otel      | OpenTelemetry                  |
| 部署           | Day 31   | production-agent     | Cloud Run                      |

---

## Week 1: 核心 Agent 建構

**目標**: 建立基本的對話 Agent

- [ ] 環境設定與專案初始化
- [ ] 建立基礎 Agent (參考 hello-agent)
- [ ] 實作 Session State Management
- [ ] 實作思考模式切換功能
- [ ] 實作安全防護層 (Guardrails)
- [ ] 簡易 CLI 測試介面

**參考專案**:

- Day 16: hello-agent
- Day 17: personal-tutor (State Management)
- Day 18: content-moderator (Callbacks & Guardrails)
- Day 20: strategic-solver (Thinking Mode)

## Week 2: 串流與持久化

**目標**: 實現串流回應與對話持久化

- [ ] 實作 SSE 串流回應
- [ ] SQLite 對話歷史儲存
- [ ] 會話管理（create/load/list sessions）
- [ ] 建立測試框架與評估數據集
- [ ] 實作單元測試與整合測試
- [ ] 基礎測試套件

**參考專案**:

- Day 23: streaming-agent
- Day 58: custom-session-agent
- Day 19: support-agent (Testing & Evaluation)

---

## Week 2.5: 知識庫整合 (Agentic RAG) 📚

**目標**: 實現文檔問答與知識管理

- [ ] Gemini File Search API 整合
- [ ] 文檔上傳與索引管理
- [ ] 引用來源追蹤與顯示（Citations）
- [ ] 文檔清單與刪除功能
- [ ] 多文檔聯合查詢測試
- [ ] RAG 評估測試案例

**參考專案**:

- Day 45: policy-navigator (File Search RAG)
- Day 26: artifact-agent (File Management)

**預期成果**:

- ✅ 支援 PDF/Word/Markdown/TXT 上傳
- ✅ 自動提取引用來源與頁碼
- ✅ 文檔管理介面（列表/刪除）
- ✅ RAG 測試覆蓋率 > 80%
