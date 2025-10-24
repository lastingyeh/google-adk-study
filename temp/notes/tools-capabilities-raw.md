# 工具與能力

## 🎯 目的
掌握 ADK 的工具生態系統，以擴展代理程式超越大型語言模型（LLM）推理的能力。

## 📚 真實來源
`google/adk-python/src/google/adk/tools/` (ADK 1.15) + 工具實現模式

---

## 🔧 工具生態系統概覽

**心智模型**：工具就像「電動工具」，能夠擴展代理程式的推理能力之外的功能：

```
┌──────────────────────────────────────────────────────────────┐
│                      工具生態系統                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ [TOOLS] 函數工具 (自訂技能)                       │
│    "Python 函數 = 代理程式能力"                   │
│    def search_database(query: str) -> dict:                  │
│        return {...}                                          │
│    用途：自訂業務邏輯                                │
│    來源：tools/function_tool.py                            │
│                                                              │
│ [API] OPENAPI 工具 (API 存取)                             │
│    "REST API 自動成為代理程式工具"              │
│    OpenAPIToolset(spec_url="https://api.com/spec.json")      │
│    用途：外部服務、第三方 API                  │
│    來源：tools/openapi_toolset.py                          │
│                                                              │
│ [MCP] MCP 工具 (標準化協定)                      │
│    "模型內容協定 = 通用工具語言"        │
│    MCPToolset(server="filesystem", path="/data")             │
│    用途：檔案系統、資料庫、標準服務             │
│    來源：tools/mcp_tool/                                   │
│                                                              │
│ [BUILTIN] 內建工具 (Google Cloud)                       │
│    "預建的 Google 功能"                           │
│    - google_search (網路基礎)                           │
│    - google_maps_grounding (地點)                        │
│    - 程式碼執行 (模型中的 Python)                        │
│    用途：搜尋、地圖、程式碼、企業資料                  │
│    來源：tools/google_*_tool.py                            │
│                                                              │
│ [FRAMEWORK] 框架工具 (第三方)                    │
│    "來自 LangChain/CrewAI 的 100 多種工具"                        │
│    LangchainTool(tool=TavilySearchResults())                 │
│    CrewaiTool(tool=SerperDevTool(), name="search")           │
│    用途：利用現有的工具生態系統                    │
│    來源：tools/third_party/                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔧 函數工具 (自訂邏輯)

### 基本函數工具模式

**心智模型**：Python 函數成為可呼叫的代理程式能力：

```python
from google.adk.tools import FunctionTool

def search_database(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    在公司資料庫中搜尋相關資訊。

    Args:
        query: 搜尋查詢字串
        limit: 要傳回的最大結果數

    Returns:
        包含搜尋結果和元資料的字典
    """
    try:
        # 在這裡編寫您的自訂邏輯
        results = database.search(query, limit=limit)

        return {
            'status': 'success',
            'report': f'找到 {len(results)} 筆關於 "{query}" 的結果',
            'data': {
                'query': query,
                'results': results,
                'total_found': len(results)
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'資料庫搜尋失敗：{str(e)}'
        }

# 建立工具
search_tool = FunctionTool(
    name="search_database",
    description="在公司資料庫中搜尋資訊",
    function=search_database
)

# 在代理程式中使用
agent = Agent(
    name="database_assistant",
    model="gemini-1.5-flash",
    tools=[search_tool],
    instruction="協助使用者搜尋和分析公司資料"
)
```

### 函數工具最佳實踐

**傳回格式標準**：

```python
# 總是傳回結構化字典
{
    'status': 'success' | 'error',
    'report': '人類可讀的訊息',
    'data': { ... }  # 可選的結構化資料
}
```

**錯誤處理**：

```python
def robust_tool(param: str) -> Dict[str, Any]:
    try:
        # 主要邏輯
        result = risky_operation(param)
        return {
            'status': 'success',
            'report': f'成功處理 {param}',
            'data': result
        }
    except ValueError as e:
        return {
            'status': 'error',
            'error': f'無效輸入：{str(e)}',
            'report': f'由於輸入無效，無法處理 {param}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': '發生未預期的錯誤'
        }
```

**工具設計原則**：
1.  **單一職責**：一個工具，一個明確的目的
2.  **結構化傳回**：總是傳回標準格式
3.  **全面的錯誤處理**：處理所有預期的錯誤情況
4.  **清晰的文件**：包含範例的詳細文件字串
5.  **冪等性**：使用相同輸入多次呼叫是安全的

---

## 🌐 OpenAPI 工具 (REST API 整合)

### 自動 API 工具生成

**心智模型**：REST API 自動成為代理程式工具：

```python
from google.adk.tools import OpenAPIToolset

# 載入 API 規格
api_tools = OpenAPIToolset(
    spec_url="https://api.github.com/swagger.json",
    # 或 spec_dict=loaded_spec_dict
)

# 工具會從 API 規格中自動建立
# - get_repos (GET /repos)
# - create_issue (POST /repos/issues)
# - search_code (GET /search/code)
# 等等。

# 在代理程式中使用
agent = Agent(
    name="github_assistant",
    model="gemini-1.5-flash",
    tools=api_tools.get_tools(),  # 取得所有產生的工具
    instruction="協助使用者處理 GitHub 儲存庫和問題"
)
```

### OpenAPI 工具功能

**自動參數對應**：

```
# API 規格：GET /repos/{owner}/{repo}/issues
# 成為工具：get_issues(owner: str, repo: str, state?: str)

# 代理程式可以自然地呼叫它：
# "顯示 google/adk 儲存庫中的開啟問題"
# → 呼叫 get_issues(owner="google", repo="adk", state="open")
```

**驗證處理**：

```python
# 使用 API 金鑰
api_tools = OpenAPIToolset(
    spec_url="https://api.service.com/spec.json",
    auth_config={
        'type': 'bearer',
        'token': os.getenv('API_TOKEN')
    }
)

# 使用 OAuth2
api_tools = OpenAPIToolset(
    spec_url="https://api.service.com/spec.json",
    auth_config={
        'type': 'oauth2',
        'client_id': '...',
        'client_secret': '...',
        'token_url': 'https://api.service.com/oauth/token'
    }
)
```

### 常見 OpenAPI 模式

**CRUD 操作**：

```python
# 資料庫 API
db_tools = OpenAPIToolset(spec_url="https://db-api.company.com/spec.json")
# 建立：create_record, read_record, update_record, delete_record

# 檔案儲存 API
storage_tools = OpenAPIToolset(spec_url="https://storage.company.com/spec.json")
# 建立：upload_file, download_file, list_files, delete_file

# 通訊 API
comm_tools = OpenAPIToolset(spec_url="https://slack.company.com/spec.json")
# 建立：send_message, create_channel, invite_user
```

---

## 🔌 MCP 工具 (模型內容協定)

### MCP 架構

**心智模型**：MCP 就像工具的「USB」（通用連接器）：

```
MCP 之前 (自訂整合)
   代理程式 ──自訂──► 檔案系統
   代理程式 ──自訂──► 資料庫
   代理程式 ──自訂──► API 服務
        (每個整合都不同)

MCP 之後 (標準化協定)
   代理程式 ───MCP────► MCP 伺服器 (檔案系統)
   代理程式 ───MCP────► MCP 伺服器 (資料庫)
   代理程式 ───MCP────► MCP 伺服器 (API 服務)
        (一個協定，多個伺服器)
```

### MCP 工具用法

**Stdio 連線 (本機)**：

```python
from google.adk.tools.mcp_tool import MCPToolset

# 檔案系統存取
filesystem_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-filesystem', '/data']
    )
)

# 資料庫存取
db_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-sqlite', '--db-path', '/data/app.db']
    )
)

# 在代理程式中使用
agent = Agent(
    name="data_analyst",
    model="gemini-1.5-flash",
    tools=filesystem_tools.get_tools() + db_tools.get_tools(),
    instruction="從檔案和資料庫分析資料"
)
```

**HTTP 連線 (遠端)**：

```python
# 遠端 MCP 伺服器
remote_tools = MCPToolset(
    connection_params=HttpConnectionParams(
        url='https://mcp-server.company.com'
    )
)
```

### MCP 與自訂工具比較

| 層面 | 自訂工具 | MCP 工具 |
| :--- | :--- | :--- |
| 設定 | 編寫 Python 程式碼 | 安裝 MCP 伺服器 |
| 可重用性 | 單一代理程式 | 任何代理程式 |
| 探索 | 手動 | 自動 |
| 驗證 | 自訂 | 內建 OAuth2 |
| 社群 | N/A | 100+ 伺服器 |

---

## 🏢 內建工具 (Google Cloud)

### Google 搜尋 (網路基礎)

**心智模型**：將 LLM 的想像力與真實世界的資訊連結：

```python
from google.adk.tools import google_search

# Gemini 1.5+ 自動內建
agent = Agent(
    name="researcher",
    model="gemini-1.5-flash",  # 內建搜尋
    instruction="使用網路搜尋研究主題"
)

# 明確使用工具
search_agent = Agent(
    name="web_searcher",
    model="gemini-1.5-flash",
    tools=[google_search],
    instruction="在網路上搜尋最新資訊"
)
```

**搜尋能力**：
*   即時網路結果
*   事實基礎
*   最新事件和資料
*   來源引用

### Google 地圖基礎

**心智模型**：用於空間推理的地點智慧：

```python
from google.adk.tools import google_maps_grounding

location_agent = Agent(
    name="location_assistant",
    model="gemini-1.5-flash",
    tools=[google_maps_grounding],
    instruction="協助使用者處理地點相關查詢和路線規劃"
)

# 能力：
# - 地址解析
# - 距離計算
# - 興趣點
# - 路線規劃
```

### 程式碼執行

**心智模型**：內建於模型中的 Python 直譯器：

```python
# Gemini 1.5+ 內建程式碼執行
code_agent = Agent(
    name="programmer",
    model="gemini-1.5-flash",  # 內建程式碼執行
    instruction="編寫和測試 Python 程式碼"
)

# 可以執行以下程式碼：
# "計算 10 的階乘"
# "繪製正弦波"
# "處理此 CSV 資料"
```

---

## 🔗 框架工具 (第三方)

### LangChain 整合

**心智模型**：利用 LangChain 的 50 多種工具：

```python
from google.adk.tools.third_party import LangchainTool
from langchain_community.tools import TavilySearchResults

# 包裝 LangChain 工具
search_tool = LangchainTool(
    tool=TavilySearchResults(max_results=5),
    name="web_search",
    description="使用 Tavily 搜尋網路"
)

agent = Agent(
    name="research_assistant",
    model="gemini-1.5-flash",
    tools=[search_tool],
    instruction="使用網路搜尋研究主題"
)
```

### CrewAI 整合

**心智模型**：使用 CrewAI 的專業工具：

```python
from google.adk.tools.third_party import CrewaiTool
from crewai_tools import SerperDevTool

# 包裝 CrewAI 工具
search_tool = CrewaiTool(
    tool=SerperDevTool(),
    name="google_search",
    description="使用 Serper 搜尋 Google"
)

agent = Agent(
    name="web_researcher",
    model="gemini-1.5-flash",
    tools=[search_tool],
    instruction="使用 Google 搜尋尋找資訊"
)
```

---

## ⚡ 平行工具執行

### 自動平行化

**心智模型**：多個工具透過 `asyncio.gather()` 同時執行：

```
使用者："查詢舊金山、洛杉磯、紐約市的天氣"
         │
    LLM 產生 3 個 FunctionCall
         │
    ┌────┴────┐
    │ ADK     │  asyncio.gather()
    │ 執行時期 │  ───────────────────►
    └─────────┘
         │
    ┌────┴────┬────────┬────────┐
    │         │        │        │
 任務 A    任務 B    任務 C   (平行)
    舊金山        洛杉磯        紐約市
    │         │        │
    └────┬────┴────────┘
         │
    合併結果
         │
    傳回給 LLM
```

**效能優勢**：
*   **速度**：獨立任務平行執行
*   **成本**：相同的 token 成本，更快的執行速度
*   **擴充性**：同時處理多個請求

### 平行工具模式

**扇出/扇入**：

```python
# 平行研究多個來源
parallel_research = ParallelAgent(
    sub_agents=[
        web_search_agent,
        database_search_agent,
        api_search_agent
    ]
)

# 然後合併結果
merger_agent = Agent(
    name="result_merger",
    model="gemini-1.5-flash",
    instruction="合併和摘要來自多個來源的研究結果"
)

# 完整流程
research_pipeline = SequentialAgent(
    sub_agents=[parallel_research, merger_agent]
)
```

---

## [TOOLS] 工具選擇決策樹

```
需要某項功能嗎？
    │
    ├─ Python 程式碼？
    │  └─ FunctionTool ✓
    │
    ├─ REST API？
    │  └─ OpenAPIToolset ✓
    │
    ├─ 檔案系統/資料庫？
    │  └─ MCPToolset ✓
    │
    ├─ 網路/地圖？
    │  └─ 內建工具 ✓
    │
    └─ 第三方？
        └─ 框架工具 ✓
```

### 工具選擇矩陣

| 使用案例 | FunctionTool | OpenAPIToolset | MCPToolset | 內建 | 框架 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 自訂業務邏輯 | ✅ | ❌ | ❌ | ❌ | ❌ |
| REST API 整合 | ❌ | ✅ | ❌ | ❌ | ❌ |
| 檔案系統存取 | ❌ | ❌ | ✅ | ❌ | ❌ |
| 網路搜尋 | ❌ | ❌ | ❌ | ✅ | ✅ |
| 地點服務 | ❌ | ❌ | ❌ | ✅ | ❌ |
| 程式碼執行 | ❌ | ❌ | ❌ | ✅ | ❌ |
| 現有工具重用 | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🔧 工具開發最佳實踐

### 工具設計原則
1.  **明確目的**：每個工具都做好一件事
2.  **一致的介面**：所有工具都使用標準的傳回格式
3.  **錯誤恢復能力**：優雅地處理失敗
4.  **效能意識**：考慮執行時間和資源使用
5.  **安全意識**：驗證輸入，限制存取

### 工具測試模式

```python
def test_tool():
    # 測試成功案例
    result = search_tool("測試查詢")
    assert result['status'] == 'success'
    assert 'data' in result

    # 測試錯誤案例
    result = search_tool("")  # 無效輸入
    assert result['status'] == 'error'
    assert 'error' in result

    # 測試邊界案例
    result = search_tool("不存在")
    assert result['status'] == 'success'  # 有效查詢，但沒有結果
    assert result['data']['results'] == []
```

### 工具文件

```python
def comprehensive_tool(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    跨多個資料來源的綜合搜尋。

    此工具會搜尋資料庫、API 和檔案，為使用者查詢提供
    全面的結果。

    Args:
        query: 搜尋查詢字串 (必要)
        filters: 用於縮小結果範圍的可選篩選器
            - date_range: {"start": "2024-01-01", "end": "2024-12-31"}
            - categories: ["tech", "business"]
        limit: 要傳回的最大結果數 (預設：100，最大：1000)

    Returns:
        包含以下內容的字典：
        - status: "success" 或 "error"
        - report: 人類可讀的摘要
        - data: 包含元資料的結構化結果

    Examples:
        # 基本搜尋
        tool("機器學習")

        # 篩選搜尋
        tool("AI 趨勢", filters={"categories": ["tech"]}, limit=50)

    Raises:
        無明確例外 - 所有錯誤都在結果字典中傳回
    """
```

---

## 🔍 偵錯工具

### 工具呼叫檢查

```python
# 啟用詳細的工具日誌記錄
import logging
logging.getLogger('google.adk.tools').setLevel(logging.DEBUG)

# 檢查代理程式回應中的工具呼叫
result = await runner.run_async(query)
for event in result.events:
    if event.type == 'TOOL_CALL_START':
        print(f"工具：{event.tool_name}")
        print(f"參數：{event.arguments}")
    elif event.type == 'TOOL_CALL_RESULT':
        print(f"結果：{event.result}")
```

### 工具效能監控

```python
# 追蹤工具執行時間
import time

def timed_tool(*args, **kwargs):
    start_time = time.time()
    result = original_tool(*args, **kwargs)
    duration = time.time() - start_time

    # 記錄效能
    print(f"工具執行時間：{duration:.2f}s")

    # 新增至結果
    result['execution_time'] = duration
    return result
```

---

## 📚 相關主題
*   **[代理程式架構 →](https://raphaelmansuy.github.io/adk_training/docs/agent-architecture)**：代理程式如何使用工具
*   **[工作流程與協調 →](https://raphaelmansuy.github.io/adk_training/docs/workflows-orchestration)**：協調多個工具
*   **[LLM 整合 →](https://raphaelmansuy.github.io/adk_training/docs/llm-integration)**：LLM 如何呼叫工具

### 🎓 實作教學
*   **[教學 02：函數工具](https://raphaelmansuy.github.io/adk_training/docs/tutorials/foundation/02-function-tools)**：建立自訂 Python 函數工具
*   **[教學 03：OpenAPI 工具](https://raphaelmansuy.github.io/adk_training/docs/tutorials/foundation/03-openapi-tools)**：自動連線到 REST API
*   **[教學 11：內建工具與基礎](https://raphaelmansuy.github.io/adk_training/docs/tutorials/advanced/11-builtin-tools-grounding)**：使用 Google 搜尋、地圖和程式碼執行
*   **[教學 16：MCP 整合](https://raphaelmansuy.github.io/adk_training/docs/tutorials/advanced/16-mcp-integration)**：標準化工具協定

---

## 🎯 關鍵要點
1.  **工具類型**：用於自訂邏輯的函數、用於 REST API 的 OpenAPI、用於標準的 MCP
2.  **內建功能**：Google 工具提供搜尋、地圖、程式碼執行
3.  **平行執行**：獨立工具同時執行以提高速度
4.  **標準格式**：所有工具都傳回 `{status, report, data}` 結構
5.  **錯誤處理**：工具優雅地處理錯誤，傳回結構化的錯誤資訊

**🔗 下一步**：了解**[工作流程與協調](https://raphaelmansuy.github.io/adk_training/docs/workflows-orchestration)**，以有效地協調多個工具。