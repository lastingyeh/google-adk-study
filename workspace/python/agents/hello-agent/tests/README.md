# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## Agent 模組測試 (`tests/test_agent.py`)

此部分涵蓋對 Agent 設定與基本功能的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-001** | 測試 `root_agent` 是否可以被匯入 | Python 環境已設定 | 1. 匯入 `hello_agent.agent.root_agent` | `None` | `root_agent` 成功匯入，不為 `None` |
| **Agent 設定** | **TC-AGENT-002** | 測試 `root_agent` 是否為 `Agent` 的一個實例 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent` 的類型 | `None` | `root_agent` 是 `google.adk.agents.Agent` 的實例 |
| **Agent 設定** | **TC-AGENT-003** | 測試 Agent 是否有正確的名稱 | `root_agent` 已成功匯入 | 1. 讀取 `root_agent.name` 屬性 | `None` | 名稱為 "hello_assistant" |
| **Agent 設定** | **TC-AGENT-004** | 測試 Agent 是否有正確的模型 | `root_agent` 已成功匯入 | 1. 讀取 `root_agent.model` 屬性 | `None` | 模型為 "gemini-2.0-flash" |
| **Agent 設定** | **TC-AGENT-005** | 測試 Agent 是否有描述 | `root_agent` 已成功匯入 | 1. 讀取 `root_agent.description` 屬性 | `None` | 描述包含 "friendly AI assistant" |
| **Agent 設定** | **TC-AGENT-006** | 測試 Agent 是否有指令 | `root_agent` 已成功匯入 | 1. 讀取 `root_agent.instruction` 屬性 | `None` | 指令包含 "warm and helpful assistant" 和 "Greet users enthusiastically" |
| **Agent 設定** | **TC-AGENT-007** | 測試指令的長度是否合理 | `root_agent` 已成功匯入 | 1. 檢查 `root_agent.instruction` 的長度 | `None` | 長度介於 50 到 1000 個字元之間 |
| **Agent 功能** | **TC-AGENT-008** | 使用模擬的 Agent 類別測試 Agent 的建立 | `unittest.mock.patch` 可用 | 1. 模擬 `google.adk.agents.Agent` 類別<br>2. 重新載入 `hello_agent.agent` 模組<br>3. 驗證 `Agent` 類別是否以正確的參數被呼叫 | `name`: 'hello_assistant'<br>`model`: 'gemini-2.0-flash'<br>`description`: 包含 'friendly'<br>`instruction`: 包含 'warm and helpful' | `Agent` 類別被呼叫一次，且參數符合預期 |
| **Agent 整合** | **TC-AGENT-009** | 測試 Agent 是否可以在不引發例外的情況下被建立 | 真實的 ADK 環境 | 1. 匯入 `hello_agent.agent.root_agent` | `None` | 程式碼執行無誤，沒有引發例外 |
| **Agent 整合** | **TC-AGENT-010** | 測試 Agent 的設定對於 API 呼叫是否有效 | `GOOGLE_API_KEY` 環境變數已設定 | 1. 檢查 `model` 和 `instruction` 屬性是否存在且合理<br>2. 驗證 `model` 是否為已知的 Gemini 模型 | `None` | 屬性存在，指令長度大於 20，且模型為有效的 Gemini 模型之一 |

---

## 匯入模組測試 (`tests/test_imports.py`)

此部分涵蓋對專案必要模組匯入功能的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **匯入測試** | **TC-IMPORT-001** | 測試是否可以從 `google.adk.agents` 匯入 `Agent` | Python 環境已設定 | 1. 執行 `from google.adk.agents import Agent` | `None` | `Agent` 類別成功匯入，不為 `None` |
| **匯入測試** | **TC-IMPORT-002** | 測試是否可以匯入 `hello_agent` 模組 | 專案路徑已加入 Python Path | 1. 執行 `import hello_agent` | `None` | `hello_agent` 模組成功匯入，不為 `None` |
| **匯入測試** | **TC-IMPORT-003** | 測試是否可以從 `hello_agent` 匯入 `agent` 模組 | `hello_agent` 模組可被存取 | 1. 執行 `from hello_agent import agent` | `None` | `agent` 模組成功匯入，不為 `None` |
| **匯入測試** | **TC-IMPORT-004** | 測試 `root_agent` 是否在 `agent` 模組中被定義 | `hello_agent.agent` 模組可被存取 | 1. 執行 `from hello_agent.agent import root_agent` | `None` | `root_agent` 成功匯入，不為 `None` |
| **匯入測試** | **TC-IMPORT-005** | 測試 `__future__ annotations` 的匯入是否有效 | `hello_agent/agent.py` 檔案存在 | 1. 讀取 `agent.py` 檔案內容<br>2. 解析 AST 語法樹<br>3. 檢查是否存在 `from __future__ import annotations` | `None` | `annotations` 成功從 `__future__` 匯入 |

### **欄位說明**

*   **群組**: 測試案例所屬的功能子群組或類別。例如：`Agent 設定`、`Agent 功能`。
*   **測試案例編號**: 唯一的測試案例識別碼。建議格式為 `TC-[模組]-[編號]`，例如 `TC-AGENT-001`。
*   **描述**: 對此測試案例目標的簡潔說明。
*   **前置條件**: 執行測試前系統或環境必須處於的狀態。
*   **測試步驟**: 執行測試所需遵循的具體步驟，應清晰且可重複。
*   **測試數據**: 在測試步驟中使用的具體輸入數據。
*   **預期結果**: 在成功執行測試步驟後，系統應顯示的確切結果或狀態。

---

## 專案結構測試 (`tests/test_structure.py`)

此部分涵蓋對專案結構是否符合 ADK 慣例的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **專案結構** | **TC-STRUCT-001** | 測試 `hello_agent` 目錄是否存在 | 檔案系統可存取 | 1. 檢查 `hello_agent` 是否為一個目錄 | `None` | `hello_agent` 目錄存在 |
| **專案結構** | **TC-STRUCT-002** | 測試 `hello_agent` 中是否存在 `__init__.py` | `hello_agent` 目錄存在 | 1. 檢查 `hello_agent/__init__.py` 是否為一個檔案 | `None` | `__init__.py` 檔案存在 |
| **專案結構** | **TC-STRUCT-003** | 測試 `hello_agent` 中是否存在 `agent.py` | `hello_agent` 目錄存在 | 1. 檢查 `hello_agent/agent.py` 是否為一個檔案 | `None` | `agent.py` 檔案存在 |
| **專案結構** | **TC-STRUCT-004** | 測試 `hello_agent` 中是否存在 `.env.example` | `hello_agent` 目錄存在 | 1. 檢查 `hello_agent/.env.example` 是否為一個檔案 | `None` | `.env.example` 檔案存在 |
| **專案結構** | **TC-STRUCT-005** | 測試 `__init__.py` 的內容是否正確 | `hello_agent/__init__.py` 檔案存在 | 1. 讀取檔案內容並去除頭尾空白 | `None` | 內容為 "from . import agent" |
| **專案結構** | **TC-STRUCT-006** | 測試 `agent.py` 是否為有效的 Python 檔案 | `hello_agent/agent.py` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含特定 Python 程式碼 | `None` | 檔案非空，且包含 `from __future__ import annotations`、`from google.adk.agents import Agent` 和 `root_agent = Agent(` |
| **專案結構** | **TC-STRUCT-007** | 測試 `.env.example` 是否包含必要的設定 | `hello_agent/.env.example` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含特定環境變數 | `None` | 內容包含 `GOOGLE_GENAI_USE_VERTEXAI=FALSE`、`GOOGLE_API_KEY=` 和 API 金鑰說明 |
| **測試結構** | **TC-STRUCT-008** | 測試 `tests` 目錄是否存在 | 檔案系統可存取 | 1. 檢查 `tests` 是否為一個目錄 | `None` | `tests` 目錄存在 |
| **測試結構** | **TC-STRUCT-009** | 測試 `tests/__init__.py` 是否存在 | `tests` 目錄存在 | 1. 檢查 `tests/__init__.py` 是否為一個檔案 | `None` | `__init__.py` 檔案存在 |
| **測試結構** | **TC-STRUCT-010** | 測試所有測試檔案是否存在 | `tests` 目錄存在 | 1. 遍歷測試檔案列表<br>2. 檢查每個檔案是否存在於 `tests/` 目錄下 | `['test_agent.py', 'test_imports.py', 'test_structure.py']` | 所有指定的測試檔案都存在 |
| **根目錄檔案** | **TC-STRUCT-011** | 測試 `README.md` 是否存在 | 檔案系統可存取 | 1. 檢查 `README.md` 是否為一個檔案 | `None` | `README.md` 檔案存在 |
| **根目錄檔案** | **TC-STRUCT-012** | 測試 `Makefile` 是否存在 | 檔案系統可存取 | 1. 檢查 `Makefile` 是否為一個檔案 | `None` | `Makefile` 檔案存在 |
| **根目錄檔案** | **TC-STRUCT-013** | 測試 `requirements.txt` 是否存在 | 檔案系統可存取 | 1. 檢查 `requirements.txt` 是否為一個檔案 | `None` | `requirements.txt` 檔案存在 |
| **根目錄檔案** | **TC-STRUCT-014** | 測試 `README.md` 是否有基本內容 | `README.md` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查內容長度和關鍵字 | `None` | 內容長度大於 100，且包含 "Tutorial 01" 和 "Hello World Agent" |
| **根目錄檔案** | **TC-STRUCT-015** | 測試 `Makefile` 是否有基本的目標 | `Makefile` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含特定目標 | `None` | 內容包含 "help:"、"setup:"、"test:" 和 "dev:" |
| **根目錄檔案** | **TC-STRUCT-016** | 測試 `requirements.txt` 是否包含 ADK | `requirements.txt` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 "google-adk" | `None` | 內容包含 "google-adk" |
