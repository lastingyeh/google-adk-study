# Grounding Agent 測試案例

## 簡介

此文件提供了 Grounding Agent 的詳細測試案例，旨在為專案建立清晰、一致且全面的測試文件。

## `test_agents.py`

此部分涵蓋對 Grounding Agent 的主要功能測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **工具函式** | **TC-GA-001** | 測試成功的搜尋結果分析 | `tool_context` 已模擬 | 1. 呼叫 `analyze_search_results` 函式 | `query`: "quantum computing", `content`: "Quantum computing uses quantum mechanics..." | 函式回傳 `status` 為 `success`，且報告包含 "quantum computing" |
| **工具函式** | **TC-GA-002** | 測試使用空內容進行分析 | `tool_context` 已模擬 | 1. 呼叫 `analyze_search_results` 函式 | `query`: "test query", `content`: "" | 函式回傳 `status` 為 `success`，且 `word_count` 為 0 |
| **工具函式** | **TC-GA-003** | 測試分析中的錯誤處理 | `tool_context` 已模擬 | 1. 呼叫 `analyze_search_results` 函式 | `query`: "test", `content`: "valid content" | 函式回傳 `status` 為 `success` |
| **工具函式** | **TC-GA-004** | 測試成功儲存研究發現 | `tool_context` 已模擬 | 1. 呼叫 `save_research_findings` 函式 | `topic`: "AI Developments", `findings`: "Recent breakthroughs..." | 函式回傳 `status` 為 `success`，且報告包含 "saved as" |
| **工具函式** | **TC-GA-005** | 測試主題中包含特殊字元的儲存 | `tool_context` 已模擬 | 1. 呼叫 `save_research_findings` 函式 | `topic`: "Quantum Computing & AI", `findings`: "Test findings" | 函式回傳 `status` 為 `success`，且檔名包含 "research_quantum_computing_&_ai.md" |
| **Agent 組態** | **TC-GA-006** | 測試 root_agent 是否為 basic_grounding_agent | None | 1. 斷言 `root_agent` is `basic_grounding_agent` | None | 斷言成功 |
| **Agent 組態** | **TC-GA-007** | 測試 basic_grounding_agent 的組態 | None | 1. 檢查 `name`, `model`, `tools`, `output_key` | None | 所有屬性符合預期 |
| **Agent 組態** | **TC-GA-008** | 測試 advanced_grounding_agent 的組態 | None | 1. 檢查 `name`, `model`, `tools`, `output_key` | None | 所有屬性符合預期 |
| **Agent 組態** | **TC-GA-009** | 測試 research_assistant 的組態 | None | 1. 檢查 `name`, `model`, `tools`, `output_key`, `generate_content_config` | None | 所有屬性符合預期 |
| **Agent 組態** | **TC-GA-010** | 測試所有 Agent 是否都有描述 | None | 1. 迭代檢查每個 Agent 的 `description` | None | 每個 Agent 的 `description` 都不為 None 且長度大於 0 |
| **Agent 組態** | **TC-GA-011** | 測試所有 Agent 是否都有指令 | None | 1. 迭代檢查每個 Agent 的 `instruction` | None | 每個 Agent 的 `instruction` 都不為 None 且包含 "search" |
| **Grounding 功能** | **TC-GA-012** | 測試 basic_agent 是否有 google_search 工具 | None | 1. 檢查 `basic_grounding_agent.tools` | None | `tools` 中包含 "google_search" |
| **Grounding 功能** | **TC-GA-013** | 測試 advanced_agent 是否有 google_search 工具 | None | 1. 檢查 `advanced_grounding_agent.tools` | None | `tools` 中包含 "google_search" |
| **Grounding 功能** | **TC-GA-014** | 測試 research_agent 是否有完整的指令 | None | 1. 檢查 `research_assistant.instruction` | None | `instruction` 包含 "analyze_search_results", "save_research_findings", "research process", "web research" |
| **整合測試** | **TC-GA-015** | 測試模擬的研究工作流程 | `tool_context` 已模擬 | 1. 呼叫 `analyze_search_results`<br>2. 呼叫 `save_research_findings` | `query`: "AI trends 2025", `content`: "Artificial Intelligence..." | 兩個函式都回傳 `status` 為 `success` |
| **整合測試** | **TC-GA-016** | 測試工具是否能優雅地處理錯誤 | `tool_context` 已模擬 | 1. 使用空字串呼叫 `analyze_search_results`<br>2. 使用空字串呼叫 `save_research_findings` | `query`: "", `content`: "" | 兩個函式都回傳 `status` 為 `success` |
| **Agent 匯入** | **TC-GA-017** | 測試所有 Agent 匯入是否正常運作 | None | 1. 從 `grounding_agent.agent` 匯入所有 agents | None | 所有 agents 都不為 None |
| **Agent 匯入** | **TC-GA-018** | 測試工具匯入是否正常運作 | None | 1. 從 `grounding_agent.agent` 匯入 `analyze_search_results`, `save_research_findings` | None | 兩個函式都是 `callable` |
| **VertexAI 條件邏輯** | **TC-GA-019** | 測試 VertexAI 預設為停用 | 未設定 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數 | 1. 呼叫 `is_vertexai_enabled` | None | 回傳 `False` |
| **VertexAI 條件邏輯** | **TC-GA-020** | 測試設定環境變數時 VertexAI 是否啟用 | 設定 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數為 "1" | 1. 呼叫 `is_vertexai_enabled` | None | 回傳 `True` |
| **VertexAI 條件邏輯** | **TC-GA-021** | 測試未啟用 VertexAI 時的工具載入 | 未設定 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數 | 1. 呼叫 `get_available_grounding_tools` | None | 回傳的工具列表長度為 1，且包含 "google_search" |
| **VertexAI 條件邏輯** | **TC-GA-022** | 測試啟用 VertexAI 時的工具載入 | 設定 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數為 "1" | 1. 呼叫 `get_available_grounding_tools` | None | 回傳的工具列表長度為 2，且包含 "google_search" 和 "google_maps" |
| **VertexAI 條件邏輯** | **TC-GA-023** | 測試未啟用 VertexAI 時的功能描述 | 未設定 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數 | 1. 呼叫 `get_agent_capabilities_description` | None | 描述包含 "web search for current information"，不包含 "maps" |
| **VertexAI 條件邏輯** | **TC-GA-024** | 測試啟用 VertexAI 時的功能描述 | 設定 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數為 "1" | 1. 呼叫 `get_agent_capabilities_description` | None | 描述包含 "web search for current information" 和 "location-based queries and maps grounding" |
| **VertexAI 條件邏輯** | **TC-GA-025** | 測試啟用 VertexAI 時 Agent 是否包含地圖工具 | 設定 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數為 "1" | 1. 呼叫 `get_available_grounding_tools` | None | 回傳的工具列表長度為 2 |
| **VertexAI 條件邏輯** | **TC-GA-026** | 測試 root_agent 選擇邏輯是否正常運作 | 未設定 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數 | 1. 呼叫 `is_vertexai_enabled` | None | 回傳 `False` |
| **VertexAI 條件邏輯** | **TC-GA-027** | 測試 Agent 指令是否根據 VertexAI 的可用性進行調整 | 未設定 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數 | 1. 檢查 `basic_grounding_agent.instruction` | None | 指令中不應提及地圖 |
