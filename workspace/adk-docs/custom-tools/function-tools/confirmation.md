# 取得 ADK 工具的操作確認

🔔 `更新日期：2026-01-13`

[`ADK 支援`: `Python v1.14.0` | `Experimental`]

某些代理工作流程需要確認才能進行決策、驗證、安全性或一般監督。在這些情況下，您會希望在繼續工作流程之前，從人類或監督系統取得回應。代理開發套件 (ADK) 中的 *工具確認 (Tool Confirmation)* 功能允許 ADK 工具暫停執行，並與使用者或其他系統進行互動以取得確認，或在繼續之前收集結構化數據。您可以透過以下方式將工具確認與 ADK 工具搭配使用：

-   **[布林確認 (Boolean Confirmation)](#布林確認-boolean-confirmation)：** 您可以為 `FunctionTool` 配置 `require_confirmation` 參數。此選項會暫停工具，等待「是」或「否」的確認回應。
-   **[進階確認 (Advanced Confirmation)](#進階確認-advanced-confirmation)：** 對於需要結構化數據回應的情境，您可以為 `FunctionTool` 配置文字提示來解釋確認內容以及預期的回應。

> [!NOTE] Experiemental
    工具確認功能目前處於實驗階段，且有一些[已知限制 (#known-limitations)](#known-limitations)。
    我們歡迎您的[回饋](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=tool%20confirmation)！

您可以配置向使用者傳達請求的方式，系統也可以使用透過 ADK 伺服器的 REST API 發送的[遠端回應 (#remote-response)](#remote-response)。當在 ADK 網頁使用者介面使用確認功能時，代理工作流程會向使用者顯示一個對話框以請求輸入，如圖 1 所示：

![工具確認預設使用者介面截圖](https://google.github.io/adk-docs/assets/confirmation-ui.png)

**圖 1.** 使用進階工具回應實作的確認回應請求對話框範例。

以下章節介紹如何針對不同的確認情境使用此功能。如需完整的程式碼範例，請參閱 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 範例。還有其他方法可以將人類輸入整合到您的代理工作流程中，詳情請參閱 [人機協作 (Human-in-the-loop)](../../agents/multi-agents.md#人機協同模式-human-in-the-loop-pattern) 代理模式。

## 布林確認 (Boolean Confirmation)

當您的工具只需要使用者簡單的「是」或「否」時，您可以使用 `FunctionTool` 類別作為包裝器來附加確認步驟。例如，如果您有一個名為 `reimburse` (報支) 的工具，您可以透過使用 `FunctionTool` 類別包裝它並將 `require_confirmation` 參數設置為 `True` 來啟用確認步驟，如下例所示：

```python
# 來自 agent.py
root_agent = Agent(
   ...
   tools=[
        # 將 require_confirmation 設置為 True，以要求對該工具調用進行使用者確認。
        FunctionTool(reimburse, require_confirmation=True),
    ],
...
```

這種實作方法需要的程式碼最少，但僅限於來自使用者或確認系統的簡單批准。如需此方法的完整範例，請參閱 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 程式碼範例。

### 需要確認函數 (Require confirmation function)

您可以透過將 `require_confirmation` 的輸入值替換為傳回布林回應的函數，來修改其行為。以下範例顯示了一個用於確定是否需要確認的函數：

```python
async def confirmation_threshold(
    amount: int, tool_context: ToolContext
) -> bool:
  """如果金額大於 1000，則傳回 true。"""
  # 判斷金額是否超過門檻值 1000
  return amount > 1000
```

然後可以將此函數設置為 `require_confirmation` 參數的參數值：

```python
root_agent = Agent(
   ...
   tools=[
        # 設置 require_confirmation 為自定義的確認函數
        FunctionTool(reimburse, require_confirmation=confirmation_threshold),
    ],
...
```

如需此實作的完整範例，請參閱 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 程式碼範例。

## 進階確認 (Advanced confirmation)

當工具確認需要使用者的更多細節或更複雜的回應時，請使用 `tool_confirmation` 實作。此方法擴展了 `ToolContext` 物件，為使用者增加請求的文字描述，並允許更複雜的回應數據。以此方式實作工具確認時，您可以暫停工具的執行，請求特定資訊，然後使用提供的數據恢復工具執行。

此確認流程包含一個請求階段（系統組裝並發送輸入請求給人類回應）和一個回應階段（系統接收並處理傳回的數據）。

### 確認定義

當建立具有進階確認的工具時，請建立一個包含 `ToolContext` 物件的函數。然後使用 `tool_confirmation` 物件定義確認，即使用帶有 `hint` 和 `payload` 參數的 `tool_context.request_confirmation()` 方法。這些屬性的用法如下：

-   `hint`：解釋使用者需要提供什麼內容的描述性訊息。
-   `payload`：您預期傳回的數據結構。此數據類型為 `Any`，且必須可序列化為 JSON 格式的字串，例如字典 (dictionary) 或 pydantic 模型。

以下程式碼顯示了處理員工請假請求工具的範例實作：

```python
def request_time_off(days: int, tool_context: ToolContext):
    """為員工申請休假。"""
    ...
    # 取得目前的工具確認物件
    tool_confirmation = tool_context.tool_confirmation

    # 如果尚未取得確認，則發起確認請求
    if not tool_confirmation:
        tool_context.request_confirmation(
            hint=(
                '請透過回傳帶有預期 ToolConfirmation payload 的 FunctionResponse，'
                '來批准或拒絕 request_time_off() 的工具調用請求。'
            ),
            payload={
                'approved_days': 0,
            },
        )
        # 傳回中間狀態，指示工具正在等待確認回應：
        return {'status': '需要經理批准。'}

    # 從確認回應的 payload 中取得核准的天數
    approved_days = tool_confirmation.payload['approved_days']
    # 確保核准天數不超過申請天數
    approved_days = min(approved_days, days)

    # 如果核准天數為 0，表示請求被拒絕
    if approved_days == 0:
        return {'status': '休假申請已被拒絕。', 'approved_days': 0}

    # 回傳成功的狀態及核准天數
    return {
        'status': 'ok',
        'approved_days': approved_days,
    }
```

如需此方法的完整範例，請參閱 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 程式碼範例。請記住，在取得確認期間，代理工作流程的工具執行會暫停。收到確認後，您可以訪問 `tool_confirmation.payload` 物件中的確認回應，然後繼續執行工作流程。

## 使用 REST API 進行遠端確認 (Remote confirmation with REST API)

如果代理工作流程的人類確認沒有活動的使用者介面，您可以透過命令行介面處理確認，或將其路由到其他管道，如電子郵件或聊天應用程式。要確認工具調用，使用者或調用程式需要發送一個帶有工具確認數據的 `FunctionResponse` 事件。

您可以將請求發送到 ADK API 伺服器的 `/run` 或 `/run_sse` 端點，或者直接發送到 ADK 執行器 (runner)。以下範例使用 `curl` 指令將確認發送到 `/run_sse` 端點：

```
# 使用 curl 發送 POST 請求至 /run_sse 端點進行工具確認
 curl -X POST http://localhost:8000/run_sse \
 -H "Content-Type: application/json" \
 -d '{
    "app_name": "human_tool_confirmation",
    "user_id": "user",
    "session_id": "7828f575-2402-489f-8079-74ea95b6a300",
    "new_message": {
        "parts": [
            {
                "function_response": {
                    "id": "adk-13b84a8c-c95c-4d66-b006-d72b30447e35",
                    "name": "adk_request_confirmation",
                    "response": {
                        "confirmed": true
                    }
                }
            }
        ],
        "role": "user"
    }
}'
```

基於 REST 的確認回應必須符合以下要求：

-   `function_response` 中的 `id` 應與來自 `RequestConfirmation` `FunctionCall` 事件的 `function_call_id` 相符。
-   `name` 應為 `adk_request_confirmation`。
-   `response` 物件包含確認狀態以及工具所需的任何額外 payload 數據。

> [!NOTE] 注意：搭配恢復 (Resume) 功能進行確認
    如果您的 ADK 代理工作流程配置了 [恢復 (Resume)](../../agent-runtime/resume.md) 功能，您還必須在確認回應中包含調用 ID (`invocation_id`) 參數。您提供的調用 ID 必須與生成確認請求的調用相同，否則系統會以該確認回應啟動一個新的調用。如果您的代理使用恢復功能，請考慮在確認請求中包含調用 ID 作為參數，以便將其包含在回應中。有關使用恢復功能的更多詳情，請參閱 [恢復停止的代理](../../agent-runtime/resume.md)。

## 已知限制 (Known limitations)

工具確認功能具有以下限制：

-   此功能不支援 [DatabaseSessionService](https://google.github.io/adk-docs/api-reference/python/google-adk.html#google.adk.sessions.DatabaseSessionService)。
-   此功能不支援 [VertexAiSessionService](https://google.github.io/adk-docs/api-reference/python/google-adk.html#google.adk.sessions.VertexAiSessionService)。

## 下一步

如需更多關於為代理工作流程建構 ADK 工具的資訊，請參閱 [函數工具 (Function tools)](./overview.md)。

如需如何使用 進階確認 `Advanced confirmation` 完整實作，請參閱以下範例：

- [human_tool_confirmation 參考範例](../../../python/agents/human-tool-confirmation/)