# 測試案例說明

## Agent 測試 (`tests/test_agent.py`)

此部分涵蓋對 Agent 設定與工具功能的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 root_agent 是否可以被匯入 | `model_selector.agent` 模組存在 | 1. 從 `model_selector.agent` 匯入 `root_agent` | `None` | `root_agent` 不為 `None` |
| **Agent 設定** | **TC-AGENT-002** | 測試 root_agent 是否為 Agent 的一個實例 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent` 的類型 | `None` | `root_agent` 是 `google.adk.agents.Agent` 的實例 |
| **Agent 設定** | **TC-AGENT-003** | 測試 Agent 是否有正確的名稱 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.name` 屬性 | `None` | `root_agent.name` 的值為 "model_selector_agent" |
| **Agent 設定** | **TC-AGENT-004** | 測試 Agent 是否使用建議的模型 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.model` 屬性 | `None` | `root_agent.model` 的值為 "gemini-1.5-flash" |
| **Agent 設定** | **TC-AGENT-005** | 測試 Agent 是否有描述 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.description` 屬性 | `None` | `root_agent.description` 包含 "model selection" 或 "selecting" |
| **Agent 設定** | **TC-AGENT-006** | 測試 Agent 是否有完整的指令 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.instruction` 屬性 | `None` | `root_agent.instruction` 包含 "model selection", "recommend", "gemini" |
| **Agent 設定** | **TC-AGENT-007** | 測試 Agent 是否已設定工具 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.tools` 屬性 | `None` | `root_agent.tools` 的長度大於 0 |
| **Agent 設定** | **TC-AGENT-008** | 測試 Agent 是否有預期數量的工具 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.tools` 的長度 | `None` | `root_agent.tools` 的長度為 2 |
| **工具功能** | **TC-TOOL-001** | 測試即時用例的模型推薦 | `None` | 1. 呼叫 `recommend_model_for_use_case` 函式 | `use_case`: "real-time voice assistant" | 返回成功的狀態與推薦的模型 "gemini-1.5-flash-1.5t" |
| **工具功能** | **TC-TOOL-002** | 測試複雜推理的模型推薦 | `None` | 1. 呼叫 `recommend_model_for_use_case` 函式 | `use_case`: "complex strategic planning" | 返回成功的狀態與推薦的模型 "gemini-1.5-pro" |
| **工具功能** | **TC-TOOL-003** | 測試高流量簡單任務的模型推薦 | `None` | 1. 呼叫 `recommend_model_for_use_case` 函式 | `use_case`: "high-volume content moderation" | 返回成功的狀態與推薦的模型 "gemini-1.5-flash-1.5t" |
| **工具功能** | **TC-TOOL-004** | 測試關鍵操作的模型推薦 | `None` | 1. 呼叫 `recommend_model_for_use_case` 函式 | `use_case`: "critical business operations" | 返回成功的狀態與推薦的模型 "gemini-1.5-pro" |
| **工具功能** | **TC-TOOL-005** | 測試一般用例的模型推薦 | `None` | 1. 呼叫 `recommend_model_for_use_case` 函式 | `use_case`: "general customer service" | 返回成功的狀態與推薦的模型 "gemini-1.5-flash" |
| **工具功能** | **TC-TOOL-006** | 測試大型文件的模型推薦 | `None` | 1. 呼叫 `recommend_model_for_use_case` 函式 | `use_case`: "extended context document analysis" | 返回成功的狀態與推薦的模型 "gemini-1.5-pro-2m" |
| **工具功能** | **TC-TOOL-007** | 測試獲取 gemini-1.5-flash 的資訊 | `None` | 1. 呼叫 `get_model_info` 函式 | `model_name`: "gemini-1.5-flash" | 返回成功的狀態與 "gemini-1.5-flash" 的模型資訊 |
| **工具功能** | **TC-TOOL-008** | 測試獲取 gemini-1.5-pro 的資訊 | `None` | 1. 呼叫 `get_model_info` 函式 | `model_name`: "gemini-1.5-pro" | 返回成功的狀態與 "gemini-1.5-pro" 的模型資訊 |
| **工具功能** | **TC-TOOL-009** | 測試獲取 gemini-1.5-flash-1.5t 的資訊 | `None` | 1. 呼叫 `get_model_info` 函式 | `model_name`: "gemini-1.5-flash-1.5t" | 返回成功的狀態與 "gemini-1.5-flash-1.5t" 的模型資訊 |
| **工具功能** | **TC-TOOL-010** | 測試獲取不存在模型的資訊 | `None` | 1. 呼叫 `get_model_info` 函式 | `model_name`: "nonexistent-model" | 返回錯誤的狀態與 "not found" 的報告 |
| **ModelSelector** | **TC-MODSEL-001** | 測試 ModelSelector 是否可以被建立 | `None` | 1. 建立 `ModelSelector` 的實例 | `None` | `ModelSelector` 的實例不為 `None` 且有 `benchmarks` 屬性 |
| **ModelSelector** | **TC-MODSEL-002** | 測試 benchmarks dict 是否初始化為空 | `None` | 1. 建立 `ModelSelector` 的實例並檢查 `benchmarks` | `None` | `benchmarks` 是一個空的字典 |
| **ModelBenchmark** | **TC-MODBENCH-001** | 測試 ModelBenchmark 是否可以被建立 | `None` | 1. 建立 `ModelBenchmark` 的實例 | `model`: "gemini-1.5-flash", `avg_latency`: 1.5, `avg_tokens`: 100, `quality_score`: 0.8, `cost_estimate`: 0.0001, `success_rate`: 1.0 | `ModelBenchmark` 的實例被成功建立且屬性正確 |
| **整合測試** | **TC-INT-001** | 測試 Agent 是否可以在不引發例外的情況下被建立 | `None` | 1. 匯入 `root_agent` | `None` | 沒有引發任何例外 |
| **整合測試** | **TC-INT-002** | 測試工具是否具有 tool_context 參數 | `None` | 1. 檢查 `recommend_model_for_use_case` 的簽名<br>2. 檢查 `get_model_info` 的簽名 | `None` | 兩個函式的簽名中都包含 `tool_context` |
| **整合測試** | **TC-INT-003** | 測試工具是否返回字典 | `None` | 1. 呼叫 `recommend_model_for_use_case` 函式<br>2. 呼叫 `get_model_info` 函式 | `use_case`: "test use case", `model_name`: "gemini-1.5-flash" | 兩個函式都返回字典 |

## 匯入測試 (`tests/test_imports.py`)

此部分涵蓋對所有必要匯入是否能正常運作的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入測試** | **TC-IMPORT-001** | 測試我們是否可以從 google.adk.agents 匯入 Agent | `None` | 1. 嘗試從 `google.adk.agents` 匯入 `Agent` | `None` | 成功匯入 `Agent` |
| **匯入測試** | **TC-IMPORT-002** | 測試我們是否可以從 google.adk.runners 匯入 Runner | `None` | 1. 嘗試從 `google.adk.runners` 匯入 `Runner` | `None` | 成功匯入 `Runner` |
| **匯入測試** | **TC-IMPORT-003** | 測試我們是否可以從 google.genai 匯入 types | `None` | 1. 嘗試從 `google.genai` 匯入 `types` | `None` | 成功匯入 `types` |
| **匯入測試** | **TC-IMPORT-004** | 測試我們是否可以匯入 ToolContext | `None` | 1. 嘗試匯入 `ToolContext` | `None` | 成功匯入 `ToolContext` |
| **匯入測試** | **TC-IMPORT-005** | 測試我們是否可以匯入 model_selector 模組 | `None` | 1. 嘗試匯入 `model_selector` | `None` | 成功匯入 `model_selector` |
| **匯入測試** | **TC-IMPORT-006** | 測試我們是否可以從 model_selector 匯入 agent 模組 | `None` | 1. 嘗試從 `model_selector` 匯入 `agent` | `None` | 成功匯入 `agent` |
| **匯入測試** | **TC-IMPORT-007** | 測試 root_agent 是否在 agent 模組中被定義 | `None` | 1. 嘗試從 `model_selector.agent` 匯入 `root_agent` | `None` | 成功匯入 `root_agent` |
| **匯入測試** | **TC-IMPORT-008** | 測試 ModelSelector 類別是否可以被匯入 | `None` | 1. 嘗試從 `model_selector.agent` 匯入 `ModelSelector` | `None` | 成功匯入 `ModelSelector` |
| **匯入測試** | **TC-IMPORT-009** | 測試 ModelBenchmark 資料類別是否可以被匯入 | `None` | 1. 嘗試從 `model_selector.agent` 匯入 `ModelBenchmark` | `None` | 成功匯入 `ModelBenchmark` |
| **匯入測試** | **TC-IMPORT-010** | 測試工具函式是否可以被匯入 | `None` | 1. 嘗試從 `model_selector.agent` 匯入 `recommend_model_for_use_case` 和 `get_model_info` | `None` | 成功匯入兩個函式 |

## 結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案結構是否遵循 ADK 慣例的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRUCT-001** | 測試 model_selector 目錄是否存在 | `None` | 1. 檢查 `model_selector` 目錄是否存在 | `None` | 目錄存在 |
| **專案結構** | **TC-STRUCT-002** | 測試 __init__.py 是否存在於 model_selector 中 | `None` | 1. 檢查 `model_selector/__init__.py` 檔案是否存在 | `None` | 檔案存在 |
| **專案結構** | **TC-STRUCT-003** | 測試 agent.py 是否存在於 model_selector 中 | `None` | 1. 檢查 `model_selector/agent.py` 檔案是否存在 | `None` | 檔案存在 |
| **專案結構** | **TC-STRUCT-004** | 測試 .env.example 是否存在於 model_selector 中 | `None` | 1. 檢查 `model_selector/.env.example` 檔案是否存在 | `None` | 檔案存在 |
| **專案結構** | **TC-STRUCT-005** | 測試 __init__.py 是否有正確的內容 | `None` | 1. 讀取 `model_selector/__init__.py` 的內容 | `None` | 內容為 "from . import agent" |
| **專案結構** | **TC-STRUCT-006** | 測試 agent.py 是否為一個有效的 Python 檔案 | `None` | 1. 讀取 `model_selector/agent.py` 的內容 | `None` | 檔案不為空且包含 "from google.adk.agents import Agent", "root_agent = Agent(", "ModelSelector" |
| **專案結構** | **TC-STRUCT-007** | 測試 .env.example 是否有必要的設定 | `None` | 1. 讀取 `.env.example` 的內容 | `None` | 內容包含 "GOOGLE_API_KEY=" |
| **測試結構** | **TC-STRUCT-008** | 測試 tests 目錄是否存在 | `None` | 1. 檢查 `tests` 目錄是否存在 | `None` | 目錄存在 |
| **測試結構** | **TC-STRUCT-009** | 測試 tests/__init__.py 是否存在 | `None` | 1. 檢查 `tests/__init__.py` 檔案是否存在 | `None` | 檔案存在 |
| **測試結構** | **TC-STRUCT-010** | 測試所有測試檔案是否存在 | `None` | 1. 檢查 `test_agent.py`, `test_imports.py`, `test_structure.py` 是否存在於 `tests/` | `None` | 所有檔案都存在 |
| **根目錄檔案** | **TC-STRUCT-011** | 測試 README.md 是否存在 | `None` | 1. 檢查 `README.md` 檔案是否存在 | `None` | 檔案存在 |
| **根目錄檔案** | **TC-STRUCT-012** | 測試 Makefile 是否存在 | `None` | 1. 檢查 `Makefile` 檔案是否存在 | `None` | 檔案存在 |
| **根目錄檔案** | **TC-STRUCT-013** | 測試 requirements.txt 是否存在 | `None` | 1. 檢查 `requirements.txt` 檔案是否存在 | `None` | 檔案存在 |
| **根目錄檔案** | **TC-STRUCT-014** | 測試 pyproject.toml 是否存在 | `None` | 1. 檢查 `pyproject.toml` 檔案是否存在 | `None` | 檔案存在 |
| **根目錄檔案** | **TC-STRUCT-015** | 測試 README.md 是否有基本內容 | `None` | 1. 讀取 `README.md` 的內容 | `None` | 內容長度大於 100 且包含 "Tutorial 22" 和 "Model Selection" |
| **根目錄檔案** | **TC-STRUCT-016** | 測試 Makefile 是否有基本的目標 | `None` | 1. 讀取 `Makefile` 的內容 | `None` | 內容包含 "help:", "setup:", "test:", "dev:" |
| **根目錄檔案** | **TC-STRUCT-017** | 測試 requirements.txt 是否包含 ADK | `None` | 1. 讀取 `requirements.txt` 的內容 | `None` | 內容包含 "google-adk" |
| **根目錄檔案** | **TC-STRUCT-018** | 測試 pyproject.toml 是否有正確的專案名稱 | `None` | 1. 讀取 `pyproject.toml` 的內容 | `None` | 內容包含 "tutorial22" 和 "Model Selection" |
