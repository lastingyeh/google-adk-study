# ADK 的 Spanner 資料庫工具

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/spanner/

[`ADK 支援`: `Python v1.11.0`]

這是一組旨在提供與 Spanner 整合的工具，分別為：

* **`list_table_names`**：獲取 GCP Spanner 資料庫中存在的資料表名稱。
* **`list_table_indexes`**：獲取 GCP Spanner 資料庫中存在的資料表索引。
* **`list_table_index_columns`**：獲取 GCP Spanner 資料庫中存在的資料表索引欄位。
* **`list_named_schemas`**：獲取 Spanner 資料庫的命名架構（named schema）。
* **`get_table_schema`**：獲取 Spanner 資料庫資料表架構和元數據資訊。
* **`execute_sql`**：在 Spanner 資料庫中執行 SQL 查詢並獲取結果。
* **`similarity_search`**：使用文字查詢在 Spanner 中進行相似性搜尋。

它們被封裝在工具集 `SpannerToolset` 中。

```py
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
# from google.adk.sessions import DatabaseSessionService
from google.adk.tools.google_tool import GoogleTool
from google.adk.tools.spanner import query_tool
from google.adk.tools.spanner.settings import SpannerToolSettings
from google.adk.tools.spanner.settings import Capabilities
from google.adk.tools.spanner.spanner_credentials import SpannerCredentialsConfig
from google.adk.tools.spanner.spanner_toolset import SpannerToolset
from google.genai import types
from google.adk.tools.tool_context import ToolContext
import google.auth
from google.auth.credentials import Credentials

# 為此範例代理定義常量
AGENT_NAME = "spanner_agent"
APP_NAME = "spanner_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.5-flash"

# 定義 Spanner 工具設定，將讀取權限設置為允許。
tool_settings = SpannerToolSettings(capabilities=[Capabilities.DATA_READ])

# 定義憑證配置 - 在此範例中，我們使用應用程式預設憑證
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = SpannerCredentialsConfig(
    credentials=application_default_credentials
)

# 實例化 Spanner 工具集
spanner_toolset = SpannerToolset(
    credentials_config=credentials_config, spanner_tool_settings=tool_settings
)

# 選用項目
# 在 Spanner 工具集內建的 `execute_sql` 工具之上，為代理建立一個包裝好的函式工具。
# 例如，此自定義工具可以執行動態構建的查詢。
def count_rows_tool(
    table_name: str,
    credentials: Credentials,  # GoogleTool 處理 `credentials`
    settings: SpannerToolSettings,  # GoogleTool 處理 `settings`
    tool_context: ToolContext,  # GoogleTool 處理 `tool_context`
):
  """計算指定資料表的總行數。

  Args:
    table_name: 要計算行數的資料表名稱。

  Returns:
      資料表中的總行數。
  """

  # 替換以下特定 Spanner 資料庫的設定。
  PROJECT_ID = "<PROJECT_ID>"
  INSTANCE_ID = "<INSTANCE_ID>"
  DATABASE_ID = "<DATABASE_ID>"

  query = f"""
  SELECT count(*) FROM {table_name}
    """

  return query_tool.execute_sql(
      project_id=PROJECT_ID,
      instance_id=INSTANCE_ID,
      database_id=DATABASE_ID,
      query=query,
      credentials=credentials,
      settings=settings,
      tool_context=tool_context,
  )

# 代理定義
spanner_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description=(
        "用於回答有關 Spanner 資料庫問題並執行 SQL 查詢的代理。"
    ),
    instruction="""\
        你是一個資料助手代理，可以存取多個 Spanner 工具。
        利用這些工具來回答使用者的問題。
    """,
    tools=[
        spanner_toolset,
        # 基於內建的 Spanner 工具集添加自定義 Spanner 工具。
        GoogleTool(
            func=count_rows_tool,
            credentials_config=credentials_config,
            tool_settings=tool_settings,
        ),
    ],
)


# 會話和執行器
session_service = InMemorySessionService()

# 選擇性地，Spanner 可以用作生產環境的資料庫會話服務。
# 請注意，建議使用專用的執行個體/資料庫來存儲會話。
# session_service_spanner_db_url = "spanner+spanner:///projects/PROJECT_ID/instances/INSTANCE_ID/databases/my-adk-session"
# session_service = DatabaseSessionService(db_url=session_service_spanner_db_url)

session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
runner = Runner(
    agent=spanner_agent, app_name=APP_NAME, session_service=session_service
)


# 代理互動
def call_agent(query):
    """
    呼叫代理進行查詢的輔助函式。
    """
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    print("使用者:", query)
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理:", final_response)

# 將下方的 Spanner 資料庫和資料表名稱替換為您自己的名稱。
call_agent("列出 projects/<PROJECT_ID>/instances/<INSTANCE_ID>/databases/<DATABASE_ID> 中的所有資料表")
call_agent("描述 <TABLE_NAME> 的結構（schema）")
call_agent("列出 <TABLE_NAME> 中的前 5 行")
```
