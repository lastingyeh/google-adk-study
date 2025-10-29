# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Agent 設定與功能測試 (`tests/test_agent.py`)

此部分涵蓋對 Agent 的設定與功能測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 `root_agent` 變數是否存在 | `root_agent` 已被定義 | 1. 檢查 `root_agent` 是否為 `None` | `root_agent` | `root_agent` 不為 `None` |
| **Agent 設定** | **TC-AGENT-002** | 測試 Agent 是否使用正確的模型 | `root_agent` 已被定義 | 1. 檢查 `root_agent.model` 的值 | `root_agent.model` | `root_agent.model` 的值為 "gemini-2.0-flash-exp" |
| **Agent 設定** | **TC-AGENT-003** | 測試 Agent 是否有正確的名稱 | `root_agent` 已被定義 | 1. 檢查 `root_agent.name` 的值 | `root_agent.name` | `root_agent.name` 的值為 "mcp_file_assistant" |
| **Agent 設定** | **TC-AGENT-004** | 測試 Agent 是否有描述 | `root_agent` 已被定義 | 1. 檢查 `root_agent.description` 是否為 `None`<br>2. 檢查 `root_agent.description` 的長度是否大於 0 | `root_agent.description` | `root_agent.description` 不為 `None` 且長度大於 0 |
| **Agent 設定** | **TC-AGENT-005** | 測試 Agent 是否有指令 | `root_agent` 已被定義 | 1. 檢查 `root_agent.instruction` 是否為 `None`<br>2. 檢查 `root_agent.instruction` 是否包含 "filesystem" | `root_agent.instruction` | `root_agent.instruction` 不為 `None` 且包含 "filesystem" |
| **Agent 設定** | **TC-AGENT-006** | 測試 Agent 是否已設定工具 | `root_agent` 已被定義 | 1. 檢查 `root_agent.tools` 是否為 `None`<br>2. 檢查 `root_agent.tools` 的長度是否大於 0 | `root_agent.tools` | `root_agent.tools` 不為 `None` 且長度大於 0 |
| **Agent 建立** | **TC-AGENT-007** | 測試使用預設目錄建立 Agent | `create_mcp_filesystem_agent` 函式可用 | 1. 呼叫 `create_mcp_filesystem_agent()` | None | 函式回傳一個 Agent 物件，且其名稱為 "mcp_file_assistant" |
| **Agent 建立** | **TC-AGENT-008** | 測試使用自訂目錄建立 Agent | `create_mcp_filesystem_agent` 函式可用 | 1. 建立一個暫存目錄<br>2. 呼叫 `create_mcp_filesystem_agent(tmpdir)` | 暫存目錄路徑 | 函式回傳一個 Agent 物件 |
| **Agent 建立** | **TC-AGENT-009** | 測試使用不存在的目錄建立 Agent 會引發錯誤 | `create_mcp_filesystem_agent` 函式可用 | 1. 呼叫 `create_mcp_filesystem_agent` 並傳入一個不存在的路徑 | "/nonexistent/directory/path" | 函式引發 `ValueError` |
| **MCP 工具集** | **TC-AGENT-010** | 測試 MCP 的匯入是否可用 | None | 1. 匯入 `McpToolset` 與 `StdioConnectionParams` | None | 成功匯入 |
| **MCP 工具集** | **TC-AGENT-011** | 測試 `StdioConnectionParams` 是否可以被建立 | `StdioConnectionParams` 與 `StdioServerParameters` 可用 | 1. 建立 `StdioServerParameters`<br>2. 建立 `StdioConnectionParams` | `command="npx"`, `args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]` | 成功建立 `StdioConnectionParams` 物件 |
| **MCP 工具集** | **TC-AGENT-012** | 測試 `MCPToolset` 是否可以透過 `StdioConnectionParams` 建立 | `McpToolset` 與 `StdioConnectionParams` 可用 | 1. 建立一個暫存目錄<br>2. 建立 `StdioServerParameters`<br>3. 建立 `McpToolset` | `command="npx"`, `args=["-y", "@modelcontextprotocol/server-filesystem", tmpdir]` | 成功建立 `MCPToolset` 物件 |
| **ADK 版本** | **TC-AGENT-013** | 測試 ADK 1.16.0+ 的功能是否可用 | None | 1. 匯入 `SseConnectionParams`<br>2. 匯入 `StreamableHTTPConnectionParams` | None | 成功匯入 |
| **ADK 版本** | **TC-AGENT-014** | 測試 `SseConnectionParams` 是否可以被建立 | `SseConnectionParams` 可用 | 1. 建立 `SseConnectionParams` | `url="https://api.example.com/sse"`, `timeout=30.0`, `sse_read_timeout=300.0` | 成功建立 `SseConnectionParams` 物件 |
| **ADK 版本** | **TC-AGENT-015** | 測試 `StreamableHTTPConnectionParams` 是否可以被建立 | `StreamableHTTPConnectionParams` 可用 | 1. 建立 `StreamableHTTPConnectionParams` | `url="https://api.example.com/http"`, `timeout=30.0`, `sse_read_timeout=300.0` | 成功建立 `StreamableHTTPConnectionParams` 物件 |

## 人機互動 (HITL) 回呼功能測試 (`tests/test_hitl.py`)

此部分涵蓋對人機互動 (HITL) 回呼功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **工具名稱提取** | **TC-HITL-001** | 帶有 `.name` 屬性的工具應使用該名稱 | `before_tool_callback` 可用 | 1. 建立一個帶有 `name` 屬性的模擬工具物件<br>2. 建立一個模擬的 `tool_context`<br>3. 呼叫 `before_tool_callback` | `mock_tool.name = "write_file"` | `mock_context.state` 中 `temp:last_tool` 的值為 "write_file" |
| **工具名稱提取** | **TC-HITL-002** | 不帶 `.name` 屬性的工具應使用其字串表示 | `before_tool_callback` 可用 | 1. 建立一個不帶 `name` 屬性的模擬工具物件<br>2. 建立一個模擬的 `tool_context`<br>3. 呼叫 `before_tool_callback` | `mock_tool = Mock(spec=[])` | `mock_context.state` 中存在 `temp:last_tool` 且其型別為字串 |
| **破壞性操作偵測** | **TC-HITL-003** | 所有破壞性操作在未自動審批時應需要審批 | `before_tool_callback` 可用 | 1. 參數化測試不同的破壞性操作名稱<br>2. 建立模擬工具與 `tool_context`<br>3. 呼叫 `before_tool_callback` | `operation_name` in `["write_file", "write_text_file", "move_file", "create_directory"]` | 回傳結果不為 `None`，且狀態為 `requires_approval` |
| **破壞性操作偵測** | **TC-HITL-004** | 安全的讀取操作應無需審批即可允許 | `before_tool_callback` 可用 | 1. 參數化測試不同的安全操作名稱<br>2. 建立模擬工具與 `tool_context`<br>3. 呼叫 `before_tool_callback` | `operation_name` in `["read_file", "list_directory", "search_files", "get_file_info"]` | 回傳結果為 `None` |
| **審批工作流程** | **TC-HITL-005** | 當 `auto_approve` 為 `True` 時，應允許破壞性操作 | `before_tool_callback` 可用 | 1. 設定 `mock_context.state` 的 `user:auto_approve_file_ops` 為 `True`<br>2. 呼叫 `before_tool_callback` | `mock_tool.name = "write_file"` | 回傳結果為 `None` |
| **審批工作流程** | **TC-HITL-006** | 當缺少 `auto_approve` 標誌時，應阻止破壞性操作 | `before_tool_callback` 可用 | 1. `mock_context.state` 為空<br>2. 呼叫 `before_tool_callback` | `mock_tool.name = "write_file"` | 回傳結果不為 `None`，且狀態為 `requires_approval` |
| **審批工作流程** | **TC-HITL-007** | 當 `auto_approve` 明確為 `False` 時，應阻止破壞性操作 | `before_tool_callback` 可用 | 1. 設定 `mock_context.state` 的 `user:auto_approve_file_ops` 為 `False`<br>2. 呼叫 `before_tool_callback` | `mock_tool.name = "write_file"` | 回傳結果不為 `None`，且狀態為 `requires_approval` |
| **狀態管理** | **TC-HITL-008** | 每次呼叫時，工具計數應增加 | `before_tool_callback` 可用 | 1. 多次呼叫 `before_tool_callback` | `mock_tool.name = "read_file"` | `mock_context.state["temp:tool_count"]` 的值遞增 |
| **狀態管理** | **TC-HITL-009** | 應在狀態中追蹤最後一個工具的名稱 | `before_tool_callback` 可用 | 1. 使用不同的工具名稱呼叫 `before_tool_callback` | `mock_tool1.name = "read_file"`, `mock_tool2.name = "list_directory"` | `mock_context.state["temp:last_tool"]` 的值被更新 |
| **狀態管理** | **TC-HITL-010** | 狀態應在多次回呼調用之間保持不變 | `before_tool_callback` 可用 | 1. 初始化 `mock_context.state` 的值<br>2. 呼叫 `before_tool_callback` | `mock_context.state = {"user:custom_data": "preserved", "temp:previous_value": 42}` | 原始狀態被保留，新狀態被加入 |
| **審批訊息內容** | **TC-HITL-011** | 審批訊息應包含操作名稱 | `before_tool_callback` 可用 | 1. 呼叫 `before_tool_callback` | `mock_tool.name = "write_file"` | 回傳的訊息中包含 "write_file" |
| **審批訊息內容** | **TC-HITL-012** | 審批訊息應包含阻止的原因 | `before_tool_callback` 可用 | 1. 呼叫 `before_tool_callback` | `mock_tool.name = "write_file"` | 回傳的訊息中包含 "Reason:" |
| **審批訊息內容** | **TC-HITL-013** | 審批訊息應包含傳遞給工具的參數 | `before_tool_callback` 可用 | 1. 呼叫 `before_tool_callback` | `args = {"source": "/test/old.txt", "destination": "/test/new.txt"}` | 回傳的訊息中包含 "Arguments:" |
| **審批訊息內容** | **TC-HITL-014** | 審批訊息應包含如何審批的說明 | `before_tool_callback` 可用 | 1. 呼叫 `before_tool_callback` | `mock_tool.name = "create_directory"` | 回傳的訊息中包含 "auto_approve_file_ops" |
| **邊界情況** | **TC-HITL-015** | 回呼應能處理空的 `args` 字典 | `before_tool_callback` 可用 | 1. 呼叫 `before_tool_callback` 並傳入空的 `args` | `args={}` | 回傳結果為 `None` |
| **邊界情況** | **TC-HITL-016** | 回呼應能處理狀態中的 `None` 值 | `before_tool_callback` 可用 | 1. 設定 `mock_context.state` 的值為 `None`<br>2. 呼叫 `before_tool_callback` | `mock_context.state = {"temp:tool_count": None, "user:auto_approve_file_ops": None}` | `mock_context.state["temp:tool_count"]` 的值為 1 |
| **邊界情況** | **TC-HITL-017** | 未知的工具名稱 (不在破壞性清單中) 應被允許 | `before_tool_callback` 可用 | 1. 呼叫 `before_tool_callback` 並傳入未知的工具名稱 | `mock_tool.name = "custom_unknown_operation"` | 回傳結果為 `None` |
| **整合情境** | **TC-HITL-018** | 測試一個讀取檔案後再寫入的工作流程 | `before_tool_callback` 可用 | 1. 讀取檔案 (應被允許)<br>2. 寫入檔案 (應被阻止)<br>3. 啟用自動審批<br>4. 再次寫入檔案 (應被允許) | `read_tool.name = "read_file"`, `write_tool.name = "write_file"` | 流程符合預期 |
| **整合情境** | **TC-HITL-019** | 測試多個破壞性操作是否都被阻止 | `before_tool_callback` 可用 | 1. 迭代呼叫多個破壞性操作 | `destructive_ops` | 所有操作都被阻止 |

## 匯入功能測試 (`tests/test_imports.py`)

此部分涵蓋對匯入功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入測試** | **TC-IMPORTS-001** | 測試匯入 `agent` 模組 | None | 1. `from mcp_agent import agent` | None | 成功匯入 `agent` |
| **匯入測試** | **TC-IMPORTS-002** | 測試匯入 `root_agent` | None | 1. `from mcp_agent import root_agent` | None | 成功匯入 `root_agent` |
| **匯入測試** | **TC-IMPORTS-003** | 測試匯入建立函式 | None | 1. `from mcp_agent.agent import create_mcp_filesystem_agent` | None | 成功匯入 `create_mcp_filesystem_agent` |
| **匯入測試** | **TC-IMPORTS-004** | 測試匯入文件整理器 | None | 1. `from mcp_agent.document_organizer import create_document_organizer_agent` | None | 成功匯入 `create_document_organizer_agent` |
| **匯入測試** | **TC-IMPORTS-005** | 測試匯入 ADK 核心模組 | None | 1. `from google.adk.agents import Agent`<br>2. `from google.adk import Runner` | None | 成功匯入 `Agent` 與 `Runner` |
| **匯入測試** | **TC-IMPORTS-006** | 測試匯入 MCP 工具 | None | 1. `from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams` | None | 成功匯入 `MCPToolset` 與 `StdioConnectionParams` |
| **匯入測試** | **TC-IMPORTS-007** | 測試匯入 MCP 連線類型 (ADK 1.16.0+) | None | 1. `from google.adk.tools.mcp_tool import SseConnectionParams, StreamableHTTPConnectionParams` | None | 成功匯入 `SseConnectionParams` 與 `StreamableHTTPConnectionParams` |
| **匯入測試** | **TC-IMPORTS-008** | 測試匯入驗證憑證類別 (ADK 1.16.0+) | ADK 版本支援 | 1. `from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes` | None | 成功匯入 `AuthCredential` 與 `AuthCredentialTypes`，若不支援則跳過 |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案結構的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRUCT-001** | 測試 `mcp_agent` 目錄是否存在 | None | 1. 檢查 `mcp_agent` 是否為目錄 | `mcp_agent` | `mcp_agent` 是一個目錄 |
| **專案結構** | **TC-STRUCT-002** | 測試 `tests` 目錄是否存在 | None | 1. 檢查 `tests` 是否為目錄 | `tests` | `tests` 是一個目錄 |
| **專案結構** | **TC-STRUCT-003** | 測試 `mcp_agent/__init__.py` 是否存在 | None | 1. 檢查 `mcp_agent/__init__.py` 是否為檔案 | `mcp_agent/__init__.py` | `mcp_agent/__init__.py` 是一個檔案 |
| **專案結構** | **TC-STRUCT-004** | 測試 `mcp_agent/agent.py` 是否存在 | None | 1. 檢查 `mcp_agent/agent.py` 是否為檔案 | `mcp_agent/agent.py` | `mcp_agent/agent.py` 是一個檔案 |
| **專案結構** | **TC-STRUCT-005** | 測試 `mcp_agent/document_organizer.py` 是否存在 | None | 1. 檢查 `mcp_agent/document_organizer.py` 是否為檔案 | `mcp_agent/document_organizer.py` | `mcp_agent/document_organizer.py` 是一個檔案 |
| **專案結構** | **TC-STRUCT-006** | 測試 `.env.example` 是否存在 | None | 1. 檢查 `mcp_agent/.env.example` 是否為檔案 | `mcp_agent/.env.example` | `mcp_agent/.env.example` 是一個檔案 |
| **專案結構** | **TC-STRUCT-007** | 測試 `requirements.txt` 是否存在 | None | 1. 檢查 `requirements.txt` 是否為檔案 | `requirements.txt` | `requirements.txt` 是一個檔案 |
| **專案結構** | **TC-STRUCT-008** | 測試 `pyproject.toml` 是否存在 | None | 1. 檢查 `pyproject.toml` 是否為檔案 | `pyproject.toml` | `pyproject.toml` 是一個檔案 |
| **專案結構** | **TC-STRUCT-009** | 測試 `Makefile` 是否存在 | None | 1. 檢查 `Makefile` 是否為檔案 | `Makefile` | `Makefile` 是一個檔案 |
| **專案結構** | **TC-STRUCT-010** | 測試 `README.md` 是否存在 | None | 1. 檢查 `README.md` 是否為檔案 | `README.md` | `README.md` 是一個檔案 |
| **專案結構** | **TC-STRUCT-011** | 測試所有測試檔案是否存在 | None | 1. 檢查 `tests/__init__.py`<br>2. 檢查 `tests/test_agent.py`<br>3. 檢查 `tests/test_imports.py`<br>4. 檢查 `tests/test_structure.py` | 檔案路徑 | 所有檔案都存在 |
| **檔案內容** | **TC-STRUCT-012** | 測試 `__init__.py` 是否匯出 `root_agent` | `mcp_agent/__init__.py` 存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 "root_agent" | `mcp_agent/__init__.py` | 檔案內容包含 "root_agent" |
| **檔案內容** | **TC-STRUCT-013** | 測試 `agent.py` 是否定義 `root_agent` | `mcp_agent/agent.py` 存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 "root_agent" 與 "MCPToolset" | `mcp_agent/agent.py` | 檔案內容包含 "root_agent" 與 "MCPToolset" |
| **檔案內容** | **TC-STRUCT-014** | 測試 `.env.example` 是否有 API 金鑰的佔位符 | `mcp_agent/.env.example` 存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 "GOOGLE_API_KEY" | `mcp_agent/.env.example` | 檔案內容包含 "GOOGLE_API_KEY" |
| **檔案內容** | **TC-STRUCT-015** | 測試 `requirements.txt` 是否包含 `google-genai` | `requirements.txt` 存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 "google-genai" | `requirements.txt` | 檔案內容包含 "google-genai" |
| **檔案內容** | **TC-STRUCT-016** | 測試 `pyproject.toml` 是否有套件名稱 | `pyproject.toml` 存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 "name" 與 "mcp_agent" | `pyproject.toml` | 檔案內容包含 "name" 與 "mcp_agent" |
