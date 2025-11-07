# 教學 03：OpenAPI 工具 - REST API 整合

## 總覽

將您的代理程式連接到整個網路！學習如何從 OpenAPI 規範中自動產生工具，使您的代理程式能夠與 REST API 互動，而無需手動編寫工具函式。

**您將建立的內容**：一個 Chuck Norris 笑話助理，具備以下功能：
*   按類別搜尋 Chuck Norris 笑話
*   取得隨機笑話
*   列出可用類別
*   使用 **OpenAPIToolset** 從 API 規範自動產生工具

**為何重要**：透過 OpenAPI 規範，ADK 可以自動產生工具，無需為每個 API 端點手動編寫工具函式，從而節省時間並減少錯誤。

---

## 先決條件

*   Python 3.9+
*   已安裝 `google-adk`
*   Google API 金鑰
*   已完成教學 01-02 (基礎)
*   對 REST API 有基本了解

---

## 核心概念

### 什麼是 OpenAPI？

**OpenAPI** (前身為 Swagger) 是一種用於描述 REST API 的規範格式：

```json
{
  "openapi": "3.0.0",
  "paths": {
    "/jokes/random": {
      "get": {
        "summary": "Get random joke",
        "parameters": [...]
      }
    }
  }
}
```

### OpenAPIToolset 如何運作

```
OpenAPI 規範 → ADK 自動產生 → 代理程式可用的工具
```

**範例**：

```python
toolset = OpenAPIToolset(spec=api_spec)
# ADK 會自動建立：
# - get_jokes_random()
# - get_jokes_search()
# - get_jokes_categories()
```

**優點**：
*   ✅ 無需手動編寫工具
*   ✅ 始終與 API 規範匹配
*   ✅ 自動處理身份驗證
*   ✅ 驗證參數
*   ✅ 適用於任何符合 OpenAPI 的 API

---

## 使用案例：Chuck Norris 笑話助理

**情境**：建立一個代理程式，從公開的 Chuck Norris API 中檢索 Chuck Norris 笑話/事實。

**為何選擇此 API？**：
*   ✅ 免費，無需 API 金鑰
*   ✅ 簡單的 OpenAPI 規範
*   ✅ 非常適合學習
*   ✅ 有趣且引人入勝

**API**：[https://api.chucknorris.io/](https://api.chucknorris.io/)

**實作**：[tutorial_implementation/tutorial03](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial03/) - 包含測試的完整工作範例

---

## 實作

### 專案結構

```
chuck_norris_agent/
├── __init__.py
├── agent.py
├── .env
└── README.md
```

### 完整程式碼

**chuck_norris_agent/__init__.py**：

```python
from .agent import root_agent
__all__ = ['root_agent']
```

**chuck_norris_agent/agent.py**：

```python
"""Chuck Norris Fact Assistant - OpenAPI Tools Demonstration
This agent demonstrates how to use OpenAPIToolset to automatically
generate tools from an API specification without writing tool functions."""
from google.adk.agents import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# OPENAPI SPECIFICATION
# ============================================================================
# Chuck Norris API OpenAPI Specification
# Based on: https://api.chucknorris.io/
CHUCK_NORRIS_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Chuck Norris API",
        "description": "Free JSON API for hand curated Chuck Norris facts",
        "version": "1.0.0"
    },
    "servers": [
        {
            "url": "https://api.chucknorris.io/jokes"
        }
    ],
    "paths": {
        "/random": {
            "get": {
                "operationId": "get_random_joke",
                "summary": "Get a random Chuck Norris joke",
                "description": "Retrieve a random joke from the database. Can optionally filter by category.",
                "parameters": [
                    {
                        "name": "category",
                        "in": "query",
                        "description": "Filter jokes by category (optional)",
                        "required": False,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "icon_url": {"type": "string"},
                                        "id": {"type": "string"},
                                        "url": {"type": "string"},
                                        "value": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/search": {
            "get": {
                "operationId": "search_jokes",
                "summary": "Search for jokes",
                "description": "Free text search for jokes containing the query term.",
                "parameters": [
                    {
                        "name": "query",
                        "in": "query",
                        "description": "Search query (3+ characters required)",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "minLength": 3
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "total": {"type": "integer"},
                                        "result": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "icon_url": {"type": "string"},
                                                    "id": {"type": "string"},
                                                    "url": {"type": "string"},
                                                    "value": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/categories": {
            "get": {
                "operationId": "get_categories",
                "summary": "Get all joke categories",
                "description": "Retrieve list of available joke categories.",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# ============================================================================
# OPENAPI TOOLSET
# ============================================================================
# Create OpenAPIToolset from specification
# ADK will automatically generate 3 tools:
# - get_random_joke(category: Optional[str])
# - search_jokes(query: str)
# - get_categories()
chuck_norris_toolset = OpenAPIToolset(spec_dict=CHUCK_NORRIS_SPEC)

# ============================================================================
# AGENT DEFINITION
# ============================================================================
root_agent = Agent(
    name="chuck_norris_agent",
    model="gemini-2.0-flash",
    description="""
    Chuck Norris fact assistant that can retrieve jokes/facts from the
    Chuck Norris API using OpenAPI tools.
    """,
    instruction="""
    You are a fun Chuck Norris fact assistant!
    CAPABILITIES:
    - Get random Chuck Norris jokes (optionally filtered by category)
    - Search for jokes containing specific keywords
    - List all available joke categories
    STYLE:
    - Be enthusiastic and playful
    - Chuck Norris jokes are exaggerated for comedic effect
    - Format jokes clearly for easy reading
    - If search returns multiple results, show a few best ones
    WORKFLOW:
    - For random requests → use get_random_joke
    - For specific topics → use search_jokes with query
    - To see categories → use get_categories
    - For category-specific random → use get_random_joke with category parameter
    IMPORTANT:
    - Always extract the 'value' field from API response (that's the actual joke)
    - If search finds 0 results, suggest trying a different keyword
    - Categories are lowercase (e.g., "dev", "movie", "food")
    """,
    # Pass the toolset to the agent
    tools=[chuck_norris_toolset]
)
```

**chuck_norris_agent/.env**：

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key_here
```

---

## 執行代理程式

### 示範操作

這是在操作中的 Chuck Norris 代理程式：

![Tutorial 03 Demo - OpenAPI Tools Chuck Norris Agent](/adk_training/assets/images/tutorial03_01cap-baaaf07a09d00818a75bc45377f40465.gif)

### 方法 1：Web UI (建議)

```bash
cd /path/to/chuck_norris_agent/..
adk web chuck_norris_agent
```

**試試這些提示**：
*   "告訴我一個隨機的 Chuck Norris 笑話"
*   "找一些關於電腦的笑話"
*   "有哪些笑話類別？"
*   "給我一個隨機的電影笑話"
*   "搜尋包含 'code' 這個詞的笑話"

### 方法 2：終端機

```bash
adk run chuck_norris_agent
```

---

## 預期行為

### 範例 1：隨機笑話

**使用者**："告訴我一個隨機的 Chuck Norris 笑話"

**代理程式流程**：
1.  呼叫 `get_random_joke()` 工具 (無類別)
2.  API 回傳包含 'value' 欄位的 JSON
3.  代理程式擷取並格式化笑話

**代理程式回應**：
```
這是一個給你的 Chuck Norris 事實：
"Chuck Norris 可以除以零。"
😄 經典！
```

### 範例 2：按關鍵字搜尋

**使用者**："找一些關於程式設計的笑話"

**代理程式流程**：
1.  呼叫 `search_jokes(query="programming")` 工具
2.  API 回傳匹配笑話的陣列
3.  代理程式選擇最好的幾個並格式化

**代理程式回應**：
```
我找到一些與程式設計相關的 Chuck Norris 笑話：
1. "Chuck Norris 寫的程式碼會自我優化。"
2. "Chuck Norris 不用除錯器。臭蟲會向他坦白。"
3. "Chuck Norris 可以寫出會終止的無限遞迴。"
😎 開發者的幽默！
```

### 範例 3：列出類別

**使用者**："有哪些類別可用？"

**代理程式流程**：
1.  呼叫 `get_categories()` 工具
2.  API 回傳類別字串的陣列
3.  代理程式格式化列表

**代理程式回應**：
```
Chuck Norris 笑話有以下類別：
- animal
- career
- celebrity
- dev
- explicit
- fashion
- food
- history
- money
- movie
- music
- political
- religion
- science
- sport
- travel
試著從任何類別中要一個笑話！例如："給我一個隨機的開發笑話"
```

### 範例 4：特定類別的隨機笑話

**使用者**："告訴我一個開發類別的笑話"

**代理程式流程**：
1.  呼叫 `get_random_joke(category="dev")` 工具
2.  API 從 'dev' 類別回傳隨機笑話
3.  代理程式格式化笑話

**代理程式回應**：
```
這是一個給你的開發笑話：
"Chuck Norris 的鍵盤沒有 Ctrl 鍵，因為沒有什麼能控制 Chuck Norris。"
🤓 對開發者來說太完美了！
```

---

## 運作原理：OpenAPIToolset 深入探討

### 1. 規範結構

```json
{
  "paths": {
    "/random": {              // 端點路徑
      "get": {                // HTTP 方法
        "operationId": "...", // 成為函式名稱
        "parameters": [...]   // 成為函式參數
      }
    }
  }
}
```

### 2. 自動產生的工具

**從規範**：

```json
{
  "operationId": "search_jokes",
  "parameters": [{ "name": "query", "required": true }]
}
```

**ADK 建立**：

```python
async def search_jokes(query: str) -> Dict:
    """Search for jokes"""
    # ADK 處理 HTTP 請求
    response = requests.get(
        "https://api.chucknorris.io/jokes/search",
        params={"query": query}
    )
    return response.json()
```

### 3. 代理程式工具使用

Agent 建構函式直接接受工具集 - ADK 在內部處理非同步工具載入：

```python
root_agent = Agent(
    ...,
    tools=[chuck_norris_toolset]  # 直接傳遞工具集，而不是 get_tools()
)
```

```
使用者："找一些關於 code 的笑話"
  ↓
代理程式 (LLM)：決定呼叫 search_jokes
  ↓
search_jokes(query="code") 執行
  ↓
HTTP GET https://api.chucknorris.io/jokes/search?query=code
  ↓
API 回傳：{"total": 5, "result": [...]}
  ↓
代理程式 (LLM)：為使用者格式化回應
  ↓
使用者看到："我找到 5 個關於 code 的笑話：..."
```

### 4. ADK 自動處理的內容

*   ✅ HTTP 請求建構
*   ✅ 參數驗證 (類型、必要/可選)
*   ✅ URL 建構 (伺服器 + 路徑 + 查詢參數)
*   ✅ 回應解析 (JSON 到 dict)
*   ✅ 錯誤處理 (網路、HTTP 錯誤)
*   ✅ 身份驗證 (如果在規範中指定)

---

## 主要收穫

1.  **OpenAPIToolset = 零手動工具程式碼**：無需自己編寫 `def search_jokes()`
2.  **operationId → 函式名稱**：控制 LLM 如何看待工具
3.  **parameters → 函式參數**：成為工具函式簽章
4.  **適用於任何 OpenAPI API**：GitHub、Stripe、Twilio、自訂 API
5.  **Chuck Norris API 無需 API 金鑰**：公開且免費！

---

## 最佳實踐

### OpenAPI 規範建立

**應做**：
*   ✅ 使用描述性的 `operationId` (例如 `get_random_joke` 而不是 `endpoint1`)
*   ✅ 編寫清晰的 `description` 欄位 (LLM 讀取這些來決定工具用法)
*   ✅ 正確標記必要參數
*   ✅ 包含回應結構以改善錯誤處理

**不應做**：
*   ❌ 使用像 `api_call_1` 這樣的通用名稱
*   ❌ 省略描述 (LLM 將不知道何時使用工具)
*   ❌ 將所有參數標記為必要 (提供合理的預設值)

### 工具設計

**應做**：
*   ✅ 每個不同操作一個工具 (取得、搜尋、建立、更新)
*   ✅ 保持參數列表簡短 (理想情況下 < 5 個參數)
*   ✅ 對分類參數使用列舉
*   ✅ 在代理程式整合前獨立測試工具

**不應做**：
*   ❌ 在一個端點中結合不相關的操作
*   ❌ 使用過於複雜的巢狀參數
*   ❌ 假設 LLM 會推斷遺漏的描述

### 身份驗證

**Chuck Norris API** 不需要身份驗證，但對於需要的 API：

```python
# 標頭中的 API 金鑰
OpenAPIToolset(
    spec=spec,
    auth_config={
        "type": "api_key",
        "api_key": os.getenv("API_KEY"),
        "key_name": "X-API-Key",
        "key_location": "header"
    }
)

# Bearer token
OpenAPIToolset(
    spec=spec,
    auth_config={
        "type": "bearer",
        "token": os.getenv("AUTH_TOKEN")
    }
)

# OAuth (更複雜，請參閱 ADK 文件)
```

---

## 常見問題與疑難排解

### 問題 1：工具未被呼叫

**問題**：代理程式不使用您的 OpenAPI 工具

**解決方案**：
1.  檢查 `operationId` 是否具描述性：`get_random_joke` 而不是 `endpoint1`
2.  在規範中新增詳細的 `summary` 和 `description`
3.  直接在 Python 中測試工具以驗證其是否正常運作
4.  檢閱代理程式指令 (是否提及工具的用途？)
5.  檢查事件分頁：LLM 是否正在考慮該工具？

### 問題 2：匯入錯誤

**問題**：`ImportError: cannot import name 'OpenAPIToolset'`

**解決方案**：
1.  使用正確的匯入路徑：`from google.adk.tools.openapi_tool import OpenAPIToolset`
2.  驗證是否已安裝 `google-adk`：`pip install google-adk`
3.  檢查 ADK 版本相容性

### 問題 3：建構函式參數錯誤

**問題**：`TypeError: OpenAPIToolset.__init__() got an unexpected keyword argument 'spec'`

**解決方案**：
1.  使用 `spec_dict` 參數而不是 `spec`：`OpenAPIToolset(spec_dict=my_spec)`
2.  在您的 ADK 版本中驗證參數名稱

### 問題 4：非同步工具載入問題

**問題**：`ValidationError: Input should be a valid list [type=list_type, input_value=<coroutine object>]`

**解決方案**：
1.  直接傳遞工具集：`tools=[my_toolset]` 而不是 `tools=my_toolset.get_tools()`
2.  `get_tools()` 是非同步的並回傳一個協程 - 讓 ADK 在內部處理工具載入
3.  如果您需要直接存取工具，請等待呼叫：`tools = await my_toolset.get_tools()`

### 問題 5：無效的 API 回應

**問題**：工具回傳錯誤或非預期資料

**解決方案**：
1.  直接使用 `curl` 或 Postman 測試 API 端點
2.  驗證規範是否與實際 API 行為相符
3.  檢查是否正在傳遞必要參數
4.  尋找速率限制 (429 狀態碼)
5.  驗證 JSON 解析 (在自訂包裝函式中使用 try/except)

### 問題 6：規範驗證錯誤

**問題**：ADK 拒絕 OpenAPI 規範

**解決方案**：
1.  在 [https://editor.swagger.io/](https://editor.swagger.io/) 驗證規範
2.  檢查 OpenAPI 版本 (支援 `3.0.0` 或 `3.1.0`)
3.  驗證所有必要欄位是否存在 (`openapi`, `info`, `paths`)
4.  使用正確的 JSON 類型 (`string` 而不是 `str`, `integer` 而不是 `int`)
5.  檢查欄位名稱中是否有錯字

### 問題 7：代理程式誤解工具輸出

**問題**：代理程式未正確格式化 API 回應

**解決方案**：
1.  改進代理程式指令以指定輸出格式
2.  在指令中新增範例："從 JSON 中擷取 'value' 欄位"
3.  以結構化方式使用工具結果 (記錄 dict 鍵)
4.  考慮在自訂包裝函式中進行後處理
5.  檢查規範中的回應結構是否與實際 API 相符

---

## 真實世界應用

### 1. GitHub 整合

**使用案例**：程式碼審查助理

**OpenAPI 工具**：
*   `get_pull_request(repo, number)` - 取得 PR 詳細資訊
*   `list_comments(repo, number)` - 取得審查評論
*   `create_comment(repo, number, body)` - 新增審查評論

**範例**："總結 PR #123 中的變更並檢查安全問題"

### 2. Stripe 付款處理

**使用案例**：電子商務支援代理程式

**OpenAPI 工具**：
*   `create_payment_intent(amount, currency)` - 處理付款
*   `get_customer(id)` - 取得客戶詳細資訊
*   `create_refund(payment_id, amount)` - 發出退款

**範例**："為訂單 #456 處理 50 美元的退款"

### 3. Twilio SMS/語音

**使用案例**：通訊自動化代理程式

**OpenAPI 工具**：
*   `send_sms(to, body)` - 傳送簡訊
*   `make_call(to, from, url)` - 發起電話
*   `get_message_status(sid)` - 檢查傳送狀態

**範例**："向客戶 +1234567890 傳送確認簡訊"

### 4. Jira 專案管理

**使用案例**：開發工作流程代理程式

**OpenAPI 工具**：
*   `create_issue(project, summary, description)` - 建立票證
*   `get_issue(key)` - 取得票證詳細資訊
*   `transition_issue(key, transition_id)` - 移動到不同狀態

**範例**："為登入問題建立一個錯誤票證並將其分配給後端團隊"

---

## 進階主題

### 自訂回應處理

有時您需要對 API 回應進行後處理：

```python
from google.adk.tools import OpenAPIToolset

# 建立工具集
toolset = OpenAPIToolset(spec=api_spec)

# 使用自訂處理包裝
async def search_jokes_enhanced(query: str) -> str:
    """帶有後處理的增強搜尋"""
    result = await toolset.search_jokes(query=query)
    # 只擷取笑話
    jokes = [item['value'] for item in result.get('result', [])]
    # 格式化
    if not jokes:
        return f"找不到關於 '{query}' 的笑話"
    return "\n\n".join(f"{i+1}. {joke}" for i, joke in enumerate(jokes[:3]))

# 在代理程式中使用增強版本
root_agent = Agent(
    ...,
    tools=[search_jokes_enhanced]  # 使用包裝函式而不是原始工具集
)
```

### 多個 API 整合

在一個代理程式中結合多個 API：

```python
chuck_toolset = OpenAPIToolset(spec=chuck_norris_spec)
github_toolset = OpenAPIToolset(
    spec=github_spec,
    auth_config={"type": "bearer", "token": github_token}
)
root_agent = Agent(
    ...,
    tools=[chuck_toolset, github_toolset, custom_function]
)
```

### 速率限制處理

為受速率限制的 API 實作重試邏輯：

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def api_call_with_retry():
    return await toolset.some_endpoint()
```

---

## 練習

1.  **新增天氣 API**：整合 OpenWeatherMap API 並進行身份驗證
2.  **建立新聞代理程式**：使用 NewsAPI 擷取並總結文章
3.  **建立多 API 代理程式**：在一個代理程式中結合 3 個或更多不同的 API
4.  **自訂包裝函式**：為 Chuck Norris API 回應編寫後處理
5.  **錯誤處理**：為網路故障新增 try/except 區塊

---

## 進一步閱讀

*   [OpenAPI 規範](https://spec.openapis.org/oas/latest.html)
*   [Chuck Norris API 文件](https://api.chucknorris.io/)
*   [ADK OpenAPIToolset 文件](https://google.github.io/adk-docs/tools/openapi/)
*   [Swagger 編輯器](https://editor.swagger.io/) - 測試 OpenAPI 規範
*   [公開 API 列表](https://github.com/public-apis/public-apis) - 尋找要整合的 API

---

**恭喜！** 您現在可以將您的代理程式連接到任何符合 OpenAPI 的 REST API，而無需手動編寫工具程式碼。這開啟了與數千個網路服務的整合！

## 後續步驟

🚀 **教學 04：循序工作流程** - 學習在有序的管道中協調多個代理程式

### 💬 加入討論

有問題或回饋嗎？在 GitHub Discussions 上與社群討論本教學。
