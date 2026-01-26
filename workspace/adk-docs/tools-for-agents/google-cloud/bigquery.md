# ADK 的 BigQuery 工具

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/google-cloud/bigquery/

[`ADK 支援`: `Python v1.1.0`]

這是一組旨在提供與 BigQuery 整合的工具，具體包括：

* **`list_dataset_ids`**：獲取 GCP 專案中存在的 BigQuery 資料集 ID。
* **`get_dataset_info`**：獲取關於 BigQuery 資料集的元數據（Metadata）。
* **`list_table_ids`**：獲取 BigQuery 資料集中存在的資料表 ID。
* **`get_table_info`**：獲取關於 BigQuery 資料表的元數據（Metadata）。
* **`execute_sql`**：在 BigQuery 中執行 SQL 查詢並獲取結果。
* **`forecast`**：使用 `AI.FORECAST` 函數執行 BigQuery AI 時間序列預測。
* **`ask_data_insights`**：使用自然語言回答關於 BigQuery 資料表中數據的問題。

它們被封裝在工具集 `BigQueryToolset` 中。

```python
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
from google.genai import types
import google.auth

# 定義範例 Agent 的常數
AGENT_NAME = "bigquery_agent"
APP_NAME = "bigquery_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.0-flash"

# 定義工具配置以阻止任何寫入操作
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

# 使用應用程式預設憑證 (ADC) 進行 BigQuery 認證
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(
  credentials=application_default_credentials
)

# 實例化 BigQuery 工具集
bigquery_toolset = BigQueryToolset(
  credentials_config=credentials_config, bigquery_tool_config=tool_config
)

# Agent 定義
bigquery_agent = Agent(
  model=GEMINI_MODEL,
  name=AGENT_NAME,
  description=(
    "此 Agent 用於回應關於 BigQuery 資料與模型的問題，並執行 SQL 查詢。"
  ),
  instruction="""
    你是一位具有多種 BigQuery 工具的資料科學 agent。
    使用這些工具來回答使用者的問題。
  """,
  tools=[bigquery_toolset],
)

# 會話與 Runner
session_service = InMemorySessionService()
session = asyncio.run(
  session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
  )
)
runner = Runner(
  agent=bigquery_agent, app_name=APP_NAME, session_service=session_service
)


# 與 Agent 互動
def call_agent(query):
  """
  呼叫 agent 的輔助函式。
  """
  content = types.Content(role="user", parts=[types.Part(text=query)])
  events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  print("使用者：", query)
  for event in events:
    if event.is_final_response():
      final_response = event.content.parts[0].text
      print("代理：", final_response)


call_agent("在 bigquery-public-data 專案中有任何 ml 資料集嗎？")
call_agent("請告訴我更多關於 ml_datasets 的資訊。")
call_agent("它有哪些資料表？")
call_agent("請告訴我更多關於 census_adult_income 資料表的資訊。")
call_agent("每個收入等級有多少列？")
call_agent(
  "education_num、age 與 income_bracket 之間的統計相關性為何？"
)
```

注意：如果您想將 BigQuery 資料代理（Data Agent）作為工具訪問，請參閱 [ADK 的資料代理工具](data-agent.md)。
