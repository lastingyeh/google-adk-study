# Observability Plugins Agent 詳細測試案例說明

## 簡介

此文件提供 Observability Plugins Agent 專案的詳細測試案例說明。此專案包含多個測試模組，旨在驗證 Agent 設定、Plugin 功能、匯入機制以及專案結構的正確性。

## Agent 設定與功能測試 (`tests/test_agent.py`)

此部分涵蓋 Agent 的基本設定、模型配置以及描述說明功能的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent Config** | **TC-AGENT-001** | 測試 Agent 是否擁有正確的名稱 | Agent 已被實例化 | 1. 檢查 `root_agent.name` | None | 名稱應為 "observability_plugins_agent" |
| **Agent Config** | **TC-AGENT-002** | 測試 Agent 是否使用正確的模型 | Agent 已被實例化 | 1. 檢查 `root_agent.model` | None | 模型應為 "gemini-2.5-flash" |
| **Agent Config** | **TC-AGENT-003** | 測試 Agent 是否有描述說明 | Agent 已被實例化 | 1. 檢查 `root_agent.description` | None | 描述中應包含 "observability" 或 "monitoring" 以及 "production" |
| **Agent Config** | **TC-AGENT-004** | 測試 Agent 是否有完整的指令說明 | Agent 已被實例化 | 1. 檢查 `root_agent.instruction` | None | 指令中應包含 "production" 或 "assistant" 以及 "helpful" |
| **Agent Config** | **TC-AGENT-005** | 測試 Agent 是否有生成配置 | Agent 已被實例化 | 1. 檢查 `root_agent.generate_content_config` | None | 配置不為空，且 temperature=0.5, max_output_tokens=1024 |

## 匯入機制測試 (`tests/test_imports.py`)

此部分驗證所有必要的外部套件與內部模組是否能正確匯入。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Imports** | **TC-IMPORT-001** | 測試 Google ADK 相關模組匯入是否正常 | 已安裝 Google ADK | 1. 嘗試匯入 ADK 核心模組 | None | 無 ImportError 且匯入成功 |
| **Imports** | **TC-IMPORT-002** | 測試 Google GenAI 相關模組匯入是否正常 | 已安裝 Google GenAI | 1. 嘗試匯入 GenAI 模組<br>2. 建立 Part 物件 | None | 無 ImportError 且 Part 物件建立成功 |
| **Imports** | **TC-IMPORT-003** | 測試 Agent 模組匯入是否正常 | 專案結構正確 | 1. 匯入 `root_agent` | None | Agent 物件存在且名稱正確 |
| **Imports** | **TC-IMPORT-004** | 測試 Plugin 類別匯入是否正常 | 專案結構正確 | 1. 匯入各 Plugin 類別 | None | Plugin 類別可被匯入且可呼叫 |
| **Imports** | **TC-IMPORT-005** | 測試資料類別 (Dataclasses) 匯入是否正常 | 專案結構正確 | 1. 匯入 Metrics 相關資料類別 | None | 資料類別匯入成功 |

## 外掛程式 (Plugin) 功能測試 (`tests/test_plugins.py`)

此部分涵蓋各個監控與指標外掛程式的功能驗證，包括 MetricsCollectorPlugin, AlertingPlugin, PerformanceProfilerPlugin 以及相關資料類別。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Data Classes** | **TC-PLUGIN-001** | 測試 RequestMetrics 可以被建立 | 無 | 1. 實例化 `RequestMetrics` | id="test-001", agent="test_agent" | 屬性值設定正確，預設 success 為 True |
| **Data Classes** | **TC-PLUGIN-002** | 測試 AggregateMetrics 可以被建立 | 無 | 1. 實例化 `AggregateMetrics` | None | 所有計數器與指標初始化為 0 或 0.0 |
| **Data Classes** | **TC-PLUGIN-003** | 測試 AggregateMetrics 成功率計算 | 無 | 1. 設定 total/successful/failed requests<br>2. 檢查 `success_rate` | total=10, success=8, failed=2 | 成功率應為 0.8 |
| **Data Classes** | **TC-PLUGIN-004** | 測試 AggregateMetrics 平均延遲計算 | 無 | 1. 設定 total requests 和 total latency<br>2. 檢查 `avg_latency` | total=5, latency=10.0 | 平均延遲應為 2.0 |
| **Data Classes** | **TC-PLUGIN-005** | 測試 AggregateMetrics 平均 Tokens 計算 | 無 | 1. 設定 total requests 和 total tokens<br>2. 檢查 `avg_tokens` | total=4, tokens=400 | 平均 Tokens 應為 100.0 |
| **Metrics Plugin** | **TC-PLUGIN-006** | 測試 MetricsCollectorPlugin 初始化 | 無 | 1. 實例化 `MetricsCollectorPlugin` | None | metrics 為 AggregateMetrics 實例，current_requests 為空字典 |
| **Metrics Plugin** | **TC-PLUGIN-007** | 測試 MetricsCollectorPlugin 摘要輸出 | Plugin 已初始化 | 1. 呼叫 `get_summary()` | None | 回傳字串包含 "METRICS SUMMARY", "Total Requests", "Success Rate" |
| **Alerting Plugin** | **TC-PLUGIN-008** | 測試 AlertingPlugin 初始化 | 無 | 1. 實例化 `AlertingPlugin` | None | 使用預設閾值 (latency=5.0, error=3) |
| **Alerting Plugin** | **TC-PLUGIN-009** | 測試 AlertingPlugin 自訂閾值初始化 | 無 | 1. 實例化 `AlertingPlugin` 帶參數 | latency=3.0, error=2 | 使用設定的閾值初始化 |
| **Profiler Plugin** | **TC-PLUGIN-010** | 測試 PerformanceProfilerPlugin 初始化 | 無 | 1. 實例化 `PerformanceProfilerPlugin` | None | profiles 列表為空，current_profile 為 None |
| **Profiler Plugin** | **TC-PLUGIN-011** | 測試無資料時的 Profiler 摘要 | Plugin 已初始化 | 1. 呼叫 `get_profile_summary()` | None | 回傳字串包含 "No profiles collected" |
| **Profiler Plugin** | **TC-PLUGIN-012** | 測試 Profiler 資料結構操作 | Plugin 已初始化 | 1. 新增 profile 資料到 `profiles` 列表 | tool='test_tool', duration=1.0 | profiles 列表長度為 1，資料內容正確 |
| **Integration** | **TC-PLUGIN-013** | 測試所有 Plugin 可以一起被建立 | 無 | 1. 建立所有 Plugin 的實例列表 | None | 3 個 Plugin 實例皆建立成功 |
| **Integration** | **TC-PLUGIN-014** | 測試所有 Plugin 都繼承自 BasePlugin | ADK BasePlugin 可用 | 1. 檢查每個 Plugin 是否為 `BasePlugin` 的實例 | None | 所有 Plugin 皆繼承自 BasePlugin |

## 專案結構測試 (`tests/test_structure.py`)

此部分驗證專案的目錄結構、必要檔案存在性以及設定檔格式。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Structure** | **TC-STRUCT-001** | 測試專案根目錄是否存在 | 測試檔案位置正確 | 1. 檢查專案根路徑 | None | 目錄存在且為目錄類型 |
| **Structure** | **TC-STRUCT-002** | 測試主要套件目錄是否存在 | 根目錄存在 | 1. 檢查 `observability_plugins_agent` 目錄 | None | 目錄存在且為目錄類型 |
| **Structure** | **TC-STRUCT-003** | 測試 `__init__.py` 檔案是否存在 | 各目錄存在 | 1. 檢查套件和測試目錄下的 init 檔 | None | 檔案存在 |
| **Structure** | **TC-STRUCT-004** | 測試主要程式檔 `agent.py` 是否存在 | 套件目錄存在 | 1. 檢查 `agent.py` | None | 檔案存在且為檔案類型 |
| **Structure** | **TC-STRUCT-005** | 測試必要設定檔是否存在 | 根目錄存在 | 1. 檢查 toml, requirements, Makefile, .env.example | None | 所有列出的檔案皆存在 |
| **Structure** | **TC-STRUCT-006** | 測試 README.md 是否存在 | 根目錄存在 | 1. 檢查 `README.md` | None | 檔案存在 |
| **Structure** | **TC-STRUCT-007** | 測試 .env 檔案管理 | 根目錄存在 | 1. 檢查 `.env.example` 存在<br>2. 檢查 `.env` 是否被提交 | None | .env.example 存在，.env 不應存在 (CI/CD 環境) |
| **Structure** | **TC-STRUCT-008** | 測試 Makefile 可讀性 | Makefile 存在 | 1. 檢查檔案權限 | None | 檔案可被讀取 |
| **Structure** | **TC-STRUCT-009** | 測試 requirements.txt 內容格式 | 檔案存在 | 1. 讀取並解析檔案內容 | None | 不為空，包含 google-genai 和 google-adk |
| **Structure** | **TC-STRUCT-010** | 測試 pyproject.toml 內容格式 | 檔案存在 | 1. 讀取並檢查必要區段 | None | 包含 build-system, project 區段及正確依賴 |
