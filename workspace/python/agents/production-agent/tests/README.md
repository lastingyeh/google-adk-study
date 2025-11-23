# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Agent 設定與功能測試 (`tests/test_agent.py`)

此部分涵蓋對 Agent 設定、工具功能及整合測試的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 root_agent 是否已定義 | 無 | 驗證 `root_agent` 是否不為 None | None | root_agent 存在 |
| **Agent 設定** | **TC-AGENT-002** | 測試 Agent 是否有名稱正確 | 無 | 驗證 `root_agent.name` 是否為 "production_deployment_agent" | None | 名稱正確 |
| **Agent 設定** | **TC-AGENT-003** | 測試 Agent 是否使用正確的模型 | 無 | 驗證 `root_agent.model` 是否為 "gemini-2.0-flash" | None | 模型正確 |
| **Agent 設定** | **TC-AGENT-004** | 測試 Agent 是否有描述 | 無 | 驗證 `root_agent.description` 是否存在且長度大於 0 | None | 描述存在且不為空 |
| **Agent 設定** | **TC-AGENT-005** | 測試 Agent 是否有指令 | 無 | 驗證 `root_agent.instruction` 是否存在且長度大於 0 | None | 指令存在且不為空 |
| **Agent 設定** | **TC-AGENT-006** | 測試 Agent 是否有設定工具 | 無 | 驗證 `root_agent.tools` 是否存在且長度大於 0 | None | 工具列表存在且不為空 |
| **Agent 設定** | **TC-AGENT-007** | 測試 Agent 是否有生成設定 | 無 | 驗證 `root_agent.generate_content_config` 是否存在 | None | 生成設定存在 |
| **Agent 設定** | **TC-AGENT-008** | 測試是否已設定 temperature | 無 | 驗證 `config.temperature` 是否為 0.5 | None | temperature 為 0.5 |
| **Agent 設定** | **TC-AGENT-009** | 測試是否已設定 max_output_tokens | 無 | 驗證 `config.max_output_tokens` 是否為 2048 | None | max_output_tokens 為 2048 |
| **工具函式** | **TC-TOOL-001** | 測試 check_deployment_status 工具 | 無 | 呼叫 `check_deployment_status()` | None | 返回字典，狀態為 success，包含報告與特性 |
| **工具函式** | **TC-TOOL-002** | 測試 get_deployment_options 工具 | 無 | 呼叫 `get_deployment_options()` | None | 返回字典，狀態為 success，包含選項 (local, cloud_run, agent_engine, gke) |
| **工具函式** | **TC-TOOL-003** | 測試 get_best_practices 工具 | 無 | 呼叫 `get_best_practices()` | None | 返回字典，狀態為 success，包含各類別的最佳實踐 |
| **工具指令** | **TC-CMD-001** | 測試工具中的部署指令是否準確 | 無 | 檢查 `get_deployment_options()` 返回的指令 | None | 指令符合官方 ADK CLI |
| **工具指令** | **TC-CMD-002** | 測試每個部署選項是否有具體的特性 | 無 | 檢查 `get_deployment_options()` 返回的特性列表 | None | 每個選項至少有 3 個特性 |
| **Agent 整合** | **TC-INT-001** | 測試實際的 Agent 呼叫 | 設定 `GOOGLE_API_KEY` | 使用 `Runner` 執行對話查詢 "What deployment options are available?" | 查詢字串 | 收到非空的回應文字 |

## 導入測試 (`tests/test_imports.py`)

此部分涵蓋對模組導入及相依性的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **導入測試** | **TC-IMP-001** | 測試導入 agent 模組 | 無 | `from production_agent import agent` | None | 模組包含 `root_agent` |
| **導入測試** | **TC-IMP-002** | 測試直接導入 root_agent | 無 | `from production_agent import root_agent` | None | `root_agent` 不為 None |
| **導入測試** | **TC-IMP-003** | 測試導入 server 模組 | 無 | `from production_agent import server` | None | 模組包含 `app` |
| **導入測試** | **TC-IMP-004** | 測試必要的 Google ADK 導入是否正常運作 | 無 | 嘗試導入 Google ADK 相關模組 | None | 導入成功無錯誤 |
| **導入測試** | **TC-IMP-005** | 測試 FastAPI 導入是否正常運作 | 無 | 嘗試導入 FastAPI 相關模組 | None | 導入成功無錯誤 |
| **導入測試** | **TC-IMP-006** | 測試工具函式是否已定義 | 無 | 從 `production_agent.agent` 導入工具函式 | None | 函式可被呼叫 |

## FastAPI 伺服器測試 (`tests/test_server.py`)

此部分涵蓋對 FastAPI 伺服器端點、設定及模型的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **伺服器端點** | **TC-SRV-001** | 測試根端點 | Client 初始化 | GET `/` | None | Status 200, 返回包含 message 和 endpoints 的 JSON |
| **伺服器端點** | **TC-SRV-002** | 測試健康檢查端點 | Client 初始化 | GET `/health` | None | Status 200, 狀態為 healthy, 包含 Agent 資訊 |
| **伺服器端點** | **TC-SRV-003** | 測試 OpenAPI 文件是否可用 | Client 初始化 | GET `/docs` | None | Status 200 |
| **伺服器端點** | **TC-SRV-004** | 測試 OpenAPI 架構是否可用 | Client 初始化 | GET `/openapi.json` | None | Status 200, 返回有效的 OpenAPI schema |
| **伺服器設定** | **TC-SRV-005** | 測試 CORS 中介軟體是否已設定 | 無 | 檢查 `app.user_middleware` | None | 包含 CORS middleware |
| **伺服器設定** | **TC-SRV-006** | 測試應用程式是否有正確的標題 | 無 | 檢查 `app.title` | None | 標題為 "ADK Production Deployment API" |
| **伺服器設定** | **TC-SRV-007** | 測試應用程式是否有版本 | 無 | 檢查 `app.version` | None | 版本為 "1.0" |
| **請求模型** | **TC-MODEL-001** | 測試 QueryRequest 模型 | 無 | 建立 `QueryRequest` 物件 | 預設或自定義參數 | 屬性值正確設定 |
| **請求模型** | **TC-MODEL-002** | 測試 QueryResponse 模型 | 無 | 建立 `QueryResponse` 物件 | 回應資料 | 屬性值正確設定 |
| **指標追蹤** | **TC-METRIC-001** | 測試請求計數器是否增加 | Client 初始化 | 多次呼叫 `/health` | None | `request_count` 增加 |
| **指標追蹤** | **TC-METRIC-002** | 測試是否追蹤正常運行時間 | Client 初始化 | 呼叫 `/health` | None | `uptime_seconds` >= 0 |
| **呼叫端點** | **TC-INVOKE-001** | 測試呼叫端點是否接受 POST 請求 | Client 初始化 | POST `/invoke` | 有效的請求 Body | Status 200 或 500 (視 API Key 而定) |
| **呼叫端點** | **TC-INVOKE-002** | 測試呼叫端點是否需要查詢欄位 | Client 初始化 | POST `/invoke` | 缺少 query 的 Body | Status 422 (Validation Error) |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案檔案結構及設定檔的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRUCT-001** | 測試所有必要檔案是否存在 | 無 | 檢查專案根目錄下的檔案列表 | 預定義的檔案列表 | 所有檔案皆存在 |
| **專案結構** | **TC-STRUCT-002** | 測試必要目錄是否存在 | 無 | 檢查專案根目錄下的目錄列表 | 預定義的目錄列表 | 所有目錄皆存在 |
| **專案結構** | **TC-STRUCT-003** | 測試 .env.example 格式是否正確 | 無 | 讀取 `.env.example` 內容 | None | 包含必要的環境變數定義 |
| **專案結構** | **TC-STRUCT-004** | 測試 requirements.txt 是否包含必要的套件 | 無 | 讀取 `requirements.txt` 內容 | None | 包含關鍵套件 (google-genai, fastapi 等) |
| **專案結構** | **TC-STRUCT-005** | 測試 pyproject.toml 是否正確設定 | 無 | 讀取 `pyproject.toml` 內容 | None | 包含 [project] 區段及正確名稱 |
| **專案結構** | **TC-STRUCT-006** | 測試 Makefile 是否有必要的目標 | 無 | 讀取 `Makefile` 內容 | None | 包含 setup, dev, test 等目標 |
