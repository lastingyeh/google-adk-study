# 詳細測試案例文件

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Interactions API Basic Agent 測試 (`tests/test_agent.py`)

此部分涵蓋對 Interactions API Basic Agent 的單元測試，包含模組匯入、工具定義、Agent 設定及互動功能。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組匯入測試** | **TC-IMPORTS-001** | 測試匯入主模組。 | 模組已安裝 | 1. 匯入 create_basic_interaction 等函式<br>2. 檢查是否為 callable | 無 | 成功匯入且函式可被呼叫 |
| **模組匯入測試** | **TC-IMPORTS-002** | 測試匯入工具模組。 | 模組已安裝 | 1. 匯入工具相關函式與列表<br>2. 檢查類型與可呼叫性 | 無 | 工具函式可被呼叫，AVAILABLE_TOOLS 為列表 |
| **模組匯入測試** | **TC-IMPORTS-003** | 測試匯入常數。 | 模組已安裝 | 1. 匯入 SUPPORTED_MODELS<br>2. 檢查是否為列表且包含 gemini-2.5-flash | 無 | SUPPORTED_MODELS 為列表且包含特定模型 |
| **工具定義測試** | **TC-TOOLS-001** | 測試天氣工具具有正確的 schema。 | 無 | 1. 呼叫 get_weather_tool()<br>2. 驗證返回字典的結構 | 無 | 包含正確的 type, name, description, parameters |
| **工具定義測試** | **TC-TOOLS-002** | 測試計算器工具具有正確的 schema。 | 無 | 1. 呼叫 calculate_tool()<br>2. 驗證返回字典的結構 | 無 | 包含正確的 type, name, properties |
| **工具定義測試** | **TC-TOOLS-003** | 測試 AVAILABLE_TOOLS 包含工具。 | 無 | 1. 檢查 AVAILABLE_TOOLS 長度<br>2. 迭代檢查每個工具的結構 | 無 | 列表不為空，且每個工具都有 type, name, parameters |
| **工具執行測試** | **TC-EXEC-001** | 測試天氣工具執行。 | 無 | 1. 呼叫 execute_tool("get_weather", ...)<br>2. 驗證結果 | location: "Paris" | 結果包含 "Paris" 和 "weather" |
| **工具執行測試** | **TC-EXEC-002** | 測試計算器工具執行。 | 無 | 1. 呼叫 execute_tool("calculate", ...)<br>2. 驗證結果 | expression: "2 + 2" | 結果包含 "4" |
| **工具執行測試** | **TC-EXEC-003** | 測試帶百分比的計算器。 | 無 | 1. 呼叫 execute_tool("calculate", ...)<br>2. 驗證結果 | expression: "10% of 200" | 結果包含 "20" |
| **工具執行測試** | **TC-EXEC-004** | 測試未知工具返回錯誤訊息。 | 無 | 1. 呼叫 execute_tool("unknown_tool", ...)<br>2. 驗證結果 | tool_name: "unknown_tool" | 結果包含 "Unknown tool" |
| **Agent 設定測試** | **TC-CONFIG-001** | 測試支援的模型列表。 | 無 | 1. 檢查 SUPPORTED_MODELS 長度<br>2. 檢查特定模型是否存在 | 無 | 包含至少 4 個模型，包含 DEFAULT_MODEL 等 |
| **Agent 設定測試** | **TC-CONFIG-002** | 測試在沒有 API 金鑰的情況下 get_client 會引發異常。 | 清除 GOOGLE_API_KEY 環境變數 | 1. 呼叫 get_client() | 無 | 引發 ValueError 且包含 "GOOGLE_API_KEY" |
| **Agent 設定測試** | **TC-CONFIG-003** | 測試使用 API 金鑰取得 client。 | 設定 GOOGLE_API_KEY 環境變數 | 1. 呼叫 get_client() | GOOGLE_API_KEY='test-key' | Client 被正確初始化 |
| **Agent 設定測試** | **TC-CONFIG-004** | 測試使用明確的 API 金鑰參數取得 client。 | 無 | 1. 呼叫 get_client(api_key=...) | api_key='explicit-key' | Client 被使用指定 key 初始化 |
| **互動功能測試** | **TC-INTERACT-001** | 測試建立基本互動。 | Mock Client | 1. 設定 Mock 回應<br>2. 呼叫 create_basic_interaction | prompt: "Test prompt" | 返回正確的 id, text, status |
| **互動功能測試** | **TC-INTERACT-002** | 測試建立有狀態的對話。 | Mock Client | 1. 設定多次 Mock 回應<br>2. 呼叫 create_stateful_conversation | messages: ["Message 1", "Message 2"] | 返回列表包含 2 個結果，且 previous_id 正確串接 |
| **互動功能測試** | **TC-INTERACT-003** | 測試函式呼叫互動。 | Mock Client (Function Call) | 1. 設定 Mock 回應<br>2. 呼叫 create_function_calling_interaction | prompt: "Weather?", tools: [...] | 返回結果包含 tool_calls |
| **內建工具測試** | **TC-BUILTIN-001** | 測試 Google 搜尋內建工具。 | Mock Client | 1. 設定 Mock 回應<br>2. 呼叫 create_interaction_with_builtin_tools | tool_type="google_search" | 正確傳遞 tools 參數給 client |
| **內建工具測試** | **TC-BUILTIN-002** | 測試無效的內建工具會引發錯誤。 | 無 | 1. 呼叫 create_interaction_with_builtin_tools 使用無效 tool_type | tool_type="invalid_tool" | 引發 ValueError |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。例如：`使用者身份驗證`、`API 整合`。
*   **測試案例編號**: 唯一的測試案例識別碼。建議格式為 `TC-[模組]-[編號]`，例如 `TC-AUTH-001`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟，應清晰且可重複。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
