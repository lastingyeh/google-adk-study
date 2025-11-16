# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## A2A Agent 測試 (`tests/test_agent.py`)

此部分涵蓋對 A2A Agent 的主要設定、子 Agent、工具及模型組態的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A2A Agent 設定** | **TC-AGENT-001** | 測試 `root_agent` 是否存在且設定正確 | Agent 已初始化 | 1. 匯入 `root_agent`<br>2. 檢查其實例類型<br>3. 驗證 `name` 和 `description` 屬性 | `a2a_orchestrator.agent.root_agent` | `root_agent` 是 `Agent` 的實例，且 `name` 與 `description` 符合預期。 |
| **A2A Agent 設定** | **TC-AGENT-002** | 測試 `root_agent` 是否擁有正確的子 Agent | `root_agent` 已設定 | 1. 檢查 `sub_agents` 屬性是否存在<br>2. 驗證子 Agent 數量<br>3. 檢查是否包含所有必要的子 Agent 名稱 | `root_agent.sub_agents` | `root_agent` 包含 3 個子 Agent，且名稱符合預期。 |
| **A2A Agent 設定** | **TC-AGENT-003** | 測試 `root_agent` 是否擁有必要的工具 | `root_agent` 已設定 | 1. 檢查 `tools` 屬性是否存在<br>2. 驗證工具數量<br>3. 檢查是否包含所有必要的工具名稱 | `root_agent.tools` | `root_agent` 至少包含 2 個工具，且名稱符合預期。 |
| **A2A Agent 設定** | **TC-AGENT-004** | 測試 `check_agent_availability` 工具函式 | 工具函式可被呼叫 | 1. 使用無效的 URL 呼叫函式 | `agent_name`: "test_agent", `base_url`: "http://invalid-url:9999" | 函式返回一個字典，其中 `status` 為 "error"，`available` 為 `False`。 |
| **Agent 組態** | **TC-AGENT-005** | 測試 Agent 是否使用正確的模型 | `root_agent` 已設定 | 1. 檢查 `model` 屬性 | `root_agent.model` | `root_agent` 的模型為 "gemini-2.0-flash"。 |
| **Agent 組態** | **TC-AGENT-006** | 測試 Agent 是否有指令 | `root_agent` 已設定 | 1. 檢查 `instruction` 屬性是否存在且不為空 | `root_agent.instruction` | `instruction` 屬性存在且內容不為空。 |
| **Agent 組態** | **TC-AGENT-007** | 測試子 Agent 是否有正確的設定 | `root_agent` 已設定 | 1. 迭代所有子 Agent<br>2. 檢查每個子 Agent 的實例類型、`name` 和 `description` 屬性 | `root_agent.sub_agents` | 所有子 Agent 都是 `RemoteA2aAgent` 的實例，並具有 `name` 和 `description`。 |
| **工具** | **TC-AGENT-008** | 測試 `check_agent_availability` 是否返回正確的格式 | 工具函式可被呼叫 | 1. 使用無效的 URL 呼叫函式 | `agent_name`: "test", `base_url`: "http://invalid:9999" | 函式返回一個包含 `status`, `available`, `report` 鍵的字典。 |
| **工具** | **TC-AGENT-009** | 測試 `log_coordination_step` 是否返回正確的格式 | 工具函式可被呼叫 | 1. 呼叫函式 | `step`: "test step", `agent_name`: "test_agent" | 函式返回一個包含 `status`, `report`, `step`, `agent` 鍵的字典，且 `status` 為 "success"。 |

## 套件匯入測試 (`tests/test_imports.py`)

此部分涵蓋對 Agent 套件及其元件的匯入功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **套件匯入** | **TC-IMPORT-001** | 測試 `root_agent` 是否可以從套件中匯入 | 套件已安裝 | 1. 嘗試從 `a2a_orchestrator` 匯入 `root_agent` | `from a2a_orchestrator import root_agent` | `root_agent` 成功匯入且不為 `None`。 |
| **套件匯入** | **TC-IMPORT-002** | 測試 `agent` 模組是否可以被匯入 | 套件已安裝 | 1. 嘗試從 `a2a_orchestrator` 匯入 `agent` | `from a2a_orchestrator import agent` | `agent` 模組成功匯入，且 `agent.root_agent` 不為 `None`。 |
| **套件匯入** | **TC-IMPORT-003** | 測試工具是否可以被匯入 | 套件已安裝 | 1. 嘗試從 `a2a_orchestrator.agent` 匯入工具函式 | `from a2a_orchestrator.agent import check_agent_availability, log_coordination_step` | `check_agent_availability` 和 `log_coordination_step` 成功匯入且不為 `None`。 |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案結構及必要檔案是否存在的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **檔案結構** | **TC-STRUCT-001** | 測試 `pyproject.toml` 是否存在 | 專案根目錄 | 1. 檢查 `pyproject.toml` 檔案是否存在 | `os.path.exists("pyproject.toml")` | 檔案存在。 |
| **檔案結構** | **TC-STRUCT-002** | 測試 `requirements.txt` 是否存在 | 專案根目錄 | 1. 檢查 `requirements.txt` 檔案是否存在 | `os.path.exists("requirements.txt")` | 檔案存在。 |
| **檔案結構** | **TC-STRUCT-003** | 測試 Agent 目錄是否存在 | 專案根目錄 | 1. 檢查 `a2a_orchestrator` 目錄是否存在 | `os.path.exists("a2a_orchestrator")` | 目錄存在。 |
| **檔案結構** | **TC-STRUCT-004** | 測試 `__init__.py` 是否存在於 Agent 目錄中 | `a2a_orchestrator` 目錄存在 | 1. 檢查 `a2a_orchestrator/__init__.py` 檔案是否存在 | `os.path.join("a2a_orchestrator", "__init__.py")` | 檔案存在。 |
| **檔案結構** | **TC-STRUCT-005** | 測試 `agent.py` 是否存在 | `a2a_orchestrator` 目錄存在 | 1. 檢查 `a2a_orchestrator/agent.py` 檔案是否存在 | `os.path.join("a2a_orchestrator", "agent.py")` | 檔案存在。 |
| **檔案結構** | **TC-STRUCT-006** | 測試 `.env.example` 是否存在 | `a2a_orchestrator` 目錄存在 | 1. 檢查 `a2a_orchestrator/.env.example` 檔案是否存在 | `os.path.join("a2a_orchestrator", ".env.example")` | 檔案存在。 |
| **檔案結構** | **TC-STRUCT-007** | 測試 `tests` 目錄是否存在 | 專案根目錄 | 1. 檢查 `tests` 目錄是否存在 | `os.path.exists("tests")` | 目錄存在。 |
| **檔案結構** | **TC-STRUCT-008** | 測試測試檔案是否存在 | `tests` 目錄存在 | 1. 檢查 `test_agent.py`, `test_imports.py`, `test_structure.py` 是否存在 | `os.path.join("tests", test_file)` | 所有測試檔案都存在。 |
| **內容驗證** | **TC-STRUCT-009** | 測試 `__init__.py` 是否正確匯入 `root_agent` | `a2a_orchestrator/__init__.py` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含匯入和導出語句 | `__init__.py` 內容 | 檔案內容包含 `from .agent import root_agent` 和 `__all__ = ['root_agent']`。 |
| **內容驗證** | **TC-STRUCT-010** | 測試 `pyproject.toml` 是否有正確的專案名稱 | `pyproject.toml` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查專案名稱 | `pyproject.toml` 內容 | 檔案內容包含 `name = "tutorial17"`。 |
| **內容驗證** | **TC-STRUCT-011** | 測試 `requirements.txt` 是否包含 `google-adk` | `requirements.txt` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 `google-adk` | `requirements.txt` 內容 | 檔案內容包含 `google-adk`。 |
| **內容驗證** | **TC-STRUCT-012** | 測試 `.env.example` 是否包含必要的環境變數 | `a2a_orchestrator/.env.example` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含所有必要的環境變數 | `.env.example` 內容 | 檔案內容包含所有必要的環境變數。 |
