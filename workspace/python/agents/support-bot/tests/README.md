# 詳細測試案例文件

## 簡介

此文件提供了一個詳細的測試案例文件，旨在為 Support Bot 專案建立清晰、一致且全面的測試說明。

## Support Bot Agent 測試 (`tests/test_agent.py`)

此部分涵蓋 Agent 設定、工具功能、回傳格式以及知識庫與工單系統的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 root_agent 是否已定義且可存取 | 專案環境已設定 | 驗證 root_agent 物件 | None | Agent 物件存在 |
| **Agent 設定** | **TC-AGENT-002** | 測試 Agent 名稱 | None | 檢查 root_agent.name | None | 名稱為 'support_bot' |
| **Agent 設定** | **TC-AGENT-003** | 測試 Agent 使用正確的模型 | None | 檢查 root_agent.model | None | 模型為 'gemini-2.5-flash' |
| **Agent 設定** | **TC-AGENT-004** | 測試 Agent 是否有描述 | None | 檢查 root_agent.description | None | 描述為字串且長度 > 10 |
| **Agent 設定** | **TC-AGENT-005** | 測試 Agent 是否有指示 (instruction) | None | 檢查 root_agent.instruction | None | 指示為字串且長度 > 50 |
| **Agent 設定** | **TC-AGENT-006** | 測試 Agent 是否剛好有 2 個工具 | None | 檢查 len(root_agent.tools) | None | 工具數量為 2 |
| **Agent 設定** | **TC-AGENT-007** | 測試 Agent 工具是否為可呼叫的函式 | None | 迭代檢查 root_agent.tools | None | 每個工具皆為 callable |
| **知識庫搜尋** | **TC-KB-001** | 測試搜尋密碼重設相關文章 | 知識庫已初始化 | 呼叫 search_knowledge_base | "password reset" | status為success且包含相關文章 |
| **知識庫搜尋** | **TC-KB-002** | 測試搜尋休假政策相關文章 | 知識庫已初始化 | 呼叫 search_knowledge_base | "vacation" | 標題包含 'Vacation' |
| **知識庫搜尋** | **TC-KB-003** | 測試搜尋費用報告相關文章 | 知識庫已初始化 | 呼叫 search_knowledge_base | "expense" | 標題包含 'Expense' |
| **知識庫搜尋** | **TC-KB-004** | 測試搜尋遠端工作相關文章 | 知識庫已初始化 | 呼叫 search_knowledge_base | "remote work" | 標題包含 'Remote' |
| **知識庫搜尋** | **TC-KB-005** | 測試搜尋 IT 支援相關文章 | 知識庫已初始化 | 呼叫 search_knowledge_base | "IT support" | 標題包含 'IT' |
| **知識庫搜尋** | **TC-KB-006** | 測試搜尋無相符項目 | 知識庫已初始化 | 呼叫 search_knowledge_base | "nonexistent topic xyz" | status為success, article為None, report包含 'No articles found' |
| **知識庫搜尋** | **TC-KB-007** | 測試搜尋不分大小寫 | 知識庫已初始化 | 呼叫 search_knowledge_base | "PASSWORD", "password" | 兩者皆回傳 success |
| **知識庫搜尋** | **TC-KB-008** | 測試搜尋回傳完整的文章內容 | 知識庫已初始化 | 呼叫 search_knowledge_base | "password" | 包含標題、內容且內容長度 > 50 |
| **知識庫搜尋** | **TC-KB-009** | 測試搜尋回傳格式是否正確 | 知識庫已初始化 | 呼叫 search_knowledge_base | "vacation" | 包含 status 和 report 欄位 |
| **知識庫搜尋** | **TC-KB-010** | 測試搜尋能優雅地處理錯誤 | None | 呼叫 search_knowledge_base | None | 不崩潰，回傳包含 status |
| **建立工單** | **TC-TICKET-001** | 測試建立普通優先順序的工單 | None | 呼叫 create_support_ticket | subject="VPN...", priority="normal" | 工單 ID 以 'TKT-' 開頭, priority 為 'normal' |
| **建立工單** | **TC-TICKET-002** | 測試建立高優先順序的工單 | None | 呼叫 create_support_ticket | priority="high" | priority 為 'high' |
| **建立工單** | **TC-TICKET-003** | 測試建立緊急優先順序的工單 | None | 呼叫 create_support_ticket | priority="urgent" | priority 為 'urgent' |
| **建立工單** | **TC-TICKET-004** | 測試建立預設優先順序的工單 | None | 呼叫 create_support_ticket | 不指定 priority | priority 預設為 'normal' |
| **建立工單** | **TC-TICKET-005** | 測試建立無效優先順序的工單 | None | 呼叫 create_support_ticket | priority="invalid" | status 為 'error', report 包含 'Invalid priority' |
| **建立工單** | **TC-TICKET-006** | 測試工單建立的回傳格式 | None | 呼叫 create_support_ticket | priority="normal" | 包含 status, report, ticket 詳情 |
| **建立工單** | **TC-TICKET-007** | 測試每張工單都有唯一的 ID | None | 建立兩張工單 | "Test 1", "Test 2" | 兩張工單 ID 不同 |
| **建立工單** | **TC-TICKET-008** | 測試建立的工單會被儲存 | None | 建立工單並檢查 TICKETS 字典 | "Test", "Description" | ID 存在於 TICKETS 中 |
| **建立工單** | **TC-TICKET-009** | 測試建立的工單包含時間戳記 | None | 檢查已建立工單 | None | 包含 'created_at' 欄位 |
| **建立工單** | **TC-TICKET-010** | 測試新工單的狀態為開啟 | None | 檢查已建立工單 | None | status 為 'open' |
| **回傳格式** | **TC-FORMAT-001** | 測試搜尋結果包含必要欄位 | None | 呼叫 search_knowledge_base | "test" | 包含 'status', 'report' |
| **回傳格式** | **TC-FORMAT-002** | 測試建立工單包含必要欄位 | None | 呼叫 create_support_ticket | "Test", "Desc" | 包含 'status', 'report', 'ticket' |
| **回傳格式** | **TC-FORMAT-003** | 測試所有結果都有字串報告 | None | 檢查搜尋與工單結果 | None | 'report' 為非空字串 |
| **知識庫資料** | **TC-DATA-001** | 測試知識庫已有文章 | None | 檢查 KNOWLEDGE_BASE 長度 | None | 長度 > 0 |
| **知識庫資料** | **TC-DATA-002** | 測試知識庫包含預期的文章 | None | 檢查 KNOWLEDGE_BASE keys | None | 包含 password_reset, vacation_policy 等 |
| **知識庫資料** | **TC-DATA-003** | 測試所有文章都包含必要欄位 | None | 迭代檢查每篇文章 | None | 包含 title, content, tags |

## 匯入與模組測試 (`tests/test_imports.py`)

此部分涵蓋 Support Bot Agent 的匯入與模組可用性測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組匯入** | **TC-IMPORT-001** | 測試 root_agent 可從 support_bot 模組匯入 | 專案環境已設定 | from support_bot import root_agent | None | root_agent 不為 None |
| **模組匯入** | **TC-IMPORT-002** | 測試 root_agent 可直接從 agent.py 匯入 | 專案環境已設定 | from support_bot.agent import root_agent | None | root_agent 不為 None |
| **模組匯入** | **TC-IMPORT-003** | 測試工具函式可被匯入 | 專案環境已設定 | 匯入 search_knowledge_base, create_support_ticket | None | 函式不為 None |
| **Agent 屬性** | **TC-IMPORT-004** | 測試 Agent 具有正確的名稱 | Agent 已匯入 | 檢查 root_agent.name | None | 名稱為 "support_bot" |
| **Agent 屬性** | **TC-IMPORT-005** | 測試 Agent 使用正確的模型 | Agent 已匯入 | 檢查 root_agent.model | None | 包含 "gemini" |
| **Agent 屬性** | **TC-IMPORT-006** | 測試 Agent 已設定工具 | Agent 已匯入 | 檢查 root_agent.tools | None | tools 屬性存在且長度 > 0 |
| **Agent 屬性** | **TC-IMPORT-007** | 測試 Agent 有描述 | Agent 已匯入 | 檢查 root_agent.description | None | description 存在且非空 |
| **Agent 屬性** | **TC-IMPORT-008** | 測試 Agent 有指示 | Agent 已匯入 | 檢查 root_agent.instruction | None | instruction 存在且非空 |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋專案目錄與檔案結構的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **目錄結構** | **TC-STRUCT-001** | 測試專案根目錄存在 | None | 解析 __file__ 路徑 | None | 專案根目錄存在 |
| **目錄結構** | **TC-STRUCT-002** | 測試 support_bot 模組目錄存在 | None | 檢查 'support_bot' 目錄 | None | 目錄存在 |
| **檔案結構** | **TC-STRUCT-003** | 測試 support_bot/__init__.py 存在 | None | 檢查 __init__.py 檔案 | None | 檔案存在 |
| **檔案結構** | **TC-STRUCT-004** | 測試 support_bot/agent.py 存在 | None | 檢查 agent.py 檔案 | None | 檔案存在 |
| **目錄結構** | **TC-STRUCT-005** | 測試 tests 目錄存在 | None | 檢查 'tests' 目錄 | None | 目錄存在 |
| **檔案結構** | **TC-STRUCT-006** | 測試 .env.example 存在 | None | 檢查 .env.example 檔案 | None | 檔案存在 |
| **檔案結構** | **TC-STRUCT-007** | 測試 pyproject.toml 存在於專案根目錄 | None | 檢查 pyproject.toml | None | 檔案存在 |
| **檔案結構** | **TC-STRUCT-008** | 測試 requirements.txt 存在於專案根目錄 | None | 檢查 requirements.txt | None | 檔案存在 |
| **檔案結構** | **TC-STRUCT-009** | 測試 Makefile 存在於專案根目錄 | None | 檢查 Makefile | None | 檔案存在 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
