# 暫停/恢復調用代理（Pause/Resume Agent）測試案例說明

## 簡介

此文件提供了暫停/恢復調用代理的詳細測試案例說明，涵蓋代理配置、工具功能、模組導入以及應用程式設定的驗證。

## 代理測試 (`tests/test_agent.py`)

此部分涵蓋對暫停/恢復調用代理的全面測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理配置** | **TC-AGENT-001** | 驗證代理名稱 | 無 | 檢查 `root_agent.name` | `root_agent.name` | 應為 `"pause_resume_agent"` |
| **代理配置** | **TC-AGENT-002** | 驗證使用模型 | 無 | 檢查 `root_agent.model` | `root_agent.model` | 應為 `"gemini-2.0-flash"` |
| **代理配置** | **TC-AGENT-003** | 驗證描述內容 | 無 | 檢查 `root_agent.description` 是否包含關鍵字 | `root_agent.description` | 應包含 "pause" 與 "resume" |
| **代理配置** | **TC-AGENT-004** | 驗證指令內容 | 無 | 檢查 `root_agent.instruction` 是否包含檢查點說明 | `root_agent.instruction` | 應包含 "checkpoint" |
| **代理配置** | **TC-AGENT-005** | 驗證工具配置數量 | 無 | 檢查 `root_agent.tools` 的長度 | `len(root_agent.tools)` | 應為 3 |
| **代理配置** | **TC-AGENT-006** | 驗證代理匯出 | 無 | 重新導入 `root_agent` 並檢查 | `exported_agent` | 代理應成功匯出且名稱正確 |
| **代理工具** | **TC-TOOL-001** | 處理有效數據塊 | 無 | 調用 `process_data_chunk` | `"hello world test"` | 狀態為 "success"，字數應為 3 |
| **代理工具** | **TC-TOOL-002** | 處理多行數據塊 | 無 | 調用 `process_data_chunk` | `"line1\nline2\nline3"` | 狀態為 "success"，處理行數應為 3 |
| **代理工具** | **TC-TOOL-003** | 處理空數據塊 | 無 | 調用 `process_data_chunk` | `""` | 狀態為 "error"，錯誤訊息為 "Empty data string" |
| **代理工具** | **TC-TOOL-004** | 驗證有效檢查點 | 無 | 調用 `validate_checkpoint` | `"checkpoint_state"` | 狀態為 "success"，`is_valid` 為 True |
| **代理工具** | **TC-TOOL-005** | 驗證無效檢查點 | 無 | 調用 `validate_checkpoint` | `""` | 狀態為 "error"，`is_valid` 為 False |
| **代理工具** | **TC-TOOL-006** | 獲取處理中恢復提示 | 無 | 調用 `get_resumption_hint` | `"processing data"` | 狀態為 "success"，提示包含 "processing" |
| **代理工具** | **TC-TOOL-007** | 獲取驗證中恢復提示 | 無 | 調用 `get_resumption_hint` | `"validation check"` | 狀態為 "success"，提示包含 "validation" |
| **代理工具** | **TC-TOOL-008** | 獲取分析中恢復提示 | 無 | 調用 `get_resumption_hint` | `"analysis phase"` | 狀態為 "success"，提示包含 "analysis" |
| **代理工具** | **TC-TOOL-009** | 獲取未知情境恢復提示 | 無 | 調用 `get_resumption_hint` | `"unknown context"` | 狀態為 "success"，提示應建議重新開始 |
| **模組導入** | **TC-IMPORT-001** | 導入根代理 | 無 | 執行 `from pause_resume_agent import root_agent` | `root_agent` | 應成功導入 |
| **模組導入** | **TC-IMPORT-002** | 導入代理模組 | 無 | 執行 `from pause_resume_agent import agent` | `agent` | 應成功導入 |
| **模組導入** | **TC-IMPORT-003** | 導入應用程式 | 無 | 執行 `from app import app` | `app` | 應成功導入 |
| **應用配置** | **TC-APP-001** | 驗證應用名稱 | 無 | 檢查 `app.name` | `app.name` | 應為 `"pause_resume_app"` |
| **應用配置** | **TC-APP-002** | 驗證根代理配置 | 無 | 檢查 `app.root_agent` | `app.root_agent.name` | 應配置正確的代理名稱 |
| **應用配置** | **TC-APP-003** | 驗證恢復配置存在 | 無 | 檢查 `app.resumability_config` | `app.resumability_config` | 配置應存在且不為 None |
| **應用配置** | **TC-APP-004** | 驗證恢復功能啟用 | 無 | 檢查 `is_resumable` 狀態 | `app.resumability_config.is_resumable` | 應為 True |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。格式為 `TC-[模組]-[編號]`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
