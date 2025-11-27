# 教學 27：第三方工具整合

**學習如何將第三方框架工具 (LangChain, CrewAI) 整合到 ADK 代理程式中**

## 概述

本教學示範如何將來自熱門 AI 框架的工具整合到 Google ADK 代理程式中。實作使用 LangChain 的 Wikipedia 工具作為不需要 API 金鑰的工作範例。

### 你將學到什麼

- ✅ 如何使用 `LangchainTool` 包裝器來包裝 LangChain 工具
- ✅ 正確的匯入路徑 (`google.adk.tools.langchain_tool`)
- ✅ 工具包裝與代理程式設定
- ✅ 與第三方工具生態系統協作
- ✅ 工具整合的最佳實務

### 主要功能

- **Wikipedia 整合**：透過 LangChain 搜尋 Wikipedia
- **無需 API 金鑰**：使用公共 API 即可開箱即用
- **生產就緒**：適當的錯誤處理與測試
- **文件完善**：全面的程式碼註解與範例

## 快速開始

### 1. 設定

```bash
# 安裝相依套件
make setup

# 設定驗證 (選擇一種方法)
export GOOGLE_API_KEY=your_api_key_here  # 從 https://aistudio.google.com/app/apikey 取得
```

### 2. 執行代理程式

```bash
# 啟動 ADK 網頁介面
make dev
```

開啟 http://localhost:8000 並從下拉選單中選擇 `third_party_agent`。

### 3. 試試看

向代理程式詢問問題，例如：
- "什麼是量子運算？" (What is quantum computing?)
- "告訴我關於艾達·洛夫萊斯的事" (Tell me about Ada Lovelace)
- "解釋相對論" (Explain the theory of relativity)
- "什麼是機器學習？" (What is machine learning?)

## 專案結構

```
third-party-agent/
├── third_party_agent/          # 代理程式實作
│   ├── __init__.py
│   └── agent.py               # 包含 Wikipedia 工具的主要代理程式
├── tests/                     # 測試套件
│   └── test_agent.py         # 代理程式設定測試
├── Makefile                  # 開發指令
├── README.md                 # 本檔案
├── pyproject.toml           # 套件設定
└── requirements.txt         # 相依套件
```

## 實作細節

### 代理程式設定

代理程式使用以 `LangchainTool` 包裝的 LangChain Wikipedia 工具：

```python
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# 建立 Wikipedia 工具
wikipedia = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=4000
    )
)

# 為 ADK 進行包裝
wiki_tool = LangchainTool(tool=wikipedia)

# 在代理程式中使用
agent = Agent(
    model='gemini-2.0-flash',
    tools=[wiki_tool]
)
```

### 關鍵匯入路徑

✅ **正確**：
```python
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.tools.crewai_tool import CrewaiTool
```

❌ **錯誤**：
```python
from google.adk.tools.third_party import ...  # 模組不存在
```

## 可用指令

| 指令 | 描述 |
|---------|-------------|
| `make setup` | 安裝所有相依套件 |
| `make dev` | 在網頁介面啟動代理程式 |
| `make test` | 執行測試套件 |
| `make demo` | 顯示範例查詢 |
| `make clean` | 清理快取檔案 |

## 測試

執行全面的測試套件：

```bash
make test
```

測試涵蓋：
- 代理程式設定
- 工具註冊
- 匯入驗證
- LangChain 整合
- Wikipedia 工具功能

## 擴充實作

### 新增更多 LangChain 工具

參考教學文件中的範例：
- **Tavily Search**：為 AI 最佳化的網頁搜尋 (需要 API 金鑰)
- **Serper Search**：Google 搜尋 API (需要 API 金鑰)
- **Python REPL**：執行 Python 程式碼
- **ArXiv**：搜尋研究論文

使用 Tavily 的範例 (需要 `TAVILY_API_KEY`)：

```python
from langchain_community.tools.tavily_search import TavilySearchResults

tavily_tool = TavilySearchResults(max_results=5)
tavily_adk = LangchainTool(tool=tavily_tool)
```

### 新增 CrewAI 工具

CrewAI 工具需要 `name` (名稱) 和 `description` (描述)：

```python
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import SerperDevTool

serper_tool = SerperDevTool()
serper_adk = CrewaiTool(
    tool=serper_tool,
    name='serper_search',
    description='Search Google for current information'
)
```

## 環境變數

### 必要
- `GOOGLE_API_KEY` 或 `GOOGLE_APPLICATION_CREDENTIALS`

### 選用 (用於其他工具)
- `TAVILY_API_KEY` - 用於 Tavily 搜尋工具
- `SERPER_API_KEY` - 用於 Serper/Google 搜尋
- `OPENWEATHERMAP_API_KEY` - 用於天氣資料
- `WOLFRAM_ALPHA_APPID` - 用於計算查詢

## 疑難排解

### "ModuleNotFoundError: No module named 'langchain_community'"

```bash
pip install langchain-community
```

### "ModuleNotFoundError: No module named 'wikipedia'"

```bash
pip install wikipedia
```

### "Rate limit exceeded" (超出速率限制)

Wikipedia API 有速率限制。如有需要，請在請求之間增加延遲：

```python
import time
time.sleep(1)  # 搜尋之間
```

### 代理程式未出現在下拉選單中

確認您已安裝該套件：

```bash
pip install -e .
```

## 關鍵概念

### 工具包裝

第三方工具在 ADK 中使用前必須先經過包裝：

```python
# LangChain 工具
langchain_tool = LangchainTool(tool=your_langchain_tool)

# CrewAI 工具 (需要名稱和描述)
crewai_tool = CrewaiTool(
    tool=your_crewai_tool,
    name='tool_name',
    description='What it does'
)
```

### 工具選擇

LLM 會根據使用者查詢自動選擇並使用工具。無需明確的路由。

### 錯誤處理

第三方工具可能會失敗。代理程式會優雅地處理錯誤並提供有用的回饋。

## 資源

- [LangChain 工具](https://python.langchain.com/docs/integrations/tools/)
- [CrewAI 工具](https://docs.crewai.com/tools/)
- [ADK 第三方工具](https://google.github.io/adk-docs/tools/third-party-tools/)

## 重點摘要

- **核心概念**：整合第三方 AI 框架 (LangChain, CrewAI) 的工具到 ADK 代理程式中，擴充代理程式能力。
- **關鍵技術**：
    - **Google ADK**：代理程式開發框架。
    - **LangChain**：使用 `LangchainTool` 包裝器整合 Wikipedia 和 DuckDuckGo 搜尋。
    - **CrewAI**：整合 DirectoryReadTool 和 FileReadTool 進行檔案系統操作。
    - **Python**：實作語言。
- **重要結論**：
    - 第三方工具必須經過適當的包裝 (`LangchainTool`, `CrewaiTool`) 才能在 ADK 中使用。
    - 正確的匯入路徑 (`google.adk.tools.langchain_tool`) 對於功能運作至關重要。
    - LLM 具備自動選擇合適工具的能力，無需手動編寫路由邏輯。
- **行動項目**：
    - 執行 `make setup` 安裝相依套件。
    - 設定 Google API 金鑰。
    - 執行 `make dev` 啟動代理程式並進行測試。
