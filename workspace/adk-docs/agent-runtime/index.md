# Runtime 概述

ADK Runtime 是在使用者互動期間驅動您的代理應用程式的底層引擎。它是接收您定義的代理 (agents)、工具 (tools) 和回調 (callbacks) 並協調它們執行以回應使用者輸入的系統，管理資訊流、狀態變更以及與外部服務（如 LLM 或儲存體）的互動。

將 Runtime 視為您的代理應用程式的 **「引擎」**。您定義各個部件（代理、工具），而 Runtime 則負責處理它們如何連接並共同運作以滿足使用者的請求。

## 核心概念：事件迴圈 (Event Loop)

本質上，ADK Runtime 運作於 **事件迴圈 (Event Loop)** 之上。此迴圈促進了 `Runner` 元件與您定義的「執行邏輯 (Execution Logic)」（包含您的代理、它們進行的 LLM 呼叫、回調和工具）之間的來回通訊。

![intro_components.png](https://google.github.io/adk-docs/assets/event-loop.png)

簡單來說：

1. `Runner` 接收使用者查詢並請求主 `Agent` 開始處理。
2. `Agent`（及其相關邏輯）執行直到有事項需要報告（例如回應、使用工具的請求或狀態變更）——然後它會 **yield（產出）** 或 **emit（發出）** 一個 `Event`。
3. `Runner` 接收此 `Event`，處理任何相關的動作（例如透過 `Services` 儲存狀態變更），並將事件轉發出去（例如轉發至使用者介面）。
4. 只有在 `Runner` 處理完事件 *之後*，`Agent` 的邏輯才會從暫停處 **恢復 (resume)**，此時可能看到由 Runner 提交的變更所產生的效果。
5. 此循環會重複進行，直到代理對當前使用者查詢沒有更多的事件可以產出。

此事件驅動迴圈是 ADK 執行您的代理程式碼的基本模式。

## 核心脈動：事件迴圈 - 內部運作

事件迴圈是定義 `Runner` 與您的自訂程式碼（代理、工具、回調，在設計文件中統稱為「執行邏輯」或「邏輯元件」）之間互動的核心運作模式。它建立了明確的責任分工：

> [!NOTE]
    SDK 語言之間的具體方法名稱和參數名稱可能略有不同（例如 Python 中的 `agent.run_async(...)`，Go 中的 `agent.Run(...)`，Java 和 TypeScript 中的 `agent.runAsync(...)`）。請參閱特定語言的 API 文件以獲取詳細資訊。

### Runner 的角色（協調者）

`Runner` 擔任單次使用者調用 (invocation) 的中央協調者。它在迴圈中的職責為：

1. **啟動 (Initiation)：** 接收最終使用者的查詢 (`new_message`) 並通常透過 `SessionService` 將其附加到工作階段歷史記錄中。
2. **啟動 (Kick-off)：** 透過呼叫主代理的執行方法（例如 `agent_to_run.run_async(...)`）來開始事件生成過程。
3. **接收與處理 (Receive & Process)：** 等待代理邏輯 `yield` 或 `emit` 一個 `Event`。在收到事件後，Runner 會 **立即處理** 它。這涉及：
      * 使用配置的 `Services` (`SessionService`, `ArtifactService`, `MemoryService`) 來提交 `event.actions` 中指示的變更（如 `state_delta`, `artifact_delta`）。
      * 執行其他內部簿記工作。
4. **向上游產生 (Yield Upstream)：** 將處理後的事件轉發出去（例如轉發至呼叫的應用程式或 UI 進行渲染）。
5. **迭代 (Iterate)：** 通知代理邏輯，針對已產出事件的處理已完成，允許其恢復並生成 *下一個* 事件。

*概念性 Runner 迴圈：*

<details>
<summary>範例說明</summary>

> Python

```py
# Runner 主迴圈邏輯的簡化視圖
def run(new_query, ...) -> Generator[Event]:
    # 1. 將 new_query 附加到工作階段事件歷史記錄（透過 SessionService）
    session_service.append_event(session, Event(author='user', content=new_query))

    # 2. 透過呼叫代理啟動事件迴圈
    agent_event_generator = agent_to_run.run_async(context)

    async for event in agent_event_generator:
        # 3. 處理生成的事件並提交變更
        session_service.append_event(session, event) # 提交狀態/製品增量等
        # memory_service.update_memory(...) # 若適用
        # artifact_service 可能在代理執行期間已透過 context 被呼叫

        # 4. 產出事件供上游處理（例如 UI 渲染）
        yield event
        # Runner 隱含地通知代理生成器在產出後可以繼續
```

> TypeScript

```typescript
// Runner 主迴圈邏輯的簡化視圖
async * runAsync(newQuery: Content, ...): AsyncGenerator<Event, void, void> {
    // 1. 將 newQuery 附加到工作階段事件歷史記錄（透過 SessionService）
    await sessionService.appendEvent({
        session,
        event: createEvent({author: 'user', content: newQuery})
    });

    // 2. 透過呼叫代理啟動事件迴圈
    const agentEventGenerator = agentToRun.runAsync(context);

    for await (const event of agentEventGenerator) {
        // 3. 處理生成的事件並提交變更
        // 提交狀態/製品增量等
        await sessionService.appendEvent({session, event});
        // memoryService.updateMemory(...) // 若適用
        // artifactService 可能在代理執行期間已透過 context 被呼叫

        // 4. 產出事件供上游處理（例如 UI 渲染）
        yield event;
        // Runner 隱含地通知代理生成器在產出後可以繼續
    }
}
```

> Go

```go
// Go 中 Runner 主迴圈邏輯的簡化概念視圖
func (r *Runner) RunConceptual(ctx context.Context, session *session.Session, newQuery *genai.Content) iter.Seq2[*Event, error] {
    return func(yield func(*Event, error) bool) {
        // 1. 將 new_query 附加到工作階段事件歷史記錄（透過 SessionService）
        // ...
        userEvent := session.NewEvent(ctx.InvocationID()) // 概念視圖簡化版
        userEvent.Author = "user"
        userEvent.LLMResponse = model.LLMResponse{Content: newQuery}

        if _, err := r.sessionService.Append(ctx, &session.AppendRequest{Event: userEvent}); err != nil {
            yield(nil, err)
            return
        }

        // 2. 透過呼叫代理啟動事件串流
        // 假設 agent.Run 也返回 iter.Seq2[*Event, error]
        agentEventsAndErrs := r.agent.Run(ctx, &agent.RunRequest{Session: session, Input: newQuery})

        for event, err := range agentEventsAndErrs {
            if err != nil {
                if !yield(event, err) { // 即使有錯誤也產出事件，然後停止
                    return
                }
                return // 代理因錯誤而結束
            }

            // 3. 處理生成的事件並提交變更
            // 僅將非部分 (non-partial) 事件提交到工作階段服務（如實際程式碼所示）
            if !event.LLMResponse.Partial {
                if _, err := r.sessionService.Append(ctx, &session.AppendRequest{Event: event}); err != nil {
                    yield(nil, err)
                    return
                }
            }
            // memory_service.update_memory(...) // 若適用
            // artifact_service 可能在代理執行期間已透過 context 被呼叫

            // 4. 產出事件供上游處理
            if !yield(event, nil) {
                return // 上游消費者已停止
            }
        }
        // 代理成功結束
    }
}
```

> Java

```java
// Java 中 Runner 主迴圈邏輯的簡化概念視圖。
public Flowable<Event> runConceptual(
    Session session,
    InvocationContext invocationContext,
    Content newQuery
    ) {

    // 1. 將 new_query 附加到工作階段事件歷史記錄（透過 SessionService）
    // ...
    sessionService.appendEvent(session, userEvent).blockingGet();

    // 2. 透過呼叫代理啟動事件串流
    Flowable<Event> agentEventStream = agentToRun.runAsync(invocationContext);

    // 3. 處理每個生成的事件，提交變更，並「yield」或「emit」
    return agentEventStream.map(event -> {
        // 這會變異 session 物件（新增事件，套用 stateDelta）。
        // appendEvent 的返回值 (Single<Event>) 在概念上
        // 只是處理後的事件本身。
        sessionService.appendEvent(session, event).blockingGet(); // 簡化的阻塞呼叫

        // memory_service.update_memory(...) // 若適用 - 概念性
        // artifact_service 可能在代理執行期間已透過 context 被呼叫

        // 4. 「Yield」事件供上游處理
        //    在 RxJava 中，在 map 中返回事件即有效地將其產出給下一個運算子或訂閱者。
        return event;
    });
}
```

</details>

### 執行邏輯的角色（代理 (Agent) 、工具 (Tool) 、回調 (Callback)）

您在代理、工具和回調中的程式碼負責實際的運算和決策。它與迴圈的互動涉及：

1. **執行 (Execute)：** 根據當前的 `InvocationContext`（包括恢復執行時的工作階段狀態）執行其邏輯。
2. **產出 (Yield)：** 當邏輯需要通訊（發送訊息、呼叫工具、報告狀態變更）時，它會建構一個包含相關內容和動作的 `Event`，然後將此事件 `yield` 回 `Runner`。
3. **暫停 (Pause)：** 至關重要的是，代理邏輯的執行在 `yield` 語句（或 RxJava 中的 `return`）之後 **立即暫停**。它等待 `Runner` 完成步驟 3（處理和提交）。
4. **恢復 (Resume)：** *只有在* `Runner` 處理完產出的事件後，代理邏輯才會從緊接在 `yield` 之後的語句恢復執行。
5. **查看更新狀態 (See Updated State)：** 恢復後，代理邏輯現在可以可靠地存取工作階段狀態 (`ctx.session.state`)，該狀態反映了 `Runner` 從 *先前產出 (yield) 的* 事件中提交的變更。

*概念性執行邏輯：*

<details>
<summary>範例說明</summary>

> Python

```py
# Agent.run_async、回調或工具內部的簡化邏輯視圖

# ... 根據當前狀態執行的先前程式碼 ...

# 1. 確定需要變更或輸出，建構事件
# 範例：更新狀態
update_data = {'field_1': 'value_2'}
event_with_state_change = Event(
    author=self.name,
    actions=EventActions(state_delta=update_data),
    content=types.Content(parts=[types.Part(text="State updated.")])
    # ... 其他事件欄位 ...
)

# 2. 將事件產出 (Yield) 給 Runner 進行處理和提交
yield event_with_state_change
# <<<<<<<<<<<< 執行在此暫停 >>>>>>>>>>>>

# <<<<<<<<<<<< RUNNER 處理並提交事件 >>>>>>>>>>>>

# 3. 僅在 Runner 處理完上述事件後恢復執行。
# 現在，由 Runner 提交的狀態已可靠地反映出來。
# 後續程式碼可以安全地假設已產出事件中的變更已發生。
val = ctx.session.state['field_1']
# 此處 `val` 保證為 "value_2"（假設 Runner 提交成功）
print(f"Resumed execution. Value of field_1 is now: {val}")

# ... 後續程式碼繼續 ...
# 也許稍後產出另一個事件...
```

> TypeScript

```typescript
// Agent.runAsync、回調或工具內部的簡化邏輯視圖

// ... 根據當前狀態執行的先前程式碼 ...

// 1. 確定需要變更或輸出，建構事件
// 範例：更新狀態
const updateData = {'field_1': 'value_2'};
const eventWithStateChange = createEvent({
    author: this.name,
    actions: createEventActions({stateDelta: updateData}),
    content: {parts: [{text: "State updated."}]}
    // ... 其他事件欄位 ...
});

// 2. 將事件產出 (Yield) 給 Runner 進行處理和提交
yield eventWithStateChange;
// <<<<<<<<<<<< 執行在此暫停 >>>>>>>>>>>>

// <<<<<<<<<<<< RUNNER 處理並提交事件 >>>>>>>>>>>>

// 3. 僅在 Runner 處理完上述事件後恢復執行。
// 現在，由 Runner 提交的狀態已可靠地反映出來。
// 後續程式碼可以安全地假設已產出事件中的變更已發生。
const val = ctx.session.state['field_1'];
// 此處 `val` 保證為 "value_2"（假設 Runner 提交成功）
console.log(`Resumed execution. Value of field_1 is now: ${val}`);

// ... 後續程式碼繼續 ...
// 也許稍後產出另一個事件...
```

> Go

```go
// Agent.Run、回調或工具內部的簡化視圖

// ... 根據當前狀態執行的先前程式碼 ...

// 1. 確定需要變更或輸出，建構事件
// 範例：更新狀態
updateData := map[string]interface{}{"field_1": "value_2"}
eventWithStateChange := &Event{
    Author: self.Name(),
    Actions: &EventActions{StateDelta: updateData},
    Content: genai.NewContentFromText("State updated.", "model"),
    // ... 其他事件欄位 ...
}

// 2. 將事件產出 (Yield) 給 Runner 進行處理和提交
// 在 Go 中，這是透過將事件發送到通道 (channel) 來完成的。
eventsChan <- eventWithStateChange
// <<<<<<<<<<<< 執行在此暫停（概念上） >>>>>>>>>>>>
// 通道另一端的 Runner 將接收並處理該事件。
// 代理的 goroutine 可能會繼續，但邏輯流程會等待下一個輸入或步驟。

// <<<<<<<<<<<< RUNNER 處理並提交事件 >>>>>>>>>>>>

// 3. 僅在 Runner 處理完上述事件後恢復執行。
// 在實際的 Go 實作中，這可能由代理接收新的 RunRequest 或
// 指示下一步驟的 context 來處理。更新後的狀態將是該新請求中
// session 物件的一部分。
// 對於此概念範例，我們僅檢查狀態。
val := ctx.State.Get("field_1")
// 此處 `val` 保證為 "value_2"，因為 Runner 在再次呼叫代理之前
// 會更新工作階段狀態。
fmt.Printf("Resumed execution. Value of field_1 is now: %v\n", val)

// ... 後續程式碼繼續 ...
// 也許稍後向通道發送另一個事件...
```

> Java

```java
// Agent.runAsync、回調或工具內部的簡化視圖
// ... 根據當前狀態執行的先前程式碼 ...

// 1. 確定需要變更或輸出，建構事件
// 範例：更新狀態
ConcurrentMap<String, Object> updateData = new ConcurrentHashMap<>();
updateData.put("field_1", "value_2");

EventActions actions = EventActions.builder().stateDelta(updateData).build();
Content eventContent = Content.builder().parts(Part.fromText("State updated.")).build();

Event eventWithStateChange = Event.builder()
    .author(self.name())
    .actions(actions)
    .content(Optional.of(eventContent))
    // ... 其他事件欄位 ...
    .build();

// 2. 「Yield」事件。在 RxJava 中，這意味著將其發送到串流中。
//    Runner（或上游消費者）將訂閱此 Flowable。
//    當 Runner 接收此事件時，它將處理該事件（例如呼叫 sessionService.appendEvent）。
//    Java ADK 中的 'appendEvent' 會變異 'ctx' (InvocationContext) 中持有的 'Session' 物件。

// <<<<<<<<<<<< 概念上的暫停點 >>>>>>>>>>>>
// 在 RxJava 中，'eventWithStateChange' 的發送發生後，串流
// 可能會繼續進行 'flatMap' 或 'concatMap' 運算子，代表
// Runner 處理完此事件 *之後* 的邏輯。

// 為了模擬「僅在 Runner 處理完成後恢復執行」：
// Runner 的 `appendEvent` 本身通常是個非同步操作（返回 Single<Event>）。
// 代理的流程需要建構為：依賴於已提交狀態的後續邏輯
// 在該 `appendEvent` 完成 *之後* 執行。

// 這通常是 Runner 協調它的方式：
// Runner:
//   agent.runAsync(ctx)
//     .concatMapEager(eventFromAgent ->
//         sessionService.appendEvent(ctx.session(), eventFromAgent) // 這會更新 ctx.session().state()
//             .toFlowable() // 在處理後產出事件
//     )
//     .subscribe(processedEvent -> { /* UI renders processedEvent */ });

// 因此，在代理自身的邏輯中，如果它需要在其產出的事件被處理
// 且其狀態變更反映在 ctx.session().state() 中 *之後* 做某事，
// 該後續邏輯通常位於其反應鏈的另一個步驟中。

// 對於此概念範例，我們將發送事件，然後模擬「恢復」
// 作為 Flowable 鏈中的後續操作。

return Flowable.just(eventWithStateChange) // 步驟 2：產出事件
    .concatMap(yieldedEvent -> {
        // <<<<<<<<<<<< RUNNER 概念上處理並提交事件 >>>>>>>>>>>>
        // 此時，在實際的 runner 中，Runner 會呼叫 ctx.session().appendEvent(yieldedEvent)
        // 並且 ctx.session().state() 會被更新。
        // 由於我們 *在* 代理的概念邏輯 *內部* 試圖模擬這一點，
        // 我們假設 Runner 的動作已隱含地更新了我們的 'ctx.session()'。

        // 3. 恢復執行。
        // 現在，由 Runner（透過 sessionService.appendEvent）提交的狀態
        // 已可靠地反映在 ctx.session().state() 中。
        Object val = ctx.session().state().get("field_1");
        // 此處 `val` 保證為 "value_2"，因為 Runner 呼叫的 `sessionService.appendEvent`
        // 應該已更新了 `ctx` 物件內的工作階段狀態。

        System.out.println("Resumed execution. Value of field_1 is now: " + val);

        // ... 後續程式碼繼續 ...
        // 如果此後續程式碼需要產出另一個事件，它將在此處進行。
```

</details>

這種在 `Runner` 和您的執行邏輯之間，以 `Event` 物件為媒介的產出/暫停/恢復的協作循環，構成了 ADK Runtime 的核心。

## Runtime 的關鍵元件

多個元件在 ADK Runtime 內協同工作以執行代理調用。了解它們的角色有助於釐清事件迴圈如何運作：

1. ### `Runner`

      * **角色 (Role)：** 單次使用者查詢的主要進入點和協調者 (`run_async`)。
      * **功能 (Function)：** 管理整體事件迴圈，接收執行邏輯產出的事件，協調 Services 以處理和提交事件動作（狀態/製品變更），並將處理後的事件向上游轉發（例如轉發至 UI）。它基本上是根據產出的事件逐回合驅動對話。（定義於 `google.adk.runners.runner`）。

2. ### 執行邏輯元件 (Execution Logic Components)

      * **角色 (Role)：** 包含您的自訂程式碼和核心代理功能的部件。
      * **元件 (Components)：**
      * `Agent` (`BaseAgent`, `LlmAgent` 等)：處理資訊並決定行動的主要邏輯單元。它們實作了 `_run_async_impl` 方法來產出事件。
      * `Tools` (`BaseTool`, `FunctionTool`, `AgentTool` 等)：代理（通常是 `LlmAgent`）用來與外界互動或執行特定任務的外部函數或功能。它們執行並返回結果，這些結果隨後被包裹在事件中。
      * `Callbacks`（回調函數）：附加到代理的使用者定義函數（例如 `before_agent_callback`, `after_model_callback`），掛鉤到執行流程中的特定點，可能會修改行為或狀態，其效果會被捕捉在事件中。
      * **功能 (Function)：** 執行實際的思考、計算或外部互動。它們透過 **產出 `Event` 物件** 並暫停直到 Runner 處理它們，來傳達其結果或需求。

3. ### `Event`

      * **角色 (Role)：** 在 `Runner` 和執行邏輯之間來回傳遞的訊息。
      * **功能 (Function)：** 代表一個原子性的發生（使用者輸入、代理文字、工具呼叫/結果、狀態變更請求、控制訊號）。它同時攜帶發生的內容和預期的副作用（如 `state_delta` 等 `actions`）。

4. ### `Services`

      * **角色 (Role)：** 負責管理持久性或共用資源的後端元件。主要由 `Runner` 在事件處理期間使用。
      * **元件 (Components)：**
      * `SessionService` (`BaseSessionService`, `InMemorySessionService` 等)：管理 `Session` 物件，包括儲存/載入它們，將 `state_delta` 套用到工作階段狀態，以及將事件附加到 `event history`（事件歷史記錄）。
      * `ArtifactService` (`BaseArtifactService`, `InMemoryArtifactService`, `GcsArtifactService` 等)：管理二進位製品資料的儲存和檢索。雖然 `save_artifact` 是在執行邏輯期間透過 context 呼叫的，但事件中的 `artifact_delta` 確認了 Runner/SessionService 的動作。
      * `MemoryService` (`BaseMemoryService` 等)：（可選）管理使用者跨工作階段的長期語意記憶。
      * **功能 (Fuction)：** 提供持久層。`Runner` 與它們互動，以確保 `event.actions` 發出的變更在執行邏輯恢復 *之前* 被可靠地儲存。

5. ### `Session`

      * **角色 (Role)：** 一個資料容器，保存使用者與應用程式之間 *一次特定對話* 的狀態和歷史記錄。
      * **功能 (Function)：** 儲存目前的 `state` 字典、所有過去 `events` 的列表（`event history`），以及相關製品的參考。這是互動的主要記錄，由 `SessionService` 管理。

6. ### `Invocation`

      * **角色 (Role)：** 一個概念性術語，代表回應 *單次* 使用者查詢所發生的一切，從 `Runner` 收到查詢的那一刻起，直到代理邏輯完成該查詢的事件產出為止。
      * **功能 (Function)：** 一次調用可能涉及多次代理執行（如果使用代理轉移或 `AgentTool`）、多次 LLM 呼叫、工具執行和回調執行，所有這些都由 `InvocationContext` 中的單個 `invocation_id` 聯繫在一起。前綴為 `temp:` 的狀態變數嚴格限定於單次調用，之後會被丟棄。

這些參與者透過事件迴圈持續互動以處理使用者的請求。

## 運作方式：簡化的調用流程

讓我們追蹤一個涉及 LLM 代理呼叫工具的典型使用者查詢的簡化流程：

![intro_components.png](https://google.github.io/adk-docs/assets/invocation-flow.png)

### 逐步分解

1. **使用者輸入 (User Input)：** 使用者發送查詢（例如「法國的首都是哪裡？」）。
2. **Runner 啟動 (Runner Starts)：** `Runner.run_async` 開始。它與 `SessionService` 互動以載入相關的 `Session`，並將使用者查詢作為第一個 `Event` 新增到工作階段歷史記錄中。準備一個 `InvocationContext` (`ctx`)。
3. **代理執行 (Agent Execution)：** `Runner` 在指定的根代理（例如 `LlmAgent`）上呼叫 `agent.run_async(ctx)`。
4. **LLM 呼叫（範例）：** `Agent_Llm` 確定它需要資訊，可能是透過呼叫工具。它準備一個 `LLM` 請求。假設 LLM 決定呼叫 `MyTool`。
5. **產出 FunctionCall 事件 (Yield FunctionCall Event)：** `Agent_Llm` 收到來自 LLM 的 `FunctionCall` 回應，將其包裹在 `Event(author='Agent_Llm', content=Content(parts=[Part(function_call=...)]))` 中，並 `yields`（產出）或 `emits`（發出）此事件。
6. **代理暫停 (Agent Pauses)：** `Agent_Llm` 的執行在 `yield` 之後立即暫停。
7. **Runner 處理 (Runner Processes)：** `Runner` 接收 FunctionCall 事件。它將其傳遞給 `SessionService` 以記錄在歷史中。`Runner` 隨後將事件向上游產出給 `User`（或應用程式）。
8. **代理恢復 (Agent Resumes)：** `Runner` 發出事件已處理的信號，`Agent_Llm` 恢復執行。
9. **工具執行 (Tool Execution)：** `Agent_Llm` 的內部流程現在繼續執行請求的 `MyTool`。它呼叫 `tool.run_async(...)`。
10. **工具返回結果 (Tool Returns Result)：** `MyTool` 執行並返回其結果（例如 `{'result': 'Paris'}`）。
11. **產出 FunctionResponse 事件 (Yield FunctionResponse Event)：** 代理 (`Agent_Llm`) 將工具結果包裹進包含 `FunctionResponse` 部分的 `Event` 中（例如 `Event(author='Agent_Llm', content=Content(role='user', parts=[Part(function_response=...)]))`）。如果工具修改了狀態 (`state_delta`) 或儲存了製品 (`artifact_delta`)，此事件也可能包含 `actions`。代理 `yield`s（產出）此事件。
12. **代理暫停 (Agent Pauses)：** `Agent_Llm` 再次暫停。
13. **Runner 處理 (Runner Processes)：** `Runner` 接收 FunctionResponse 事件。它將其傳遞給 `SessionService`，後者套用任何 `state_delta`/`artifact_delta` 並將事件新增到歷史中。`Runner` 將事件向上游產出。
14. **代理恢復 (Agent Resumes)：** `Agent_Llm` 恢復，現在知道工具結果且任何狀態變更均已提交。
15. **最終 LLM 呼叫（範例）：** `Agent_Llm` 將工具結果發送回 `LLM` 以生成自然語言回應。
16. **產出最終文字事件 (Yield Final Text Event)：** `Agent_Llm` 收到來自 `LLM` 的最終文字，將其包裹在 `Event(author='Agent_Llm', content=Content(parts=[Part(text=...)]))` 中，並 `yield`s（產出）它。
17. **代理暫停 (Agent Pauses)：** `Agent_Llm` 暫停。
18. **Runner 處理 (Runner Processes)：** `Runner` 接收最終文字事件，將其傳遞給 `SessionService` 進行記錄，並將其向上游產出給 `User`。這可能被標記為 `is_final_response()`。
19. **代理恢復與結束 (Agent Resumes & Finishes)：** `Agent_Llm` 恢復。由於已完成此調用的任務，其 `run_async` 生成器結束。
20. **Runner 完成 (Runner Completes)：** `Runner` 看到代理的生成器已耗盡，並結束此調用的迴圈。

#### 流程整合表

| 步驟 | 流程 | 流程對象 | 重點說明 |
|------|----------|----------|----------|
| 1 | 使用者輸入 (User Input) | User → Runner | 使用者發送查詢(例如「法國的首都是哪裡?」) |
| 2 | Runner 啟動 (Runner Starts) | Runner → SessionService | Runner 載入 Session,將使用者查詢作為首個 Event 新增至歷史,準備 InvocationContext |
| 3 | 代理執行 (Agent Execution) | Runner → Agent | Runner 呼叫根代理的 `agent.run_async(ctx)` |
| 4 | LLM 呼叫 (LLM Call) | Agent → LLM | Agent 向 LLM 請求資訊,LLM 決定呼叫 MyTool |
| 5 | 產出 FunctionCall 事件 (Yield FunctionCall Event) | Agent → Runner | Agent 將 FunctionCall 包裹成 Event 並 yield |
| 6 | 代理暫停 (Agent Pauses) | Agent | **Agent 執行在 yield 後立即暫停** |
| 7 | Runner 處理 (Runner Processes) | Runner → SessionService → User | Runner 接收事件,記錄至歷史,向上游產出 |
| 8 | 代理恢復 (Agent Resumes) | Runner → Agent | **Runner 發出處理完成信號,Agent 恢復執行** |
| 9 | 工具執行 (Tool Execution) | Agent → MyTool | Agent 呼叫 `tool.run_async(...)` |
| 10 | 工具返回結果 (Tool Returns Result) | MyTool → Agent | MyTool 執行並返回結果(例如 `{'result': 'Paris'}`) |
| 11 | 產出 FunctionResponse 事件 (Yield FunctionResponse Event) | Agent → Runner | Agent 將工具結果包裹成含 FunctionResponse 的 Event,可能包含 state_delta/artifact_delta,並 yield |
| 12 | 代理暫停 (Agent Pauses) | Agent | **Agent 再次暫停** |
| 13 | Runner 處理 (Runner Processes) | Runner → SessionService → User | Runner 接收事件,套用 state_delta/artifact_delta,記錄至歷史,向上游產出 |
| 14 | 代理恢復 (Agent Resumes) | Runner → Agent | **Agent 恢復,此時狀態變更已提交** |
| 15 | 最終 LLM 呼叫 (Final LLM Call) | Agent → LLM | Agent 將工具結果發送回 LLM 以生成自然語言回應 |
| 16 | 產出最終文字事件 (Yield Final Text Event) | Agent → Runner | Agent 將 LLM 最終文字包裹成 Event 並 yield |
| 17 | 代理暫停 (Agent Pauses) | Agent | **Agent 暫停** |
| 18 | Runner 處理 (Runner Processes) | Runner → SessionService → User | Runner 接收最終文字事件,記錄至歷史,向上游產出(可能標記為 `is_final_response()`) |
| 19 | 代理恢復與結束 (Agent Resumes & Finishes) | Runner → Agent | **Agent 恢復,完成任務後其 run_async 生成器結束** |
| 20 | Runner 完成 (Runner Completes) | Runner | Runner 檢測到代理生成器已耗盡,結束此次調用的迴圈 |

此產出/暫停/處理/恢復循環確保狀態變更被一致地套用，並且執行邏輯在產出事件後總是基於最近提交的狀態進行操作。

## 重要的 Runtime 行為

了解 ADK Runtime 如何處理狀態、串流和非同步操作的幾個關鍵方面，對於建立可預測且高效的代理至關重要。

### 狀態更新與提交時機

* **規則：** 當您的程式碼（在代理、工具或回調中）修改工作階段狀態（例如 `context.state['my_key'] = 'new_value'`）時，此變更最初僅記錄在當前 `InvocationContext` 的本地。只有在攜帶相應 `state_delta` 的 `Event` 在其 `actions` 中被您的程式碼 `yield`（產出）並隨後由 `Runner` 處理 *之後*，該變更才 **保證被持久化**（由 `SessionService` 儲存）。

* **含義：** 在從 `yield` 恢復 *之後* 執行的程式碼可以可靠地假設 *已產出事件* 中發出的狀態變更已被提交。

<details>
<summary>範例說明</summary>

> Python

```py
# 代理邏輯內部（概念性）

# 1. 修改狀態
ctx.session.state['status'] = 'processing'
event1 = Event(..., actions=EventActions(state_delta={'status': 'processing'}))

# 2. 產出帶有增量的事件
yield event1
# --- 暫停 --- Runner 處理 event1，SessionService 提交 'status' = 'processing' ---

# 3. 恢復執行
# 現在可以安全地依賴已提交的狀態
current_status = ctx.session.state['status'] # 保證為 'processing'
print(f"Status after resuming: {current_status}")
```

> TypeScript

```typescript
// 代理邏輯內部（概念性）

// 1. 修改狀態
// 在 TypeScript 中，您透過 context 修改狀態，它會追蹤變更。
ctx.state.set('status', 'processing');
// 框架會自動從 context 中將狀態增量填入 actions。
// 為了說明，此處顯示如下。
const event1 = createEvent({
    actions: createEventActions({stateDelta: {'status': 'processing'}}),
    // ... 其他事件欄位
});

// 2. 產出帶有增量的事件
yield event1;
// --- 暫停 --- Runner 處理 event1，SessionService 提交 'status' = 'processing' ---

// 3. 恢復執行
// 現在可以安全地依賴 session 物件中的已提交狀態。
const currentStatus = ctx.session.state['status']; // 保證為 'processing'
console.log(`Status after resuming: ${currentStatus}`);
```

> Go

```go
  // 代理邏輯內部（概念性）

func (a *Agent) RunConceptual(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
  // 整個邏輯包裹在一個將作為迭代器返回的函數中。
  return func(yield func(*session.Event, error) bool) {
      // ... 根據輸入 `ctx` 的當前狀態執行的先前程式碼 ...
      // 例如，val := ctx.State().Get("field_1") 在此可能返回 "value_1"。

      // 1. 確定需要變更或輸出，建構事件
      updateData := map[string]interface{}{"field_1": "value_2"}
      eventWithStateChange := session.NewEvent(ctx.InvocationID())
      eventWithStateChange.Author = a.Name()
      eventWithStateChange.Actions = &session.EventActions{StateDelta: updateData}
      // ... 其他事件欄位 ...


      // 2. 將事件產出 (Yield) 給 Runner 進行處理和提交。
      // 代理的執行在此呼叫後立即繼續。
      if !yield(eventWithStateChange, nil) {
          // 如果 yield 返回 false，表示消費者 (Runner)
          // 已停止監聽，因此我們應該停止產生事件。
          return
      }

      // <<<<<<<<<<<< RUNNER 處理並提交事件 >>>>>>>>>>>>
      // 這發生在代理外部，在代理的迭代器產生事件之後。

      // 3. 代理 *不能* 立即看到它剛剛產出的狀態變更。
      // 在單次 `Run` 調用中，狀態是不可變的。
      val := ctx.State().Get("field_1")
      // 此處的 `val` *仍然* 是 "value_1"（或開始時的任何值）。
      // 更新後的狀態 ("value_2") 僅在後續回合的 *下一次* `Run` 調用
      // 的 `ctx` 中可用。

      // ... 後續程式碼繼續，可能產出更多事件 ...
      finalEvent := session.NewEvent(ctx.InvocationID())
      finalEvent.Author = a.Name()
      // ...
      yield(finalEvent, nil)
  }
}
```

> Java

```java
// 代理邏輯內部（概念性）
// ... 根據當前狀態執行的先前程式碼 ...

// 1. 準備狀態修改並建構事件
ConcurrentHashMap<String, Object> stateChanges = new ConcurrentHashMap<>();
stateChanges.put("status", "processing");

EventActions actions = EventActions.builder().stateDelta(stateChanges).build();
Content content = Content.builder().parts(Part.fromText("Status update: processing")).build();

Event event1 = Event.builder()
    .actions(actions)
    // ...
    .build();

// 2. 產出帶有增量的事件
return Flowable.just(event1)
    .map(
        emittedEvent -> {
            // --- 概念性暫停與 Runner 處理 ---
            // 3. 恢復執行（概念性）
            // 現在可以安全地依賴已提交的狀態。
            String currentStatus = (String) ctx.session().state().get("status");
            System.out.println("Status after resuming (inside agent logic): " + currentStatus); // 保證為 'processing'

            // 事件本身 (event1) 被傳遞下去。
            // 如果此代理步驟中的後續邏輯產生了 *另一個* 事件，
            // 您會使用 concatMap 來發送該新事件。
            return emittedEvent;
        });

// ... 後續代理邏輯可能涉及進一步的反應式運算子
// 或根據現在已更新的 `ctx.session().state()` 發送更多事件。
```

</details>

### 工作階段狀態的「髒讀 (Dirty Reads)」

* **定義：** 雖然提交發生在產出 *之後*，但 *在同一次調用內* 稍後執行，但 *在* 改變狀態的事件實際被產出和處理 *之前* 的程式碼，**通常可以看到本地的、未提交的變更**。這有時被稱為「髒讀 (dirty read)」。
* **範例：**

<details>
<summary>範例說明</summary>

> Python

```py
# before_agent_callback 中的程式碼
callback_context.state['field_1'] = 'value_1'
# 狀態在本地設置為 'value_1'，但尚未被 Runner 提交

# ... 代理執行 ...

# 稍後 *在同一次調用內* 呼叫的工具中的程式碼
# 可讀取（髒讀），但 'value_1' 尚未保證持久化。
val = tool_context.state['field_1'] # 此處 'val' 可能為 'value_1'
print(f"Dirty read value in tool: {val}")

# 假設攜帶 state_delta={'field_1': 'value_1'} 的事件
# 是在此工具執行 *之後* 被產出並由 Runner 處理的。
```

> TypeScript

```typescript
// beforeAgentCallback 中的程式碼
callbackContext.state.set('field_1', 'value_1');
// 狀態在本地設置為 'value_1'，但尚未被 Runner 提交

// --- 代理執行 ... ---

// --- 稍後 *在同一次調用內* 呼叫的工具中的程式碼 ---
// 可讀取（髒讀），但 'value_1' 尚未保證持久化。
const val = toolContext.state.get('field_1'); // 此處 'val' 可能為 'value_1'
console.log(`Dirty read value in tool: ${val}`);

// 假設攜帶 state_delta={'field_1': 'value_1'} 的事件
// 是在此工具執行 *之後* 被產出並由 Runner 處理的。
```

> Go

```go
// before_agent_callback 中的程式碼
// 回調將直接修改 context 的工作階段狀態。
// 此變更對於當前調用 context 是局部的。
ctx.State.Set("field_1", "value_1")
// 狀態在本地設置為 'value_1'，但尚未被 Runner 提交

// ... 代理執行 ...

// 稍後 *在同一次調用內* 呼叫的工具中的程式碼
// 可讀取（髒讀），但 'value_1' 尚未保證持久化。
val := ctx.State.Get("field_1") // 此處 'val' 可能為 'value_1'
fmt.Printf("Dirty read value in tool: %v\n", val)

// 假設攜帶 state_delta={'field_1': 'value_1'} 的事件
// 是在此工具執行 *之後* 被產出並由 Runner 處理的。
```

> Java

```java
// 修改狀態 - BeforeAgentCallback 中的程式碼
// 並且將此變更暫存在 callbackContext.eventActions().stateDelta() 中。
callbackContext.state().put("field_1", "value_1");

// --- 代理執行 ... ---

// --- 稍後 *在同一次調用內* 呼叫的工具中的程式碼 ---
// 可讀取（髒讀），但 'value_1' 尚未保證持久化。
Object val = toolContext.state().get("field_1"); // 此處 'val' 可能為 'value_1'
System.out.println("Dirty read value in tool: " + val);
// 假設攜帶 state_delta={'field_1': 'value_1'} 的事件
// 是在此工具執行 *之後* 被產出並由 Runner 處理的。
```

</details>

* **含義：**
  * **優點：** 允許您在單個複雜步驟（例如在下一次 LLM 回合之前的多個回調或工具呼叫）內的不同部分邏輯使用狀態進行協調，而無需等待完整的產出/提交循環。
  * **警告：** 嚴重依賴髒讀來執行關鍵邏輯是有風險的。如果調用在攜帶 `state_delta` 的事件被產出並由 `Runner` 處理 *之前* 失敗，則未提交的狀態變更將會丟失。對於關鍵的狀態轉換，請確保它們與成功處理的事件相關聯。

### 串流與非串流輸出 (Streaming vs. Non-Streaming Output) (`partial=True`)

這主要與如何處理來自 LLM 的回應有關，特別是在使用串流生成 API 時。

* **串流 (Streaming)：** LLM 逐個 token 或以小塊生成回應。
  * 框架（通常在 `BaseLlmFlow` 內）會為單個概念性回應產出多個 `Event` 物件。這些事件大多具有 `partial=True`。
  * `Runner` 在收到 `partial=True` 的事件後，通常會 **立即將其向上游轉發**（供 UI 顯示），但 **跳過處理其 `actions`**（如 `state_delta`）。
  * 最終，框架會產出該回應的最終事件，標記為非部分 (`partial=False` 或隱含透過 `turn_complete=True`)。
  * `Runner` **僅完全處理此最終事件**，提交任何相關的 `state_delta` 或 `artifact_delta`。
* **非串流 (Non-Streaming)：** LLM 一次生成整個回應。框架產出一個標記為非部分的單個事件，`Runner` 將對其進行完全處理。
* **為何重要：** 確保狀態變更是基於 LLM 的 *完整* 回應原子性地且僅應用一次，同時仍允許 UI 在生成文字時逐步顯示。

## 非同步為主 (`run_async`)

* **核心設計：** ADK Runtime 從根本上建立在非同步模式和程式庫（如 Python 的 `asyncio`，Java 的 `RxJava`，以及 TypeScript 中的原生 `Promise` 和 `AsyncGenerator`）之上，以高效地處理並發操作（如等待 LLM 回應或工具執行）而不發生阻塞。
* **主要進入點：** `Runner.run_async` 是執行代理調用的主要方法。所有核心可執行元件（代理、特定流程）內部都使用 `asynchronous` 方法。
* **同步便利性 (`run`)：** 存在的同步 `Runner.run` 方法主要是為了方便（例如，在簡單的腳本或測試環境中）。然而，在內部，`Runner.run` 通常只是呼叫 `Runner.run_async` 並為您管理非同步事件迴圈的執行。
* **開發者體驗：** 我們建議將您的應用程式（例如使用 ADK 的網頁伺服器）設計為非同步以獲得最佳效能。在 Python 中，這意味著使用 `asyncio`；在 Java 中，利用 `RxJava` 的反應式程式設計模型；在 TypeScript 中，這意味著使用原生 `Promise` 和 `AsyncGenerator` 進行構建。
* **同步回調/工具：** ADK 框架支援工具和回調的非同步和同步函數。
    * **阻塞 I/O：** 對於長時間執行的同步 I/O 操作，框架會嘗試防止停頓。Python ADK 可能使用 asyncio.to_thread，而 Java ADK 通常依賴適當的 RxJava 調度器或包裝器來進行阻塞呼叫。在 TypeScript 中，框架僅等待函數；如果同步函數執行阻塞 I/O，它將使事件迴圈停頓。開發者應盡可能使用非同步 I/O API（返回 Promise）。
    * **CPU 密集型工作：** 純 CPU 密集型的同步任務在兩種環境中仍會阻塞其執行執行緒。

了解這些行為有助於您編寫更穩健的 ADK 應用程式，並對與狀態一致性、串流更新和非同步執行相關的問題進行除錯。

## 總結

ADK Runtime 是驅動 AI 代理 (Agent) 的核心引擎，它如同一個精密的指揮系統，協調代理的思考邏輯、工具的使用以及狀態的管理。為了讓您快速掌握 Runtime 的全貌，我們將其精華濃縮如下：

### 1. 入門：Runtime 是什麼？
想像您設計了一個 AI 代理，它有大腦 (邏輯) 和手腳 (工具)。**Runtime 就是讓這個 AI 活起來的「作業系統」**。
*   您不需要擔心訊息如何傳遞、狀態如何保存。
*   您只需要專注於定義「代理該做什麼」，Runtime 會負責處理「如何讓它運作」。

### 2. 核心：事件迴圈 (Event Loop) 的運作
Runtime 的運作就像是一場 **「接力賽跑」**，由 **Runner (協調者)** 和 **Agent (執行者)** 輪流交棒：
1.  **Runner 發令 (Start)**：收到使用者的訊息，Runner 啟動 Agent。
2.  **Agent 跑棒 (Execute)**：Agent 執行邏輯，直到它決定做某件事（例如回話或用工具）。
3.  **交棒 (Yield)**：Agent 發出一個 **事件 (Event)** 給 Runner，然後 **暫停 (Pause)** 等待。
4.  **Runner 處理 (Process)**：Runner 接過事件，執行必要的動作（如儲存狀態、更新畫面）。
5.  **Agent 接棒 (Resume)**：Runner 處理完畢後，Agent **恢復 (Resume)** 執行，並能看到最新的狀態。
*這個循環會不斷重複，直到 Agent 完成任務。*

### 3. 進階：關鍵重點綱要
*   **四大支柱**：
    *   **Runner**：控制流程的中心。
    *   **Agent**：執行邏輯的大腦。
    *   **Event**：溝通的訊息載體。
    *   **Services**：管理記憶與檔案的後勤。
*   **重要特性**：
    *   **狀態確認 (Commit)**：狀態的變更只有在事件被 Runner 成功處理後才算「存檔完成」。
    *   **非同步架構 (Async)**：為了高效能，系統預設採用非同步設計，適合處理 LLM 等待與 I/O 操作。
    *   **串流支援 (Streaming)**：支援 LLM 的串流輸出，讓回應能即時呈現給使用者。
