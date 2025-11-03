# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## `agent` 模組測試 (`tests/test_agent.py`)

此部分涵蓋對 `agent` 模組的全面測試，確保多代理系統中各個元件的設定、結構與整合皆符合預期。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestIndividualAgents** | **TC-AGENT-001** | 測試新聞工作流程中代理的設定 | None | 1. 檢查 `news_fetcher` 的名稱、模型、描述與指令。<br>2. 檢查 `news_summarizer` 的名稱、模型、描述與指令。 | `news_fetcher` 與 `news_summarizer` 物件 | 所有屬性符合預期設定。 |
| **TestIndividualAgents** | **TC-AGENT-002** | 測試社群媒體工作流程中代理的設定 | None | 1. 檢查 `social_monitor` 的名稱、模型、描述與指令。<br>2. 檢查 `sentiment_analyzer` 的名稱、模型、描述與指令。 | `social_monitor` 與 `sentiment_analyzer` 物件 | 所有屬性符合預期設定。 |
| **TestIndividualAgents** | **TC-AGENT-003** | 測試專家工作流程中代理的設定 | None | 1. 檢查 `expert_finder` 的名稱、模型、描述與指令。<br>2. 檢查 `quote_extractor` 的名稱、模型、描述與指令。 | `expert_finder` 與 `quote_extractor` 物件 | 所有屬性符合預期設定。 |
| **TestIndividualAgents** | **TC-AGENT-004** | 測試內容建立代理的設定 | None | 1. 檢查 `article_writer`、`article_editor` 與 `article_formatter` 的屬性。 | `article_writer`, `article_editor`, `article_formatter` 物件 | 所有屬性符合預期設定。 |
| **TestIndividualAgents** | **TC-AGENT-005** | 測試所有代理是否都具有唯一的輸出鍵 | None | 1. 收集所有個別代理的 `output_key`。<br>2. 驗證所有鍵都是唯一的。 | 所有個別代理物件 | 輸出鍵無重複。 |
| **TestSequentialPipelines** | **TC-AGENT-006** | 測試新聞工作流程的結構 | None | 1. 檢查 `news_pipeline` 的名稱與描述。<br>2. 驗證其子代理為 `news_fetcher` 與 `news_summarizer`。 | `news_pipeline` 物件 | 工作流程結構與子代理皆正確。 |
| **TestSequentialPipelines** | **TC-AGENT-007** | 測試社群媒體工作流程的結構 | None | 1. 檢查 `social_pipeline` 的名稱與描述。<br>2. 驗證其子代理為 `social_monitor` 與 `sentiment_analyzer`。 | `social_pipeline` 物件 | 工作流程結構與子代理皆正確。 |
| **TestSequentialPipelines** | **TC-AGENT-008** | 測試專家工作流程的結構 | None | 1. 檢查 `expert_pipeline` 的名稱與描述。<br>2. 驗證其子代理為 `expert_finder` 與 `quote_extractor`。 | `expert_pipeline` 物件 | 工作流程結構與子代理皆正確。 |
| **TestParallelResearch** | **TC-AGENT-009** | 測試平行研究的設定 | None | 1. 驗證 `parallel_research` 為 `ParallelAgent` 的實例。<br>2. 檢查其名稱與描述。<br>3. 驗證其包含三個序列工作流程。 | `parallel_research` 物件 | 平行研究設定正確。 |
| **TestContentPublishingSystem** | **TC-AGENT-010** | 測試完整的內容發布系統 | None | 1. 驗證系統為 `SequentialAgent` 的實例。<br>2. 檢查系統名稱與描述。<br>3. 驗證系統包含正確的階段。 | `content_publishing_system` 物件 | 系統結構與設定正確。 |
| **TestRootAgent** | **TC-AGENT-011** | 測試根代理的設定 | None | 1. 驗證 `root_agent` 為 `content_publishing_system`。<br>2. 驗證 `root_agent` 為 `SequentialAgent` 的實例。 | `root_agent` 物件 | 根代理設定正確。 |
| **TestStateManagement** | **TC-AGENT-012** | 測試狀態管理與資料流 | None | 1. 驗證平行工作流程的輸出鍵。<br>2. 驗證寫作、編輯、格式化代理的指令包含正確的輸入鍵。<br>3. 檢查無循環依賴。 | 所有相關代理物件 | 狀態流與資料依賴正確。 |
| **TestAgentInstructions** | **TC-AGENT-013** | 測試代理指令的品質與完整性 | None | 1. 逐一檢查各代理的指令是否清晰、具體且包含輸出格式說明。 | 所有個別代理物件 | 指令內容符合品質要求。 |
| **TestAgentIntegration** | **TC-AGENT-014** | 測試代理整合與系統一致性 | None | 1. 驗證 `root_agent` 可無錯誤地實例化。<br>2. 檢查工作流程是否具有適用於 ADK API 的有效設定。<br>3. 驗證代理之間的狀態流已正確設定。 | `root_agent` 與相關代理物件 | 系統整合與一致性通過驗證。 |

## `imports` 模組測試 (`tests/test_imports.py`)

此部分涵蓋對專案中所有必要模組的匯入測試，確保環境設定正確且所有依賴項均可正常載入。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestImports** | **TC-IMPORTS-001** | 測試 `google.adk.agents` 是否能成功匯入 | Python 環境已設定 | 1. 執行 `from google.adk.agents import Agent, ParallelAgent, SequentialAgent`。 | None | 模組成功匯入，無 `ImportError`。 |
| **TestImports** | **TC-IMPORTS-002** | 測試 `content_publisher.agent` 是否能成功匯入 | 專案路徑已加入 `PYTHONPATH` | 1. 執行 `import content_publisher.agent`。 | None | 模組成功匯入，無 `ImportError`。 |
| **TestImports** | **TC-IMPORTS-003** | 測試 `root_agent` 是否已定義且可存取 | `content_publisher.agent` 模組可正常匯入 | 1. 執行 `from content_publisher.agent import root_agent`。<br>2. 檢查 `root_agent` 是否不為 `None`。 | None | `root_agent` 成功匯入且已定義。 |
| **TestImports** | **TC-IMPORTS-004** | 測試 `__future__ annotations` 的匯入是否正常 | Python 3.7+ 環境 | 1. 執行 `exec("from __future__ import annotations")`。 | None | 程式碼成功執行，無 `ImportError`。 |

## `structure` 模組測試 (`tests/test_structure.py`)

此部分涵蓋對專案結構的測試，確保所有必要的檔案與目錄都存在且內容符合預期。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TestProjectStructure** | **TC-STRUCT-001** | 測試 `content_publisher` 目錄是否存在 | 專案根目錄 | 1. 檢查 `content_publisher` 是否為一個目錄。 | 檔案系統 | `content_publisher` 目錄存在。 |
| **TestProjectStructure** | **TC-STRUCT-002** | 測試 `content_publisher` 內的必要檔案是否存在 | `content_publisher` 目錄存在 | 1. 檢查 `__init__.py`、`agent.py` 與 `.env.example` 是否存在。 | 檔案系統 | 所有必要檔案皆存在。 |
| **TestProjectStructure** | **TC-STRUCT-003** | 測試 `__init__.py` 是否包含正確的匯入 | `content_publisher/__init__.py` 檔案存在 | 1. 讀取檔案內容。<br>2. 檢查是否包含 `from . import agent`。 | `__init__.py` 檔案 | 檔案內容符合預期。 |
| **TestProjectStructure** | **TC-STRUCT-004** | 測試 `agent.py` 是否為有效的 Python 檔案 | `content_publisher/agent.py` 檔案存在 | 1. 讀取檔案內容。<br>2. 檢查是否包含關鍵程式碼。 | `agent.py` 檔案 | 檔案內容符合預期。 |
| **TestProjectStructure** | **TC-STRUCT-005** | 測試 `.env.example` 是否包含必要的變數 | `content_publisher/.env.example` 檔案存在 | 1. 讀取檔案內容。<br>2. 檢查是否包含必要的環境變數。 | `.env.example` 檔案 | 檔案內容符合預期。 |
| **TestTestStructure** | **TC-STRUCT-006** | 測試 `tests` 目錄與檔案結構 | 專案根目錄 | 1. 檢查 `tests` 目錄是否存在。<br>2. 檢查 `tests/__init__.py` 是否存在。<br>3. 檢查所有測試檔案是否存在。 | 檔案系統 | 測試目錄與檔案結構皆正確。 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
