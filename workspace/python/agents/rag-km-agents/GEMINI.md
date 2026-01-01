編碼代理指南：

# Google Agent Development Kit (ADK) Python 速查表

本文件為使用 Python Agent Development Kit (ADK) 建構、編排和部署 AI 代理的長篇綜合參考。旨在以更詳盡的細節、更多的程式碼範例和深入的最佳實踐，涵蓋所有重要面向。

## 目錄

1.  [核心概念與專案結構](#1-核心概念與專案結構)
    - 1.1 ADK 的基礎原則
    - 1.2 基本元素
    - 1.3 標準專案佈局
    - 1.A 無需程式碼建構代理 (代理設定)
2.  [代理定義 (`LlmAgent`)](#2-代理定義-llmagent)
    - 2.1 基本 `LlmAgent` 設定
    - 2.2 進階 `LlmAgent` 組態
    - 2.3 LLM 指令設計
    - 2.4 生產環境包裝器 (`App`)
3.  [使用工作流程代理進行編排](#3-使用工作流程代理進行編排)
    - 3.1 `SequentialAgent`: 線性執行
    - 3.2 `ParallelAgent`: 並行執行
    - 3.3 `LoopAgent`: 迭代過程
4.  [多代理系統與通訊](#4-多代理系統與通訊)
    - 4.1 代理層級結構
    - 4.2 代理間通訊機制
    - 4.3 常見的多代理模式
    - 4.A 分散式通訊 (A2A 協定)
5.  [建構自訂代理 (`BaseAgent`)](#5-建構自訂代理-baseagent)
    - 5.1 何時使用自訂代理
    - 5.2 實作 `_run_async_impl`
6.  [模型：Gemini、LiteLLM 與 Vertex AI](#6-模型-gemini-litellm-與-vertex-ai)
    - 6.1 Google Gemini 模型 (AI Studio & Vertex AI)
    - 6.2 透過 LiteLLM 使用其他雲端與專有模型
    - 6.3 透過 LiteLLM 使用開放與本地模型 (Ollama, vLLM)
    - 6.4 自訂 LLM API 客戶端
7.  [工具：代理的能力](#7-工具-代理的能力)
    - 7.1 定義函式工具：原則與最佳實踐
    - 7.2 `ToolContext` 物件：存取執行期資訊
    - 7.3 所有工具類型及其用法
    - 7.4 工具確認 (人在迴路)
8.  [上下文、狀態與記憶體管理](#8-上下文-狀態與記憶體管理)
    - 8.1 `Session` 物件與 `SessionService`
    - 8.2 `State`: 對話暫存區
    - 8.3 `Memory`: 長期知識與檢索
    - 8.4 `Artifacts`: 二進位資料管理
9.  [執行期、事件與執行流程](#9-執行期-事件與執行流程)
    - 9.1 執行期組態 (`RunConfig`)
    - 9.2 `Runner`: 編排器
    - 9.3 事件迴圈：核心執行流程
    - 9.4 `Event` 物件：通訊骨幹
    - 9.5 非同步程式設計 (Python 特定)
10. [使用回呼控制流程](#10-使用回呼控制流程)
    - 10.1 回呼機制：攔截與控制
    - 10.2 回呼類型
    - 10.3 回呼最佳實踐
    - 10.A 使用插件進行全域控制
11. [工具的驗證](#11-工具的驗證)
    - 11.1 核心概念：`AuthScheme` 與 `AuthCredential`
    - 11.2 互動式 OAuth/OIDC 流程
    - 11.3 自訂工具驗證
12. [部署策略](#12-部署策略)
    - 12.1 本地開發與測試 (`adk web`, `adk run`, `adk api_server`)
    - 12.2 Vertex AI 代理引擎
    - 12.3 Cloud Run
    - 12.4 Google Kubernetes Engine (GKE)
    - 12.5 CI/CD 整合
13. [評估與安全性](#13-評估與安全性)
    - 13.1 代理評估 (`adk eval`)
    - 13.2 安全性與防護機制
14. [除錯、日誌與可觀測性](#14-除錯-日誌與可觀測性)
15. [串流與進階 I/O](#15-串流與進階-io)
16. [效能最佳化](#16-效能最佳化)
17. [一般最佳實踐與常見陷阱](#17-一般最佳實踐與常見陷阱)
18. [官方 API 與 CLI 參考](#18-官方-api-與-cli-參考)

---

## 1. 核心概念與專案結構

### 1.1 ADK 的基礎原則

- **模組化**：將複雜問題分解為更小、可管理的代理和工具。
- **可組合性**：結合簡單的代理和工具來建構複雜的系統。
- **可觀測性**：詳細的事件日誌和追蹤功能，以了解代理行為。
- **可擴充性**：輕鬆與外部服務、模型和框架整合。
- **部署無關性**：一次設計代理，隨處部署。

### 1.2 基本元素

- **`Agent`**：核心智慧單元。可以是 `LlmAgent` (由 LLM 驅動) 或 `BaseAgent` (自訂/工作流程)。
- **`Tool`**：提供外部能力的可呼叫函式/類別 (`FunctionTool`, `OpenAPIToolset` 等)。
- **`Session`**：一個獨特、有狀態的對話執行緒，包含歷史 (`events`) 和短期記憶 (`state`)。
- **`State`**：`Session` 內的鍵值字典，用於暫存對話資料。
- **`Memory`**：超越單一會話的長期、可搜尋知識庫 (`MemoryService`)。
- **`Artifact`**：與會話或使用者相關聯的具名、版本化二進位資料 (檔案、圖片)。
- **`Runner`**：執行引擎；編排代理活動和事件流程。
- **`Event`**：通訊和歷史的原子單元；攜帶內容和副作用 `actions`。
- **`InvocationContext`**：全面的根上下文物件，包含單次 `run_async` 呼叫的所有執行期資訊。

### 1.3 標準專案佈局

一個結構良好的 ADK 專案對於可維護性和利用 `adk` CLI 工具至關重要。

```
your_project_root/
├── my_first_agent/             # 每個資料夾都是一個獨立的代理應用程式
│   ├── __init__.py             # 使 `my_first_agent` 成為 Python 套件 (`from . import agent`)
│   ├── agent.py                # 包含 `root_agent` 定義和 `LlmAgent`/WorkflowAgent 實例
│   ├── tools.py                # 自訂工具函式定義
│   ├── data/                   # 選用：靜態資料、範本
│   └── .env                    # 環境變數 (API 金鑰、專案 ID)
├── my_second_agent/
│   ├── __init__.py
│   └── agent.py
├── requirements.txt            # 專案的 Python 依賴項 (例如 google-adk, litellm)
├── tests/                      # 單元和整合測試
│   ├── unit/
│   │   └── test_tools.py
│   └── integration/
│       └── test_my_first_agent.py
│       └── my_first_agent.evalset.json # 用於 `adk eval` 的評估資料集
└── main.py                     # 選用：自訂 FastAPI 伺服器部署的進入點
```

- `adk web` 和 `adk run` 會自動發現在子目錄中帶有 `__init__.py` 和 `agent.py` 的代理。
- 當從根目錄或代理目錄執行時，`adk` 工具會自動載入 `.env` 檔案。

### 1.A 無需程式碼建構代理 (代理設定)

ADK 允許您使用簡單的 YAML 格式定義代理、工具，甚至是多代理工作流程，無需為編排編寫 Python 程式碼。這對於快速原型設計和讓非程式設計師設定代理非常理想。

#### **開始使用代理設定**

- **建立一個基於設定的代理**：

  ```bash
  adk create --type=config my_yaml_agent
  ```

  這會產生一個 `my_yaml_agent/` 資料夾，內含 `root_agent.yaml` 和 `.env` 檔案。

- **環境設定** (在 `.env` 檔案中)：

  ```bash
  # 用於 Google AI Studio (設定較簡單)
  GOOGLE_GENAI_USE_VERTEXAI=0
  GOOGLE_API_KEY=<your-Google-Gemini-API-key>

  # 用於 Google Cloud Vertex AI (生產環境)
  GOOGLE_GENAI_USE_VERTEXAI=1
  GOOGLE_CLOUD_PROJECT=<your_gcp_project>
  GOOGLE_CLOUD_LOCATION=us-central1
  ```

#### **核心代理設定結構**

- **基本代理 (`root_agent.yaml`)**：

  ```yaml
  # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
  name: assistant_agent
  model: gemini-2.5-flash
  description: 一個可以回答使用者各種問題的輔助代理。
  instruction: 你是一個幫助回答使用者各種問題的代理。
  ```

- **帶有內建工具的代理**：

  ```yaml
  name: search_agent
  model: gemini-2.0-flash
  description: '一個負責執行 Google 搜尋查詢並回答有關結果問題的代理。'
  instruction: 你是一個負責執行 Google 搜尋查詢並回答有關結果問題的代理。
  tools:
    - name: google_search # ADK 內建工具
  ```

- **帶有自訂工具的代理**：

  ```yaml
  agent_class: LlmAgent
  model: gemini-2.5-flash
  name: prime_agent
  description: 處理檢查數字是否為質數。
  instruction: |
    你負責檢查數字是否為質數。
    當被要求檢查質數時，你必須使用一個整數列表呼叫 check_prime 工具。
    絕不嘗試手動判斷質數。
  tools:
    - name: ma_llm.check_prime # 對 Python 函式的參考
  ```

- **帶有子代理的多代理系統**：

  ```yaml
  agent_class: LlmAgent
  model: gemini-2.5-flash
  name: root_agent
  description: 提供程式碼和數學輔導的學習助理。
  instruction: |
    你是一個幫助學生解決程式碼和數學問題的學習助理。

    你將程式碼問題委派給 code_tutor_agent，將數學問題委派給 math_tutor_agent。

    請遵循以下步驟：
    1. 如果使用者詢問有關程式設計或編碼的問題，委派給 code_tutor_agent。
    2. 如果使用者詢問有關數學概念或問題，委派給 math_tutor_agent。
    3. 始終提供清晰的解釋並鼓勵學習。
  sub_agents:
    - config_path: code_tutor_agent.yaml
    - config_path: math_tutor_agent.yaml
  ```

#### **在 Python 中載入代理設定**

```python
from google.adk.agents import config_agent_utils
root_agent = config_agent_utils.from_config("{agent_folder}/root_agent.yaml")
```

#### **執行代理設定代理**

從代理目錄中，使用以下任一指令：

- `adk web` - 啟動網頁 UI 介面
- `adk run` - 在終端機中執行，無 UI
- `adk api_server` - 作為服務為其他應用程式執行

#### **部署支援**

代理設定代理可以使用以下方式部署：

- `adk deploy cloud_run` - 部署到 Google Cloud Run
- `adk deploy agent_engine` - 部署到 Vertex AI 代理引擎

#### **主要功能與能力**

- **支援的內建工具**：`google_search`, `load_artifacts`, `url_context`, `exit_loop`, `preload_memory`, `get_user_choice`, `enterprise_web_search`, `load_web_page`
- **自訂工具整合**：使用完整的模組路徑參考 Python 函式
- **多代理編排**：透過 `config_path` 參考連結代理
- **結構驗證**：內建的 YAML 結構，用於 IDE 支援和驗證

#### **目前限制** (實驗性功能)

- **模型支援**：目前僅支援 Gemini 模型
- **語言支援**：自訂工具必須用 Python 編寫
- **不支援的代理類型**：`LangGraphAgent`, `A2aAgent`
- **不支援的工具**：`AgentTool`, `LongRunningFunctionTool`, `VertexAiSearchTool`, `MCPToolset`, `LangchainTool`, `ExampleTool`

有關完整範例和參考，請參閱 [ADK 範例儲存庫](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+.yaml&type=code)。

---

## 2. 代理定義 (`LlmAgent`)

`LlmAgent` 是智慧行為的基石，利用 LLM 進行推理和決策。

### 2.1 基本 `LlmAgent` 設定

```python
from google.adk.agents import Agent

def get_current_time(city: str) -> dict:
    """返回指定城市的目前時間。"""
    # 模擬實作
    if city.lower() == "new york":
        return {"status": "success", "time": "10:30 AM EST"}
    return {"status": "error", "message": f"無法取得 {city} 的時間。"}

my_first_llm_agent = Agent(
    name="time_teller_agent",
    model="gemini-3-flash-preview", # 必要：驅動代理的 LLM
    instruction="你是一個樂於助人的助理，會告知城市的目前時間。請使用 'get_current_time' 工具來達成此目的。",
    description="告知指定城市的目前時間。", # 對於多代理委派至關重要
    tools=[get_current_time] # 可呼叫函式/工具實例的列表
)
```

### 2.2 進階 `LlmAgent` 組態

- **`generate_content_config`**：控制 LLM 生成參數 (溫度、權杖限制、安全性)。

  ```python
  from google.genai import types as genai_types
  from google.adk.agents import Agent

  gen_config = genai_types.GenerateContentConfig(
      temperature=0.2,            # 控制隨機性 (0.0-1.0)，較低值更具確定性。
      top_p=0.9,                  # 核心取樣：從 top_p 機率質量中取樣。
      top_k=40,                   # Top-k 取樣：從 top_k 最可能的權杖中取樣。
      max_output_tokens=1024,     # LLM 回應中的最大權杖數。
      stop_sequences=["## END"]   # 如果出現這些序列，LLM 將停止生成。
  )
  agent = Agent(
      # ... 基本組態 ...
      generate_content_config=gen_config
  )
  ```

- **`output_key`**：自動將代理的最終文字或結構化 (如果使用 `output_schema`) 回應儲存到 `session.state` 中，並使用此鍵。有助於代理之間的資料流動。

  ```python
  agent = Agent(
      # ... 基本組態 ...
      output_key="llm_final_response_text"
  )
  # 代理執行後，session.state['llm_final_response_text'] 將包含其輸出。
  ```

- **`input_schema` & `output_schema`**：使用 Pydantic 模型定義嚴格的 JSON 輸入/輸出格式。
  > **警告**：使用 `output_schema` 會強制 LLM 生成 JSON，並**停用**其使用工具或委派給其他代理的能力。

#### **範例：定義和使用結構化輸出**

這是讓 LLM 產生可預測、可解析的 JSON 最可靠的方法，這對於多代理工作流程至關重要。

1.  **使用 Pydantic 定義結構：**

    ```python
    from pydantic import BaseModel, Field
    from typing import Literal

    class SearchQuery(BaseModel):
        """代表用於網路搜尋的特定搜尋查詢的模型。"""
        search_query: str = Field(
            description="一個用於網路搜尋的高度具體和有針對性的查詢。"
        )

    class Feedback(BaseModel):
        """用於提供研究品質評估回饋的模型。"""
        grade: Literal["pass", "fail"] = Field(
            description="評估結果。如果研究足夠，則為 'pass'；如果需要修改，則為 'fail'。"
        )
        comment: str = Field(
            description="評估的詳細解釋，突顯研究的優點和/或缺點。"
        )
        follow_up_queries: list[SearchQuery] | None = Field(
            default=None,
            description="為彌補研究差距所需的具體、有針對性的後續搜尋查詢列表。如果評分為 'pass'，此項應為 null 或空。"
        )
    ```

    - **`BaseModel` & `Field`**：定義資料類型、預設值和關鍵的 `description` 欄位。這些描述會被傳送給 LLM 以指導其輸出。
    - **`Literal`**：強制執行嚴格的列舉式值 (`"pass"` 或 `"fail"`)，防止 LLM 產生意料之外的值。

2.  **將結構指派給 `LlmAgent`：**
    ```python
    research_evaluator = LlmAgent(
        name="research_evaluator",
        model="gemini-3-pro-preview",
        instruction="""你是一位一絲不苟的品質保證分析師。評估 'section_research_findings' 中的研究發現，並非常嚴格。
        如果你發現重大差距，給予 'fail' 的評分，撰寫詳細評論，並產生 5-7 個具體的後續查詢。
        如果研究透徹，則評分為 'pass'。
        你的回應必須是單一、原始的 JSON 物件，並通過 'Feedback' 結構的驗證。
        """,
        output_schema=Feedback, # 這會強制 LLM 輸出符合 Feedback 模型的 JSON。
        output_key="research_evaluation", # 產生的 JSON 物件將被儲存到狀態中。
        disallow_transfer_to_peers=True, # 防止此代理進行委派。它的工作只是評估。
    )
    ```

- **`include_contents`**：控制是否將對話歷史傳送給 LLM。

  - `'default'` (預設)：傳送相關歷史。
  - `'none'`：不傳送任何歷史；代理僅根據當前回合的輸入和 `instruction` 運作。適用於無狀態的 API 包裝器代理。

  ```python
  agent = Agent(..., include_contents='none')
  ```

- **`planner`**：指派一個 `BasePlanner` 實例以啟用多步驟推理。

  - **`BuiltInPlanner`**：利用模型的原生「思考」或規劃能力 (例如 Gemini)。

    ```python
    from google.adk.planners import BuiltInPlanner
    from google.genai.types import ThinkingConfig

    agent = Agent(
        model="gemini-3-flash-preview",
        planner=BuiltInPlanner(
            thinking_config=ThinkingConfig(include_thoughts=True)
        ),
        # ... 工具 ...
    )
    ```

  - **`PlanReActPlanner`**：指示模型遵循結構化的 Plan-Reason-Act 輸出格式，適用於沒有內建規劃功能的模型。

- **`code_executor`**：指派一個 `BaseCodeExecutor` 以允許代理執行程式碼區塊。

  - **`BuiltInCodeExecutor`**：ADK 提供的標準、沙箱化的程式碼執行器，用於安全執行。
    ```python
    from google.adk.code_executors import BuiltInCodeExecutor
    agent = Agent(
        name="code_agent",
        model="gemini-3-flash-preview",
        instruction="編寫並執行 Python 程式碼來解決數學問題。",
        code_executor=BuiltInCodeExecutor() # 從列表更正為實例
    )
    ```

- **Callbacks**：在關鍵生命週期點觀察和修改代理行為的掛鉤 (`before_model_callback`, `after_tool_callback` 等)。(在回呼章節中涵蓋)。

### 2.3 LLM 指令設計 (`instruction`)

`instruction` 至關重要。它指導 LLM 的行為、角色和工具使用。以下範例展示了創建專業、可靠代理的強大技術。

**最佳實踐與範例：**

- **具體且簡潔**：避免模稜兩可。
- **定義角色與職責**：給予 LLM 一個清晰的角色。
- **約束行為與工具使用**：明確說明 LLM *應該*和*不應該*做什麼。
- **定義輸出格式**：告訴 LLM 其輸出*確切*應該是什麼樣子，尤其是在不使用 `output_schema` 時。
- **動態注入**：使用 `{state_key}` 將 `session.state` 中的執行期資料注入到提示中。
- **迭代**：測試、觀察並改進指令。

**範例 1：約束工具使用和輸出格式**

```python
import datetime
from google.adk.tools import google_search


plan_generator = LlmAgent(
    model="gemini-3-flash-preview",
    name="plan_generator",
    description="產生一個 4-5 行以行動為導向的研究計畫。",
    instruction=f"""
    你是一位研究策略師。你的工作是創建一個高層次的「研究計畫」，而不是摘要。
    **規則：你的輸出必須是一個包含 4-5 個以行動為導向的研究目標或關鍵問題的項目符號列表。**
    - 一個好的目標以動詞開頭，如「分析」、「識別」、「調查」。
    - 一個不好的輸出是事實陳述，如「該事件發生在 2024 年 4 月」。
    **工具使用受到嚴格限制：**
    你的目標是創建一個通用、高品質的計畫，*而無需搜尋*。
    只有在主題模稜兩可且你絕對無法在沒有它的情況下創建計畫時，才使用 `google_search`。
    你被明確禁止研究主題的*內容*或*主題*。
    目前日期：{datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[google_search],
)
```

**範例 2：從狀態注入資料並指定自訂標籤**
此代理的 `instruction` 依賴於先前代理放置在 `session.state` 中的資料。

```python
report_composer = LlmAgent(
    model="gemini-3-pro-preview",
    name="report_composer_with_citations",
    include_contents="none", # 不需要歷史記錄；所有資料都已注入。
    description="將研究資料和 markdown 大綱轉換為最終的、帶有引用的報告。",
    instruction="""
    將提供的資料轉換為一份精美、專業且引用嚴謹的研究報告。

    ---
    ### 輸入資料
    *   研究計畫：`{research_plan}`
    *   研究發現：`{section_research_findings}`
    *   引用來源：`{sources}`
    *   報告結構：`{report_sections}`

    ---
    ### 關鍵：引用系統
    要引用一個來源，你必須在其支持的主張之後直接插入一個特殊的引用標籤。

    **唯一正確的格式是：** `<cite source="src-ID_NUMBER" />`

    ---
    ### 最終指令
    使用「僅」`<cite source="src-ID_NUMBER" />` 標籤系統為所有引用生成一份綜合報告。
    最終報告必須嚴格遵循**報告結構** markdown 大綱中提供的結構。
    不要包含「參考文獻」或「來源」部分；所有引用都必須是行內引用。
    """,
    output_key="final_cited_report",
)
```

### 2.4 生產環境包裝器 (`App`)

包裝 `root_agent` 以啟用 `Agent` 單獨無法處理的生產級執行期功能。

```python
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps.events_compaction_config import EventsCompactionConfig
from google.adk.apps.resumability_config import ResumabilityConfig

production_app = App(
    name="my_app",
    root_agent=my_agent,
    # 1. 為長上下文降低成本/延遲
    context_cache_config=ContextCacheConfig(min_tokens=2048, ttl_seconds=600),
    # 2. 允許從上次狀態恢復崩潰的工作流程
    resumability_config=ResumabilityConfig(is_resumable=True),
    # 3. 自動管理長對話歷史
    events_compaction_config=EventsCompactionConfig(compaction_interval=5, overlap_size=1)
)

# 用法：將 'app' 而非 'agent' 傳遞給 Runner
# runner = Runner(app=production_app, ...)
```

---

## 3. 使用工作流程代理進行編排

工作流程代理 (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) 提供確定性的控制流程，將 LLM 的能力與結構化執行相結合。它們**不**使用 LLM 來進行自己的編排邏輯。

### 3.1 `SequentialAgent`: 線性執行

按照定義的順序逐一執行 `sub_agents`。`InvocationContext` 會被傳遞下去，使得狀態變更對後續的代理可見。

```python
from google.adk.agents import SequentialAgent, Agent

# 代理 1：摘要文件並儲存到狀態
summarizer = Agent(
    name="DocumentSummarizer",
    model="gemini-3-flash-preview",
    instruction="用 3 個句子摘要提供的文件。",
    output_key="document_summary" # 輸出儲存到 session.state['document_summary']
)

# 代理 2：根據狀態中的摘要生成問題
question_generator = Agent(
    name="QuestionGenerator",
    model="gemini-3-flash-preview",
    instruction="根據此摘要生成 3 個理解問題：{document_summary}",
    # 'document_summary' 從 session.state 動態注入
)

document_pipeline = SequentialAgent(
    name="SummaryQuestionPipeline",
    sub_agents=[summarizer, question_generator], # 順序很重要！
    description="摘要文件然後生成問題。"
)
```

### 3.2 `ParallelAgent`: 並行執行

同時執行 `sub_agents`。適用於獨立任務以減少整體延遲。所有子代理共享相同的 `session.state`。

```python
from google.adk.agents import ParallelAgent, Agent, SequentialAgent

# 並行獲取資料的代理
fetch_stock_price = Agent(name="StockPriceFetcher", ..., output_key="stock_data")
fetch_news_headlines = Agent(name="NewsFetcher", ..., output_key="news_data")
fetch_social_sentiment = Agent(name="SentimentAnalyzer", ..., output_key="sentiment_data")

# 合併結果的代理 (在 ParallelAgent 之後執行，通常在 SequentialAgent 中)
merger_agent = Agent(
    name="ReportGenerator",
    model="gemini-3-flash-preview",
    instruction="將股票資料：{stock_data}、新聞：{news_data} 和情緒：{sentiment_data} 合併成一份市場報告。"
)

# 先並行獲取然後順序合併的管線
market_analysis_pipeline = SequentialAgent(
    name="MarketAnalyzer",
    sub_agents=[
        ParallelAgent(
            name="ConcurrentFetch",
            sub_agents=[fetch_stock_price, fetch_news_headlines, fetch_social_sentiment]
        ),
        merger_agent # 在所有並行代理完成後執行
    ]
)
```

- **並行性警告**：當並行代理寫入相同的 `state` 鍵時，可能會發生競爭條件。請始終使用不同的 `output_key` 或明確管理並行寫入。

### 3.3 `LoopAgent`: 迭代過程

重複執行其 `sub_agents` (在每個迴圈迭代中順序執行)，直到滿足條件或達到 `max_iterations`。

#### **`LoopAgent` 的終止**

`LoopAgent` 在以下情況下終止：

1.  達到 `max_iterations`。
2.  子代理 (或其內的工具) 產生的任何 `Event` 將 `actions.escalate` 設為 `True`。這提供了動態的、由內容驅動的迴圈終止。

#### **範例：使用自訂 `BaseAgent` 進行控制的迭代改進迴圈**

此範例顯示一個迴圈，它會持續進行，直到由評估代理決定的條件被滿足為止。

```python
from google.adk.agents import LoopAgent, Agent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

# 一個評估研究並產生結構化 JSON 輸出的 LLM 代理
research_evaluator = Agent(
    name="research_evaluator",
    # ... 來自第 2.2 節的組態 ...
    output_schema=Feedback,
    output_key="research_evaluation",
)

# 一個根據回饋執行額外搜尋的 LLM 代理
enhanced_search_executor = Agent(
    name="enhanced_search_executor",
    instruction="執行 'research_evaluation' 中的後續查詢，並與現有發現結合。",
    # ... 其他組態 ...
)

# 一個自訂的 BaseAgent 來檢查評估並停止迴圈
class EscalationChecker(BaseAgent):
    """檢查研究評估，如果評分為 'pass'，則上報以停止迴圈。"""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        evaluation = ctx.session.state.get("research_evaluation")
        if evaluation and evaluation.get("grade") == "pass":
            # 停止迴圈的關鍵：產生一個 escalate=True 的 Event
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            # 讓迴圈繼續
            yield Event(author=self.name)

# 定義迴圈
iterative_refinement_loop = LoopAgent(
    name="IterativeRefinementLoop",
    sub_agents=[
        research_evaluator, # 步驟 1：評估
        EscalationChecker(name="EscalationChecker"), # 步驟 2：檢查並可能停止
        enhanced_search_executor, # 步驟 3：改進 (僅在迴圈未停止時執行)
    ],
    max_iterations=5, # 防止無限迴圈的備用方案
    description="迭代評估和改進研究，直到通過品質檢查。"
)
```

---

## 4. 多代理系統與通訊

透過組合多個專業代理來建構複雜的應用程式。

### 4.1 代理層級結構

由 `BaseAgent` 初始化期間的 `sub_agents` 參數定義的父子關係的層級 (樹狀) 結構。一個代理只能有一個父代理。

```python
# 概念層級結構
# Root
# └── Coordinator (LlmAgent)
#     ├── SalesAgent (LlmAgent)
#     └── SupportAgent (LlmAgent)
#     └── DataPipeline (SequentialAgent)
#         ├── DataFetcher (LlmAgent)
#         └── DataProcessor (LlmAgent)
```

### 4.2 代理間通訊機制

1.  **共享會話狀態 (`session.state`)**：最常見且最穩健的方法。代理讀取和寫入同一個可變字典。

    - **機制**：代理 A 設定 `ctx.session.state['key'] = value`。代理 B 稍後讀取 `ctx.session.state.get('key')`。`LlmAgent` 上的 `output_key` 是一個方便的自動設定器。
    - **最適用於**：在管線 (Sequential, Loop 代理) 中傳遞中間結果、共享組態和旗標。

2.  **LLM 驅動的委派 (`transfer_to_agent`)**：`LlmAgent` 可以根據其推理動態地將控制權移交給另一個代理。

    - **機制**：LLM 生成一個特殊的 `transfer_to_agent` 函式呼叫。ADK 框架攔截此呼叫，將下一輪路由到目標代理。
    - **先決條件**：
      - 發起的 `LlmAgent` 需要 `instruction` 來指導委派，以及目標代理的 `description`。
      - 目標代理需要清晰的 `description` 來幫助 LLM 做出決定。
      - 目標代理必須在目前代理的層級結構中可被發現 (直接的 `sub_agent` 或後代)。
    - **組態**：可以透過 `LlmAgent` 上的 `disallow_transfer_to_parent` 和 `disallow_transfer_to_peers` 來啟用/停用。

3.  **明確叫用 (`AgentTool`)**：`LlmAgent` 可以將另一個 `BaseAgent` 實例視為可呼叫的工具。
    - **機制**：將目標代理 (`target_agent`) 包裝在 `AgentTool(agent=target_agent)` 中，並將其添加到呼叫 `LlmAgent` 的 `tools` 列表中。`AgentTool` 為 LLM 生成一個 `FunctionDeclaration`。當被呼叫時，`AgentTool` 執行目標代理並將其最終回應作為工具結果返回。
    - **最適用於**：層級任務分解，其中較高層級的代理需要來自較低層級代理的特定輸出。

**委派 vs. 代理即工具**

- **委派 (`sub_agents`)**：父代理*轉移控制權*。子代理在後續的回合中直接與使用者互動，直到完成。
- **代理即工具 (`AgentTool`)**：父代理像函式一樣*呼叫*另一個代理。父代理保持控制，接收子代理的整個互動作為單一工具結果，並為使用者總結它。

```python
# 委派：「我讓專家來處理這個對話。」
root = Agent(name="root", sub_agents=[specialist])

# 代理即工具：「我需要專家完成一項任務並給我結果。」
from google.adk.tools import AgentTool
root = Agent(name="root", tools=[AgentTool(specialist)])
```

### 4.3 常見的多代理模式

- **協調器/調度器**：一個中央代理將請求路由到專業的子代理 (通常透過 LLM 驅動的委派)。
- **順序管線**：`SequentialAgent` 編排一個固定的任務序列，透過共享狀態傳遞資料。
- **並行扇出/收集**：`ParallelAgent` 執行並行任務，然後由一個最終代理從狀態中綜合結果。
- **審查/評論 (生成器-評論家)**：`SequentialAgent` 帶有一個生成器，後跟一個評論家，通常在 `LoopAgent` 中進行迭代改進。
- **層級任務分解 (規劃器/執行器)**：高層級代理分解複雜問題，將子任務委派給低層級代理 (通常透過 `AgentTool` 和委派)。

#### **範例：層級規劃器/執行器模式**

此模式結合了多種機制。一個頂層的 `interactive_planner_agent` 使用另一個代理 (`plan_generator`) 作為工具來創建計畫，然後將該計畫的執行委派給一個複雜的 `SequentialAgent` (`research_pipeline`)。

```python
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools.agent_tool import AgentTool

# 假設 plan_generator, section_planner, research_evaluator 等已定義。

# 執行管線本身就是一個複雜的代理。
research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="執行一個預先批准的研究計畫。它執行迭代研究、評估，並撰寫一份最終的、帶有引用的報告。",
    sub_agents=[
        section_planner,
        section_researcher,
        LoopAgent(
            name="iterative_refinement_loop",
            max_iterations=3,
            sub_agents=[
                research_evaluator,
                EscalationChecker(name="escalation_checker"),
                enhanced_search_executor,
            ],
        ),
        report_composer,
    ],
)

# 與使用者互動的頂層代理。
interactive_planner_agent = LlmAgent(
    name="interactive_planner_agent",
    model="gemini-3-flash-preview",
    description="主要的研究助理。它與使用者合作創建研究計畫，並在批准後執行。",
    instruction="""
    你是一位研究規劃助理。你的工作流程是：
    1.  **計畫：** 使用 `plan_generator` 工具創建一個研究計畫草案。
    2.  **改進：** 納入使用者回饋，直到計畫被批准。
    3.  **執行：** 一旦使用者給予「明確」批准 (例如，「看起來不錯，執行吧」)，你「必須」將任務委派給 `research_pipeline` 代理。
    你的工作是規劃、改進和委派。不要自己做研究。
    """,
    # 規劃器委派給管線。
    sub_agents=[research_pipeline],
    # 規劃器使用另一個代理作為工具。
    tools=[AgentTool(plan_generator)],
    output_key="research_plan",
)

# 應用程式的根代理是頂層規劃器。
root_agent = interactive_planner_agent
```

### 4.A. 分散式通訊 (A2A 協定)

代理對代理 (A2A) 協定使代理能夠透過網路進行通訊，即使它們是用不同語言編寫或作為獨立服務執行。使用 A2A 來整合第三方代理、建構基於微服務的代理架構，或當需要強大、正式的 API 合約時。對於內部程式碼組織，請優先使用本地子代理。

- **公開代理**：讓現有的 ADK 代理可供其他代理透過 A2A 使用。

  - **`to_a2a()` 工具程式**：最簡單的方法。包裝您的 `root_agent` 並創建一個可執行的 FastAPI 應用程式，自動生成所需的 `agent.json` 卡片。
    ```python
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
    # root_agent 是您現有的 ADK Agent 實例
    a2a_app = to_a2a(root_agent, port=8001)
    # 使用以下指令執行：uvicorn your_module:a2a_app --host localhost --port 8001
    ```
  - **`adk api_server --a2a`**：一個從目錄提供代理的 CLI 指令。需要您為每個要公開的代理手動創建一個 `agent.json` 卡片。

- **使用遠端代理**：像使用本地代理一樣使用遠端 A2A 代理。

  - **`RemoteA2aAgent`**：此代理充當客戶端代理。您使用遠端代理卡片的 URL 來初始化它。

    ```python
    from google.adk.a2a.remote_a2a_agent import RemoteA2aAgent

    # 此代理現在可以作為子代理或工具使用
    prime_checker_agent = RemoteA2aAgent(
        name="prime_agent",
        description="一個檢查數字是否為質數的遠端代理。",
        agent_card="http://localhost:8001/a2a/check_prime_agent/.well-known/agent.json"
    )
    ```

---

## 5. 建構自訂代理 (`BaseAgent`)

對於不符合標準工作流程代理的獨特編排邏輯，直接繼承自 `BaseAgent`。

### 5.1 何時使用自訂代理

- **複雜的條件邏輯**：基於多個狀態變數的 `if/else` 分支。
- **動態代理選擇**：根據執行期評估選擇要執行的子代理。
- **直接外部整合**：在編排流程中直接呼叫外部 API 或函式庫。
- **自訂迴圈/重試邏輯**：比 `LoopAgent` 更複雜的迭代模式，例如 `EscalationChecker` 範例。

### 5.2 實作 `_run_async_impl`

這是您必須覆寫的核心非同步方法。

#### **範例：用於迴圈控制的自訂代理**

此代理讀取狀態，應用簡單的 Python 邏輯，並產生一個帶有 `escalate` 動作的 `Event` 來控制 `LoopAgent`。

```python
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from typing import AsyncGenerator
import logging

class EscalationChecker(BaseAgent):
    """檢查研究評估，如果評分為 'pass'，則上報以停止迴圈。"""

    def __init__(self, name: str):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # 1. 從會話狀態讀取。
        evaluation_result = ctx.session.state.get("research_evaluation")

        # 2. 應用自訂 Python 邏輯。
        if evaluation_result and evaluation_result.get("grade") == "pass":
            logging.info(
                f"[{self.name}] 研究通過。上報以停止迴圈。"
            )
            # 3. 產生一個帶有控制動作的 Event。
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            logging.info(
                f"[{self.name}] 研究失敗或未找到。迴圈繼續。"
            )
            # 產生一個沒有動作的事件讓流程繼續。
            yield Event(author=self.name)
```

- **非同步產生器**：`async def ... yield Event`。這允許暫停和恢復執行。
- **`ctx: InvocationContext`**：提供對所有會話狀態 (`ctx.session.state`) 的存取。
- **呼叫子代理**：使用 `async for event in self.sub_agent_instance.run_async(ctx): yield event`。
- **控制流程**：使用標準的 Python `if/else`, `for/while` 迴圈來實現複雜邏輯。

---

## 6. 模型：Gemini、LiteLLM 與 Vertex AI

ADK 的模型靈活性允許整合各種 LLM 以滿足不同需求。

### 6.1 Google Gemini 模型 (AI Studio & Vertex AI)

- **預設整合**：透過 `google-genai` 函式庫原生支援。
- **AI Studio (輕鬆入門)**：
  - 設定 `GOOGLE_API_KEY="YOUR_API_KEY"` (環境變數)。
  - 設定 `GOOGLE_GENAI_USE_VERTEXAI="False"`。
  - 模型字串：`"gemini-3-flash-preview"`, `"gemini-3-pro-preview"` 等。
- **Vertex AI (生產環境)**：
  - 透過 `gcloud auth application-default login` 進行驗證 (建議)。
  - 設定 `GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"`, `GOOGLE_CLOUD_LOCATION="your-region"` (環境變數)。
  - 設定 `GOOGLE_GENAI_USE_VERTEXAI="True"`。
  - 模型字串：`"gemini-3-flash-preview"`, `"gemini-3-pro-preview"`，或特定部署的完整 Vertex AI 端點資源名稱。

### 6.2 透過 LiteLLM 使用其他雲端與專有模型

`LiteLlm` 提供了一個統一的介面來存取 100 多種 LLM (OpenAI, Anthropic, Cohere 等)。

- **安裝**：`pip install litellm`
- **API 金鑰**：根據 LiteLLM 的要求設定環境變數 (例如 `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)。
- **用法**：
  ```python
  from google.adk.models.lite_llm import LiteLlm
  agent_openai = Agent(model=LiteLlm(model="openai/gpt-4o"), ...)
  agent_claude = Agent(model=LiteLlm(model="anthropic/claude-3-haiku-20240307"), ...)
  ```

### 6.3 透過 LiteLLM 使用開放與本地模型 (Ollama, vLLM)

用於自架、節省成本、隱私或離線使用。

- **Ollama 整合**：在本地執行 Ollama (`ollama run <model>`)。

  ```bash
  export OLLAMA_API_BASE="http://localhost:11434" # 確保 Ollama 伺服器正在執行
  ```

  ```python
  from google.adk.models.lite_llm import LiteLlm
  # 使用 'ollama_chat' 提供者以獲得 Ollama 模型的工具呼叫能力
  agent_ollama = Agent(model=LiteLlm(model="ollama_chat/llama3:instruct"), ...)
  ```

- **自架端點 (例如 vLLM)**：
  ```python
  from google.adk.models.lite_llm import LiteLlm
  api_base_url = "https://your-vllm-endpoint.example.com/v1"
  agent_vllm = Agent(
      model=LiteLlm(
          model="your-model-name-on-vllm",
          api_base=api_base_url,
          extra_headers={"Authorization": "Bearer YOUR_TOKEN"},
      ),
      ...
  )
  ```

### 6.4 自訂 LLM API 客戶端

對於 `google-genai` (由 Gemini 模型使用)，您可以設定底層的客戶端。

```python
import os
from google.genai import configure as genai_configure

genai_configure.use_defaults(
    timeout=60, # 秒
    client_options={"api_key": os.getenv("GOOGLE_API_KEY")},
)
```

---

## 7. 工具：代理的能力

工具擴展了代理超越文字生成的能力。

### 7.1 定義函式工具：原則與最佳實踐

- **簽章**：`def my_tool(param1: Type, param2: Type, tool_context: ToolContext) -> dict:`
- **函式名稱**：描述性的動詞-名詞 (例如 `schedule_meeting`)。
- **參數**：清晰的名稱，必要的類型提示，**沒有預設值**。
- **返回類型**：**必須**是 `dict` (可 JSON 序列化)，最好帶有 `'status'` 鍵。
- **文件字串 (Docstring)**：**至關重要**。解釋目的、何時使用、參數和返回值結構。**避免**提及 `tool_context`。

  ```python
  def calculate_compound_interest(
      principal: float,
      rate: float,
      years: int,
      compounding_frequency: int,
      tool_context: ToolContext
  ) -> dict:
      """計算複利投資的未來價值。

      使用此工具計算投資的未來價值，給定
      本金、年利率、投資年數以及每年
      複利的次數。

      Args:
          principal (float): 初始投資金額。
          rate (float): 年利率 (例如，5% 為 0.05)。
          years (int): 投資的年數。
          compounding_frequency (int): 每年複利的次數
                                       (例如，每年為 1，每月為 12)。

      Returns:
          dict: 包含計算結果。
                - 'status' (str): "success" 或 "error"。
                - 'future_value' (float, optional): 計算出的未來價值。
                - 'error_message' (str, optional): 錯誤描述 (如果有的話)。
      """
      # ... 實作 ...
  ```

### 7.2 `ToolContext` 物件：存取執行期資訊

`ToolContext` 是工具與 ADK 執行期互動的閘道。

- `tool_context.state`：讀取和寫入目前 `Session` 的 `state` 字典。
- `tool_context.actions`：修改 `EventActions` 物件 (例如 `tool_context.actions.escalate = True`)。
- `tool_context.load_artifact(filename)` / `tool_context.save_artifact(filename, part)`：管理二進位資料。
- `tool_context.search_memory(query)`：查詢長期 `MemoryService`。

### 7.3 所有工具類型及其用法

1.  **自訂函式工具**：

    - **`FunctionTool`**：最常見的類型，包裝一個標準的 Python 函式。
    - **`LongRunningFunctionTool`**：包裝一個 `async` 函式，該函式 `yields` 中間結果，用於提供進度更新的任務。
    - **`AgentTool`**：包裝另一個 `BaseAgent` 實例，允許它被父代理作為工具叫用。

2.  **內建工具**：ADK 提供的即用型工具。

    - `google_search`：提供 Google 搜尋的 grounding。
    - **程式碼執行**：
      - `BuiltInCodeExecutor`：本地，方便開發。**不**適用於不受信任的生產環境。
      - `GkeCodeExecutor`：生產級。在 Google Kubernetes Engine (GKE) 上的臨時、沙箱化 pod 中執行程式碼，使用 gVisor 進行隔離。需要 GKE 叢集設定。
    - `VertexAiSearchTool`：從您的私有 Vertex AI Search 資料儲存中提供 grounding。
    - `BigQueryToolset`：用於與 BigQuery 互動的工具集合 (例如 `list_datasets`, `execute_sql`)。
      > **警告**：一個代理一次只能使用一種內建工具，且它們不能在子代理中使用。

3.  **第三方工具包裝器**：用於與其他框架無縫整合。

    - `LangchainTool`：包裝來自 LangChain 生態系統的工具。

4.  **OpenAPI 與協定工具**：用於與 API 和服務互動。

    - **`OpenAPIToolset`**：從 OpenAPI (Swagger) v3 規範自動生成一組 `RestApiTool`。
    - **`MCPToolset`**：連接到外部模型上下文協定 (MCP) 伺服器，以動態載入其工具。

5.  **Google Cloud 工具**：用於與 Google Cloud 服務深度整合。

    - **`ApiHubToolset`**：將 Apigee API Hub 中任何有文件的 API 轉換為工具。
    - **`ApplicationIntegrationToolset`**：將 Application Integration 工作流程和 Integration Connectors (例如 Salesforce, SAP) 轉換為可呼叫的工具。
    - **Toolbox for Databases**：一個開源的 MCP 伺服器，ADK 可以連接到它以進行資料庫互動。

6.  **動態工具集 (`BaseToolset`)**：與其使用靜態的工具列表，不如使用 `Toolset` 根據目前上下文 (例如使用者權限) 動態決定代理可以使用哪些工具。

    ```python
    from google.adk.tools.base_toolset import BaseToolset

    class AdminAwareToolset(BaseToolset):
        async def get_tools(self, context: ReadonlyContext) -> list[BaseTool]:
            # 檢查狀態以查看使用者是否為管理員
            if context.state.get('user:role') == 'admin':
                 return [admin_delete_tool, standard_query_tool]
            return [standard_query_tool]

    # 用法：
    agent = Agent(tools=[AdminAwareToolset()])
    ```

### 7.4 工具確認 (人在迴路)

ADK 可以在繼續執行前暫停工具執行以請求人類或系統確認，這對於敏感操作至關重要。

- **布林確認**：透過 `FunctionTool(..., require_confirmation=True)` 進行簡單的是/否確認。
- **動態確認**：將一個函式傳遞給 `require_confirmation`，以根據參數在執行期決定。
- **進階/負載確認**：在工具內部使用 `tool_context.request_confirmation()` 以獲得結構化回饋。

```python
from google.adk.tools import FunctionTool, ToolContext

# 1. 簡單布林確認
# 暫停執行，直到收到 'confirmed': True/False 事件。
sensitive_tool = FunctionTool(delete_database, require_confirmation=True)

# 2. 動態閾值確認
def needs_approval(amount: float, **kwargs) -> bool:
    return amount > 10000

transfer_tool = FunctionTool(wire_money, require_confirmation=needs_approval)

# 3. 進階負載確認 (在工具定義內部)
def book_flight(destination: str, price: float, tool_context: ToolContext):
    # 暫停並要求使用者在繼續前選擇座位等級
    tool_context.request_confirmation(
        hint="請確認預訂並選擇座位等級。",
        payload={"seat_class": ["economy", "business", "first"]} # 預期結構
    )
    return {"status": "pending_confirmation"}
```

---

## 8. 上下文、狀態與記憶體管理

有效的上下文管理對於連貫的多輪對話至關重要。

### 8.1 `Session` 物件與 `SessionService`

- **`Session`**：單一、持續對話的容器 (`id`, `state`, `events`)。
- **`SessionService`**：管理 `Session` 物件的生命週期 (`create_session`, `get_session`, `append_event`)。
- **實作**：`InMemorySessionService` (開發)、`VertexAiSessionService` (生產)、`DatabaseSessionService` (自行管理)。

### 8.2 `State`: 對話暫存區

`session.state` 中的一個可變字典，用於短期、動態的資料。

- **更新機制**：始終透過 `context.state` (在回呼/工具中) 或 `LlmAgent.output_key` 進行更新。
- **範圍前綴**：
  - **(無前綴)**：會話特定 (例如 `session.state['booking_step']`)。
  - `user:`：對一個 `user_id` 在其所有會話中持續存在 (例如 `session.state['user:preferred_currency']`)。
  - `app:`：對 `app_name` 在所有使用者和會話中持續存在。
  - `temp:`：僅存在於目前**叫用** (一個使用者請求 -> 最終代理回應週期) 的臨時狀態。之後會被丟棄。

### 8.3 `Memory`: 長期知識與檢索

用於超越單一對話的知識。

- **`BaseMemoryService`**：定義介面 (`add_session_to_memory`, `search_memory`)。
- **實作**：`InMemoryMemoryService`, `VertexAiRagMemoryService`。
- **用法**：代理透過工具互動 (例如內建的 `load_memory` 工具)。

### 8.4 `Artifacts`: 二進位資料管理

用於具名、版本化的二進位資料 (檔案、圖片)。

- **表示**：`google.genai.types.Part` (包含一個帶有 `data: bytes` 和 `mime_type: str` 的 `Blob`)。
- **`BaseArtifactService`**：管理儲存 (`save_artifact`, `load_artifact`)。
- **實作**：`InMemoryArtifactService`, `GcsArtifactService`。

---

## 9. 執行期、事件與執行流程

`Runner` 是 ADK 應用程式的中央編排器。

### 9.1 執行期組態 (`RunConfig`)

傳遞給 `run` 或 `run_live` 以控制執行限制和輸出格式。

```python
from google.adk.agents.run_config import RunConfig
from google.genai import types

config = RunConfig(
    # 安全限制
    max_llm_calls=100,  # 防止無限代理迴圈

    # 串流與模態
    response_modalities=["AUDIO", "TEXT"], # 請求特定的輸出格式

    # 語音組態 (用於 AUDIO 模態)
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        )
    ),

    # 除錯
    save_input_blobs_as_artifacts=True # 將上傳的檔案儲存到 ArtifactService
)
```

### 9.2 `Runner`: 編排器

- **角色**：管理代理的生命週期、事件迴圈，並與服務協調。
- **進入點**：`runner.run_async(user_id, session_id, new_message)`。

### 9.3 事件迴圈：核心執行流程

1.  使用者輸入成為一個 `user` `Event`。
2.  `Runner` 呼叫 `agent.run_async(invocation_context)`。
3.  代理 `yield` 一個 `Event` (例如工具呼叫、文字回應)。執行暫停。
4.  `Runner` 處理 `Event` (應用狀態變更等) 並將其 `yield` 給客戶端。
5.  執行恢復。此循環重複直到代理完成。

### 9.4 `Event` 物件：通訊骨幹

`Event` 物件攜帶所有資訊和信號。

- `Event.author`：事件的來源 (`'user'`, 代理名稱, `'system'`)。
- `Event.content`：主要負載 (文字、函式呼叫、函式回應)。
- `Event.actions`：信號副作用 (`state_delta`, `transfer_to_agent`, `escalate`)。
- `Event.is_final_response()`：用於識別完整、可顯示訊息的輔助函式。

### 9.5 非同步程式設計 (Python 特定)

ADK 建構在 `asyncio` 之上。對所有 I/O 密集型操作使用 `async def`、`await` 和 `async for`。

---

## 10. 使用回呼控制流程

回呼是在特定點攔截和控制代理執行的函式。

### 10.1 回呼機制：攔截與控制

- **定義**：指派給代理 `callback` 參數的 Python 函式 (例如 `after_agent_callback=my_func`)。
- **上下文**：接收一個帶有執行期資訊的 `CallbackContext` (或 `ToolContext`)。
- **返回值**：**關鍵地決定流程**。
  - `return None`：允許預設動作繼續。
  - `return <Specific Object>`：**覆寫**預設動作/結果。

### 10.2 回呼類型

1.  **代理生命週期**：`before_agent_callback`, `after_agent_callback`。
2.  **LLM 互動**：`before_model_callback`, `after_model_callback`。
3.  **工具執行**：`before_tool_callback`, `after_tool_callback`。

### 10.3 回呼最佳實踐

- **保持專注**：每個回呼用於單一目的。
- **效能**：避免阻塞 I/O 或繁重的計算。
- **錯誤處理**：使用 `try...except` 來防止崩潰。

#### **範例 1：使用 `after_agent_callback` 進行資料彙總**

此回呼在代理執行後運行，檢查 `session.events` 以尋找來自工具呼叫的結構化資料 (如 `google_search` 結果)，並將其儲存到狀態中以供後續使用。

```python
from google.adk.agents.callback_context import CallbackContext

def collect_research_sources_callback(callback_context: CallbackContext) -> None:
    """從代理事件中收集並組織網路研究來源。"""
    session = callback_context._invocation_context.session
    # 從狀態中獲取現有來源以附加到它們。
    url_to_short_id = callback_context.state.get("url_to_short_id", {})
    sources = callback_context.state.get("sources", {})
    id_counter = len(url_to_short_id) + 1

    # 迭代會話中的所有事件以尋找 grounding 元資料。
    for event in session.events:
        if not (event.grounding_metadata and event.grounding_metadata.grounding_chunks):
            continue
        # ... 解析 grounding_chunks 和 grounding_supports 的邏輯 ...
        # (請參閱原始程式碼片段中的完整實作)

    # 將更新後的來源對應儲存回狀態。
    callback_context.state["url_to_short_id"] = url_to_short_id
    callback_context.state["sources"] = sources

# 在這樣的代理中使用：
# section_researcher = LlmAgent(..., after_agent_callback=collect_research_sources_callback)
```

#### **範例 2：使用 `after_agent_callback` 進行輸出轉換**

此回呼接收 LLM 的原始輸出 (包含自訂標籤)，使用 Python 將其格式化為 markdown，並返回修改後的內容，覆寫原始內容。

```python
import re
from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types

def citation_replacement_callback(callback_context: CallbackContext) -> genai_types.Content:
    """將報告中的 <cite> 標籤替換為 Markdown 格式的連結。"""
    # 1. 從狀態中獲取原始報告和來源。
    final_report = callback_context.state.get("final_cited_report", "")
    sources = callback_context.state.get("sources", {})

    # 2. 為正則表達式替換定義一個替換函式。
    def tag_replacer(match: re.Match) -> str:
        short_id = match.group(1)
        if not (source_info := sources.get(short_id)):
            return "" # 移除無效標籤
        title = source_info.get("title", short_id)
        return f" [{title}]({source_info['url']})"

    # 3. 使用正則表達式找到所有 <cite> 標籤並替換它們。
    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?(src-\d+)["\']?\s*/>',
        tag_replacer,
        final_report,
    )
    processed_report = re.sub(r"\s+([.,;:])", r"\1", processed_report) # 修正間距

    # 4. 將新版本儲存到狀態並返回它以覆寫原始代理輸出。
    callback_context.state["final_report_with_citations"] = processed_report
    return genai_types.Content(parts=[genai_types.Part(text=processed_report)])

# 在這樣的代理中使用：
# report_composer = LlmAgent(..., after_agent_callback=citation_replacement_callback)
```

### 10.A. 使用插件進行全域控制

插件是可狀態化、可重用的模組，用於實作適用於由 `Runner` 管理的所有代理、工具和模型呼叫的橫切關注點。與每個代理單獨設定的回呼不同，插件在 `Runner` 上註冊一次。

- **使用案例**：非常適合通用日誌記錄、應用程式範圍的策略執行、全域快取和收集指標。
- **執行順序**：插件回呼在其對應的代理級別回呼**之前**執行。如果插件回呼返回值，則跳過代理級別的回呼。
- **定義插件**：繼承自 `BasePlugin` 並實作回呼方法。

  ```python
  from google.adk.plugins import BasePlugin
  from google.adk.agents.callback_context import CallbackContext
  from google.adk.models.llm_request import LlmRequest

  class AuditLoggingPlugin(BasePlugin):
      def __init__(self):
          super().__init__(name="audit_logger")

      async def before_model_callback(self, callback_context: CallbackContext, llm_request: LlmRequest):
          # 記錄發送到任何 LLM 的每個提示
          print(f"[AUDIT] Agent {callback_context.agent_name} calling LLM with: {llm_request.contents[-1]}")

      async def on_tool_error_callback(self, tool, error, **kwargs):
          # 所有工具的全域錯誤處理器
          print(f"[ALERT] Tool {tool.name} failed: {error}")
          # 可選地返回一個 dict 來抑制異常並提供備用方案
          return {"status": "error", "message": "An internal error occurred, handled by plugin."}
  ```

- **註冊插件**：
  ```python
  from google.adk.runners import Runner
  # runner = Runner(agent=root_agent, ..., plugins=[AuditLoggingPlugin()])
  ```
- **錯誤處理回呼**：插件支援獨特的錯誤掛鉤，如 `on_model_error_callback` 和 `on_tool_error_callback`，用於集中式錯誤管理。
- **限制**：`adk web` 介面不支援插件。

---

## 11. 工具的驗證

使代理能夠安全地存取受保護的外部資源。

### 11.1 核心概念：`AuthScheme` 與 `AuthCredential`

- **`AuthScheme`**：定義 API *如何*期望驗證 (例如 `APIKey`, `HTTPBearer`, `OAuth2`, `OpenIdConnectWithConfig`)。
- **`AuthCredential`**：持有*啟動*驗證過程的*初始*資訊 (例如 API 金鑰值、OAuth 客戶端 ID/密鑰)。

### 11.2 互動式 OAuth/OIDC 流程

當工具需要使用者互動 (OAuth 同意) 時，ADK 會暫停並向您的 `Agent Client` 應用程式發出信號。

1.  **偵測驗證請求**：`runner.run_async()` 產生一個帶有特殊 `adk_request_credential` 函式呼叫的事件。
2.  **重新導向使用者**：從事件的 `auth_config` 中提取 `auth_uri`。您的客戶端應用程式將使用者的瀏覽器重新導向到此 `auth_uri` (附加 `redirect_uri`)。
3.  **處理回呼**：您的客戶端應用程式有一個預先註冊的 `redirect_uri`，用於在授權後接收使用者。它捕獲完整的的回呼 URL (包含 `authorization_code`)。
4.  **將驗證結果傳送給 ADK**：您的客戶端為 `adk_request_credential` 準備一個 `FunctionResponse`，將 `auth_config.exchanged_auth_credential.oauth2.auth_response_uri` 設定為捕獲的回呼 URL。
5.  **恢復執行**：再次使用此 `FunctionResponse` 呼叫 `runner.run_async()`。ADK 執行權杖交換，儲存存取權杖，並重試原始的工具呼叫。

### 11.3 自訂工具驗證

如果建構需要驗證的 `FunctionTool`：

1.  **檢查快取憑證**：`tool_context.state.get("my_token_cache_key")`。
2.  **檢查驗證回應**：`tool_context.get_auth_response(my_auth_config)`。
3.  **啟動驗證**：如果沒有憑證，呼叫 `tool_context.request_credential(my_auth_config)` 並返回一個待處理狀態。這會觸發外部流程。
4.  **快取憑證**：獲取後，儲存在 `tool_context.state` 中。
5.  **進行 API 呼叫**：使用有效的憑證 (例如 `google.oauth2.credentials.Credentials`)。

---

## 12. 部署策略

從本地開發到生產環境。

### 12.1 本地開發與測試 (`adk web`, `adk run`, `adk api_server`)

- **`adk web`**：啟動一個本地網頁 UI，用於互動式聊天、會話檢查和視覺化追蹤。
  ```bash
  adk web /path/to/your/project_root
  ```
- **`adk run`**：命令列互動式聊天。
  ```bash
  adk run /path/to/your/agent_folder
  ```
- **`adk api_server`**：啟動一個本地 FastAPI 伺服器，公開 `/run`, `/run_sse`, `/list-apps` 等，用於使用 `curl` 或客戶端函式庫進行 API 測試。
  ```bash
  adk api_server /path/to/your/project_root
  ```

### 12.2 Vertex AI 代理引擎

在 Google Cloud 上為 ADK 代理提供的全代管、可擴展的服務。

- **功能**：自動擴展、會話管理、可觀測性整合。
- **ADK CLI**：`adk deploy agent_engine --project <id> --region <loc> ... /path/to/agent`
- **部署**：使用 `vertexai.agent_engines.create()`。

  ```python
  from vertexai.preview import reasoning_engines # 或在較新版本中直接使用 agent_engines

  # 為部署包裝您的 root_agent
  app_for_engine = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)

  # 部署
  remote_app = agent_engines.create(
      agent_engine=app_for_engine,
      requirements=["google-cloud-aiplatform[adk,agent_engines]"],
      display_name="My Production Agent"
  )
  print(remote_app.resource_name) # projects/PROJECT_NUM/locations/REGION/reasoningEngines/ID
  ```

- **互動**：使用 `remote_app.stream_query()`, `create_session()` 等。

### 12.3 Cloud Run

用於自訂網頁應用程式的無伺服器容器平台。

- **ADK CLI**：`adk deploy cloud_run --project <id> --region <loc> ... /path/to/agent`
- **部署**：
  1.  為您的 FastAPI 應用程式創建一個 `Dockerfile` (使用 `google.adk.cli.fast_api.get_fast_api_app`)。
  2.  使用 `gcloud run deploy --source .`。
  3.  或者，`adk deploy cloud_run` (更簡單、更直覺)。
- **`main.py` 範例**：

  ```python
  import os
  from fastapi import FastAPI
  from google.adk.cli.fast_api import get_fast_api_app

  # 確保您的 agent_folder (例如 'my_first_agent') 與 main.py 在同一目錄中
  app: FastAPI = get_fast_api_app(
      agents_dir=os.path.dirname(os.path.abspath(__file__)),
      session_service_uri="sqlite:///./sessions.db", # 容器內 SQLite，適用於簡單情況
      # 對於生產環境：使用持久性資料庫 (Cloud SQL) 或 VertexAiSessionService
      allow_origins=["*"],
      web=True # 提供 ADK UI
  )
  # uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) # 如果直接執行
  ```

### 12.4 Google Kubernetes Engine (GKE)

為了最大程度的控制，在 Kubernetes 叢集中執行您的容器化代理。

- **ADK CLI**：`adk deploy gke --project <id> --cluster_name <name> ... /path/to/agent`
- **部署**：
  1.  建構 Docker 映像 (`gcloud builds submit`)。
  2.  創建 Kubernetes Deployment 和 Service YAML。
  3.  使用 `kubectl apply -f deployment.yaml` 應用。
  4.  為 GCP 權限設定 Workload Identity。

### 12.5 CI/CD 整合

- 在 CI 中自動化測試 (`pytest`, `adk eval`)。
- 自動化容器建構和部署 (例如 Cloud Build, GitHub Actions)。
- 使用環境變數管理密鑰。

---

## 13. 評估與安全性

對於穩健、生產就緒的代理至關重要。

### 13.1 代理評估 (`adk eval`)

使用預定義的測試案例系統地評估代理效能。

- **Evalset 檔案 (`.evalset.json`)**：包含 `eval_cases`，每個案例都有一個 `conversation` (使用者查詢、預期的工具呼叫、預期的中間/最終回應) 和 `session_input` (初始狀態)。
  ```json
  {
    "eval_set_id": "weather_bot_eval",
    "eval_cases": [
      {
        "eval_id": "london_weather_query",
        "conversation": [
          {
            "user_content": { "parts": [{ "text": "倫敦天氣如何？" }] },
            "final_response": { "parts": [{ "text": "倫敦的天氣是多雲..." }] },
            "intermediate_data": {
              "tool_uses": [
                { "name": "get_weather", "args": { "city": "London" } }
              ]
            }
          }
        ],
        "session_input": {
          "app_name": "weather_app",
          "user_id": "test_user",
          "state": {}
        }
      }
    ]
  }
  ```
- **執行評估**：
  - `adk web`：用於創建/執行評估案例的互動式 UI。
  - `adk eval /path/to/agent_folder /path/to/evalset.json`：CLI 執行。
  - `pytest`：將 `AgentEvaluator.evaluate()` 整合到單元/整合測試中。
- **指標**：`tool_trajectory_avg_score` (工具呼叫與預期相符)，`response_match_score` (使用 ROUGE 的最終回應相似度)。可透過 `test_config.json` 設定。

### 13.2 安全性與防護機制

多層次防禦有害內容、未對齊和不安全的操作。

1.  **身份與授權**：
    - **代理驗證**：工具以代理的服務帳號身份行事 (例如 `Vertex AI User` 角色)。簡單，但所有使用者共享存取級別。需要日誌進行歸因。
    - **使用者驗證**：工具以終端使用者的身份行事 (透過 OAuth 權杖)。降低濫用風險。
2.  **工具內防護機制**：防禦性地設計工具。工具可以從 `tool_context.state` 讀取策略 (由開發人員確定性地設定) 並在執行前驗證模型提供的參數。
    ```python
    def execute_sql(query: str, tool_context: ToolContext) -> dict:
        policy = tool_context.state.get("user:sql_policy", {})
        if not policy.get("allow_writes", False) and ("INSERT" in query.upper() or "DELETE" in query.upper()):
            return {"status": "error", "message": "策略：不允許寫入操作。"}
        # ... 執行查詢 ...
    ```
3.  **內建 Gemini 安全功能**：
    - **內容安全過濾器**：自動阻止有害內容 (CSAM, PII, 仇恨言論等)。可設定閾值。
    - **系統指令**：指導模型行為，定義禁止的主題、品牌語氣、免責聲明。
4.  **模型與工具回呼 (LLM 作為防護機制)**：使用回呼來檢查輸入/輸出。
    - `before_model_callback`：在 `LlmRequest` 到達 LLM 之前攔截它。阻止 (返回 `LlmResponse`) 或修改。
    - `before_tool_callback`：在執行前攔截工具呼叫 (名稱、參數)。阻止 (返回 `dict`) 或修改。
    - **基於 LLM 的安全性**：在回呼中使用一個便宜/快速的 LLM (例如 Gemini Flash) 來分類輸入/輸出的安全性。
      ```python
      def safety_checker_callback(context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
          # 使用一個獨立的小型 LLM 來分類安全性
          safety_llm_agent = Agent(name="SafetyChecker", model="gemini-2.5-flash-001", instruction="將輸入分類為 'safe' 或 'unsafe'。僅輸出該詞。")
          # 執行安全代理 (可能需要一個新的 runner 實例或直接模型呼叫)
          # 為簡單起見，一個模擬：
          user_input = llm_request.contents[-1].parts[0].text
          if "dangerous_phrase" in user_input.lower():
              context.state["safety_violation"] = True
              return LlmResponse(content=genai_types.Content(parts=[genai_types.Part(text="由於安全考量，我無法處理此請求。")]))
          return None
      ```
5.  **沙箱化程式碼執行**：
    - `BuiltInCodeExecutor`：使用安全、沙箱化的執行環境。
    - Vertex AI Code Interpreter 擴充功能。
    - 如果自訂，確保封閉環境 (無網路、隔離)。
6.  **網路控制與 VPC-SC**：將代理活動限制在安全邊界內 (VPC Service Controls) 以防止資料外洩。
7.  **UI 中的輸出轉義**：始終在網頁 UI 中正確轉義 LLM 生成的內容，以防止 XSS 攻擊和間接提示注入。

**Grounding**：一個關鍵的安全性和可靠性功能，將代理的回應與可驗證的資訊連結起來。

- **機制**：使用 `google_search` 或 `VertexAiSearchTool` 等工具來獲取即時或私有資料。
- **好處**：透過將回應基於檢索到的事實來減少模型幻覺。
- **要求**：使用 `google_search` 時，您的應用程式 UI **必須**顯示提供的搜尋建議和引用，以符合服務條款。

---

## 14. 除錯、日誌與可觀測性

- **`adk web` UI**：最佳的第一步。提供視覺化追蹤、會話歷史和狀態檢查。
- **事件串流日誌**：迭代 `runner.run_async()` 事件並列印相關欄位。
  ```python
  async for event in runner.run_async(...):
      print(f"[{event.author}] Event ID: {event.id}, Invocation: {event.invocation_id}")
      if event.content and event.content.parts:
          if event.content.parts[0].text:
              print(f"  Text: {event.content.parts[0].text[:100]}...")
          if event.get_function_calls():
              print(f"  Tool Call: {event.get_function_calls()[0].name} with {event.get_function_calls()[0].args}")
          if event.get_function_responses():
              print(f"  Tool Response: {event.get_function_responses()[0].response}")
      if event.actions:
          if event.actions.state_delta:
              print(f"  State Delta: {event.actions.state_delta}")
          if event.actions.transfer_to_agent:
              print(f"  TRANSFER TO: {event.actions.transfer_to_agent}")
      if event.error_message:
          print(f"  ERROR: {event.error_message}")
  ```
- **工具/回呼 `print` 陳述式**：在您的函式中直接進行簡單的日誌記錄。
- **日誌記錄**：使用 Python 的標準 `logging` 模組。使用 `adk web --log_level DEBUG` 或 `adk web -v` 控制詳細程度。
- **一行式可觀測性整合**：ADK 為流行的追蹤平台提供原生掛鉤。
  - **AgentOps**：
    ```python
    import agentops
    agentops.init(api_key="...") # 自動檢測 ADK 代理
    ```
  - **Arize Phoenix**：
    ```python
    from phoenix.otel import register
    register(project_name="my_agent", auto_instrument=True)
    ```
  - **Google Cloud Trace**：在部署期間透過旗標啟用：`adk deploy [cloud_run|agent_engine] --trace_to_cloud ...`
- **會話歷史 (`session.events`)**：持久化以進行詳細的事後分析。

---

## 15. 串流與進階 I/O

ADK 支援即時、雙向通訊，以實現如即時語音對話等互動體驗。

#### 雙向串流迴圈 (`run_live`)

對於即時語音/影像，請使用 `run_live` 搭配 `LiveRequestQueue`。這能實現低延遲、雙向通訊，使用者可以打斷代理。

```python
import asyncio
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig

async def start_streaming_session(runner, session, user_id):
    # 1. 設定模態 (例如，語音代理的 AUDIO 輸出)
    run_config = RunConfig(response_modalities=["AUDIO"])

    # 2. 為客戶端資料 (音訊區塊、文字) 創建輸入佇列
    live_queue = LiveRequestQueue()

    # 3. 啟動雙向串流
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_queue,
        run_config=run_config
    )

    # 4. 處理事件 (簡化迴圈)
    try:
        async for event in live_events:
            # 處理代理輸出 (文字或音訊位元組)
            if event.content and event.content.parts:
                part = event.content.parts[0]
                if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                    # 將音訊位元組傳送給客戶端
                    await client.send_audio(part.inline_data.data)
                elif part.text:
                     # 將文字傳送給客戶端
                     await client.send_text(part.text)

            # 處理輪次信號
            if event.turn_complete:
                 pass # 向客戶端發出代理已講完話的信號
    finally:
        live_queue.close()

# 在串流期間將使用者輸入傳送給代理：
# await live_queue.send_content(Content(role="user", parts=[Part(text="Hello")]))
# await live_queue.send_realtime(Blob(mime_type="audio/pcm", data=audio_bytes))
```

- **串流工具**：一種特殊類型的 `FunctionTool`，可以將中間結果串流回代理。

  - **定義**：必須是一個 `async` 函式，返回類型為 `AsyncGenerator`。

    ```python
    from typing import AsyncGenerator

    async def monitor_stock_price(symbol: str) -> AsyncGenerator[str, None]:
        """當股價更新時產生更新。"""
        while True:
            price = await get_live_price(symbol)
            yield f"{symbol} 的更新：${price}"
            await asyncio.sleep(5)
    ```

- **進階 I/O 模態**：ADK (特別是與 Gemini Live API 模型一起使用時) 支援更豐富的互動。
  - **音訊**：透過 `Blob(mime_type="audio/pcm", data=bytes)` 輸入，透過 `RunConfig` 中的 `genai_types.SpeechConfig` 輸出。
  - **視覺 (圖片/影片)**：透過 `Blob(mime_type="image/jpeg", data=bytes)` 或 `Blob(mime_type="video/mp4", data=bytes)` 輸入。像 `gemini-2.5-flash-exp` 這樣的模型可以處理這些。
  - **`Content` 中的多模態輸入**：
    ```python
    multimodal_content = genai_types.Content(
        parts=[
            genai_types.Part(text="描述這張圖片："),
            genai_types.Part(inline_data=genai_types.Blob(mime_type="image/jpeg", data=image_bytes))
        ]
    )
    ```

---

## 16. 效能最佳化

- **模型選擇**：選擇滿足需求的最小模型 (例如，簡單任務使用 `gemini-2.5-flash`)。
- **指令提示工程**：簡潔、清晰的指令可以減少權杖並提高準確性。
- **工具使用最佳化**：
  - 設計高效的工具 (快速的 API 呼叫、最佳化資料庫查詢)。
  - 快取工具結果 (例如，使用 `before_tool_callback` 或 `tool_context.state`)。
- **狀態管理**：僅在狀態中儲存必要的資料，以避免過大的上下文視窗。
- **`include_contents='none'`**：對於無狀態的工具代理，可以節省 LLM 上下文視窗。
- **並行化**：對獨立任務使用 `ParallelAgent`。
- **串流**：使用 `StreamingMode.SSE` 或 `BIDI` 來降低感知延遲。
- **`max_llm_calls`**：限制 LLM 呼叫以防止失控的代理並控制成本。

---

## 17. 一般最佳實踐與常見陷阱

- **從簡單開始**：從 `LlmAgent`、模擬工具和 `InMemorySessionService` 開始。逐步增加複雜性。
- **迭代開發**：建構小功能、測試、除錯、改進。
- **模組化設計**：使用代理和工具來封裝邏輯。
- **清晰命名**：為代理、工具、狀態鍵使用描述性名稱。
- **錯誤處理**：在工具和回呼中實作穩健的 `try...except` 區塊。指導 LLM 如何處理工具錯誤。
- **測試**：為工具/回呼編寫單元測試，為代理流程編寫整合測試 (`pytest`, `adk eval`)。
- **依賴管理**：使用虛擬環境 (`venv`) 和 `requirements.txt`。
- **密鑰管理**：絕不硬式編碼 API 金鑰。本地開發使用 `.env`，生產環境使用環境變數或密鑰管理器 (Google Cloud Secret Manager)。
- **避免無限迴圈**：尤其是在 `LoopAgent` 或複雜的 LLM 工具呼叫鏈中。使用 `max_iterations`、`max_llm_calls` 和強有力的指令。
- **處理 `None` & `Optional`**：在存取巢狀屬性時，始終檢查 `None` 或 `Optional` 值 (例如 `event.content and event.content.parts and event.content.parts[0].text`)。
- **事件的不可變性**：事件是不可變的記錄。如果您需要在處理*之前*更改某些內容，請在 `before_*` 回呼中進行，並返回一個*新的*修改後物件。
- **理解 `output_key` vs. 直接 `state` 寫入**：`output_key` 用於代理的*最終對話*輸出。直接 `tool_context.state['key'] = value` 用於您想儲存的*任何其他*資料。
- **範例代理**：在 [ADK 範例儲存庫](https://github.com/google/adk-samples) 中尋找實用範例和參考實作。

### 測試代理的輸出

以下腳本示範如何以程式化方式測試代理的輸出。當 LLM 或編碼代理需要與開發中的代理互動時，以及用於自動化測試、除錯或需要將代理執行整合到其他工作流程中時，這種方法非常有用：

```python
import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from app.agent import root_agent
from google.genai import types as genai_types


async def main():
    """使用範例查詢執行代理。"""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="test_user", session_id="test_session"
    )
    runner = Runner(
        agent=root_agent, app_name="app", session_service=session_service
    )
    query = "我想要一個鬆餅的食譜"
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 18. 官方 API 與 CLI 參考

有關所有類別、方法和指令的詳細規格，請參閱官方參考文件。

- [Python API 參考](https://github.com/google/adk-docs/tree/main/docs/api-reference/python)
- [Java API 參考](https://github.com/google/adk-docs/tree/main/docs/api-reference/java)
- [CLI 參考](https://github.com/google/adk-docs/tree/main/docs/api-reference/cli)
- [REST API 參考](https://github.com/google/adk-docs/tree/main/docs/api-reference/rest)
- [代理設定 YAML 參考](https://github.com/google/adk-docs/tree/main/docs/api-reference/agentconfig)

---

## **llm.txt** 文件記錄了 "Agent Starter Pack" 儲存庫，提供了關於其目的、功能和用法的真實來源。

### 第 1 節：專案概覽

- **專案名稱：** Agent Starter Pack
- **目的：** 加速在 Google Cloud 上開發可投入生產的 GenAI 代理。
- **標語：** 在 Google Cloud 上更快地建構可投入生產的代理。

**「生產差距」：**
雖然 GenAI 代理的原型製作很快，但生產部署通常需要 3-9 個月。

**解決的關鍵挑戰：**

- **客製化：** 業務邏輯、資料 grounding、安全性/合規性。
- **評估：** 指標、品質評估、測試資料集。
- **部署：** 雲端基礎設施、CI/CD、UI 整合。
- **可觀測性：** 效能追蹤、使用者回饋。

**解決方案：Agent Starter Pack**
提供 MLOps 和基礎設施範本，讓開發人員專注於代理邏輯。

- **您建構：** 提示、LLM 互動、業務邏輯、代理編排。
- **我們提供：**
  - 部署基礎設施、CI/CD、測試
  - 日誌、監控
  - 評估工具
  - 資料連接、UI 遊樂場
  - 安全性最佳實踐

從第一天起就建立生產模式，節省設定時間。

---

### 第 2 節：創建與增強代理專案

從預定義的範本創建一個新的代理專案，或用代理功能增強現有專案。這兩個過程都支援互動式和全自動設定。

**先決條件：**
在開始之前，請確保您已安裝並驗證了 `uv`/`uvx`、`gcloud` CLI、`terraform`、`git` 和 `gh` CLI (用於自動化 CI/CD 設定)。

**安裝 `agent-starter-pack` CLI：**
選擇一種方法來獲取 `agent-starter-pack` 指令：

1.  **`uvx` (推薦用於零安裝/自動化)：** 無需事先安裝即可直接執行。
    ```bash
    uvx agent-starter-pack create ...
    ```
2.  **虛擬環境 (`pip` 或 `uv`)：**
    ```bash
    pip install agent-starter-pack
    ```
3.  **持久性 CLI 安裝 (`pipx` 或 `uv tool`)：** 在隔離的環境中全域安裝。

---

### `agent-starter-pack create` 指令

根據選擇的範本和組態生成一個新的代理專案目錄。

**用法：**

```bash
agent-starter-pack create PROJECT_NAME [OPTIONS]
```

**參數：**

- `PROJECT_NAME`：您的新專案目錄名稱，也是 GCP 資源命名的基礎 (最多 26 個字元，轉換為小寫)。

**範本選擇：**

- `-a, --agent`：代理範本 - 內建代理 (例如 `adk_base`, `agentic_rag`)、遠端範本 (`adk@gemini-fullstack`, `github.com/user/repo@branch`) 或本地專案 (`local@./path`)。

**部署選項：**

- `-d, --deployment-target`：目標環境 (`cloud_run` 或 `agent_engine`)。
- `--cicd-runner`：CI/CD 執行器 (`google_cloud_build` 或 `github_actions`)。
- `--region`：GCP 區域 (預設：`us-central1`)。

**資料與儲存：**

- `-i, --include-data-ingestion`：包含資料擷取管線。
- `-ds, --datastore`：資料儲存類型 (`vertex_ai_search`, `vertex_ai_vector_search`, `cloud_sql`)。
- `--session-type`：會話儲存 (`in_memory`, `cloud_sql`, `agent_engine`)。

**專案創建：**

- `-o, --output-dir`：輸出目錄 (預設：目前目錄)。
- `--agent-directory, -dir`：代理程式碼目錄名稱 (預設：`app`)。
- `--in-folder`：在目前目錄中創建檔案，而不是新的子目錄。

**自動化：**

- `--auto-approve`：**跳過所有互動式提示 (對自動化至關重要)。**
- `--skip-checks`：跳過 GCP/Vertex AI 驗證檢查。
- `--debug`：啟用除錯日誌。

**自動化創建範例：**

```bash
uvx agent-starter-pack create my-automated-agent \
  -a adk_base \
  -d cloud_run \
  --region us-central1 \
  --auto-approve
```

---

### `agent-starter-pack enhance` 指令

透過就地添加 agent-starter-pack 功能來增強您現有的專案，賦予其 AI 代理能力。此指令支援與 `create` 相同的所有選項，但直接在目前目錄中套用範本，而不是創建新的專案目錄。

**用法：**

```bash
agent-starter-pack enhance [TEMPLATE_PATH] [OPTIONS]
```

**與 `create` 的主要區別：**

- 在目前目錄中套用範本 (相當於 `create --in-folder`)
- `TEMPLATE_PATH` 預設為目前目錄 (`.`)
- 專案名稱預設為目前目錄名稱
- 額外的 `--base-template` 選項以覆寫範本繼承

**增強專案範例：**

```bash
# 用代理功能增強目前目錄
uvx agent-starter-pack enhance . \
  --base-template adk_base \
  -d cloud_run \
  --region us-central1 \
  --auto-approve
```

**專案結構：** 預期代理程式碼在 `app/` 目錄中 (可透過 `--agent-directory` 設定)。

---

### 可用代理範本

用於 `create` 指令的範本 (透過 `-a` 或 `--agent`)：

| 代理名稱               | 描述                          |
| :--------------------- | :---------------------------- |
| `adk_base`             | 基礎 ReAct 代理 (ADK)         |
| `adk_gemini_fullstack` | 可投入生產的全端研究代理      |
| `agentic_rag`          | 用於文件檢索與問答的 RAG 代理 |
| `langgraph_base`       | 基礎 ReAct 代理 (LangGraph)   |
| `adk_live`             | 即時多模態 RAG 代理           |

---

### 包含資料擷取管線 (用於 RAG 代理)

對於需要自訂文件搜尋的 RAG 代理，啟用此選項可自動化載入、分塊、使用 Vertex AI 嵌入文件，並將其儲存在向量資料庫中。

**如何啟用：**

```bash
uvx agent-starter-pack create my-rag-agent \
  -a agentic_rag \
  -d cloud_run \
  -i \
  -ds vertex_ai_search \
  --auto-approve
```

**創建後：** 遵循新專案的 `data_ingestion/README.md` 來部署必要的基礎設施。

---

### 第 3 節：開發與自動化部署工作流程

---

本節描述代理的端到端生命週期，重點在於自動化。

### 1. 本地開發與迭代

專案創建後，進入其目錄開始開發。

**首先，安裝依賴項 (執行一次)：**

```bash
make install
```

**接下來，測試您的代理。推薦的方法是使用程式化腳本。**

#### 程式化測試 (推薦工作流程)

此方法允許快速、自動地驗證您的代理邏輯。

1.  **創建一個腳本：** 在專案的根目錄中，創建一個名為 `run_agent.py` 的 Python 腳本。
2.  **叫用代理：** 在腳本中，編寫程式碼以程式化方式呼叫您的代理，並使用範例輸入，然後 `print()` 輸出以供檢查。
    - **指南：** 如果您不確定或沒有指南，可以查看 `tests/` 目錄中的檔案，以獲取如何匯入和呼叫代理主函式的範例。
    - **重要：** 此腳本用於簡單驗證。**不需要斷言**，您不應創建正式的 `pytest` 檔案。
3.  **執行測試：** 從終端機使用 `uv` 執行您的腳本。
    `bash
    uv run python run_agent.py
    `
    您可以保留此測試檔案以供將來測試。

#### 使用 UI 遊樂場手動測試 (選用)

如果使用者需要手動在聊天介面中與您的代理互動以進行除錯：

1.  執行以下指令以啟動本地網頁 UI：
    ```bash
    make playground
    ```
    這對於人在迴路的測試很有用，並具有熱重載功能。

### 2. 部署到雲端開發環境

在設定完整的 CI/CD 之前，您可以部署到個人的雲端開發環境。

1.  **設定專案：** `gcloud config set project YOUR_DEV_PROJECT_ID`
2.  **配置資源：** `make setup-dev-env` (使用 Terraform)。
3.  **部署後端：** `make deploy` (建構並部署代理)。

### 3. 使用 CI/CD 進行自動化生產就緒部署

為了可靠的部署，`setup-cicd` 指令簡化了整個過程。它會創建一個 GitHub 儲存庫，將其連接到您選擇的 CI/CD 執行器 (Google Cloud Build 或 GitHub Actions)，配置預備/生產基礎設施，並設定部署觸發器。

**自動化 CI/CD 設定範例 (推薦)：**

```bash
# 從專案根目錄執行。此指令將引導您或可使用旗標自動化。
uvx agent-starter-pack setup-cicd
```

**CI/CD 工作流程邏輯：**

- **發起 Pull Request 時：** CI 管線執行測試。
- **合併到 `main` 分支時：** CD 管線部署到預備環境。
- **手動批准：** 手動批准步驟觸發到生產環境的部署。

---

### 第 4 節：主要功能與客製化

---

### 部署使用者介面 (UI)

- **統一化部署 (用於開發/測試)：** 後端和前端可以打包並從單一的 Cloud Run 服務提供，並使用 Identity-Aware Proxy (IAP) 進行保護。
- **部署 UI：** `make deploy IAP=true`
- **存取控制：** 使用 IAP 部署後，在 IAM 中授予使用者 `IAP-secured Web App User` 角色以給予他們存取權限。

### 會話管理

對於有狀態的代理，入門套件支援持久性會話。

- **Cloud Run：** 使用 `--session-type` 旗標在 `in_memory` (用於測試) 和持久的 `cloud_sql` 會話之間選擇。
- **代理引擎：** 自動提供會話管理。

### 監控與可觀測性

- **技術：** 使用 OpenTelemetry 將事件發送到 Google Cloud Trace 和 Logging。
- **自訂追蹤器：** `app/utils/tracing.py` (或 app 以外的其他代理目錄) 中的自訂追蹤器透過連結到 GCS 來處理大型負載，克服了預設服務限制。
- **基礎設施：** Terraform 會配置一個 Log Router 將資料匯出到 BigQuery。

---

### 第 5 節：CI/CD 設定的 CLI 參考

---

### `agent-starter-pack setup-cicd`

自動化基於 GitHub 部署的完整 CI/CD 基礎設施設定。智慧地偵測您的 CI/CD 執行器 (Google Cloud Build 或 GitHub Actions) 並自動設定所有內容。

**用法：**

```bash
uvx agent-starter-pack setup-cicd [OPTIONS]
```

**先決條件：**

- 從專案根目錄 (帶有 `pyproject.toml` 的目錄) 執行
- 必要工具：`gh` CLI (已驗證)、`gcloud` CLI (已驗證)、`terraform`
- GCP 專案的 `Owner` 角色
- 具有 `repo` 和 `workflow` 範圍的 GitHub 權杖

**主要選項：**

- `--staging-project`, `--prod-project`：GCP 專案 ID (如果省略將會提示)。
- `--repository-name`, `--repository-owner`：GitHub 儲存庫詳細資訊 (如果省略將會提示)。
- `--cicd-project`：CI/CD 資源專案 (預設為生產專案)。
- `--dev-project`：開發專案 ID (選用)。
- `--region`：GCP 區域 (預設：`us-central1`)。
- `--auto-approve`：跳過所有互動式提示。
- `--local-state`：使用本地 Terraform 狀態而不是 GCS 後端。
- `--debug`：啟用除錯日誌。

**它會做什麼：**

1. 創建/連接 GitHub 儲存庫
2. 使用遠端狀態設定 Terraform 基礎設施
3. 設定 CI/CD 執行器連接 (Cloud Build 或帶有 WIF 的 GitHub Actions)
4. 配置預備/生產環境
5. 設定帶有 origin 遠端的本地 Git 儲存庫

**自動化範例：**

```bash
uvx agent-starter-pack setup-cicd \
  --staging-project your-staging-project \
  --prod-project your-prod-project \
  --repository-name your-repo-name \
  --repository-owner your-username \
  --auto-approve
```

**設定後，推送以觸發管線：**

```bash
git add . && git commit -m "Initial commit" && git push -u origin main
```

- 注意：對於編碼代理 - 在使用 `--auto-approve` 執行前，請向使用者詢問必要的專案 ID 和儲存庫詳細資訊。
- 注意：如果使用者偏好不同的 git 提供者，請參考 `deployment/README.md` 進行手動部署。

---

### 第 6 節：編碼代理的操作指南

這些指南對於有效地與 Agent Starter Pack 專案互動至關重要。

---

### 原則 1：程式碼保存與隔離

當使用 `replace` 或 `write_file` 等工具執行程式碼修改時，您的首要目標是精準操作。您**必須僅更改使用者請求直接針對的程式碼片段**，同時**嚴格保留所有周圍和無關的程式碼。**

**強制性執行前驗證：**

在為 `replace` 操作最終確定任何 `new_string` 之前，請仔細驗證以下內容：

1.  **目標識別：** *僅*根據使用者的明確指示，清楚定義要更改的確切行或表達式。
2.  **保存檢查：** 將您提議的 `new_string` 與 `old_string` 進行比較。確保所有在已識別目標*之外*的程式碼、組態值 (例如 `model`, `version`, `api_key`)、註解和格式保持相同且一字不差。

**範例：遵守保存原則**

- **使用者請求：** 「將代理的指令更改為食譜建議者。」
- **原始程式碼片段：**
  ```python
  root_agent = Agent(
      name="root_agent",
      model="gemini-3-flash-preview",
      instruction="你是一個樂於助人的 AI 助理。"
  )
  ```
- **不正確的修改 (違規)：**
  ```python
  root_agent = Agent(
      name="recipe_suggester",
      model="gemini-1.5-flash", # 意外的變動 - 未要求更改模型
      instruction="你是一個食譜建議者。"
  )
  ```
- **正確的修改 (合規)：**
  ```python
  root_agent = Agent(
      name="recipe_suggester", # 可以，與新目的相關
      model="gemini-3-flash-preview", # 必須保留
      instruction="你是一個食譜建議者。" # 可以，是直接目標
  )
  ```

**嚴重錯誤：** 未能遵守此保存原則是嚴重錯誤。始終將現有、未更改程式碼的完整性置於重寫整個區塊的便利性之上。

---

### 原則 2：工作流程與執行最佳實踐

- **標準工作流程：**
  經過驗證的端到端流程是：`create` → `test` → `setup-cicd` → 推送以部署。請將此高層次工作流程視為開發和交付代理的預設流程。

- **代理測試：**

  - **除非特別指示，否則避免使用 `make playground`**；它專為人類互動而設計。專注於程式化測試。

- **模型選擇：**

  - **使用 Gemini 時，優先選擇現代模型系列**以獲得最佳效能和能力：「gemini-2.5-pro」、「gemini-2.5-flash」和「gemini-3-flash-preview」

- **執行 Python 指令：**

  - 在此儲存庫中始終使用 `uv` 來執行 Python 指令 (例如 `uv run run_agent.py`)。
  - 在執行腳本之前，請執行 `make install` 以確保已安裝專案依賴項。
  - 查閱專案的 `Makefile` 和 `README.md` 以獲取其他有用的開發指令。

- **進一步閱讀與疑難排解：**
  - 對於有關特定框架 (例如 LangGraph) 或 Google Cloud 產品 (例如 Cloud Run) 的問題，其官方文件和線上資源是最佳的真實來源。
  - **當遇到持續性錯誤或在初步疑難排解後不確定如何進行時，強烈建議進行有針對性的 Google 搜尋。** 這通常是找到相關文件、社群討論或直接解決方案的最快方法。
