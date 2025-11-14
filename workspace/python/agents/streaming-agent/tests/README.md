# 詳細測試案例說明

## 簡介

此文件提供了 `streaming-agent` 專案的詳細測試案例，旨在建立清晰、一致且全面的測試文件。使用此文件可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## 代理程式功能測試 (`tests/test_agent.py`)

此部分涵蓋對代理程式設定、串流功能及工具函式的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理程式設定** | **TC-AGENT-001** | 測試串流代理程式是否以正確的設定建立 | None | 1. 呼叫 `create_streaming_agent()`<br>2. 檢查回傳的代理程式物件 | None | 代理程式物件不為 None，且 `name`、`description`、`model` 符合預期設定 |
| **代理程式設定** | **TC-AGENT-002** | 測試 `root_agent` 是否已正確實例化 | None | 1. 檢查 `root_agent` 物件 | None | `root_agent` 物件不為 None，且具有 `name` 和 `model` 屬性 |
| **串流功能** | **TC-AGENT-003** | 測試基本串流回應功能 | None | 1. 定義一個非空查詢字串<br>2. 呼叫 `stream_agent_response()` 並迭代接收到的 `chunks`<br>3. 組合 `chunks` 成完整回應 | `query = "Hello world"` | 回應的 `chunks` 數量大於 0，且組合後的回應文字不為空 |
| **串流功能** | **TC-AGENT-004** | 測試使用空查詢進行串流 | None | 1. 定義一個空查詢字串<br>2. 呼叫 `stream_agent_response()` 並迭代接收到的 `chunks`<br>3. 組合 `chunks` 成完整回應 | `query = ""` | 系統能優雅地處理空查詢，並回傳一個有效的回應 |
| **串流功能** | **TC-AGENT-005** | 測試完整回應功能 | None | 1. 定義一個測試查詢字串<br>2. 呼叫 `get_complete_response()` | `query = "Test query"` | 回傳一個字串型別的回應，且內容不為空 |
| **工具函式** | **TC-AGENT-006** | 測試串流資訊工具 | None | 1. 呼叫 `format_streaming_info()` | None | 回傳的結果中 `status` 為 `success`，且 `data` 包含 `streaming_modes`、`benefits`、`use_cases` 等資訊 |
| **工具函式** | **TC-AGENT-007** | 測試使用預設參數的效能分析 | None | 1. 呼叫 `analyze_streaming_performance()` | None | 回傳的結果中 `status` 為 `success`，且 `data` 包含 `estimated_chunks`、`estimated_total_time_seconds` 等資訊 |
| **工具函式** | **TC-AGENT-008** | 測試使用自訂查詢長度的效能分析 | None | 1. 呼叫 `analyze_streaming_performance()` 並傳入自訂長度 | `query_length = 500` | 回傳的結果中 `status` 為 `success`，且 `estimated_chunks` 和 `estimated_total_time_seconds` 為正數 |
| **工具函式** | **TC-AGENT-009** | 測試使用零查詢長度的效能分析 | None | 1. 呼叫 `analyze_streaming_performance()` 並傳入 0 | `query_length = 0` | 回傳的結果中 `status` 為 `success`，且 `estimated_chunks` 至少為 1 |
| **整合測試** | **TC-AGENT-010** | 測試代理程式是否擁有預期的工具 | None | 1. 檢查 `root_agent.tools` 屬性 | None | `root_agent` 擁有 2 個工具，且工具名稱符合預期 |
| **整合測試** | **TC-AGENT-011** | 測試代理程式是否具有適當的指令 | None | 1. 檢查 `root_agent.instruction` 內容 | None | 指令內容包含 `helpful`、`streaming`、`conversational` 等關鍵字 |

## 匯入與套件結構測試 (`tests/test_imports.py`)

此部分涵蓋對套件匯入及結構的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入測試** | **TC-IMPORTS-001** | 測試 `streaming_agent` 套件是否可以被匯入 | None | 1. 嘗試 `import streaming_agent` | None | 匯入成功，無 `ImportError` |
| **匯入測試** | **TC-IMPORTS-002** | 測試 `root_agent` 是否可以被匯入 | None | 1. 嘗試 `from streaming_agent import root_agent` | None | 匯入成功，無 `ImportError` |
| **結構測試** | **TC-IMPORTS-003** | 測試所有預期的匯出項目是否都可用 | None | 1. 從 `streaming_agent` 匯入所有預期項目 | None | 所有項目 (`root_agent`, `stream_agent_response` 等) 均不為 None |
| **結構測試** | **TC-IMPORTS-004** | 測試代理程式模組是否具有預期的結構 | None | 1. 匯入 `streaming_agent.agent`<br>2. 檢查模組是否包含必要的函式/類別 | None | 模組包含 `create_streaming_agent`、`root_agent` 等預期成員 |
| **結構測試** | **TC-IMPORTS-005** | 測試工具函式是否可用 | None | 1. 從 `streaming_agent.agent` 匯入工具函式 | None | `format_streaming_info` 和 `analyze_streaming_performance` 均為可呼叫的函式 |
| **結構測試** | **TC-IMPORTS-006** | 測試套件是否包含版本資訊 | None | 1. 匯入 `streaming_agent`<br>2. 檢查 `__file__` 屬性 | None | `streaming_agent` 套件具有 `__file__` 屬性 |
| **匯入測試** | **TC-IMPORTS-007** | 測試匯入時不會引發任何錯誤 | None | 1. 匯入 `streaming_agent` 及其主要成員 | None | 整個匯入過程無任何例外拋出 |
| **匯入測試** | **TC-IMPORTS-008** | 測試沒有循環匯入問題 | None | 1. 使用 `importlib.reload` 重新載入 `streaming_agent` | None | 重新載入成功，無循環匯入錯誤 |

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案結構與設定檔的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **結構測試** | **TC-STRUCT-001** | 測試專案是否具有預期的目錄結構 | None | 1. 檢查 `streaming_agent` 和 `tests` 目錄是否存在<br>2. 檢查所有必要的專案檔案是否存在 | None | 所有必要的目錄和檔案都存在於專案中 |
| **設定檔測試** | **TC-STRUCT-002** | 測試 `.env.example` 是否具有必要的結構 | None | 1. 讀取 `.env.example` 檔案內容<br>2. 檢查是否包含必要的環境變數 | None | 檔案中包含 `GOOGLE_API_KEY` 和 `GOOGLE_GENAI_USE_VERTEXAI` |
| **設定檔測試** | **TC-STRUCT-003** | 測試 `pyproject.toml` 是否具有必要的結構 | None | 1. 讀取 `pyproject.toml` 檔案內容<br>2. 檢查是否包含必要的區段和專案名稱 | None | 檔案中包含 `[build-system]`、`[project]` 等區段，且專案名稱為 `streaming_agent` |
| **設定檔測試** | **TC-STRUCT-004** | 測試 `requirements.txt` 是否包含必要的依賴項 | None | 1. 讀取 `requirements.txt` 檔案內容<br>2. 檢查是否包含必要的依賴項 | None | 檔案中包含 `google-genai` 和 `pytest` |
| **設定檔測試** | **TC-STRUCT-005** | 測試 `Makefile` 是否包含必要的目標 | None | 1. 讀取 `Makefile` 檔案內容<br>2. 檢查是否包含必要的目標 | None | 檔案中包含 `setup`、`dev`、`test` 等目標 |
| **結構測試** | **TC-STRUCT-006** | 測試 `agent.py` 是否具有必要的結構 | None | 1. 讀取 `agent.py` 檔案內容<br>2. 檢查是否包含必要的函式/變數 | None | 檔案中包含 `root_agent`、`create_streaming_agent` 等 |
| **結構測試** | **TC-STRUCT-007** | 測試 `__init__.py` 是否包含必要的匯出 | None | 1. 讀取 `streaming_agent/__init__.py` 檔案內容<br>2. 檢查是否包含必要的匯出 | None | 檔案中包含 `root_agent`、`stream_agent_response` 等 |
| **安全性測試** | **TC-STRUCT-008** | 測試 `.env` 檔案不存在 | None | 1. 檢查 `streaming_agent/.env` 檔案是否存在 | None | `.env` 檔案不應存在於專案中 |
| **文件測試** | **TC-STRUCT-009** | 測試 `README.md` 是否存在 | None | 1. 檢查 `README.md` 檔案是否存在且不為空 | None | `README.md` 存在且內容不為空 |
| **結構測試** | **TC-STRUCT-010** | 測試測試檔案是否結構正確 | None | 1. 讀取各測試檔案內容<br>2. 檢查是否包含測試函式或類別 | None | 所有測試檔案都包含 `def test_` 或 `class Test` 結構 |

---

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。例如：`代理程式設定`、`串流功能`。
*   **測試案例編號**: 唯一的測試案例識別碼。格式為 `TC-[模組]-[編號]`，例如 `TC-AGENT-001`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟，應清晰且可重複。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。
