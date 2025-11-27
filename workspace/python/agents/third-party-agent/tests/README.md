# 詳細測試案例文件

## 簡介

此文件提供了一個詳細的測試案例文件，旨在為 `third-party-agent` 專案建立清晰、一致且全面的測試文件。

## 代理測試 (`tests/test_agent.py`)

此部分涵蓋對第三方工具代理 (Third-Party Agent) 的配置、工具整合、專案結構與文件的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理配置與設定** | **TC-CONF-001** | 測試代理是否建立成功 | 系統環境已設定，相關模組可匯入 | 1. 檢查 root_agent 是否存在<br>2. 檢查名稱是否為 'third_party_agent'<br>3. 檢查模型是否為 'gemini-2.0-flash' | None | 代理物件成功建立，名稱與模型屬性正確 |
| **代理配置與設定** | **TC-CONF-002** | 測試代理是否擁有適當的描述 | root_agent 已初始化 | 1. 取得 root_agent.description<br>2. 檢查是否包含關鍵字 (comprehensive research, wikipedia, web search 等) | None | 描述中包含所有預期的關鍵字 |
| **代理配置與設定** | **TC-CONF-003** | 測試代理是否擁有完整的指導指令 | root_agent 已初始化 | 1. 取得 root_agent.instruction<br>2. 檢查是否包含關鍵能力說明 (wikipedia, web search, directory reading 等) | None | 指令中包含所有預期的關鍵字 |
| **代理配置與設定** | **TC-CONF-004** | 測試工具是否正確註冊 | root_agent 已初始化 | 1. 取得 root_agent.tools<br>2. 檢查工具數量 | None | 工具列表長度為 4 |
| **代理配置與設定** | **TC-CONF-005** | 測試輸出鍵值是否已配置 | root_agent 已初始化 | 1. 檢查 root_agent.output_key | None | output_key 等於 'research_response' |
| **網路搜尋工具** | **TC-WEB-001** | 測試網路搜尋工具是否能被建立 | 相關依賴套件已安裝 | 1. 呼叫 create_web_search_tool()<br>2. 檢查回傳值 | None | 回傳有效的工具物件 (非 None) |
| **網路搜尋工具** | **TC-WEB-002** | 測試網路搜尋工具是否具有正確的型別 | 相關依賴套件已安裝 | 1. 呼叫 create_web_search_tool()<br>2. 檢查物件型別 | None | 物件是 LangchainTool 的實例 |
| **網路搜尋工具** | **TC-WEB-003** | 測試網路搜尋工具是否正確配置 | 相關依賴套件已安裝 | 1. 呼叫 create_web_search_tool()<br>2. 檢查必要屬性 (name, description, func) | None | 工具物件包含所有必要屬性 |
| **匯入測試** | **TC-IMP-001** | 測試 ADK 核心匯入 | ADK 套件已安裝 | 1. 嘗試匯入 google.adk.agents.Agent | None | 匯入成功不拋出錯誤 |
| **匯入測試** | **TC-IMP-002** | 測試 LangchainTool 匯入路徑 | ADK 套件已安裝 | 1. 嘗試匯入 google.adk.tools.langchain_tool.LangchainTool | None | 匯入成功不拋出錯誤 |
| **匯入測試** | **TC-IMP-003** | 測試 LangChain 社群套件匯入 | LangChain 相關套件已安裝 | 1. 嘗試匯入 WikipediaQueryRun, DuckDuckGoSearchRun, WikipediaAPIWrapper | None | 匯入成功不拋出錯誤 |
| **匯入測試** | **TC-IMP-004** | 測試 wikipedia 套件是否可用 | wikipedia 套件已安裝 | 1. 嘗試匯入 wikipedia | None | 匯入成功不拋出錯誤 |
| **代理整合** | **TC-INT-001** | 測試代理是否能被成功匯入 | 專案模組路徑正確 | 1. 從 third_party_agent.agent 匯入 root_agent<br>2. 檢查物件與名稱 | None | 匯入成功且屬性正確 |
| **代理整合** | **TC-INT-002** | 測試代理描述是否提及所有工具能力 | root_agent 已初始化 | 1. 檢查描述與指令內容<br>2. 驗證所有工具關鍵字 | None | 描述與指令涵蓋所有工具能力 |
| **代理整合** | **TC-INT-003** | 測試 Wikipedia 工具是否具有執行能力 | root_agent 已初始化 | 1. 建立 Wikipedia 工具<br>2. 檢查 run_async 與 func 屬性 | None | 工具具備執行所需的方法與屬性 |
| **專案結構** | **TC-STR-001** | 測試模組是否具有預期的結構 | 專案結構正確 | 1. 匯入 third_party_agent<br>2. 檢查 root_agent 屬性 | None | 模組包含 root_agent |
| **專案結構** | **TC-STR-002** | 測試 __all__ 是否正確定義 | 專案結構正確 | 1. 匯入 third_party_agent<br>2. 檢查 __all__ 定義 | None | __all__ 包含 'root_agent' |
| **專案結構** | **TC-STR-003** | 測試所有內部匯入是否正確運作 | 專案結構正確 | 1. 匯入主要元件與工廠函式 | None | 所有元件皆可成功匯入 |
| **Wikipedia 工具** | **TC-WIKI-001** | 測試 Wikipedia 工具是否能被建立 | 相關依賴套件已安裝 | 1. 呼叫 create_wikipedia_tool()<br>2. 檢查回傳值 | None | 回傳有效的工具物件 (非 None) |
| **Wikipedia 工具** | **TC-WIKI-002** | 測試 Wikipedia 工具是否具有正確的型別 | 相關依賴套件已安裝 | 1. 呼叫 create_wikipedia_tool()<br>2. 檢查物件型別 | None | 物件是 LangchainTool 的實例 |
| **Wikipedia 工具** | **TC-WIKI-003** | 測試 Wikipedia 工具是否正確配置 | 相關依賴套件已安裝 | 1. 呼叫 create_wikipedia_tool()<br>2. 檢查必要屬性 (name, description, func) | None | 工具物件包含所有必要屬性 |
| **文件測試** | **TC-DOC-001** | 測試模組是否有 Docstring | None | 1. 檢查模組 __doc__ 屬性 | None | 模組包含非空的文件字串 |
| **文件測試** | **TC-DOC-002** | 測試工廠函式是否有 Docstrings | None | 1. 檢查工廠函式 __doc__ 屬性<br>2. 驗證關鍵字 | None | 函式包含正確的文件字串 |
| **文件測試** | **TC-DOC-003** | 測試代理是否有描述欄位 | root_agent 已初始化 | 1. 檢查 root_agent.description | None | 描述欄位不為空 |
| **文件測試** | **TC-DOC-004** | 測試代理是否有指導指令欄位 | root_agent 已初始化 | 1. 檢查 root_agent.instruction | None | 指令欄位不為空 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
