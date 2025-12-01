# 詳細測試案例文件

## 簡介

此文件提供 `workspace/python/agents/customer-support-agent` 專案的詳細測試案例說明。這些測試涵蓋了專案結構、模組匯入、代理配置、工具函式以及 FastAPI 應用程式配置。

## 代理結構與配置測試 (`tests/test_agent.py`)

此部分涵蓋對代理程式結構、檔案存在性、模組匯入、代理配置及工具定義的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRUCT-001** | 測試 agent 目錄是否存在 | 專案根目錄存在 | 檢查 `agent` 目錄是否存在 | 無 | 目錄存在 |
| **專案結構** | **TC-STRUCT-002** | 測試 agent.py 是否存在 | 專案根目錄存在 | 檢查 `agent/agent.py` 是否存在 | 無 | 檔案存在 |
| **專案結構** | **TC-STRUCT-003** | 測試 \_\_init\_\_.py 是否存在 | 專案根目錄存在 | 檢查 `agent/__init__.py` 是否存在 | 無 | 檔案存在 |
| **專案結構** | **TC-STRUCT-004** | 測試 .env.example 是否存在 | 專案根目錄存在 | 檢查 `agent/.env.example` 是否存在 | 無 | 檔案存在 |
| **專案結構** | **TC-STRUCT-005** | 測試 requirements.txt 是否存在 | 專案根目錄存在 | 檢查 `requirements.txt` 是否存在 | 無 | 檔案存在 |
| **專案結構** | **TC-STRUCT-006** | 測試 pyproject.toml 是否存在 | 專案根目錄存在 | 檢查 `pyproject.toml` 是否存在 | 無 | 檔案存在 |
| **專案結構** | **TC-STRUCT-007** | 測試 Next.js 前端目錄是否存在 | 專案根目錄存在 | 檢查 `nextjs_frontend` 目錄是否存在 | 無 | 目錄存在 |
| **代理匯入** | **TC-IMPORT-001** | 測試 agent 模組是否可以匯入 | 依賴已安裝 | 嘗試匯入 `agent` 模組 | 無 | 匯入成功 |
| **代理匯入** | **TC-IMPORT-002** | 測試 root_agent 是否從 agent 模組匯出 | 依賴已安裝 | 從 `agent.agent` 匯入 `root_agent` | 無 | `root_agent` 存在且具有 `name` 屬性 |
| **代理匯入** | **TC-IMPORT-003** | 測試 FastAPI 應用程式是否匯出 | 依賴已安裝 | 從 `agent.agent` 匯入 `app` | 無 | `app` 存在且具有 `title` 屬性 |
| **代理配置** | **TC-CONFIG-001** | 測試 agent 是否有正確的名稱 | 依賴已安裝 | 檢查 `root_agent.name` | 無 | 名稱為 "customer_support_agent" |
| **代理配置** | **TC-CONFIG-002** | 測試 agent 是否配置了工具 | 依賴已安裝 | 檢查 `root_agent.tools` | 無 | 工具列表存在且不為空 |
| **代理配置** | **TC-CONFIG-003** | 測試 agent 是否配置了指令 | 依賴已安裝 | 檢查 `root_agent.instruction` | 無 | 指令存在且不為空 |
| **代理配置** | **TC-CONFIG-004** | 測試 agent 是否配置了模型 | 依賴已安裝 | 檢查 `root_agent.model` | 無 | 模型配置存在 |
| **工具定義** | **TC-TOOLDEF-001** | 測試 search_knowledge_base 函式是否存在 | 依賴已安裝 | 檢查 `search_knowledge_base` 是否可呼叫 | 無 | 函式存在且可呼叫 |
| **工具定義** | **TC-TOOLDEF-002** | 測試 lookup_order_status 函式是否存在 | 依賴已安裝 | 檢查 `lookup_order_status` 是否可呼叫 | 無 | 函式存在且可呼叫 |
| **工具定義** | **TC-TOOLDEF-003** | 測試 create_support_ticket 函式是否存在 | 依賴已安裝 | 檢查 `create_support_ticket` 是否可呼叫 | 無 | 函式存在且可呼叫 |
| **工具定義** | **TC-TOOLDEF-004** | 測試 search_knowledge_base 是否回傳字典 | 依賴已安裝 | 呼叫 `search_knowledge_base("refund policy")` | "refund policy" | 回傳字典包含 "status" 和 "report" |
| **工具定義** | **TC-TOOLDEF-005** | 測試 lookup_order_status 是否回傳字典 | 依賴已安裝 | 呼叫 `lookup_order_status("ORD-12345")` | "ORD-12345" | 回傳字典包含 "status" 和 "report" |
| **工具定義** | **TC-TOOLDEF-006** | 測試 create_support_ticket 是否回傳字典 | 依賴已安裝 | 呼叫 `create_support_ticket("Test issue", "normal")` | "Test issue", "normal" | 回傳字典包含 "status", "report", "ticket" |
| **FastAPI配置** | **TC-FASTAPI-001** | 測試應用程式是否有標題 | 依賴已安裝 | 檢查 `app.title` | 無 | 標題為 "Customer Support Agent API" |
| **FastAPI配置** | **TC-FASTAPI-002** | 測試應用程式是否有健康檢查端點 | 依賴已安裝 | 檢查 `app.routes` | 無 | 包含 "/health" 端點 |
| **FastAPI配置** | **TC-FASTAPI-003** | 測試應用程式是否有 copilotkit 端點 | 依賴已安裝 | 檢查 `app.routes` | 無 | 包含 "/api/copilotkit" 端點 |

## 模組匯入測試 (`tests/test_imports.py`)

此部分涵蓋對專案所需模組匯入的測試，確保所有依賴項已正確安裝且可被引用。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組匯入** | **TC-MODIMP-001** | 測試匯入 agent 模組 | 依賴已安裝 | `import agent` | 無 | 匯入成功 |
| **模組匯入** | **TC-MODIMP-002** | 測試匯入 agent.agent | 依賴已安裝 | `from agent import agent as agent_module` | 無 | 匯入成功 |
| **模組匯入** | **TC-MODIMP-003** | 測試匯入 fastapi | 依賴已安裝 | `import fastapi` | 無 | 匯入成功 |
| **模組匯入** | **TC-MODIMP-004** | 測試匯入 uvicorn | 依賴已安裝 | `import uvicorn` | 無 | 匯入成功 |
| **模組匯入** | **TC-MODIMP-005** | 測試匯入 google.adk | 依賴已安裝 | `import google.adk` | 無 | 匯入成功 |
| **模組匯入** | **TC-MODIMP-006** | 測試匯入 google.adk.agents | 依賴已安裝 | `from google.adk.agents import Agent` | 無 | 匯入成功 |
| **模組匯入** | **TC-MODIMP-007** | 測試匯入 ag_ui_adk | 依賴已安裝 | `import ag_ui_adk` | 無 | 匯入成功 |
| **模組匯入** | **TC-MODIMP-008** | 測試匯入 dotenv | 依賴已安裝 | `import dotenv` | 無 | 匯入成功 |

## 專案結構測試 (`tests/test_structure.py`)

此部分詳細檢查專案的目錄結構和必要檔案是否存在，以及部分檔案的內容是否符合預期。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-PSTRUCT-001** | 測試 agent 目錄是否存在 | 無 | 檢查 `agent` 目錄 | 無 | 目錄存在 |
| **專案結構** | **TC-PSTRUCT-002** | 測試 tests 目錄是否存在 | 無 | 檢查 `tests` 目錄 | 無 | 目錄存在 |
| **專案結構** | **TC-PSTRUCT-003** | 測試 nextjs_frontend 目錄是否存在 | 無 | 檢查 `nextjs_frontend` 目錄 | 無 | 目錄存在 |
| **專案結構** | **TC-PSTRUCT-004** | 測試 agent/__init__.py 是否存在 | 無 | 檢查 `agent/__init__.py` 檔案 | 無 | 檔案存在 |
| **專案結構** | **TC-PSTRUCT-005** | 測試 agent/agent.py 是否存在 | 無 | 檢查 `agent/agent.py` 檔案 | 無 | 檔案存在 |
| **專案結構** | **TC-PSTRUCT-006** | 測試 agent/.env.example 是否存在 | 無 | 檢查 `agent/.env.example` 檔案 | 無 | 檔案存在 |
| **專案結構** | **TC-PSTRUCT-007** | 測試 requirements.txt 是否存在 | 無 | 檢查 `requirements.txt` 檔案 | 無 | 檔案存在 |
| **專案結構** | **TC-PSTRUCT-008** | 測試 pyproject.toml 是否存在 | 無 | 檢查 `pyproject.toml` 檔案 | 無 | 檔案存在 |
| **專案結構** | **TC-PSTRUCT-009** | 測試 Makefile 是否存在 | 無 | 檢查 `Makefile` 檔案 | 無 | 檔案存在 |
| **專案結構** | **TC-PSTRUCT-010** | 測試 README.md 是否存在 | 無 | 檢查 `README.md` 檔案 | 無 | 檔案存在 |
| **專案結構** | **TC-PSTRUCT-011** | 測試 nextjs_frontend/package.json 是否存在 | 無 | 檢查 `nextjs_frontend/package.json` 檔案 | 無 | 檔案存在 |
| **專案結構** | **TC-PSTRUCT-012** | 測試 nextjs_frontend/app 目錄是否存在 | 無 | 檢查 `nextjs_frontend/app` 目錄 | 無 | 目錄存在 |
| **專案結構** | **TC-PSTRUCT-013** | 測試 nextjs_frontend/app/page.tsx 是否存在 | 無 | 檢查 `nextjs_frontend/app/page.tsx` 檔案 | 無 | 檔案存在 |
| **專案結構** | **TC-PSTRUCT-014** | 測試 nextjs_frontend/app/layout.tsx 是否存在 | 無 | 檢查 `nextjs_frontend/app/layout.tsx` 檔案 | 無 | 檔案存在 |
| **需求內容** | **TC-REQCONT-001** | 測試 requirements.txt 是否包含 google-adk | `requirements.txt` 存在 | 讀取檔案內容並檢查 "google-adk" | 無 | 內容包含 "google-adk" |
| **需求內容** | **TC-REQCONT-002** | 測試 requirements.txt 是否包含 fastapi | `requirements.txt` 存在 | 讀取檔案內容並檢查 "fastapi" | 無 | 內容包含 "fastapi" |
| **需求內容** | **TC-REQCONT-003** | 測試 requirements.txt 是否包含 uvicorn | `requirements.txt` 存在 | 讀取檔案內容並檢查 "uvicorn" | 無 | 內容包含 "uvicorn" |
| **需求內容** | **TC-REQCONT-004** | 測試 requirements.txt 是否包含 ag-ui-adk | `requirements.txt` 存在 | 讀取檔案內容並檢查 "ag-ui-adk" | 無 | 內容包含 "ag-ui-adk" |
| **環境範例** | **TC-ENVEX-001** | 測試 .env.example 是否提及 GOOGLE_API_KEY | `agent/.env.example` 存在 | 讀取檔案內容並檢查 "GOOGLE_API_KEY" | 無 | 內容包含 "GOOGLE_API_KEY" |
| **環境範例** | **TC-ENVEX-002** | 測試 .env.example 是否不包含真實的 API 金鑰 | `agent/.env.example` 存在 | 檢查 GOOGLE_API_KEY 的值是否為佔位符 | 無 | 值為佔位符 (e.g., "your", "placeholder") |

## 工具功能測試 (`tests/test_tools.py`)

此部分涵蓋對代理程式所使用的各種工具函式的詳細功能測試，包括知識庫搜尋、訂單查詢、工單建立、產品卡片生成及退款處理。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **知識庫搜尋** | **TC-KB-001** | 測試搜尋退款政策 | 依賴已安裝 | 呼叫 `search_knowledge_base("refund policy")` | "refund policy" | 狀態成功，標題包含 "Refund" |
| **知識庫搜尋** | **TC-KB-002** | 測試搜尋運送資訊 | 依賴已安裝 | 呼叫 `search_knowledge_base("shipping")` | "shipping" | 狀態成功，標題包含 "Shipping" |
| **知識庫搜尋** | **TC-KB-003** | 測試搜尋保固資訊 | 依賴已安裝 | 呼叫 `search_knowledge_base("warranty")` | "warranty" | 狀態成功，標題包含 "Warranty" |
| **知識庫搜尋** | **TC-KB-004** | 測試未知查詢返回一般支援 | 依賴已安裝 | 呼叫 `search_knowledge_base("some unknown query")` | "some unknown query" | 狀態成功，標題包含 "Support" |
| **訂單查詢** | **TC-ORDER-001** | 測試查詢有效訂單 | 依賴已安裝 | 呼叫 `lookup_order_status("ORD-12345")` | "ORD-12345" | 狀態成功，包含正確的 order_id |
| **訂單查詢** | **TC-ORDER-002** | 測試查詢無效訂單 | 依賴已安裝 | 呼叫 `lookup_order_status("ORD-99999")` | "ORD-99999" | 狀態錯誤 |
| **訂單查詢** | **TC-ORDER-003** | 測試訂單 ID 查詢不分大小寫 | 依賴已安裝 | 呼叫 `lookup_order_status("ord-12345")` | "ord-12345" | 狀態成功 |
| **工單建立** | **TC-TICKET-001** | 測試建立普通優先級工單 | 依賴已安裝 | 呼叫 `create_support_ticket("Test issue", "normal")` | "Test issue", "normal" | 狀態成功，優先級 "normal" |
| **工單建立** | **TC-TICKET-002** | 測試建立緊急優先級工單 | 依賴已安裝 | 呼叫 `create_support_ticket("Urgent issue", "urgent")` | "Urgent issue", "urgent" | 狀態成功，優先級 "urgent"，預估回應 "1-2 hours" |
| **工單建立** | **TC-TICKET-003** | 測試建立預設優先級工單 | 依賴已安裝 | 呼叫 `create_support_ticket("Test issue")` | "Test issue" | 狀態成功，優先級 "normal" |
| **工單建立** | **TC-TICKET-004** | 測試工單 ID 格式是否正確 | 依賴已安裝 | 檢查回傳的 `ticket_id` | 無 | ID 以 "TICKET-" 開頭 |
| **產品卡片** | **TC-PCARD-001** | 測試為有效產品建立產品卡片 | 依賴已安裝 | 呼叫 `create_product_card("PROD-001")` | "PROD-001" | 狀態成功，包含正確產品資訊，組件為 "ProductCard" |
| **產品卡片** | **TC-PCARD-002** | 測試為所有可用產品建立產品卡片 | 依賴已安裝 | 對多個 ID 呼叫 `create_product_card` | ["PROD-001", "PROD-002", "PROD-003"] | 所有呼叫皆成功且包含必要欄位 |
| **產品卡片** | **TC-PCARD-003** | 測試為無效產品建立產品卡片 | 依賴已安裝 | 呼叫 `create_product_card("PROD-999")` | "PROD-999" | 狀態錯誤 |
| **產品卡片** | **TC-PCARD-004** | 測試產品 ID 查詢不分大小寫 | 依賴已安裝 | 呼叫 `create_product_card("prod-001")` | "prod-001" | 狀態成功 |
| **退款處理** | **TC-REFUND-001** | 測試成功處理退款 | 依賴已安裝 | 呼叫 `process_refund("ORD-12345", 99.99, "Product defective")` | "ORD-12345", 99.99, "Product defective" | 狀態成功，包含正確退款資訊 |
| **退款處理** | **TC-REFUND-002** | 測試退款 ID 格式是否正確 | 依賴已安裝 | 檢查回傳的 `refund_id` | 無 | ID 以 "REF-" 開頭 |
| **退款處理** | **TC-REFUND-003** | 測試退款回應包含所有必要欄位 | 依賴已安裝 | 檢查回傳的 `refund` 物件 | 無 | 包含所有必要欄位 (refund_id, order_id, etc.) |
| **退款處理** | **TC-REFUND-004** | 測試處理不同金額的退款 | 依賴已安裝 | 對不同金額呼叫 `process_refund` | [10.50, 99.99, 299.99, 1000.00] | 狀態成功，金額正確 |
