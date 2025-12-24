# NotChatGPT - 專案規劃文件

## 📋 專案概述

使用 Google ADK + Gemini 2.0 建構一個類 ChatGPT 的對話式 AI 系統，具備多輪對話、工具呼叫、串流回應、思考模式切換等核心功能。

## 🎯 核心需求分析

### 1. 基礎對話能力

#### 功能需求

- ✅ 多輪對話支援
- ✅ 上下文記憶管理（Session State）
- ✅ 串流式回應（SSE）
- ✅ 對話歷史持久化
- ✅ 思考模式切換（Thinking Mode Toggle）

#### 技術實現

- **Session Management**: 參考 Day 17 (personal-tutor)
- **Streaming**: 參考 Day 23 (streaming-agent)
- **Memory**: 使用 ADK Session State with user/app/temp 前綴
- **Thinking Mode**: 參考 Day 20 (strategic-solver) 使用 BuiltInPlanner 與 ThinkingConfig

---

### 2. 工具整合能力

#### 功能需求

- ✅ 網路搜尋（Google Search Grounding）
- ✅ 程式碼執行（Code Execution）
- ✅ 檔案處理（Upload/Analysis）
- ⬜ 圖片分析（Multimodal Vision）

#### 技術實現

- **Google Search**: 參考 Day 7 (grounding-agent)
- **Code Execution**: 參考 Day 21 (code-calculator)
- **File Handling**: 參考 Day 26 (artifact-agent)

---

### 3. 使用者介面

#### 功能需求

- ✅ Web 介面（React/Next.js）
- ✅ 即時串流顯示
- ✅ 對話管理（新增、刪除、切換）
- ✅ Markdown 渲染
- ⬜ 程式碼高亮
- ✅ **模式切換控制（思考模式 💭 / 標準模式 💬）**

#### 技術實現

- **Frontend Framework**:
  - Option A: React Vite + AG-UI Protocol (Day 40)
  - Option B: Next.js 15 + CopilotKit (Day 39)
- **Streaming UI**: SSE with EventSource API
- **Mode Selector**: Toggle Switch + 模式狀態顯示

---

### 4. 生產環境考量

#### 功能需求

- ✅ 狀態持久化（Redis/PostgreSQL）
- ✅ 錯誤處理與重試
- ✅ 監控與日誌（OpenTelemetry）
- ⬜ 速率限制與配額管理

#### 技術實現

- **Session Storage**: 參考 Day 58 (custom-session-agent)
- **Monitoring**: 參考 Day 47 (math-agent-otel)
- **Deployment**: 參考 Day 31 (Cloud Run/Agent Engine)

---

## 🏗️ 技術架構設計

### 系統架構圖

```text
┌─────────────────┐
│   Frontend      │
│  React Vite     │ ◄─── AG-UI Protocol
│  + AG-UI SDK    │
│  + Mode Toggle  │ ◄─── 思考模式切換器 (💭/💬)
└────────┬────────┘
         │ HTTP/SSE
         │ thinking_mode: bool
         ▼
┌─────────────────┐
│   Backend API   │
│   FastAPI       │
│  + Mode Config  │ ◄─── ThinkingConfig 動態設定
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   ADK Agent     │◄────►│  Gemini 2.0  │
│  Core Engine    │      │  Flash/Pro   │
│ + BuiltInPlanner│◄────►│  + Thinking  │
└────────┬────────┘      └──────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ Tools  │ │Session │
│Google  │ │ Store  │
│Search  │ │ SQLite │
│Code    │ │  /     │
│Execute │ │ Redis  │
└────────┘ └────────┘
```

### 技術棧選型

| 層級         | 開發環境         | 生產環境               |
| ------------ | ---------------- | ---------------------- |
| **前端**     | React Vite       | React Vite             |
| **後端**     | FastAPI + ADK    | FastAPI + ADK          |
| **模型**     | Gemini 2.0 Flash | Gemini 2.0 Flash       |
| **會話存儲** | SQLite           | Redis + PostgreSQL     |
| **部署**     | Local (adk web)  | Cloud Run              |
| **監控**     | Console Logs     | OpenTelemetry + Jaeger |

---

## 📅 實現路線圖

### Phase 1: 基礎對話系統（Week 1-2）

#### Week 1: 核心 Agent 建構

**目標**: 建立基本的對話 Agent

- [ ] 環境設定與專案初始化
- [ ] 建立基礎 Agent (參考 hello-agent)
- [ ] 實作 Session State Management
- [ ] **實作思考模式切換功能**
- [ ] 簡易 CLI 測試介面

**參考專案**:

- Day 16: hello-agent
- Day 17: personal-tutor (State Management)
- **Day 20: strategic-solver (Thinking Mode)**

**產出**:

```python
# agents/conversation_agent.py
- Basic Agent with Gemini 2.0 Flash
- Session state with user/app/temp prefixes
- Simple memory management
- Thinking mode configuration (thinking_mode: bool)
- BuiltInPlanner with ThinkingConfig
```

#### Week 2: 串流與持久化

**目標**: 實現串流回應與對話持久化

- [ ] 實作 SSE 串流回應
- [ ] SQLite 對話歷史儲存
- [ ] 會話管理（create/load/list sessions）
- [ ] 基礎測試套件

**參考專案**:

- Day 23: streaming-agent
- Day 58: custom-session-agent

**產出**:

```python
# agents/streaming_agent.py
- SSE response streaming
- SQLite session persistence
- Session CRUD operations
```

---

### Phase 2: 工具整合與 UI（Week 3-4）

#### Week 3: 工具整合

**目標**: 整合核心工具能力

- [ ] Google Search Grounding
- [ ] Code Execution (BuiltInCodeExecutor)
- [ ] File Upload/Download (Artifact Tool)
- [ ] 工具使用測試與調優

**參考專案**:

- Day 7: grounding-agent
- Day 21: code-calculator
- Day 26: artifact-agent

**產出**:

```python
# tools/
- google_search.py
- code_executor.py
- file_handler.py
```

#### Week 4: Web UI 建構

**目標**: 建立前端介面

- [ ] React Vite 專案設定
- [ ] AG-UI Protocol 整合
- [ ] SSE 串流顯示
- [ ] 對話管理 UI (new/load/delete)
- [ ] Markdown 渲染
- [ ] **模式切換控制元件（Toggle Switch + 狀態指示器）**

**參考專案**:

- Day 40: data-analysis-dashboard (React Vite + AG-UI)

**產出**:

```typescript
// frontend/
- ConversationView.tsx
- MessageList.tsx
- InputBox.tsx
- SessionManager.tsx
- ModeSelector.tsx  // 新增：思考模式切換器
```

---

### Phase 3: 生產優化（Week 5-6）

#### Week 5: 進階功能

**目標**: 提升系統可靠性

- [ ] Redis Session Storage
- [ ] 錯誤處理與重試機制
- [ ] 上下文壓縮 (Context Compaction)
- [ ] 速率限制與配額

**參考專案**:

- Day 58: custom-session-agent (Redis)
- Day 55: context-compaction-agent

**產出**:

```python
# services/
- redis_session_service.py
- error_handler.py
- context_compactor.py
```

#### Week 6: 部署與監控

**目標**: 準備生產環境

- [ ] OpenTelemetry 整合
- [ ] Cloud Run 部署配置
- [ ] 性能優化與壓測
- [ ] 文檔撰寫

**參考專案**:

- Day 47: math-agent-otel (OpenTelemetry)
- Day 31: production-agent (Deployment)

**產出**:

```yaml
# deployment/
- Dockerfile
- cloudbuild.yaml
- otel-config.yaml
```

---

## 🎨 最小可行產品 (MVP) 定義

### 核心功能範圍

#### ✅ 必須包含 (P0)

1. **基礎對話**
   - 多輪對話
   - 上下文記憶（至少 5 輪）
   - 串流回應

2. **工具能力**
   - Google Search
   - Code Execution

3. **使用者介面**
   - Web 聊天介面
   - 新增對話
   - 顯示對話歷史

4. **持久化**
   - SQLite 會話儲存
   - 對話歷史查詢

#### 🔄 下一版本 (P1)

1. 檔案上傳與分析
2. 圖片辨識（Multimodal）
3. Redis Session Storage
4. OpenTelemetry 監控

#### 📋 未來規劃 (P2)

1. 多使用者系統
2. 使用者偏好設定
3. 對話分享功能
4. 多語言支援

---

## 📊 技術決策記錄

### 1. 為何選擇 React Vite 而非 Next.js？

**決策**: React Vite

**理由**:

- ✅ 更輕量，適合 MVP
- ✅ 不需要 SSR（Server-Side Rendering）
- ✅ 更快的開發體驗（HMR）
- ✅ 參考 Day 40 有完整的 AG-UI 整合範例

**權衡**:

- ❌ 無內建 API Routes（需額外設定 FastAPI）
- ❌ 無 SSR 優化

---

### 2. 為何使用 SQLite 而非 PostgreSQL（開發階段）？

**決策**: SQLite (Dev) → PostgreSQL (Prod)

**理由**:

- ✅ 零配置，快速啟動
- ✅ 本地開發無需額外服務
- ✅ 易於遷移至 PostgreSQL

**遷移計劃**:

```python
# 使用 SQLAlchemy ORM，抽象化資料庫
# 僅需修改連接字串即可切換
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sessions.db")
```

---

### 3. 為何使用 Gemini 2.0 Flash？

**決策**: Gemini 2.0 Flash

**理由**:

- ✅ 低延遲（< 1s）
- ✅ 成本效益高
- ✅ 內建思考能力（Thinking）
- ✅ 原生支援 Code Execution

**效能比較**:

| 模型 | 延遲 | 成本 | 推理能力 |
| ----- | ---- | ----- | -------- |
| Flash | ⚡ 快 | 💰 低 | ⭐⭐⭐ |
| Pro | 🐢 慢 | 💰💰 高 | ⭐⭐⭐⭐⭐ |

---

### 4. 思考模式 vs 標準模式的使用時機？

**決策**: 提供使用者可切換的模式選項

**思考模式 (💭) 適用場景**:

- ✅ 複雜邏輯推理（數學證明、程式碼除錯）
- ✅ 多步驟問題解決（策略規劃、方案比較）
- ✅ 需要深度分析的任務（資料分析、文獻綜述）
- ✅ 程式碼優化與重構建議

**標準模式 (💬) 適用場景**:

- ✅ 快速回答簡單問題
- ✅ 閒聊與日常對話
- ✅ 資訊查詢（天氣、新聞）
- ✅ 低延遲需求場景

**效能與成本比較**:

| 模式 | 延遲 | Token 消耗 | 推理品質 | 適用場景 | 成本估算 |
| -------- | ------------- | ------------ | -------- | -------- | ----------- |
| 思考模式 | 🐢 較慢 (3-5s) | 💰💰 高 (+40%) | ⭐⭐⭐⭐⭐ | 複雜推理 | ~$0.0005/次 |
| 標準模式 | ⚡ 快 (<2s) | 💰 標準 | ⭐⭐⭐ | 一般對話 | ~$0.0004/次 |

**實作方式**:

```python
# 在 Agent 配置中動態切換思考模式
from google.genai.types import GenerateContentConfig, ThinkingConfig

# 從 Session State 讀取使用者偏好
thinking_enabled = session_state.get("user:thinking_mode", False)

config = GenerateContentConfig(
    temperature=0.7,
    thinking=ThinkingConfig(
        include_thoughts=thinking_enabled,
        # 控制思考過程是否顯示給使用者
    ) if thinking_enabled else None,
)

# 在 Agent 初始化時設定
agent = Agent(
    model="gemini-2.0-flash-exp",
    config=config,
    planner=BuiltInPlanner() if thinking_enabled else None,
)
```

**UI 設計建議**:

1. **Toggle Switch 控制元件**:

   ```tsx
   <ModeToggle 
     mode={thinkingMode ? 'thinking' : 'standard'}
     onChange={(enabled) => setThinkingMode(enabled)}
   />
   ```

2. **模式狀態指示器**:
   - 思考模式：顯示 "💭 深度思考中..."
   - 標準模式：顯示 "💬 快速回應"

3. **智慧建議提示**:
   - 當使用者輸入複雜問題時，自動提示：
     > "💡 這個問題較為複雜，建議開啟思考模式以獲得更深入的分析"

**自動模式切換邏輯**:

```python
# 啟發式判斷：根據問題複雜度自動建議模式
def should_suggest_thinking_mode(user_input: str) -> bool:
    """判斷是否應建議使用思考模式"""
    
    # 關鍵詞檢測
    thinking_keywords = [
        "為什麼", "如何", "解釋", "分析", "比較",
        "推理", "證明", "步驟", "計畫", "策略",
        "優化", "重構", "除錯", "評估", "建議"
    ]
    
    # 長度檢測（超過 50 字可能較複雜）
    is_long_query = len(user_input) > 50
    
    # 包含程式碼片段
    has_code = "```" in user_input or "def " in user_input
    
    # 包含數學符號
    has_math = any(op in user_input for op in ["=", "+", "-", "*", "/", "^"])
    
    keyword_match = any(kw in user_input for kw in thinking_keywords)
    
    return keyword_match or is_long_query or has_code or has_math
```

**思考過程可視化**:

```typescript
// 前端顯示思考過程
interface ThinkingProcess {
  step: number;
  thought: string;
  timestamp: Date;
}

function ThinkingDisplay({ thoughts }: { thoughts: ThinkingProcess[] }) {
  return (
    <div className="thinking-process">
      <h4>💭 思考過程</h4>
      {thoughts.map((t, i) => (
        <div key={i} className="thought-step">
          <span className="step-number">步驟 {t.step}</span>
          <p>{t.thought}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔧 開發指南

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
│   │   └── file_handler.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py
│   │   └── redis_session_service.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── mode_config.py  # 新增：思考模式配置
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
│   │   │   └── ModeSelector.tsx  # 新增：模式切換器
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_session.py
├── deployment/
│   ├── Dockerfile
│   └── cloudbuild.yaml
├── docs/
│   ├── API.md
│   └── DEPLOYMENT.md
├── planning.md (本檔案)
└── README.md
```

---

### 環境設定

```bash
# 後端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 設定環境變數
export GOOGLE_API_KEY="your-api-key"
export PROJECT_ID="your-project-id"

# 前端
cd frontend
npm install
```

---

### 開發工作流程

#### 1. 後端開發

```bash
# 啟動 ADK Web 伺服器
cd backend
adk web agents/conversation_agent.py

# 或使用 FastAPI
uvicorn main:app --reload
```

#### 2. 前端開發

```bash
cd frontend
npm run dev
```

#### 3. 測試

```bash
# 單元測試
pytest tests/

# 整合測試
pytest tests/ -m integration

# 評估測試
adk evaluate agents/conversation_agent.py --eval-set tests/eval_set.json
```

---

## 📚 參考資源對照表

| 功能模組       | 參考 Day | 專案名稱                | 核心技術                       |
| -------------- | -------- | ----------------------- | ------------------------------ |
| 基礎 Agent     | Day 16   | hello-agent             | Agent, Root                    |
| 狀態管理       | Day 17   | personal-tutor          | Session State                  |
| 思考模式       | Day 20   | strategic-solver        | BuiltInPlanner, ThinkingConfig |
| 串流回應       | Day 23   | streaming-agent         | SSE                            |
| Google Search  | Day 7    | grounding-agent         | Grounding                      |
| Code Execution | Day 21   | code-calculator         | BuiltInCodeExecutor            |
| 檔案處理       | Day 26   | artifact-agent          | Artifact Tool                  |
| React UI       | Day 40   | data-analysis-dashboard | React Vite + AG-UI             |
| Redis Session  | Day 58   | custom-session-agent    | BaseSessionService             |
| 監控           | Day 47   | math-agent-otel         | OpenTelemetry                  |
| 部署           | Day 31   | production-agent        | Cloud Run                      |

---

## 🚀 快速啟動檢查清單

### Phase 1 啟動（基礎對話）

- [ ] 已安裝 Python 3.11+
- [ ] 已安裝 Node.js 18+
- [ ] 已設定 `GOOGLE_API_KEY`
- [ ] 已設定 `PROJECT_ID`
- [ ] 已建立虛擬環境
- [ ] 已安裝 `google-genai-adk`
- [ ] 已測試 `adk web` 指令
- [ ] 已建立 `agents/conversation_agent.py`
- [ ] 已實作基本對話功能
- [ ] **已實作思考模式切換（BuiltInPlanner + ThinkingConfig）**
- [ ] CLI 測試通過

### Phase 2 啟動（工具 + UI）

- [ ] Google Search Tool 測試通過
- [ ] Code Execution 測試通過
- [ ] React 專案建立完成
- [ ] AG-UI Protocol 整合完成
- [ ] SSE 串流顯示正常
- [ ] 前後端連接成功

### Phase 3 啟動（生產優化）

- [ ] Redis 安裝與設定
- [ ] OpenTelemetry 整合
- [ ] Dockerfile 建立
- [ ] Cloud Run 部署測試
- [ ] 性能測試通過
- [ ] 文檔撰寫完成

---

## 🎯 成功指標

### MVP 達成標準

1. **功能完整性**: ✅ 所有 P0 功能實作完成
2. **效能指標**:
   - 首次回應延遲 < 2s
   - 串流回應 token/s > 50
   - 錯誤率 < 1%
3. **測試覆蓋率**: > 70%
4. **文檔完整性**: API 文檔 + 部署文檔

---

## 📝 常見問題 (FAQ)

### Q1: 為何不使用 LangChain？

**A**: ADK 是 Google 官方框架，與 Gemini 整合更深，且有以下優勢：

- 原生支援 Gemini 2.0 進階功能（Thinking、Grounding）
- 更好的 Agent Engine 整合
- 官方長期支援

### Q2: 如何處理長對話的 Context Window 限制？

**A**: 使用 Day 55 的 Context Compaction 技術：

```python
from google.genai.types import ContextCompactionConfig

config = ContextCompactionConfig(
    max_tokens=50000,
    keep_recent_messages=10
)
```

### Q3: 如何估算使用成本？

**A**: Gemini 2.0 Flash 定價（2024）：

- Input: $0.075 / 1M tokens
- Output: $0.30 / 1M tokens

假設每次對話 1000 tokens：

- 每次成本 ≈ $0.000375
- 1000 次對話 ≈ $0.375

---

### Q4: 思考模式會增加多少成本？

**A**: 思考模式會產生額外的內部推理 tokens，實測數據：

#### 範例場景：複雜數學問題

- 標準模式：
  - Input: 100 tokens
  - Output: 500 tokens
  - 成本: $0.000375
  
- 思考模式：
  - Input: 100 tokens
  - Thinking: 300 tokens (內部推理，不計費)
  - Output: 500 tokens
  - 成本: $0.000375 (相同！)

**重點**: Gemini 2.0 的內建思考功能 **不額外收費**，僅計算最終輸出 tokens！

**建議策略**：

1. 預設使用標準模式（快速回應）
2. 複雜問題時自動提示切換思考模式
3. 允許使用者隨時切換模式

---

### Q5: 如何判斷何時該使用思考模式？

**A**: 提供三種判斷策略：

**1. 關鍵詞檢測（啟發式）**:

```python
def should_use_thinking_mode(user_input: str) -> bool:
    thinking_indicators = [
        "為什麼", "如何", "解釋", "分析", "推理",
        "證明", "步驟", "優化", "比較", "評估"
    ]
    return any(keyword in user_input for keyword in thinking_indicators)
```

**2. 問題長度判斷**:

```python
# 超過 50 字的問題通常較複雜
if len(user_input) > 50:
    suggest_thinking_mode = True
```

**3. 內容類型檢測**:

```python
def detect_complex_content(user_input: str) -> bool:
    # 包含程式碼
    has_code = "```" in user_input or "def " in user_input
    
    # 包含數學公式
    has_math = any(sym in user_input for sym in ["=", "∫", "∑", "lim"])
    
    # 包含資料結構
    has_data = "json" in user_input.lower() or "[" in user_input
    
    return has_code or has_math or has_data
```

**最佳實踐**：結合三種策略 + 使用者手動控制

---

### Q6: 思考模式的思考過程該如何顯示？

**A**: 提供三種顯示策略：

**1. 完整顯示（適合教學場景）**:

```python
config = ThinkingConfig(
    include_thoughts=True,  # 顯示完整思考過程
)
```

**2. 摘要顯示（適合一般使用）**:

```tsx
// 前端僅顯示關鍵思考步驟
<ThinkingSummary 
  steps={["分析問題", "探索方案", "評估結果"]}
/>
```

**3. 隱藏顯示（適合追求速度）**:

```python
config = ThinkingConfig(
    include_thoughts=False,  # 僅返回最終結果
)
```

---

## 📅 版本歷史

| 版本 | 日期       | 變更內容                 |
| ---- | ---------- | ------------------------ |
| 0.1  | 2024-01-XX | 初始規劃                 |
| 0.2  | 2024-01-XX | 新增技術決策記錄         |
| 0.3  | 2024-01-XX | 新增思考模式切換功能規劃 |

---

## 👥 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送至分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

---

## 📄 授權

MIT License

---

**下一步**: 開始 Phase 1 - Week 1 的實作！🚀
