# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 代理配置與功能 測試 (`tests/test_agent.py`)

此部分涵蓋對 數據分析代理的配置、工具功能及 API 端點 的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理配置** | **TC-AGENT-001** | 測試代理是否正確導入 | 無 | 1. 導入 `agent`, `root_agent`, `app` | 無 | 模組導入成功，物件不為 None |
| **代理配置** | **TC-AGENT-002** | 測試 root_agent 是否具有正確的屬性 | 無 | 1. 導入 `root_agent`<br>2. 檢查屬性 | 無 | `root_agent` 具有 `name`, `model`, `instruction`, `tools` 屬性，且 name 為 "data_analyst" |
| **代理配置** | **TC-AGENT-003** | 測試代理是否具有所需的工具 | 無 | 1. 導入 `root_agent`<br>2. 檢查工具列表 | 無 | `root_agent` 擁有 3 個工具：`load_csv_data`, `analyze_data`, `create_chart` |
| **代理配置** | **TC-AGENT-004** | 測試 FastAPI 應用程序是否配置正確 | 無 | 1. 導入 `app`<br>2. 檢查屬性 | 無 | `app` title 為 "Data Analysis Agent API"，且包含 version 資訊 |
| **CSV 數據加載** | **TC-LOAD-001** | 測試成功的 CSV 數據加載 | 無 | 1. 準備 CSV 內容<br>2. 呼叫 `load_csv_data` | `test.csv`, "name,age,score\nAlice,30,95..." | status 為 "success"，返回正確的行數、欄位及預覽 |
| **CSV 數據加載** | **TC-LOAD-002** | 測試帶有標題的 CSV 加載 | 無 | 1. 準備帶標題 CSV 內容<br>2. 呼叫 `load_csv_data` | `products.csv`, "product,quantity,price..." | status 為 "success"，正確解析欄位名稱及行數 |
| **CSV 數據加載** | **TC-LOAD-003** | 測試無效數據的 CSV 加載 | 無 | 1. 準備無效 CSV 內容<br>2. 呼叫 `load_csv_data` | `invalid.csv`, "invalid csv format..." | 返回結果包含 "status" 欄位 (預期包含錯誤訊息) |
| **CSV 數據加載** | **TC-LOAD-004** | 測試空內容的 CSV 加載 | 無 | 1. 準備空字串<br>2. 呼叫 `load_csv_data` | `empty.csv`, "" | 返回結果包含 "status" 欄位 (預期包含錯誤訊息) |
| **數據分析** | **TC-ANALYZE-001** | 測試摘要分析 | 已加載 `test.csv` | 1. 呼叫 `analyze_data` (summary) | `test.csv`, "summary" | status 為 "success"，返回 describe, missing, unique 等統計數據 |
| **數據分析** | **TC-ANALYZE-002** | 測試特定欄位的分析 | 已加載 `test.csv` | 1. 呼叫 `analyze_data` 指定欄位 | `test.csv`, columns=["age", "score"] | status 為 "success"，返回指定欄位的數據 |
| **數據分析** | **TC-ANALYZE-003** | 測試相關性分析 | 已加載 `test.csv` | 1. 呼叫 `analyze_data` (correlation) | `test.csv`, "correlation" | status 為 "success"，返回相關性分析數據 |
| **數據分析** | **TC-ANALYZE-004** | 測試趨勢分析 | 已加載 `test.csv` | 1. 呼叫 `analyze_data` (trend) | `test.csv`, "trend" | status 為 "success"，返回趨勢方向 (upward/downward) |
| **數據分析** | **TC-ANALYZE-005** | 測試不存在的數據集分析 | 無 | 1. 呼叫 `analyze_data` | `nonexistent.csv` | status 為 "error"，訊息包含 "not found" |
| **數據分析** | **TC-ANALYZE-006** | 測試無效欄位的分析 | 已加載 `test.csv` | 1. 呼叫 `analyze_data` 無效欄位 | `test.csv`, columns=["invalid_col"] | status 為 "error" |
| **數據分析** | **TC-ANALYZE-007** | 測試無效分析類型的分析 | 已加載 `test.csv` | 1. 呼叫 `analyze_data` 無效類型 | `test.csv`, "invalid_type" | status 為 "error" |
| **圖表建立** | **TC-CHART-001** | 測試折線圖建立 | 已加載 `sales.csv` | 1. 呼叫 `create_chart` (line) | `sales.csv`, "line", "month", "sales" | status 為 "success"，chart_type 為 "line"，包含正確數據與標籤 |
| **圖表建立** | **TC-CHART-002** | 測試長條圖建立 | 已加載 `sales.csv` | 1. 呼叫 `create_chart` (bar) | `sales.csv`, "bar", "month", "sales" | status 為 "success"，chart_type 為 "bar" |
| **圖表建立** | **TC-CHART-003** | 測試散點圖建立 | 已加載 `sales.csv` | 1. 呼叫 `create_chart` (scatter) | `sales.csv`, "scatter", "month", "sales" | status 為 "success"，chart_type 為 "scatter" |
| **圖表建立** | **TC-CHART-004** | 測試不存在的數據集圖表建立 | 無 | 1. 呼叫 `create_chart` | `nonexistent.csv` | status 為 "error"，訊息包含 "not found" |
| **圖表建立** | **TC-CHART-005** | 測試無效欄位的圖表建立 | 已加載 `sales.csv` | 1. 呼叫 `create_chart` 無效欄位 | `sales.csv`, "invalid_col" | status 為 "error" |
| **圖表建立** | **TC-CHART-006** | 測試無效圖表類型的圖表建立 | 已加載 `sales.csv` | 1. 呼叫 `create_chart` 無效類型 | `sales.csv`, "invalid_type" | status 為 "error" |
| **圖表建立** | **TC-CHART-007** | 測試圖表是否具有適當的選項 | 已加載 `sales.csv` | 1. 呼叫 `create_chart` | `sales.csv` | status 為 "success"，options 包含 title, x_label, y_label |
| **API 端點** | **TC-API-001** | 測試健康檢查端點 | FastAPI App 運行中 | 1. GET 請求 `/health` | 無 | status code 200, JSON 包含 status: "healthy", agent: "data_analyst" |
| **API 端點** | **TC-API-002** | 測試數據集列表端點 | FastAPI App 運行中 | 1. GET 請求 `/datasets` | 無 | status code 200, JSON 包含 datasets 列表與 count |

## 模組導入 測試 (`tests/test_imports.py`)

此部分涵蓋對 專案依賴模組導入 的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **基礎導入** | **TC-IMPORT-001** | 測試代理模組是否正確導入 | 無 | 1. 導入 `agent` | 無 | `agent` 物件不為 None |
| **基礎導入** | **TC-IMPORT-002** | 測試 root_agent 是否可用 | 無 | 1. 導入 `root_agent` | 無 | `root_agent` 物件不為 None |
| **基礎導入** | **TC-IMPORT-003** | 測試 FastAPI 應用程序是否正確導入 | 無 | 1. 導入 `app` | 無 | `app` 物件不為 None |
| **依賴導入** | **TC-IMPORT-004** | 測試 ADK 依賴項是否可用 | 安裝 google-adk | 1. 導入 `google.adk.agents.Agent` | 無 | `Agent` 類別不為 None |
| **依賴導入** | **TC-IMPORT-005** | 測試 ag_ui_adk 是否可用 | 安裝 ag_ui_adk | 1. 導入 `ag_ui_adk` 相關物件 | 無 | `ADKAgent` 與 `add_adk_fastapi_endpoint` 不為 None |
| **依賴導入** | **TC-IMPORT-006** | 測試 pandas 是否可用 | 安裝 pandas | 1. 導入 `pandas` | 無 | `pandas` 模組不為 None |
| **依賴導入** | **TC-IMPORT-007** | 測試 FastAPI 是否可用 | 安裝 fastapi | 1. 導入 `fastapi.FastAPI` | 無 | `FastAPI` 類別不為 None |

## 專案結構 測試 (`tests/test_structure.py`)

此部分涵蓋對 專案目錄與檔案結構完整性 的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 結構** | **TC-STRUCT-001** | 測試 agent 目錄是否存在 | 無 | 1. 檢查 `agent` 目錄路徑 | 無 | 目錄存在且為目錄類型 |
| **Agent 結構** | **TC-STRUCT-002** | 測試 agent/__init__.py 是否存在 | 無 | 1. 檢查 `agent/__init__.py` 路徑 | 無 | 檔案存在且為檔案類型 |
| **Agent 結構** | **TC-STRUCT-003** | 測試 agent/agent.py 是否存在 | 無 | 1. 檢查 `agent/agent.py` 路徑 | 無 | 檔案存在且為檔案類型 |
| **專案設定** | **TC-STRUCT-004** | 測試 requirements.txt 是否存在 | 無 | 1. 檢查 `requirements.txt` 路徑 | 無 | 檔案存在且為檔案類型 |
| **專案設定** | **TC-STRUCT-005** | 測試 agent/requirements.txt 是否存在 | 無 | 1. 檢查 `agent/requirements.txt` 路徑 | 無 | 檔案存在且為檔案類型 |
| **專案設定** | **TC-STRUCT-006** | 測試 pyproject.toml 是否存在 | 無 | 1. 檢查 `pyproject.toml` 路徑 | 無 | 檔案存在且為檔案類型 |
| **專案設定** | **TC-STRUCT-007** | 測試 agent/.env.example 是否存在 | 無 | 1. 檢查 `agent/.env.example` 路徑 | 無 | 檔案存在且為檔案類型 |
| **測試結構** | **TC-STRUCT-008** | 測試 tests 目錄是否存在 | 無 | 1. 檢查 `tests` 目錄路徑 | 無 | 目錄存在且為目錄類型 |
| **Frontend 結構** | **TC-STRUCT-009** | 測試 frontend 目錄是否存在 | 無 | 1. 檢查 `frontend` 目錄路徑 | 無 | 目錄存在且為目錄類型 |
| **Frontend 結構** | **TC-STRUCT-010** | 測試 frontend/package.json 是否存在 | 無 | 1. 檢查 `frontend/package.json` 路徑 | 無 | 檔案存在且為檔案類型 |
| **Frontend 結構** | **TC-STRUCT-011** | 測試 frontend/vite.config.ts 是否存在 | 無 | 1. 檢查 `frontend/vite.config.ts` 路徑 | 無 | 檔案存在且為檔案類型 |
| **Frontend 結構** | **TC-STRUCT-012** | 測試 frontend/src 目錄是否存在 | 無 | 1. 檢查 `frontend/src` 目錄路徑 | 無 | 目錄存在且為目錄類型 |
| **Frontend 結構** | **TC-STRUCT-013** | 測試 frontend/src/App.tsx 是否存在 | 無 | 1. 檢查 `frontend/src/App.tsx` 路徑 | 無 | 檔案存在且為檔案類型 |
| **Frontend 結構** | **TC-STRUCT-014** | 測試 frontend/src/components 目錄是否存在 | 無 | 1. 檢查 `frontend/src/components` 目錄路徑 | 無 | 目錄存在且為目錄類型 |
| **Frontend 結構** | **TC-STRUCT-015** | 測試 ChartRenderer 組件是否存在 | 無 | 1. 檢查 `frontend/src/components/ChartRenderer.tsx` | 無 | 檔案存在且為檔案類型 |
| **Frontend 結構** | **TC-STRUCT-016** | 測試 DataTable 組件是否存在 | 無 | 1. 檢查 `frontend/src/components/DataTable.tsx` | 無 | 檔案存在且為檔案類型 |
