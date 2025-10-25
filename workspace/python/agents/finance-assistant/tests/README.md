# `finance_assistant` 測試案例

## 簡介

此文件詳細記錄了 `finance_assistant` 代理及其財務計算工具的測試案例，旨在確保每個財務函式的準確性、可靠性、錯誤處理能力，以及代理本身的設定和整合都符合預期。

---

## 財務計算工具測試 (`workspace/python/agents/finance-assistant/tests/test_tools.py`)

此部分涵蓋對財務計算工具的測試，包括複利、貸款月付金和每月儲蓄的計算。

### `TestCompoundInterest` (複利計算)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **基本計算** | **TC-CI-001** | 測試基本的複利計算。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=1000`, `rate=0.05`, `years=1` | 函式回傳 `status: "success"`，`final_amount: 1050.00`，`interest_earned: 50.00`。 |
| **基本計算** | **TC-CI-002** | 測試包含按月複利的計算。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=10000`, `rate=0.06`, `years=5`, `compounding_periods=12` | 函式回傳 `status: "success"`，`final_amount` 約為 `13488.50`，`interest_earned` 約為 `3488.50`。 |
| **基本計算** | **TC-CI-003** | 測試按季複利的計算。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=1000`, `rate=0.04`, `years=2`, `compounding_periods=4` | 函式回傳 `status: "success"`，`final_amount` > 1000，`interest_earned` > 0。 |
| **邊界情況** | **TC-CI-004** | 測試高精度要求的計算。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=12345.67`, `rate=0.0725`, `years=7`, `compounding_periods=12` | 函式回傳 `status: "success"`，且 `final_amount` 和 `interest_earned` 為浮點數。 |
| **錯誤處理** | **TC-CI-005** | 測試對零本金的錯誤處理。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=0`, `rate=0.05`, `years=1` | 函式回傳 `status: "error"`，錯誤訊息包含 "Principal must be positive"。 |
| **錯誤處理** | **TC-CI-006** | 測試對負數本金的錯誤處理。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=-1000`, `rate=0.05`, `years=1` | 函式回傳 `status: "error"`，錯誤訊息包含 "Principal must be positive"。 |
| **錯誤處理** | **TC-CI-007** | 測試對利率 > 100% 的錯誤處理。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=1000`, `rate=1.5`, `years=1` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid interest rate"。 |
| **錯誤處理** | **TC-CI-008** | 測試對負數利率的錯誤處理。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=1000`, `rate=-0.05`, `years=1` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid interest rate"。 |
| **錯誤處理** | **TC-CI-009** | 測試對零年期的錯誤處理。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=1000`, `rate=0.05`, `years=0` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid time period"。 |
| **錯誤處理** | **TC-CI-010** | 測試對負數年期的錯誤處理。 | 無 | 1. 呼叫 `calculate_compound_interest` 函式。 | `principal=1000`, `rate=0.05`, `years=-1` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid time period"。 |

### `TestLoanPayment` (貸款月付金計算)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **基本計算** | **TC-LP-001** | 測試基本的貸款月付金計算。 | 無 | 1. 呼叫 `calculate_loan_payment` 函式。 | `amount=100000`, `rate=0.05`, `years=10` | 函式回傳 `status: "success"`，`total_paid` 約為 `127278.62`。 |
| **基本計算** | **TC-LP-002** | 測試 30 年期抵押貸款的計算。 | 無 | 1. 呼叫 `calculate_loan_payment` 函式。 | `amount=300000`, `rate=0.045`, `years=30` | 函式回傳 `status: "success"`，`monthly_payment` 約為 `1520.06`。 |
| **邊界情況** | **TC-LP-003** | 測試零利率的貸款月付金計算。 | 無 | 1. 呼叫 `calculate_loan_payment` 函式。 | `amount=120000`, `rate=0.0`, `years=10` | 函式回傳 `status: "success"`，`monthly_payment` 為 `1000`，`total_interest` 為 `0`。 |
| **邊界情況** | **TC-LP-004** | 測試高利率的貸款月付金計算。 | 無 | 1. 呼叫 `calculate_loan_payment` 函式。 | `amount=50000`, `rate=0.15`, `years=5` | 函式回傳 `status: "success"`，`monthly_payment` > `833.33`。 |
| **錯誤處理** | **TC-LP-005** | 測試對零貸款金額的錯誤處理。 | 無 | 1. 呼叫 `calculate_loan_payment` 函式。 | `amount=0`, `rate=0.05`, `years=10` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid loan amount"。 |
| **錯誤處理** | **TC-LP-006** | 測試對負數貸款金額的錯誤處理。 | 無 | 1. 呼叫 `calculate_loan_payment` 函式。 | `amount=-100000`, `rate=0.05`, `years=10` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid loan amount"。 |
| **錯誤處理** | **TC-LP-007** | 測試對利率 > 100% 的錯誤處理。 | 無 | 1. 呼叫 `calculate_loan_payment` 函式。 | `amount=100000`, `rate=1.2`, `years=10` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid interest rate"。 |
| **錯誤處理** | **TC-LP-008** | 測試對零年期的錯誤處理。 | 無 | 1. 呼叫 `calculate_loan_payment` 函式。 | `amount=100000`, `rate=0.05`, `years=0` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid loan term"。 |

### `TestMonthlySavings` (每月儲蓄計算)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **基本計算** | **TC-MS-001** | 測試基本的每月儲蓄計算。 | 無 | 1. 呼叫 `calculate_monthly_savings` 函式。 | `target_amount=10000`, `years=2`, `return_rate=0.05` | 函式回傳 `status: "success"`，`monthly_savings` > 0。 |
| **基本計算** | **TC-MS-002** | 測試為頭期款目標的儲蓄計算。 | 無 | 1. 呼叫 `calculate_monthly_savings` 函式。 | `target_amount=50000`, `years=3`, `return_rate=0.05` | 函式回傳 `status: "success"`，`monthly_savings` 約為 `1290.21`。 |
| **邊界情況** | **TC-MS-003** | 測試零回報率的儲蓄計算。 | 無 | 1. 呼叫 `calculate_monthly_savings` 函式。 | `target_amount=12000`, `years=2`, `return_rate=0.0` | 函式回傳 `status: "success"`，`monthly_savings` 為 `500`，`interest_earned` 為 `0`。 |
| **邊界情況** | **TC-MS-004** | 測試高回報率的儲蓄計算。 | 無 | 1. 呼叫 `calculate_monthly_savings` 函式。 | `target_amount=100000`, `years=10`, `return_rate=0.08` | 函式回傳 `status: "success"`，`monthly_savings` > 0。 |
| **錯誤處理** | **TC-MS-005** | 測試對零目標金額的錯誤處理。 | 無 | 1. 呼叫 `calculate_monthly_savings` 函式。 | `target_amount=0`, `years=5`, `return_rate=0.05` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid target amount"。 |
| **錯誤處理** | **TC-MS-006** | 測試對負數目標金額的錯誤處理。 | 無 | 1. 呼叫 `calculate_monthly_savings` 函式。 | `target_amount=-10000`, `years=5`, `return_rate=0.05` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid target amount"。 |
| **錯誤處理** | **TC-MS-007** | 測試對零年期的錯誤處理。 | 無 | 1. 呼叫 `calculate_monthly_savings` 函式。 | `target_amount=10000`, `years=0`, `return_rate=0.05` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid time period"。 |
| **錯誤處理** | **TC-MS-008** | 測試對負數回報率的錯誤處理。 | 無 | 1. 呼叫 `calculate_monthly_savings` 函式。 | `target_amount=10000`, `years=5`, `return_rate=-0.05` | 函式回傳 `status: "error"`，錯誤訊息包含 "Invalid return rate"。 |

### `TestIntegration` (整合測試)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **整合** | **TC-INT-001** | 測試多個計算是否能協同工作。 | 無 | 1. 呼叫 `calculate_compound_interest`。<br>2. 呼叫 `calculate_loan_payment`。<br>3. 呼叫 `calculate_monthly_savings`。 | (多個) | 所有函式均回傳 `status: "success"`。 |
| **整合** | **TC-INT-002** | 測試所有函式的錯誤處理整合。 | 無 | 1. 使用無效參數呼叫每個財務函式。 | (多個無效參數) | 每個函式均回傳 `status: "error"`。 |
| **整合** | **TC-INT-003** | 測試真實世界的財務情境。 | 無 | 1. 計算退休儲蓄。<br>2. 計算汽車貸款。<br>3. 計算投資增長。 | (多個真實世界數據) | 所有計算均成功並回傳合理結果。 |

---

## 代理設定與整合測試 (`tests/test_agent.py`)

此部分涵蓋對 `finance-assistant` 代理的基本設定、工具功能和整體整合的驗證。

### 代理設定測試

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理設定** | **TC-AGENT-001** | 測試代理是否成功建立 | 代理程式碼已定義 | 1. 匯入 `root_agent` | `root_agent` | `root_agent` 物件不為 `None`，且其 `name` 為 `finance_assistant`，`model` 為 `gemini-2.0-flash`。 |
| **代理設定** | **TC-AGENT-002** | 測試代理是否有適當的描述 | `root_agent` 已建立 | 1. 讀取 `root_agent.description` | `root_agent.description` | 描述應包含 "financial calculation assistant"、"compound interest"、"loan payment" 和 "monthly savings" 等關鍵字。 |
| **代理設定** | **TC-AGENT-003** | 測試所有工具是否都已註冊 | `root_agent` 已建立 | 1. 讀取 `root_agent.tools` | `root_agent.tools` | 代理應註冊 3 個工具，且 `calculate_compound_interest`、`calculate_loan_payment` 和 `calculate_monthly_savings` 函式都應在工具清單中。 |

### 工具函式簽名測試

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **函式簽名** | **TC-SIG-001** | 測試 `calculate_compound_interest` 函式的簽名 | 函式已定義 | 1. 檢查函式是否可呼叫<br>2. 檢查 `__doc__` | `calculate_compound_interest` | 函式可呼叫，且其 `__doc__` 包含 "compound interest"、"Args:" 和 "Returns:"。 |
| **函式簽名** | **TC-SIG-002** | 測試 `calculate_loan_payment` 函式的簽名 | 函式已定義 | 1. 檢查函式是否可呼叫<br>2. 檢查 `__doc__` | `calculate_loan_payment` | 函式可呼叫，且其 `__doc__` 包含 "loan payment"、"Args:" 和 "Returns:"。 |
| **函式簽名** | **TC-SIG-003** | 測試 `calculate_monthly_savings` 函式的簽名 | 函式已定義 | 1. 檢查函式是否可呼叫<br>2. 檢查 `__doc__` | `calculate_monthly_savings` | 函式可呼叫，且其 `__doc__` 包含 "monthly savings"、"Args:" 和 "Returns:"。 |
| **函式簽名** | **TC-SIG-004** | 測試函式是否有適當的型別提示 | 函式已定義 | 1. 使用 `inspect.signature` 檢查參數 | 各工具函式 | `calculate_compound_interest` 應有 `principal`、`annual_rate`、`years`、`compounds_per_year` 參數。<br>`calculate_loan_payment` 應有 `loan_amount`、`annual_rate`、`years` 參數。<br>`calculate_monthly_savings` 應有 `target_amount`、`years`、`annual_return` 參數。 |

### 工具回傳格式測試

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **回傳格式** | **TC-RET-001** | 測試 `calculate_compound_interest` 的成功回傳格式 | 函式可正常執行 | 1. 呼叫函式 | `principal=1000`, `annual_rate=0.05`, `years=1` | 回傳的字典應包含 `status`、`final_amount`、`interest_earned`、`report` 鍵，且 `status` 為 "success"，其餘值的型別正確。 |
| **回傳格式** | **TC-RET-002** | 測試 `calculate_loan_payment` 的成功回傳格式 | 函式可正常執行 | 1. 呼叫函式 | `loan_amount=100000`, `annual_rate=0.05`, `years=10` | 回傳的字典應包含 `status`、`monthly_payment`、`total_paid`、`total_interest`、`report` 鍵，且 `status` 為 "success"，其餘值的型別正確。 |
| **回傳格式** | **TC-RET-003** | 測試 `calculate_monthly_savings` 的成功回傳格式 | 函式可正常執行 | 1. 呼叫函式 | `target_amount=10000`, `years=2`, `annual_return=0.05` | 回傳的字典應包含 `status`、`monthly_savings`、`total_contributed`、`interest_earned`、`report` 鍵，且 `status` 為 "success"，其餘值的型別正確。 |
| **回傳格式** | **TC-RET-004** | 測試所有工具的錯誤回傳格式 | 函式可處理錯誤 | 1. 使用無效參數呼叫函式 | `principal=-1000` (複利)<br>`years=0` (貸款)<br>`years=0` (儲蓄) | 回傳的字典應包含 `status`、`error`、`report` 鍵，且 `status` 為 "error"。 |

### 代理整合與專案結構測試

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **整合** | **TC-INT-001** | 測試代理是否具有 ADK 所需的所有屬性 | `root_agent` 已建立 | 1. 檢查 `root_agent` 的屬性 | `root_agent` | `root_agent` 應具有 `name`、`model`、`description` 和 `tools` 屬性。 |
| **整合** | **TC-INT-002** | 測試所有註冊的工具是否都可呼叫 | `root_agent` 已註冊工具 | 1. 迭代 `root_agent.tools` 並檢查 | `root_agent.tools` | 所有工具都應為可呼叫的函式。 |
| **整合** | **TC-INT-003** | 測試代理是否可以成功匯入 | 模組路徑正確 | 1. 從 `finance_assistant.agent` 匯入 `root_agent` | - | 匯入成功，且匯入的代理物件不為 `None`，其 `name` 為 `finance_assistant`。 |
| **結構** | **TC-STR-001** | 測試所有匯入是否正常運作 | 專案結構正確 | 1. 使用 `importlib` 載入 `finance_assistant.agent` | - | 模組可以被找到並成功載入，不會引發 `ImportError`。 |
| **結構** | **TC-STR-002** | 測試模組是否具有預期的結構 | 模組已載入 | 1. 檢查 `finance_assistant.agent` 的屬性 | `finance_assistant.agent` | 模組應具有 `root_agent`、`calculate_compound_interest`、`calculate_loan_payment` 和 `calculate_monthly_savings` 屬性。 |
| **結構** | **TC-STR-003** | 測試主執行區段是否不會引發錯誤 | 腳本可獨立執行 | 1. 使用 `subprocess` 執行 `finance_assistant/agent.py` | - | 腳本應成功執行（回傳碼 0），且標準輸出包含 "Finance Assistant Agent" 和各工具的測試輸出。 |