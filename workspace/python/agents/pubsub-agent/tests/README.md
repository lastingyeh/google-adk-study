# 詳細測試案例報告

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 文件處理代理 - 代理測試 (`tests/test_agent.py`)

此部分涵蓋對文件處理代理系統的核心配置驗證，包括 Root Agent、子代理、工具包裝及輸出 Schema。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **協調代理設定** | **TC-AGENT-001** | 測試 root_agent 匯入 | `pubsub_agent` 套件已安裝 | 匯入 `root_agent` | 無 | 成功匯入且不為 None |
| **協調代理設定** | **TC-AGENT-002** | 測試 root_agent 實例類型 | 無 | 檢查 `root_agent` 是否為 `LlmAgent` | 無 | `isinstance` 返回 True |
| **協調代理設定** | **TC-AGENT-003** | 測試代理名稱 | 無 | 檢查 `root_agent.name` | 無 | 名稱為 "pubsub_processor" |
| **協調代理設定** | **TC-AGENT-004** | 測試代理模型 | 無 | 檢查 `root_agent.model` | 無 | 模型為 "gemini-2.5-flash" |
| **協調代理設定** | **TC-AGENT-005** | 測試代理描述 | 無 | 檢查 `root_agent.description` | 無 | 包含 "event-driven", "document processing", "coordinator" 等關鍵字 |
| **協調代理設定** | **TC-AGENT-006** | 測試代理指令 | 無 | 檢查 `root_agent.instruction` | 無 | 包含路由職責關鍵字 (financial, technical, sales, marketing) |
| **協調代理設定** | **TC-AGENT-007** | 測試代理工具 | 無 | 檢查 `root_agent.tools` | 無 | 擁有 4 個子代理工具 |
| **子代理設定** | **TC-SUB-001** | 測試子代理匯入 | 無 | 匯入各子代理 (financial, technical, sales, marketing) | 無 | 成功匯入且不為 None |
| **子代理設定** | **TC-SUB-002** | 測試子代理類型 | 無 | 檢查各子代理是否為 `LlmAgent` | 無 | `isinstance` 返回 True |
| **子代理設定** | **TC-SUB-003** | 測試子代理配置 | 無 | 檢查各子代理的名稱、模型與描述 | 無 | 設定正確 (如 "financial_analyzer", "gemini-2.5-flash") |
| **子代理設定** | **TC-SUB-004** | 測試子代理輸出 Schema | 無 | 檢查各子代理的 `output_schema` | 無 | 對應到正確的 Pydantic Class (如 `FinancialAnalysisOutput`) |
| **工具包裝** | **TC-TOOL-001** | 測試子代理工具包裝 | 無 | 檢查各工具變數 (financial_tool 等) | 無 | 均為 `AgentTool` 實例 |
| **輸出架構** | **TC-SCHEMA-001** | 測試 Pydantic Schema 定義 | 無 | 檢查各 Output Schema 的欄位定義 | 無 | 包含必要的業務欄位 (summary, entities, recommendations 等) |
| **輸出架構** | **TC-SCHEMA-002** | 測試 Schema 實例化 | 無 | 使用測試數據實例化 `EntityExtraction` 與 `DocumentSummary` | 測試數據字典 | 屬性值與輸入一致 |
| **基本功能** | **TC-FUNC-001** | 測試代理建立流程 | 無 | 嘗試匯入並建立所有代理與工具 | 無 | 無異常拋出 |
| **整合測試** | **TC-INT-001** | 測試路由策略整合 | 無 | 檢查協調者的指令中是否整合了所有子代理的路由關鍵字 | 無 | 包含所有子代理相關的決策關鍵字 |

## 匯入與模組測試 (`tests/test_imports.py`)

此部分涵蓋對專案模組結構與匯入機制的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **模組結構** | **TC-IMP-001** | 測試模組存在性 | 無 | 匯入 `pubsub_agent` 及其子模組 | 無 | 成功匯入無錯誤 |
| **模組結構** | **TC-IMP-002** | 測試 root_agent 匯出 | 無 | 從 `pubsub_agent.agent` 匯入 `root_agent` | 無 | 成功取得物件 |
| **外部匯入** | **TC-IMP-003** | 測試 ADK 匯入 | `google-adk` 已安裝 | 匯入 `google.adk.agents.Agent` | 無 | 成功匯入 |
| **外部匯入** | **TC-IMP-004** | 測試 Schema 匯入 | 無 | 匯入所有定義的 Pydantic Models | 無 | 成功匯入 |
| **模組匯出** | **TC-IMP-005** | 測試匯出物件類型 | 無 | 檢查匯出物件的繼承關係 | 無 | `root_agent` 是 `LlmAgent`，Schemas 是 `BaseModel` |
| **套件初始化** | **TC-IMP-006** | 測試 __init__.py | 無 | 匯入 `pubsub_agent` 套件 | 無 | `agent` 模組可透過套件存取 |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案檔案組織、配置檔案與基本程式碼品質的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **目錄結構** | **TC-STR-001** | 測試必要目錄存在 | 無 | 檢查 `pubsub_agent` 和 `tests` 目錄 | 無 | `os.path.isdir` 返回 True |
| **檔案結構** | **TC-STR-002** | 測試必要檔案存在 | 無 | 檢查 `__init__.py`, `agent.py`, `Makefile`, `README.md` 等 | 無 | `os.path.isfile` 返回 True |
| **配置檔案** | **TC-STR-003** | 測試 requirements.txt | 無 | 讀取檔案內容 | 無 | 包含 `google-adk` 和 `google-cloud-pubsub` |
| **配置檔案** | **TC-STR-004** | 測試 pyproject.toml | 無 | 讀取檔案內容 | 無 | 包含正確的套件名稱與依賴 |
| **配置檔案** | **TC-STR-005** | 測試 .env.example | 無 | 檢查內容格式與敏感資訊 | 無 | 包含 API Key 預留位置且無真實金鑰 |
| **程式碼品質** | **TC-STR-006** | 測試 Python 語法 | 無 | 使用 `compile()` 檢查所有 `.py` 檔案 | 無 | 無 SyntaxError |
| **程式碼品質** | **TC-STR-007** | 測試 Docstrings | 無 | 檢查 `agent.py` | 無 | 包含模組級文件字串 |
| **文件** | **TC-STR-008** | 測試 README 內容 | 無 | 檢查 `README.md` 大小與標題 | 無 | 檔案非空且包含標題 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
