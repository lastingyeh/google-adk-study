# 詳細測試案例範本

## 簡介

此文件提供了一個詳細的測試案例範本，旨在為專案建立清晰、一致且全面的測試文件。使用此範本可以幫助開發者和測試人員標準化測試流程，確保所有關鍵功能都得到充分的驗證。

## `content_moderator` 代理程式測試 (`tests/test_agent.py`)

此部分涵蓋對 `content_moderator` 代理程式的回調和工具函式進行的單元測試。

| 群組 | 測試案例編號 | 描述 | 前置條件 | 測試步驟 | 測試數據 | 預期結果 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **代理前回調** | **TC-AGENT-001** | 測試代理程式是否在維護模式下攔截請求。 | `app:maintenance_mode` 狀態設定為 `True`。 | 1. 建立 `MockCallbackContext`。<br>2. 設定 `ctx.state["app:maintenance_mode"] = True`。<br>3. 呼叫 `before_agent_callback(ctx)`。 | `app:maintenance_mode`: `True` | 函式返回一個包含 "maintenance" 訊息的回應。 |
| **代理前回調** | **TC-AGENT-002** | 測試代理程式是否增加請求計數。 | `user:request_count` 狀態已存在。 | 1. 建立 `MockCallbackContext`。<br>2. 設定 `ctx.state["user:request_count"] = 2`。<br>3. 呼叫 `before_agent_callback(ctx)`。 | `user:request_count`: `2` | `user:request_count` 狀態增加到 `3`。 |
| **模型回調** | **TC-MODEL-001** | 測試模型前回調是否攔截不當內容。 | 無 | 1. 建立 `MockCallbackContext`。<br>2. 建立包含不當內容的請求。<br>3. 呼叫 `before_model_callback(ctx, req)`。 | 請求文字: "This contains profanity1" | 函式返回一個包含 "inappropriate content" 訊息的回應，且 `user:blocked_requests` 增加 `1`。 |
| **模型回調** | **TC-MODEL-002** | 測試模型前回調是否添加安全指示。 | 無 | 1. 建立 `MockCallbackContext`。<br>2. 建立一個安全的請求。<br>3. 呼叫 `before_model_callback(ctx, req)`。 | 請求文字: "Safe text" | 系統指示中加入 "IMPORTANT"，且 `user:llm_calls` 增加 `1`。 |
| **模型回調** | **TC-MODEL-003** | 測試模型後回調是否過濾個人身份資訊。 | 無 | 1. 建立 `MockCallbackContext`。<br>2. 建立包含電子郵件的回應。<br>3. 呼叫 `after_model_callback(ctx, resp)`。 | 回應文字: "Contact me at john.doe@example.com" | 回應中的電子郵件被替換為 "[EMAIL_REDACTED]"。 |
| **工具回調** | **TC-TOOL-001** | 測試工具前回調是否驗證字數。 | 無 | 1. 建立 `MockCallbackContext`。<br>2. 建立包含無效字數的參數。<br>3. 呼叫 `before_tool_callback`。 | `word_count`: `-5` | 函式返回一個錯誤狀態，訊息中包含 "invalid word_count"。 |
| **工具回調** | **TC-TOOL-002** | 測試工具前回調是否進行速率限制。 | `user:tool_generate_text_count` 達到限制。 | 1. 建立 `MockCallbackContext`。<br>2. 設定 `ctx.state["user:tool_generate_text_count"] = 100`。<br>3. 呼叫 `before_tool_callback`。 | `user:tool_generate_text_count`: `100` | 函式返回一個錯誤狀態，訊息中包含 "rate limit"。 |
| **工具回調** | **TC-TOOL-003** | 測試工具後回調是否記錄結果。 | 無 | 1. 建立 `MockCallbackContext`。<br>2. 建立一個成功的工具回應。<br>3. 呼叫 `after_tool_callback`。 | `tool_response`: `{"status": "success"}` | `temp:last_tool_result` 狀態中包含 "success"。 |
| **工具函式** | **TC-TOOL-004** | 測試生成文本工具。 | 無 | 1. 建立 `Mock` 上下文。<br>2. 呼叫 `generate_text`。 | `topic`: "Python", `word_count`: `100` | 函式返回成功狀態，且訊息中包含 "Python"。 |
| **工具函式** | **TC-TOOL-005** | 測試語法檢查工具。 | 無 | 1. 建立 `Mock` 上下文。<br>2. 呼叫 `check_grammar`。 | `text`: "This is a test sentence with some errors." | 函式返回成功狀態，且結果中包含 "issues_found"。 |
| **工具函式** | **TC-TOOL-006** | 測試獲取使用統計工具。 | 狀態中包含使用統計數據。 | 1. 建立 `Mock` 上下文。<br>2. 設定多個使用統計狀態。<br>3. 呼叫 `get_usage_stats`。 | `user:request_count`: `5`, `user:llm_calls`: `3`, etc. | 函式返回成功狀態，並包含所有統計數據。 |
