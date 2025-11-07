# Reference Guide (參考指南)

**Purpose (目的)**: 快速參考常見的 ADK 模式、組態和實作。

**Source of Truth (真實來源)**: [google/adk-python/src/google/adk/](https://github.com/google/adk-python/tree/main/src/google/adk/) (ADK 1.15) + production examples

---

## Table of Contents (目錄)

1.  [Agent Patterns (代理模式)](#agent-patterns-代理模式)
2.  [Tool Implementations (工具實作)](#tool-implementations-工具實作)
3.  [State Management (狀態管理)](#state-management-狀態管理)
4.  [Deployment Configurations (部署組態)](#deployment-configurations-部署組態)
5.  [Monitoring & Observability (監控與可觀測性)](#monitoring--observability-監控與可觀測性)
6.  [Testing Patterns (測試模式)](#testing-patterns-測試模式)
7.  [Configuration Templates (組態模板)](#configuration-templates-組態模板)
8.  [Common Issues & Solutions (常見問題與解決方案)](#common-issues--solutions-常見問題與解決方案)
9.  [API Reference (API 參考)](#api-reference-api-參考)
10. [Quick Start Templates (快速入門模板)](#quick-start-templates-快速入門模板)
11. [Additional Resources (其他資源)](#additional-resources-其他資源)

---

## Agent Patterns (代理模式)

### Problem: Build an agent that takes user input and generates responses (問題：建立一個能接收使用者輸入並生成回應的代理)

#### Solution (解決方案)

```python
# 匯入 Agent 類別
from google.adk.agents import Agent

# 建立一個基本的 Agent 實例
agent = Agent(
    name="basic_agent", # 代理名稱
    model="gemini-2.0-flash", # 使用的模型
    instruction="You are a helpful assistant.", # 給予代理的指示
    tools=[],  # 可在此處加入工具
    output_key="response" # 指定輸出鍵值
)
```

### Sequential Workflow (循序工作流程)

```python
# 匯入 SequentialAgent 類別
from google.adk.agents import SequentialAgent

# 建立一個循序工作流程的 Agent
workflow = SequentialAgent(
    name="data_pipeline", # 工作流程名稱
    sub_agents=[extract_agent, transform_agent, load_agent], # 依序執行的子代理
    description="ETL data processing pipeline" # 工作流程描述
)
```

### Parallel Processing (平行處理)

```python
# 匯入 ParallelAgent 類別
from google.adk.agents import ParallelAgent

# 建立一個平行處理的 Agent
parallel = ParallelAgent(
    name="multi_source_analysis", # 代理名稱
    sub_agents=[web_agent, database_agent, api_agent], # 同時執行的子代理
    description="Gather data from multiple sources simultaneously" # 代理描述
)
```

### Iterative Refinement (迭代優化)

```python
# 匯入 LoopAgent 類別
from google.adk.agents import LoopAgent

# 建立一個循環執行的 Agent
refiner = LoopAgent(
    sub_agents=[critic_agent, improvement_agent], # 循環執行的子代理
    max_iterations=5, # 最大迭代次數
    description="Iteratively improve content quality" # 代理描述
)
```

---

## 🔧 Tool Implementations (工具實作)

### Function Tool (函式工具)

```python
from typing import Dict, Any

def search_database(query: str) -> Dict[str, Any]:
    """
    在資料庫中搜尋相關資訊。

    Args:
        query: 搜尋查詢字串

    Returns:
        包含狀態、報告和資料的字典
    """
    try:
        results = db.search(query)
        return {
            'status': 'success',
            'report': f'Found {len(results)} results for "{query}"',
            'data': results
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'Database search failed: {str(e)}'
        }
```

### OpenAPI Tool (OpenAPI 工具)

```python
# 匯入 OpenAPIToolset
from google.adk.tools import OpenAPIToolset

# 從 OpenAPI 規格自動生成工具
weather_tools = OpenAPIToolset.from_url(
    "https://api.weatherapi.com/v1/swagger.json",
    api_key="your_api_key" # 替換成你的 API 金鑰
)

# 建立使用 OpenAPI 工具的 Agent
agent = Agent(
    name="weather_agent",
    tools=weather_tools,
    instruction="Provide weather information and forecasts."
)
```

### MCP Tool (MCP 工具)

```python
# 匯入 MCPToolset 和 StdioConnectionParams
from google.adk.tools import MCPToolset
from google.adk.tools.mcp import StdioConnectionParams

# 連接到 MCP 伺服器
filesystem_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-filesystem', '/data']
    )
)
```

---

## 💾 State Management (狀態管理)

### State Scopes (狀態範圍)

```python
# Session state (對話範圍)
state['session:user_query'] = query
state['session:conversation_history'] = messages

# User state (跨對話的使用者資料)
state['user:preferences'] = user_prefs
state['user:subscription_tier'] = 'premium'

# App state (全域應用程式資料)
state['app:version'] = '1.0.0'
state['app:feature_flags'] = flags

# Temporary state (僅限請求)
state['temp:cache'] = cached_data
```

### State Interpolation (狀態內插)

```python
# 建立使用狀態內插的 Agent
agent = Agent(
    name="personalized_agent",
    instruction=f"""
    Welcome back {state['user:name']}!
    Your last query was: {state['session:last_query']}
    Current preferences: {state['user:preferences']}
    """,
    tools=[personalized_tools]
)
```

---

## 🚀 Deployment Configurations (部署組態)

### Local Development (本地開發)

```bash
# 安裝 ADK
pip install google-adk

# 執行網頁介面
adk web

# 執行特定的 agent
adk web agent_name
```

### Cloud Run Deployment (Cloud Run 部署)

#### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["adk", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

#### Deploy Command (部署指令)
```bash
gcloud run deploy agent-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Vertex AI Agent Engine (Vertex AI 代理引擎)

#### agent.yaml
```yaml
name: my-agent
description: My ADK Agent
model: gemini-2.0-flash
instruction: You are a helpful assistant.
tools: []
```

#### Deploy Command (部署指令)
```bash
adk deploy agent_engine --config agent.yaml
```

---

## 📊 Monitoring & Observability (監控與可觀測性)

### Event Tracking (事件追蹤)

```python
# 匯入 EventTracker
from google.adk.observability import EventTracker

tracker = EventTracker()

# 追蹤 agent 互動
@tracker.track_agent_calls
def run_agent(query):
    result = agent.run(query)
    return result

# 自訂事件
tracker.track_event(
    event_type="user_interaction",
    properties={
        "query_length": len(query),
        "response_time": response_time,
        "agent_name": agent.name
    }
)
```

### Error Handling (錯誤處理)

```python
# 匯入 ErrorHandler
from google.adk.error_handling import ErrorHandler

error_handler = ErrorHandler()

@error_handler.catch_and_log
def safe_agent_call(query):
    try:
        return agent.run(query)
    except Exception as e:
        # 記錄錯誤並回傳備用回應
        logger.error(f"Agent error: {e}")
        return {"error": "Service temporarily unavailable"}
```

---

## 🧪 Testing Patterns (測試模式)

### Unit Test Structure (單元測試結構)

```python
import pytest
from unittest.mock import Mock, patch

class TestMyAgent:
    def test_agent_initialization(self):
        agent = Agent(name="test", model="gemini-2.0-flash")
        assert agent.name == "test"
        assert agent.model == "gemini-2.0-flash"

    @patch('google.adk.agents.Agent.run')
    def test_agent_response(self, mock_run):
        mock_run.return_value = {"response": "Hello!"}
        agent = Agent(name="test")
        result = agent.run("Hi")
        assert result["response"] == "Hello!"
        mock_run.assert_called_once_with("Hi")

    def test_tool_execution(self):
        # 獨立測試工具函式
        result = search_database("test query")
        assert result["status"] in ["success", "error"]
        assert "report" in result
```

### Integration Testing (整合測試)

```python
class TestAgentIntegration:
    def test_full_workflow(self):
        # 測試完整的 agent 工作流程
        workflow = create_etl_pipeline()
        result = workflow.run(test_data)
        assert result["status"] == "success"
        assert len(result["processed_data"]) > 0

    def test_api_integration(self):
        # 測試外部 API 整合
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"weather": "sunny"}
            result = weather_agent.run("What's the weather?")
            assert "sunny" in result["response"]
```

---

## ⚙️ Configuration Templates (組態模板)

### Environment Variables (環境變數)

#### .env file
```
GOOGLE_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

### YAML Configuration (YAML 組態)

#### config.yaml
```yaml
agent:
  name: production_agent
  model: gemini-2.0-flash
  temperature: 0.7
  max_tokens: 1000
tools:
  - type: openapi
    url: https://api.example.com/swagger.json
    api_key: ${API_KEY}
  - type: function
    name: search_database
    function: myapp.tools.search_database
deployment:
  type: cloud_run
  region: us-central1
  memory: 1Gi
  cpu: 1
monitoring:
  enable_events: true
  log_level: INFO
  metrics:
    - response_time
    - error_rate
    - token_usage
```

---

## 🚨 Common Issues & Solutions (常見問題與解決方案)

### Agent Not Responding (代理沒有回應)

**Problem**: 代理回傳空的或 null 回應
**Solutions**:
*   檢查 API 金鑰有效性
*   驗證模型名稱拼寫
*   確保指令格式正確
*   檢查速率限制

### Tool Execution Failures (工具執行失敗)

**Problem**: 工具回傳錯誤狀態
**Solutions**:
*   驗證工具函式簽章
*   檢查外部服務連線
*   驗證身份驗證憑證
*   檢閱錯誤日誌以取得詳細資訊

### State Persistence Issues (狀態持續性問題)

**Problem**: 狀態在呼叫之間未持續存在
**Solutions**:
*   使用正確的狀態範圍前綴
*   檢查狀態後端組態
*   驗證 session/user 識別
*   檢閱狀態序列化

### Performance Problems (效能問題)

**Problem**: 回應時間緩慢
**Solutions**:
*   切換到更快的模型 (flash variants)
*   實作平行處理
*   新增快取層
*   優化工具實作

---

## 📚 API Reference (API 參考)

### Core Classes (核心類別)

| Class             | Purpose (目的)             | Key Methods (主要方法)       |
| ----------------- | -------------------------- | ---------------------------- |
| `Agent`           | 基本代理實作               | `run()`, `run_async()`       |
| `SequentialAgent` | 循序工作流程執行           | `add_agent()`, `run()`       |
| `ParallelAgent`   | 並行任務執行               | `add_agent()`, `run()`       |
| `LoopAgent`       | 迭代優化                   | `set_max_iterations()`, `run()` |
| `RemoteA2aAgent`  | 分散式代理通訊             | `connect()`, `run()`         |

### Tool Classes (工具類別)

| Class           | Purpose (目的)       | Key Features (主要功能)     |
| --------------- | -------------------- | --------------------------- |
| `FunctionTool`  | 自訂 Python 函式     | 錯誤處理、類型提示          |
| `OpenAPIToolset`| REST API 整合        | 自動生成、驗證              |
| `MCPToolset`    | 基於協定的工具       | 互通性、安全性              |
| `AgentTool`     | 代理即工具模式       | 組合、委派                  |

### State Management (狀態管理)

| Scope     | Lifetime (生命週期) | Use Case (使用案例)       |
| --------- | ------------------- | ------------------------- |
| `session:`| 對話                | 上下文、歷史紀錄          |
| `user:`   | 使用者帳戶          | 偏好設定、設定            |
| `app:`    | 應用程式            | 全域組態、功能            |
| `temp:`   | 請求                | 快取、暫存資料            |

---

## 🎯 Quick Start Templates (快速入門模板)

### Hello World Agent (Hello World 代理)

```python
from google.adk.agents import Agent

# 最小化的 agent
agent = Agent(
    name="hello_world",
    model="gemini-2.0-flash",
    instruction="You are a friendly assistant. Greet users warmly."
)

# 本地執行
if __name__ == "__main__":
    result = agent.run("Hello!")
    print(result)
```

### Tool-Enabled Agent (啟用工具的代理)

```python
from google.adk.agents import Agent

def get_weather(city: str) -> dict:
    # 實作天氣 API 呼叫
    return {"status": "success", "temperature": 72, "conditions": "sunny"}

agent = Agent(
    name="weather_assistant",
    model="gemini-2.0-flash",
    instruction="Provide weather information using the get_weather tool.",
    tools=[get_weather]
)
```

### Workflow Agent (工作流程代理)

```python
from google.adk.agents import SequentialAgent, Agent

# 個別的 agents
researcher = Agent(name="researcher", instruction="Gather information")
writer = Agent(name="writer", instruction="Create content")
editor = Agent(name="editor", instruction="Review and improve")

# 組合的工作流程
workflow = SequentialAgent(
    name="content_pipeline",
    sub_agents=[researcher, writer, editor],
    description="Research → Write → Edit content pipeline"
)
```

---

## 🔗 Additional Resources (其他資源)

*   **Official Documentation**: `https://github.com/google/adk-python/tree/main/docs`
*   **Tutorial Implementations**: `tutorial_implementation/`
*   **Research & Examples**: `research/`
*   **Community Forums**: GitHub Issues, Stack Overflow
*   **API Reference**: Inline code documentation
*   **[Contact the Author](/adk_training/docs/contact)**: Get in touch with Raphaël MANSUY
