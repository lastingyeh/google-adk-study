# 運行時事件迴圈 (Runtime Event Loop)

> 🔔 `更新日期：2026-01-27`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/runtime/event-loop/

[`ADK 支援`: `Python v0.1.0` | `Typescript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

ADK 運行時 (Runtime) 是在使用者互動期間驅動您的代理程式應用程式的底層引擎。它是一個系統，負責接收您定義的代理程式、工具和回呼，並編排它們的執行以回應使用者輸入，管理資訊流、狀態變化以及與 LLM 或儲存等外部服務的互動。

可以將運行時想像成代理程式應用程式的 **「引擎」**。您定義各個零件（代理程式、工具），而運行時則負責處理它們如何連接和共同運行，以滿足使用者的請求。

## 核心概念：事件迴圈 (The Event Loop)

ADK 運行時的核心運作模式是**事件迴圈 (Event Loop)**。此迴圈促進了 `Runner` 組件與您定義的「執行邏輯」（包括您的代理程式、它們發出的 LLM 呼叫、回呼和工具）之間的往返通訊。

![intro_components.png](https://google.github.io/adk-docs/assets/event-loop.png)

簡單來說：

1. `Runner` 接收使用者查詢並要求主 `Agent` 開始處理。
2. `Agent`（及其相關邏輯）持續運行，直到有內容需要報告（例如回應、使用工具的請求或狀態更改）——然後它會**產出 (yield)** 或**發送 (emit)** 一個 `Event`。
3. `Runner` 接收此 `Event`，處理任何相關操作（例如透過 `Services` 儲存狀態更改），並將事件向前轉發（例如轉發給使用者介面）。
4. 只有在 `Runner` 處理完事件*之後*，`Agent` 的邏輯才會從暫停的地方**恢復 (resume)**，此時它可能會看到由 Runner 提交的更改效果。
5. 循環往復，直到代理程式對於當前的使用者查詢不再有產出事件為止。

這種事件驅動迴圈是管理 ADK 如何執行您的代理程式程式碼的基本模式。

## 心跳 (The Heartbeat)：事件迴圈 - 內部運作

事件迴圈是定義 `Runner` 與您的自訂程式碼（代理程式、工具、回呼，在設計文件中統稱為「執行邏輯」或「邏輯組件」）之間互動的核心操作模式。它建立了明確的責任分工：

> [!NOTE]
具體的方法名稱和參數名稱可能因 SDK 語言而異（例如 Python 中的 `agent.run_async(...)`、Go 中的 `agent.Run(...)`、Java 和 TypeScript 中的 `agent.runAsync(...)`）。詳情請參閱各語言特定的 API 文件。

### Runner 的角色 (協調者)

`Runner` 作為單次使用者調用的中央協調器。它在迴圈中的職責是：

1. **啟動 (Initiation)：** 接收終端使用者的查詢 (`new_message`)，通常會透過 `SessionService` 將其追加到對話歷史紀錄中。
2. **啟跑 (Kick-off)：** 透過呼叫主代理程式的執行方法（例如 `agent_to_run.run_async(...)`）啟動事件生成過程。
3. **接收與處理 (Receive & Process)：** 等待代理程式邏輯 `yield` 或 `emit` 一個 `Event`。收到事件後，Runner 會**立即處理**它。這包括：
      * 使用配置的 `Services` (`SessionService`, `ArtifactService`, `MemoryService`) 來提交 `event.actions` 中指示的更改（例如 `state_delta`, `artifact_delta`）。
      * 執行其他內部簿記工作。
4. **向上游產出 (Yield Upstream)：** 將處理後的事件向前轉發（例如轉發給呼叫應用程式或 UI 進行渲染）。
5. **迭代 (Iterate)：** 向代理程式邏輯發送信號，表示產出事件的處理已完成，允許其恢復並生成*下一個*事件。

<details>
<summary>概念性 Runner 迴圈：</summary>

> Python

```python
# Runner 主迴圈邏輯的簡化視圖
async def run(new_query, ...) -> Generator[Event]:
    # 1. 將 new_query 追加到對話事件歷史紀錄中 (透過 SessionService)
    session_service.append_event(session, Event(author='user', content=new_query))

    # 2. 透過呼叫代理程式啟動事件迴圈
    agent_event_generator = agent_to_run.run_async(context)

    async for event in agent_event_generator:
        # 3. 處理生成的事件並提交更改
        session_service.append_event(session, event) # 提交狀態/產出物增量 (deltas) 等。
        # memory_service.update_memory(...) # 如果適用
        # artifact_service 可能在代理程式運行期間已透過 context 被呼叫

        # 4. 為上游處理產出事件 (例如 UI 渲染)
        yield event
        # Runner 在產出後隱式發訊號表示代理程式生成器可以繼續
```

> typescript

```typescript
// Runner 主迴圈邏輯的簡化視圖
async * runAsync(newQuery: Content, ...): AsyncGenerator<Event, void, void> {
    // 1. 將 newQuery 追加到對話事件歷史紀錄中 (透過 SessionService)
    await sessionService.appendEvent({
        session,
        event: createEvent({author: 'user', content: newQuery})
    });

    // 2. 透過呼叫代理程式啟動事件迴圈
    const agentEventGenerator = agentToRun.runAsync(context);

    for await (const event of agentEventGenerator) {
        // 3. 處理生成的事件並提交更改
        // 提交狀態/產出物增量 (deltas) 等。
        await sessionService.appendEvent({session, event});
        // memoryService.updateMemory(...) // 如果適用
        // artifactService 可能在代理程式運行期間已透過 context 被呼叫

        // 4. 為上游處理產出事件 (例如 UI 渲染)
        yield event;
        // Runner 在產出後隱式發訊號表示代理程式生成器可以繼續
    }
}
```

> go

```go
// Go 中 Runner 主迴圈邏輯的簡化概念視圖
func (r *Runner) RunConceptual(ctx context.Context, session *session.Session, newQuery *genai.Content) iter.Seq2[*Event, error] {
    return func(yield func(*Event, error) bool) {
        // 1. 將 new_query 追加到對話事件歷史紀錄中 (透過 SessionService)
        // ...
        userEvent := session.NewEvent(ctx.InvocationID()) // 概念視圖簡化
        userEvent.Author = "user"
        userEvent.LLMResponse = model.LLMResponse{Content: newQuery}

        if _, err := r.sessionService.Append(ctx, &session.AppendRequest{Event: userEvent}); err != nil {
            yield(nil, err)
            return
        }

        // 2. 透過呼叫代理程式啟動事件串流
        // 假設 agent.Run 也回傳 iter.Seq2[*Event, error]
        agentEventsAndErrs := r.agent.Run(ctx, &agent.RunRequest{Session: session, Input: newQuery})

        for event, err := range agentEventsAndErrs {
            if err != nil {
                if !yield(event, err) { // 即使發生錯誤也產出事件，然後停止
                    return
                }
                return // 代理程式以錯誤結束
            }

            // 3. 處理生成的事件並提交更改
            // 僅將非部分 (non-partial) 事件提交給對話服務 (如實際程式碼所示)
            if !event.LLMResponse.Partial {
                if _, err := r.sessionService.Append(ctx, &session.AppendRequest{Event: event}); err != nil {
                    yield(nil, err)
                    return
                }
            }
            // memory_service.update_memory(...) // 如果適用
            // artifact_service 可能在代理程式運行期間已透過 context 被呼叫

            // 4. 為上游處理產出事件
            if !yield(event, nil) {
                return // 上游消費者已停止
            }
        }
        // 代理程式成功結束
    }
}
```

> java

```java
// Java 中 Runner 主迴圈邏輯的簡化概念視圖。
public Flowable<Event> runConceptual(
    Session session,
    InvocationContext invocationContext,
    Content newQuery
    ) {

    // 1. 將 new_query 追加到對話事件歷史紀錄中 (透過 SessionService)
    // ...
    sessionService.appendEvent(session, userEvent).blockingGet();

    // 2. 透過呼叫代理程式啟動事件串流
    Flowable<Event> agentEventStream = agentToRun.runAsync(invocationContext);

    // 3. 處理每個生成的事件，提交更改，並「產出」或「發送」
    return agentEventStream.map(event -> {
        // 這會變更對話物件 (新增事件，套用 stateDelta)。
        // appendEvent 的回傳值 (一個 Single<Event>) 在概念上
        // 只是處理後的事件本身。
        sessionService.appendEvent(session, event).blockingGet(); // 簡化的阻塞呼叫

        // memory_service.update_memory(...) // 如果適用 - 概念性
        // artifact_service 可能在代理程式運行期間已透過 context 被呼叫

        // 4. 「產出」事件供上游處理
        // 在 RxJava 中，在 map 中回傳事件有效地將其產出給下一個操作符或訂閱者。
        return event;
    });
}
```
</details>

### 執行邏輯的角色 (代理程式、工具、回呼)

代理程式、工具和回呼中的程式碼負責實際的計算和決策。它與迴圈的互動涉及：

1. **執行 (Execute)：** 根據目前的 `InvocationContext` 運行其邏輯，包括*恢復執行時*的對話狀態。
2. **產出 (Yield)：** 當邏輯需要通訊時（發送訊息、呼叫工具、報告狀態更改），它會建構一個包含相關內容和操作的 `Event`，然後將此事件 `yield` 回 `Runner`。
3. **暫停 (Pause)：** 至關重要的是，代理程式邏輯的執行在 `yield` 語句（或 RxJava 中的 `return`）之後**立即暫停**。它等待 `Runner` 完成步驟 3（處理和提交）。
4. **恢復 (Resume)：***只有在* `Runner` 處理完產出事件後，代理程式邏輯才會從緊接在 `yield` 之後的語句恢復執行。
5. **查看更新後的狀態 (See Updated State)：** 恢復後，代理程式邏輯現在可以可靠地存取對話狀態 (`ctx.session.state`)，這反映了由 `Runner` 從*先前產出的事件*中提交的更改。


<details>
<summary> 概念性執行邏輯： </summary>

> Python

```python
# Agent.run_async、回呼或工具內部邏輯的簡化視圖

# ... 先前程式碼根據目前狀態運行 ...

# 1. 確定需要更改或輸出，建構事件
# 範例：更新狀態
update_data = {'field_1': 'value_2'}
event_with_state_change = Event(
    author=self.name,
    actions=EventActions(state_delta=update_data),
    content=types.Content(parts=[types.Part(text="狀態已更新。")])
    # ... 其他事件欄位 ...
)

# 2. 將事件產出給 Runner 進行處理和提交
yield event_with_state_change
# <<<<<<<<<<<< 執行在此暫停 >>>>>>>>>>>>

# <<<<<<<<<<<< RUNNER 處理並提交事件 >>>>>>>>>>>>

# 3. 只有在 Runner 處理完上述事件後才恢復執行。
# 現在，Runner 提交的狀態已可靠反映。
# 後續程式碼可以安全地假設來自產出事件的更改已發生。
val = ctx.session.state['field_1']
# 這裡保證 `val` 為 "value_2" (假設 Runner 成功提交)
print(f"恢復執行。field_1 的值現在為：{val}")

# ... 後續程式碼繼續 ...
# 稍後可能產出另一個事件...
```

> typescript

```typescript
// Agent.runAsync、回呼或工具內部邏輯的簡化視圖

// ... 先前程式碼根據目前狀態運行 ...

// 1. 確定需要更改或輸出，建構事件
// 範例：更新狀態
const updateData = {'field_1': 'value_2'};
const eventWithStateChange = createEvent({
    author: this.name,
    actions: createEventActions({stateDelta: updateData}),
    content: {parts: [{text: "狀態已更新。"}]}
    // ... 其他事件欄位 ...
});

// 2. 將事件產出給 Runner 進行處理和提交
yield eventWithStateChange;
// <<<<<<<<<<<< 執行在此暫停 >>>>>>>>>>>>

// <<<<<<<<<<<< RUNNER 處理並提交事件 >>>>>>>>>>>>

// 3. 只有在 Runner 處理完上述事件後才恢復執行。
# 現在，Runner 提交的狀態已可靠反映。
# 後續程式碼可以安全地假設來自產出事件的更改已發生。
const val = ctx.session.state['field_1'];
// 這裡保證 `val` 為 "value_2" (假設 Runner 成功提交)
console.log(`恢復執行。field_1 的值現在為：${val}`);

// ... 後續程式碼繼續 ...
// 稍後可能產出另一個事件...
```

> go

```go
// Agent.Run、回呼或工具內部邏輯的簡化視圖

// ... 先前程式碼根據目前狀態運行 ...

// 1. 確定需要更改或輸出，建構事件
// 範例：更新狀態
updateData := map[string]interface{}{"field_1": "value_2"}
eventWithStateChange := &Event{
    Author: self.Name(),
    Actions: &EventActions{StateDelta: updateData},
    Content: genai.NewContentFromText("狀態已更新。", "model"),
    // ... 其他事件欄位 ...
}

// 2. 將事件產出給 Runner 進行處理和提交
// 在 Go 中，這透過將事件發送到通道 (channel) 來完成。
eventsChan <- eventWithStateChange
// <<<<<<<<<<<< 執行在此暫停 (概念上) >>>>>>>>>>>>
// 通道另一側的 Runner 將接收並處理該事件。
// 代理程式的 goroutine 可能會繼續，但邏輯流會等待下一個輸入或步驟。

// <<<<<<<<<<<< RUNNER 處理並提交事件 >>>>>>>>>>>>

// 3. 只有在 Runner 處理完上述事件後才恢復執行。
// 在實際的 Go 實作中，這通常透過代理程式接收
// 新的 RunRequest 或指示下一步的 context 來處理。更新後的狀態
// 將成為該新請求中對話物件的一部分。
// 對於此概念範例，我們將僅檢查狀態。
val := ctx.State.Get("field_1")
// 這裡保證 `val` 為 "value_2"，因為 Runner 在再次呼叫代理程式之前
// 會更新對話狀態。
fmt.Printf("恢復執行。field_1 的值現在為：%v\n", val)

// ... 後續程式碼繼續 ...
// 稍後可能向通道發送另一個事件...
```

> java

```java
// Agent.runAsync、回呼或工具內部邏輯的簡化視圖
// ... 先前程式碼根據目前狀態運行 ...

// 1. 確定需要更改或輸出，建構事件
// 範例：更新狀態
ConcurrentMap<String, Object> updateData = new ConcurrentHashMap<>();
updateData.put("field_1", "value_2");

EventActions actions = EventActions.builder().stateDelta(updateData).build();
Content eventContent = Content.builder().parts(Part.fromText("狀態已更新。")).build();

Event eventWithStateChange = Event.builder()
    .author(self.name())
    .actions(actions)
    .content(Optional.of(eventContent))
    // ... 其他事件欄位 ...
    .build();

// 2. 「產出」事件。在 RxJava 中，這意味著將其發送到串流中。
//    Runner (或上游消費者) 將訂閱此 Flowable。
//    當 Runner 接收到此事件時，它將處理它 (例如呼叫 sessionService.appendEvent)。
//    Java ADK 中的 'appendEvent' 會變更 'ctx' (InvocationContext) 中持有的 'Session' 物件。

// <<<<<<<<<<<< 概念性暫停點 >>>>>>>>>>>>
// 在 RxJava 中，發送 'eventWithStateChange' 會發生，然後串流
// 可能會繼續使用 'flatMap' 或 'concatMap' 操作符，代表
// Runner 處理此事件*之後*的邏輯。

// 為了模擬「只有在 Runner 處理完後才恢復執行」：
// Runner 的 `appendEvent` 通常本身就是一個非同步操作 (回傳 Single<Event>)。
// 代理程式的流程需要結構化，以便後續
// 依賴已提交狀態的邏輯在 `appendEvent` 完成*之後*運行。

// 這是 Runner 通常編排它的方式：
// Runner:
//   agent.runAsync(ctx)
//     .concatMapEager(eventFromAgent ->
//         sessionService.appendEvent(ctx.session(), eventFromAgent) // 這會更新 ctx.session().state()
//             .toFlowable() // 在事件處理後發送它
//     )
//     .subscribe(processedEvent -> { /* UI 渲染 processedEvent */ });

// 因此，在代理程式自身的邏輯中，如果它需要在其產出的事件
// 被處理且其狀態更改已反映在 ctx.session().state() 中*之後*執行某些操作，
// 該後續邏輯通常會位於其反應式鏈的另一個步驟中。

// 對於這個概念範例，我們將發送事件，然後模擬「恢復」
// 作為 Flowable 鏈中的後續操作。

return Flowable.just(eventWithStateChange) // 步驟 2：產出事件
    .concatMap(yieldedEvent -> {
        // <<<<<<<<<<<< RUNNER 概念上處理並提交事件 >>>>>>>>>>>>
        // 此時，在實際的運行時中，Runner 會呼叫 ctx.session().appendEvent(yieldedEvent)
        // 且 ctx.session().state() 會被更新。
        // 由於我們是在代理程式的概念邏輯*內部*嘗試模擬這一點，
        // 我們假設 Runner 的動作已隱式更新了我們的 'ctx.session()'。

        // 3. 恢復執行。
        // 現在，由 Runner (透過 sessionService.appendEvent) 提交的狀態
        // 已可靠地反映在 ctx.session().state() 中。
        Object val = ctx.session().state().get("field_1");
        // 這裡保證 `val` 為 "value_2"，因為由 Runner 呼叫的
        // `sessionService.appendEvent` 會更新 `ctx` 物件內的對話狀態。

        System.out.println("恢復執行。field_1 的值現在為：" + val);

        // ... 後續程式碼繼續 ...
        // 如果後續程式碼需要產出另一個事件，會在此處執行。
```
</details>

這是在 `Runner` 與您的執行邏輯之間，由 `Event` 物件媒合的協作產出/暫停/恢復循環，構成了 ADK 運行時的核心。

![event_loop_diagram.png](../assets/agent-runtime_event-loop.png)

## 運行時的主要組件

多個組件在 ADK 運行時內協同工作以執行代理程式調用。了解它們的角色可以釐清事件迴圈如何運作：

1. ### `Runner`

      * **角色：** 單次使用者查詢 (`run_async`) 的主要進入點和協調器。
      * **功能：** 管理整體的事件迴圈，接收執行邏輯產出的事件，與 Services 協調以處理和提交事件操作（狀態/產出物更改），並將處理後的事件向上游轉發（例如轉發給 UI）。它基本上是根據產出的事件，逐輪驅動對話。（定義在 `google.adk.runners.runner`）。

2. ### 執行邏輯組件 (Execution Logic Components)

      * **角色：** 包含您的自訂程式碼和核心代理程式功能的零件。
      * **組件：**
      * `Agent` (`BaseAgent`, `LlmAgent` 等)：您的主要邏輯單元，負責處理資訊並決定採取的操作。它們實作了產出事件的 `_run_async_impl` 方法。
      * `Tools` (`BaseTool`, `FunctionTool`, `AgentTool` 等)：由代理程式（通常是 `LlmAgent`）使用的外部函數或功能，用於與外界互動或執行特定任務。它們執行並回傳結果，然後包裝在事件中。
      * `Callbacks` (函數)：附加到代理程式的使用者定義函數（例如 `before_agent_callback`, `after_model_callback`），它們掛接到執行流程中的特定點，可能修改行為或狀態，其效果會記錄在事件中。
      * **功能：** 執行實際的思考、計算或外部互動。它們透過**產出 `Event` 物件**來傳遞結果或需求，並暫停直到 Runner 處理完它們。

3. ### `Event`

      * **角色：** 在 `Runner` 與執行邏輯之間往返傳遞的訊息。
      * **功能：** 代表原子發生的事件（使用者輸入、代理程式文本、工具呼叫/結果、狀態更改請求、控制訊號）。它同時攜帶發生的內容和預期的副作用（如 `state_delta` 的 `actions`）。

4. ### `Services`

      * **角色：** 負責管理持久性或共享資源的後端組件。主要由 `Runner` 在事件處理期間使用。
      * **組件：**
      * `SessionService` (`BaseSessionService`, `InMemorySessionService` 等)：管理 `Session` 物件，包括儲存/載入、將 `state_delta` 套用到對話狀態，以及將事件追加到 `對話歷史紀錄`。
      * `ArtifactService` (`BaseArtifactService`, `InMemoryArtifactService`, `GcsArtifactService` 等)：管理二進位產出物資料的儲存與檢索。雖然 `save_artifact` 是在執行邏輯期間透過 context 呼叫的，但事件中的 `artifact_delta` 會向 Runner/SessionService 確認此操作。
      * `MemoryService` (`BaseMemoryService` 等)：（選配）管理使用者跨對話的長期語義記憶。
      * **功能：** 提供持久化層。`Runner` 與它們互動，確保在執行邏輯恢復*之前*，`event.actions` 發出的更改已被可靠儲存。

5. ### `Session`

      * **角色：** 資料容器，保存使用者與應用程式之間*一次特定對話*的狀態與歷史。
      * **功能：** 儲存目前的 `state` 字典、所有過去事件的清單（`對話歷史紀錄`）以及相關產出物的引用。它是互動的主要紀錄，由 `SessionService` 管理。

6. ### `Invocation`

      * **角色：** 概念性術語，代表為回應*單次*使用者查詢而發生的所有事情，從 `Runner` 接收查詢那一刻起到代理程式邏輯完成該查詢的事件產出為止。
      * **功能：** 一次調用可能涉及多次代理程式運行（如果使用代理程式轉移或 `AgentTool`）、多次 LLM 呼叫、工具執行和回呼執行，所有這些都透過 `InvocationContext` 內的單個 `invocation_id` 連結在一起。前綴為 `temp:` 的狀態變數嚴格限於單次調用，之後會被捨棄。

這些角色透過事件迴圈持續互動，以處理使用者的請求。

## 運作原理：簡化的調用範例

讓我們追蹤一個典型使用者查詢的簡化流程，涉及 LLM 代理程式呼叫工具：

![intro_components.png](https://google.github.io/adk-docs/assets/invocation-flow.png)

### 逐步分解

1. **使用者輸入：** 使用者發送查詢（例如「法國的首都是哪裡？」）。
2. **Runner 啟動：** `Runner.run_async` 開始。它與 `SessionService` 互動以載入相關 `Session`，並將使用者查詢作為第一個 `Event` 新增到對話歷史紀錄中。準備 `InvocationContext` (`ctx`)。
3. **代理程式執行：** `Runner` 對指定的根代理程式（例如 `LlmAgent`）呼叫 `agent.run_async(ctx)`。
4. **LLM 呼叫 (範例)：** `Agent_Llm` 判斷它需要資訊，可能是透過呼叫工具。它為 `LLM` 準備請求。假設 LLM 決定呼叫 `MyTool`。
5. **產出 FunctionCall 事件：** `Agent_Llm` 收到來自 LLM 的 `FunctionCall` 回應，將其包裝在 `Event(author='Agent_Llm', content=Content(parts=[Part(function_call=...)]))` 中，並 `yield` 或 `emit` 此事件。
6. **代理程式暫停：** `Agent_Llm` 的執行在 `yield` 之後立即暫停。
7. **Runner 處理：** `Runner` 接收到 FunctionCall 事件。它將其傳遞給 `SessionService` 以記錄在歷史紀錄中。然後 `Runner` 將事件向上游產出給 `User`（或應用程式）。
8. **代理程式恢復：** `Runner` 發訊號表示事件已處理，`Agent_Llm` 恢復執行。
9. **工具執行：** `Agent_Llm` 的內部流程現在繼續執行請求的 `MyTool`。它呼叫 `tool.run_async(...)`。
10. **工具回傳結果：** `MyTool` 執行並回傳結果（例如 `{'result': '巴黎'}`）。
11. **產出 FunctionResponse 事件：** 代理程式 (`Agent_Llm`) 將工具結果包裝成包含 `FunctionResponse` 部分的 `Event`（例如 `Event(author='Agent_Llm', content=Content(role='user', parts=[Part(function_response=...)]))`）。如果工具修改了狀態 (`state_delta`) 或儲存了產出物 (`artifact_delta`)，此事件也可能包含 `actions`。代理程式 `yield` 此事件。
12. **代理程式暫停：** `Agent_Llm` 再次暫停。
13. **Runner 處理：** `Runner` 接收到 FunctionResponse 事件。它將其傳遞給 `SessionService`，後者會套用任何 `state_delta`/`artifact_delta` 並將事件新增到歷史紀錄中。`Runner` 將事件向上游產出。
14. **代理程式恢復：** `Agent_Llm` 恢復執行，現在知道工具結果和任何狀態更改都已提交。
15. **最終 LLM 呼叫 (範例)：** `Agent_Llm` 將工具結果發送回 `LLM` 以生成自然語言回應。
16. **產出最終文本事件：** `Agent_Llm` 收到來自 `LLM` 的最終文本，將其包裝在 `Event(author='Agent_Llm', content=Content(parts=[Part(text=...)]))` 中並 `yield` 產出。
17. **代理程式暫停：** `Agent_Llm` 暫停。
18. **Runner 處理：** `Runner` 接收最終文本事件，傳遞給 `SessionService` 紀錄歷史，並向上游產出給 `User`。這通常被標記為 `is_final_response()`。
19. **代理程式恢復並結束：** `Agent_Llm` 恢復。完成此調用的任務後，其 `run_async` 生成器結束。
20. **Runner 完成：** `Runner` 看到代理程式的生成器已耗盡，並結束此調用的迴圈。

此產出/暫停/處理/恢復循環確保狀態更改被一致套用，且執行邏輯在產出事件後始終操作於最近提交的狀態。

## 重要的運行時行為

了解 ADK 運行時如何處理狀態、串流和非同步操作的幾個關鍵方面，對於建立可預測且高效的代理程式至關重要。

### 狀態更新與提交時機

* **規則：** 當您的程式碼（在代理程式、工具或回呼中）修改對話狀態（例如 `context.state['my_key'] = 'new_value'`）時，此更改最初會記錄在當前 `InvocationContext` 的本地。只有在帶有對應 `actions` 中 `state_delta` 的 `Event` 被您的程式碼 `yield` 產出並隨後被 `Runner` 處理之後，該更改才**保證被持久化**（由 `SessionService` 儲存）。

* **意義：** 在從 `yield` 恢復*之後*運行的程式碼可以可靠地假設在*產出的事件*中發出的狀態更改已經被提交。

<details>
<summary>概念性範例：</summary>

> Python
```python
# 代理程式邏輯內部 (概念性)

# 1. 修改狀態
ctx.session.state['status'] = 'processing'
event1 = Event(..., actions=EventActions(state_delta={'status': 'processing'}))

# 2. 產出帶有 delta 的事件
yield event1
# --- 暫停 --- Runner 處理 event1，SessionService 提交 'status' = 'processing' ---

# 3. 恢復執行
# 現在可以安全地依賴已提交的狀態
current_status = ctx.session.state['status'] # 保證為 'processing'
print(f"恢復後的狀態：{current_status}")
```

> typescript

```typescript
// 代理程式邏輯內部 (概念性)

// 1. 修改狀態
// 在 TypeScript 中，您透過 context 修改狀態，它會追蹤更改。
ctx.state.set('status', 'processing');
// 框架將自動根據 context 的狀態增量 (delta) 填入 actions。
// 為了說明，此處顯示如下。
const event1 = createEvent({
    actions: createEventActions({stateDelta: {'status': 'processing'}}),
    // ... 其他事件欄位
});

// 2. 產出帶有 delta 的事件
yield event1;
// --- 暫停 --- Runner 處理 event1，SessionService 提交 'status' = 'processing' ---

// 3. 恢復執行
// 現在可以安全地依賴對話物件中已提交的狀態。
const currentStatus = ctx.session.state['status']; // 保證為 'processing'
console.log(`恢復後的狀態：${currentStatus}`);
```

> go

```go
  // 代理程式邏輯內部 (概念性)

func (a *Agent) RunConceptual(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
  // 整個邏輯包裝在一個函數中，該函數將作為迭代器回傳。
  return func(yield func(*session.Event, error) bool) {
      // ... 先前程式碼根據來自輸入 `ctx` 的目前狀態運行 ...
      // 例如，val := ctx.State().Get("field_1") 在此可能回傳 "value_1"。

      // 1. 確定需要更改或輸出，建構事件
      updateData := map[string]interface{}{"field_1": "value_2"}
      eventWithStateChange := session.NewEvent(ctx.InvocationID())
      eventWithStateChange.Author = a.Name()
      eventWithStateChange.Actions = &session.EventActions{StateDelta: updateData}
      // ... 其他事件欄位 ...


      // 2. 將事件產出給 Runner 進行處理和提交。
      // 代理程式的執行在此呼叫後立即繼續。
      if !yield(eventWithStateChange, nil) {
          // 如果 yield 回傳 false，代表消費者 (Runner)
          // 已停止監聽，因此我們應該停止生成事件。
          return
      }

      // <<<<<<<<<<<< RUNNER 處理並提交事件 >>>>>>>>>>>>
      // 這發生在代理程式外部，在代理程式的迭代器生成事件之後。

      // 3. 代理程式無法立即看到它剛剛產出的狀態更改。
      // 在單次 `Run` 調用中，狀態是不可變的。
      val := ctx.State().Get("field_1")
      // 這裡的 `val` 仍然是 "value_1" (或啟動時的值)。
      // 更新後的狀態 ("value_2") 僅在後續輪次的*下一次* `Run` 調用的 `ctx` 中可用。

      // ... 後續程式碼繼續，可能產出更多事件 ...
      finalEvent := session.NewEvent(ctx.InvocationID())
      finalEvent.Author = a.Name()
      // ...
      yield(finalEvent, nil)
  }
}
```

> java

```java
// 代理程式邏輯內部 (概念性)
// ... 先前程式碼根據目前狀態運行 ...

// 1. 準備狀態修改並建構事件
ConcurrentHashMap<String, Object> stateChanges = new ConcurrentHashMap<>();
stateChanges.put("status", "processing");

EventActions actions = EventActions.builder().stateDelta(stateChanges).build();
Content content = Content.builder().parts(Part.fromText("狀態更新：正在處理")).build();

Event event1 = Event.builder()
    .actions(actions)
    // ...
    .build();

// 2. 產出帶有 delta 的事件
return Flowable.just(event1)
    .map(
        emittedEvent -> {
            // --- 概念性暫停與 RUNNER 處理 ---
            // 3. 恢復執行 (概念上)
            // 現在可以安全地依賴已提交的狀態。
            String currentStatus = (String) ctx.session().state().get("status");
            System.out.println("恢復執行後 (代理程式邏輯內部)：" + currentStatus); // 保證為 'processing'

            // 事件本身 (event1) 被傳遞下去。
            // 如果此代理程式步驟中的後續邏輯產生了*另一個*事件，
            // 您會使用 concatMap 來發送該新事件。
            return emittedEvent;
        });

// ... 後續代理程式邏輯可能涉及進一步的反應式操作符
// 或根據現在已更新的 `ctx.session().state()` 發送更多事件。
```
</details>

### 對話狀態的「髒讀 (Dirty Reads)」

* **定義：** 雖然提交發生在產出之後，但在*同一次調用中的稍後*運行、但在狀態更改事件實際產出並處理*之前*的程式碼，**通常可以看到本地未提交的更改**。這有時被稱為「髒讀 (dirty read)」。
* ****

<details>
<summary>範例：</summary>

> Python
```python
# before_agent_callback 中的程式碼
callback_context.state['field_1'] = 'value_1'
# 狀態在本地設置為 'value_1'，但尚未由 Runner 提交

# ... 代理程式運行 ...

# 在*同一次調用中*稍後呼叫的工具程式碼
# 可讀取 (髒讀)，但 'value_1' 尚未保證持久化。
val = tool_context.state['field_1'] # 這裡 'val' 很可能是 'value_1'
print(f"工具中的髒讀值：{val}")

# 假設帶有 state_delta={'field_1': 'value_1'} 的事件
# 在此工具運行之後產出並由 Runner 處理。
```

> typescript

```typescript
// beforeAgentCallback 中的程式碼
callbackContext.state.set('field_1', 'value_1');
// 狀態在本地設置為 'value_1'，但尚未由 Runner 提交

// --- 代理程式運行 ... ---

// --- 在*同一次調用中*稍後呼叫的工具程式碼 ---
// 可讀取 (髒讀)，但 'value_1' 尚未保證持久化。
const val = toolContext.state.get('field_1'); // 這裡 'val' 很可能是 'value_1'
console.log(`工具中的髒讀值：${val}`);

// 假設帶有 state_delta={'field_1': 'value_1'} 的事件
// 在此工具運行之後產出並由 Runner 處理。
```

> go

```go
// before_agent_callback 中的程式碼
// 回呼會直接修改 context 的對話狀態。
// 此更改對於當前調用 context 是本地的。
ctx.State.Set("field_1", "value_1")
// 狀態在本地設置為 'value_1'，但尚未由 Runner 提交

// ... 代理程式運行 ...

// 在*同一次調用中*稍後呼叫的工具程式碼
// 可讀取 (髒讀)，但 'value_1' 尚未保證持久化。
val := ctx.State.Get("field_1") // 這裡 'val' 很可能是 'value_1'
fmt.Printf("工具中的髒讀值：%v\n", val)

// 假設帶有 state_delta={'field_1': 'value_1'} 的事件
// 在此工具運行之後產出並由 Runner 處理。
```

> java

```java
// 修改狀態 - BeforeAgentCallback 中的程式碼
// 並在 callbackContext.eventActions().stateDelta() 中暫存此更改。
callbackContext.state().put("field_1", "value_1");

// --- 代理程式運行 ... ---

// --- 在*同一次調用中*稍後呼叫的工具程式碼 ---
// 可讀取 (髒讀)，但 'value_1' 尚未保證持久化。
Object val = toolContext.state().get("field_1"); // 這裡 'val' 很可能是 'value_1'
System.out.println("工具中的髒讀值：" + val);
// 假設帶有 state_delta={'field_1': 'value_1'} 的事件
// 在此工具運行之後產出並由 Runner 處理。
```
</details>

* **影響：**
  * **優點：** 允許單個複雜步驟中的不同邏輯部分（例如在下一次 LLM 輪次之前的多次回呼或工具呼叫）使用狀態進行協調，而無需等待完整的產出/提交循環。
  * **警告：** 過度依賴髒讀來處理關鍵邏輯可能有風險。如果調用在帶有 `state_delta` 的事件產出並由 `Runner` 處理*之前*失敗，未提交的狀態更改將會丟失。對於關鍵的狀態轉換，請確保它們與成功處理的事件相關聯。

### 串流與非串流輸出 (`partial=True`)

這主要與如何處理來自 LLM 的回應有關，特別是在使用串流生成 API 時。

* **串流 (Streaming)：** LLM 逐字 (token-by-token) 或以小塊生成回應。
  * 框架（通常在 `BaseLlmFlow` 內）會為單個概念性回應產出多個 `Event` 物件。這些事件中的大多數將標記為 `partial=True`。
  * `Runner` 在接收到 `partial=True` 的事件時，通常會**立即將其轉發**給上游（供 UI 顯示），但會**跳過對其 `actions`（如 `state_delta`）的處理**。
  * 最終，框架會為該回應產出一個最終事件，標記為非部分 (`partial=False` 或隱式透過 `turn_complete=True`)。
  * `Runner` **僅完全處理此最終事件**，提交任何相關的 `state_delta` 或 `artifact_delta`。
* **非串流 (Non-Streaming)：** LLM 一次生成整個回應。框架產出一個標記為非部分的單個事件，`Runner` 對其進行完全處理。
* **為什麼重要：** 確保狀態更改根據來自 LLM 的*完整*回應以原子方式且僅套用一次，同時仍允許 UI 在文本生成時逐步顯示。

## 非同步是首選 (`run_async`)

* **核心設計：** ADK 運行時從根本上建立在非同步模式和函式庫（如 Python 的 `asyncio`、Java 的 `RxJava` 以及 TypeScript 中的原生 `Promise` 和 `AsyncGenerator`）之上，以高效地處理並發操作（如等待 LLM 回應或工具執行）而不發生阻塞。
* **主要進入點：** `Runner.run_async` 是執行代理程式調用的主要方法。所有核心可運行組件（代理程式、特定流程）內部都使用 `asynchronous` 方法。
* **同步便捷方法 (`run`)：** 存在同步 `Runner.run` 方法主要是為了方便（例如在簡單的腳本或測試環境中）。然而，在內部，`Runner.run` 通常只是呼叫 `Runner.run_async` 並為您管理非同步事件迴圈執行。
* **開發者體驗：** 我們建議將您的應用程式（例如使用 ADK 的網頁伺服器）設計為非同步以獲得最佳效能。在 Python 中，這意味著使用 `asyncio`；在 Java 中，利用 `RxJava` 的反應式編程模型；在 TypeScript 中，這意味著使用原生的 `Promise` 和 `AsyncGenerator` 進行構建。
* **同步回呼/工具：** ADK 框架支援工具和回呼的非同步與同步函數。
    * **阻塞式 I/O：** 對於長時間運行的同步 I/O 操作，框架會嘗試防止停頓。Python ADK 可能會使用 `asyncio.to_thread`，而 Java ADK 通常依賴適當的 RxJava 調度器或包裝器來進行阻塞呼叫。在 TypeScript 中，框架只是簡單地等待 (await) 函數；如果同步函數執行阻塞式 I/O，它將使事件迴圈停頓。開發者應盡可能使用非同步 I/O API（回傳 Promise）。
    * **CPU 密集型工作：** 純粹的 CPU 密集型同步任務在兩種環境中仍會阻塞其執行執行緒。

了解這些行為有助於您編寫更穩健的 ADK 應用程式，並偵錯與狀態一致性、串流更新和非同步執行相關的問題。

## 總結說明

### 運行組件整合

| 組件 | 角色 | 主要功能 | 參考位置 |
|---|---|---|---|
| `Runner` | 單次查詢的協調器 | 管理事件迴圈、接收並處理 `Event`、與 `Services` 協調並向上游產出處理後的事件 | `google.adk.runners.runner` |
| 執行邏輯（Agent / Tools / Callbacks） | 實際決策與外部互動的執行單元 | 產出 `Event`（包括 LLM 呼叫、工具呼叫、回呼產生的變更）、暫停並在 Runner 處理後恢復 | Agent 實作 `_run_async_impl` / 各類 `Tool` |
| `Event` | 訊息與副作用的載體 | 表示原子事件（使用者輸入、FunctionCall/Response、狀態/產出物變更等），並攜帶 `actions`（如 `state_delta`、`artifact_delta`） | - |
| `Services` | 持久化與共享資源管理 | 管理並提交狀態/產出物（Session/Artifact/Memory），確保在執行邏輯恢復前變更已被儲存 | `SessionService`, `ArtifactService`, `MemoryService` |
| `Session` | 單次對話的狀態容器 | 保存 `state`、對話歷史與產出物參考，作為 Invocation 的資料來源／目標 | 由 `SessionService` 管理 |
| `Invocation` | 單次調用的範圍概念 | 將反覆的代理程式運行、LLM 呼叫與工具執行以 `invocation_id` 聯結；`temp:` 前綴的狀態限於此範圍 | - |
