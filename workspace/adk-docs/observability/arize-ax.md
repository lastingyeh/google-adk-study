# 使用 Arize AX 實現 Agent 可觀測性

> 🔔 `更新日期：2026-01-29`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/arize-ax/

[Arize AX](https://arize.com/docs/ax) 是一個企業級的可觀測性平台，用於大規模監控、偵錯和改進 LLM 應用程式與 AI Agent。它為您的 Google ADK 應用程式提供全面的追蹤（Tracing）、評估（Evaluation）和監控能力。若要開始使用，請註冊一個[免費帳號](https://app.arize.com/auth/join)。

關於開源、自我託管的替代方案，請參考 [Phoenix](https://arize.com/docs/phoenix)。

## 概覽

Arize AX 可以使用 [OpenInference 儀表化（instrumentation）](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk) 自動從 Google ADK 收集追蹤數據，讓您可以：

- **追蹤 Agent 互動** - 自動捕捉每一次 Agent 執行、工具調用、模型請求及其回應，並包含上下文和元數據（metadata）。
- **評估效能** - 使用自定義或預建的評估器評估 Agent 行為，並執行實驗以測試 Agent 配置。
- **生產環境監控** - 設置即時儀表板和警報以追蹤效能。
- **對問題進行偵錯** - 分析詳細的追蹤數據，以快速識別瓶頸、失敗的工具調用以及任何非預期的 Agent 行為。

![Agent 追蹤](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-traces.png)

## 安裝

安裝所需的套件：

```bash
# 安裝 OpenInference Google ADK 儀表化工具、Google ADK 本體以及 Arize OTEL 擴充
pip install openinference-instrumentation-google-adk google-adk arize-otel
```

## 設定

### 1. 配置環境變數

設定您的 Google API 金鑰：

```bash
# 設定 Google API 金鑰以便調用模型
export GOOGLE_API_KEY=[您的金鑰]
```

### 2. 將您的應用程式連接到 Arize AX

```python
from arize.otel import register

# 註冊並連接至 Arize AX
tracer_provider = register(
    space_id="your-space-id",      # 位於應用程式空間設定頁面
    api_key="your-api-key",        # 位於應用程式空間設定頁面
    project_name="your-project-name"  # 您可以自行命名此專案名稱
)

# 從 OpenInference 匯入並配置自動儀表化工具
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# 完成自動儀表化設定，將追蹤數據導向至 tracer_provider
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
```

## 觀測

現在您已經完成了追蹤設定，所有 Google ADK SDK 的請求都將串流至 Arize AX 以進行可觀測性分析和評估。

```python
import nest_asyncio
# 允許在非同步環境（如 Jupyter Notebook）中運行 nested 事件迴圈
nest_asyncio.apply()

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# 定義一個工具函數
def get_weather(city: str) -> dict:
    """檢索指定城市的當前天氣報告。

    參數:
        city (str): 要檢索天氣報告的城市名稱。

    回傳:
        dict: 狀態與結果，或錯誤訊息。
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

# 建立一個帶有工具的 Agent
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    description="使用天氣工具回答問題的 Agent。",
    instruction="您必須使用可用的工具來尋找答案。",
    tools=[get_weather]
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
# 使用內存運行器（InMemoryRunner）來執行 Agent
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

# 建立一個會話
await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

# 執行 Agent（所有的互動都將被追蹤）
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="紐約的天氣如何？")]
    )
):
    # 當收到最終回應事件時，印出內容
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## 在 Arize AX 中查看結果
![Arize AX 中的追蹤數據](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-dashboard.png)
![Agent 視覺化](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-agent.png)
![Agent 實驗](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-experiments.png)

## 支援與資源
- [Arize AX 文件](https://arize.com/docs/ax/integrations/frameworks-and-platforms/google-adk)
- [Arize 社群 Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference 套件](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
