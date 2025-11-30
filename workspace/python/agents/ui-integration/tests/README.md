# UI Integration 測試案例

## 簡介

此文件提供了 UI Integration 專案的詳細測試案例，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Agent 設定測試 (`tests/test_agent.py`)

此部分涵蓋對 Agent 設定、FastAPI 應用程式、ADK Agent 封裝及環境設定的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 `root_agent` 是否成功匯出 | None | 1. 匯入 `agent.agent.root_agent` | None | `root_agent` 物件不為 None |
| **Agent 設定** | **TC-AGENT-002** | 測試 `root_agent` 是否為 `Agent` 類別的實例 | `root_agent` 已成功匯出 | 1. 檢查 `root_agent` 的類型 | None | `root_agent` 是 `google.adk.agents.Agent` 的實例 |
| **Agent 設定** | **TC-AGENT-003** | 測試 Agent 的名稱是否設定為 'quickstart_agent' | `root_agent` 已成功匯出 | 1. 讀取 `root_agent.name` 屬性 | None | 名稱應為 "quickstart_agent" |
| **Agent 設定** | **TC-AGENT-004** | 測試 Agent 是否已設定語言模型 | `root_agent` 已成功匯出 | 1. 檢查 `root_agent.model` 屬性 | None | 模型名稱應包含 "gemini" |
| **Agent 設定** | **TC-AGENT-005** | 測試 Agent 是否包含非空的 instruction | `root_agent` 已成功匯出 | 1. 檢查 `root_agent.instruction` 的內容與長度 | None | instruction 字串長度應大於 0 |
| **FastAPI 應用**| **TC-AGENT-006** | 測試 FastAPI 的 `app` 物件是否已建立 | None | 1. 匯入 `agent.agent.app` | None | `app` 物件不為 None |
| **FastAPI 應用**| **TC-AGENT-007** | 測試 `app` 的標題是否正確 | `app` 物件已建立 | 1. 讀取 `app.title` 屬性 | None | 標題應包含 "Tutorial 29" 或 "UI Integration" |
| **FastAPI 應用**| **TC-AGENT-008** | 測試 `/health` 健康檢查路由是否存在 | `app` 物件已建立 | 1. 遍歷 `app.routes` | None | 路由列表中應包含 `/health` |
| **FastAPI 應用**| **TC-AGENT-009** | 測試 `/` 根路由是否存在 | `app` 物件已建立 | 1. 遍歷 `app.routes` | None | 路由列表中應包含 `/` |
| **FastAPI 應用**| **TC-AGENT-010** | 測試 `/api/copilotkit` 相關路由是否存在 | `app` 物件已建立 | 1. 遍歷 `app.routes` | None | 應存在包含 "copilotkit" 的路由 |
| **ADK Agent 封裝**| **TC-AGENT-011** | 測試 ADK Agent 的封裝物件是否存在 | None | 1. 匯入 `agent.agent.agent` | None | `agent` 物件不為 None |
| **ADK Agent 封裝**| **TC-AGENT-012** | 測試封裝物件是否為 `ADKAgent` 的實例 | `agent` 物件已建立 | 1. 檢查 `agent` 的類型 | None | `agent` 是 `ag_ui_adk.ADKAgent` 的實例 |
| **ADK Agent 封裝**| **TC-AGENT-013** | 測試 `agent` 是否已設定 `app_name` | `agent` 物件已建立 | 1. 檢查 `agent` 是否為 `ADKAgent` 實例 (隱含 `app_name` 的設定) | None | `agent` 是 `ag_ui_adk.ADKAgent` 的實例 |
| **環境設定** | **TC-AGENT-014** | 測試 `agent/.env.example` 檔案是否存在 | None | 1. 檢查檔案路徑 `agent/.env.example` | None | 檔案存在 |
| **環境設定** | **TC-AGENT-015** | 測試 `agent/.env.example` 檔案中是否包含 `GOOGLE_API_KEY` | `agent/.env.example` 存在 | 1. 讀取檔案內容 | None | 內容應包含 "GOOGLE_API_KEY" |

## 模組匯入測試 (`tests/test_imports.py`)

此部分涵蓋對專案所有必要模組是否能正確匯入的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **依賴匯入** | **TC-IMPORTS-001** | 測試 Google ADK 相關模組的匯入 | Python 環境已設定 | 1. 嘗試匯入 `Agent` 和 `InMemoryRunner` | None | 模組成功匯入，無 `ImportError` |
| **依賴匯入** | **TC-IMPORTS-002** | 測試 FastAPI 相關模組的匯入 | Python 環境已設定 | 1. 嘗試匯入 `FastAPI`、`CORSMiddleware` 和 `uvicorn` | None | 模組成功匯入，無 `ImportError` |
| **依賴匯入** | **TC-IMPORTS-003** | 測試 AG-UI ADK 相關模組的匯入 | Python 環境已設定 | 1. 嘗試匯入 `ADKAgent` 和 `add_adk_fastapi_endpoint` | None | 模組成功匯入，無 `ImportError` |
| **內部模組** | **TC-IMPORTS-004** | 測試本地 `agent` 模組是否能成功匯入 | 專案結構正確 | 1. 嘗試匯入 `agent`、`root_agent` 和 `app` | None | 模組成功匯入，無 `ImportError` |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案目錄與檔案結構完整性的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **目錄結構** | **TC-STRUCT-001** | 測試 `agent` 目錄是否存在 | None | 1. 檢查 `agent` 是否為目錄 | None | `agent` 目錄存在 |
| **目錄結構** | **TC-STRUCT-002** | 測試 `frontend` 目錄是否存在 | None | 1. 檢查 `frontend` 是否為目錄 | None | `frontend` 目錄存在 |
| **目錄結構** | **TC-STRUCT-003** | 測試 `tests` 目錄是否存在 | None | 1. 檢查 `tests` 是否為目錄 | None | `tests` 目錄存在 |
| **檔案存在性**| **TC-STRUCT-004** | 測試 `agent` 目錄中的必要檔案是否存在 | `agent` 目錄存在 | 1. 檢查 `__init__.py`, `agent.py`, `.env.example` 檔案 | None | 所有檔案都存在 |
| **檔案存在性**| **TC-STRUCT-005** | 測試根目錄中的必要檔案是否存在 | None | 1. 檢查 `requirements.txt`, `pyproject.toml`, `Makefile`, `README.md` 檔案 | None | 所有檔案都存在 |
| **檔案內容** | **TC-STRUCT-006** | 測試 `.env.example` 檔案是否包含 `GOOGLE_API_KEY` | `.env.example` 檔案存在 | 1. 讀取檔案內容並搜尋關鍵字 | None | 檔案內容包含 "GOOGLE_API_KEY" |
| **檔案內容** | **TC-STRUCT-007** | 測試 `requirements.txt` 檔案是否包含所有必要的套件 | `requirements.txt` 檔案存在 | 1. 讀取檔案內容並搜尋所有必要套件 | `google-adk`, `fastapi`, `uvicorn`, `ag-ui-adk`, `python-dotenv`, `pytest` | 所有套件都存在於檔案內容中 |
