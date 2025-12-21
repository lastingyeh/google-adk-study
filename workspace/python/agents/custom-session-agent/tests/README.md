# 詳細測試案例

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 代理配置測試 (`tests/test_agent.py`)

此部分涵蓋對 Custom Session Agent 的配置、類別結構及模型設定的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理配置** | **TC-AGENT-001** | 測試 root_agent 是否已定義 | 已安裝 ADK | 匯入 `custom_session_agent.agent.root_agent` | 無 | `root_agent` 不為 None |
| **代理配置** | **TC-AGENT-002** | 測試 root_agent 是否有名稱 | 已安裝 ADK | 檢查 `root_agent.name` 屬性 | 無 | 名稱為 "custom_session_agent" |
| **代理配置** | **TC-AGENT-003** | 測試 root_agent 是否有描述 | 已安裝 ADK | 檢查 `root_agent.description` 屬性 | 無 | 描述包含 "custom session service" |
| **代理配置** | **TC-AGENT-004** | 測試 root_agent 是否有工具 | 已安裝 ADK | 檢查 `root_agent.tools` 屬性 | 無 | 工具數量 >= 4 |
| **代理配置** | **TC-AGENT-005** | 測試所有代理工具是否可呼叫 | 已安裝 ADK | 遍歷 `root_agent.tools` | 無 | 每個工具皆為 callable |
| **代理配置** | **TC-AGENT-006** | 測試 root_agent 是否有用於狀態管理的 output_key | 已安裝 ADK | 檢查 `root_agent.output_key` 屬性 | 無 | `output_key` 為 "session_result" |
| **CustomSessionServiceDemo 類別** | **TC-AGENT-007** | 測試 demo 類別是否有 register_redis_service 方法 | 已安裝 ADK | 檢查 `CustomSessionServiceDemo` 類別屬性 | 無 | 擁有 `register_redis_service` 方法且可呼叫 |
| **CustomSessionServiceDemo 類別** | **TC-AGENT-008** | 測試 demo 類別是否有 register_memory_service 方法 | 已安裝 ADK | 檢查 `CustomSessionServiceDemo` 類別屬性 | 無 | 擁有 `register_memory_service` 方法且可呼叫 |
| **CustomSessionServiceDemo 類別** | **TC-AGENT-009** | 測試模組匯入時服務是否已註冊 | 已安裝 ADK | 1. 取得服務註冊表<br>2. 嘗試獲取 "redis" session service factory | 無 | 成功獲取 factory，不為 None |
| **代理模型配置** | **TC-AGENT-010** | 測試 root_agent 是否使用 Gemini 模型 | 已安裝 ADK | 檢查 `root_agent.model` 屬性 | 無 | 模型名稱包含 "gemini" |
| **代理模型配置** | **TC-AGENT-011** | 測試 root_agent 是否有指令文字 | 已安裝 ADK | 檢查 `root_agent.instruction` 屬性 | 無 | 指令長度 > 0 且包含 "session service" |

## 匯入與環境測試 (`tests/test_imports.py`)

此部分涵蓋對模組匯入、類別存在性及環境變數配置的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入測試** | **TC-IMPORT-001** | 測試是否可以匯入代理模組 | 已安裝 ADK | 匯入 `custom_session_agent.agent` | 無 | 模組包含 `root_agent` 屬性 |
| **匯入測試** | **TC-IMPORT-002** | 測試 CustomSessionServiceDemo 類別是否存在 | 已安裝 ADK | 從 agent 模組匯入 `CustomSessionServiceDemo` | 無 | 成功匯入且不為 None |
| **匯入測試** | **TC-IMPORT-003** | 測試所有工具函式是否已定義 | 已安裝 ADK | 從 agent 模組匯入所有工具函式 | 無 | 所有工具函式皆可呼叫 |
| **環境配置** | **TC-IMPORT-004** | 測試 .env.example 檔案是否存在 | 專案根目錄有 .env.example | 檢查檔案路徑是否存在 | 無 | 檔案存在 |
| **環境配置** | **TC-IMPORT-005** | 測試 .env.example 是否包含必要的 Redis 變數 | .env.example 存在 | 讀取檔案內容並檢查關鍵字 | 無 | 包含 GOOGLE_API_KEY, REDIS_HOST, REDIS_PORT, SESSION_SERVICE_URI |

## 工具函式測試 (`tests/test_tools.py`)

此部分涵蓋對各個工具函式的回傳結構及內容的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **工具函式測試** | **TC-TOOL-001** | 測試 describe_session_info 是否回傳適當的字典 | 已安裝 ADK | 呼叫 `describe_session_info` | "test_session_123" | 回傳 dict，包含 status, report, data，status 為 success |
| **工具函式測試** | **TC-TOOL-002** | 測試 describe_session_info 是否在資料中回傳 session ID | 已安裝 ADK | 呼叫 `describe_session_info` | "session_xyz" | data['session_id'] 等於輸入的 session ID |
| **工具函式測試** | **TC-TOOL-003** | 測試 test_session_persistence 是否回傳適當的字典 | 已安裝 ADK | 呼叫 `test_session_persistence` | "user_name", "John Doe" | 回傳 dict，包含 status, report, data，status 為 success |
| **工具函式測試** | **TC-TOOL-004** | 測試 test_session_persistence 是否儲存鍵和值 | 已安裝 ADK | 呼叫 `test_session_persistence` | "color", "blue" | data 中包含正確的 key 和 value |
| **工具函式測試** | **TC-TOOL-005** | 測試 show_service_registry_info 是否回傳適當的字典 | 已安裝 ADK | 呼叫 `show_service_registry_info` | 無 | 回傳 dict，包含 status, report, data |
| **工具函式測試** | **TC-TOOL-006** | 測試 show_service_registry_info 是否說明 Redis 註冊 | 已安裝 ADK | 呼叫 `show_service_registry_info` | 無 | data 包含 redis_registration 資訊 |
| **工具函式測試** | **TC-TOOL-007** | 測試 get_session_backend_guide 是否回傳適當的字典 | 已安裝 ADK | 呼叫 `get_session_backend_guide` | 無 | 回傳 dict，包含 status, report, data，status 為 success |
| **工具函式測試** | **TC-TOOL-008** | 測試 get_session_backend_guide 是否專注於 Redis | 已安裝 ADK | 呼叫 `get_session_backend_guide` | 無 | data 包含 why_redis, redis_setup, features, best_practices |
| **工具函式測試** | **TC-TOOL-009** | 測試 get_session_backend_guide 是否有 Redis 設定資訊 | 已安裝 ADK | 呼叫 `get_session_backend_guide` | 無 | redis_setup 包含 start_container 和 connect |
| **工具回傳結構測試** | **TC-TOOL-010** | 測試所有工具是否回傳 status 鍵 | 已安裝 ADK | 依次呼叫所有工具函式 | 各自所需的參數 | 所有結果皆包含 "status" 鍵 |
| **工具回傳結構測試** | **TC-TOOL-011** | 測試所有工具是否回傳 report 鍵 | 已安裝 ADK | 依次呼叫所有工具函式 | 各自所需的參數 | 所有結果皆包含 "report" 鍵 |
