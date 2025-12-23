# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為 ADK Interactions Agent 專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 模組導入測試 (`tests/test_agent.py`)

此部分涵蓋對模組導入結構的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestImports** | **TC-IMP-001** | 測試套件是否正確導入 | 已安裝套件 | 1. 導入 adk_interactions_agent.root_agent<br>2. 驗證 root_agent 是否存在 | None | root_agent 不為 None |
| **TestImports** | **TC-IMP-002** | 測試工具是否正確導入 | 已安裝套件 | 1. 導入各工具函數<br>2. 驗證是否為可呼叫物件 | get_current_weather, calculate_expression, search_knowledge_base | 各工具函數均為 callable |
| **TestImports** | **TC-IMP-003** | 測試代理模組導入 | 已安裝套件 | 1. 導入代理相關工廠與函數<br>2. 驗證是否正確導入 | create_interactions_enabled_agent, create_standard_agent, AgentFactory | 各函數與類別均能正確導入 |

## 工具函數測試 (`tests/test_agent.py`)

此部分涵蓋對個別工具功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestToolFunctions** | **TC-TOOL-001** | 測試天氣工具返回有效的結構 | 無 | 1. 呼叫 get_current_weather | "Tokyo, Japan" | 返回 success 狀態且包含 report, temperature 等欄位 |
| **TestToolFunctions** | **TC-TOOL-002** | 測試天氣工具使用華氏單位 | 無 | 1. 呼叫 get_current_weather 並指定單位為 fahrenheit | "New York, USA", units="fahrenheit" | 返回 success 狀態且單位為 °F |
| **TestToolFunctions** | **TC-TOOL-003** | 測試天氣工具使用攝氏單位 | 無 | 1. 呼叫 get_current_weather 並指定單位為 celsius | "London, UK", units="celsius" | 返回 success 狀態且單位為 °C |
| **TestToolFunctions** | **TC-TOOL-004** | 測試基本算術運算 | 無 | 1. 呼叫 calculate_expression 進行加法 | "2 + 2" | 返回 success 狀態且結果為 4 |
| **TestToolFunctions** | **TC-TOOL-005** | 測試百分比計算 | 無 | 1. 呼叫 calculate_expression 進行百分比計算 | "15% of 250" | 返回 success 狀態且結果為 37.5 |
| **TestToolFunctions** | **TC-TOOL-006** | 測試簡單百分比 | 無 | 1. 呼叫 calculate_expression 轉換百分比 | "50%" | 返回 success 狀態且結果為 0.5 |
| **TestToolFunctions** | **TC-TOOL-007** | 測試複雜表達式 | 無 | 1. 呼叫 calculate_expression 進行混合運算 | "(10 + 5) * 2" | 返回 success 狀態且結果為 30 |
| **TestToolFunctions** | **TC-TOOL-008** | 測試除以零的處理 | 無 | 1. 呼叫 calculate_expression 除以零 | "10 / 0" | 返回 error 狀態且錯誤訊息包含 "zero" |
| **TestToolFunctions** | **TC-TOOL-009** | 測試無效表達式的處理 | 無 | 1. 呼叫 calculate_expression 輸入無效字串 | "invalid expression!@#" | 返回 error 狀態 |
| **TestToolFunctions** | **TC-TOOL-010** | 測試知識庫搜尋返回結果 | 無 | 1. 呼叫 search_knowledge_base | "machine learning" | 返回 success 狀態且 results 列表不為空 |
| **TestToolFunctions** | **TC-TOOL-011** | 測試 max_results 參數 | 無 | 1. 呼叫 search_knowledge_base 並限制數量 | "computing", max_results=2 | 返回 results 數量小於等於 2 |
| **TestToolFunctions** | **TC-TOOL-012** | 測試搜尋結果結構 | 無 | 1. 呼叫 search_knowledge_base<br>2. 檢查每個結果項目 | "AI" | 每個結果均包含 id, title, snippet |

## 代理配置測試 (`tests/test_agent.py`)

此部分涵蓋對代理配置與工廠模式的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestAgentConfiguration** | **TC-CONF-001** | 測試 root_agent 是否已定義 | 環境變數 GOOGLE_API_KEY 已設定 | 1. 導入 root_agent<br>2. 檢查屬性 | env: GOOGLE_API_KEY="test_key" | root_agent 存在且名稱正確 |
| **TestAgentConfiguration** | **TC-CONF-002** | 測試 root_agent 是否配置了工具 | 環境變數 GOOGLE_API_KEY 已設定 | 1. 檢查 root_agent.tools | env: GOOGLE_API_KEY="test_key" | tools 列表長度為 3 |
| **TestAgentConfiguration** | **TC-CONF-003** | 測試 root_agent 是否有描述 | 環境變數 GOOGLE_API_KEY 已設定 | 1. 檢查 root_agent.description | env: GOOGLE_API_KEY="test_key" | description 屬性存在且不為空 |
| **TestAgentConfiguration** | **TC-CONF-004** | 測試 root_agent 是否有指令 | 環境變數 GOOGLE_API_KEY 已設定 | 1. 檢查 root_agent.instruction | env: GOOGLE_API_KEY="test_key" | instruction 屬性存在且不為空 |
| **TestAgentConfiguration** | **TC-CONF-005** | 測試 AgentFactory 建立互動代理 | 環境變數 GOOGLE_API_KEY 已設定 | 1. 呼叫 AgentFactory.interactions_agent() | env: GOOGLE_API_KEY="test_key" | 返回有效的代理物件 |
| **TestAgentConfiguration** | **TC-CONF-006** | 測試 AgentFactory 建立標準代理 | 環境變數 GOOGLE_API_KEY 已設定 | 1. 呼叫 AgentFactory.standard_agent() | env: GOOGLE_API_KEY="test_key" | 返回標準代理物件 |
| **TestAgentConfiguration** | **TC-CONF-007** | 測試 AgentFactory 建立 Pro 代理 | 環境變數 GOOGLE_API_KEY 已設定 | 1. 呼叫 AgentFactory.pro_agent() | env: GOOGLE_API_KEY="test_key" | 返回 Pro 代理物件 |

## 實用工具函數測試 (`tests/test_agent.py`)

此部分涵蓋對輔助工具函數的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestUtilities** | **TC-UTIL-001** | 測試 Markdown 格式化 | 無 | 1. 呼叫 format_response 使用 markdown 風格 | style="markdown" | 返回包含 markdown 語法的字串 |
| **TestUtilities** | **TC-UTIL-002** | 測試純文字格式化 | 無 | 1. 呼叫 format_response 使用 plain 風格 | style="plain" | 返回純文字報告 |
| **TestUtilities** | **TC-UTIL-003** | 測試 JSON 格式化 | 無 | 1. 呼叫 format_response 使用 json 風格 | style="json" | 返回有效的 JSON 字串 |

## 演示模組測試 (`tests/test_agent.py`)

此部分涵蓋對演示模組功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestDemoModule** | **TC-DEMO-001** | 測試演示模組導入 | 無 | 1. 導入演示模組相關函數 | None | 函數均可正確導入 |
| **TestDemoModule** | **TC-DEMO-002** | 測試設置了密鑰的環境檢查 | 環境變數 GOOGLE_API_KEY 已設定 | 1. 呼叫 check_environment() | env: GOOGLE_API_KEY="test_key" | 返回 True |
| **TestDemoModule** | **TC-DEMO-003** | 測試沒有密鑰的環境檢查 | 環境變數 GOOGLE_API_KEY 未設定 | 1. 清除環境變數<br>2. 呼叫 check_environment() | env: GOOGLE_API_KEY removed | 返回 False |

## 邊界案例測試 (`tests/test_agent.py`)

此部分涵蓋對異常輸入與邊界條件的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestEdgeCases** | **TC-EDGE-001** | 測試地點為空的天氣查詢 | 無 | 1. 呼叫 get_current_weather 傳入空字串 | "" | 返回 success 狀態 (模擬行為) |
| **TestEdgeCases** | **TC-EDGE-002** | 測試空表達式的計算 | 無 | 1. 呼叫 calculate_expression 傳入空字串 | "" | 返回 error 狀態 |
| **TestEdgeCases** | **TC-EDGE-003** | 測試空查詢的搜尋 | 無 | 1. 呼叫 search_knowledge_base 傳入空字串 | "" | 返回 success 狀態且有預設結果 |
| **TestEdgeCases** | **TC-EDGE-004** | 測試帶有特殊字符的計算 | 無 | 1. 呼叫 calculate_expression 傳入特殊字符 | "abc!@#$%" | 返回 error 狀態 |

## 整合測試 (`tests/test_agent.py`)

此部分涵蓋需實際 API 連線的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestIntegration** | **TC-INT-001** | 測試 SDK 中是否有 Interactions API 可用 | 安裝 google-genai 且設定 API Key | 1. 建立 genai.Client<br>2. 檢查 interactions 或 models 屬性 | env: GOOGLE_API_KEY real key | Client 物件包含 interactions 屬性 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
