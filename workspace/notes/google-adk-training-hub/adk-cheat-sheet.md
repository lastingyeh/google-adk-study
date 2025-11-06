# ADK Cheat Sheet (ADK 備忘單)

**來源**: [google/adk-python](https://github.com/google/adk-python) (ADK 1.16+)

**最後更新**: 2025 年 10 月

---

## 1. Agent Creation (5 Minutes) (代理建立)

### Minimal Agent (最小代理)
```python
# 匯入 Agent 類別
from google.adk.agents import Agent

# 建立一個基本的 Agent
root_agent = Agent(
  name="assistant",  # 代理名稱
  model="gemini-2.0-flash",  # 使用的模型
  instruction="You are a helpful assistant."  # 給予代理的指令
)
```

### Agent with Description (帶有描述的代理)
```python
# 建立一個帶有描述的 Agent，用於執行數學計算
root_agent = Agent(
  name="calculator",  # 代理名稱
  model="gemini-2.0-flash",  # 使用的模型
  description="Performs mathematical calculations",  # 描述代理的功能
  instruction="Use tools to compute calculations accurately."  # 指示代理使用工具精確計算
)
```

### Agent with Tools (帶有工具的代理)
```python
# 定義一個工具函數，用於將兩個數字相加
def add_numbers(a: int, b: int) -> dict:
  """Add two numbers together."""
  return {
    "status": "success",
    "result": a + b,
    "report": f"{a} + {b} = {a + b}"
  }

# 建立一個帶有工具的 Agent
root_agent = Agent(
  name="calculator",  # 代理名稱
  model="gemini-2.0-flash",  # 使用的模型
  instruction="Help users with calculations.",  # 指示代理協助使用者計算
  tools=[add_numbers]  # 將工具函數列表傳遞給代理
)
```

### Agent with Output Key (Auto-save) (帶有輸出鍵的代理 - 自動儲存)
```python
# 建立一個代理，其回應會自動儲存到狀態中
root_agent = Agent(
  name="analyzer",  # 代理名稱
  model="gemini-2.0-flash",  # 使用的模型
  instruction="Analyze the provided data.",  # 指示代理分析提供的資料
  output_key="analysis_result"  # 將回應儲存到狀態的 'analysis_result' 鍵中
)
```

---

## 2. Running Agents (執行代理)

### CLI (Web Interface - Recommended for Development) (命令列介面 - 建議用於開發)
```bash
# 啟動開發者 UI，其中包含代理下拉式選單
adk web

# 在 http://localhost:8000 的 UI 中從下拉式選單選擇代理
```

### Programmatic Execution (程式化執行)
```python
from google.adk.runners import Runner
from google.genai import types

async def run_agent_example():
  runner = Runner(agent=root_agent)
  session = await runner.session_service.create_session(
    app_name="my_app",
    user_id="user_123"
  )
  new_message = types.Content(
    role="user",
    parts=[types.Part(text="Hello!")]
  )
  async for event in runner.run_async(
    user_id="user_123",
    session_id=session.id,
    new_message=new_message
  ):
    if event.content and event.content.parts:
      print(event.content.parts[0].text)
```

---

## 3. Workflow Decision Tree (工作流程決策樹)

**選擇正確的工作流程類型：**

```mermaid
graph TD
  A[需要多個任務嗎？] -->|否| B(單一 Agent)
  A -->|是| C{順序是否重要？}
  C -->|是| D{需要迭代嗎？}
  D -->|是| E(Loop Agent)
  D -->|否| F(Sequential Agent)
  C -->|否| G(Parallel Agent)
```

---

## 4. Workflow Patterns (工作流程模式)

### Sequential Agent (One After Another) (循序代理 - 依序執行)
**使用時機**: 任務必須按順序執行，且每個任務都需要前一個任務的輸出。
```python
from google.adk.agents import SequentialAgent

# 研究代理
research = Agent(
  name="research",
  instruction="Research the topic.",
  output_key="findings"
)

# 寫作代理
write = Agent(
  name="write",
  instruction="Write article based on: {findings}",
  output_key="article"
)

# 循序工作流程
pipeline = SequentialAgent(
  name="BlogPipeline",
  sub_agents=[research, write],
  description="Research then write blog"
)
root_agent = pipeline
```

### Parallel Agent (Simultaneous Execution) (平行代理 - 同時執行)
**使用時機**: 任務彼此獨立，且速度很重要。
```python
from google.adk.agents import ParallelAgent

# 搜尋航班、飯店、活動的代理
search_flights = Agent(name="flights", instruction="...")
search_hotels = Agent(name="hotels", instruction="...")
find_activities = Agent(name="activities", instruction="...")

# 平行搜尋
travel_search = ParallelAgent(
  name="TravelSearch",
  sub_agents=[search_flights, search_hotels, find_activities],
  description="Search flights, hotels, activities in parallel"
)
root_agent = travel_search
```

### Loop Agent (Iterative Refinement) (循環代理 - 迭代優化)
**使用時機**: 品質優先於速度，需要迭代（寫作 → 評論 → 改進）。
```python
from google.adk.agents import LoopAgent

# 寫草稿的代理
write_draft = Agent(name="writer", instruction="Write essay...")

# 結束循環的工具
def exit_loop(tool_context):
  """Call when done."""
  tool_context.actions.end_of_agent = True
  return {"status": "success"}

# 評論代理
critic = Agent(
  name="critic",
  instruction="Critique the draft. If perfect say: APPROVE",
  output_key="feedback"
)

# 改進代理
improve = Agent(
  name="improver",
  instruction="Improve based on feedback: {feedback}. "
        "If feedback says APPROVE, call exit_loop.",
  tools=[exit_loop],
  output_key="improved_draft"
)

# 優化循環
refinement_loop = LoopAgent(
  sub_agents=[critic, improve],
  max_iterations=5
)
root_agent = refinement_loop
```

### Fan-Out/Gather (Parallel + Sequential) (分散/收集 - 平行 + 循序)
**使用時機**: 從多個來源收集資料，然後進行綜合。
```python
from google.adk.agents import ParallelAgent, SequentialAgent

# 平行收集資料
parallel_search = ParallelAgent(
  name="DataGathering",
  sub_agents=[web_searcher, database_lookup, api_query]
)

# 循序綜合結果
synthesizer = Agent(
  name="synthesizer",
  instruction="Combine the gathered data into summary"
)

# 結合：平行收集 + 循序綜合
fan_out_gather = SequentialAgent(
  name="FanOutGather",
  sub_agents=[parallel_search, synthesizer]
)
root_agent = fan_out_gather
```

---

## 5. Tool Patterns (工具模式)

### Function Tool (Most Common) (函式工具 - 最常見)
```python
def search_database(query: str, tool_context) -> dict:
  """
  Search database for information.
  Args:
    query: Search query string
  Returns:
    Dict with status, report, and data
  """
  try:
    results = db.search(query)
    return {
      "status": "success",
      "report": f"Found {len(results)} results",
      "data": results,
      "result_count": len(results)
    }
  except Exception as e:
    return {
      "status": "error",
      "error": str(e),
      "report": f"Search failed: {str(e)}"
    }
agent = Agent(..., tools=[search_database])
```

### Tool Return Format (Standard) (工具回傳格式 - 標準)
```json
// ✅ 正確格式
{
  "status": "success" or "error",     // 必要
  "report": "Human-readable message",  // 必要
  "data": "actual_result",               // 可選
  "count": 42                          // 可選自訂欄位
}

// ❌ 錯誤格式
{
  "result": "just_the_data",          // 缺少 status/report
  "error_code": 500                   // 非結構化
}
```

### OpenAPI Tool (REST APIs)
```python
from google.adk.tools.openapi_toolset import OpenAPIToolset

# 從 OpenAPI 規格建立工具集
toolset = OpenAPIToolset(
  spec="https://api.example.com/openapi.json",
  auth_config={"type": "bearer", "token": "your-token"}
)
agent = Agent(..., tools=[toolset])
```

### MCP Tool (Filesystem, Database) (MCP 工具 - 檔案系統、資料庫)
```python
from google.adk.tools.mcp_toolset import MCPToolset

# 檔案系統存取
fs_tools = MCPToolset(server="filesystem", path="/allowed/path")

# PostgreSQL 資料庫
db_tools = MCPToolset(
  server="postgresql",
  connection_string="postgresql://user:pass@host/db"
)
agent = Agent(..., tools=[fs_tools, db_tools])
```

### Built-in Tools (內建工具)
```python
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.code_execution_tool import CodeExecutionTool

agent = Agent(
  ...,
  tools=[
    GoogleSearchTool(),        # 網路搜尋
    CodeExecutionTool(),       # Python 執行
  ]
)
```

---

## 6. State Management (狀態管理)

### State Scopes Quick Reference (狀態範圍快速參考)

| Scope | Persistence | Use Case | Example |
| :--- | :--- | :--- | :--- |
| `None` (session) | SessionService dependent | Current task | `state['counter'] = 5` |
| `user:` | Persistent across sessions | User preferences | `state['user:language'] = 'en'` |
| `app:` | Global, all users | App settings | `state['app:version'] = '1.0'` |
| `temp:` | **Never persisted** | Temp calculations | `state['temp:score'] = 85` |

### Using State in Tools (在工具中使用狀態)
```python
def save_preference(language: str, tool_context) -> dict:
  # 持久化使用者偏好
  tool_context.state['user:language'] = language
  # 會話級別資料
  tool_context.state['current_language'] = language
  # 臨時資料
  tool_context.state['temp:calculation'] = len(language)
  return {"status": "success", "report": "Preferences saved"}

def get_user_history(tool_context) -> dict:
  # 讀取使用者持久化資料
  language = tool_context.state.get('user:language', 'en')
  history = tool_context.state.get('user:history', [])
  return {
    "status": "success",
    "report": f"User language: {language}",
    "data": {"language": language, "history": history}
  }
```

### State in Agent Instructions (在代理指令中使用狀態)
```python
agent = Agent(
  name="personalized_assistant",
  instruction=(
    "You are helping a user.\n"
    "User's preferred language: {user:language}\n"
    "Current topic: {current_topic}\n"
    "\n"
    "Respond in their preferred language and about the topic."
  )
)
```

### State Best Practices (狀態最佳實踐)
```python
# ✅ 執行：使用適當的範圍
state['user:preferences'] = {...}      # 使用者級別持久化
state['current_task'] = 'pending'       # 會話級別
state['temp:calculation'] = 42          # 僅臨時

# ❌ 不要：錯誤的範圍
state['preferences'] = {...}            # 應為 user:preferences
state['user:temp_var'] = x              # 應為 temp:temp_var

# ✅ 執行：使用預設值安全讀取
language = state.get('user:language', 'en')

# ❌ 不要：不安全的存取
language = state['user:language']  # 如果未設定會失敗！

# ✅ 執行：更新前檢查
if 'user:history' not in state:
  state['user:history'] = []
state['user:history'].append(item)

# ✅ 執行：使用 output_key 自動儲存
agent = Agent(..., output_key="task_result")
# 回應會自動儲存到 state['task_result']
```

---

## 7. Common Patterns & Examples (常見模式與範例)

### Retry Logic (重試邏輯)
```python
from typing import Any
import time

def retry_api_call(
  endpoint: str,
  retries: int = 3,
  tool_context = None) -> dict:
  """Call API with retry logic."""
  for attempt in range(retries):
    try:
      response = requests.get(endpoint, timeout=5)
      response.raise_for_status()
      return {
        "status": "success",
        "report": f"Success on attempt {attempt + 1}",
        "data": response.json()
      }
    except requests.RequestException as e:
      if attempt == retries - 1:
        return {
          "status": "error",
          "error": str(e),
          "report": f"Failed after {retries} attempts"
        }
      time.sleep(2 ** attempt)  # 指數退避
  return {"status": "error", "report": "Unknown error"}
```

### Caching (快取)
```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_cached_data(key: str) -> str:
  """Cached data lookup."""
  # 昂貴的操作
  return fetch_from_api(key)

def cache_operation(query: str, tool_context) -> dict:
  """Tool with TTL-based caching."""
  cache_key = f"search:{query}"
  # 檢查是否在快取中
  if cache_key in tool_context.state:
    cached_value, timestamp = tool_context.state[cache_key]
    if time.time() - timestamp < 300:  # 5 分鐘 TTL
      return {
        "status": "success",
        "report": "Result from cache",
        "data": cached_value
      }
  # 全新查詢
  result = search_api(query)
  tool_context.state[cache_key] = (result, time.time())
  return {
    "status": "success",
    "report": "Fresh result",
    "data": result
  }
```

### Validation (驗證)
```python
def validate_input(user_input: str, tool_context) -> dict:
  """Validate and sanitize user input."""
  # 長度檢查
  if not user_input or len(user_input) > 1000:
    return {
      "status": "error",
      "report": "Input must be 1-1000 characters"
    }
  # 檢查注入模式
  dangerous_patterns = ['DROP TABLE', '<script>', '{{', ']]']
  for pattern in dangerous_patterns:
    if pattern.lower() in user_input.lower():
      return {
        "status": "error",
        "report": "Input contains invalid patterns"
      }
  # 清理
  clean_input = user_input.strip()
  return {
    "status": "success",
    "report": "Input validated",
    "data": clean_input
  }
```

---

## 8. Environment Setup (環境設定)

### Authentication (驗證)
```bash
# Google AI Studio (開發)
export GOOGLE_GENAI_USE_VERTEXAI=false
export GOOGLE_API_KEY="your-api-key"

# Vertex AI (生產)
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"

# 驗證
gcloud auth application-default login
```

### Model Selection (模型選擇)
```python
# 快速回應，較低成本
Agent(model="gemini-2.0-flash")

# 高品質，推理能力強
Agent(model="gemini-2.0-flash-thinking")

# 上一代模型
Agent(model="gemini-1.5-flash")
Agent(model="gemini-1.5-pro")

# 其他 LLM (如果支援)
Agent(model="claude-3.5-sonnet")  # Anthropic
Agent(model="gpt-4-turbo")         # OpenAI
```

---

## 9. Testing & Debugging (測試與除錯)

### Unit Test Template (單元測試範本)
```python
import pytest
from google.adk.agents import Agent
from google.adk.runners import Runner

class TestMyAgent:
  @pytest.fixture
  def agent(self):
    return Agent(
      name="test_agent",
      model="gemini-2.0-flash",
      instruction="Test instruction"
    )

  @pytest.mark.asyncio
  async def test_basic_response(self, agent):
    runner = Runner(agent=agent)
    session = await runner.session_service.create_session(
      app_name="test_app",
      user_id="test_user"
    )

    from google.genai import types
    message = types.Content(
      role="user",
      parts=[types.Part(text="Hello")]
    )

    responses = []
    async for event in runner.run_async(
      user_id="test_user",
      session_id=session.id,
      new_message=message
    ):
      if event.content and event.content.parts:
        responses.append(event.content.parts[0].text)

    assert len(responses) > 0
    assert "hello" in responses[-1].lower()
```

### Run Tests (執行測試)
```bash
# 所有測試
pytest tests/ -v

# 包含覆蓋率報告
pytest tests/ --cov=src --cov-report=html

# 特定測試
pytest tests/test_agent.py::TestMyAgent::test_basic_response -v

# 顯示 print 語句
pytest tests/ -s
```

### Debugging in Web UI (在 Web UI 中除錯)
1.  **啟動**: `adk web`
2.  **開啟**: `http://localhost:8000`
3.  從下拉式選單中選擇代理
4.  輸入訊息
5.  點擊 "Events" 標籤查看：
  *   代理執行流程
  *   工具呼叫
  *   狀態變更
  *   錯誤

---

## 10. CLI Commands (命令列指令)

### Development (開發)
```bash
adk web                    # 啟動開發 UI
adk web --debug           # 除錯模式
adk web --port 8080       # 自訂埠號
```

### Deployment (部署)
```bash
# Cloud Run
adk deploy cloud_run \
  --project my-project \
  --region us-central1 \
  --service-name my-agent

# Vertex AI Agent Engine
adk deploy agent_engine \
  --project my-project \
  --region us-central1

# GKE
adk deploy gke \
  --project my-project \
  --cluster my-cluster
```

---

## 11. Production Checklist (生產環境檢查清單)

### Before Deployment (部署前)
*   [ ] 所有測試通過 (100% 關鍵)
*   [ ] 所有工具失敗的錯誤處理
*   [ ] 所有工具的輸入驗證
*   [ ] 設定速率限制
*   [ ] 密鑰儲存在 Secret Manager (非硬式編碼)
*   [ ] 設定日誌和監控
*   [ ] 效能基準符合 SLA
*   [ ] 完成安全性審查
*   [ ] 文件完整

### During Deployment (部署期間)
*   [ ] 分階段推出 (開發 → 預備 → 生產)
*   [ ] 設定健康檢查
*   [ ] 啟用自動擴展
*   [ ] 設定警報
*   [ ] 準備好回滾計畫
*   [ ] 安排好輪值

### After Deployment (部署後)
*   [ ] 監控錯誤率
*   [ ] 檢查回應時間
*   [ ] 審查日誌以找出問題
*   [ ] 衡量 SLI/SLO 合規性
*   [ ] 收集使用者回饋
*   [ ] 計畫優化

---

## 12. Best Practices Checklists (最佳實踐檢查清單)

### Agent Design (代理設計)
*   [ ] 單一職責 (一個明確的目的)
*   [ ] 描述性名稱 (`content_writer` 而非 `agent1`)
*   [ ] 清晰、具體的指令 (非模糊)
*   [ ] 帶有實用訊息的錯誤處理
*   [ ] 適合任務的模型 (平衡速度/品質)

### Tool Development (工具開發)
*   [ ] 回傳 `{"status", "report", "data"}`
*   [ ] Docstring 解釋工具的功能
*   [ ] 驗證所有輸入
*   [ ] 優雅地處理錯誤
*   [ ] 冪等性 (可安全多次呼叫)

### State Management (狀態管理)
*   [ ] 使用正確的範圍 (`user:`, `temp:`, `app:`)
*   [ ] 描述性的鍵名
*   [ ] 使用 `.get()` 和預設值安全讀取
*   [ ] 清理舊的/未使用的狀態

### Performance (效能)
*   [ ] 對於獨立任務使用 `ParallelAgent`
*   [ ] 快取昂貴的操作
*   [ ] 對於長輸出使用串流
*   [ ] 選擇合適的模型 (flash vs pro)
*   [ ] 監控回應時間

### Security (安全性)
*   [ ] 驗證所有使用者輸入
*   [ ] 使用前進行清理
*   [ ] 絕不硬式編碼密鑰
*   [ ] 在生產環境中使用 Secret Manager
*   [ ] 記錄安全性事件

---

## 13. Quick Troubleshooting (快速疑難排解)

| Problem | Solution |
| :--- | :--- |
| Agent doesn't use tool | Check docstring and parameter names |
| State not persisting | Use persistent SessionService |
| Slow responses | Use `gemini-2.0-flash`, enable caching |
| Memory errors | Reduce context, use streaming |
| Tool not found | Check `adk web` - make sure agent is discoverable |
| Import errors | Run `pip install -e .` in tutorial dir |
| Auth fails | Check `GOOGLE_API_KEY` and `GOOGLE_CLOUD_PROJECT` |

---

## 14. Comparison Tables (比較表)

### Agent Types (代理類型)

| Type | Execution | Use Case |
| :--- | :--- | :--- |
| `Agent` | Single LLM call | Basic tasks, conversations |
| `SequentialAgent` | One after another | Pipelines, step-by-step |
| `ParallelAgent` | All simultaneous | Independent tasks, speed |
| `LoopAgent` | Repeated until done | Refinement, iteration |

### Tool Types (工具類型)

| Type | Use | Complexity |
| :--- | :--- | :--- |
| Function | Python functions | Low |
| OpenAPI | REST APIs | Medium |
| MCP | Standard protocol | High |
| Built-in | Google tools | Low |

### State Scopes (狀態範圍)

| Scope | Persistence | Speed | Sharing |
| :--- | :--- | :--- | :--- |
| None | Session-dependent | Fast | Agents in invocation |
| `user:` | Across sessions | Medium | Per user |
| `app:` | Global | Slow | All users |
| `temp:` | Never | Fast | Invocation only |

---

## 15. Quick Links & Resources (快速連結與資源)

*   **Official Docs**: [google.github.io/adk-docs](https://google.github.io/adk-docs)
*   **GitHub**: [github.com/google/adk-python](https://github.com/google/adk-python)
*   **API Reference**: [google/adk-python API docs](https://github.com/google/adk-python)
*   **Tutorials**: [Tutorial Index](/adk_training/docs/tutorial_index)
*   **Mental Models**: [Agent Architecture](/adk_training/docs/agent-architecture)
*   **Glossary**: [ADK Glossary](/adk_training/docs/glossary)
