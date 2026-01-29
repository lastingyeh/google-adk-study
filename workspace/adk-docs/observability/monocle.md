# 使用 Monocle 實現 Agent 可觀測性

> 🔔 `更新日期：2026-01-29`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/observability/monocle/

[Monocle](https://github.com/monocle2ai/monocle) 是一個開源的可觀測性平台，用於監控、偵錯和改進 LLM 應用程式和 AI Agent。它透過自動儀表化（automatic instrumentation）為您的 Google ADK 應用程式提供全面的追蹤能力。Monocle 會產生符合 OpenTelemetry 標準的追蹤（traces），並可匯出至各種目的地，包括本地檔案或控制台輸出。

## 概覽

Monocle 會自動對 Google ADK 應用程式進行儀表化，讓您可以：

- **追蹤 Agent 互動** - 自動擷取每次 Agent 執行、工具調用和模型請求，並包含完整的上下文和詮釋資料（metadata）
- **監控執行流程** - 透過詳細的追蹤記錄 Agent 狀態、委派事件和執行流程
- **偵錯問題** - 分析詳細的追蹤資訊，快速識別瓶頸、失敗的工具調用和意外的 Agent 行為
- **靈活的匯出選項** - 將追蹤資料匯出至本地檔案或控制台進行分析
- **相容 OpenTelemetry** - 產生標準的 OpenTelemetry 追蹤，可與任何相容 OTLP 的後端協作

Monocle 會自動儀表化以下 Google ADK 組件：

- **`BaseAgent.run_async`** - 擷取 Agent 執行、Agent 狀態和委派事件
- **`FunctionTool.run_async`** - 擷取工具執行，包括工具名稱、參數和結果
- **`Runner.run_async`** - 擷取 Runner 執行，包括請求上下文和執行流程

## 安裝

### 1. 安裝必要套件

```bash
# 安裝 Monocle 應用程式追蹤套件與 Google ADK
pip install monocle_apptrace google-adk
```

## 設定

### 1. 配置 Monocle 遙測

當您初始化遙測時，Monocle 會自動儀表化 Google ADK。只需在應用程式啟動時呼叫 `setup_monocle_telemetry()`：

```python
from monocle_apptrace import setup_monocle_telemetry

# 初始化 Monocle 遙測 - 自動對 Google ADK 進行儀表化
setup_monocle_telemetry(workflow_name="my-adk-app")
```

就這樣！Monocle 將自動偵測並儀表化您的 Google ADK Agent、工具和 Runner。

### 2. 配置匯出器（選用）

預設情況下，Monocle 將追蹤資料匯出為本地 JSON 檔案。您可以使用環境變數配置不同的匯出器。

#### 匯出至控制台（用於偵錯）

設定環境變數：

```bash
# 將匯出器設定為控制台
export MONOCLE_EXPORTER="console"
```

#### 匯出至本地檔案（預設）

```bash
# 將匯出器設定為檔案
export MONOCLE_EXPORTER="file"
```

或者直接省略 `MONOCLE_EXPORTER` 變數 - 它的預設值就是 `file`。

## 觀測

現在您已經完成了追蹤設定，所有的 Google ADK SDK 請求都將由 Monocle 自動追蹤。

```python
from monocle_apptrace import setup_monocle_telemetry
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# 初始化 Monocle 遙測 - 必須在啟動 ADK 之前呼叫
setup_monocle_telemetry(workflow_name="weather_app")

# 定義一個工具函數
def get_weather(city: str) -> dict:
    """擷取指定城市的當前天氣報告。

    參數:
        city (str): 要獲取天氣報告的城市名稱。

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
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

# 建立會話
await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

# 執行 Agent（所有的互動都會被自動追蹤）
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="紐約的天氣如何？")]
    )
):
    # 如果是最終回應，則印出內容
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## 存取追蹤資料

預設情況下，Monocle 在本地目錄 `./monocle` 中產生 JSON 追蹤檔案。檔案名稱格式為：

```
monocle_trace_{workflow_name}_{trace_id}_{timestamp}.json
```

每個追蹤檔案都包含一組符合 OpenTelemetry 標準的 Span，擷取內容包括：

- **Agent 執行 Span** - Agent 狀態、委派事件和執行流程
- **工具執行 Span** - 工具名稱、輸入參數和輸出結果
- **LLM 互動 Span** - 模型呼叫、提示詞（prompts）、回應以及 Token 使用量（如果使用 Gemini 或其他 LLM）

您可以使用任何相容 OpenTelemetry 的工具分析這些追蹤檔案，或編寫自定義分析腳本。

## 使用 VS Code 擴充功能視覺化追蹤

[Okahu Trace Visualizer](https://marketplace.visualstudio.com/items?itemName=OkahuAI.okahu-ai-observability) VS Code 擴充功能提供了一種互動方式，直接在 Visual Studio Code 中視覺化和分析 Monocle 產生的追蹤。

### 安裝

1. 開啟 VS Code
2. 按下 `Ctrl+P`（Mac 為 `Cmd+P`）開啟快速開啟
3. 貼上以下指令並按 Enter：

```
ext install OkahuAI.okahu-ai-observability
```

或者，您可以從 [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=OkahuAI.okahu-ai-observability) 安裝。

### 功能

該擴充功能提供：

- **自定義活動列面板** - 專用於追蹤檔案管理的側邊欄
- **互動式檔案樹** - 使用自定義 React UI 瀏覽並選擇追蹤檔案
- **分欄檢視分析** - 甘特圖視覺化與 JSON 資料檢視器並排顯示
- **即時通訊** - VS Code 與 React 組件之間的無縫資料流
- **VS Code 主題化** - 完全整合 VS Code 的淺色/深色主題

### 使用方法

1. 在啟用了 Monocle 追蹤的情況下執行您的 ADK 應用程式後，追蹤檔案將在 `./monocle` 目錄中產生
2. 從 VS Code 活動列開啟 Okahu Trace Visualizer 面板
3. 從互動式檔案樹中瀏覽並選擇追蹤檔案
4. 透過以下方式查看追蹤：
   - **甘特圖視覺化** - 查看 Span 的時間軸和層級結構
   - **JSON 資料檢視器** - 檢查詳細的 Span 屬性和事件
   - **Token 計數** - 查看 LLM 呼叫的 Token 使用量
   - **錯誤徽章** - 快速識別失敗的操作

![Monocle VS Code 擴充功能](https://google.github.io/adk-docs/assets/monocle-vs-code-ext.png)

## 哪些內容會被追蹤

Monocle 會自動從 Google ADK 擷取以下資訊：

- **Agent 執行**：Agent 狀態、委派事件和執行流程
- **工具調用**：工具名稱、輸入參數和輸出結果
- **Runner 執行**：請求上下文和整體執行流程
- **時間資訊**：每項操作的開始時間、結束時間和持續時間
- **錯誤資訊**：異常和錯誤狀態

所有追蹤均以 OpenTelemetry 格式產生，使其與任何相容 OTLP 的可觀測性後端相容。

## 支援與資源

- [Monocle 說明文件](https://docs.okahu.ai/monocle_overview/)
- [Monocle GitHub 儲存庫](https://github.com/monocle2ai/monocle)
- [Google ADK 旅遊 Agent 範例](https://github.com/okahu-demos/adk-travel-agent)
- [Discord 社群](https://discord.gg/D8vDbSUhJX)
