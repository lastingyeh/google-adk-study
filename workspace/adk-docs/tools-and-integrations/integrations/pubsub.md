# ADK 的 Pub/Sub 工具

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/google-cloud/pubsub/

[`ADK 支援`: `Python v1.22.0`]

`PubSubToolset` 允許代理 (agents) 與 [Google Cloud Pub/Sub](https://cloud.google.com/pubsub) 服務進行互動，以發布、提取和確認訊息。

## 前置作業

在開始使用 `PubSubToolset` 之前，您需要：

1.  **在您的 Google Cloud 專案中啟用 Pub/Sub API**。
2.  **身分驗證與授權**：確保執行代理的主體（例如：使用者、服務帳戶）具備執行 Pub/Sub 操作所需的 IAM 權限。有關 Pub/Sub 角色的更多資訊，請參閱 [Pub/Sub 存取控制文件](https://cloud.google.com/pubsub/docs/access-control)。
3.  **建立主題 (Topic) 或訂閱 (Subscription)**：[建立主題](https://cloud.google.com/pubsub/docs/create-topic) 以發布訊息，並 [建立訂閱](https://cloud.google.com/pubsub/docs/create-subscription) 以接收訊息。

## 使用方法

```py
import asyncio
import os

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.pubsub.config import PubSubToolConfig
from google.adk.tools.pubsub.pubsub_credentials import PubSubCredentialsConfig
from google.adk.tools.pubsub.pubsub_toolset import PubSubToolset
from google.genai import types
import google.auth

# 定義此範例代理的常數
AGENT_NAME = "pubsub_agent"
APP_NAME = "pubsub_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.0-flash"

# 定義 Pub/Sub 工具配置。
# 您可以在此處選擇性設定 project_id，或讓代理從上下文/使用者輸入中推斷。
tool_config = PubSubToolConfig(project_id=os.getenv("GOOGLE_CLOUD_PROJECT"))

# 預設使用外部管理的應用程式預設憑證 (ADC)。
# 這將身分驗證與代理/工具生命週期解耦。
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = PubSubCredentialsConfig(
    credentials=application_default_credentials
)

# 實例化 Pub/Sub 工具集
pubsub_toolset = PubSubToolset(
    credentials_config=credentials_config, pubsub_tool_config=tool_config
)

# 代理定義
pubsub_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description=(
        "用於從 Google Cloud Pub/Sub 發布、提取和確認訊息的代理。"
    ),
    instruction="""
        你是一位雲端工程師代理，具備存取 Google Cloud Pub/Sub 工具的權限。
        你可以將訊息發布到主題、從訂閱中提取訊息，以及確認訊息。
    """,
    tools=[pubsub_toolset],
)

# 會話 (Session) 與執行器 (Runner)
session_service = InMemorySessionService()
session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
runner = Runner(
    agent=pubsub_agent, app_name=APP_NAME, session_service=session_service
)


# 代理互動
def call_agent(query):
    """
    呼叫代理並傳入查詢的輔助函式。
    """
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    print("使用者:", query)
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理:", final_response)

# 執行範例查詢
call_agent("將 'Hello World' 發布到 'my-topic'")
call_agent("從 'my-subscription' 提取訊息")
```

## 工具

`PubSubToolset` 包含以下工具：

### `publish_message`

將訊息發布到 Pub/Sub 主題。

| 參數           | 類型                | 說明                                                                                             |
| -------------- | ------------------- | ------------------------------------------------------------------------------------------------------- |
| `topic_name`   | `str`               | Pub/Sub 主題名稱 (例如：`projects/my-project/topics/my-topic`)。                            |
| `message`      | `str`               | 要發布的訊息內容。                                                                         |
| `attributes`   | `dict[str, str]`    | (選填) 附加至訊息的屬性。                                                         |
| `ordering_key` | `str`               | (選填) 訊息的排序金鑰。如果設定此參數，訊息將按順序發布。 |

### `pull_messages`

從 Pub/Sub 訂閱中提取訊息。

| 參數                | 類型    | 說明                                                                                                 |
| ------------------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `subscription_name` | `str`   | Pub/Sub 訂閱名稱 (例如：`projects/my-project/subscriptions/my-sub`)。                      |
| `max_messages`      | `int`   | (選填) 要提取的最大訊息數量。預設為 `1`。                                         |
| `auto_ack`          | `bool`  | (選填) 是否自動確認訊息。預設為 `False`。                            |

### `acknowledge_messages`

確認 Pub/Sub 訂閱中的一或多則訊息。

| 參數                | 類型          | 說明                                                                                       |
| ------------------- | ------------- | ------------------------------------------------------------------------------------------------- |
| `subscription_name` | `str`         | Pub/Sub 訂閱名稱 (例如：`projects/my-project/subscriptions/my-sub`)。            |
| `ack_ids`           | `list[str]`   | 要確認的確認 ID (acknowledgment IDs) 列表。                                                      |
