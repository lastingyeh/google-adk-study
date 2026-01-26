# ADK 的數據代理工具 (Data Agents tools)

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/google-cloud/data-agent/

[`ADK 支援`: `Python v1.23.0`]

這是一組旨在提供與 [Conversational Analytics API](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/overview) 所驅動的數據代理 (Data Agents) 集成的工具。

數據代理是人工智慧驅動的代理，可幫助您使用自然語言分析數據。在配置數據代理時，您可以從支援的數據源中進行選擇，包括 **BigQuery**、**Looker** 和 **Looker Studio**。

**先決條件**

在使用這些工具之前，您必須在 Google Cloud 中建構並配置您的數據代理：

* [使用 HTTP 和 Python 建構數據代理](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-http)
* [使用 Python SDK 建構數據代理](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk)
* [在 BigQuery Studio 中建立數據代理](https://docs.cloud.google.com/bigquery/docs/create-data-agents#create_a_data_agent)

`DataAgentToolset` 包含以下工具：

* **`list_accessible_data_agents`**：列出您在配置的 GCP 專案中有權訪問的數據代理。
* **`get_data_agent_info`**：根據特定數據代理的完整資源名稱檢索其詳細資訊。
* **`ask_data_agent`**：使用自然語言與特定的數據代理進行對話。

它們被封裝在工具集 `DataAgentToolset` 中。

```py
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.data_agent.config import DataAgentToolConfig
from google.adk.tools.data_agent.credentials import DataAgentCredentialsConfig
from google.adk.tools.data_agent.data_agent_toolset import DataAgentToolset
from google.genai import types
import google.auth

# 定義此範例代理的常數
AGENT_NAME = "data_agent_example"
APP_NAME = "data_agent_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.5-flash"

# 定義工具配置
tool_config = DataAgentToolConfig(
    max_query_result_rows=100,
)

# 使用應用程式預設憑據 (ADC)
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = DataAgentCredentialsConfig(
    credentials=application_default_credentials
)

# 實例化數據代理工具集
da_toolset = DataAgentToolset(
    credentials_config=credentials_config,
    data_agent_tool_config=tool_config,
    tool_filter=[
        "list_accessible_data_agents",
        "get_data_agent_info",
        "ask_data_agent",
    ],
)

# 代理定義
data_agent = Agent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    description="使用數據代理回答使用者問題的代理。",
    instruction=(
        "## 角色\n您是一個樂於助人的助手，使用數據代理"
        " 來回答使用者關於其數據的問題。\n\n"
    ),
    tools=[da_toolset],
)

# 會話和執行器
session_service = InMemorySessionService()
session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
runner = Runner(
    agent=data_agent, app_name=APP_NAME, session_service=session_service
)


# 代理交互
def call_agent(query):
    """
    呼叫代理並傳入查詢的輔助函數。
    """
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    print("使用者:", query)
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理:", final_response)

call_agent("列出專案 <PROJECT_ID> 中可訪問的數據代理。")
call_agent("獲取有關 <DATA_AGENT_NAME> 的資訊。")
# 此範例中的數據代理配置了 BigQuery 表：
# `bigquery-public-data.san_francisco.street_trees`
call_agent("要求 <DATA_AGENT_NAME> 計算表中的行數。")
call_agent("表中有哪些欄位？")
call_agent("前 5 種樹種是什麼？")
call_agent("對於這些物種，法律地位的分布如何？")
```
