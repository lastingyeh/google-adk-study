# 詳細測試案例文件

## 簡介

此文件提供了一個詳細的測試案例說明，旨在為 `Best Practices Agent` 專案建立清晰、一致且全面的測試文件。此文件涵蓋了代理功能、匯入驗證及專案結構的測試。

## 代理功能測試 (`tests/test_agent.py`)

此部分涵蓋對最佳實踐代理及其工具的測試，包含配置、驗證、重試、斷路器、快取、批次處理及監控等功能。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理配置** | **TC-AGENT-001** | 測試 root_agent 是否已正確定義 | 代理模組已載入 | 檢查 `root_agent` 是否不為 None | None | `root_agent` 物件存在 |
| **代理配置** | **TC-AGENT-002** | 測試代理是否具有正確的名稱 | 代理模組已載入 | 檢查 `root_agent.name` | None | 名稱為 "best_practices_agent" |
| **代理配置** | **TC-AGENT-003** | 測試代理是否使用正確的模型 | 代理模組已載入 | 檢查 `root_agent.model` | None | 模型為 "gemini-2.5-flash" |
| **代理配置** | **TC-AGENT-004** | 測試代理是否有描述 | 代理模組已載入 | 檢查 `root_agent.description` | None | 描述存在且包含 "production-ready" |
| **代理配置** | **TC-AGENT-005** | 測試代理是否有指令 | 代理模組已載入 | 檢查 `root_agent.instruction` | None | 指令存在且不為空 |
| **代理配置** | **TC-AGENT-006** | 測試代理是否具有所有必需的工具 | 代理模組已載入 | 檢查 `root_agent.tools` 列表 | None | 包含所有 7 個預期工具 |
| **驗證** | **TC-VALID-001** | 測試有效電子郵件的驗證 | 驗證工具可用 | 呼叫 `validate_input_tool` | email="user@example.com", priority="normal" | 狀態為 'success'，返回驗證後數據 |
| **驗證** | **TC-VALID-002** | 測試無效電子郵件的驗證 | 驗證工具可用 | 呼叫 `validate_input_tool` | email="invalid-email", priority="normal" | 狀態為 'error' |
| **驗證** | **TC-VALID-003** | 測試無效優先級的驗證 | 驗證工具可用 | 呼叫 `validate_input_tool` | priority="super-urgent" | 狀態為 'error' |
| **驗證** | **TC-VALID-004** | 測試驗證是否阻擋危險模式 (SQL Injection) | 驗證工具可用 | 呼叫 `validate_input_tool` | text="DROP TABLE users" | 狀態為 'error'，包含 'dangerous' 警示 |
| **驗證** | **TC-VALID-005** | 測試驗證是否阻擋 XSS 攻擊嘗試 | 驗證工具可用 | 呼叫 `validate_input_tool` | text="<script>alert('xss')</script>" | 狀態為 'error' |
| **驗證** | **TC-VALID-006** | 測試驗證是否拒絕空文字 | 驗證工具可用 | 呼叫 `validate_input_tool` | text="" | 狀態為 'error' |
| **驗證** | **TC-VALID-007** | 測試 InputRequest Pydantic 模型 | Pydantic 模組可用 | 建立 `InputRequest` 物件 | 各種有效與無效參數 | 有效參數建立成功，無效參數拋出 ValueError |
| **重試邏輯** | **TC-RETRY-001** | 測試重試邏輯最終能否成功 | 重試工具可用 | 呼叫 `retry_with_backoff_tool` | max_retries=5 | 最終狀態包含 'status'，有嘗試記錄 |
| **重試邏輯** | **TC-RETRY-002** | 測試重試是否遵守最大重試次數 | 重試工具可用 | 呼叫 `retry_with_backoff_tool` | max_retries=1 | 結果包含 'report' |
| **重試邏輯** | **TC-RETRY-003** | 測試重試是否包含計時資訊 | 重試工具可用 | 呼叫 `retry_with_backoff_tool` | max_retries=2 | 結果包含 'total_time_ms' |
| **斷路器** | **TC-CB-001** | 測試斷路器呼叫成功的情況 | 斷路器工具可用 | 呼叫 `circuit_breaker_call_tool` | simulate_failure=False | 狀態為 'success' |
| **斷路器** | **TC-CB-002** | 測試斷路器呼叫失敗的情況 | 斷路器工具可用 | 呼叫 `circuit_breaker_call_tool` | simulate_failure=True | 狀態為 'error' |
| **斷路器** | **TC-CB-003** | 直接測試 CircuitBreaker 類別 | CircuitBreaker 類別可用 | 實例化並模擬失敗呼叫 | failure_threshold=2 | 達到閾值後狀態變為 OPEN |
| **斷路器** | **TC-CB-004** | 測試 CircuitState 列舉 | CircuitState 列舉可用 | 檢查列舉值 | None | 值為 'closed', 'open', 'half_open' |
| **快取** | **TC-CACHE-001** | 測試快取的設定和獲取操作 | 快取工具可用 | 1. `set` 操作<br>2. `get` 操作 | key="test_key", value="test_value" | set 成功，get 成功且命中快取 |
| **快取** | **TC-CACHE-002** | 測試快取未命中場景 | 快取工具可用 | 執行 `get` 操作 | key="nonexistent_key" | 狀態成功但 'cache_hit' 為 False |
| **快取** | **TC-CACHE-003** | 測試快取統計資訊 | 快取工具可用 | 執行 `stats` 操作 | operation="stats" | 返回包含 hits/misses 的統計資訊 |
| **快取** | **TC-CACHE-004** | 測試快取設定是否需要值 | 快取工具可用 | 執行 `set` 操作但不給 value | key="test_key" | 狀態為 'error' |
| **快取** | **TC-CACHE-005** | 直接測試 CachedDataStore 類別 | CachedDataStore 類別可用 | 測試 set/get 及 TTL | ttl_seconds=1 | 在 TTL 內可獲取值，統計正確 |
| **批次處理** | **TC-BATCH-001** | 測試項目的批次處理 | 批次工具可用 | 呼叫 `batch_process_tool` | items=["item1", "item2", "item3"] | 處理 3 個項目，狀態成功 |
| **批次處理** | **TC-BATCH-002** | 測試單個項目的批次處理 | 批次工具可用 | 呼叫 `batch_process_tool` | items=["single_item"] | 處理 1 個項目，狀態成功 |
| **批次處理** | **TC-BATCH-003** | 測試空列表的批次處理 | 批次工具可用 | 呼叫 `batch_process_tool` | items=[] | 狀態為 'error' |
| **批次處理** | **TC-BATCH-004** | 測試批次處理是否報告效率 | 批次工具可用 | 呼叫 `batch_process_tool` | items=["a", "b", "c", "d", "e"] | 結果包含 'efficiency_gain' |
| **監控** | **TC-MON-001** | 測試健康檢查工具 | 健康檢查工具可用 | 呼叫 `health_check_tool` | None | 狀態為 'success'，包含健康狀態 |
| **監控** | **TC-MON-002** | 測試指標檢索 | 指標工具可用 | 呼叫 `get_metrics_tool` | None | 狀態為 'success'，包含指標數據 |
| **監控** | **TC-MON-003** | 直接測試 MetricsCollector 類別 | MetricsCollector 類別可用 | 記錄請求並獲取指標 | latency, error | 統計數據正確反映記錄 |
| **整合測試** | **TC-INT-001** | 測試使用多個工具的完整工作流程 | 所有工具可用 | 依序執行驗證、快取、批次處理、健康檢查 | 綜合數據 | 所有步驟皆成功 |
| **整合測試** | **TC-INT-002** | 測試跨多個操作的錯誤處理 | 所有工具可用 | 執行無效的驗證、快取、批次操作，最後檢查健康 | 無效數據 | 各別操作失敗，但健康檢查仍成功 |
| **效能測試** | **TC-PERF-001** | 測試驗證是否迅速完成 | 驗證工具可用 | 呼叫 `validate_input_tool` | 一般數據 | 執行時間小於 1000ms |
| **效能測試** | **TC-PERF-002** | 測試批次處理是否有效率 | 批次工具可用 | 呼叫 `batch_process_tool` | 10 個項目 | 批次時間 <= 預估順序時間 |

## 匯入測試 (`tests/test_imports.py`)

此部分涵蓋對專案依賴及模組匯入的測試，確保環境設置正確。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入驗證** | **TC-IMP-001** | 測試代理模組是否可以被匯入 | 專案已安裝 | 匯入 `best_practices_agent` | None | 無 ImportError，物件不為 None |
| **匯入驗證** | **TC-IMP-002** | 測試 Google ADK 是否可以被匯入 | google-adk 已安裝 | 匯入 `google.adk.agents` | None | 無 ImportError，Agent 類別存在 |
| **匯入驗證** | **TC-IMP-003** | 測試 Pydantic 是否可以被匯入 | pydantic 已安裝 | 匯入 `pydantic` | None | 無 ImportError，BaseModel 存在 |
| **匯入驗證** | **TC-IMP-004** | 測試 Google GenAI 是否可以被匯入 | google-genai 已安裝 | 匯入 `google.genai` | None | 無 ImportError，types 存在 |
| **匯入驗證** | **TC-IMP-005** | 測試所有工具是否可以從代理模組匯入 | 代理模組完整 | 從 `agent` 模組匯入所有工具函式 | None | 所有工具函式皆可成功匯入 |
| **匯入驗證** | **TC-IMP-006** | 測試支援的類別是否可以被匯入 | 代理模組完整 | 從 `agent` 模組匯入支援類別 | None | 所有類別 (CircuitBreaker 等) 皆可成功匯入 |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案檔案結構及配置文件的測試，確保專案符合規範。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **結構驗證** | **TC-STRUC-001** | 測試必需的檔案和目錄是否存在 | 專案根目錄存在 | 檢查 README, requirements, toml, Makefile, env 等檔案及目錄 | 檔案路徑 | 所有必需檔案及目錄皆存在 |
| **結構驗證** | **TC-STRUC-002** | 測試 requirements.txt 是否包含必要的依賴 | requirements.txt 存在 | 讀取檔案內容並檢查關鍵字 | google-genai, google-adk, pydantic | 包含所有關鍵依賴套件 |
| **結構驗證** | **TC-STRUC-003** | 測試 pyproject.toml 是否正確配置 | pyproject.toml 存在 | 讀取檔案內容並檢查關鍵字 | 專案名稱及依賴 | 包含正確的專案配置資訊 |
| **結構驗證** | **TC-STRUC-004** | 測試 .env.example 是否存在且包含必需的變數 | .env.example 存在 | 讀取檔案內容並檢查變數 | GOOGLE_API_KEY | 包含必要的環境變數範例 |
| **結構驗證** | **TC-STRUC-005** | 測試 Makefile 是否包含必需的目標 | Makefile 存在 | 讀取檔案內容並檢查目標 | setup, dev, test, clean, demo | 包含所有標準化操作指令 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
