# 詳細測試案例文件

## 簡介

此文件詳細列出了 `tool-use-evaluator` 專案的測試案例，涵蓋 Agent 設定、工具功能、模組匯入與應用程式結構。

## Agent 與工具測試 (`tests/test_agent.py`)

此部分涵蓋 Agent 的基本設定驗證以及各個工具函式的單元測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 Agent 名稱 | 無 | 驗證 `root_agent.name` | 無 | 名稱為 "tool_use_evaluator" |
| **Agent 設定** | **TC-AGENT-002** | 測試 Agent 模型 | 無 | 驗證 `root_agent.model` | 無 | 模型為 "gemini-2.0-flash" |
| **Agent 設定** | **TC-AGENT-003** | 測試 Agent 描述 | 無 | 驗證 `root_agent.description` | 無 | 包含 "tool use quality" |
| **Agent 設定** | **TC-AGENT-004** | 測試 Agent 指令 | 無 | 驗證 `root_agent.instruction` | 無 | 包含 "data" |
| **Agent 設定** | **TC-AGENT-005** | 測試 Agent 工具列表 | 無 | 檢查 `root_agent.tools` 列表 | 無 | 包含 analyze_data, extract_features, validate_quality, apply_model |
| **Agent 設定** | **TC-AGENT-006** | 測試 Agent 輸出鍵值 | 無 | 驗證 `root_agent.output_key` | 無 | 鍵值為 "analysis_result" |
| **工具功能** | **TC-TOOL-001** | 測試 analyze_data 成功 | 無 | 呼叫 `analyze_data("customer_data")` | "customer_data" | 狀態 success, 報告含 "analyzed" |
| **工具功能** | **TC-TOOL-002** | 測試 analyze_data 失敗 | 無 | 呼叫 `analyze_data("")` | "" (空字串) | 狀態 error |
| **工具功能** | **TC-TOOL-003** | 測試 extract_features 成功 | 無 | 呼叫 `extract_features({"test": "data"})` | `{"test": "data"}` | 狀態 success, 數據含 "features" |
| **工具功能** | **TC-TOOL-004** | 測試 extract_features 失敗 | 無 | 呼叫 `extract_features(None)` | None | 狀態 error |
| **工具功能** | **TC-TOOL-005** | 測試 validate_quality 成功 | 無 | 呼叫 `validate_quality({"features": "data"})` | `{"features": "data"}` | 狀態 success, 數據含 "quality_score" |
| **工具功能** | **TC-TOOL-006** | 測試 validate_quality 失敗 | 無 | 呼叫 `validate_quality(None)` | None | 狀態 error |
| **工具功能** | **TC-TOOL-007** | 測試 apply_model 成功 | 無 | 呼叫 `apply_model(...)` | features=`{"features": "data"}`, model="random_forest" | 狀態 success, 數據含 "model" |
| **工具功能** | **TC-TOOL-008** | 測試 apply_model 無特徵 | 無 | 呼叫 `apply_model(None, ...)` | features=None, model="random_forest" | 狀態 error |
| **工具功能** | **TC-TOOL-009** | 測試 apply_model 無模型 | 無 | 呼叫 `apply_model(..., "")` | features=`{"features": "data"}`, model="" | 狀態 error |

## 匯入與結構測試 (`tests/test_imports.py`)

此部分驗證專案的模組匯入機制與結構完整性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入測試** | **TC-IMPORT-001** | 測試從模組匯入 Agent | 專案環境已設定 | `from tool_use_evaluator import root_agent` | 無 | root_agent 成功匯入且名稱正確 |
| **匯入測試** | **TC-IMPORT-002** | 測試匯入 App | 專案環境已設定 | `from app import app` | 無 | app 成功匯入且名稱正確 |
| **匯入測試** | **TC-IMPORT-003** | 測試 Agent 模組導出 | 專案環境已設定 | `from tool_use_evaluator.agent import root_agent` | 無 | 屬性 name 與 tools 存在 |
| **結構測試** | **TC-STRUCT-001** | 測試 init 導出 | 無 | 檢查 `__init__.py` 導出 | 無 | 可從頂層匯入 root_agent |
| **結構測試** | **TC-STRUCT-002** | 測試模組存在 | 無 | `import tool_use_evaluator` | 無 | 模組包含 root_agent |

## 應用程式結構測試 (`tests/test_structure.py`)

此部分驗證應用程式層級的設定與 Agent 整合。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **App 設定** | **TC-APP-001** | 測試 App 建立 | 無 | 匯入並檢查 app 物件 | 無 | app 名稱為 "tool_use_quality_app" |
| **App 設定** | **TC-APP-002** | 測試 App 包含 Root Agent | 無 | 檢查 `app.root_agent` | 無 | root_agent 名稱為 "tool_use_evaluator" |
| **App 設定** | **TC-APP-003** | 測試 App Root Agent 工具 | 無 | 檢查 `app.root_agent.tools` | 無 | 工具數量為 4，包含 analyze_data |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
