# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 個人化學習導師 (`tests/test_agent.py`)

此部分涵蓋對個人化學習導師功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **狀態管理** | **TC-TUTOR-001** | 測試設定基本使用者偏好 | `mock_context.state` 為空字典 | 1. 呼叫 `set_user_preferences` 函式 | `language="en"`, `difficulty="intermediate"` | `status` 為 `success`，`user:language` 為 `en`，`user:difficulty_level` 為 `intermediate` |
| **狀態管理** | **TC-TUTOR-002** | 測試覆寫已存在的使用者偏好 | `mock_context.state` 包含 `user:language` 和 `user:difficulty_level` | 1. 呼叫 `set_user_preferences` 函式 | `language="fr"`, `difficulty="advanced"` | `status` 為 `success`，`user:language` 為 `fr`，`user:difficulty_level` 為 `advanced` |
| **狀態管理** | **TC-TUTOR-003** | 測試記錄一個新主題的完成狀態 | `mock_context.state` 為空字典 | 1. 呼叫 `record_topic_completion` 函式 | `topic="Python Basics"`, `score=85` | `status` 為 `success`，`topics_count` 為 1，`user:topics_covered` 包含 `Python Basics` |
| **狀態管理** | **TC-TUTOR-004** | 測試更新已存在主題的分數 | `mock_context.state` 包含 `user:topics_covered` 和 `user:quiz_scores` | 1. 呼叫 `record_topic_completion` 函式 | `topic="Python Basics"`, `score=90` | `status` 為 `success`，`topics_count` 為 1，`user:quiz_scores` 中的 `Python Basics` 更新為 90 |
| **狀態管理** | **TC-TUTOR-005** | 測試新使用者的進度查詢 | `mock_context.state` 為空字典 | 1. 呼叫 `get_user_progress` 函式 | None | `status` 為 `success`，回傳預設值 |
| **狀態管理** | **TC-TUTOR-006** | 測試已有資料的使用者進度查詢 | `mock_context.state` 包含使用者進度資料 | 1. 呼叫 `get_user_progress` 函式 | None | `status` 為 `success`，回傳正確的進度資料 |
| **會話管理** | **TC-TUTOR-007** | 測試啟動一個基本的學習會話 | `mock_context.state` 為空字典 | 1. 呼叫 `start_learning_session` 函式 | `topic="Data Structures"` | `status` 為 `success`，`current_topic` 為 `Data Structures` |
| **會話管理** | **TC-TUTOR-008** | 測試根據使用者偏好啟動學習會話 | `mock_context.state` 包含 `user:difficulty_level` | 1. 呼叫 `start_learning_session` 函式 | `topic="Algorithms"` | `status` 為 `success`，`difficulty_level` 為 `advanced` |
| **臨時狀態** | **TC-TUTOR-009** | 測試計算滿分的測驗成績 | `mock_context.state` 為空字典 | 1. 呼叫 `calculate_quiz_grade` 函式 | `correct=10`, `total=10` | `status` 為 `success`，`grade` 為 `A`，`percentage` 為 100.0 |
| **臨時狀態** | **TC-TUTOR-010** | 測試計算不及格的測驗成績 | `mock_context.state` 為空字典 | 1. 呼叫 `calculate_quiz_grade` 函式 | `correct=3`, `total=10` | `status` 為 `success`，`grade` 為 `F`，`percentage` 為 30.0 |
| **臨時狀態** | **TC-TUTOR-011** | 測試所有成績級距的邊界 | `mock_context.state` 為空字典 | 1. 呼叫 `calculate_quiz_grade` 函式 | 多組測試數據 | 回傳對應的正確成績級距 |
| **記憶體操作** | **TC-TUTOR-012** | 測試搜尋存在的學習課程 | `mock_context.state` 包含 `user:topics_covered` | 1. 呼叫 `search_past_lessons` 函式 | `query="python"` | `status` 為 `success`，`found` 為 `True` |
| **記憶體操作** | **TC-TUTOR-013** | 測試搜尋多筆符合條件的課程 | `mock_context.state` 包含多個相關主題 | 1. 呼叫 `search_past_lessons` 函式 | `query="python"` | `status` 為 `success`，`found` 為 `True`，回傳所有相關主題 |
| **記憶體操作** | **TC-TUTOR-014** | 測試搜尋不存在的學習課程 | `mock_context.state` 不包含相關主題 | 1. 呼叫 `search_past_lessons` 函式 | `query="python"` | `status` 為 `success`，`found` 為 `False` |
| **記憶體操作** | **TC-TUTOR-015** | 測試在沒有任何已完成主題的情況下進行搜尋 | `mock_context.state` 為空字典 | 1. 呼叫 `search_past_lessons` 函式 | `query="anything"` | `status` 為 `success`，`found` 為 `False` |
| **Agent 設定** | **TC-TUTOR-016** | 測試根 Agent 是否已正確設定 | None | 1. 檢查 `root_agent` 的屬性 | None | `name`, `model`, `output_key` 符合預期 |
| **Agent 設定** | **TC-TUTOR-017** | 測試 Agent 是否有正確的描述 | None | 1. 檢查 `root_agent.description` | None | 描述內容不為 None 且包含關鍵字 |
| **Agent 設定** | **TC-TUTOR-018** | 測試 Agent 是否有完整的指令 | None | 1. 檢查 `root_agent.instruction` | None | 指令內容不為 None 且包含關鍵字 |
| **Agent 設定** | **TC-TUTOR-019** | 測試 Agent 是否已具備所有必要的工具 | None | 1. 檢查 `root_agent.tools` | None | 所有預期的工具都已包含在內 |
| **整合測試** | **TC-TUTOR-020** | 測試一個完整的學習會話工作流程 | `mock_context.state` 為空字典 | 1. 依序呼叫設定偏好、啟動會話、計算成績、記錄完成、檢查進度、搜尋課程等函式 | 綜合測試數據 | 每一步驟的結果都符合預期 |
| **整合測試** | **TC-TUTOR-021** | 測試包含多個主題的工作流程 | `mock_context.state` 為空字典 | 1. 學習多個主題並記錄分數<br>2. 檢查最終進度<br>3. 搜尋課程 | 綜合測試數據 | 最終進度與搜尋結果符合預期 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。例如：`狀態管理`、`會話管理`。
*   **測試案例編號**: 唯一的測試案例識別碼。建議格式為 `TC-[模組]-[編號]`，例如 `TC-TUTOR-001`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟，應清晰且可重複。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
