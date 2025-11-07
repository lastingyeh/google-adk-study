# 教學 11：內建工具與基礎 (Built-in Tools & Grounding)

**目標**：學習如何使用 Gemini 2.0+ 的內建工具進行網路基礎、定位服務和企業搜尋，讓您的代理程式能夠存取來自網際網路的最新資訊。

**先決條件**：無

**您將學到**：
- `google_search`
- `google_maps_grounding`
- `enterprise_web_search`
- `GoogleSearchAgentTool`

**完成時間**：45-60 分鐘

## 為何內建工具很重要

傳統的 AI 模型有知識截止日期——它們不知道最近發生的事件、當前新聞或即時資訊。內建工具透過允許模型**將其回應建立在當前的網路資料基礎上**來解決這個問題。

**主要優點**：
- **即時資訊**：存取最新新聞、事件和資料。
- **提高準確性**：透過引用權威來源減少捏造。
- **擴展知識**：超越模型的原始訓練資料。

**重要提示**：內建工具**僅適用於 Gemini 2.0+**，在舊版模型（1.5、1.0）上會引發錯誤。

## 1. Google 搜尋工具 (網路基礎)

### 什麼是 `google_search`？

`google_search` 是一個**內建工具**，允許 Gemini 2.0+ 模型搜尋網路並將結果整合到其回應中。與傳統工具不同，它在**模型內部**執行——沒有本地程式碼運行。

### 基本用法

```python
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import Runner

# 使用 google_search 建立代理程式
agent = Agent(
    model='gemini-2.0-flash', # 需要 Gemini 2.0+
    name='web_researcher',
    instruction='您是一個有用的助理，可以存取最新的網路資訊。',
    tools=[google_search] # 新增內建搜尋功能
)

# 執行代理程式 - 現在可以搜尋網路
runner = Runner()
result = runner.run(
    "2025 年量子計算的最新發展是什麼？",
    agent=agent
)

print(result.content.parts[0].text)
# 模型會自動搜尋網路並提供最新答案
```

**發生了什麼**：
1. 模型收到一個需要最新資訊的問題。
2. 它識別出 `google_search` 是解決此問題的工具。
3. 模型在內部執行搜尋，無需外部工具呼叫。
4. 搜尋結果用於產生準確、最新的回應。

### 內部運作原理

**來源**：`google/adk/tools/google_search_tool.py`

```python
# 內部實作 (簡化)
class GoogleSearchTool:
    def process_llm_request(self, llm_request):
        """將 google_search 新增到模型的工具清單中。"""
        # 新增內建搜尋工具
        llm_request.tools.append(
            types.Tool(google_search=types.GoogleSearch())
        )

        # 模型現在知道它可以搜尋網路
        return llm_request
```

**關鍵細節**：
- `GoogleSearchTool` 類別攔截對模型的請求。
- 它將 `google_search` 功能新增到模型的工具清單中。
- 這使得模型能夠在需要時自主決定使用網路搜尋。
- 回應中包含 `GroundingMetadata`，提供有關所執行搜尋的資訊。

### 基礎元資料 (Grounding Metadata)

當模型使用 `google_search` 時，它會儲存有關搜尋的元資料：

```python
from google.adk.agents import Agent, Runner
from google.adk.tools import google_search

agent = Agent(
    model='gemini-2.0-flash',
    tools=[google_search]
)

runner = Runner()
result = runner.run(
    "今天舊金山的天氣如何？",
    agent=agent
)

# 存取基礎元資料
# 在執行期間暫時儲存在狀態中
# 鍵：temp:_adk_grounding_metadata
```

**GroundingMetadata 結構**：
```json
{
    "web_search_queries": [
        "舊金山今天天氣",
        "舊金山當前溫度"
    ],
    // 其他基礎資訊...
}
```

### 模型相容性

```python
# ✅ 適用於 Gemini 2.0+
agent = Agent(model='gemini-2.0-flash', tools=[google_search])
agent = Agent(model='gemini-2.0-flash-exp', tools=[google_search])

# ❌ 在 Gemini 1.x 上會引發錯誤
agent = Agent(model='gemini-1.5-flash', tools=[google_search])
# 錯誤：google_search 需要 Gemini 2.0+
```

## 2. Google 地圖基礎工具

### 什麼是 `google_maps_grounding`？

`google_maps_grounding` 啟用基於位置的查詢——尋找附近地點、獲取路線、理解地理環境。

### 基本用法

```python
from google.adk.agents import Agent
from google.adk.tools import google_maps_grounding
from google.adk.runners import Runner

agent = Agent(
    model='gemini-2.0-flash', # 僅限 Gemini 2.0+
    name='location_assistant',
    instruction='幫助使用者處理基於位置的查詢。',
    tools=[google_maps_grounding]
)

runner = Runner()
result = runner.run(
    "紐約時代廣場 5 英里內最好的義大利餐廳有哪些？",
    agent=agent
)

print(result.content.parts[0].text)
# 模型使用地圖基礎獲取當前位置資料
```

### 使用案例

**導航**：
```python
result = runner.run(
    "如何從 JFK 機場搭乘大眾運輸工具到中央公園？",
    agent=agent
)
```

**本地探索**：
```python
result = runner.run(
    "尋找史丹佛大學附近現在營業的咖啡店。",
    agent=agent
)
```

**地理環境**：
```python
result = runner.run(
    "洛杉磯和聖地牙哥之間的距離是多少？",
    agent=agent
)
```

### 重要限制

**僅限 VertexAI API**：
```python
# ✅ 適用於 VertexAI
import os
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'my-project'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

agent = Agent(
    model='gemini-2.0-flash',
    tools=[google_maps_grounding]
)

# ❌ 不適用於 AI Studio API
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '0'
# 地圖基礎需要 VertexAI
```

### 條件式環境偵測

對於生產應用程式，根據環境實作條件式工具載入：

```python
from google.adk.agents import Agent
from google.adk.tools import google_search, google_maps_grounding
import os

def is_vertexai_enabled() -> bool:
    """透過環境變數檢查 VertexAI 是否已啟用。"""
    return os.environ.get('GOOGLE_GENAI_USE_VERTEXAI') == '1'

def get_available_grounding_tools():
    """根據環境獲取可用的基礎工具。"""
    tools = [google_search] # 始終可用

    # 僅在啟用 VertexAI 時新增地圖基礎
    if is_vertexai_enabled():
        tools.append(google_maps_grounding)

    return tools

def get_agent_capabilities_description() -> str:
    """根據可用工具獲取代理程式功能描述。"""
    capabilities = ["用於最新資訊的網路搜尋"]

    if is_vertexai_enabled():
        capabilities.append("基於位置的查詢和地圖基礎")

    return " 和 ".join(capabilities)

# 使用條件式工具建立代理程式
agent = Agent(
    model='gemini-2.0-flash',
    name='conditional_grounding_agent',
    instruction=f"""您是一個研究助理，可以存取 {get_agent_capabilities_description()}。

當被問到問題時：
1. 使用 google_search 尋找最新、準確的資訊
{"2. 在可用時使用 google_maps_grounding 進行基於位置的查詢" if is_vertexai_enabled() else ""}
{("3. " if is_vertexai_enabled() else "2. ")}根據搜尋結果提供清晰、真實的答案
{("4. " if is_vertexai_enabled() else "3. ")}始終引用資訊來自網路搜尋
{("5. " if is_vertexai_enabled() else "4. ")}如果資訊似乎過時或不確定，請提及這一點

要樂於助人、準確，並在您使用搜尋功能時註明。""",
    tools=get_available_grounding_tools()
)
```

這種方法確保您的代理程式在 AI Studio（僅網路搜尋）和 VertexAI（網路搜尋 + 地圖）環境中都能自動運作。

## 3. 企業網路搜尋工具

### 什麼是 `enterprise_web_search`？

`enterprise_web_search` 提供**符合企業規範的網路基礎**，並為企業環境提供額外控制。

**文件**：[企業網路基礎](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/web-grounding-enterprise)

### 基本用法

```python
from google.adk.agents import Agent
from google.adk.tools import enterprise_web_search
from google.adk.runners import Runner

agent = Agent(
    model='gemini-2.0-flash', # 僅限 Gemini 2+
    name='enterprise_assistant',
    instruction='使用符合企業規範的來源提供資訊。',
    tools=[enterprise_web_search]
)

runner = Runner()
result = runner.run(
    "最新的 GDPR 合規要求是什麼？",
    agent=agent
)

print(result.content.parts[0].text)
# 使用具有合規控制的企業搜尋
```

### 何時使用企業搜尋

**使用 `enterprise_web_search` 的時機**：
- 需要企業級安全性和合規性。
- 在受監管的行業中運作。
- 需要對搜尋來源進行精細控制。

**使用 `google_search` 的時機**：
- 用於一般用途的網路搜尋。
- 當不需要嚴格的企業控制時。
- 用於快速原型設計和開發。

## 4. GoogleSearchAgentTool (解決方案)

### 問題

**目前限制**：內建工具（如 `google_search`）**無法**與自訂函式工具在同一個代理程式中結合使用。

```python
# ❌ 這無法如預期運作
from google.adk.tools import google_search, FunctionTool

def my_custom_tool(query: str) -> str:
    return f"自訂結果：{query}"

agent = Agent(
    model='gemini-2.0-flash',
    tools=[
        google_search, # 內建工具
        FunctionTool(my_custom_tool) # 自訂工具
    ]
)
# 只有一種工具會運作
```

### 解決方案：GoogleSearchAgentTool

`GoogleSearchAgentTool` 建立一個帶有 `google_search` 的**子代理程式**，並將其包裝成一個常規工具。

**來源**：`google/adk/tools/google_search_agent_tool.py`

```python
from google.adk.agents import Agent
from google.adk.tools import GoogleSearchAgentTool, FunctionTool
from google.adk.runners import Runner

# 自訂工具
def calculate_tax(amount: float, rate: float) -> float:
    """計算金額的稅金。"""
    return amount * rate

# 建立 GoogleSearchAgentTool 包裝器
search_tool = GoogleSearchAgentTool()

# 現在您可以結合它們！
agent = Agent(
    model='gemini-2.0-flash',
    name='hybrid_assistant',
    instruction='使用網路搜尋和計算來回答問題。',
    tools=[
        search_tool, # 包裝的 google_search
        FunctionTool(calculate_tax) # 自訂工具
    ]
)

runner = Runner()

# 使用兩種工具
result = runner.run(
    "加州目前的銷售稅率是多少，100 美元的稅金是多少？",
    agent=agent
)

print(result.content.parts[0].text)
# 代理程式使用搜尋獲取稅率，使用計算獲取金額
```

### GoogleSearchAgentTool 的運作原理

```python
# 內部實作 (簡化)
class GoogleSearchAgentTool:
    def __init__(self):
        # 建立帶有 google_search 的子代理程式
        self.search_agent = Agent(
            model='gemini-2.0-flash',
            tools=[google_search]
        )

    async def _run_async_impl(self, query: str, tool_context):
        """透過子代理程式執行搜尋。"""
        runner = Runner()
        result = await runner.run_async(query, agent=self.search_agent)

        # 將基礎元資料轉發給父級
        if 'temp:_adk_grounding_metadata' in result.state:
            tool_context.invocation_context.state[
                'temp:_adk_grounding_metadata'
            ] = result.state['temp:_adk_grounding_metadata']

        return result.content.parts[0].text
```

### 輔助函式

```python
from google.adk.tools.google_search_agent_tool import create_google_search_agent

# 建立預先配置的搜尋代理程式
search_agent = create_google_search_agent()

# 作為子代理程式使用
main_agent = Agent(
    name='orchestrator',
    sub_agents=[search_agent],
    flow='sequential'
)
```

### 何時不再需要此解決方案

`# TODO(b/448114567): 當不再需要此解決方案時移除`
`# Google 正在努力允許內建 + 自訂工具一起使用`
`# 查看 ADK 版本以獲取更新`

## 5. 真實世界範例：研究助理

讓我們建立一個生產就緒的研究助理，它可以搜尋網路、處理結果並提供引用。

### 完整實作

```python
"""
帶有網路基礎的研究助理
搜尋網路、提取關鍵資訊、提供引用。
"""

import asyncio
import os
from datetime import datetime
from google.adk.agents import Agent, Runner
from google.adk.tools import google_search, FunctionTool, GoogleSearchAgentTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# 環境設定
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'


# 自訂工具：儲存研究筆記
async def save_research_notes(
    topic: str,
    findings: str,
    tool_context: ToolContext
) -> str:
    """將研究結果儲存為產物。"""

    # 建立研究文件
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    document = f"""
# 研究報告：{topic}
產生時間：{timestamp}

## 研究結果
{findings}

## 元資料
- 主題：{topic}
- 產生者：研究助理
- 模型：gemini-2.0-flash
    """.strip()

    # 儲存為產物
    filename = f"research_{topic.replace(' ', '_')}.md"
    version = await tool_context.save_artifact(
        filename=filename,
        part=types.Part.from_text(document)
    )

    return f"研究已儲存為 {filename} (版本 {version})"


# 自訂工具：提取關鍵事實
def extract_key_facts(text: str, num_facts: int = 5) -> list[str]:
    """從文本中提取關鍵事實 (簡化)。"""
    # 在生產中，使用更複雜的提取方法
    sentences = text.split('.')
    return sentences[:num_facts]


# 建立搜尋工具 (使用解決方案以與自訂工具混合使用)
search_tool = GoogleSearchAgentTool()

# 建立研究助理
research_assistant = Agent(
    model='gemini-2.0-flash',
    name='research_assistant',
    description='進行網路研究並彙編研究結果',
    instruction="""
您是一位專業的研究助理，可以存取：
1. 透過 search_tool 進行網路搜尋
2. 透過 extract_key_facts 進行事實提取
3. 透過 save_research_notes 儲存筆記

當給定一個研究主題時：
1. 使用 search_tool 尋找最新資訊
2. 使用 extract_key_facts 提取關鍵事實
3. 將研究結果綜合為清晰的摘要
4. 使用 save_research_notes 儲存研究
5. 提供帶有要點的摘要

要全面但簡潔。始終引用您的來源。
    """.strip(),
    tools=[
        search_tool,
        FunctionTool(extract_key_facts),
        FunctionTool(save_research_notes)
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3, # 較低以確保事實準確性
        max_output_tokens=2048
    )
)


async def conduct_research(topic: str):
    """對主題進行全面研究。"""

    print(f"\n{'='*60}")
    print(f"研究主題：{topic}")
    print(f"{'='*60}\n")

    runner = Runner()

    # 執行研究
    result = await runner.run_async(
        f"研究此主題並提供全面摘要：{topic}",
        agent=research_assistant
    )

    # 顯示結果
    print("\n📊 研究結果：\n")
    print(result.content.parts[0].text)

    # 檢查是否有基礎元資料
    if 'temp:_adk_grounding_metadata' in result.state:
        metadata = result.state['temp:_adk_grounding_metadata']
        if 'web_search_queries' in metadata:
            print("\n\n🔍 使用的搜尋查詢：")
            for query in metadata['web_search_queries']:
                print(f" - {query}")

    print(f"\n{'='*60}\n")


# 範例用法
async def main():
    """執行研究範例。"""

    # 研究最新技術
    await conduct_research(
        "2025 年量子計算的突破"
    )

    await asyncio.sleep(2)

    # 研究時事
    await conduct_research(
        "再生能源技術的最新發展"
    )

    await asyncio.sleep(2)

    # 研究科學主題
    await conduct_research(
        "CRISPR 基因編輯在醫學中的應用"
    )


if __name__ == '__main__':
    asyncio.run(main())
```

## 6. 記憶體工具 - 持久狀態管理

**來源**：`google/adk/tools/__init__.py`, `google/adk/tools/memory_tools.py`

ADK 提供內建工具來管理跨代理程式會話的持久記憶體。這些工具使代理程式能夠儲存、檢索和管理超越單次對話的上下文。

### `load_memory` - 載入持久記憶體

將先前儲存的記憶體狀態載入到目前會話中。

```python
from google.adk.agents import Agent
from google.adk.tools import load_memory
from google.adk.runners import Runner

agent = Agent(
    model='gemini-2.5-flash',
    name='memory_agent',
    instruction='您可以使用 load_memory 記住先前對話的資訊。',
    tools=[load_memory]
)

runner = Runner()
result = runner.run(
    "載入我先前的對話歷史並總結我們討論的內容。",
    agent=agent
)
```

### `preload_memory` - 初始化記憶體

在代理程式執行開始前預先載入記憶體狀態。

```python
from google.adk.tools import preload_memory

agent = Agent(
    model='gemini-2.5-flash',
    name='preloaded_agent',
    instruction='您可以存取預先載入的使用者偏好和上下文。',
    tools=[preload_memory]
)

# 記憶體在第一輪對話前自動載入
```

### `load_artifacts` - 存取儲存的資料

將先前儲存的產物（文件、檔案、資料）載入到對話中。

```python
from google.adk.tools import load_artifacts

agent = Agent(
    model='gemini-2.5-flash',
    name='artifact_agent',
    instruction='您可以使用 load_artifacts 載入和引用儲存的文件。',
    tools=[load_artifacts]
)

runner = Runner()
result = runner.run(
    "載入上週的研究文件並從我們上次離開的地方繼續。",
    agent=agent
)
```

## 7. 工作流程工具 - 代理程式控制流程

**來源**：`google/adk/tools/__init__.py`, `google/adk/tools/workflow_tools.py`

工作流程工具允許代理程式控制自己的執行流程並與使用者協調互動。

### `exit_loop` - 終止執行

允許代理程式決定何時停止循環中的執行。

```python
from google.adk.agents import Agent
from google.adk.tools import exit_loop

agent = Agent(
    model='gemini-2.5-flash',
    name='loop_agent',
    instruction="""
處理任務直到完成，然後呼叫 exit_loop。
您決定工作何時完成。
    """,
    tools=[exit_loop]
)

# 代理程式在滿意時會呼叫 exit_loop
```

### `get_user_choice` - 請求使用者輸入

在執行期間請求明確的使用者輸入。

```python
from google.adk.tools import get_user_choice

agent = Agent(
    model='gemini-2.5-flash',
    name='interactive_agent',
    instruction="""
當您需要澄清時，使用 get_user_choice 詢問使用者。
在繼續之前等待他們的回應。
    """,
    tools=[get_user_choice]
)

runner = Runner()
result = runner.run(
    "幫我規劃一個假期。",
    agent=agent
)

# 代理程式可能會呼叫：get_user_choice("您的預算是多少：高、中或低？")
# 使用者提供答案
# 代理程式根據該資訊繼續
```

### `transfer_to_agent` - 代理程式交接

在多代理程式系統中將控制權轉移給另一個代理程式。

```python
from google.adk.agents import Agent
from google.adk.tools import transfer_to_agent

# 專家代理程式
coding_agent = Agent(
    model='gemini-2.5-pro',
    name='coding_expert',
    instruction='您是一位專業的程式設計師。'
)

research_agent = Agent(
    model='gemini-2.5-flash',
    name='research_expert',
    instruction='您是一位研究專家。'
)

# 路由器代理程式
router_agent = Agent(
    model='gemini-2.5-flash',
    name='router',
    instruction="""
分析使用者的請求並轉移給適當的專家：
- 對於程式設計問題，轉移給 coding_expert
- 對於研究問題，轉移給 research_expert
使用 transfer_to_agent 工具。
    """,
    sub_agents=[coding_agent, research_agent],
    tools=[transfer_to_agent]
)

runner = Runner()
result = runner.run(
    "解釋快速排序的原理並用 Python 實作。",
    agent=router_agent
)

# 路由器會自動轉移給 coding_expert
```

## 8. 上下文工具 - 外部資料存取

**來源**：`google/adk/tools/url_context_tool.py`

上下文工具使代理程式能夠在執行期間存取外部資料來源。

### `url_context` - 從 URL 載入內容

從 URL 獲取並整合內容到對話中。

```python
from google.adk.agents import Agent
from google.adk.tools import url_context
from google.adk.runners import Runner

agent = Agent(
    model='gemini-2.5-flash',
    name='url_agent',
    instruction='您可以使用 url_context 從 URL 載入內容來回答問題。',
    tools=[url_context]
)

runner = Runner()
result = runner.run(
    "總結 https://example.com/article 的內容",
    agent=agent
)

# 代理程式呼叫 url_context("https://example.com/article")
# 內容被載入和分析
```

## 9. 企業工具 - 生產系統

**來源**：`google/adk/tools/__init__.py`, `google/adk/tools/vertex_ai_search_tool.py`

企業工具將代理程式連接到 Google Cloud 生產服務。

### `VertexAiSearchTool` - 企業搜尋

連接到 Vertex AI Search（前身為 Discovery Engine）以進行企業級搜尋。

```python
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
from google.adk.runners import Runner

# 建立 Vertex AI Search 工具
search_tool = VertexAiSearchTool(
    project_id='your-project-id',
    location='global',
    data_store_id='your-datastore-id'
)

agent = Agent(
    model='gemini-2.5-flash',
    name='enterprise_search_agent',
    instruction='使用 vertex_ai_search 搜尋企業知識庫。',
    tools=[search_tool]
)

runner = Runner()
result = runner.run(
    "尋找與遠端工作相關的公司政策。",
    agent=agent
)
```

## 10. 整合包裝器 - 第三方工具

**來源**：`google/adk/tools/__init__.py`

ADK 提供包裝器以整合第三方框架工具。

### `LangchainTool` - LangChain 整合

將任何 LangChain 工具包裝起來，以便在 ADK 代理程式中使用。

```python
from google.adk.tools import LangchainTool
from google.adk.agents import Agent
from langchain_community.tools import TavilySearchResults

# 建立 LangChain 工具
tavily = TavilySearchResults(max_results=5)

# 為 ADK 包裝
adk_tavily = LangchainTool(tool=tavily)

agent = Agent(
    model='gemini-2.5-flash',
    name='langchain_agent',
    instruction='使用 tavily_search 進行網路搜尋。',
    tools=[adk_tavily]
)
```

### `CrewaiTool` - CrewAI 整合

為 ADK 包裝 CrewAI 工具。

```python
from google.adk.tools import CrewaiTool
from crewai_tools import SerperDevTool

# 建立 CrewAI 工具
serper = SerperDevTool(n_results=10)

# 為 ADK 包裝 (必須提供名稱和描述！)
adk_serper = CrewaiTool(
    name="InternetNewsSearch",
    description="在網路上搜尋新聞文章",
    tool=serper
)

agent = Agent(
    model='gemini-2.5-flash',
    name='crewai_agent',
    instruction='使用 InternetNewsSearch 尋找新聞。',
    tools=[adk_serper]
)
```

## 11. 工具類別與工具集

**來源**：`google/adk/tools/__init__.py`

ADK 提供基礎類別和工具集，用於進階工具管理。

### `FunctionTool` - 函式包裝器

將常規 Python 函式包裝為工具。

### `AgentTool` - 代理程式即工具

將整個代理程式包裝為另一個代理程式的工具。

### `MCPToolset` - 模型上下文協定

存取外部 MCP 伺服器。

### `OpenAPIToolset` - REST API 整合

從 OpenAPI 規範自動產生工具。

## 12. 完整的內建工具參考

**來源**：`google/adk/tools/__init__.py`

以下是所有 ADK 內建工具的完整清單：

### 基礎工具 (3)
- `google_search`
- `google_maps_grounding`
- `enterprise_web_search`

### 記憶體工具 (3)
- `load_memory`
- `preload_memory`
- `load_artifacts`

### 工作流程工具 (3)
- `exit_loop`
- `get_user_choice`
- `transfer_to_agent`

### 上下文工具 (1)
- `url_context`

### 企業工具 (2)
- `VertexAiSearchTool`
- `DiscoveryEngineSearchTool`

### 整合包裝器 (2)
- `LangchainTool`
- `CrewaiTool`

### 工具類別 (5)
- `FunctionTool`
- `AgentTool`
- `GoogleSearchAgentTool`
- `Tool`
- `AsyncTool`

### 工具集 (3)
- `MCPToolset`
- `OpenAPIToolset`
- `Toolset`

## 13. 真實世界範例：綜合代理程式系統

讓我們建立一個使用多個內建工具類別的代理程式。

```python
"""
綜合多工具代理程式
展示：基礎、記憶體、工作流程、上下文、企業工具
"""

import os
import asyncio
from google.adk.agents import Agent, Runner
from google.adk.tools import (
    google_search,
    load_memory,
    load_artifacts,
    exit_loop,
    transfer_to_agent,
    url_context,
    FunctionTool
)
from google.genai import types

# 環境設定
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

# 自訂分析函式
def analyze_data(data: str) -> dict:
    """分析資料並回傳洞察。"""
    # 簡化分析
    word_count = len(data.split())
    return {
        "status": "success",
        "report": f"分析：{word_count} 字，資料品質：良好"
    }

# 專家：研究代理程式
research_agent = Agent(
    model='gemini-2.5-flash',
    name='research_specialist',
    instruction="""
您是一位研究專家。使用 google_search 和 url_context
收集全面的資訊。使用 load_artifacts 儲存重要發現。
    """,
    tools=[google_search, url_context, load_artifacts]
)

# 專家：資料分析師
analyst_agent = Agent(
    model='gemini-2.5-pro',
    name='data_analyst',
    instruction="""
您是一位資料分析師。使用 analyze_data 處理資訊。
提供詳細的洞察和建議。
    """,
    tools=[FunctionTool(analyze_data)]
)

# 主要協調器
orchestrator = Agent(
    model='gemini-2.5-flash',
    name='orchestrator',
    description='多工具代理程式系統',
    instruction="""
您協調研究和分析任務：

1. 如果繼續工作，使用 load_memory 載入先前的上下文
2. 對於研究任務，轉移給 research_specialist
3. 對於資料分析，轉移給 data_analyst
4. 當工作完成時，呼叫 exit_loop

您根據使用者需求決定工作流程。
    """,
    sub_agents=[research_agent, analyst_agent],
    tools=[
        load_memory,
        transfer_to_agent,
        exit_loop
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3
    )
)


async def main():
    """執行綜合代理程式系統。"""

    runner = Runner()

    print("="*60)
    print("綜合代理程式系統")
    print("="*60 + "\n")

    query = """
研究量子計算的最新發展，
分析關鍵技術突破，
並提供策略建議。
    """

    result = await runner.run_async(query, agent=orchestrator)

    print("\n📊 結果：\n")
    print(result.content.parts[0].text)

    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
```

## 14. 最佳實踐

- **使用適當的模型**：內建工具需要 Gemini 2.0+。
- **正確處理混合工具**：使用 `GoogleSearchAgentTool` 來混合內建和自訂工具。
- **為事實設定低溫**：對於事實性查詢，使用較低的溫度以獲得更確定的結果。
- **提供清晰的指示**：指導模型何時以及如何使用搜尋工具。
- **檢查 VertexAI 要求**：`google_maps_grounding` 需要 VertexAI 環境。

## 15. 疑難排解

- **錯誤："google_search requires Gemini 2.0+"**：請確保您使用的是 Gemini 2.0 或更高版本的模型。
- **錯誤："Built-in tools not working with custom tools"**：使用 `GoogleSearchAgentTool` 包裝器。
- **錯誤："Maps grounding not available"**：請確保您使用的是 VertexAI API，而不是 AI Studio API。
- **問題："Search results not appearing in response"**：確保您的提示需要最新資訊，並在代理程式的指令中明確指示使用搜尋。
- **問題："Grounding metadata not accessible"**：元資料是暫時的，只能在執行期間或執行後立即存取。

## 程式碼實現 (Code Implementation)
- grounding-agent：[程式碼連結](../../../python/agents/grounding-agent/README.md)