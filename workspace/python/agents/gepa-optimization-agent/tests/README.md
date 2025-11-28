# 詳細測試案例說明

## 簡介

此文件提供了 `tutorial_gepa_optimization` 專案的詳細測試案例，旨在為專案建立清晰、一致且全面的測試文件。

## GEPA 代理程式測試 (`tests/test_agent.py`)

此部分涵蓋對 GEPA 教學代理程式的全面測試，包括其設定、工具使用及與 GEPA 優化概念的整合。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理程式設定** | **TC-AGENT-001** | 測試代理程式是否能成功建立 | `create_support_agent` 函式可用 | 1. 呼叫 `create_support_agent()` | `None` | 成功建立代理程式實例，且名稱為 `customer_support_agent` |
| **代理程式設定** | **TC-AGENT-002** | 測試 `root_agent` 是否已正確匯出 | `root_agent` 已在模組中定義 | 1. 檢查 `root_agent` 是否存在 | `None` | `root_agent` 不為 `None` 且具有 `name` 屬性 |
| **代理程式設定** | **TC-AGENT-003** | 測試使用自訂提示建立代理程式 | `create_support_agent` 函式可用 | 1. 使用自訂提示呼叫 `create_support_agent()` | `prompt="You are a test agent."` | 成功建立代理程式實例 |
| **代理程式設定** | **TC-AGENT-004** | 測試代理程式是否預設使用 `INITIAL_PROMPT` | `INITIAL_PROMPT` 已定義 | 1. 呼叫 `create_support_agent()` | `None` | 代理程式的 `instruction` 屬性等於 `INITIAL_PROMPT` |
| **代理程式設定** | **TC-AGENT-005** | 測試代理程式是否擁有所有必要的工具 | 代理程式已建立 | 1. 檢查代理程式的 `tools` 屬性 | `None` | `tools` 屬性不為 `None` 且包含 3 個工具 |
| **代理程式設定** | **TC-AGENT-006** | 測試代理程式是否使用正確的模型 | 代理程式已建立 | 1. 檢查代理程式的 `model` 屬性 | `None` | `model` 屬性不為 `None` |
| **客戶身份驗證工具** | **TC-TOOL-VCI-001** | 測試工具是否可以被實例化 | `VerifyCustomerIdentity` 類別可用 | 1. 實例化 `VerifyCustomerIdentity` | `None` | 成功建立工具實例，且名稱為 `verify_customer_identity` |
| **客戶身份驗證工具** | **TC-TOOL-VCI-002** | 測試使用有效客戶進行驗證 | 工具已實例化 | 1. 使用有效訂單 ID 和電子郵件呼叫 `run_async` | `order_id="ORD-12345", email="customer@example.com"` | 結果包含 "✓" 且回傳 "verified" |
| **客戶身份驗證工具** | **TC-TOOL-VCI-003** | 測試使用錯誤的電子郵件進行驗證 | 工具已實例化 | 1. 使用錯誤的電子郵件呼叫 `run_async` | `order_id="ORD-12345", email="wrong@example.com"` | 結果包含 "✗" 且回傳 "failed" |
| **退貨政策工具** | **TC-TOOL-CRP-001** | 測試訂單是否在 30 天退貨期內 | `CheckReturnPolicy` 工具已實例化 | 1. 使用在退貨期內的 `days_since_purchase` 呼叫 `run_async` | `order_id="ORD-12345", days_since_purchase=15` | 結果包含 "✓" 且回傳 "eligible" |
| **退貨政策工具** | **TC-TOOL-CRP-002** | 測試訂單是否超出 30 天退貨期 | `CheckReturnPolicy` 工具已實例化 | 1. 使用超出退貨期的 `days_since_purchase` 呼叫 `run_async` | `order_id="ORD-12345", days_since_purchase=45` | 結果包含 "✗" 且回傳 "cannot be returned" |
| **退款處理工具** | **TC-TOOL-PR-001** | 測試退款處理是否成功 | `ProcessRefund` 工具已實例化 | 1. 使用有效的退款參數呼叫 `run_async` | `order_id="ORD-12345", amount=99.99` | 結果包含 "✓" 且回傳 "processed" |
| **GEPA 概念** | **TC-GEPA-001** | 測試初始提示是否具有可供優化的已知差距 | `INITIAL_PROMPT` 已定義 | 1. 檢查 `INITIAL_PROMPT` 的內容 | `None` | 提示應為通用性描述，缺乏具體的操作指令 |

## GEPA 優化器模組測試 (`tests/test_gepa_optimizer.py`)

此部分涵蓋對 GEPA 優化器模組的測試，包括其資料類別、核心邏輯和整合功能。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **評估情境** | **TC-OPTIM-001** | 測試建立評估情境 | `EvaluationScenario` 類別可用 | 1. 實例化 `EvaluationScenario` | `name="Test Scenario", customer_input="Hello"` | 成功建立實例，且屬性符合預期 |
| **執行結果** | **TC-OPTIM-002** | 測試建立成功的執行結果 | `ExecutionResult` 類別可用 | 1. 實例化 `ExecutionResult` | `success=True, tools_used=["tool1"]` | 成功建立實例，`success` 屬性為 `True` |
| **GEPA 迭代** | **TC-OPTIM-003** | 測試建立 GEPA 迭代結果 | `GEPAIteration` 類別可用 | 1. 實例化 `GEPAIteration` | `iteration=1, success_rate=0.8` | 成功建立實例，屬性符合預期 |
| **優化器邏輯** | **TC-OPTIM-004** | 測試建立 GEPA 優化器 | `RealGEPAOptimizer` 類別可用 | 1. 實例化 `RealGEPAOptimizer` | `max_iterations=2, budget=30` | 成功建立優化器，且預算分配正確 (`budget_per_iteration` 為 15) |
| **優化器邏輯** | **TC-OPTIM-005** | 測試從提示中提取工具 | 優化器已實例化 | 1. 使用包含工具名稱的提示呼叫 `_extract_tools_from_prompt` | `prompt="Always verify customer identity"` | 返回的工具列表中包含 `verify_customer_identity` |
| **優化器邏輯** | **TC-OPTIM-006** | 測試用於遺傳變異的提示突變 | 優化器已實例化 | 1. 使用基礎提示呼叫 `_mutate_prompt` | `prompt="Base prompt"` | 返回一個與基礎提示不同的新提示 |
| **整合測試** | **TC-OPTIM-007** | 測試優化器是否追蹤迭代 | 優化器已實例化 | 1. 手動向優化器的 `iterations` 列表添加迭代 | `None` | `iterations` 列表的長度應為 2 |

## 專案結構與匯入測試 (`tests/test_imports.py`)

此部分用於驗證專案的模組結構是否正確，以及所有必要的元件是否可以成功匯入。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組匯入** | **TC-IMPORT-001** | 測試匯入 `agent` 模組 | 專案路徑已設定 | 1. `from gepa_agent import agent` | `None` | 模組成功匯入，未引發 `ImportError` |
| **模組匯入** | **TC-IMPORT-002** | 測試匯入 `root_agent` | `agent` 模組可匯入 | 1. `from gepa_agent.agent import root_agent` | `None` | `root_agent` 成功匯入且不為 `None` |
| **模組匯入** | **TC-IMPORT-003** | 測試匯入工具類別 | `agent` 模組可匯入 | 1. 匯入 `VerifyCustomerIdentity`, `CheckReturnPolicy`, `ProcessRefund` | `None` | 所有工具類別成功匯入 |
| **專案結構** | **TC-STRUCT-001** | 測試 `gepa_agent` 套件是否存在 | 專案已安裝或在路徑中 | 1. `import gepa_agent` | `None` | 套件成功匯入 |
| **專案結構** | **TC-STRUCT-002** | 測試 `gepa_agent` 是否有 `__init__.py` | `gepa_agent` 套件存在 | 1. 檢查 `__all__` 和 `__version__` | `None` | `__all__` 和 `__version__` 變數存在且不為 `None` |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
