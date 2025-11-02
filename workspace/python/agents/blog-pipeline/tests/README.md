# 部落格建立流程測試案例

## 簡介

此文件提供了針對「部落格建立流程」專案的詳細測試案例，旨在確保 Agent 配置、工作流程、模組匯入與專案結構的正確性與穩定性。

## Agent 功能測試 (`test_agent.py`)

此部分涵蓋對核心 Agent 的配置、流程結構、狀態管理及整合能力的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 配置** | **TC-AGENT-001** | 測試 `root_agent` 可以被匯入 | 專案環境已設定 | 1. 匯入 `root_agent` | `None` | `root_agent` 成功匯入，物件不為 `None`。 |
| **Agent 配置** | **TC-AGENT-002** | 測試 `root_agent` 是否為 `SequentialAgent` 實例 | `root_agent` 已匯入 | 1. 檢查 `root_agent` 的類型 | `None` | `root_agent` 必須是 `SequentialAgent` 的一個實例。 |
| **Agent 配置** | **TC-AGENT-003** | 測試流程是否有正確的名稱 | `root_agent` 已匯入 | 1. 讀取 `root_agent.name` 屬性 | `None` | 名稱應為 "BlogCreationPipeline"。 |
| **Agent 配置** | **TC-AGENT-004** | 測試流程是否有 4 個子 agent | `root_agent` 已匯入 | 1. 檢查 `root_agent.sub_agents` 的長度 | `None` | `sub_agents` 列表的長度應為 4。 |
| **個別 Agent** | **TC-AGENT-005** | 測試研究 agent (`researcher`) 的配置 | `research_agent` 已匯入 | 1. 檢查 `name`, `model`, `output_key` 和 `instruction` | `None` | 配置符合預期，`output_key` 為 "research_findings"。 |
| **個別 Agent** | **TC-AGENT-006** | 測試寫作 agent (`writer`) 的配置 | `writer_agent` 已匯入 | 1. 檢查 `name`, `model`, `output_key` 和 `instruction` | `None` | 配置符合預期，指令中包含 `{research_findings}`。 |
| **個別 Agent** | **TC-AGENT-007** | 測試編輯 agent (`editor`) 的配置 | `editor_agent` 已匯入 | 1. 檢查 `name`, `model`, `output_key` 和 `instruction` | `None` | 配置符合預期，指令中包含 `{draft_post}`。 |
| **個別 Agent** | **TC-AGENT-008** | 測試格式化 agent (`formatter`) 的配置 | `formatter_agent` 已匯入 | 1. 檢查 `name`, `model`, `output_key` 和 `instruction` | `None` | 配置符合預期，指令中包含 `{draft_post}` 和 `{editorial_feedback}`。 |
| **流程結構** | **TC-AGENT-009** | 測試 agent 是否按正確順序執行 | `root_agent` 已匯入 | 1. 讀取 `root_agent.sub_agents` 的順序 | `None` | 順序應為 `researcher` -> `writer` -> `editor` -> `formatter`。 |
| **狀態管理** | **TC-AGENT-010** | 測試研究結果是否能流向寫作 agent | `writer_agent` 已匯入 | 1. 檢查 `writer_agent.instruction` | `None` | 指令中必須包含 `{research_findings}` 以接收狀態。 |
| **狀態管理** | **TC-AGENT-011** | 測試草稿和意見是否能流向格式化 agent | `formatter_agent` 已匯入 | 1. 檢查 `formatter_agent.instruction` | `None` | 指令中必須包含 `{draft_post}` 和 `{editorial_feedback}`。 |
| **整合測試** | **TC-AGENT-012** | 測試流程可以無錯誤地建立 | `root_agent` 已匯入 | 1. 存取 `root_agent` 及其屬性 | `None` | 流程建立不應引發任何錯誤。 |

## 模組匯入測試 (`test_imports.py`)

此部分涵蓋對專案所需模組和套件的匯入功能測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ADK 匯入** | **TC-IMPORTS-001** | 測試 `google.adk.agents` 匯入是否正常 | 專案環境已設定 | 1. 從 `google.adk.agents` 匯入 `Agent` 和 `SequentialAgent` | `None` | `Agent` 和 `SequentialAgent` 類別成功匯入，不為 `None`。 |
| **本地模組匯入** | **TC-IMPORTS-002** | 測試 `blog_pipeline.agent` 匯入是否正常 | 專案環境已設定 | 1. 從 `blog_pipeline.agent` 匯入 `root_agent` | `None` | `root_agent` 物件成功匯入，不為 `None`。 |
| **本地模組匯入** | **TC-IMPORTS-003** | 測試 `root_agent` 是否正確定義 | `root_agent` 已匯入 | 1. 檢查 `root_agent` 是否存在<br>2. 檢查 `name` 和 `sub_agents` 屬性 | `None` | `root_agent` 物件存在且包含必要的屬性。 |
| **Python 功能** | **TC-IMPORTS-004** | 測試 `__future__ annotations` 匯入是否正常 | 專案環境已設定 | 1. 匯入 `__future__` 模組<br>2. 檢查 `annotations` 屬性 | `None` | `__future__` 模組支援 `annotations` 功能。 |

## 專案結構測試 (`test_structure.py`)

此部分涵蓋對專案目錄結構、必要檔案及其內容的驗證。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **目錄結構** | **TC-STRUCT-001** | 測試 `blog_pipeline` 目錄是否存在 | 專案已下載 | 1. 檢查 `blog_pipeline` 目錄是否存在 | `None` | 目錄必須存在於專案根目錄。 |
| **核心檔案** | **TC-STRUCT-002** | 測試 `__init__.py` 和 `agent.py` 是否存在 | `blog_pipeline` 目錄存在 | 1. 檢查 `blog_pipeline/__init__.py`<br>2. 檢查 `blog_pipeline/agent.py` | `None` | 兩個核心 Python 檔案都必須存在。 |
| **環境配置** | **TC-STRUCT-003** | 測試 `.env.example` 是否存在 | `blog_pipeline` 目錄存在 | 1. 檢查 `blog_pipeline/.env.example` | `None` | 環境變數範例檔案必須存在。 |
| **檔案內容** | **TC-STRUCT-004** | 測試 `__init__.py` 是否有正確的內容 | `__init__.py` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 `from .agent import root_agent` 和 `__all__` | `None` | 檔案內容符合模組匯出標準。 |
| **檔案內容** | **TC-STRUCT-005** | 測試 `.env.example` 是否包含必要變數 | `.env.example` 檔案存在 | 1. 讀取檔案內容<br>2. 檢查是否包含 `GOOGLE_GENAI_USE_VERTEXAI` 和 `GOOGLE_API_KEY` | `None` | 檔案包含必要的 Google AI 相關設定。 |
| **測試結構** | **TC-STRUCT-006** | 測試 `tests` 目錄與 `__init__.py` 是否存在 | 專案已下載 | 1. 檢查 `tests` 目錄<br>2. 檢查 `tests/__init__.py` | `None` | `tests` 目錄應作為一個 Python 套件存在。 |
