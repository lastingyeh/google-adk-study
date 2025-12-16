# 掌握 Google Interactions API：通往 Gemini 模型與 Deep Research Agent 的統一閘道 (Mastering Google's Interactions API: A Unified Gateway to Gemini Models and Deep Research Agent)

> 📝 **原文翻譯自 Raphaël MANSUY 的 Blog**：[Mastering Google's Interactions API: A Unified Gateway to Gemini Models and Deep Research Agent](https://raphaelmansuy.github.io/adk_training/blog/interactions-api-deep-research)

> 🖼️ 圖片來源：[interaction](https://github.com/raphaelmansuy/adk_training/tree/main/docs/blog/assets/interraction)

## 簡介 (Introduction)

AI 開發領域正在從無狀態的請求-回應模式轉變為**有狀態、多輪對話的代理工作流程 (stateful, multi-turn agentic workflows)**。Google 全新的 **Interactions API** 專為這個新時代設計，提供了一個統一的介面，可同時存取原始 Gemini 模型與完全託管的 **Deep Research Agent**。

**一句話總結**：Interactions API 是一個與 Gemini 模型及代理互動的統一端點，具備伺服器端狀態管理、長執行任務的背景執行功能，並原生支援 Deep Research Agent。

![Interactions API Overview](./assets/interaction/interaction.png)

## 為什麼 Interactions API 很重要 (Why the Interactions API Matters)

### 從 generateContent 到 Interactions 的演進 (The Evolution from generateContent to Interactions)

原本的 `generateContent` API 是為無狀態的請求-回應文字生成而設計，非常適合聊天機器人和簡單的補全任務。但隨著 AI 應用程式向代理模式演進，開發者需要更複雜的功能：

| 挑戰 (Challenge)                    | generateContent                       | Interactions API                                           |
| :---------------------------------- | :------------------------------------ | :--------------------------------------------------------- |
| **狀態管理 (State Management)**     | 僅限客戶端 (Client-side only)         | 透過 `previous_interaction_id` 進行伺服器端管理            |
| **長執行任務 (Long-running Tasks)** | 逾時 (Timeouts)                       | 具備輪詢功能的背景執行 (Background execution with polling) |
| **代理存取 (Agent Access)**         | 僅限模型 (Models only)                | 模型與內建代理 (Models AND built-in agents)                |
| **工具編排 (Tool Orchestration)**   | 基本函式呼叫 (Basic function calling) | 原生支援 MCP、Google Search、程式碼執行                    |
| **對話歷史 (Conversation History)** | 手動管理 (Manual management)          | 透過 session IDs 自動管理                                  |

### 關鍵優勢 (Key Benefits)

1.  **伺服器端狀態管理 (Server-Side State Management)**：將對話歷史卸載至伺服器，降低客戶端複雜度。
2.  **背景執行 (Background Execution)**：執行長達數小時的研究任務，無需維持客戶端連線。
3.  **統一端點 (Unified Endpoint)**：模型 (`gemini-3-pro-preview`) 與代理 (`deep-research-pro-preview-12-2025`) 使用相同的 API。
4.  **遠端 MCP 支援 (Remote MCP Support)**：模型可以直接呼叫 Model Context Protocol 伺服器。
5.  **改進的快取命中率 (Improved Cache Hits)**：伺服器管理的狀態能實現更好的上下文快取，降低成本。

## 快速開始 (Getting Started)

### 先決條件 (Prerequisites)

```bash
# 安裝最新的 google-genai SDK (需要 1.55.0+)
pip install "google-genai>=1.55.0"

# 設定您的 API 金鑰
export GOOGLE_API_KEY="your-api-key-here"
```

### 基本互動 (Basic Interaction)

使用 Interactions API 最簡單的方式：

```python
from google import genai

client = genai.Client()

# 建立一個互動 (Create an interaction)
interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="Tell me a short joke about programming." # 告訴我一個關於程式設計的短笑話
)

print(interaction.outputs[-1].text)
```

ℹ️ SDK 需求

- **Python**: `google-genai>=1.55.0`
- **JavaScript**: `@google/genai>=1.33.0`

## 有狀態對話 (Stateful Conversations)

其中一個最強大的功能是伺服器端狀態管理。您不需要在每次請求時發送完整的對話歷史，只需引用前一次的互動：

### 伺服器端狀態 (建議使用) (Server-Side State (Recommended))

```python
from google import genai

client = genai.Client()

# 第一輪對話
interaction1 = client.interactions.create(
    model="gemini-2.5-flash",
    input="Hi, my name is Alex." # 嗨，我的名字是 Alex
)
print(f"Model: {interaction1.outputs[-1].text}")

# 第二輪對話 - 上下文自動保留！
interaction2 = client.interactions.create(
    model="gemini-2.5-flash",
    input="What is my name?", # 我的名字是什麼？
    previous_interaction_id=interaction1.id
)
print(f"Model: {interaction2.outputs[-1].text}")
# 輸出: "Your name is Alex."
```

### 伺服器端狀態的優點 (Benefits of Server-Side State)

- **降低 Token 成本**：無需重新發送完整的歷史記錄。
- **改進的快取命中率**：伺服器可以更有效地快取上下文。
- **更簡單的客戶端程式碼**：無需本地狀態管理。
- **可靠的上下文**：伺服器確保一致性。

### 檢索過去的互動 (Retrieving Past Interactions)

```python
# 透過 ID 取得先前的互動
previous = client.interactions.get("<YOUR_INTERACTION_ID>")
print(previous.outputs[-1].text)
```

## Deep Research Agent

**Deep Research Agent** (`deep-research-pro-preview-12-2025`) 是自主研究任務的遊戲規則改變者。由 Gemini 3 Pro 驅動，它能自主規劃、執行並綜合多步驟的研究任務。

### 何時使用 Deep Research (When to Use Deep Research)

| 使用案例 (Use Case)   | Deep Research                    | 標準模型 (Standard Model) |
| :-------------------- | :------------------------------- | :------------------------ |
| **延遲 (Latency)**    | 分鐘級 (非同步)                  | 秒級                      |
| **流程 (Process)**    | 規劃 → 搜尋 → 閱讀 → 迭代 → 輸出 | 生成 → 輸出               |
| **輸出 (Output)**     | 附帶引用的詳細報告               | 對話式文字                |
| **適用於 (Best For)** | 市場分析、盡職調查、文獻回顧     | 聊天、資訊擷取、創意寫作  |

### Deep Research 基礎用法 (Basic Deep Research)

```python
import time
from google import genai

client = genai.Client()

# 在背景開始研究
interaction = client.interactions.create(
    input="研究 2025 年 AI 程式碼助理的競爭格局",
    agent="deep-research-pro-preview-12-2025",
    background=True  # 代理必須設定為 True
)

print(f"Research started: {interaction.id}")

# 輪詢完成狀態
while True:
    interaction = client.interactions.get(interaction.id)
    print(f"Status: {interaction.status}")

    if interaction.status == "completed":
        print("\n📊 Research Report:\n")
        print(interaction.outputs[-1].text)
        break
    elif interaction.status == "failed":
        print(f"Research failed: {interaction.error}")
        break

    time.sleep(10)  # 每 10 秒輪詢一次
```

### 具備進度更新的串流 Deep Research (Streaming Deep Research with Progress Updates)

要在研究過程中獲得即時進度更新：

```python
from google import genai

client = genai.Client()

stream = client.interactions.create(
    input="研究 Google TPU 的歷史",
    agent="deep-research-pro-preview-12-2025",
    background=True,
    stream=True,
    agent_config={
        "type": "deep-research",
        "thinking_summaries": "auto"  # 啟用思維串流
    }
)

interaction_id = None
last_event_id = None

for chunk in stream:
    if chunk.event_type == "interaction.start":
        interaction_id = chunk.interaction.id
        print(f"🚀 Research started: {interaction_id}")

    if chunk.event_id:
        last_event_id = chunk.event_id

    if chunk.event_type == "content.delta":
        if chunk.delta.type == "text":
            print(chunk.delta.text, end="", flush=True)
        elif chunk.delta.type == "thought_summary":
            print(f"💭 Thought: {chunk.delta.content.text}", flush=True)

    elif chunk.event_type == "interaction.complete":
        print("\n✅ Research Complete")
```

### 自訂格式的研究 (Research with Custom Formatting)

您可以使用特定的格式化指令來引導代理的輸出：

```python
prompt = """
提示詞翻譯：
研究電動車電池的競爭格局。
將輸出格式化為技術報告，包含：
1. 執行摘要 (最多 200 字)
2. 主要參與者 (包含比較表，欄位：公司、產能、化學成分、市佔率)
3. 供應鏈風險 (列點)
4. 未來展望 (2025-2030)
使用清晰的標題並為所有主張包含引用。
"""

interaction = client.interactions.create(
    input=prompt,
    agent="deep-research-pro-preview-12-2025",
    background=True
)
```

### 後續問題 (Follow-up Questions)

在研究完成後繼續對話：

```python
# 研究完成後
follow_up = client.interactions.create(
    input="Can you elaborate on the third key player you mentioned?", # 你能詳細說明你提到的第三個主要參與者嗎？
    model="gemini-3-pro-preview",  # 可以使用模型進行後續追問
    previous_interaction_id=completed_interaction.id
)
print(follow_up.outputs[-1].text)
```

## Interactions API 的函式呼叫 (Function Calling with Interactions API)

Interactions API 提供強大的函式呼叫功能：

```python
from google import genai

client = genai.Client()

# 定義工具
def get_weather(location: str) -> str:
    """Gets current weather for a location."""
    # 這裡實作您的邏輯
    return f"The weather in {location} is sunny and 72°F."

weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": "Gets the weather for a given location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA"
            }
        },
        "required": ["location"]
    }
}

# 發送帶有工具的請求
interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="What is the weather in Paris?", # 巴黎的天氣如何？
    tools=[weather_tool]
)

# 處理工具呼叫
for output in interaction.outputs:
    if output.type == "function_call":
        print(f"Tool Call: {output.name}({output.arguments})")

        # 執行工具
        result = get_weather(**output.arguments)

        # 將結果回傳
        interaction = client.interactions.create(
            model="gemini-2.5-flash",
            previous_interaction_id=interaction.id,
            input=[{
                "type": "function_result",
                "name": output.name,
                "call_id": output.id,
                "result": result
            }]
        )
        print(f"Response: {interaction.outputs[-1].text}")
```

## 內建工具 (Built-in Tools)

Interactions API 提供存取強大的內建工具：

### Google Search Grounding

```python
interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="誰贏得了 2024 年超級盃?",
    tools=[{"type": "google_search"}]
)

# 取得文字輸出 (過濾搜尋結果)
text_output = next((o for o in interaction.outputs if o.type == "text"), None)
if text_output:
    print(text_output.text)
```

### 程式碼執行 (Code Execution)

```python
interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="計算第 50 個費氏數列數字",
    tools=[{"type": "code_execution"}]
)
print(interaction.outputs[-1].text)
```

### URL Context

```python
interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="總結這個網址的內容 `https://google.github.io/adk-docs/`",
    tools=[{"type": "url_context"}]
)
print(interaction.outputs[-1].text)
```

### 遠端 MCP 伺服器 (Remote MCP Servers)

```python
mcp_server = {
    "type": "mcp_server",
    "name": "weather_service",
    "url": "https://your-mcp-server.example.com/mcp"
}

interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="紐約的天氣如何？",
    tools=[mcp_server]
)
print(interaction.outputs[-1].text)
```

## 與 Google ADK 整合 (Integration with Google ADK)

Interactions API 與 Agent Development Kit (ADK) 無縫整合：

### 使用 Interactions 後端的 ADK Agent (ADK Agent with Interactions Backend)

```python
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.google_search_tool import GoogleSearchTool

def get_current_weather(location: str) -> dict:
    """Get weather for a location."""
    return {
        "status": "success",
        "location": location,
        "temperature": "72°F",
        "conditions": "Sunny"
    }

# 建立啟用 Interactions API 的 Agent

root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        use_interactions_api=True  # 啟用 Interactions API!
    ),
    name="interactions_enabled_agent",
    description="一個由 Interactions API 驅動的代理",
    instruction="""
    你是一個樂於助人的助理，可以存取：
    - 用於獲取最新資訊的 Google 搜尋
    - 用於地點查詢的天氣資料

    請務必提供準確且來源可靠的資訊。""",
    tools=[
        GoogleSearchTool(bypass_multi_tools_limit=True),
        get_current_weather,
    ],
)
```

### ADK 開發者的優勢 (Benefits for ADK Developers)

1.  **自動狀態管理**：ADK 為您處理 `previous_interaction_id`。
2.  **背景任務支援**：長執行代理不會逾時。
3.  **原生思維處理**：存取模型推理鏈。
4.  **統一工具體驗**：相同的工具適用於模型和代理。

## 多模態功能 (Multimodal Capabilities)

Interactions API 支援多模態輸入：

### 影像理解 (Image Understanding)

```python
import base64
from pathlib import Path

with open("image.png", "rb") as f:
    base64_image = base64.b64encode(f.read()).decode('utf-8')

interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input=[
        {"type": "text", "text": "Describe what you see in this image."}, # 描述你在這張圖片中看到什麼
        {"type": "image", "data": base64_image, "mime_type": "image/png"}
    ]
)
print(interaction.outputs[-1].text)
```

### 影像生成 (Image Generation)

```python
interaction = client.interactions.create(
    model="gemini-3-pro-image-preview",
    input="Generate an image of a futuristic AI research lab.", # 生成一張未來 AI 研究實驗室的圖片
    response_modalities=["IMAGE"]
)

for output in interaction.outputs:
    if output.type == "image":
        with open("generated_lab.png", "wb") as f:
            f.write(base64.b64decode(output.data))
        print("Image saved!")
```

## 結構化輸出 (Structured Output)

強制執行特定的 JSON 輸出結構描述：

```python
from pydantic import BaseModel, Field
from typing import Literal

class ContentModeration(BaseModel):
    is_safe: bool = Field(description="Whether the content is safe")
    category: Literal["safe", "spam", "inappropriate", "harmful"]
    confidence: float = Field(ge=0, le=1, description="Confidence score")
    reason: str = Field(description="Explanation for the classification")

interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="Moderate: 'Free money! Click here to claim your prize!'", # 審核：'免費金錢！點擊這裡領取獎品！'
    response_format=ContentModeration.model_json_schema()
)

result = ContentModeration.model_validate_json(interaction.outputs[-1].text)
print(f"Safe: {result.is_safe}, Category: {result.category}")
```

## 資料儲存與保留 (Data Storage and Retention)

儲存互動的重要考量：

| 層級 (Tier)     | 保留期限 (Retention Period) |
| :-------------- | :-------------------------- |
| **付費 (Paid)** | 55 天                       |
| **免費 (Free)** | 1 天                        |

### 選擇不儲存 (Opting Out of Storage)

```python
# 停用儲存 (不能與 background=True 一起使用)
interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="Process this privately", # 私密處理
    store=False  # 選擇不儲存
)
```

### 刪除互動 (Deleting Interactions)

```python
# 刪除特定互動
client.interactions.delete(interaction_id="<INTERACTION_ID>")
```

## 最佳實務 (Best Practices)

### 1. 對話使用伺服器端狀態 (Use Server-Side State for Conversations)

```python
# ✅ Good: 伺服器管理歷史記錄
interaction2 = client.interactions.create(
    model="gemini-2.5-flash",
    input="Continue our discussion",
    previous_interaction_id=interaction1.id
)

# ❌ Avoid: 每次發送完整的歷史記錄
interaction2 = client.interactions.create(
    model="gemini-2.5-flash",
    input=[...entire_conversation_history...]  # 昂貴！
)
```

### 2. 代理務必使用 background=True (Always Use background=True for Agents)

```python
# ✅ 代理 (如 Deep Research) 必須設定
interaction = client.interactions.create(
    agent="deep-research-pro-preview-12-2025",
    input="Research task",
    background=True
)
```

### 3. 以彈性處理長執行任務 (Handle Long-Running Tasks with Resilience)

```python
import time

def run_research_with_retry(prompt: str, max_retries: int = 3):
    """Run research with automatic retry on failure."""
    interaction = client.interactions.create(
        agent="deep-research-pro-preview-12-2025",
        input=prompt,
        background=True
    )

    retries = 0
    while retries < max_retries:
        try:
            while True:
                status = client.interactions.get(interaction.id)
                if status.status == "completed":
                    return status.outputs[-1].text
                elif status.status == "failed":
                    raise Exception(status.error)
                time.sleep(10)
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                raise
            time.sleep(30)
```

### 4. 在對話中混合使用模型與代理 (Mix Models and Agents in Conversations)

```python
# 從 Deep Research 開始
research = client.interactions.create(
    agent="deep-research-pro-preview-12-2025",
    input="量子計算的最新進展",
    background=True
)
# ... 輪詢完成狀態 ...

# 使用標準模型進行後續追問
summary = client.interactions.create(
    model="gemini-2.5-flash",
    input="目的為非技術受眾總結重點", #
    previous_interaction_id=research.id
)
```

## 支援的模型與代理 (Supported Models and Agents)

| 名稱 (Name)           | 類型 (Type) | 識別碼 (Identifier)                 |
| :-------------------- | :---------- | :---------------------------------- |
| Gemini 2.5 Pro        | Model       | `gemini-2.5-pro`                    |
| Gemini 2.5 Flash      | Model       | `gemini-2.5-flash`                  |
| Gemini 2.5 Flash-lite | Model       | `gemini-2.5-flash-lite`             |
| Gemini 3 Pro Preview  | Model       | `gemini-3-pro-preview`              |
| Deep Research Preview | Agent       | `deep-research-pro-preview-12-2025` |

## 目前限制 (Current Limitations)

⚠️ warning Beta 狀態
Interactions API 處於 **public beta** 階段。功能和結構描述可能會變更。

1.  **尚未支援 (Not Yet Supported)**：

    - 使用 Google Maps 進行 Grounding
    - 電腦使用 (Computer Use)
    - 在單一請求中結合 MCP + 函式呼叫 + 內建工具

2.  **Deep Research 特定限制 (Deep Research Specific)**：

    - 最長研究時間：60 分鐘 (大多數在約 20 分鐘內完成)
    - 無自訂函式呼叫工具
    - 無結構化輸出或計畫批准
    - 不支援音訊輸入

3.  **儲存需求 (Storage Requirements)**：
    - `background=True` 需要 `store=True`

## 遷移指南 (Migration Guide)

### 何時使用 Interactions API vs generateContent (When to Use Interactions API vs generateContent)

| 情境 (Scenario)                                | 建議 API (Recommended API) |
| :--------------------------------------------- | :------------------------- |
| 簡單文字補全                                   | `generateContent`          |
| 標準聊天機器人                                 | `generateContent`          |
| 生產關鍵任務 (Production critical)             | `generateContent`          |
| 代理工作流程 (Agentic workflows)               | **Interactions API**       |
| 長執行研究 (Long-running research)             | **Interactions API**       |
| 複雜工具編排 (Complex tool orchestration)      | **Interactions API**       |
| 數小時的背景任務 (Multi-hour background tasks) | **Interactions API**       |
| MCP 伺服器整合 (MCP server integration)        | **Interactions API**       |

## 資源 (Resources)

- [Interactions API 文件](https://ai.google.dev/gemini-api/docs/interactions)
- [Deep Research Agent 指南](https://ai.google.dev/gemini-api/docs/deep-research)
- [ADK 文件](https://google.github.io/adk-docs/)
- [ADK Interactions 範例](https://github.com/google/adk-python/tree/main/contributing/samples/interactions_api)
- [Google AI Studio](https://aistudio.google.com/apikey) (取得您的 API 金鑰)

## 結論 (Conclusion)

Interactions API 代表了我們建構 AI 應用程式方式的重大演進。透過提供：

- **伺服器端狀態管理**，實現更簡單、更可靠的對話
- **背景執行**，用於長執行代理任務
- **統一存取**，同時支援模型與專門代理 (如 Deep Research)
- **原生工具整合**，支援 MCP、Google Search 等

...開發者現在可以使用更少的樣板程式碼和更好的可靠性來建構複雜的 AI 系統。

無論您是在建構研究助理、多輪客戶支援代理，還是複雜的代理工作流程，Interactions API 都為下一代 AI 應用程式提供了基礎。
