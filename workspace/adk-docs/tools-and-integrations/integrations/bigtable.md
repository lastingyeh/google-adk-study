# ADK 的 Bigtable 資料庫工具

> 🔔 `更新日期：2026-03-05`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/bigtable/

[`ADK 支援`: `Python v1.12.0`]

這些是一組旨在提供與 Bigtable 整合的工具，分別為：

* **`list_instances`**：擷取 Google Cloud 專案中的 Bigtable 執行個體。
* **`get_instance_info`**：擷取 Google Cloud 專案中的執行個體中繼資料資訊。
* **`list_tables`**：擷取 GCP Bigtable 執行個體中的資料表。
* **`get_table_info`**：擷取 GCP Bigtable 中的資料表中繼資料資訊。
* **`execute_sql`**：在 Bigtable 資料表中執行 SQL 查詢並擷取結果。

它們被封裝在工具集 `BigtableToolset` 中。

```py
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.google_tool import GoogleTool
from google.adk.tools.bigtable import query_tool
from google.adk.tools.bigtable.settings import BigtableToolSettings
from google.adk.tools.bigtable.bigtable_credentials import BigtableCredentialsConfig
from google.adk.tools.bigtable.bigtable_toolset import BigtableToolset
from google.genai import types
from google.adk.tools.tool_context import ToolContext
import google.auth
from google.auth.credentials import Credentials

# 為此範例代理程式定義常數
AGENT_NAME = "bigtable_agent"
APP_NAME = "bigtable_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.5-flash"

# 定義 Bigtable 工具設定，並將讀取功能設置為允許。
tool_settings = BigtableToolSettings()

# 定義憑證設定 - 在此範例中，我們使用應用程式預設憑證
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = BigtableCredentialsConfig(
    credentials=application_default_credentials
)

# 具現化一個 Bigtable 工具集
bigtable_toolset = BigtableToolset(
    credentials_config=credentials_config, bigtable_tool_settings=tool_settings
)

# 選用
# 在 Bigtable 工具集中內建的 `execute_sql` 工具之上，
# 為代理程式建立一個封裝好的函式工具。
# 例如，此自訂工具可以執行動態構建的查詢。
def count_rows_tool(
    table_name: str,
    credentials: Credentials,  # GoogleTool 處理 `credentials`
    settings: BigtableToolSettings,  # GoogleTool 處理 `settings`
    tool_context: ToolContext,  # GoogleTool 處理 `tool_context`
):
  """計算指定資料表的總列數。

  參數:
    table_name: 要計算列數的資料表名稱。

  回傳:
      資料表中的總列數。
  """

  # 替換以下特定 Bigtable 資料庫的設定。
  PROJECT_ID = "<PROJECT_ID>"
  INSTANCE_ID = "<INSTANCE_ID>"

  query = f"""
  SELECT count(*) FROM {table_name}
    """

  # 執行 SQL 查詢
  return query_tool.execute_sql(
      project_id=PROJECT_ID,
      instance_id=INSTANCE_ID,
      query=query,
      credentials=credentials,
      settings=settings,
      tool_context=tool_context,
  )

# 代理程式定義
bigtable_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description=(
        "用於回答有關 Bigtable 資料庫問題並執行 SQL 查詢的代理程式。"
    ),
    instruction="""\
        你是一個資料助理代理程式，可以使用多種 Bigtable 工具。
        利用這些工具來回答使用者的問題。
    """,
    tools=[
        bigtable_toolset,
        # 基於內建的 Bigtable 工具集新增自訂 Bigtable 工具。
        GoogleTool(
            func=count_rows_tool,
            credentials_config=credentials_config,
            tool_settings=tool_settings,
        ),
    ],
)


# 工作階段與執行器
session_service = InMemorySessionService()

# 建立工作階段
session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
runner = Runner(
    agent=bigtable_agent, app_name=APP_NAME, session_service=session_service
)


# 代理程式互動
def call_agent(query):
    """
    呼叫代理程式並進行查詢的輔助函式。
    """
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    print("使用者:", query)
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理程式:", final_response)

# 將下方的 Bigtable 執行個體和資料表名稱替換為你自己的名稱。
call_agent("列出 projects/<PROJECT_ID>/instances/<INSTANCE_ID> 中的所有資料表")
call_agent("列出 <TABLE_NAME> 中的前 5 列")
```
