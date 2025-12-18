# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Context Compaction Agent 測試 (`tests/test_agent.py`)

此部分涵蓋對 Context Compaction Agent 的結構、配置、工具功能及應用程式整合的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 配置** | **TC-CC-CFG-001** | 測試 root_agent 是否正確定義 | 無 | 1. 驗證 root_agent 物件是否存在<br>2. 驗證 root_agent 具有 name 屬性 | None | root_agent 非 None 且具有 name 屬性 |
| **Agent 配置** | **TC-CC-CFG-002** | 測試 Agent 是否具有正確名稱 | root_agent 已定義 | 1. 驗證 agent 名稱是否為 'context_compaction_agent' | None | 名稱正確 |
| **Agent 配置** | **TC-CC-CFG-003** | 測試 Agent 是否使用正確的模型 | root_agent 已定義 | 1. 驗證模型是否設定為 'gemini-2.0-flash' | None | 模型正確 |
| **Agent 配置** | **TC-CC-CFG-004** | 測試 Agent 是否有具意義的描述 | root_agent 已定義 | 1. 驗證描述屬性是否存在<br>2. 驗證描述中包含 'context compaction' 關鍵字 | None | 描述存在且包含關鍵字 |
| **Agent 配置** | **TC-CC-CFG-005** | 測試 Agent 是否有完整的指示說明 | root_agent 已定義 | 1. 驗證 instruction 屬性是否存在<br>2. 驗證指示長度大於 100 字元 | None | 指示存在且長度充足 |
| **Agent 配置** | **TC-CC-CFG-006** | 測試 Agent 是否配置了工具 | root_agent 已定義 | 1. 驗證 tools 屬性是否存在<br>2. 驗證工具列表不為空<br>3. 驗證至少包含 2 個工具 | None | tools 存在且數量 >= 2 |
| **Agent 配置** | **TC-CC-CFG-007** | 測試 Agent 工具是否具有預期的名稱 | root_agent 已定義 | 1. 取得所有工具名稱<br>2. 驗證包含 'summarize_text'<br>3. 驗證包含 'calculate_complexity' | None | 包含預期的工具名稱 |
| **工具功能** | **TC-CC-TOOL-001** | 測試 summarize_text 工具運作正確 | 工具可匯入 | 1. 使用長文本呼叫 summarize_text<br>2. 檢查回傳狀態與內容 | long_text = "x" * 300 | status="success", summary 長度 < 輸入長度 |
| **工具功能** | **TC-CC-TOOL-002** | 測試 summarize_text 處理短文本的情況 | 工具可匯入 | 1. 使用短文本呼叫 summarize_text<br>2. 檢查回傳狀態與內容 | short_text = "Hello world" | status="success", summary == 輸入文本 |
| **工具功能** | **TC-CC-TOOL-003** | 測試 calculate_complexity 工具運作正確 | 工具可匯入 | 1. 使用複雜問題呼叫 calculate_complexity<br>2. 檢查回傳狀態與內容 | complex_q = "What is the best way..." | status="success", level in [low, medium, high] |
| **工具功能** | **TC-CC-TOOL-004** | 測試 calculate_complexity 處理簡單輸入的情況 | 工具可匯入 | 1. 使用簡單問候呼叫 calculate_complexity<br>2. 檢查回傳狀態與等級 | simple_q = "Hi" | status="success", level == "low" |
| **工具功能** | **TC-CC-TOOL-005** | 測試 calculate_complexity 處理中等輸入的情況 | 工具可匯入 | 1. 使用中等問題呼叫 calculate_complexity<br>2. 檢查回傳狀態與等級 | medium_q = "How do you use..." | status="success", level in [low, medium] |
| **模組匯入** | **TC-CC-IMP-001** | 測試 agent 模組匯入成功 | 環境配置正確 | 1. 嘗試匯入 context_compaction_agent.agent<br>2. 驗證匯入物件 | None | 模組匯入成功 (非 None) |
| **模組匯入** | **TC-CC-IMP-002** | 測試 root_agent 可被匯入 | 環境配置正確 | 1. 從模組匯入 root_agent<br>2. 驗證物件名稱 | None | root_agent 匯入成功且名稱正確 |
| **模組匯入** | **TC-CC-IMP-003** | 測試工具可被匯入 | 環境配置正確 | 1. 匯入 summarize_text 與 calculate_complexity<br>2. 驗證是否可呼叫 | None | 工具可匯入且為 callable |
| **App 配置** | **TC-CC-APP-001** | 測試 app 配置可被匯入 | 環境配置正確 | 1. 從 app 模組匯入 app 物件<br>2. 驗證物件 | None | app 匯入成功 (非 None) |
| **App 配置** | **TC-CC-APP-002** | 測試 app 是否配置了 root_agent | app 已匯入 | 1. 驗證 app 物件具有 root_agent 屬性 | None | app.root_agent 存在 |
| **App 配置** | **TC-CC-APP-003** | 測試 EventsCompactionConfig 可被匯入 | 環境配置正確 | 1. 從 google.adk.apps.app 匯入 EventsCompactionConfig | None | 類別匯入成功 |
| **App 配置** | **TC-CC-APP-004** | 測試 EventsCompactionConfig 可被建立 | 類別可匯入 | 1. 實例化 EventsCompactionConfig<br>2. 驗證屬性值 | interval=5, overlap=1 | 屬性值設定正確 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。例如：`使用者身份驗證`、`API 整合`。
*   **測試案例編號**: 唯一的測試案例識別碼。建議格式為 `TC-[模組]-[編號]`，例如 `TC-AUTH-001`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟，應清晰且可重複。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
