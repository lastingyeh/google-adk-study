# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Agent 指令約束測試 (`tests/test_agent_instructions.py`)

此部分涵蓋對 Root Agent 指令內容的約束驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **指令約束** | **TC-INSTR-001** | 驗證 Root Agent 指令約束 | `agent.py` 檔案存在 | 1. 讀取 `agent.py` 檔案內容<br>2. 檢查是否包含禁止特定字面語句的指令<br>3. 檢查是否包含儲存偏好設定的指令<br>4. 檢查是否包含使用真實 URL 的指令 | `agent.py` 檔案內容 | 指令中必須禁止 "Engaging Narrative:"，必須包含 "Preference Manager" 呼叫要求，必須包含 "real URLs" 使用要求 |

## Callback 與類型測試 (`tests/test_callback_and_types.py`)

此部分涵蓋對 Grounding Metadata Callback 及型別定義的單元測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Grounding Metadata Callback** | **TC-CB-001** | 驗證 Callback 建立 | 無 | 1. 呼叫 `create_grounding_callback` | verbose=True/False | Callback 函式成功建立且可呼叫 |
| **Grounding Metadata Callback** | **TC-CB-002** | 驗證網域名稱提取 | 無 | 1. 呼叫 `_extract_domain` | 各種 URL 格式 | 正確提取網域名稱 (例如: decathlon.com.hk) |
| **Grounding Metadata Callback** | **TC-CB-003** | 驗證信賴度計算 | 無 | 1. 呼叫 `_calculate_confidence` | 來源數量 (0, 1, 2, 3, 5) | 正確回傳信賴度等級 (low, medium, high) |
| **Grounding Metadata Callback** | **TC-CB-004** | 驗證無候選回應處理 | Mock 環境 | 1. 模擬無候選回應的 LLM Response<br>2. 執行 Callback | 空回應 | 回傳 None，不引發錯誤 |
| **Grounding Metadata Callback** | **TC-CB-005** | 驗證 Metadata 提取 | Mock 環境 | 1. 模擬包含 Grounding Metadata 的回應<br>2. 執行 Callback | Mock Metadata (Sources, Supports) | 正確提取並更新 `callback_context.state` 中的 `_grounding_sources` 和 `_grounding_metadata` |
| **Tool Types** | **TC-TYPE-001** | 驗證 ToolResult 結構 | 無 | 1. 建立成功的 ToolResult 字典 | Status="success", Data={"value": 42} | 字典欄位存取正確 |
| **Tool Types** | **TC-TYPE-002** | 驗證 ToolResult 錯誤結構 | 無 | 1. 建立失敗的 ToolResult 字典 | Status="error", Error="ValueError" | 字典包含 error 欄位 |
| **Preferences Types** | **TC-PREF-TYPE-001** | 驗證 save_preferences 回傳型別 | Mock Context | 1. 呼叫 `save_preferences` | Preference Data | 回傳符合 ToolResult 結構的字典，且 context state 被更新 |
| **Preferences Types** | **TC-PREF-TYPE-002** | 驗證 get_preferences 回傳型別 | Mock Context | 1. 呼叫 `get_preferences` | Existing Preferences in Context | 回傳包含 preferences data 的 ToolResult |

## 端對端測試 (`tests/test_e2e.py`)

此部分涵蓋 Commerce Agent 的完整使用者場景與流程測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **使用者場景** | **TC-E2E-001** | 新運動員完整流程 | 資料庫初始化 | 1. 設定偏好 (Running, Cycling)<br>2. 執行搜尋查詢<br>3. 加入最愛商品 | User ID: "new_athlete" | 偏好、歷史記錄與最愛商品皆正確儲存 |
| **使用者場景** | **TC-E2E-002** | 回訪客戶流程 | 資料庫初始化 | 1. 初始設定與搜尋<br>2. 更新偏好 (新增 Hiking)<br>3. 新增互動記錄 | User ID: "returning_customer" | 偏好包含新舊興趣，歷史記錄包含兩次 Session |
| **使用者場景** | **TC-E2E-003** | 多使用者隔離測試 | 資料庫初始化 | 1. 使用者 Alice 設定偏好與最愛<br>2. 使用者 Bob 設定偏好與最愛<br>3. 驗證彼此資料互不干擾 | User Alice, User Bob | Alice 與 Bob 的資料完全獨立 |
| **互動追蹤** | **TC-E2E-004** | 互動概況建立測試 | 資料庫初始化 | 1. 建立偏好<br>2. 新增多筆搜尋記錄<br>3. 取得 Engagement Profile | User ID: "engaged_user" | Profile 包含正確的互動次數、喜好類別與品牌 |
| **錯誤恢復** | **TC-E2E-005** | 無效更新恢復測試 | 資料庫初始化 | 1. 執行有效更新<br>2. 嘗試無效更新 (缺少欄位)<br>3. 驗證資料狀態 | User ID: "recovery_user" | 操作回傳 error，但原始資料保持完整 |
| **錯誤恢復** | **TC-E2E-006** | 缺失使用者預設值測試 | 資料庫初始化 | 1. 取得不存在使用者的偏好 | User ID: "nonexistent_user" | 回傳預設偏好設定 |
| **資料持久性** | **TC-E2E-007** | 操作間資料持久性測試 | 資料庫初始化 | 1. 設定初始偏好<br>2. 執行其他操作 (歷史、最愛)<br>3. 驗證偏好未被覆蓋 | User ID: "persistence_user" | 偏好設定在其他操作後保持不變 |

## 整合測試 (`tests/test_integration.py`)

此部分涵蓋 Agent 設定、資料庫與工具的整合測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-INT-001** | Search Agent 存在與設定驗證 | 無 | 1. 檢查 `search_agent` 物件 | 無 | Agent 名稱與 Model 設定正確 (gemini-2.5-flash) |
| **Agent 設定** | **TC-INT-002** | Preferences Agent 存在驗證 | 無 | 1. 檢查 `preferences_agent` 物件 | 無 | Agent 名稱正確 |
| **Agent 設定** | **TC-INT-003** | Root Agent 存在與設定驗證 | 無 | 1. 檢查 `root_agent` 物件 | 無 | Agent 名稱正確，包含正確數量的工具 (2個) |
| **Agent 設定** | **TC-INT-004** | Agent 指令驗證 | 無 | 1. 檢查所有 Agent 的 instruction 屬性 | 無 | 所有 Agent 皆有設定指令 |
| **資料庫整合** | **TC-INT-005** | 資料庫初始化測試 | 無 | 1. 呼叫 `init_database()` | 無 | 執行成功不拋出例外 |
| **資料庫整合** | **TC-INT-006** | 資料庫多使用者測試 | 資料庫已初始化 | 1. 儲存 User 1 偏好<br>2. 儲存 User 2 偏好<br>3. 分別讀取驗證 | User 1, User 2 | 兩位使用者的資料正確且獨立 |
| **工具整合** | **TC-INT-007** | 偏好工具可呼叫性 | 無 | 1. 呼叫 `manage_user_preferences` | Action: "get" | 回傳包含 status, report, data 的結果 |
| **工具整合** | **TC-INT-008** | 策展工具可呼叫性 | 無 | 1. 呼叫 `curate_products` | Empty list | 回傳成功狀態 |
| **匯入路徑** | **TC-INT-009** | 模組匯入測試 | 無 | 1. 嘗試匯入主要 Agent, Tools, Models | `commerce_agent` package | 所有元件皆可成功匯入 |

## 工具單元測試 (`tests/test_tools.py`)

此部分涵蓋各個別工具函式的獨立單元測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **偏好工具** | **TC-TOOL-001** | 新使用者偏好取得 | 資料庫初始化 | 1. `manage_user_preferences` (get) | New User ID | 回傳預設偏好結構 |
| **偏好工具** | **TC-TOOL-002** | 更新使用者偏好 | 資料庫初始化 | 1. `manage_user_preferences` (update) | Sports, Price Range, Brands | 偏好更新成功 |
| **偏好工具** | **TC-TOOL-003** | 取得現有使用者偏好 | 資料庫初始化 | 1. 儲存偏好<br>2. 讀取偏好 | User ID | 讀取到的偏好與儲存一致 |
| **偏好工具** | **TC-TOOL-004** | 新增歷史記錄 | 資料庫初始化 | 1. `manage_user_preferences` (add_history) | Session ID, Query | 歷史記錄新增成功 |
| **偏好工具** | **TC-TOOL-005** | 新增最愛商品 | 資料庫初始化 | 1. `manage_user_preferences` (add_favorite) | Product Info | 最愛商品新增成功 |
| **偏好工具** | **TC-TOOL-006** | 取得最愛商品 | 資料庫初始化 | 1. 新增多個最愛<br>2. `manage_user_preferences` (get_favorites) | User ID | 回傳正確數量的最愛商品 |
| **偏好工具** | **TC-TOOL-007** | 無效操作處理 | 資料庫初始化 | 1. `manage_user_preferences` | Invalid Action | 回傳 error 狀態與報告 |
| **產品策展** | **TC-TOOL-008** | 空列表策展 | 無 | 1. `curate_products` | 空列表 | 回傳空列表 |
| **產品策展** | **TC-TOOL-009** | 基本策展 (無過濾) | 無 | 1. `curate_products` | 產品列表, limit=2 | 回傳數量不超過限制 |
| **產品策展** | **TC-TOOL-010** | 價格過濾策展 | 無 | 1. `curate_products` | 產品列表 + 價格範圍 (50-100) | 只回傳價格範圍內的產品 |
| **產品策展** | **TC-TOOL-011** | 品牌優先策展 | 無 | 1. `curate_products` | 產品列表 + 喜好品牌 | 回傳結果包含偏好品牌產品 |
| **產品策展** | **TC-TOOL-012** | 數量限制測試 | 無 | 1. `curate_products` | 產品列表, limit=1 | 回傳數量遵守限制 |
| **產品敘事** | **TC-TOOL-013** | 產生產品敘事 | 無 | 1. `generate_product_narrative` | 產品資料 | 回傳包含產品名稱的敘事樣板 |
| **產品敘事** | **TC-TOOL-014** | 帶有 Context 的敘事 | 無 | 1. `generate_product_narrative` | 產品資料 + User Context | 回傳內容關聯使用者興趣 |
| **產品敘事** | **TC-TOOL-015** | 缺失資料錯誤處理 | 無 | 1. `generate_product_narrative` | 空產品資料 | 回傳 error 狀態 |
