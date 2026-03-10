# Phoenix 在 ADK 的觀測能力

> 🔔 `更新日期：2026-03-08`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/integrations/phoenix/

[`ADK 支援`: `Python`]

[Phoenix](https://arize.com/docs/phoenix) 是一個開源、自我託管的觀測平台，用於大規模監控、偵錯和改進 LLM 應用程式及 AI Agent。它為您的 Google ADK 應用程式提供全面的追蹤（tracing）和評估能力。要開始使用，請註冊一個[免費帳號](https://phoenix.arize.com/)。

## 概覽

Phoenix 可以透過 [OpenInference 儀表化（instrumentation）](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk) 自動從 Google ADK 收集追蹤數據，讓您能夠：

- **追蹤 Agent 互動** - 自動捕捉每一次 Agent 運行、工具調用、模型請求和回應，並包含完整的上下文和元數據（metadata）。
- **評估效能** - 使用自定義或內建的評估器評估 Agent 行為，並執行實驗以測試 Agent 配置。
- **偵錯問題** - 分析詳細的追蹤數據，快速識別瓶頸、失敗的工具調用以及非預期的 Agent 行為。
- **自我託管控制** - 將數據保留在您自己的基礎架構中。

## 安裝

### 1. 安裝必要套件

```bash
# 安裝 Google ADK 的 OpenInference 儀表化套件、ADK 本身以及 Phoenix OpenTelemetry 套件
pip install openinference-instrumentation-google-adk google-adk arize-phoenix-otel
```

## 設定

### 1. 啟動 Phoenix

這些指令向您展示如何使用 Phoenix Cloud。您也可以在 notebook、終端機中[啟動 Phoenix](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)，或使用容器進行自我託管。

1. 註冊一個[免費 Phoenix 帳號](https://phoenix.arize.com/)。
1. 從您新 Phoenix Space 的設定頁面（Settings page）建立您的 API 金鑰（API key）。
1. 複製您的端點（endpoint），格式應如下：https://app.phoenix.arize.com/s/[your-space-name]

**設定您的 Phoenix 端點和 API 金鑰：**

```python
import os

# 設定 Phoenix API 金鑰
os.environ["PHOENIX_API_KEY"] = "在此加入您的 PHOENIX API 金鑰"
# 設定 Phoenix 收集器端點
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "在此加入您的 PHOENIX 收集器端點"

# 如果您的 Phoenix Cloud 實例是在 2025 年 6 月 24 日之前建立的，請將 API 金鑰設定為標頭：
# os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={os.getenv('PHOENIX_API_KEY')}"
```

### 2. 將您的應用程式連接到 Phoenix

```python
from phoenix.otel import register

# 配置 Phoenix 追蹤器
tracer_provider = register(
    project_name="my-llm-app",  # 專案名稱，預設為 'default'
    auto_instrument=True        # 根據已安裝的 OI 依賴項自動對應用程式進行儀表化
)
```

## 觀察

現在您已設定好追蹤，所有 Google ADK SDK 的請求都將串流傳輸到 Phoenix 以進行觀測和評估。

```python
import nest_asyncio
# 允許在非同步環境（如 Jupyter Notebook）中巢狀使用事件迴圈
nest_asyncio.apply()

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# 定義一個工具函數
def get_weather(city: str) -> dict:
    """檢索指定城市的當前天氣報告。

    參數：
        city (str): 要檢索天氣報告的城市名稱。

    回傳：
        dict: 狀態與結果或錯誤訊息。
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "紐約的天氣晴朗，溫度為攝氏 25 度"
                "（華氏 77 度）。"
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"無法取得 '{city}' 的天氣資訊。",
        }

# 建立帶有工具的 Agent
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
# 使用記憶體內部的執行器
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

# 建立會話
await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

# 運行 Agent（所有互動都將被追蹤）
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="紐約的天氣如何？")]
    )
):
    # 如果事件是最終回應，則列印內容
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## 支援與資源

- [Phoenix 文件](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)
- [社群 Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference 套件](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
