# 教學 28：透過 LiteLLM 使用其他大型語言模型 (Tutorial 28: Using Other LLMs with LiteLLM)

**目標**：透過 LiteLLM 在您的 ADK 代理程式中使用 OpenAI、Claude、Ollama 及其他大型語言模型

**先決條件**：

- 教學 01 (Hello World 代理程式)
- 教學 22 (模型選擇與設定)
- 對 API 金鑰與環境變數有基本了解

**您將學到**：

- 在 ADK 中使用 OpenAI 模型 (GPT-4o-mini)
- 在 ADK 中使用 Anthropic Claude 模型 (3.7 Sonnet)
- 透過 Ollama 執行本地模型 (Granite 4) 以保護隱私
- 多供應商比較與成本優化
- 何時不該使用 LiteLLM
- 跨供應商開發的最佳實踐

**來源**：`google/adk/models/lite_llm.py`、
`contributing/samples/hello_world_litellm/`、
`contributing/samples/hello_world_ollama/`

---

## 為什麼要使用 LiteLLM？ (Why Use LiteLLM?)

**LiteLLM** 讓 ADK 代理程式能夠以統一的介面使用 **超過 100 種 LLM 供應商**。

**何時使用 LiteLLM**：

- ✅ 需要 OpenAI 模型 (GPT-4o, GPT-4o-mini)
- ✅ 想要 Anthropic Claude (3.7 Sonnet, Opus, Haiku)
- ✅ 透過 Ollama 執行本地模型 (隱私、成本、離線)
- ✅ Azure OpenAI (企業合約)
- ✅ 多供應商策略 (備援、成本優化)
- ✅ 比較跨供應商的模型性能

**何時不該使用 LiteLLM**：

- ❌ **使用 Gemini 模型** → 請使用原生的 `GoogleGenAI` (性能更佳、功能更完整)
- ❌ 僅使用 Gemini 的簡單原型
- ❌ 需要 Gemini 特定功能時 (例如 `thinking_config`, `grounding`)

---

## 1. OpenAI 整合 (OpenAI Integration)

**OpenAI 的 GPT 模型** 因其強大的推理與指令遵循能力而被廣泛使用。

### 設定 (Setup)

**1. 安裝依賴套件**：

```bash
pip install google-adk[litellm]
# 或手動安裝：
pip install litellm openai
```

**2. 從 [OpenAI Platform](https://platform.openai.com/api-keys) 取得 API 金鑰**

**3. 設定環境變數**：

```bash
export OPENAI_API_KEY='sk-...'
```

### 範例：GPT-4o 代理程式 (Example: GPT-4o Agent)

```python
"""
使用 LiteLLM 的 ADK 代理程式，搭配 OpenAI GPT-4o。
來源：contributing/samples/hello_world_litellm/agent.py
"""
import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.models import LiteLlm
from google.adk.tools import FunctionTool
from google.genai import types

# 設定環境
os.environ['OPENAI_API_KEY'] = 'sk-...'  # 您的 OpenAI API 金鑰


def calculate_square(number: int) -> int:
    """計算一個數字的平方。"""
    return number ** 2


async def main():
    """使用 OpenAI GPT-4o 的代理程式。"""

    # 建立 LiteLLM 模型 - 格式："openai/模型名稱"
    gpt4o_model = LiteLlm(model='openai/gpt-4o-mini')  # 或 'openai/gpt-4o'

    # 透過 OpenAI 模型建立代理程式
    agent = Agent(
        model=gpt4o_model,  # 使用 LiteLlm 實例，而非字串
        name='gpt4o_agent',
        description='由 OpenAI GPT-4o 驅動的代理程式',
        instruction='您是一位樂於助人的助理。',
        tools=[FunctionTool(calculate_square)]
    )

    # 建立 runner 和 session
    runner = InMemoryRunner(agent=agent, app_name='gpt4o_app')
    session = await runner.session_service.create_session(
        app_name='gpt4o_app',
        user_id='user_001'
    )

    # 使用 async 迭代執行查詢
    query = "12 的平方是多少？"
    new_message = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )

    async for event in runner.run_async(
        user_id='user_001',
        session_id=session.id,
        new_message=new_message
    ):
        if event.content and event.content.parts:
            print(event.content.parts[0].text)


if __name__ == '__main__':
    asyncio.run(main())
```

**輸出**：

```
12 的平方是 144。
```

### GPT-4o-mini (成本優化) (Cost-Optimized)

對於簡單任務，**GPT-4o-mini** 比 GPT-4o **便宜 60 倍**。

```python
from google.adk.models import LiteLlm

# GPT-4o：$2.50/1M 輸入 tokens，$10/1M 輸出 tokens
gpt4o = LiteLlm(model='openai/gpt-4o')

# GPT-4o-mini：$0.15/1M 輸入 tokens，$0.60/1M 輸出 tokens
gpt4o_mini = LiteLlm(model='openai/gpt-4o-mini')

# 使用 mini 處理日常任務
routine_agent = Agent(
    model=gpt4o_mini,
    instruction='您能快速處理簡單的查詢。'
)

# 使用完整的 GPT-4o 處理複雜推理
complex_agent = Agent(
    model=gpt4o,
    instruction='您能解決複雜的多步驟問題。'
)
```

### 可用的 OpenAI 模型 (Available OpenAI Models)

| 模型 (Model)       | 輸入成本 (Input Cost) | 輸出成本 (Output Cost) | 最適用途 (Best For)       |
| ------------------ | --------------------- | --------------------- | ------------------------- |
| `openai/gpt-4o`    | $2.50/1M tokens       | $10/1M tokens         | 複雜推理、編碼 (Complex reasoning, coding) |
| `openai/gpt-4o-mini` | $0.15/1M tokens       | $0.60/1M tokens         | 簡單任務、高流量 (Simple tasks, high volume) |
| `openai/o1`        | $15/1M tokens         | $60/1M tokens         | 進階推理鏈 (Advanced reasoning chains) |
| `openai/o1-mini`   | $3/1M tokens          | $12/1M tokens         | STEM 推理 (STEM reasoning) |

**模型字串格式**：`openai/[模型名稱]`

---

## 2. Anthropic Claude 整合 (Anthropic Claude Integration)

**Anthropic 的 Claude** 在長篇內容、分析以及遵循複雜指令方面表現出色。

### Claude 設定 (Claude Setup)

**1. 安裝依賴套件**：

```bash
pip install google-adk[litellm] anthropic
```

**2. 從 [Anthropic Console](https://console.anthropic.com/) 取得 API 金鑰**

**3. 設定環境變數**：

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### 範例：Claude 3.7 Sonnet 代理程式 (Example: Claude 3.7 Sonnet Agent)

```python
"""
使用 LiteLLM 的 ADK 代理程式，搭配 Anthropic Claude 3.7 Sonnet。
"""
import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.models import LiteLlm
from google.adk.tools import FunctionTool
from google.genai import types

# 設定環境
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'  # 您的 Anthropic API 金鑰


def analyze_sentiment(text: str) -> dict:
    """分析文本的情感（模擬實現）。"""
    # 在生產環境中，應使用實際的情感分析工具
    return {
        'sentiment': 'positive',
        'confidence': 0.85,
        'key_phrases': ['exciting', 'innovative', 'breakthrough']
    }


async def main():
    """使用 Claude 3.7 Sonnet 的代理程式。"""

    # 建立 LiteLLM 模型 - 格式："anthropic/模型名稱"
    claude_model = LiteLlm(model='anthropic/claude-3-7-sonnet-20250219')

    # 透過 Claude 模型建立代理程式
    agent = Agent(
        model=claude_model,
        name='claude_agent',
        description='由 Claude 3.7 Sonnet 驅動的代理程式',
        instruction="""
        您是一位深思熟慮的分析師，能提供詳細且細緻的回答。
        您擅長：
        - 複雜推理
        - 長篇內容
        - 倫理考量
        - 遵循詳細指令
        """.strip(),
        tools=[FunctionTool(analyze_sentiment)]
    )

    # 建立 runner 和 session
    runner = InMemoryRunner(agent=agent, app_name='claude_app')
    session = await runner.session_service.create_session(
        app_name='claude_app',
        user_id='user_001'
    )

    query = """
    分析此產品評論的情感並解釋您的推理：
    "這款新的人工智慧助理真是太棒了！它能非常好地理解上下文，
    並提供有幫助且準確的回應。介面直觀，速度也令人印象深刻。強烈推薦！"
    """.strip()

    # 使用 async 迭代執行查詢
    new_message = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )

    async for event in runner.run_async(
        user_id='user_001',
        session_id=session.id,
        new_message=new_message
    ):
        if event.content and event.content.parts:
            print(event.content.parts[0].text)


if __name__ == '__main__':
    asyncio.run(main())
```

**輸出**：

```
我將分析此產品評論的情感：

**整體情感**：非常正面

**分析**：
此評論透過多個指標展現出極為正面的情感：

1. **最高級形容詞**：「真是太棒了」、「非常好地」、「強烈推薦」——這些都是強調性的正面描述詞。

2. **具體讚揚**：評論者強調了多個優點：
   - 上下文理解能力
   - 有幫助且準確的回應
   - 直觀的介面
   - 令人印象深刻的速度

3. **驚嘆號**：兩個驚嘆號 (!!) 表達了熱情。

4. **推薦**：明確的背書（「強烈推薦」）顯示了高度的滿意度。

5. **無批評**：完全沒有負面評論或警告。

**信賴度**：95% - 語言清晰明確，且始終保持正面。

**主要情感基調**：熱情的讚賞與滿意。
```

### 可用的 Claude 模型 (Available Claude Models)

| 模型 (Model)                                 | 輸入成本 (Input Cost) | 輸出成本 (Output Cost) | 上下文 (Context) | 最適用途 (Best For)         |
| -------------------------------------------- | --------------------- | --------------------- | ---------------- | --------------------------- |
| `anthropic/claude-3-7-sonnet-20250219`         | $3/1M tokens          | $15/1M tokens         | 200K             | 平衡型 (最受歡迎) (Balanced (most popular)) |
| `anthropic/claude-3-5-opus-20240229`           | $15/1M tokens         | $75/1M tokens         | 200K             | 複雜推理 (Complex reasoning) |
| `anthropic/claude-3-5-haiku-20241022`          | $0.80/1M tokens       | $4/1M tokens          | 200K             | 快速、簡單任務 (Fast, simple tasks) |

**模型字串格式**：`anthropic/[模型名稱-含日期]`

**注意**：Claude 3.7 Sonnet 是**預設推薦的模型**（截至 2025 年第一季）。

---

## 3. Ollama 本地模型 (Ollama Local Models)

**Ollama** 讓您可以在**本地**執行 LLM，以保護隱私、節省成本並進行離線操作。

### 為何使用 Ollama？ (Why Use Ollama?)

**優點**：

- ✅ **隱私**：資料永遠不會離開您的機器
- ✅ **成本**：初次下載後無 API 費用
- ✅ **離線**：無需網路即可運作
- ✅ **合規性**：將敏感資料保留在本地
- ✅ **實驗**：自由嘗試多種模型

**權衡**：

- ❌ 需要 GPU 才能獲得良好性能
- ❌ 在複雜任務上，品質低於 GPT-4o/Claude/Gemini
- ❌ 在 CPU 上推論速度較慢
- ❌ 有限的上下文視窗（通常為 4K-32K，而雲端模型為 200K）

### Ollama 設定 (Ollama Setup)

**1. 安裝 Ollama**：

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# 從 https://ollama.com/download 下載
```

**2. 啟動 Ollama 伺服器**：

```bash
ollama serve
# 預設在 http://localhost:11434 執行
```

**3. 下載模型**：

```bash
# Granite 4 (IBM，強推理能力，8B 參數)
ollama pull granite4:latest

# Llama 3.3 (Meta，高品質，70B 參數)
ollama pull llama3.3

# Mistral (7B 參數，速度快)
ollama pull mistral

# Phi-4 (14B 參數，Microsoft，擅長編碼)
ollama pull phi4
```

**4. 安裝 Python 依賴套件**：

```bash
pip install google-adk[litellm]
```

### ⚠️ 關鍵：使用 `ollama_chat`，而非 `ollama` (CRITICAL: Use `ollama_chat`, NOT `ollama`)

**錯誤** ❌：

```python
# 這將無法正常運作！
model = LiteLlm(model='ollama/llama3.3')  # ❌ 錯誤
```

**正確** ✅：

```python
# 務必使用 ollama_chat 前綴！
model = LiteLlm(model='ollama_chat/llama3.3')  # ✅ 正確
```

**為什麼？** LiteLLM 有兩種 Ollama 介面：

- `ollama/` - 使用 completion API (舊版，功能有限)
- `ollama_chat/` - 使用 chat API (推薦，功能完整)

ADK 代理程式需要**聊天 API** 才能正常進行函式呼叫與多輪對話。

### 範例：Granite 4 本地代理程式 (Example: Granite 4 Local Agent)

```python
"""
使用本地 Granite 4 透過 Ollama 的 ADK 代理程式。
來源：tutorial_implementation/tutorial28/multi_llm_agent/agent.py
"""
import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.models import LiteLlm
from google.adk.tools import FunctionTool
from google.genai import types

# Ollama 環境設定
os.environ['OLLAMA_API_BASE'] = 'http://localhost:11434'


def get_weather(city: str) -> dict:
    """取得指定城市目前的天氣（模擬）。"""
    # 在生產環境中，應呼叫真實的天氣 API
    return {
        'city': city,
        'temperature': 72,
        'condition': 'Sunny',
        'humidity': 45
    }


async def main():
    """使用本地 Granite 4 模型的代理程式。"""

    # 建立 LiteLLM 模型 - 格式："ollama_chat/模型名稱"
    # ⚠️ 重要：使用 ollama_chat，而非 ollama！
    granite_model = LiteLlm(model='ollama_chat/granite4:latest')

    # 使用本地模型建立代理程式
    agent = Agent(
        model=granite_model,
        name='local_agent',
        description='在本地執行的 Granite 4 代理程式',
        instruction='您是由 IBM Granite 4 驅動的本地助理。所有處理都在裝置上進行。',
        tools=[FunctionTool(get_weather)]
    )

    # 建立 runner 和 session
    runner = InMemoryRunner(agent=agent, app_name='ollama_app')
    session = await runner.session_service.create_session(
        app_name='ollama_app',
        user_id='user_001'
    )

    print("\n" + "="*60)
    print("本地 OLLAMA 代理程式 (隱私優先)")
    print("="*60 + "\n")

    # 使用 async 迭代執行查詢
    query = "舊金山現在天氣如何？"
    new_message = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )

    async for event in runner.run_async(
        user_id='user_001',
        session_id=session.id,
        new_message=new_message
    ):
        if event.content and event.content.parts:
            print(event.content.parts[0].text)

    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
```

**輸出**：

```
============================================================
本地 OLLAMA 代理程式 (隱私優先)
============================================================

舊金山目前天氣晴朗，溫度為
72°F，濕度為 45%。真是美好的一天！

[所有處理都在本地完成 - 無資料傳送至雲端]

============================================================
```

### 熱門的 Ollama 模型 (Popular Ollama Models)

| 模型 (Model)                | 大小 (Size) | 最適用途 (Best For)             | GPU RAM |
| ----------------------------- | ----------- | ------------------------------- | ------- |
| `ollama_chat/granite4:latest` | 8B          | IBM Granite，強推理能力 (IBM Granite, strong reasoning) | 12GB    |
| `ollama_chat/llama3.3`        | 70B         | 一般任務，強推理能力 (General tasks, strong reasoning) | 40GB+   |
| `ollama_chat/llama3.2`        | 3B          | 快速，低資源需求 (Fast, low resource) | 4GB     |
| `ollama_chat/mistral`         | 7B          | 速度/品質平衡 (Balanced speed/quality) | 8GB     |
| `ollama_chat/phi4`            | 14B         | 編碼，STEM (Coding, STEM)       | 16GB    |
| `ollama_chat/gemma2`          | 9B          | Google，指令遵循 (Google, instruction following) | 12GB    |
| `ollama_chat/qwen2.5`         | 7B-72B      | 多語言 (Multilingual)         | 8-40GB  |

**模型字串格式**：`ollama_chat/[模型名稱]` ⚠️ 不是 `ollama/`！

### 設定選項 (Configuration Options)

```python
from google.adk.models import LiteLlm

# 基本用法
model = LiteLlm(model='ollama_chat/llama3.3')

# 使用自訂 Ollama 伺服器
os.environ['OLLAMA_API_BASE'] = 'http://192.168.1.100:11434'
model = LiteLlm(model='ollama_chat/llama3.3')

# 使用額外參數（傳遞給 Ollama）
model = LiteLlm(
    model='ollama_chat/llama3.3',
    temperature=0.7,
    top_p=0.9,
    max_tokens=2048
)
```

---

## 4. Azure OpenAI 整合 (Azure OpenAI Integration)

**Azure OpenAI** 適用於有 **Azure 合約**或**合規性要求**的企業。

### Azure 設定 (Azure Setup)

**1. 在 Azure Portal 建立 Azure OpenAI 資源**

**2. 部署模型**（例如 gpt-4o）

**3. 取得憑證**：

- 來自 Azure Portal 的 API 金鑰
- 端點 URL（例如 `https://your-resource.openai.azure.com/`）
- 部署名稱（例如 `gpt-4o-deployment`）

**4. 設定環境變數**：

```bash
export AZURE_API_KEY='your-azure-key'
export AZURE_API_BASE='https://your-resource.openai.azure.com/'
export AZURE_API_VERSION='2024-02-15-preview'
```

### 範例：Azure OpenAI 代理程式 (Example: Azure OpenAI Agent)

```python
"""
使用 Azure OpenAI 的 ADK 代理程式。
"""
import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.models import LiteLlm
from google.genai import types

# Azure OpenAI 設定
os.environ['AZURE_API_KEY'] = 'your-azure-key'
os.environ['AZURE_API_BASE'] = 'https://your-resource.openai.azure.com/'
os.environ['AZURE_API_VERSION'] = '2024-02-15-preview'


async def main():
    """使用 Azure OpenAI 的代理程式。"""

    # 建立 LiteLLM 模型 - 格式："azure/部署名稱"
    azure_model = LiteLlm(model='azure/gpt-4o-deployment')

    # 建立代理程式
    agent = Agent(
        model=azure_model,
        name='azure_agent',
        description='使用 Azure OpenAI 的代理程式',
        instruction='您是在 Azure 上運行的企業助理。'
    )

    # 建立 runner 和 session
    runner = InMemoryRunner(agent=agent, app_name='azure_app')
    session = await runner.session_service.create_session(
        app_name='azure_app',
        user_id='user_001'
    )

    # 使用 async 迭代執行查詢
    query = "解釋 Azure OpenAI 對企業的好處"
    new_message = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )

    async for event in runner.run_async(
        user_id='user_001',
        session_id=session.id,
        new_message=new_message
    ):
        if event.content and event.content.parts:
            print(event.content.parts[0].text)


if __name__ == '__main__':
    asyncio.run(main())
```

**為何選擇 Azure OpenAI？**

- ✅ 企業級 SLA (99.9% 正常運行時間)
- ✅ 資料落地 (歐盟、美國、亞洲)
- ✅ 私有網路 (VNet 整合)
- ✅ 合規性 (SOC 2, HIPAA, GDPR)
- ✅ 與 Azure 服務統一計費

---

## 5. 透過 Vertex AI 使用 Claude (Claude via Vertex AI)

**Vertex AI 上的 Claude** 結合了 Anthropic 的模型與 Google Cloud 的基礎設施。

### Vertex AI 設定 (Vertex AI Setup)

**1. 在 Google Cloud Console 中啟用 Vertex AI API**

**2. 設定身份驗證**：

```bash
export GOOGLE_CLOUD_PROJECT='your-project'
export GOOGLE_CLOUD_LOCATION='us-central1'  # 或您偏好的區域
export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account-key.json'
```

**3. 確保 Vertex AI Claude 存取權限**（可能需要審批）

### 範例：透過 Vertex AI 使用 Claude (Example: Claude via Vertex AI)

```python
"""
使用 Vertex AI 上的 Claude 3.7 Sonnet 的 ADK 代理程式。
"""
import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.models import LiteLlm
from google.genai import types

# Vertex AI 設定
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'


async def main():
    """透過 Vertex AI 使用 Claude 的代理程式。"""

    # 建立 LiteLLM 模型 - 格式："vertex_ai/模型名稱"
    claude_vertex = LiteLlm(model='vertex_ai/claude-3-7-sonnet@20250219')

    # 建立代理程式
    agent = Agent(
        model=claude_vertex,
        name='claude_vertex_agent',
        description='在 Vertex AI 上使用 Claude 的代理程式',
        instruction='您透過 Google Cloud 基礎設施利用 Claude。'
    )

    # 建立 runner 和 session
    runner = InMemoryRunner(agent=agent, app_name='vertex_claude_app')
    session = await runner.session_service.create_session(
        app_name='vertex_claude_app',
        user_id='user_001'
    )

    # 使用 async 迭代執行查詢
    query = "比較直接使用 Claude 與在 Vertex AI 上使用 Claude"
    new_message = types.Content(
        role='user',
        parts=[types.Part(text=query)]
    )

    async for event in runner.run_async(
        user_id='user_001',
        session_id=session.id,
        new_message=new_message
    ):
        if event.content and event.content.parts:
            print(event.content.parts[0].text)


if __name__ == '__main__':
    asyncio.run(main())
```

**直接使用 Claude vs. Vertex AI**：

| 因素 (Factor)      | 直接 (Anthropic) | 透過 Vertex AI (Via Vertex AI) |
| ------------------ | ---------------- | ---------------------------- |
| **定價 (Pricing)** | 按 token 計費    | 相同或略高 (Same or slightly higher) |
| **資料落地 (Data residency)** | 美國             | 可選擇 GCP 區域 (Choose GCP region) |
| **SLA**            | 標準 (Standard)  | Google Cloud SLA             |
| **整合 (Integration)** | Anthropic API    | 與 GCP 統一 (Unified with GCP) |
| **計費 (Billing)** | 獨立 (Separate)  | 統一 GCP 計費 (Unified GCP billing) |
| **設定 (Setup)**   | 較簡單 (Simpler) | 較複雜 (More complex)        |

**何時使用 Vertex AI Claude**：

- ✅ 已大量使用 Google Cloud
- ✅ 需要在特定 GCP 區域進行資料落地
- ✅ 希望統一 GCP 計費
- ✅ 需要 Google Cloud SLA

---

## 6. 多供應商比較 (Multi-Provider Comparison)

**使用情境**：比較多個供應商對同一查詢的回應品質。

```python
"""
多供應商代理程式比較。
在 Gemini、GPT-4o、Claude 和 Llama 3.3 上測試相同的查詢。
"""
import asyncio
import os
from google.adk.agents import Agent, Runner
from google.adk.models import GoogleGenAI, LiteLlm

# 環境設定
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['OPENAI_API_KEY'] = 'sk-...'
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'
os.environ['OLLAMA_API_BASE'] = 'http://localhost:11434'


async def compare_models():
    """比較 4 個供應商的回應品質。"""

    # 定義模型
    models = {
        'Gemini 2.5 Flash': GoogleGenAI(model='gemini-2.5-flash'),
        'GPT-4o': LiteLlm(model='openai/gpt-4o'),
        'Claude 3.7 Sonnet': LiteLlm(model='anthropic/claude-3-7-sonnet-20250219'),
        'Llama 3.3 (Local)': LiteLlm(model='ollama_chat/llama3.3')
    }

    # 測試查詢
    query = """
    向一位 12 歲的孩子解釋量子糾纏。
    使用他們能理解的比喻。
    """.strip()

    print("\n" + "="*70)
    print("多供應商模型比較")
    print("="*70 + "\n")
    print(f"查詢: {query}\n")
    print("="*70 + "\n")

    # 測試每個模型
    for model_name, model in models.items():
        print(f"### {model_name}")
        print("-" * 70)

        agent = Agent(
            model=model,
            instruction='您能清晰簡單地解釋複雜的主題。'
        )

        # 為此模型建立 runner 和 session
        runner = InMemoryRunner(agent=agent, app_name='compare_app')
        session = await runner.session_service.create_session(
            app_name='compare_app',
            user_id='user_001'
        )

        try:
            # 使用 async 迭代執行查詢
            new_message = types.Content(
                role='user',
                parts=[types.Part(text=query)]
            )

            response = ""
            async for event in runner.run_async(
                user_id='user_001',
                session_id=session.id,
                new_message=new_message
            ):
                if event.content and event.content.parts:
                    response = event.content.parts[0].text

            print(response)
            print(f"\n[長度: {len(response)} 字元]")

        except Exception as e:
            print(f"錯誤: {e}")

        print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    asyncio.run(compare_models())
```

**範例輸出**：

```
======================================================================
多供應商模型比較
======================================================================

查詢: 向一位 12 歲的孩子解釋量子糾纏。
使用他們能理解的比喻。

======================================================================

### Gemini 2.5 Flash
----------------------------------------------------------------------
想像你有兩個魔法硬幣。當你拋擲其中一個，它正面朝上時，
另一個硬幣會立即反面朝上——無論它們相距多遠。即使一個硬幣在地球，
另一個在火星！

這就是量子糾纏。兩個粒子變得「糾纏」，以至於
測量其中一個會立即影響另一個，即使距離很遠。

[長度: 387 字元]

======================================================================

### GPT-4o
----------------------------------------------------------------------
把量子糾纏想像成有兩個相連的魔法骰子。當你擲出一個骰子
顯示 6 時，另一個骰子會自動顯示 1——立即，即使它在
世界的另一端！科學家還不完全明白這是如何發生的，但
他們知道確實如此。這是物理學中最奇怪的事情之一！

[長度: 415 字元]

======================================================================

### Claude 3.7 Sonnet
----------------------------------------------------------------------
想像你和你最好的朋友各有一顆魔法彈珠。無論你們走多遠——
即使去了不同的國家——當你捏住你的彈珠，它變成紅色時，
你朋友的彈珠會在完全相同的瞬間變成藍色。

這就是量子糾纏！兩個粒子被連結起來，以至於發生在其中一個
身上的事會立即影響另一個，無論距離多遠。愛因斯坦稱之為
「鬼魅般的超距作用」，因為連他都覺得這很奇怪！

[長度: 512 字元]

======================================================================

### Llama 3.3 (Local)
----------------------------------------------------------------------
把量子糾纏想像成有兩個特殊的雙胞胎硬幣。如果你拋擲一個硬幣
它正面朝上，另一個硬幣總會反面朝上——立即！它們以一種
神秘的方式相連，科學家們仍在努力完全理解。

[長度: 287 字元]

======================================================================
```

**觀察**：

- **Gemini 2.5 Flash**：快速、簡潔、準確
- **GPT-4o**：清晰的比喻，承認神秘性
- **Claude 3.7 Sonnet**：最詳細，包含愛因斯坦的名言
- **Llama 3.3**：最短，較簡單但吸引力較低

---

## 7. 成本優化策略 (Cost Optimization Strategies)

### 成本比較（每 1M tokens）(Cost Comparison (per 1M tokens))

| 供應商 (Provider) | 模型 (Model)            | 輸入成本 (Input Cost) | 輸出成本 (Output Cost) | 總計 (1M 輸入 + 1M 輸出) (Total (1M in + 1M out)) |
| ----------------- | ----------------------- | --------------------- | --------------------- | --------------------------------------------------- |
| **Google**        | gemini-2.5-flash        | $0.075                | $0.30                 | **$0.375** ⭐ 最便宜 (Cheapest)                   |
| **Google**        | gemini-2.5-pro          | $1.25                 | $5.00                 | $6.25                                               |
| **OpenAI**        | gpt-4o-mini             | $0.15                 | $0.60                 | $0.75                                               |
| **OpenAI**        | gpt-4o                  | $2.50                 | $10.00                | $12.50                                              |
| **Anthropic**     | claude-3-5-haiku        | $0.80                 | $4.00                 | $4.80                                               |
| **Anthropic**     | claude-3-7-sonnet       | $3.00                 | $15.00                | $18.00                                              |
| **Ollama**        | granite4:latest (local) | $0                    | $0                    | **$0** 🎉 免費 (Free)                               |

### 策略 1：分層模型選擇 (Strategy 1: Tiered Model Selection)

```python
def get_model_for_task(complexity: str):
    """根據任務複雜度選擇模型。"""

    if complexity == 'simple':
        # 對於簡單任務，使用最便宜的模型
        return LiteLlm(model='openai/gpt-4o-mini')  # 或 gemini-2.5-flash

    elif complexity == 'medium':
        # 平衡成本/品質
        return GoogleGenAI(model='gemini-2.5-flash')

    elif complexity == 'complex':
        # 最佳推理能力，值得花費
        return LiteLlm(model='anthropic/claude-3-7-sonnet-20250219')

    elif complexity == 'local_ok':
        # 隱私/成本優先
        return LiteLlm(model='ollama_chat/llama3.3')

# 範例用法
simple_agent = Agent(model=get_model_for_task('simple'))
complex_agent = Agent(model=get_model_for_task('complex'))
```

### 策略 2：備援鏈 (Strategy 2: Fallback Chain)

```python
async def run_with_fallback(query: str):
    """按成本順序嘗試模型（最便宜的優先）。"""

    models = [
        ('gemini-2.5-flash', GoogleGenAI(model='gemini-2.5-flash')),
        ('gpt-4o-mini', LiteLlm(model='openai/gpt-4o-mini')),
        ('gpt-4o', LiteLlm(model='openai/gpt-4o'))
    ]

    for model_name, model in models:
        try:
            agent = Agent(model=model)
            runner = InMemoryRunner(agent=agent, app_name='fallback_app')
            session = await runner.session_service.create_session(
                app_name='fallback_app',
                user_id='user_001'
            )

            new_message = types.Content(
                role='user',
                parts=[types.Part(text=query)]
            )

            result_text = None
            async for event in runner.run_async(
                user_id='user_001',
                session_id=session.id,
                new_message=new_message
            ):
                if event.content and event.content.parts:
                    result_text = event.content.parts[0].text

            print(f"✅ 成功使用 {model_name}")
            return result_text

        except Exception as e:
            print(f"❌ {model_name} 失敗: {e}")
            continue

    raise Exception("所有模型都失敗了")
```

### 策略 3：高流量使用本地模型 (Strategy 3: Local for High Volume)

```python
"""
對高流量、簡單的任務使用本地 Ollama。
僅在需要時使用雲端模型。
"""

async def process_batch(queries: list[str]):
    """以符合成本效益的方式處理大量查詢。"""

    # 用於大量處理的本地模型
    local_model = LiteLlm(model='ollama_chat/llama3.3')
    local_agent = Agent(model=local_model)

    # 用於複雜查詢的雲端模型
    cloud_model = GoogleGenAI(model='gemini-2.5-flash')
    cloud_agent = Agent(model=cloud_model)

    results = []

    for query in queries:
        # 根據複雜度路由並建立適當的 runner
        if is_simple(query):
            # 免費的本地處理
            runner = InMemoryRunner(agent=local_agent, app_name='batch_app')
        else:
            # 對於複雜查詢使用雲端模型
            runner = InMemoryRunner(agent=cloud_agent, app_name='batch_app')

        # 建立 session
        session = await runner.session_service.create_session(
            app_name='batch_app',
            user_id='batch_user'
        )

        # 使用 async 迭代執行查詢
        new_message = types.Content(
            role='user',
            parts=[types.Part(text=query)]
        )

        result_text = None
        async for event in runner.run_async(
            user_id='batch_user',
            session_id=session.id,
            new_message=new_message
        ):
            if event.content and event.content.parts:
                result_text = event.content.parts[0].text

        results.append(result_text)

    return results


def is_simple(query: str) -> bool:
    """判斷查詢是否足夠簡單以使用本地模型。"""
    simple_keywords = ['what is', 'define', 'explain', 'summarize']
    return any(kw in query.lower() for kw in simple_keywords)
```

---

## 8. 最佳實踐 (Best Practices)

### ✅ 應該做 (DO)

**1. 盡可能使用原生 Gemini**：

```python
# ✅ 最佳 - 原生 Gemini
agent = Agent(model='gemini-2.5-flash')

# ❌ 不建議 - 透過 LiteLLM 使用 Gemini (速度較慢，功能缺失)
agent = Agent(model=LiteLlm(model='gemini/gemini-2.5-flash'))
```

**2. 安全地設定環境變數**：

```python
import os

# ✅ 良好 - 從環境變數讀取
api_key = os.environ.get('OPENAI_API_KEY')

# ❌ 不佳 - 硬式編碼
api_key = 'sk-...'  # 絕不要提交這個！
```

**3. 處理特定供應商的錯誤**：

```python
try:
    result = await runner.run_async(query, agent=agent)
except Exception as e:
    if 'rate_limit' in str(e).lower():
        print("達到速率限制，等待中...")
        await asyncio.sleep(60)
    elif 'quota' in str(e).lower():
        print("配額已超過，切換供應商...")
        agent.model = fallback_model
    else:
        raise
```

**4. 正確使用 Ollama**：

```python
# ✅ 正確 - 使用 ollama_chat 前綴
model = LiteLlm(model='ollama_chat/llama3.3')

# ❌ 錯誤 - 使用 ollama 前綴 (功能受限)
model = LiteLlm(model='ollama/llama3.3')
```

**5. 監控成本**：

```python
import time

class CostTracker:
    def __init__(self):
        self.total_tokens = 0
        self.model_costs = {
            'openai/gpt-4o': 2.50 / 1_000_000,  # 每輸入 token
            'anthropic/claude-3-7-sonnet-20250219': 3.00 / 1_000_000
        }

    def track(self, model: str, tokens: int):
        cost = tokens * self.model_costs.get(model, 0)
        self.total_tokens += tokens
        print(f"成本: ${cost:.4f} | 總計: {self.total_tokens:,} tokens")

tracker = CostTracker()
```

### ❌ 不應該做 (DON'T)

**1. 不要為 Gemini 使用 LiteLLM**：

```python
# ❌ 不佳 - 失去 Gemini 特定功能
model = LiteLlm(model='gemini/gemini-2.5-flash')

# ✅ 良好 - 使用原生
model = 'gemini-2.5-flash'  # 或 GoogleGenAI('gemini-2.5-flash')
```

**2. 不要忘記 `ollama_chat` 前綴**：

```python
# ❌ 錯誤
LiteLlm(model='ollama/llama3.3')

# ✅ 正確
LiteLlm(model='ollama_chat/llama3.3')
```

**3. 不要忽略供應商的限制**：

- OpenAI：200K tokens/分鐘（依層級而定）
- Anthropic：200K tokens/分鐘（不固定）
- Ollama：受您的 GPU 限制

**4. 不要混淆憑證**：

```bash
# ❌ 不佳 - 衝突
export OPENAI_API_KEY='key1'
export OPENAI_API_KEY='key2'  # 會覆蓋！

# ✅ 良好 - 如有需要，使用不同的環境變數名稱
export OPENAI_API_KEY='key1'
export AZURE_OPENAI_API_KEY='key2'
```

---

## 總結 (Summary)

您已學會如何在 ADK 代理程式中透過 LiteLLM 使用 OpenAI、Claude、Ollama 及其他 LLM：

**重點回顧**：

- ✅ **LiteLLM** 讓 ADK 能使用超過 100 種 LLM 供應商
- ✅ **OpenAI**：`LiteLlm(model='openai/gpt-4o-mini')` - 需要 `OPENAI_API_KEY`
- ✅ **Claude**：`LiteLlm(model='anthropic/claude-3-7-sonnet-20250219')` - 需要 `ANTHROPIC_API_KEY`
- ✅ **Ollama**：`LiteLlm(model='ollama_chat/granite4:latest')` - ⚠️ 使用 `ollama_chat`，而非 `ollama`！
- ✅ **Azure OpenAI**：`LiteLlm(model='azure/deployment-name')` - 企業選項
- ✅ **不要**為 Gemini 使用 LiteLLM - 請改用原生的 `GoogleGenAI`
- ✅ **本地模型** (Ollama) 非常適合隱私、成本及離線使用
- ✅ **成本優化**：gemini-2.5-flash ($0.375/1M)、gpt-4o-mini ($0.75/1M)、本地 (免費)

**模型字串格式**：

| 供應商 (Provider) | 格式 (Format)       | 範例 (Example)                               |
| ----------------- | --------------------- | ---------------------------------------------- |
| OpenAI            | `openai/[model]`      | `openai/gpt-4o`                                |
| Anthropic         | `anthropic/[model]`   | `anthropic/claude-3-7-sonnet-20250219`         |
| Ollama            | `ollama_chat/[model]` | `ollama_chat/granite4:latest` ⚠️ 不是 `ollama/` |
| Azure             | `azure/[deployment]`  | `azure/gpt-4o-deployment`                      |
| Vertex AI         | `vertex_ai/[model]`   | `vertex_ai/claude-3-7-sonnet@20250219`         |

**何時使用何種模型**：

| 使用情境 (Use Case)         | 推薦模型 (Recommended Model)        |
| --------------------------- | ----------------------------------- |
| 簡單任務，高流量 (Simple tasks, high volume) | gemini-2.5-flash 或 gpt-4o-mini     |
| 複雜推理 (Complex reasoning) | claude-3-7-sonnet 或 gpt-4o         |
| 隱私/合規性 (Privacy/compliance) | ollama_chat/granite4:latest (本地) |
| 企業 Azure (Enterprise Azure) | azure/gpt-4o-deployment             |
| 成本優化 (Cost optimization) | gemini-2.5-flash (最便宜的雲端模型) |
| 離線/氣隙環境 (Offline/air-gapped) | ollama_chat 模型                  |
| 編碼任務 (Coding tasks)     | ollama_chat/phi4 或 gpt-4o          |
| 長篇內容 (Long-form content) | claude-3-7-sonnet                   |

**所需環境變數**：

```bash
# OpenAI
export OPENAI_API_KEY='sk-...'

# Anthropic
export ANTHROPIC_API_KEY='sk-ant-...'

# Ollama
export OLLAMA_API_BASE='http://localhost:11434'

# Azure OpenAI
export AZURE_API_KEY='...'
export AZURE_API_BASE='https://your-resource.openai.azure.com/'
export AZURE_API_VERSION='2024-02-15-preview'

# Google (用於原生 Gemini，非 LiteLLM)
export GOOGLE_CLOUD_PROJECT='your-project'
export GOOGLE_CLOUD_LOCATION='us-central1'
```

**生產檢查清單**：

- [ ] 環境變數已安全設定（非硬式編碼）
- [ ] API 金鑰儲存在秘密管理器中（生產環境）
- [ ] 已實作成效追蹤
- [ ] 已處理速率限制
- [ ] 已設定備援模型
- [ ] Ollama 模型使用 `ollama_chat` 前綴（非 `ollama`）
- [ ] 未使用 LiteLLM 處理 Gemini（改用原生）
- [ ] 處理特定供應商的錯誤
- [ ] 根據任務複雜度選擇模型
- [ ] 已設定監控與警報

**資源**：

- [LiteLLM 文件](https://docs.litellm.ai/)
- [OpenAI API 參考](https://platform.openai.com/docs/api-reference)
- [Anthropic Claude 文件](https://docs.anthropic.com/)
- [Ollama 模型](https://ollama.com/library)
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [ADK LiteLLM 範例](https://github.com/google/adk-docs/tree/main/contributing/samples/hello_world_litellm)

---

## 程式碼實現 (Code Implementation)
- multi-llm-agent: [程式碼連結](../../../python/agents/multi-llm-agent/)
