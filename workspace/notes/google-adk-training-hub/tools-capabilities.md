# Tools & Capabilities

# 完整內容大綱

## 第一部分: ADK 工具生態系核心概念
### 1.1 工具生態系統概覽
- **核心概念**: 將工具視為擴展 Agent 推理能力之外的「電動工具」，彌補 LLM 在特定領域知識、即時資訊、或執行特定任務上的不足。
- **關鍵技術**: 涵蓋五大類工具：函數工具 (Function Tools)、OpenAPI 工具、MCP 工具、內建工具 (Built-in) 及框架工具 (Framework Tools)。
- **程式碼範例**:
  ```
  ┌──────────────────────────────────────────────────────────────┐
  │                      工具生態系統                          │
  ├──────────────────────────────────────────────────────────────┤
  │ [TOOLS] 函數工具 (自訂技能)                       │
  │ [API] OPENAPI 工具 (API 存取)                             │
  │ [MCP] MCP 工具 (標準化協定)                      │
  │ [BUILTIN] 內建工具 (Google Cloud)                       │
  │ [FRAMEWORK] 框架工具 (第三方)                    │
  └──────────────────────────────────────────────────────────────┘
  ```

### 1.2 函數工具 (Function Tools)
- **核心概念**: 將任何 Python 函數直接轉換為 Agent 可呼叫的能力，適用於實現自訂的業務邏輯。
- **關鍵技術**: 使用 `google.adk.tools.FunctionTool` 類別進行封裝，並定義清晰的 `name`, `description`, 與 `function`。
- **程式碼範例**:
  ```python
  from google.adk.tools import FunctionTool

  def search_database(query: str, limit: int = 10) -> dict:
      """在公司資料庫中搜尋相關資訊。"""
      # ... 實作邏輯 ...
      pass

  search_tool = FunctionTool(
      name="search_database",
      description="在公司資料庫中搜尋資訊",
      function=search_database
  )
  ```

### 1.3 OpenAPI 工具
- **核心概念**: 透過提供 OpenAPI 規格 (Swagger)，自動將 RESTful API 的所有端點轉換為 Agent 可用的工具集。
- **關鍵技術**: 使用 `google.adk.tools.OpenAPIToolset`，並傳入 `spec_url` 或 `spec_dict`。支援 API Key 和 OAuth2 驗證。
- **程式碼範例**:
  ```python
  from google.adk.tools import OpenAPIToolset

  api_tools = OpenAPIToolset(
      spec_url="https://api.github.com/swagger.json"
  )

  agent = Agent(
      tools=api_tools.get_tools(),
      # ...
  )
  ```

### 1.4 MCP 工具 (Model Context Protocol)
- **核心概念**: 將 MCP 視為工具的 "USB"，提供一個標準化協定，讓 Agent 能與各種外部資源（如檔案系統、資料庫）進行通用、可重用的互動。
- **關鍵技術**: 使用 `MCPToolset` 搭配 `StdioConnectionParams` (本地執行) 或 `HttpConnectionParams` (遠端服務)。
- **程式碼範例**:
  ```python
  from google.adk.tools.mcp_tool import MCPToolset

  filesystem_tools = MCPToolset(
      connection_params=StdioConnectionParams(
          command='npx',
          args=['-y', '@modelcontextprotocol/server-filesystem', '/data']
      )
  )
  ```

### 1.5 內建與框架工具
- **核心概念**: 直接利用 Google 提供的強大內建能力（搜尋、地圖、程式碼執行）以及整合 LangChain、CrewAI 等成熟框架的現有工具生態。
- **關鍵技術**: 直接匯入如 `google_search`，或使用 `LangchainTool`, `CrewaiTool` 進行封裝。
- **程式碼範例**:
  ```python
  from google.adk.tools import google_search
  from google.adk.tools.third_party import LangchainTool
  from langchain_community.tools import TavilySearchResults

  # 內建工具
  agent = Agent(tools=[google_search])

  # 框架工具
  lc_tool = LangchainTool(tool=TavilySearchResults())
  agent = Agent(tools=[lc_tool])
  ```

## 第二部分: 進階工具使用與開發實踐
### 2.1 平行工具執行
- **核心概念**: ADK 執行時期能自動偵測並行化獨立的工具呼叫，透過 `asyncio.gather()` 大幅提升執行效率。
- **關鍵技術**: 當 LLM 在單次回應中產生多個無依賴關係的 `FunctionCall` 時，ADK 會自動平行處理。
- **程式碼範例**:
  ```
  # 使用者: "查詢舊金山、洛杉磯、紐約市的天氣"
  # LLM -> 產生 3 個獨立的 get_weather() 呼叫
  # ADK Runtime -> 平行執行 3 個任務
  ```

### 2.2 工具選擇與開發最佳實踐
- **核心概念**: 提供決策樹與選擇矩陣，幫助開發者根據使用場景（如自訂邏輯、API整合、檔案操作等）選擇最適合的工具類型。
- **關鍵技術**: 遵循工具設計五大原則：單一職責、結構化返回、全面錯誤處理、清晰文件、冪等性。
- **程式碼範例**:
  ```python
  # 結構化返回格式
  {
      'status': 'success' or 'error',
      'report': '人類可讀的訊息',
      'data': { ... }
  }
  ```

### 2.3 偵錯與監控
- **核心概念**: 透過日誌記錄與事件監聽，深入了解工具的呼叫過程與效能。
- **關鍵技術**: 啟用 `google.adk.tools` 的 `DEBUG` 等級日誌；迭代 `runner` 回應的 `events` 來檢查 `TOOL_CALL_START` 和 `TOOL_CALL_RESULT` 事件。
- **程式碼範例**:
  ```python
  import logging
  logging.getLogger('google.adk.tools').setLevel(logging.DEBUG)

  result = await runner.run_async(query)
  for event in result.events:
      if event.type == 'TOOL_CALL_START':
          print(f"工具：{event.tool_name}, 參數：{event.arguments}")
  ```

---

# 內容重點說明

## 核心知識點
1.  **ADK 工具的五大類型**: 掌握 `FunctionTool`（自訂邏輯）、`OpenAPIToolset`（API整合）、`MCPToolset`（標準化資源）、`Built-in`（Google原生能力）和 `Framework Tools`（第三方生態）的適用場景與核心用法。
2.  **MCP 的核心價值**: 理解 MCP 作為一個 "通用連接器" 的重要性，它解耦了 Agent 與具體工具的實現，提高了工具的可重用性與標準化程度。
3.  **自動平行執行**: 了解 ADK 如何自動將多個獨立的工具呼叫並行化，這是優化 Agent 執行效率和回應速度的關鍵。
4.  **工具設計的標準化**: 所有工具都應遵循統一的 `{status, report, data}` 返回結構，並實施健全的錯誤處理機制，這對於建構穩定可靠的 Agent 至關重要。

## 技術實作要點
- **FunctionTool 實作**: 必須包含完整的 `try...except` 錯誤處理邏輯，並在 `FunctionTool` 建構子中提供清晰的 `name` 和 `description`，以利 LLM 理解與呼叫。
- **OpenAPI 整合**: 確保你的 API 擁有良好定義的 OpenAPI v3 規格文件。對於需要驗證的 API，需在 `OpenAPIToolset` 中正確配置 `auth_config`。
- **MCP 伺服器**: 使用 MCP 工具前，需確保對應的 MCP 伺服器（如 `@modelcontextprotocol/server-filesystem`）已安裝並可被 ADK 執行環境存取。
- **偵錯**: 啟用 `google.adk.tools` 的 `DEBUG` 日誌是追蹤工具呼叫流程與排查問題最直接有效的方法。

---

# 學習資源分類

## 依主題分類
### Agent 核心能力擴展
- **入門級**:
  - `https://raphaelmansuy.github.io/adk_training/docs/tools-capabilities#%F0%9F%94%A7-function-tools-custom-logic`: 學習如何將 Python 函數變成 Agent 的工具。
  - `https://raphaelmansuy.github.io/adk_training/docs/tutorials/foundation/02-function-tools`: 透過實作教學掌握 FunctionTool。
- **中級**:
  - `https://raphaelmansuy.github.io/adk_training/docs/tools-capabilities#%F0%9F%8C%90-openapi-tools-rest-api-integration`: 學習自動將 REST API 整合為工具。
  - `https://raphaelmansuy.github.io/adk_training/docs/tutorials/foundation/03-openapi-tools`: 透過實作教學掌握 OpenAPI 工具。
- **進階**:
  - `https://raphaelmansuy.github.io/adk_training/docs/tools-capabilities#%F0%9F%94%8C-mcp-tools-model-context-protocol`: 學習使用標準化協定連接檔案系統、資料庫等資源。
  - `https://raphaelmansuy.github.io/adk_training/docs/tools-capabilities#%E2%9A%A1-parallel-tool-execution`: 了解如何利用 ADK 的能力進行平行工具執行以優化效能。

### 整合與生態系
- **入門級**:
  - `https://raphaelmansuy.github.io/adk_training/docs/tools-capabilities#%F0%9F%8F%A2-built-in-tools-google-cloud`: 了解如何使用 Google 內建的搜尋、地圖等強大工具。
- **中級**:
  - `https://raphaelmansuy.github.io/adk_training/docs/tools-capabilities#%F0%9F%94%97-framework-tools-third-party`: 學習如何整合 LangChain 和 CrewAI 的工具生態。

## 依資源類型分類
### 官方文件
- `https://raphaelmansuy.github.io/adk_training/docs/tools-capabilities` - 工具與能力 - 提供了 ADK 中所有工具類型的全面概覽、心智模型、程式碼範例和最佳實踐。

### 教學指南
- `https://raphaelmansuy.github.io/adk_training/docs/tutorials/foundation/02-function-tools` - 教學 02: 函數工具 - 指導如何建立自訂的 Python 函數工具。
- `https://raphaelmansuy.github.io/adk_training/docs/tutorials/foundation/03-openapi-tools` - 教學 03: OpenAPI 工具 - 指導如何自動連接到 REST API。
- `https://raphaelmansuy.github.io/adk_training/docs/tutorials/advanced/11-builtin-tools-grounding` - 教學 11: 內建工具與基礎 - 指導如何使用 Google 搜尋、地圖和程式碼執行。
- `https://raphaelmansuy.github.io/adk_training/docs/tutorials/advanced/16-mcp-integration` - 教學 16: MCP 整合 - 指導如何使用標準化工具協定。

### 程式碼範例
- `https://raphaelmansuy.github.io/adk_training/docs/tools-capabilities` - 工具與能力 - 文件中包含了各類工具的完整程式碼範例，涵蓋從定義、建立到在 Agent 中使用的完整流程。

---

# 相關資源推薦

## GitHub 專案
| 專案名稱                                                                      | 描述                                                             | 星數估計 | 相關度 | 專案連結                                               |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------- | -------- | ------ | ------------------------------------------------------ |
| [google/generative-ai-python](https://github.com/google/generative-ai-python) | Google 官方的生成式 AI Python SDK，是使用 Gemini 和 ADK 的基礎。 | 3.5k+    | 高     | [連結](https://github.com/google/generative-ai-python) |
| [LangChain](https://github.com/langchain-ai/langchain)                        | 用於開發由語言模型驅動的應用程式的框架，ADK 可與其工具整合。     | 78k+     | 中     | [連結](https://github.com/langchain-ai/langchain)      |
| [CrewAI](https://github.com/joaomdmoura/crewAI)                               | 用於協調角色扮演、自主 AI Agent 的框架，ADK 可與其工具整合。     | 10k+     | 中     | [連結](https://github.com/joaomdmoura/crewAI)          |

## 學習網站
| 網站名稱                                                                 | 類型 | 描述                                                      | 推薦指數 | 網站連結                                              |
| ------------------------------------------------------------------------ | ---- | --------------------------------------------------------- | -------- | ----------------------------------------------------- |
| [Google ADK Training Hub](https://raphaelmansuy.github.io/adk_training/) | 教學 | 本次分析的資源來源，提供 ADK 的完整教學與心智模型。       | ★★★★★    | [連結](https://raphaelmansuy.github.io/adk_training/) |
| [Google AI for Developers](https://ai.google.dev/)                       | 官方 | Google 官方的 AI 開發者中心，提供最新的模型、文件與教學。 | ★★★★★    | [連結](https://ai.google.dev/)                        |

## 技術文章
- **[The official guide to function calling with Gemini](https://ai.google.dev/docs/function_calling)** - Google AI Devs - 官方文件詳細解釋了 Gemini 模型如何進行函數呼叫，這是理解 ADK 工具運作的基礎。 - [文章連結](https://ai.google.dev/docs/function_calling)
