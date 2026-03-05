# 使用 Cloud Trace 實現 Agent 的可觀測性

> 🔔 `更新日期：2026-03-05`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/cloud-trace/

透過 ADK，您已經可以利用 [這裡](../../evaluation/index.md#使用追蹤檢視-trace-view-進行除錯) 討論過的強大 Web 開發 UI 在本地檢查並觀察您的 Agent 互動。然而，如果我們的目標是雲端部署，我們將需要一個集中式的儀表板來觀察實際流量。

Cloud Trace 是 Google Cloud Observability 的一個組件。它是一個強大的工具，專門透過追蹤功能來監控、偵錯並改善應用程式的效能。對於 Agent 開發套件 (ADK) 應用程式，Cloud Trace 實現了全面的追蹤，協助您了解請求如何流經您的 Agent 互動，並識別 AI Agent 內的效能瓶頸或錯誤。

## 總覽

Cloud Trace 建構於 [OpenTelemetry](https://opentelemetry.io/) 之上，這是一個支援多種語言和擷取方法以產生追蹤數據的開源標準。這與 ADK 應用程式的可觀測性實作一致，ADK 同樣利用與 OpenTelemetry 相容的檢測，讓您能夠：

- **追蹤 Agent 互動**：Cloud Trace 持續收集並分析來自您專案的追蹤數據，讓您能夠快速診斷 ADK 應用程式中的延遲問題與錯誤。這種自動數據收集簡化了在複雜 Agent 工作流中識別問題的過程。
- **偵錯問題**：透過分析詳細的追蹤紀錄，快速診斷延遲問題與錯誤。這對於理解跨不同服務或在特定 Agent 動作（如工具呼叫）期間表現出的通訊延遲至關重要。
- **深度分析與視覺化**：Trace Explorer 是分析追蹤紀錄的主要工具，提供視覺輔助，如跨度 (span) 持續時間的熱圖和請求/錯誤率的折線圖。它還提供了一個跨度表格，可按服務和操作分組，讓您一鍵存取代表性的追蹤紀錄和瀑布視圖，以輕鬆識別 Agent 執行路徑中的瓶頸和錯誤源。

以下範例將假設具備以下 Agent 目錄結構：

```
working_dir/
├── weather_agent/
│   ├── agent.py
│   └── __init__.py
└── deploy_agent_engine.py
└── deploy_fast_api_app.py
└── agent_runner.py
```

```python
# weather_agent/agent.py

import os
from google.adk.agents import Agent

# 設定環境變數
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "{your-project-id}")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


# 定義一個工具函數
def get_weather(city: str) -> dict:
    """擷取指定城市的當前天氣報告。

    參數:
        city (str): 要擷取天氣報告的城市名稱。

    回傳:
        dict: 狀態與結果或錯誤訊息。
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "紐約的天氣晴朗，氣溫為攝氏 25 度"
                "（華氏 77 度）。"
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"無法取得 '{city}' 的天氣資訊。",
        }


# 建立帶有工具的 Agent
root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description="使用天氣工具回答問題的 Agent。",
    instruction="您必須使用可用的工具來尋找答案。",
    tools=[get_weather],
)
```

## Cloud Trace 設定

### Agent Engine 部署設定

#### Agent Engine 部署 - 透過 ADK CLI

在使用 `adk deploy agent_engine` 命令部署 Agent 時，您可以透過添加 `--trace_to_cloud` 標記來啟用雲端追蹤。

```bash
# 部署 Agent Engine 並啟用雲端追蹤
adk deploy agent_engine \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --staging_bucket=$STAGING_BUCKET \
    --trace_to_cloud \
    $AGENT_PATH
```

#### Agent Engine 部署 - 透過 Python SDK

如果您偏好使用 Python SDK，可以在初始化 `AdkApp` 物件時添加 `enable_tracing=True` 來啟用雲端追蹤。

```python
# deploy_agent_engine.py

from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from weather_agent.agent import root_agent

import vertexai

PROJECT_ID = "{your-project-id}"
LOCATION = "{your-preferred-location}"
STAGING_BUCKET = "{your-staging-bucket}"

# 初始化 Vertex AI
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# 建立 AdkApp 並啟用追蹤
adk_app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)


# 建立遠端應用程式
remote_app = agent_engines.create(
    agent_engine=adk_app,
    extra_packages=[
        "./weather_agent",
    ],
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
)
```

### Cloud Run 部署設定

#### Cloud Run 部署 - 透過 ADK CLI

在使用 `adk deploy cloud_run` 命令進行 Cloud Run 部署時，您可以透過添加 `--trace_to_cloud` 標記來啟用雲端追蹤。

```bash
# 部署至 Cloud Run 並啟用雲端追蹤
adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --trace_to_cloud \
    $AGENT_PATH
```

如果您想啟用雲端追蹤並在 Cloud Run 上使用自定義 Agent 服務部署，可以參考下方的 [自定義部署設定](#自定義部署設定) 章節。

### 自定義部署設定

#### 透過內建的 `get_fast_api_app` 模組

如果您想自定義自己的 Agent 服務，可以使用內建的 `get_fast_api_app` 模組初始化 FastAPI 應用程式，並設置 `trace_to_cloud=True` 來啟用雲端追蹤。

```python
# deploy_fast_api_app.py

import os
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI

# 設定用於雲端追蹤的 GOOGLE_CLOUD_PROJECT 環境變數
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "alvin-exploratory-2")

# 在當前工作目錄中尋找 `weather_agent` 目錄
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 建立啟用了雲端追蹤的 FastAPI 應用程式
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    trace_to_cloud=True,
)

app.title = "weather-agent"
app.description = "與 weather-agent 互動的 API"


# 主要執行入口
if __name__ == "__main__":
    import uvicorn

    # 執行伺服器
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

#### 透過自定義 Agent Runner

如果您想完全自定義您的 ADK Agent 執行時期 (runtime)，可以使用 Opentelemetry 的 `CloudTraceSpanExporter` 模組來啟用雲端追蹤。

```python
# agent_runner.py

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from weather_agent.agent import root_agent as weather_agent
from google.genai.types import Content, Part
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import export
from opentelemetry.sdk.trace import TracerProvider

APP_NAME = "weather_agent"
USER_ID = "u_123"
SESSION_ID = "s_123"

# 設定追蹤提供者與處理器
provider = TracerProvider()
processor = export.BatchSpanProcessor(
    CloudTraceSpanExporter(project_id="{your-project-id}")
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# 初始化 Session 服務與 Runner
session_service = InMemorySessionService()
runner = Runner(agent=weather_agent, app_name=APP_NAME, session_service=session_service)

async def main():
    # 取得或建立 Session
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )

    # 設定使用者訊息
    user_content = Content(
        role="user", parts=[Part(text="巴黎的天氣如何？")]
    )

    final_response_content = "無回應"
    # 非同步執行 Agent
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_content = event.content.parts[0].text

    print(final_response_content)


if __name__ == "__main__":
    import asyncio

    # 執行主程式
    asyncio.run(main())
```

## 查看雲端追蹤紀錄

設定完成後，每當您與 Agent 互動時，它都會自動將追蹤數據發送到 Cloud Trace。您可以前往 [console.cloud.google.com](https://console.cloud.google.com) 並在設定的 Google Cloud 專案中存取 Trace Explorer 來查看追蹤紀錄。

![cloud-trace](https://google.github.io/adk-docs/assets/cloud-trace1.png)

接著，您將看到由 ADK Agent 產生的所有可用追蹤紀錄，這些紀錄配置在多個跨度名稱中，例如 `invocation`、`agent_run`、`call_llm` 和 `execute_tool`。

![cloud-trace](https://google.github.io/adk-docs/assets/cloud-trace2.png)

如果您點擊其中一條追蹤紀錄，您將看到詳細流程的瀑布視圖，這與我們在 Web 開發 UI 中使用 `adk web` 命令看到的內容相似。

![cloud-trace](https://google.github.io/adk-docs/assets/cloud-trace3.png)

### 實作範例

-   [`Short Movie Agents`](../../../python/agents/short-movie-agents/): 展示透過實現`CloudTraceSpanExporter`使用 Cloud Trace 來監控和偵錯生成式 AI 代理的完整範例。

## 資源

- [Google Cloud Trace 文件](https://cloud.google.com/trace)

## 整理說明
下表整理了各種 Cloud Trace 設定方式及其適用情境：

| 設定方式 | 適用場景 | 啟用追蹤方式 | 主要用途/說明 |
|---|---|---|---|
| Agent Engine 部署（ADK CLI） | 使用 ADK CLI 部署 Agent Engine | `adk deploy agent_engine --trace_to_cloud` | 直接於部署時啟用雲端追蹤，適合標準部署流程 |
| Agent Engine 部署（Python SDK） | 以 Python SDK 程式化部署 Agent Engine | `AdkApp(enable_tracing=True)` | 於程式碼層級啟用追蹤，彈性高，適合自動化或自訂部署 |
| Cloud Run 部署（ADK CLI） | 使用 ADK CLI 部署至 Cloud Run | `adk deploy cloud_run --trace_to_cloud` | 於雲端服務部署時直接啟用追蹤，適合標準雲端部署 |
| Cloud Run 自定義服務 | Cloud Run 上自定義 FastAPI/服務 | `get_fast_api_app(trace_to_cloud=True)` | 適合需自訂 API 服務的場景，於應用程式層啟用追蹤 |
| 完全自定義 Agent Runner | 需高度自訂執行流程 | `CloudTraceSpanExporter` + OpenTelemetry | 最高彈性，適合特殊需求或進階可觀測性整合 |

> 各設定方式皆可將追蹤資料自動上傳至 Google Cloud Trace，方便於 Trace Explorer 進行視覺化分析與效能診斷。
