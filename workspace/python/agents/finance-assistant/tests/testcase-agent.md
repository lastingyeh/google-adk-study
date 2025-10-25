# Finance Assistant Agent 測試案例

## 簡介

此文件提供了 `finance-assistant` 代理的詳細測試案例，旨在驗證其設定、工具功能和整體整合的正確性。測試案例根據 `tests/test_agent.py` 中定義的測試套件進行組織。

## 代理設定測試 (`tests/test_agent.py`)

此部分涵蓋對 `finance-assistant` 代理基本設定的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理設定** | **TC-AGENT-001** | 測試代理是否成功建立 | 代理程式碼已定義 | 1. 匯入 `root_agent` | `root_agent` | `root_agent` 物件不為 `None`，且其 `name` 為 `finance_assistant`，`model` 為 `gemini-2.0-flash`。 |
| **代理設定** | **TC-AGENT-002** | 測試代理是否有適當的描述 | `root_agent` 已建立 | 1. 讀取 `root_agent.description` | `root_agent.description` | 描述應包含 "financial calculation assistant"、"compound interest"、"loan payment" 和 "monthly savings" 等關鍵字。 |
| **代理設定** | **TC-AGENT-003** | 測試所有工具是否都已註冊 | `root_agent` 已建立 | 1. 讀取 `root_agent.tools` | `root_agent.tools` | 代理應註冊 3 個工具，且 `calculate_compound_interest`、`calculate_loan_payment` 和 `calculate_monthly_savings` 函式都應在工具清單中。 |

## 工具函式簽名測試 (`tests/test_agent.py`)

此部分涵蓋對工具函式的簽名、說明文件和型別提示的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **函式簽名** | **TC-SIG-001** | 測試 `calculate_compound_interest` 函式的簽名 | 函式已定義 | 1. 檢查函式是否可呼叫<br>2. 檢查 `__doc__` | `calculate_compound_interest` | 函式可呼叫，且其 `__doc__` 包含 "compound interest"、"Args:" 和 "Returns:"。 |
| **函式簽名** | **TC-SIG-002** | 測試 `calculate_loan_payment` 函式的簽名 | 函式已定義 | 1. 檢查函式是否可呼叫<br>2. 檢查 `__doc__` | `calculate_loan_payment` | 函式可呼叫，且其 `__doc__` 包含 "loan payment"、"Args:" 和 "Returns:"。 |
| **函式簽名** | **TC-SIG-003** | 測試 `calculate_monthly_savings` 函式的簽名 | 函式已定義 | 1. 檢查函式是否可呼叫<br>2. 檢查 `__doc__` | `calculate_monthly_savings` | 函式可呼叫，且其 `__doc__` 包含 "monthly savings"、"Args:" 和 "Returns:"。 |
| **函式簽名** | **TC-SIG-004** | 測試函式是否有適當的型別提示 | 函式已定義 | 1. 使用 `inspect.signature` 檢查參數 | 各工具函式 | `calculate_compound_interest` 應有 `principal`、`annual_rate`、`years`、`compounds_per_year` 參數。<br>`calculate_loan_payment` 應有 `loan_amount`、`annual_rate`、`years` 參數。<br>`calculate_monthly_savings` 應有 `target_amount`、`years`、`annual_return` 參數。 |

## 工具回傳格式測試 (`tests/test_agent.py`)

此部分涵蓋對工具函式回傳格式的驗證，包括成功和錯誤案例。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **回傳格式** | **TC-RET-001** | 測試 `calculate_compound_interest` 的成功回傳格式 | 函式可正常執行 | 1. 呼叫函式 | `principal=1000`, `annual_rate=0.05`, `years=1` | 回傳的字典應包含 `status`、`final_amount`、`interest_earned`、`report` 鍵，且 `status` 為 "success"，其餘值的型別正確。 |
| **回傳格式** | **TC-RET-002** | 測試 `calculate_loan_payment` 的成功回傳格式 | 函式可正常執行 | 1. 呼叫函式 | `loan_amount=100000`, `annual_rate=0.05`, `years=10` | 回傳的字典應包含 `status`、`monthly_payment`、`total_paid`、`total_interest`、`report` 鍵，且 `status` 為 "success"，其餘值的型別正確。 |
| **回傳格式** | **TC-RET-003** | 測試 `calculate_monthly_savings` 的成功回傳格式 | 函式可正常執行 | 1. 呼叫函式 | `target_amount=10000`, `years=2`, `annual_return=0.05` | 回傳的字典應包含 `status`、`monthly_savings`、`total_contributed`、`interest_earned`、`report` 鍵，且 `status` 為 "success"，其餘值的型別正確。 |
| **回傳格式** | **TC-RET-004** | 測試所有工具的錯誤回傳格式 | 函式可處理錯誤 | 1. 使用無效參數呼叫函式 | `principal=-1000` (複利)<br>`years=0` (貸款)<br>`years=0` (儲蓄) | 回傳的字典應包含 `status`、`error`、`report` 鍵，且 `status` 為 "error"。 |

## 代理整合測試 (`tests/test_agent.py`)

此部分涵蓋對代理與 ADK 框架整合的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **整合** | **TC-INT-001** | 測試代理是否具有 ADK 所需的所有屬性 | `root_agent` 已建立 | 1. 檢查 `root_agent` 的屬性 | `root_agent` | `root_agent` 應具有 `name`、`model`、`description` 和 `tools` 屬性。 |
| **整合** | **TC-INT-002** | 測試所有註冊的工具是否都可呼叫 | `root_agent` 已註冊工具 | 1. 迭代 `root_agent.tools` 並檢查 | `root_agent.tools` | 所有工具都應為可呼叫的函式。 |
| **整合** | **TC-INT-003** | 測試代理是否可以成功匯入 | 模組路徑正確 | 1. 從 `finance_assistant.agent` 匯入 `root_agent` | - | 匯入成功，且匯入的代理物件不為 `None`，其 `name` 為 `finance_assistant`。 |

## 專案結構測試 (`tests/test_agent.py`)

此部分涵蓋對專案結構、模組匯入和主執行區段的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **結構** | **TC-STR-001** | 測試所有匯入是否正常運作 | 專案結構正確 | 1. 使用 `importlib` 載入 `finance_assistant.agent` | - | 模組可以被找到並成功載入，不會引發 `ImportError`。 |
| **結構** | **TC-STR-002** | 測試模組是否具有預期的結構 | 模組已載入 | 1. 檢查 `finance_assistant.agent` 的屬性 | `finance_assistant.agent` | 模組應具有 `root_agent`、`calculate_compound_interest`、`calculate_loan_payment` 和 `calculate_monthly_savings` 屬性。 |
| **結構** | **TC-STR-003** | 測試主執行區段是否不會引發錯誤 | 腳本可獨立執行 | 1. 使用 `subprocess` 執行 `finance_assistant/agent.py` | - | 腳本應成功執行（回傳碼 0），且標準輸出包含 "Finance Assistant Agent" 和各工具的測試輸出。 |