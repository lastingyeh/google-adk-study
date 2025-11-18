# 詳細測試案例說明

## 簡介

此文件提供了 `artifact-agent` 專案的詳細測試案例，旨在為專案建立清晰、一致且全面的測試文件。使用此文件可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 代理程式設定測試 (`tests/test_agent.py`)

此部分涵蓋對代理程式設定與基本功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理程式設定** | **TC-AGENT-001** | 測試代理程式是否有正確的名稱 | `root_agent` 已被初始化 | 1. 存取 `root_agent.name` | `None` | 名稱為 `artifact_agent` |
| **代理程式設定** | **TC-AGENT-002** | 測試代理程式是否使用正確的模型 | `root_agent` 已被初始化 | 1. 存取 `root_agent.model` | `None` | 模型為 `gemini-1.5-flash` |
| **代理程式設定** | **TC-AGENT-003** | 測試代理程式是否有描述 | `root_agent` 已被初始化 | 1. 存取 `root_agent.description` | `None` | 描述中包含 `artifact` 和 `document` |
| **代理程式設定** | **TC-AGENT-004** | 測試代理程式是否有全面的指令 | `root_agent` 已被初始化 | 1. 存取 `root_agent.instruction` | `None` | 指令中包含 `artifacts`、`document` 和 `versioning` |
| **代理程式設定** | **TC-AGENT-005** | 測試代理程式是否具備預期的工具 | `root_agent` 已被初始化 | 1. 存取 `root_agent.tools` | `None` | 工具列表中包含 `load_artifacts` |
| **代理程式設定** | **TC-AGENT-006** | 測試代理程式是否設定了多個工具 | `root_agent` 已被初始化 | 1. 檢查 `root_agent.tools` 的長度 | `None` | 工具數量大於等於 6 |

## 導入測試 (`tests/test_imports.py`)

此部分涵蓋對專案所有必要導入是否正常運作的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **依賴導入** | **TC-IMPORTS-001** | 測試 ADK 的導入是否正常 | `None` | 1. 導入 `google.adk` 相關模組 | `None` | 成功導入，無 `ImportError` |
| **依賴導入** | **TC-IMPORTS-002** | 測試 Google GenAI 的導入是否正常 | `None` | 1. 導入 `google.genai` 相關模組 | `None` | 成功導入，無 `ImportError` |
| **模組導入** | **TC-IMPORTS-003** | 測試代理程式模組的導入是否正常 | `None` | 1. 導入 `artifact_agent.agent` | `None` | 成功導入，無 `ImportError` |
| **模組導入** | **TC-IMPORTS-004** | 測試工具函式是否可以被導入 | `None` | 1. 從 `artifact_agent.agent` 導入所有工具函式 | `None` | 所有工具函式皆可被呼叫 |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案結構與設定的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **檔案系統** | **TC-STRUCT-001** | 測試專案根目錄是否存在 | `None` | 1. 檢查專案根目錄 | `None` | 目錄存在且為一個目錄 |
| **檔案系統** | **TC-STRUCT-002** | 測試 `artifact_agent` 套件是否存在 | `None` | 1. 檢查 `artifact_agent` 目錄 | `None` | 目錄存在且為一個目錄 |
| **檔案系統** | **TC-STRUCT-003** | 測試 `__init__.py` 檔案是否存在 | `None` | 1. 檢查 `artifact_agent/__init__.py`<br>2. 檢查 `tests/__init__.py` | `None` | 兩個檔案都存在 |
| **檔案系統** | **TC-STRUCT-004** | 測試 `agent.py` 檔案是否存在 | `None` | 1. 檢查 `artifact_agent/agent.py` | `None` | 檔案存在且為一個檔案 |
| **設定檔** | **TC-STRUCT-005** | 測試設定檔是否存在 | `None` | 1. 檢查 `pyproject.toml`<br>2. 檢查 `requirements.txt`<br>3. 檢查 `Makefile`<br>4. 檢查 `.env.example` | `None` | 所有檔案都存在 |
| **設定檔** | **TC-STRUCT-006** | 測試 `.env` 檔案未被提交 | `None` | 1. 檢查 `.env` 檔案是否存在 | `None` | `.env` 檔案不存在 |
| **設定檔** | **TC-STRUCT-007** | 測試 `requirements.txt` 的格式是否有效 | `None` | 1. 讀取 `requirements.txt` | `None` | 檔案內容不為空，且包含 `google-genai` 和 `google-adk` |
| **設定檔** | **TC-STRUCT-008** | 測試 `pyproject.toml` 的格式是否有效 | `None` | 1. 讀取 `pyproject.toml` | `None` | 檔案內容包含 `[build-system]`、`[project]` 等區段 |

## 工具函式測試 (`tests/test_tools.py`)

此部分涵蓋對 `artifact-agent` 中所有工具函式的單元測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ExtractTextTool** | **TC-TOOLS-001** | 測試成功的文字擷取 | `mock_tool_context` 已建立 | 1. 呼叫 `extract_text_tool` | `test_text = "..."` | `status` 為 `success`，回傳的 `data` 包含檔名、內容等資訊 |
| **ExtractTextTool** | **TC-TOOLS-002** | 測試空文字的擷取 | `mock_tool_context` 已建立 | 1. 呼叫 `extract_text_tool` | `test_text = ""` | `status` 為 `error` |
| **SummarizeDocumentTool** | **TC-TOOLS-003** | 測試成功的文件摘要 | `mock_tool_context` 已建立 | 1. 呼叫 `summarize_document_tool` | `test_text = "..."` | `status` 為 `success`，回傳的 `data` 包含摘要內容 |
| **TranslateDocumentTool** | **TC-TOOLS-004** | 測試成功的文件翻譯 | `mock_tool_context` 已建立 | 1. 呼叫 `translate_document_tool` | `test_text = "Hello world", target_lang = "Spanish"` | `status` 為 `success`，回傳的 `data` 包含翻譯後的內容 |
| **CreateFinalReportTool** | **TC-TOOLS-005** | 測試成功的最終報告建立 | `mock_tool_context` 已建立，且 `list_artifacts` 回傳兩個檔案 | 1. 呼叫 `create_final_report_tool` | `None` | `status` 為 `success`，回傳的 `data` 包含最終報告 |
| **ListArtifactsTool** | **TC-TOOLS-006** | 測試成功的 artifact 列表 | `mock_tool_context` 已建立，且 `list_artifacts` 回傳兩個檔案 | 1. 呼叫 `list_artifacts_tool` | `None` | `status` 為 `success`，回傳的 `data` 包含 artifact 列表與數量 |
| **LoadArtifactTool** | **TC-TOOLS-007** | 測試成功的 artifact 載入 | `mock_tool_context` 已建立，且 `load_artifact` 回傳一個模擬的 artifact | 1. 呼叫 `load_artifact_tool` | `filename = "test_artifact.txt"` | `status` 為 `success`，回傳的 `data` 包含 artifact 內容 |
| **ToolReturnFormats** | **TC-TOOLS-008** | 測試所有工具是否回傳字典結果 | `mock_tool_context` 已建立 | 1. 呼叫所有工具函式 | `None` | 所有工具都回傳一個字典，且包含 `status` 和 `report` 欄位 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。
*   **測試案例編號**: 唯一的測試案例識別碼。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
