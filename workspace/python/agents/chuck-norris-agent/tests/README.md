# Chuck Norris Agent 測試案例

此目錄包含 `chuck-norris-agent` 的所有測試案例，旨在確保 Agent 的功能、結構與依賴性皆符合預期。

---

# Agent 功能測試 (`tests/test_agent.py`)

此檔案包含對 `chuck-norris-agent` 的核心功能、設定、OpenAPI 規範及整合的完整測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 `root_agent` 是否能成功匯入 | `chuck_norris_agent` 套件已安裝 | 1. 從 `chuck_norris_agent.agent` 匯入 `root_agent` | `None` | `root_agent` 物件成功匯入，不為 `None` |
| **Agent 設定** | **TC-AGENT-002** | 測試 `root_agent` 是否為 `Agent` 的實例 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent` 的類型 | `root_agent` | `root_agent` 是 `google.adk.agents.Agent` 的一個實例 |
| **Agent 設定** | **TC-AGENT-003** | 測試 Agent 的名稱是否正確 | `root_agent` 已成功匯入 | 1. 讀取 `root_agent.name` 屬性 | `None` | 名稱應為 `chuck_norris_agent` |
| **Agent 設定** | **TC-AGENT-004** | 測試 Agent 使用的模型是否正確 | `root_agent` 已成功匯入 | 1. 讀取 `root_agent.model` 屬性 | `None` | 模型應為 `gemini-2.0-flash` |
| **Agent 設定** | **TC-AGENT-005** | 測試 Agent 是否有描述 | `root_agent` 已成功匯入 | 1. 讀取 `root_agent.description` 屬性 | `None` | 描述應包含 "Chuck Norris" 和 "OpenAPI tools" |
| **Agent 設定** | **TC-AGENT-006** | 測試 Agent 是否有完整的指令 | `root_agent` 已成功匯入 | 1. 讀取 `root_agent.instruction` 屬性 | `None` | 指令應包含 "Chuck Norris fact assistant"、"get_random_joke"、"search_jokes" 和 "get_categories" |
| **Agent 設定** | **TC-AGENT-007** | 測試指令的長度是否足夠 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.instruction` 的長度 | `None` | 長度應大於 500 個字元 |
| **Agent 設定** | **TC-AGENT-008** | 測試 Agent 是否已設定工具 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.tools` 屬性 | `None` | `tools` 屬性不為 `None` 且應包含至少一個工具 |
| **OpenAPI 規範** | **TC-AGENT-009** | 測試規範是否具備必要的 OpenAPI 結構 | `CHUCK_NORRIS_SPEC` 已定義 | 1. 檢查 `CHUCK_NORRIS_SPEC` 的頂層鍵 | `None` | 應包含 `openapi`, `info`, `servers`, `paths` |
| **OpenAPI 規範** | **TC-AGENT-010** | 測試規範是否使用 OpenAPI 3.0.0 | `CHUCK_NORRIS_SPEC` 已定義 | 1. 讀取 `openapi` 鍵的值 | `None` | 版本應為 `3.0.0` |
| **OpenAPI 規範** | **TC-AGENT-011** | 測試規範是否有正確的伺服器設定 | `CHUCK_NORRIS_SPEC` 已定義 | 1. 檢查 `servers` 列表 | `None` | 應包含一個伺服器 URL，指向 `api.chucknorris.io` |
| **OpenAPI 規範** | **TC-AGENT-012** | 測試規範是否包含所有必要的路徑 | `CHUCK_NORRIS_SPEC` 已定義 | 1. 檢查 `paths` 物件的鍵 | `None` | 應包含 `/random`, `/search`, `/categories` |
| **OpenAPI 工具集** | **TC-AGENT-013** | 測試工具集是否能從規範中建立 | `chuck_norris_toolset` 已建立 | 1. 檢查 `chuck_norris_toolset` 的類型 | `chuck_norris_toolset` | 物件應為 `OpenAPIToolset` 的實例 |
| **OpenAPI 工具集** | **TC-AGENT-014** | 測試工具集是否提供工具 | `chuck_norris_toolset` 已建立 | 1. 非同步呼叫 `get_tools()` 方法 | `None` | 返回一個包含 3 個工具的列表 |
| **Agent 整合** | **TC-AGENT-015** | 測試 Agent 建立時不會拋出例外 | `root_agent` 已定義 | 1. 嘗試存取 `root_agent` | `None` | 程式應能成功執行，不會引發任何例外 |
| **Agent 整合** | **TC-AGENT-016** | 測試 Agent 是否具備 API 使用所需的所有設定 | `root_agent` 已定義 | 1. 檢查 `model` 和 `tools` 屬性<br>2. 檢查 `instruction` 內容 | `None` | 模型和工具皆已設定，且指令中包含 `random`, `search`, `categories` |

---

# 模組匯入測試 (`tests/test_imports.py`)

此檔案用於驗證專案所需的所有模組和套件是否能成功匯入，確保環境設定的正確性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **依賴性匯入** | **TC-IMPORT-001** | 測試 `google.adk.agents` 的匯入 | `google-adk` 套件已安裝 | 1. 嘗試從 `google.adk.agents` 匯入 `Agent` | `None` | `Agent` 類別成功匯入，不為 `None` |
| **依賴性匯入** | **TC-IMPORT-002** | 測試 `google.adk.tools` 的匯入 | `google-adk` 套件已安裝 | 1. 嘗試從 `google.adk.tools.openapi_tool` 匯入 `OpenAPIToolset` | `None` | `OpenAPIToolset` 類別成功匯入，不為 `None` |
| **專案模組匯入** | **TC-IMPORT-003** | 測試 `chuck_norris_agent` 模組的匯入 | 專案路徑已加入 Python Path | 1. 嘗試匯入 `chuck_norris_agent` | `None` | `chuck_norris_agent` 模組成功匯入，不為 `None` |
| **專案模組匯入** | **TC-IMPORT-004** | 測試 `chuck_norris_agent.agent` 模組的匯入 | 專案路徑已加入 Python Path | 1. 嘗試從 `chuck_norris_agent` 匯入 `agent` | `None` | `agent` 模組成功匯入，不為 `None` |
| **專案模組匯入** | **TC-IMPORT-005** | 測試 `root_agent` 是否能從套件中匯入 | 專案路徑已加入 Python Path | 1. 嘗試從 `chuck_norris_agent` 匯入 `root_agent` | `None` | `root_agent` 物件成功匯入，不為 `None` |
| **Python 特性** | **TC-IMPORT-006** | 測試 `__future__ annotations` 的匯入 | Python 3.7+ 環境 | 1. 嘗試匯入 `__future__` 並檢查 `annotations` 屬性 | `None` | 匯入成功，且 `__future__` 模組具有 `annotations` 屬性 |

---

# 專案結構測試 (`tests/test_structure.py`)

此檔案確保專案的目錄結構和重要檔案都符合預期，是維持專案一致性的關鍵。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRUCT-001** | 測試 `chuck_norris_agent` 目錄是否存在 | 專案根目錄 | 1. 檢查 `chuck_norris_agent` 是否為一個目錄 | `None` | `chuck_norris_agent` 目錄存在 |
| **專案結構** | **TC-STRUCT-002** | 測試 `chuck_norris_agent/__init__.py` 是否存在 | `chuck_norris_agent` 目錄存在 | 1. 檢查 `__init__.py` 檔案是否存在 | `None` | `__init__.py` 檔案存在 |
| **專案結構** | **TC-STRUCT-003** | 測試 `chuck_norris_agent/agent.py` 是否存在 | `chuck_norris_agent` 目錄存在 | 1. 檢查 `agent.py` 檔案是否存在 | `None` | `agent.py` 檔案存在 |
| **專案結構** | **TC-STRUCT-004** | 測試 `__init__.py` 的內容是否正確 | `__init__.py` 檔案存在 | 1. 讀取檔案內容並檢查 | `None` | 內容包含 `from .agent import root_agent` 和 `__all__ = ['root_agent']` |
| **專案結構** | **TC-STRUCT-005** | 測試 `agent.py` 是否為有效的 Python 檔案 | `agent.py` 檔案存在 | 1. 讀取檔案內容並檢查關鍵匯入 | `None` | 內容包含 `from google.adk.agents import Agent` 和 `root_agent = Agent(` |
| **測試結構** | **TC-STRUCT-006** | 測試 `tests` 目錄是否存在 | 專案根目錄 | 1. 檢查 `tests` 是否為一個目錄 | `None` | `tests` 目錄存在 |
| **測試結構** | **TC-STRUCT-007** | 測試 `tests/__init__.py` 是否存在 | `tests` 目錄存在 | 1. 檢查 `__init__.py` 檔案是否存在 | `None` | `__init__.py` 檔案存在 |
| **測試結構** | **TC-STRUCT-008** | 測試所有必要的測試檔案是否存在 | `tests` 目錄存在 | 1. 遍歷檢查指定的測試檔案 | `['test_agent.py', 'test_imports.py', 'test_structure.py']` | 所有指定的測試檔案都存在 |
| **根目錄檔案** | **TC-STRUCT-009** | 測試 `README.md` 是否存在 | 專案根目錄 | 1. 檢查 `README.md` 檔案是否存在 | `None` | `README.md` 檔案存在 |
| **根目錄檔案** | **TC-STRUCT-010** | 測試 `Makefile` 是否存在 | 專案根目錄 | 1. 檢查 `Makefile` 檔案是否存在 | `None` | `Makefile` 檔案存在 |
| **根目錄檔案** | **TC-STRUCT-011** | 測試 `requirements.txt` 是否存在 | 專案根目錄 | 1. 檢查 `requirements.txt` 檔案是否存在 | `None` | `requirements.txt` 檔案存在 |
