# 測試案例：Support Agent

## 簡介

此文件包含 `support-agent` 的詳細測試案例，旨在驗證其在各種情境下的功能，確保系統的穩定性與可靠性。

## 多輪對話測試 (`complex.evalset.json`)

此部分涵蓋多輪對話與後續建立工單的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **密碼重設後續追蹤** | **TC-MULTI-001** | 測試多輪對話與後續的工單建立 | None | 1. 使用者詢問：「如何重設密碼？」<br>2. 模型根據知識庫提供回覆。<br>3. 使用者表示：「那沒有用，可以提供更多協助嗎？」<br>4. 模型回應將建立支援工單。 | 使用者輸入 1：「How do I reset my password?」<br>使用者輸入 2：「That didn't work, can you help me more?」 | 1. 模型首先嘗試使用知識庫 (`search_knowledge_base`) 解決問題。<br>2. 當初始方案失敗時，模型會建立支援工單 (`create_ticket`) 進行升級處理。<br>3. 最終回應確認將會建立工單。 |

## 簡單知識庫搜尋測試 (`simple.test.json`)

此部分涵蓋簡單知識庫搜尋功能的測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **密碼重設** | **TC-SIMPLE-001** | 測試簡單的知識庫搜尋功能 | None | 1. 使用者詢問：「如何重設密碼？」<br>2. 模型根據知識庫提供回覆。 | 使用者輸入：「How do I reset my password?」 | 1. 模型應能理解使用者意圖並觸發 `search_knowledge_base` 工具。<br>2. 根據知識庫內容，提供直接且準確的密碼重設指南。<br>3. 最終回應包含重設密碼的具體步驟。 |

## Pytest 測試 (`test_agent.py`)

此部分涵蓋對 `support-agent` 的 Pytest 測試，包括工具函式、Agent 設定、整合與評估。

### 工具函式測試 (TestToolFunctions)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **知識庫搜尋** | **TC-AGENT-001** | 測試知識庫搜尋密碼重設 | Mock `ToolContext` | 呼叫 `search_knowledge_base` | `query`: "password reset" | 成功找到密碼重設資訊。 |
| **知識庫搜尋** | **TC-AGENT-002** | 測試知識庫搜尋退款政策 | Mock `ToolContext` | 呼叫 `search_knowledge_base` | `query`: "refund" | 成功找到退款政策資訊。 |
| **知識庫搜尋** | **TC-AGENT-003** | 測試知識庫搜尋運送資訊 | Mock `ToolContext` | 呼叫 `search_knowledge_base` | `query`: "shipping" | 成功找到運送資訊。 |
| **知識庫搜尋** | **TC-AGENT-004** | 測試知識庫搜尋不存在的主題 | Mock `ToolContext` | 呼叫 `search_knowledge_base` | `query`: "nonexistent topic" | 回報找不到相關文章。 |
| **工單建立** | **TC-AGENT-005** | 測試建立一般優先級工單 | Mock `ToolContext` | 呼叫 `create_ticket` | `issue`: "My account is locked", `priority`: "normal" | 成功建立一般優先級工單。 |
| **工單建立** | **TC-AGENT-006** | 測試建立高優先級工單 | Mock `ToolContext` | 呼叫 `create_ticket` | `issue`: "Website is down", `priority`: "high" | 成功建立高優先級工單。 |
| **工單建立** | **TC-AGENT-007** | 測試使用無效優先級建立工單 | Mock `ToolContext` | 呼叫 `create_ticket` | `priority`: "invalid" | 回傳錯誤，提示優先級無效。 |
| **工單建立** | **TC-AGENT-008** | 測試工單 ID 的唯一性 | Mock `ToolContext` | 連續呼叫 `create_ticket` 兩次 | `issue`: "Issue 1", "Issue 2" | 兩個工單的 ID 不應相同。 |
| **工單狀態** | **TC-AGENT-009** | 測試檢查現有工單的狀態 | Mock `ToolContext` | 1. 建立工單。<br>2. 呼叫 `check_ticket_status`。 | `ticket_id`: (由步驟 1 產生) | 成功回傳工單狀態為 "open"。 |
| **工單狀態** | **TC-AGENT-010** | 測試檢查不存在的工單狀態 | Mock `ToolContext` | 呼叫 `check_ticket_status` | `ticket_id`: "TICK-NONEXISTENT" | 回傳錯誤，提示找不到工單。 |

### Agent 設定測試 (TestAgentConfiguration)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 設定** | **TC-AGENT-011** | 測試 Agent 是否已正確定義 | None | 檢查 `root_agent` 物件 | None | `root_agent` 不為 None 且有名稱屬性。 |
| **Agent 設定** | **TC-AGENT-012** | 測試 Agent 名稱是否正確 | None | 檢查 `root_agent.name` | None | 名稱為 "support_agent"。 |
| **Agent 設定** | **TC-AGENT-013** | 測試 Agent 是否包含必要工具 | None | 檢查 `root_agent.tools` | None | 包含 `search_knowledge_base`, `create_ticket`, `check_ticket_status`。 |
| **Agent 設定** | **TC-AGENT-014** | 測試 Agent 使用的模型是否正確 | None | 檢查 `root_agent.model` | None | 模型為 "gemini-2.0-flash-exp"。 |
| **Agent 設定** | **TC-AGENT-015** | 測試 Agent 是否有描述 | None | 檢查 `root_agent.description` | None | 描述不為 None 且包含 "support"。 |
| **Agent 設定** | **TC-AGENT-016** | 測試 Agent 是否有指令 | None | 檢查 `root_agent.instruction` | None | 指令不為 None 且長度大於 0。 |
| **Agent 設定** | **TC-AGENT-017** | 測試 Agent 的輸出金鑰是否正確 | None | 檢查 `root_agent.output_key` | None | 輸出金鑰為 "support_response"。 |

### 整合測試 (TestIntegration)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **整合測試** | **TC-AGENT-018** | 測試知識庫是否涵蓋預期主題 | Mock `ToolContext` | 迭代呼叫 `search_knowledge_base` | `topics`: ["password", "refund", "shipping", "account", "billing", "technical"] | 所有主題都能成功找到結果。 |
| **整合測試** | **TC-AGENT-019** | 測試完整的工單建立與狀態檢查流程 | Mock `ToolContext` | 1. 建立高優先級工單。<br>2. 檢查該工單的狀態。 | `issue`: "Website loading slowly" | 工單成功建立，且狀態檢查結果正確。 |

### Agent 評估測試 (TestAgentEvaluation)

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent 評估** | **TC-AGENT-020** | 測試簡單知識庫搜尋評估 | None | 執行 `AgentEvaluator.evaluate` | `eval_dataset`: `simple.test.json` | 評估成功執行。 |
| **Agent 評估** | **TC-AGENT-021** | 測試工單建立流程評估 | None | 執行 `AgentEvaluator.evaluate` | `eval_dataset`: `ticket_creation.test.json` | 評估成功執行。 |
| **Agent 評估** | **TC-AGENT-022** | 測試複雜的多輪對話 | None | 執行 `AgentEvaluator.evaluate` | `eval_dataset`: `complex.evalset.json` | 評估成功執行。 |

## 工單建立流程測試 (`ticket_creation.test.json`)

此部分涵蓋工單建立流程與知識庫搜尋的整合測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **緊急帳戶鎖定** | **TC-TICKET-001** | 測試緊急帳戶鎖定情境下的工單建立流程 | None | 1. 使用者回報帳戶被鎖定且情況緊急。<br>2. 模型首先搜尋知識庫。<br>3. 模型根據搜尋結果與使用者情況，建議建立緊急支援工單。 | 使用者輸入：「My account is completely locked and I can't access anything. This is urgent!」 | 1. 模型應能辨識使用者問題的緊急性。<br>2. 即使知識庫提供了相關文章，模型也應能判斷該方案不適用於當前情況（帳戶已鎖定）。<br>3. 主動提議建立緊急工單，以提供更直接的協助。 |
