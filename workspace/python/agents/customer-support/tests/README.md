# 詳細測試案例說明

## 簡介

此文件提供了客戶支援代理（Customer Support Agent）專案的詳細測試案例說明。測試涵蓋了代理設定、匯入檢查、專案結構驗證以及工具功能的實作測試。

## 代理測試 (`tests/test_agent.py`)

此部分涵蓋代理的 YAML 設定載入、屬性驗證及整合測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **YAML 設定** | **TC-AGENT-001** | 測試 root_agent.yaml 是否存在 | 無 | 1. 檢查檔案路徑是否存在 | `customer_support/root_agent.yaml` | 檔案存在 |
| **YAML 設定** | **TC-AGENT-002** | 測試從 YAML 載入代理 | `root_agent.yaml` 存在 | 1. 使用 `from_config` 載入代理 | `customer_support/root_agent.yaml` | 代理物件成功建立且不為 None |
| **YAML 設定** | **TC-AGENT-003** | 測試代理基本屬性 | 代理已載入 | 1. 檢查 `name` 屬性<br>2. 檢查 `model` 屬性<br>3. 檢查 `description` 屬性 | 無 | 名稱正確、模型為 gemini-2.0-flash、描述包含關鍵字 |
| **YAML 設定** | **TC-AGENT-004** | 測試代理指令 | 代理已載入 | 1. 檢查 `instruction` 屬性 | 無 | 指令包含 "customer support agent" 和 "available tools" |
| **YAML 設定** | **TC-AGENT-005** | 測試單一代理無子代理 | 代理已載入 | 1. 檢查 `sub_agents` 屬性 | 無 | `sub_agents` 列表長度為 0 |
| **YAML 設定** | **TC-AGENT-006** | 測試代理工具數量 | 代理已載入 | 1. 檢查 `tools` 屬性 | 無 | `tools` 列表長度為 11 |
| **YAML 設定** | **TC-AGENT-007** | 測試工具是否為函式 | 代理已載入 | 1. 遍歷 `tools` 列表<br>2. 檢查每個項目是否可呼叫 | 無 | 所有工具皆為 callable 物件 |
| **設定驗證** | **TC-AGENT-008** | 測試無效設定檔路徑 | 無 | 1. 嘗試載入不存在的設定檔 | `non_existent.yaml` | 拋出異常 |
| **設定驗證** | **TC-AGENT-009** | 測試設定載入錯誤處理 | 無 | 1. 模擬載入過程發生錯誤 | 無 | 拋出異常 |
| **代理整合** | **TC-AGENT-010** | 測試代理建立無錯誤 | ADK 環境正常 | 1. 嘗試建立代理 | `customer_support/root_agent.yaml` | 建立過程無異常 |
| **代理整合** | **TC-AGENT-011** | 測試 API 設定有效性 | GOOGLE_API_KEY 存在 | 1. 檢查模型名稱<br>2. 檢查指令長度 | 無 | 模型有效且指令長度足夠 |

## 匯入測試 (`tests/test_imports.py`)

此部分驗證所有必要的模組、套件及函式能否正確匯入。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入檢查** | **TC-IMPORT-001** | 測試 tools 套件匯入 | 專案已安裝 | 1. 匯入 `customer_support.tools` | 無 | 匯入成功不為 None |
| **匯入檢查** | **TC-IMPORT-002** | 測試 customer_tools 模組匯入 | 專案已安裝 | 1. 匯入 `customer_support.tools.customer_tools` | 無 | 匯入成功不為 None |
| **匯入檢查** | **TC-IMPORT-003** | 測試所有工具函式匯入 | 專案已安裝 | 1. 匯入所有定義的工具函式 | `check_customer_status`, `log_interaction` 等 | 所有函式皆可匯入 |
| **匯入檢查** | **TC-IMPORT-004** | 測試 ADK config utils 匯入 | Google ADK 已安裝 | 1. 匯入 `google.adk.agents.config_agent_utils` | 無 | 匯入成功不為 None |
| **匯入檢查** | **TC-IMPORT-005** | 測試 run_agent 匯入 | `run_agent.py` 存在 | 1. 匯入 `run_agent` | 無 | 匯入成功不為 None |
| **函式簽章** | **TC-IMPORT-006** | 測試工具函式可呼叫 | 工具已匯入 | 1. 檢查函式是否 callable | `check_customer_status` | 為 callable |
| **函式簽章** | **TC-IMPORT-007** | 測試工具函式回傳字典 | 工具已匯入 | 1. 呼叫函式<br>2. 檢查回傳型別 | `check_customer_status('test')` | 回傳值為 dict |

## 結構測試 (`tests/test_structure.py`)

此部分驗證專案的檔案結構、目錄組織及 YAML 設定檔的結構正確性。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRUCT-001** | 測試 root_agent.yaml 存在 | 無 | 1. 檢查檔案是否存在 | `customer_support/root_agent.yaml` | 檔案存在 |
| **專案結構** | **TC-STRUCT-002** | 測試 tools 目錄存在 | 無 | 1. 檢查目錄是否存在 | `customer_support/tools` | 目錄存在且為目錄型別 |
| **專案結構** | **TC-STRUCT-003** | 測試 tools/__init__.py 存在 | 無 | 1. 檢查檔案是否存在 | `customer_support/tools/__init__.py` | 檔案存在 |
| **專案結構** | **TC-STRUCT-004** | 測試 customer_tools.py 存在 | 無 | 1. 檢查檔案是否存在 | `customer_support/tools/customer_tools.py` | 檔案存在 |
| **專案結構** | **TC-STRUCT-005** | 測試 run_agent.py 存在 | 無 | 1. 檢查檔案是否存在 | `run_agent.py` | 檔案存在 |
| **專案結構** | **TC-STRUCT-006** | 測試 tests 目錄存在 | 無 | 1. 檢查目錄是否存在 | `tests` | 目錄存在且為目錄型別 |
| **專案結構** | **TC-STRUCT-007** | 測試所有測試檔案存在 | 無 | 1. 遍歷檢查測試檔案 | `test_agent.py`, `test_tools.py` 等 | 所有測試檔案皆存在 |
| **專案結構** | **TC-STRUCT-008** | 測試專案設定檔存在 | 無 | 1. 遍歷檢查專案檔 | `pyproject.toml`, `requirements.txt`, `Makefile` | 所有專案檔皆存在 |
| **YAML 結構** | **TC-STRUCT-009** | 測試 YAML 有效性 | `root_agent.yaml` 存在 | 1. 解析 YAML 檔案 | 無 | 解析成功且為字典 |
| **YAML 結構** | **TC-STRUCT-010** | 測試 YAML 必要欄位 | YAML 可解析 | 1. 檢查必要鍵值 | `name`, `model`, `description`, `instruction` | 所有欄位皆存在且非空 |
| **YAML 結構** | **TC-STRUCT-011** | 測試無 sub_agents 欄位 | YAML 可解析 | 1. 檢查是否無 `sub_agents` | 無 | 不包含 `sub_agents` 鍵值 |
| **YAML 結構** | **TC-STRUCT-012** | 測試 tools 欄位 | YAML 可解析 | 1. 檢查 `tools` 欄位 | 無 | `tools` 存在且為列表，長度 > 0 |
| **YAML 結構** | **TC-STRUCT-013** | 測試工具定義格式 | YAML 可解析 | 1. 檢查每個工具項目 | 無 | 每個工具為字典，且名稱正確引用模組 |
| **工具結構** | **TC-STRUCT-014** | 測試所有預期工具函式定義 | 模組可匯入 | 1. 檢查每個函式是否可呼叫 | 所有工具函式列表 | 所有函式皆定義且可呼叫 |
| **工具結構** | **TC-STRUCT-015** | 測試 tools 套件匯出 | 套件可匯入 | 1. 檢查套件屬性 | 所有工具函式名稱 | 套件匯出所有工具函式 |

## 工具測試 (`tests/test_tools.py`)

此部分針對各類工具函式進行功能驗證，包括正常情況與邊界情況。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **客戶工具** | **TC-TOOL-001** | 測試高級會員狀態 | 無 | 1. 呼叫 `check_customer_status` | `CUST-001` | 狀態成功，tier 為 premium |
| **客戶工具** | **TC-TOOL-002** | 測試標準會員狀態 | 無 | 1. 呼叫 `check_customer_status` | `CUST-999` | 狀態成功，tier 為 standard |
| **客戶工具** | **TC-TOOL-003** | 測試記錄互動 | 無 | 1. 呼叫 `log_interaction` | `CUST-001`, `inquiry`, `msg` | 狀態成功，資料正確回傳 |
| **訂單工具** | **TC-TOOL-004** | 測試取得現有訂單 | 無 | 1. 呼叫 `get_order_status` | `ORD-001` | 狀態成功，status 為 shipped |
| **訂單工具** | **TC-TOOL-005** | 測試不存在訂單 | 無 | 1. 呼叫 `get_order_status` | `ORD-999` | 狀態錯誤，包含錯誤訊息 |
| **訂單工具** | **TC-TOOL-006** | 測試追蹤現有出貨 | 無 | 1. 呼叫 `track_shipment` | `ORD-001` | 狀態成功，carrier 為 UPS |
| **訂單工具** | **TC-TOOL-007** | 測試追蹤不存在出貨 | 無 | 1. 呼叫 `track_shipment` | `ORD-999` | 狀態錯誤，包含錯誤訊息 |
| **訂單工具** | **TC-TOOL-008** | 測試成功取消訂單 | 無 | 1. 呼叫 `cancel_order` | `ORD-001`, `reason` | 狀態成功，理由正確回傳 |
| **訂單工具** | **TC-TOOL-009** | 測試取消不符資格訂單 | 無 | 1. 呼叫 `cancel_order` | `ORD-004`, `reason` | 狀態錯誤，顯示不符資格 |
| **技術工具** | **TC-TOOL-010** | 測試搜尋知識庫成功 | 無 | 1. 呼叫 `search_knowledge_base` | `login issue` | 狀態成功，回傳結果列表 > 0 |
| **技術工具** | **TC-TOOL-011** | 測試搜尋知識庫無結果 | 無 | 1. 呼叫 `search_knowledge_base` | `quantum physics` | 狀態成功，回傳結果列表為 0 |
| **技術工具** | **TC-TOOL-012** | 測試已知問題診斷 | 無 | 1. 呼叫 `run_diagnostic` | `connection` | 狀態成功，系統運作正常 |
| **技術工具** | **TC-TOOL-013** | 測試未知問題診斷 | 無 | 1. 呼叫 `run_diagnostic` | `unknown` | 狀態錯誤，無可用診斷 |
| **技術工具** | **TC-TOOL-014** | 測試建立工單 | 無 | 1. 呼叫 `create_ticket` | `CUST-001`, `issue`, `high` | 狀態成功，優先級為 high |
| **帳務工具** | **TC-TOOL-015** | 測試取得帳務歷史 | 無 | 1. 呼叫 `get_billing_history` | `CUST-001` | 狀態成功，包含交易紀錄 |
| **帳務工具** | **TC-TOOL-016** | 測試無帳務歷史 | 無 | 1. 呼叫 `get_billing_history` | `CUST-999` | 狀態錯誤，無紀錄 |
| **帳務工具** | **TC-TOOL-017** | 測試小額退款 | 無 | 1. 呼叫 `process_refund` | `ORD-001`, 50.00 | 狀態成功，approved |
| **帳務工具** | **TC-TOOL-018** | 測試大額退款(需審核) | 無 | 1. 呼叫 `process_refund` | `ORD-001`, 150.00 | 狀態錯誤，REQUIRES_APPROVAL |
| **帳務工具** | **TC-TOOL-019** | 測試更新有效付款方式 | 無 | 1. 呼叫 `update_payment_method` | `CUST-001`, `paypal` | 狀態成功，更新為 paypal |
| **帳務工具** | **TC-TOOL-020** | 測試更新無效付款方式 | 無 | 1. 呼叫 `update_payment_method` | `CUST-001`, `crypto` | 狀態錯誤，類型無效 |
| **回傳格式** | **TC-TOOL-021** | 測試所有工具回傳字典 | 無 | 1. 呼叫所有工具<br>2. 檢查回傳型別 | 所有工具 | 回傳值皆為 dict |
| **回傳格式** | **TC-TOOL-022** | 測試回傳必要欄位 | 無 | 1. 檢查回傳字典鍵值 | `status`, `report`, `data` | 包含所有必要欄位 |
| **回傳格式** | **TC-TOOL-023** | 測試錯誤回應欄位 | 無 | 1. 觸發錯誤<br>2. 檢查回傳欄位 | `get_order_status('ORD-999')` | 包含 `error` 欄位 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼，格式為 `TC-[模組]-[編號]`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
