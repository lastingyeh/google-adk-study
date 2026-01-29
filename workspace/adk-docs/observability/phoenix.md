# 使用 Phoenix 進行 Agent 可觀測性監控

> 🔔 `更新日期：2026-01-29`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/phoenix/

[Phoenix](https://arize.com/docs/phoenix) 是一個開源、自我託管的可觀測性平台，用於大規模監控、偵錯和改進 LLM 應用程式與 AI Agent。它為您的 Google ADK 應用程式提供全面的追蹤（tracing）和評估能力。要開始使用，請註冊一個 [免費帳戶](https://phoenix.arize.com/)。

## 概覽

Phoenix 可以使用 [OpenInference instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk) 自動收集來自 Google ADK 的追蹤數據，讓您能夠：

- **追蹤 Agent 互動** - 自動擷取每一次的 Agent 執行、工具調用、模型請求和回應，並帶有完整的上下文和中繼資料（metadata）。
- **評估效能** - 使用自定義或內建的評估器來評估 Agent 行為，並執行實驗以測試 Agent 配置。
- **偵錯問題** - 分析詳細的追蹤數據，快速識別瓶頸、失敗的工具調用以及非預期的 Agent 行為。
- **自我託管控制** - 將數據保留在您自己的基礎設施中。

## 安裝

### 1. 安裝必要的套件 { #install-required-packages }

```bash
# 安裝 Google ADK 的 OpenInference 儀器化工具、Google ADK 本體以及 Phoenix OpenTelemetry 支援
pip install openinference-instrumentation-google-adk google-adk arize-phoenix-otel
```
## 設定

### 1. 啟動 Phoenix { #launch-phoenix }

這些說明向您展示如何使用 Phoenix Cloud。您也可以在筆記本中、從終端機[啟動 Phoenix](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)，或使用容器自行託管。

1. 註冊一個 [免費的 Phoenix 帳戶](https://phoenix.arize.com/)。
2. 從新 Phoenix 空間的「Settings」（設定）頁面建立您的 API 金鑰。
3. 複製您的端點（endpoint），格式應如下：https://app.phoenix.arize.com/s/[您的空間名稱]

**設定您的 Phoenix 端點和 API 金鑰：**

```python
import os

# 設定 Phoenix API 金鑰
os.environ["PHOENIX_API_KEY"] = "在此處加入您的 PHOENIX API 金鑰"
# 設定 Phoenix 收集器端點
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "在此處加入您的 PHOENIX 收集器端點"

# 如果您的 Phoenix Cloud 實例是在 2025 年 6 月 24 日之前建立的，請將 API 金鑰設定為標頭：
# os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={os.getenv('PHOENIX_API_KEY')}"
```

### 2. 將您的應用程式連接到 Phoenix { #connect-your-application-to-phoenix }

```python
from phoenix.otel import register

# 配置 Phoenix 追蹤器
tracer_provider = register(
    project_name="my-llm-app",  # 專案名稱，預設為 'default'
    auto_instrument=True        # 根據已安裝的 OpenInference 依賴項自動對您的應用程式進行儀器化
)
```

## 觀察

現在您已經完成了追蹤設定，所有的 Google ADK SDK 請求都將串流到 Phoenix 以供可觀測性分析和評估。


```python
import nest_asyncio
# 在異步環境中應用 nest_asyncio
nest_asyncio.apply()

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

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
# 建立記憶體內的 Runner
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

# 建立會話
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
    # 如果事件是最終回應，則列印內容
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## 支援與資源
- [Phoenix 文件](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)
- [社群 Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference 套件](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
