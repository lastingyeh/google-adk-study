# Tutorial 01: Hello World Agent - 使用 Google ADK 打造你的第一個 AI Agent

本篇教學將引導您使用 Google Agent Development Kit (ADK) 從零開始，建立一個能與使用者進行簡單對話的 AI Agent。無需任何 ADK 使用經驗！

## 總覽 (Overview)

本教學將從頭開始，引導您使用 Google Agent Development Kit (ADK) 建立您的第一個 AI Agent。您將創建一個能夠與使用者聊天的簡單對話型 Agent。完全不需要任何先前的 ADK 經驗！

## 先決條件 (Prerequisites)

*   系統已安裝 **Python 3.9+**
*   可使用**終端機/命令列**
*   **Google API 金鑰** - 可在 [Google AI Studio](https://aistudio.google.com/app/apikey) 免費取得
*   具備基礎的 Python 理解能力 (看得懂 Python 即可)

## 核心概念 (Core Concepts)

### 什麼是 Agent？ (What is an Agent?)

在 ADK 中，**Agent** 是一個由大型語言模型 (LLM) 驅動的 AI 助理。您可以將其視為一個定義以下內容的藍圖：

*   Agent 的目的 (其指令)
*   驅動它的 LLM 模型 (例如 Gemini)
*   它所具備的能力 (工具 - 我們將在下一個教學中加入)

### Agent 類別 (The Agent Class)

ADK 提供了 `Agent` 類別作為定義 Agent 的現代化方式。它是一個簡單的設定物件 - 您只需告訴它您想要什麼！

## 使用案例 (Use Case)

我們正在打造一個**友善的 AI 助理**，它具備以下特點：

*   熱情地問候使用者
*   以對話方式回答一般性問題
*   目前沒有特殊工具 (僅限純對話)

這是所有 ADK Agent 的基礎起點！

## 快速開始 (Quick Start)

最簡單的入門方式是使用我們提供的現成實作：

```bash
# 複製或導覽至教學實作目錄
cd tutorial_implementation/tutorial01
# 安裝依賴套件並進行設定
make setup
# 啟動 Agent
make dev
```

然後在您的瀏覽器中開啟 `http://localhost:8000` 並選擇 "hello_agent"！

## 逐步設定 (替代方案) (Step-by-Step Setup (Alternative))

如果您偏好自行建構，請依照以下步驟操作：

### 步驟 1: 安裝 (Step 1: Installation)

開啟您的終端機並安裝 ADK：

```bash
pip install google-adk
```

此指令會安裝完整的 ADK 工具包，包含開發 UI、CLI 工具及所有依賴項目。

### 步驟 2: 建立專案結構 (Step 2: Create Project Structure)

ADK 需要特定的資料夾結構。為您的 Agent 建立一個新目錄：

```bash
# 建立 Agent 目錄
mkdir hello_agent
cd hello_agent
# 建立必要的 Python 檔案
touch __init__.py agent.py .env
```

您的資料夾結構應如下所示：

```
hello_agent/
├── __init__.py    # 使其成為一個 Python 套件
├── agent.py       # 您的 Agent 定義
└── .env           # 身份驗證憑證
```

### 步驟 3: 設定身份驗證 (Step 3: Configure Authentication)

在您的文字編輯器中開啟 `.env` 檔案，並加入您的 Google AI Studio API 金鑰：

#### hello_agent/.env

```env
# 使用 Google AI Studio (建議學習時使用)
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key-here
```

請將 `your-api-key-here` 替換為您從 [Google AI Studio](https://aistudio.google.com/app/apikey) 取得的實際 API 金鑰。

### 步驟 4: 設定套件匯入 (Step 4: Set Up Package Import)

開啟 `__init__.py` 並加入這一行：

#### hello_agent/__init__.py

```python
from . import agent
```

這一行會告訴 ADK 在哪裡可以找到您的 Agent 定義。這是必要步驟！

### 步驟 5: 定義您的 Agent (Step 5: Define Your Agent)

現在是最令人興奮的部分！開啟 `agent.py` 並建立您的 Agent：

#### hello_agent/agent.py

```python
# ADK 要求，用於正確的 Python 型別提示
from __future__ import annotations
# 匯入 Agent 類別
from google.adk.agents import Agent

# 定義您的 Agent - 必須命名為 'root_agent'
root_agent = Agent(
    name="hello_assistant",
    model="gemini-2.0-flash",
    description="一個用於一般對話的友善 AI 助理",
    instruction=(
        "你是一個熱情且樂於助人的助理。"
        "熱情地問候使用者，並清楚地回答他們的問題。"
        "保持對話性和友善！"
    )
)
```

### 程式碼說明 (Code Explanation)

*   **`from __future__ import annotations`**: ADK 的慣例，用於更好的型別處理。
*   **`Agent`**: 現代化的 ADK Agent 類別 (取代舊的 `LlmAgent`)。
*   **`name`**: 您的 Agent 的內部識別碼。
*   **`model`**: 要使用的 LLM - `gemini-2.0-flash` 速度快且具成本效益。
*   **`description`**: 您的 Agent 功能的簡要摘要。
*   **`instruction`**: 給予 LLM 的詳細行為指示。
*   **`root_agent`**: 必須使用這個確切的變數名稱 - ADK 會尋找它！

### 步驟 6: 執行您的 Agent (Step 6: Run Your Agent)

導覽至 `hello_agent` 的**父目錄**：

```bash
cd ..  # 上一層目錄，您所在的資料夾應包含 hello_agent/
```

#### 選項 1: 開發 UI (建議學習時使用) (Option 1: Dev UI (Recommended for Learning))

啟動互動式開發介面：

```bash
adk web
```

這會啟動一個網頁伺服器。在您的瀏覽器中開啟 `http://localhost:8000` 並：

1.  **選擇您的 Agent**: 從左上角的下拉選單中選擇 "hello_agent"。
2.  **開始聊天**: 在聊天框中輸入訊息。
3.  **探索 Events 標籤**: 點擊左側的 "Events" 查看 LLM 接收和回傳的確切內容。

**試試這些提示：**

*   "Hello!"
*   "What can you help me with?"
*   "Tell me a joke"

#### 選項 2: 命令列 (Option 2: Command Line)

用於在終端機中快速測試：

```bash
adk run hello_agent
```

在提示時輸入您的訊息，Agent 將會回應。

## 了解背後原理 (Understanding What's Happening)

當您向 Agent 發送訊息時：

1.  **ADK 封裝您的訊息** 以及 Agent 的指令。
2.  **將其發送至 Gemini** (在 `model` 中指定的 LLM)。
3.  **Gemini 根據指令生成回應**。
4.  **ADK 將回應回傳** 給您。

**使用開發 UI 中的 Events 標籤** 來詳細查看此流程 - 它會顯示確切的提示和回應！

## 預期行為 (Expected Behavior)

```
You: Hello!
Agent: Hello! It's great to hear from you! How can I help you today?

You: What can you do?
Agent: I'm here to chat and answer your questions! I can help with general
       information, have conversations, explain concepts, or just be a
       friendly companion. What would you like to talk about?
```

## 重點摘要 (Key Takeaways)

| 重點 | 說明 |
| --- | --- |
| ✅ **ADK Agent 只是設定** | 您定義您想要的，ADK 處理其餘部分。 |
| ✅ **需要標準結構** | 在一個目錄中包含 `__init__.py`, `agent.py`, `.env`。 |
| ✅ **變數必須命名為 `root_agent`** | ADK 會尋找這個確切的名稱。 |
| ✅ **使用 `Agent` 類別** | 這是現代化且建議的方法。 |
| ✅ **開發 UI 是您的好朋友** | Events 標籤會顯示底層發生的確切情況。 |
| ✅ **透過 .env 進行身份驗證** | 確保您的 API 金鑰安全，不要寫在程式碼中。 |

## 常見問題與解決方案 (Common Issues & Solutions)

| 問題 | 解決方案 |
| --- | --- |
| **"Agent not found in dropdown"** | 確保您是從包含 `hello_agent/` 的父目錄執行 `adk web`。 |
| **"Authentication error"** | 檢查您的 `.env` 檔案是否包含正確的 API 金鑰及 `GOOGLE_GENAI_USE_VERTEXAI=FALSE`。 |
| **"Module not found"** | 確認 `__init__.py` 包含 `from . import agent`。 |
| **"root_agent not found"** | 您在 `agent.py` 中的變數必須確切命名為 `root_agent`。 |

## 我們打造了什麼 (What We Built)

您現在擁有一個功能齊全的 AI Agent！它可以：

*   進行自然對話
*   根據上下文回應問題
*   在一個會話期間記住對話歷史

但它的能力僅限於 LLM 所知道的。在下一個教學中，我們將透過新增自訂工具來賦予它**超能力**！

## 下一步 (Next Steps)

*   🚀 **[教學 02: 函式工具](./02_function_tools.md)** - 賦予您的 Agent 執行 Python 函式、執行計算及與資料互動的能力。
*   📖 **延伸閱讀**:
    *   [官方 ADK 快速入門](https://google.github.io/adk-docs/get-started/quickstart/)
    *   [Agent 設定指南](https://google.github.io/adk-docs/agents/llm-agents/)
    *   [模型選項](https://google.github.io/adk-docs/agents/models/)

## 完整檔案參考 (Complete File Reference)

為方便參考，以下是所有三個檔案的完整內容：

### `hello_agent/__init__.py`

```python
from . import agent
```

### `hello_agent/.env`

```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key-here
```

### `hello_agent/agent.py`

```python
from __future__ import annotations
from google.adk.agents import Agent

root_agent = Agent(
    name="hello_assistant",
    model="gemini-2.0-flash",
    description="A friendly AI assistant for general conversation",
    instruction=(
        "You are a warm and helpful assistant. "
        "Greet users enthusiastically and answer their questions clearly. "
        "Be conversational and friendly!"
    )
)
```

恭喜！您已經成功打造了您的第一個 ADK Agent！

## 程式碼實現 (Code Implementation)

*   hello-agent：[程式碼連結](../../../python/agents/hello-agent/README.md)
