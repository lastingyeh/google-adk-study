# 為 Agent 倒回 (Rewind) 會話

🔔 `更新日期：2026 年 1 月 5 日`

ADK 的會話倒回 (Rewind) 功能允許您將會話還原到之前的請求狀態，讓您能夠撤銷錯誤、探索替代路徑，或從已知的良好起點重新開始流程。本文件提供該功能的概述、使用方法及其限制。

## 倒回會話 (Rewind a session)

當您倒回會話時，需要指定一個您想要撤銷的使用者請求或 **_調用 (invocation)_**，系統將會撤銷該請求及其之後的所有請求。
例如：如果您有三個請求 (A, B, C)，而您想回到請求 A 之後的狀態，您應指定 B，這將撤銷來自請求 B 和 C 的變更。

您可以透過在 **_Runner_** 實例上使用 `rewind_async` 方法，並指定使用者、會話和調用 ID (invocation id) 來倒回會話，如下列程式碼片段所示：

> **重點說明**：倒回操作會將會話層級的資源還原到指定調用 ID _之前_ 的狀態。

```python
# 1. 建立 Runner 實例
runner = InMemoryRunner(
    agent=agent.root_agent,
    app_name=APP_NAME,
)

# 2. 建立會話 (Session)
session = await runner.session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID
)

# 3. 呼叫 Agent（例如：設定狀態顏色為紅色）
await call_agent_async(
    runner, USER_ID, session.id, "set state color to red"
)

# ... 執行更多 Agent 呼叫 ...

# 4. 更新狀態顏色為藍色，並獲取事件列表以取得調用 ID
events_list = await call_agent_async(
    runner, USER_ID, session.id, "update state color to blue"
)

# 5. 獲取想要倒回的調用 ID (此處假設要倒回更新為藍色的操作)
rewind_invocation_id = events_list[1].invocation_id

# 6. 執行倒回操作 (執行後狀態顏色將回復為：紅色)
await runner.rewind_async(
    user_id=USER_ID,
    session_id=session.id,
    rewind_before_invocation_id=rewind_invocation_id,
)
```

當您呼叫 **_rewind_** 方法時，所有由 ADK 管理的「會話層級 (session-level)」資源都會還原到您透過 **_invocation id_** 指定的請求*之前*的狀態，參考[範例連結](https://github.com/google/adk-python/tree/main/contributing/samples/rewind_session)。然而，全域資源（例如應用程式層級或使用者層級的狀態與成果物 Artifacts）則**不會**被還原，限制說明[連結](#倒回會話-rewind-a-session)。

## 運作原理

倒回功能會建立一個特殊的 **_rewind_** 請求，將會話的狀態和成果物還原到指定調用 ID 之前的狀況。這種方式意味著所有請求（包括被倒回的請求）都會保留在日誌中，以便日後進行偵錯、分析或審計。

倒回後，系統在為 AI 模型準備下一個請求時，會忽略已倒回的請求。這表示 Agent 所使用的 AI 模型實際上會「忘記」從倒回點到下一個請求之間的所有互動。

## 使用限制

在使用倒回功能於 Agent 工作流時，請留意以下限制：

- **全域 Agent 資源**：應用程式層級 (App-level) 和使用者層級 (User-level) 的狀態與成果物**不會**被倒回功能還原。僅還原會話層級 (Session-level) 的內容。
- **外部依賴項**：倒回功能不管理外部依賴。如果您的 Agent 工具與外部系統互動，您需要自行負責將這些系統還原至先前的狀態。
- **原子性 (Atomicity)**：狀態更新、成果物更新和事件持久化並非在單一原子事務中執行。因此，應避免倒回進行中的活躍會話，或在倒回期間同時操作會話成果物，以防止數據不一致。

## 參考資源

- [rewind_session 範例程式碼](https://github.com/google/adk-python/tree/main/contributing/samples/rewind_session)
- [限制說明](https://google.github.io/adk-docs/sessions/rewind/#how-it-works)