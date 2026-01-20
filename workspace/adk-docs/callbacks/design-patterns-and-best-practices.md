# Callbacks 的設計模式與最佳實踐
🔔 `更新日期：2026-01-20`

Callbacks（回調）為代理（agent）生命週期提供了強大的掛鉤（hooks）。以下是一些常見的設計模式，展示了如何在 ADK 中有效地利用它們，隨後是實施的最佳實踐。

## 設計模式

這些模式展示了使用 Callbacks 增強或控制代理行為的典型方式：

### 1. 護欄與策略執行

**模式概述：**
在請求到達 LLM 或工具之前攔截請求以執行規則。

**實施：**
- 使用 `before_model_callback` 檢查 `LlmRequest` 提示詞
- 使用 `before_tool_callback` 檢查工具參數
- 如果檢測到違反策略（例如：禁止話題、髒話）：
  - 返回預定義的回應（`LlmResponse` 或 `dict`/`Map`）以阻止操作
  - （選用）更新 `context.state` 以記錄違規行為

**範例使用場景：**
`before_model_callback` 檢查 `llm_request.contents` 是否包含敏感關鍵字，如果發現，則返回標準的「無法處理此請求」之 `LlmResponse`，從而阻止 LLM 調用。

### 2. 動態狀態管理

**模式概述：**
在 Callbacks 中讀取和寫入會話狀態（session state），使代理行為具有上下文感知能力，並在步驟之間傳遞數據。

**實施：**
- 訪問 `callback_context.state` 或 `tool_context.state`
- 修改（`state['key'] = value`）會自動追蹤在隨後的 `Event.actions.state_delta` 中
- 更改由 `SessionService` 持久化

**範例使用場景：**
`after_tool_callback` 將工具結果中的 `transaction_id` 保存到 `tool_context.state['last_transaction_id']`。稍後的 `before_agent_callback` 可能會讀取 `state['user_tier']` 以自定義代理的問候語。

### 3. 日誌記錄與監控

**模式概述：**
在特定的生命週期點添加詳細日誌，以實現可觀測性和調試。

**實施：**
- 實施 Callbacks（例如：`before_agent_callback`、`after_tool_callback`、`after_model_callback`）
- 列印或發送包含以下內容的結構化日誌：
  - 代理名稱
  - 工具名稱
  - 調用 ID
  - 來自上下文或參數的相關數據

**範例使用場景：**
記錄如下消息：`INFO: [Invocation: e-123] Before Tool: search_api - Args: {'query': 'ADK'}`。

### 4. 快取

**模式概述：**
通過快取結果來避免多餘的 LLM 調用或工具執行。

**實施步驟：**
1. **操作前：** 在 `before_model_callback` 或 `before_tool_callback` 中：
   - 根據請求/參數生成快取鍵（cache key）
   - 檢查 `context.state`（或外部快取）是否存在此鍵
   - 如果找到，直接返回快取的 `LlmResponse` 或結果

2. **操作後：** 如果發生快取未命中（cache miss）：
   - 使用相應的 `after_` 回調，使用該鍵將新結果存儲在快取中

**範例使用場景：**
針對 `get_stock_price(symbol)` 的 `before_tool_callback` 檢查 `state[f"cache:stock:{symbol}"]`。如果存在，則返回快取的價格；否則，允許進行 API 調用，並由 `after_tool_callback` 將結果保存到狀態鍵中。

### 5. 請求/回應修改

**模式概述：**
在數據發送到 LLM/工具之前或收到數據之後立即更改數據。

**實施選項：**
- **`before_model_callback`：** 修改 `llm_request`（例如：根據 `state` 添加系統指令）
- **`after_model_callback`：** 修改返回的 `LlmResponse`（例如：格式化文本、過濾內容）
- **`before_tool_callback`：** 修改工具 `args` 字典（在 Java 中為 Map）
- **`after_tool_callback`：** 修改 `tool_response` 字典（在 Java 中為 Map）

**範例使用場景：**
如果 `context.state['lang'] == 'es'`，`before_model_callback` 會在 `llm_request.config.system_instruction` 中附加「用戶語言偏好：西班牙語」。

### 6. 有條件地跳過步驟

**模式概述：**
根據某些條件阻止標準操作（代理運行、LLM 調用、工具執行）。

**實施：**
- 從 `before_` 回調返回一個值以跳過正常執行：
  - 從 `before_agent_callback` 返回 `Content`
  - 從 `before_model_callback` 返回 `LlmResponse`
  - 從 `before_tool_callback` 返回 `dict`
- 框架將此返回值解釋為該步驟的結果

**範例使用場景：**
`before_tool_callback` 檢查 `tool_context.state['api_quota_exceeded']`。如果為 `True`，則返回 `{'error': 'API quota exceeded'}`，從而阻止實際的工具函數運行。

### 7. 工具特定操作（身分驗證與摘要控制）

**模式概述：**
處理特定於工具生命週期的操作，主要是身分驗證和控制 LLM 對工具結果的摘要。

**實施：**
在工具回調（`before_tool_callback`、`after_tool_callback`）中使用 `ToolContext`：

- **身分驗證：** 如果需要憑證但未找到（例如：通過 `tool_context.get_auth_response` 或狀態檢查），在 `before_tool_callback` 中調用 `tool_context.request_credential(auth_config)`。這將啟動身分驗證流程。
- **摘要：** 如果工具的原始字典輸出應傳回給 LLM 或可能直接顯示，從而繞過預設的 LLM 摘要步驟，請設置 `tool_context.actions.skip_summarization = True`。

**範例使用場景：**
安全 API 的 `before_tool_callback` 檢查狀態中的身分驗證權杖；如果缺失，則調用 `request_credential`。返回結構化 JSON 的工具之 `after_tool_callback` 可能會設置 `skip_summarization = True`。

### 8. Artifact 處理

**模式概述：**
在代理生命週期中保存或加載與會話相關的文件或大型數據塊（blobs）。

**實施：**
- **保存：** 使用 `callback_context.save_artifact` / `await tool_context.save_artifact` 來存儲數據：
  - 生成的報告
  - 日誌
  - 中間數據
- **加載：** 使用 `load_artifact` 檢索以前存儲的成品（artifacts）
- **追蹤：** 更改通過 `Event.actions.artifact_delta` 進行追蹤

**範例使用場景：**
「generate_report」工具的 `after_tool_callback` 使用 `await tool_context.save_artifact("report.pdf", report_part)` 保存輸出文件。`before_agent_callback` 可能會使用 `callback_context.load_artifact("agent_config.json")` 加載配置成品。

## 設計模式整合

以下表格整合了 8 種 Callbacks 設計模式的核心概念與應用場景：

| # | 設計模式 | 模式概述 | 主要 Callback 類型 | 典型使用場景 |
|---|---------|---------|------------------|-------------|
| 1 | **護欄與策略執行** | 在請求到達 LLM 或工具之前攔截並執行規則 | `before_model_callback`<br/>`before_tool_callback` | 內容過濾、敏感詞檢測、策略違規攔截 |
| 2 | **動態狀態管理** | 讀寫會話狀態，使代理具有上下文感知能力 | `before_agent_callback`<br/>`after_tool_callback` | 跨步驟數據傳遞、用戶偏好追蹤、交易 ID 記錄 |
| 3 | **日誌記錄與監控** | 在生命週期點添加詳細日誌以實現可觀測性 | `before_agent_callback`<br/>`after_tool_callback`<br/>`after_model_callback` | 調試追蹤、性能監控、審計日誌 |
| 4 | **快取** | 通過快取結果避免多餘的 LLM 或工具調用 | `before_model_callback`<br/>`after_model_callback`<br/>`before_tool_callback`<br/>`after_tool_callback` | API 結果快取、頻繁查詢優化、降低成本 |
| 5 | **請求/回應修改** | 在數據發送或接收時動態修改內容 | `before_model_callback`<br/>`after_model_callback`<br/>`before_tool_callback`<br/>`after_tool_callback` | 多語言適配、內容格式化、參數注入 |
| 6 | **有條件地跳過步驟** | 根據條件阻止標準操作的執行 | `before_agent_callback`<br/>`before_model_callback`<br/>`before_tool_callback` | 配額控制、條件式短路、預設回應 |
| 7 | **工具特定操作** | 處理身分驗證與 LLM 摘要控制 | `before_tool_callback`<br/>`after_tool_callback` | OAuth 流程、憑證管理、摘要控制 |
| 8 | **Artifact 處理** | 保存或加載會話相關文件與大型數據 | `before_agent_callback`<br/>`after_tool_callback` | 報告生成、配置加載、中間數據存儲 |

### 模式選擇指南

**何時使用 `before_` Callbacks：**
- 需要驗證或修改輸入數據
- 實施訪問控制或護欄
- 檢查快取以避免操作
- 條件式跳過執行

**何時使用 `after_` Callbacks：**
- 需要處理或轉換輸出結果
- 保存執行結果到快取或狀態
- 記錄執行完成事件
- 保存生成的 artifacts

**組合使用策略：**
多個模式可以組合使用以實現複雜需求。例如：
- **快取 + 日誌記錄：** 在快取檢查時記錄命中率
- **狀態管理 + 護欄：** 根據用戶狀態動態調整策略
- **Artifact 處理 + 摘要控制：** 保存原始數據同時控制 LLM 摘要

---
## Callbacks 的最佳實踐

### 設計原則

**保持明確：**
為單一且定義明確的目的（例如：僅日誌記錄、僅驗證）設計每個回調。避免使用龐大臃腫的回調。

**注意性能：**
Callbacks 在代理的處理循環中同步執行。避免長時間運行或阻塞的操作（網絡調用、大量計算）。如有必要，請卸載任務，但要注意這會增加複雜性。

### 錯誤處理

**優雅地處理錯誤：**
- 在回調函數中使用 `try...except/catch` 塊
- 適當地記錄錯誤
- 決定代理髮起是否應該停止或嘗試恢復
- 不要讓回調錯誤導致整個進程崩潰

### 狀態管理

**謹慎管理狀態：**
- 審慎地從 `context.state` 讀取和寫入
- 更改在「當前」調用中立即可見，並在事件處理結束時持久化
- 使用特定的狀態鍵，而不是修改廣泛的結構，以避免意外的副作用
- 考慮使用狀態前綴（如 `State.APP_PREFIX`、`State.USER_PREFIX`、`State.TEMP_PREFIX`）以提高清晰度，特別是使用持久化 `SessionService` 實施時

### 可靠性

**考慮冪等性：**
如果回調執行具有外部副作用的操作（例如：增加外部計數器），請盡可能將其設計為冪等（使用相同輸入多次運行是安全的），以處理框架或應用程式中潛在的重試。

### 測試與文件

**徹底測試：**
- 使用模擬上下文對象單元測試您的回調函數
- 執行集成測試以確保回調在完整的代理流程中正常運作

**確保清晰：**
- 為您的回調函數使用描述性名稱
- 添加清晰的 docstrings，說明其目的、運行時機以及任何副作用（特別是狀態修改）

**使用正確的上下文類型：**
始終使用提供的特定上下文類型（代理/模型的 `CallbackContext`，工具的 `ToolContext`），以確保可以訪問適當的方法和屬性。

## 最佳實務整合

以下表格整合了 Callbacks 開發的核心最佳實踐與實施要點：

| 實踐類別 | 核心原則 | 關鍵要點 | 實施建議 |
|---------|---------|---------|---------|
| **設計原則** | 保持明確、注意性能 | • 單一職責原則<br/>• 同步執行特性<br/>• 避免阻塞操作 | • 每個回調專注於單一明確目的<br/>• 避免長時間運行的網絡調用或大量計算<br/>• 必要時卸載任務，但注意複雜性增加 |
| **錯誤處理** | 優雅地處理錯誤 | • 防禦性編程<br/>• 錯誤記錄<br/>• 恢復策略<br/>• 系統穩定性 | • 使用 `try...except/catch` 塊包裹回調邏輯<br/>• 適當記錄錯誤詳情以便調試<br/>• 決定是停止代理還是嘗試恢復<br/>• 確保回調錯誤不會導致整個進程崩潰 |
| **狀態管理** | 謹慎管理狀態 | • 審慎讀寫<br/>• 立即可見性<br/>• 持久化機制<br/>• 命名規範 | • 審慎地從 `context.state` 讀取和寫入<br/>• 更改在當前調用中立即可見，事件結束時持久化<br/>• 使用特定的狀態鍵，避免意外副作用<br/>• 使用狀態前綴（`APP_PREFIX`、`USER_PREFIX`、`TEMP_PREFIX`）提高清晰度 |
| **可靠性** | 考慮冪等性 | • 副作用控制<br/>• 重試安全性<br/>• 操作可重複性 | • 設計為冪等操作（使用相同輸入多次運行是安全的）<br/>• 處理框架或應用程式中潛在的重試情況<br/>• 特別注意具有外部副作用的操作（如計數器增加） |
| **測試與文件** | 徹底測試、確保清晰、使用正確類型 | • 單元測試<br/>• 集成測試<br/>• 描述性命名<br/>• 文件記錄<br/>• 類型正確性 | • 使用模擬上下文對象進行單元測試<br/>• 執行集成測試確保完整流程正常<br/>• 使用描述性的回調函數名稱<br/>• 添加清晰的 docstrings 說明目的、時機和副作用<br/>• 使用正確的上下文類型（`CallbackContext` 或 `ToolContext`） |

### 實踐優先級建議

**高優先級（必須遵循）：**
1. **錯誤處理：** 使用 try-catch 塊，防止回調崩潰
2. **類型正確性：** 使用正確的上下文類型
3. **單一職責：** 每個回調專注於單一目的

**中優先級（強烈建議）：**
1. **性能考量：** 避免阻塞操作
2. **狀態管理：** 使用命名規範和特定鍵
3. **文件記錄：** 添加清晰的 docstrings

**持續改進（最佳化）：**
1. **冪等性設計：** 處理重試場景
2. **測試覆蓋：** 單元測試和集成測試
3. **日誌記錄：** 適當記錄錯誤和關鍵事件

通過應用這些模式和最佳實踐，您可以有效地使用 Callbacks 在 ADK 中創建更健壯、可觀測且自定義的代理行為。
