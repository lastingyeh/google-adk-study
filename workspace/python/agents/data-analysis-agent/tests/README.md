# 詳細測試案例說明

## 簡介

此文件提供了一個詳細的測試案例說明，旨在為 `data-analysis-agent` 專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Agent 配置與工具測試 (`tests/test_agent.py`)

此部分涵蓋對 Data Analysis Agent 的核心配置、屬性以及各個分析工具的功能正確性驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 配置** | **TC-AGENT-001** | 驗證 Root Agent 定義 | 安裝相依套件 | 匯入 `root_agent` 並檢查是否存在 | None | `root_agent` 不為 None |
| **Agent 配置** | **TC-AGENT-002** | 驗證 Agent 名稱 | 無 | 檢查 `root_agent.name` | None | 名稱應為 `data_analysis_agent` 或 `data_analysis_coordinator` |
| **Agent 配置** | **TC-AGENT-003** | 驗證 Agent 模型 | 無 | 檢查 `root_agent.model` | None | 模型應為 `gemini-2.0-flash` |
| **Agent 配置** | **TC-AGENT-004** | 驗證 Agent 描述 | 無 | 檢查 `root_agent.description` | None | 描述不為 None 且長度大於 0 |
| **Agent 配置** | **TC-AGENT-005** | 驗證 Agent 指令 | 無 | 檢查 `root_agent.instruction` | None | 指令不為 None 且長度大於 0 |
| **Agent 配置** | **TC-AGENT-006** | 驗證 Agent 工具配置 | 無 | 檢查 `root_agent.tools` 屬性 | None | `tools` 屬性存在且不為 None，長度大於 0 |
| **Agent 配置** | **TC-AGENT-007** | 驗證 Agent 工具數量 | 無 | 檢查 `root_agent.tools` 數量 | None | 工具數量應大於等於 2 |
| **工具測試** | **TC-TOOL-001** | 測試 analyze_column 工具結構 | 無 | 呼叫 `analyze_column("test_column", "summary")` | "test_column", "summary" | 返回字典，包含 status 和 report |
| **工具測試** | **TC-TOOL-002** | 測試 analyze_column 成功案例 | 無 | 呼叫 `analyze_column("age", "summary")` | "age", "summary" | status 為 "success"，包含 report |
| **工具測試** | **TC-TOOL-003** | 測試 analyze_column 無效欄位 | 無 | 呼叫 `analyze_column("", "summary")` | "", "summary" | status 為 "error"，包含 report |
| **工具測試** | **TC-TOOL-004** | 測試 calculate_correlation 工具 | 無 | 呼叫 `calculate_correlation("col1", "col2")` | "col1", "col2" | 返回字典，包含 status 和 report |
| **工具測試** | **TC-TOOL-005** | 測試 calculate_correlation 缺參 | 無 | 呼叫 `calculate_correlation("col1", "")` | "col1", "" | status 為 "error" |
| **工具測試** | **TC-TOOL-006** | 測試 filter_data 工具 | 無 | 呼叫 `filter_data("age", "greater_than", "30")` | "age", "greater_than", "30" | 返回字典，包含 status 和 report |
| **工具測試** | **TC-TOOL-007** | 測試 filter_data 缺參 | 無 | 呼叫 `filter_data("", "equals", "value")` | "", "equals", "value" | status 為 "error" |
| **工具測試** | **TC-TOOL-008** | 測試 get_dataset_summary 工具 | 無 | 呼叫 `get_dataset_summary()` | None | status 為 "success"，包含 report |
| **工具測試** | **TC-TOOL-009** | 驗證所有工具返回格式一致性 | 無 | 遍歷呼叫所有工具 | 各工具測試數據 | 所有返回皆為字典且包含 status 和 report |
| **例外處理** | **TC-EXCEPT-001** | analyze_column 例外處理 | 無 | 呼叫 `analyze_column(None, None)` | None, None | 不拋出異常，返回包含 status 的字典 |
| **例外處理** | **TC-EXCEPT-002** | filter_data 例外處理 | 無 | 呼叫 `filter_data(None, None, None)` | None, None, None | 不拋出異常，返回包含 status 的字典 |

## 匯入與結構驗證測試 (`tests/test_imports.py`)

此部分涵蓋對模組、類別與函式匯入的驗證，確保程式碼結構的完整性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入測試** | **TC-IMPORT-001** | 驗證 Agent 模組匯入 | 安裝專案套件 | `from data_analysis_agent import agent` | None | `agent` 不為 None |
| **匯入測試** | **TC-IMPORT-002** | 驗證 Root Agent 模組匯入 | 無 | `from data_analysis_agent import root_agent` | None | `root_agent` 不為 None |
| **匯入測試** | **TC-IMPORT-003** | 驗證套件層級匯入 | 無 | 匯入 `root_agent` 並檢查屬性 | None | 具有 `name`, `model` 屬性 |
| **結構測試** | **TC-IMPORT-004** | 驗證工具函式存在性 | 無 | 匯入並檢查 `callable()` | analyze_column, etc. | 所有工具函式皆可被呼叫 |
| **結構測試** | **TC-IMPORT-005** | 驗證 Agent 屬性 | 無 | 檢查 `root_agent` 屬性 | None | 包含 `name`, `model`, `description`, `instruction`, `tools` |

## 專案結構與檔案存在性測試 (`tests/test_structure.py`)

此部分涵蓋對專案目錄結構、必要設定檔及程式碼品質規範的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **檔案結構** | **TC-STRUCT-001** | 驗證 Agent 模組目錄 | 無 | 檢查目錄 `data_analysis_agent` | None | 目錄存在 |
| **檔案結構** | **TC-STRUCT-002** | 驗證 `__init__.py` | 無 | 檢查檔案 `data_analysis_agent/__init__.py` | None | 檔案存在 |
| **檔案結構** | **TC-STRUCT-003** | 驗證 `agent.py` | 無 | 檢查檔案 `data_analysis_agent/agent.py` | None | 檔案存在 |
| **檔案結構** | **TC-STRUCT-004** | 驗證測試目錄 | 無 | 檢查目錄 `tests` | None | 目錄存在 |
| **檔案結構** | **TC-STRUCT-005** | 驗證測試檔案 | 無 | 檢查測試檔案存在性 | None | `test_agent.py`, `test_imports.py` 存在 |
| **檔案結構** | **TC-STRUCT-006** | 驗證設定檔 | 無 | 檢查設定檔存在性 | None | `pyproject.toml`, `requirements.txt`, `Makefile` 存在 |
| **檔案結構** | **TC-STRUCT-007** | 驗證環境範本檔 | 無 | 檢查 `.env.example` | None | 檔案存在 |
| **檔案結構** | **TC-STRUCT-008** | 驗證 Streamlit App | 無 | 檢查 `app.py` | None | 檔案存在 |
| **檔案結構** | **TC-STRUCT-009** | 驗證 README | 無 | 檢查 `README.md` | None | 檔案存在 |
| **設定內容** | **TC-STRUCT-010** | 驗證 pyproject.toml 內容 | `pyproject.toml` 存在 | 讀取檔案內容 | None | 包含 `[project]` 和 `data-analysis-agent` |
| **設定內容** | **TC-STRUCT-011** | 驗證 requirements.txt 依賴 | `requirements.txt` 存在 | 讀取檔案內容 | None | 包含 `google-genai`, `streamlit`, `pandas` |
| **環境設定** | **TC-ENV-001** | 驗證環境範本非正式環境 | `.env.example` 存在 | 檢查 `.env` 與範本區別 | None | `.env.example` 存在且不等於 `.env` |
| **環境設定** | **TC-ENV-002** | 驗證環境範本佔位符 | `.env.example` 存在 | 讀取內容檢查 API Key | None | 包含 `your_api_key_here` 或 `GOOGLE_API_KEY` |
| **環境設定** | **TC-ENV-003** | 驗證 Makefile 目標 | `Makefile` 存在 | 讀取內容檢查 targets | None | 包含 `help`, `setup`, `dev`, `test` |
| **程式碼品質** | **TC-QUALITY-001** | 驗證 Agent 模組 Docstrings | `agent.py` 存在 | 檢查檔案 Docstrings | None | 包含 `"""` 和 `Data Analysis Agent` |
| **程式碼品質** | **TC-QUALITY-002** | 驗證 App Docstring | `app.py` 存在 | 檢查檔案 Docstrings | None | 包含 `"""` 和 `Streamlit` 相關描述 |
| **程式碼品質** | **TC-QUALITY-003** | 驗證函式 Docstrings | `agent.py` 存在 | 檢查主要函式定義 | None | `analyze_column` 等函式存在 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。例如：`使用者身份驗證`、`API 整合`。
*   **測試案例編號**: 唯一的測試案例識別碼。建議格式為 `TC-[模組]-[編號]`，例如 `TC-AUTH-001`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟，應清晰且可重複。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
