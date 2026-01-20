# 自定義代理 (Custom agents)
🔔 `更新日期：2026-01-14`

[`ADK 支援`: `Python v0.1.0` | `Typescript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

自定義代理在 ADK 中提供了極致的靈活性，允許您透過直接繼承 `BaseAgent` 並實現自己的控制流來定義**任意編排邏輯**。這超越了 `SequentialAgent`、`LoopAgent` 和 `ParallelAgent` 的預定義模式，使您能夠構建高度特定且複雜的代理工作流。

> [!WARNING] 進階概念
    透過直接實現 `_run_async_impl`（或其在其他語言中的等效項）來構建自定義代理可提供強大的控制力，但比使用預定義的 `LlmAgent` 或標準 `WorkflowAgent` 類型更為複雜。我們建議在嘗試自定義編排邏輯之前，先了解這些基礎代理類型。

## 簡介：超越預定義的工作流

### 什麼是自定義代理？

自定義代理本質上是您創建的任何繼承自 `google.adk.agents.BaseAgent` 的類別，並在其 `_run_async_impl` 非同步方法中實現其核心執行邏輯。您可以完全控制此方法如何呼叫其他代理（子代理）、管理狀態以及處理事件。

> [!NOTE]
    用於實現代理核心非同步邏輯的特定方法名稱可能會因 SDK 語言而略有不同（例如，Java 中的 `runAsyncImpl`、Python 中的 `_run_async_impl` 或 TypeScript 中的 `runAsyncImpl`）。詳情請參閱各語言特定的 API 文件。

### 為什麼要使用它們？

雖然標準 [工作流代理](workflow-agents/index.md) (`SequentialAgent`, `LoopAgent`, `ParallelAgent`) 涵蓋了常見的編排模式，但當您的需求包括以下內容時，您將需要自定義代理：

* **條件邏輯 (Conditional Logic)：** 根據執行時條件或先前步驟的結果執行不同的子代理或採取不同的路徑。
* **複雜的狀態管理 (Complex state Management)：** 實現精細的邏輯，用於在整個工作流中維護和更新狀態，而不僅僅是簡單的順序傳遞。
* **外部整合 (External Integrations)：** 直接在編排流程控制中加入對外部 API、資料庫或自定義庫的呼叫。
* **動態代理選擇 (Dynamic Agent Selection)：** 根據對情況或輸入的動態評估，選擇下一個要運行的子代理。
* **獨特的工作流模式 (Unique Workflow Pattern)：** 實現不符合標準順序、並行或迴圈結構的編排邏輯。

![intro_components.png](https://google.github.io/adk-docs/assets/custom-agent-flow.png)

## 實現自定義邏輯：

任何自定義代理的核心在於您定義其獨特非同步行為的方法。此方法允許您編排子代理並管理執行流程。

<details>
<summary>Python</summary>

任何自定義代理的核心是 `_run_async_impl` 方法。這是您定義其獨特行為的地方。

* **簽名：** `async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:`
* **非同步產生器：** 它必須是一個 `async def` 函式並返回一個 `AsyncGenerator`。這允許它將子代理或其自身邏輯產生的事件 `yield` 回運行器 (runner)。
* **`ctx` (InvocationContext):** 提供對關鍵執行時資訊的訪問，最重要的是 `ctx.session.state`，這是由您的自定義代理編排的步驟之間共享資料的主要方式。
</details>

<details>
<summary>TypeScript</summary>

任何自定義代理的核心是 `runAsyncImpl` 方法。這是您定義其獨特行為的地方。

*   **簽名：** `async* runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined>`
*   **非同步產生器：** 它必須是一個 `async` 產生器函式 (`async*`)。
*   **`ctx` (InvocationContext):** 提供對關鍵執行時資訊的訪問，最重要的是 `ctx.session.state`，這是由您的自定義代理編排的步驟之間共享資料的主要方式。
</details>

<details>
<summary>Go</summary>

在 Go 中，您將 `Run` 方法作為滿足 `agent.Agent` 介面的結構體的一部分來實現。實際邏輯通常是您的自定義代理結構體上的一個方法。

*   **簽名：** `Run(ctx agent.InvocationContext) iter.Seq2[*session.Event, error]`
*   **迭代器：** `Run` 方法返回一個迭代器 (`iter.Seq2`)，用於產生事件和錯誤。這是處理代理執行串流結果的標準方式。
*   **`ctx` (InvocationContext):** `agent.InvocationContext` 提供對會話（包括狀態）和其他關鍵執行時資訊的訪問。
*   **會話狀態：** 您可以透過 `ctx.Session().State()` 訪問會話狀態。
</details>

<details>
<summary>Java</summary>

任何自定義代理的核心是 `runAsyncImpl` 方法，您從 `BaseAgent` 覆寫該方法。

*   **簽名：** `protected Flowable<Event> runAsyncImpl(InvocationContext ctx)`
*   **反應式串流 (`Flowable`)：** 它必須返回一個 `io.reactivex.rxjava3.core.Flowable<Event>`。此 `Flowable` 代表將由自定義代理邏輯產生的事件串流，通常是透過組合或轉換來自子代理的多個 `Flowable`。
*   **`ctx` (InvocationContext):** 提供對關鍵執行時資訊的訪問，最重要的是 `ctx.session().state()`，它是一個 `java.util.concurrent.ConcurrentMap<String, Object>`。這是由您的自定義代理編排的步驟之間共享資料的主要方式。
</details>

---
**核心非同步方法中的關鍵功能：**

<details>
<summary>Python</summary>

1. **呼叫子代理：** 您使用子代理（通常儲存為實例屬性，如 `self.my_llm_agent`）的 `run_async` 方法並產生其事件：

    ```python
    # 遍歷子代理的非同步事件產生器
    async for event in self.some_sub_agent.run_async(ctx):
        # 可選擇檢查或記錄事件
        yield event # 將事件向上傳遞
    ```
2. **管理狀態：** 從會話狀態字典 (`ctx.session.state`) 讀取和寫入資料，以便在子代理呼叫之間傳遞資料或做出決策：

    ```python
    # 讀取先前代理設定的資料
    previous_result = ctx.session.state.get("some_key")

    # 根據狀態做出決策
    if previous_result == "some_value":
        # ... 呼叫特定的子代理 ...
    else:
        # ... 呼叫另一個子代理 ...

    # 為稍後的步驟儲存結果（通常透過子代理的 output_key 完成）
    # ctx.session.state["my_custom_result"] = "calculated_value"
    ```

3. **實現控制流：** 使用標準 Python 結構 (`if`/`elif`/`else`, `for`/`while` 迴圈, `try`/`except`) 來創建涉及子代理的精細、有條件或迭代的工作流。
</details>

<details>
<summary>TypeScript</summary>

 1.  **呼叫子代理：** 您使用子代理（通常儲存為實例屬性，如 `this.myLlmAgent`）的 `run` 方法並產生其事件：

    ```typescript
    // 使用 for await 遍歷子代理的非同步事件
    for await (const event of this.someSubAgent.runAsync(ctx)) {
        // 可選擇檢查或記錄事件
        yield event; // 將事件向上傳遞給運行器
    }
    ```

2.  **管理狀態：** 從會話狀態物件 (`ctx.session.state`) 讀取和寫入資料，以便在子代理呼叫之間傳遞資料或做出決策：

    ```typescript
    // 讀取先前代理設定的資料
    const previousResult = ctx.session.state['some_key'];

    // 根據狀態做出決策
    if (previousResult === 'some_value') {
      // ... 呼叫特定的子代理 ...
    } else {
      // ... 呼叫另一個子代理 ...
    }

    // 為稍後的步驟儲存結果（通常透過子代理的 outputKey 完成）
    // ctx.session.state['my_custom_result'] = 'calculated_value';
    ```

3. **實現控制流：** 使用標準 TypeScript/JavaScript 結構 (`if`/`else`, `for`/`while` 迴圈, `try`/`catch`) 來創建涉及子代理的精細、有條件或迭代的工作流。
</details>

<details>
<summary>Go</summary>

 1. **呼叫子代理：** 您透過呼叫子代理的 `Run` 方法來啟動它們。

    ```go
    // 範例：執行一個子代理並產生其事件
    for event, err := range someSubAgent.Run(ctx) {
        if err != nil {
            // 處理或傳播錯誤
            return
        }
        // 將事件向上產生給呼叫者
        if !yield(event, nil) {
        return
        }
    }
    ```

 2. **管理狀態：** 從會話狀態讀取和寫入資料，以便在子代理呼叫之間傳遞資料或做出決策。
    ```go
    // `ctx` (`agent.InvocationContext`) 會直接傳遞給代理的 `Run` 函式。
    // 讀取先前代理設定的資料
    previousResult, err := ctx.Session().State().Get("some_key")
    if err != nil {
        // 處理金鑰可能尚不存在的情況
    }

    // 根據狀態做出決策
    if val, ok := previousResult.(string); ok && val == "some_value" {
        // ... 呼叫特定的子代理 ...
    } else {
        // ... 呼叫另一個子代理 ...
    }

    // 為稍後的步驟儲存結果
    if err := ctx.Session().State().Set("my_custom_result", "calculated_value"); err != nil {
        // 處理錯誤
    }
    ```

 3. **實現控制流：** 使用標準 Go 結構 (`if`/`else`, `for`/`switch` 迴圈, goroutines, channels) 來創建涉及子代理的精細、有條件或迭代的工作流。
</details>

<details>
<summary>Java</summary>

1. **呼叫子代理：** 您使用子代理（通常儲存為實例屬性或物件）的非同步執行方法並返回其事件串流：

    您通常使用 RxJava 運算子（如 `concatWith`、`flatMapPublisher` 或 `concatArray`）來連結來自子代理的 `Flowable`。

    ```java
    // 範例：執行一個子代理
    // return someSubAgent.runAsync(ctx);

    // 範例：順序執行子代理
    Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
        .doOnNext(event -> System.out.println("來自代理 1 的事件: " + event.id()));

    Flowable<Event> secondAgentEvents = Flowable.defer(() ->
        someSubAgent2.runAsync(ctx)
            .doOnNext(event -> System.out.println("來自代理 2 的事件: " + event.id()))
    );

    return firstAgentEvents.concatWith(secondAgentEvents);
    ```
    如果後續階段的執行取決於先前階段完成後的完成情況或狀態，則通常使用 `Flowable.defer()`。

 2. **管理狀態：** 從會話狀態讀取和寫入資料，以便在子代理呼叫之間傳遞資料或做出決策。會話狀態是透過 `ctx.session().state()` 獲得的 `java.util.concurrent.ConcurrentMap<String, Object>`。

     ```java
     // 讀取先前代理設定的資料
     Object previousResult = ctx.session().state().get("some_key");

     // 根據狀態做出決策
     if ("some_value".equals(previousResult)) {
         // ... 包含特定子代理 Flowable 的邏輯 ...
     } else {
         // ... 包含另一個子代理 Flowable 的邏輯 ...
     }

     // 為稍後的步驟儲存結果（通常透過子代理的 output_key 完成）
     // ctx.session().state().put("my_custom_result", "calculated_value");
     ```

 3. **實現控制流：** 將標準語言結構 (`if`/`else`, 迴圈, `try`/`catch`) 與反應式運算子 (RxJava) 結合使用，以創建精細的工作流。

    *   **有條件：** 使用 `Flowable.defer()` 根據條件選擇要訂閱的 `Flowable`，或如果您在串流中過濾事件，則使用 `filter()`。
    *   **迭代：** 使用 `repeat()`、`retry()` 等運算子，或透過構建您的 `Flowable` 鏈以根據條件遞迴呼叫其自身部分（通常使用 `flatMapPublisher` 或 `concatMap` 管理）。
</details>


## 管理子代理和狀態

通常，自定義代理會編排其他代理（如 `LlmAgent`、`LoopAgent` 等）。

* **初始化：** 您通常將這些子代理的實例傳遞到自定義代理的建構函式中，並將其儲存為實例欄位/屬性（例如，`this.story_generator = story_generator_instance` 或 `self.story_generator = story_generator_instance`）。這使得它們可以在自定義代理的核心非同步執行邏輯（例如：`_run_async_impl` 方法）中被存取。
* **子代理列表：** 使用 `super()` 建構函式初始化 `BaseAgent` 時，應傳遞一個 `sub agents` 列表。此列表告訴 ADK 框架關於此自定義代理直接層級結構中的代理。這對於框架功能（如生命週期管理、內省以及未來的路由功能）非常重要，即使您的核心執行邏輯 (`_run_async_impl`) 透過 `self.xxx_agent` 直接呼叫代理。請包含您的自定義邏輯在最上層直接呼叫的代理。
* **狀態：** 如前所述，`ctx.session.state` 是子代理（特別是使用 `output key` 的 `LlmAgent`）將結果回傳給編排器，以及編排器如何將必要的輸入向下傳遞的標準方式。

## 設計模式範例：`StoryFlowAgent`

讓我們用一個範例模式來說明自定義代理的力量：一個具有條件邏輯的多階段內容生成工作流。

**目標：** 創建一個系統，生成故事，透過批評和修改迭代地完善它，執行最終檢查，並且至關重要的是，**如果最終語調檢查失敗，則重新生成故事**。

**為什麼要自定義？** 這裡驅動對自定義代理需求的核心要求是**基於語調檢查的條件式重新生成**。標準工作流代理沒有基於子代理任務結果的內建條件分支。我們需要在編排器中加入自定義邏輯 (`if tone == "negative": ...`)。

---

### 第 1 部分：簡化的自定義代理初始化

<details>
<summary>範例說明</summary>

> Python

```python
# 定義繼承自 BaseAgent 的 StoryFlowAgent
class StoryFlowAgent(BaseAgent):
    def __init__(self, story_generator, critic, reviser, grammar_check, tone_check):
        # 儲存傳入的子代理實例
        self.story_generator = story_generator

        # 創建一個迴圈代理來處理批評和修改的迭代
        self.loop_agent = LoopAgent(
            agent=SequentialAgent(agents=[critic, reviser]),
            max_iterations=3
        )

        # 創建一個順序代理來處理後處理步驟
        self.sequential_agent = SequentialAgent(
            agents=[grammar_check, tone_check]
        )

        # 呼叫父類別建構函式，註冊頂層子代理
        super().__init__(agents=[self.story_generator, self.loop_agent, self.sequential_agent])
```

> typescript

```typescript
// 定義擴展自 BaseAgent 的 StoryFlowAgent
export class StoryFlowAgent extends BaseAgent {
  private storyGenerator: LlmAgent;
  private loopAgent: LoopAgent;
  private sequentialAgent: SequentialAgent;

  constructor(storyGenerator: LlmAgent, critic: LlmAgent, reviser: LlmAgent, grammarCheck: LlmAgent, toneCheck: LlmAgent) {
    // 1. 儲存主要的子代理
    const storyGen = storyGenerator;

    // 2. 建立內部的複合代理
    const loop = new LoopAgent({
      agent: new SequentialAgent({ agents: [critic, reviser] }),
      maxIterations: 3
    });

    const sequential = new SequentialAgent({
      agents: [grammarCheck, toneCheck]
    });

    // 3. 呼叫 super 並註冊所有頂層子代理
    super({ agents: [storyGen, loop, sequential] });

    this.storyGenerator = storyGen;
    this.loopAgent = loop;
    this.sequentialAgent = sequential;
  }
}
```

> go

```go
// StoryFlowAgent 結構體定義
type StoryFlowAgent struct {
    *agent.BaseAgent
    storyGenerator       agent.Agent
    revisionLoopAgent    agent.Agent
    postProcessorAgent   agent.Agent
}

// NewStoryFlowAgent 建立一個新的故事流程代理實例
func NewStoryFlowAgent(storyGen, critic, reviser, grammar, tone agent.Agent) *StoryFlowAgent {
    // 建立內部的迴圈與順序代理
    loop, _ := loopagent.New(loopagent.Config{
        Agent:         sequentialagent.New(sequentialagent.Config{Agents: []agent.Agent{critic, reviser}}),
        MaxIterations: 3,
    })

    post, _ := sequentialagent.New(sequentialagent.Config{
        Agents: []agent.Agent{grammar, tone},
    })

    return &StoryFlowAgent{
        BaseAgent:          agent.NewBaseAgent(agent.BaseConfig{Agents: []agent.Agent{storyGen, loop, post}}),
        storyGenerator:     storyGen,
        revisionLoopAgent:  loop,
        postProcessorAgent: post,
    }
}
```

> java

```java
// 定義擴展自 BaseAgent 的 StoryFlowAgentExample
public class StoryFlowAgentExample extends BaseAgent {
    private final LlmAgent storyGenerator;
    private final LoopAgent loopAgent;
    private final SequentialAgent sequentialAgent;

    public StoryFlowAgentExample(LlmAgent storyGenerator, LlmAgent critic, LlmAgent reviser, LlmAgent grammarCheck, LlmAgent toneCheck) {
        // 註冊頂層子代理到父類別
        super(List.of(storyGenerator,
            new LoopAgent(new SequentialAgent(List.of(critic, reviser)), 3),
            new SequentialAgent(List.of(grammarCheck, toneCheck))));

        this.storyGenerator = storyGenerator;
        this.loopAgent = (LoopAgent) getAgents().get(1);
        this.sequentialAgent = (SequentialAgent) getAgents().get(2);
    }
}
```

</details>

---

### 第 2 部分：定義自定義執行邏輯

<details>
<summary>範例說明</summary>

> Python

```python
async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
    # 1. 執行初始故事生成
    async for event in self.story_generator.run_async(ctx):
        yield event

    # 2. 執行批評與修改迴圈
    async for event in self.loop_agent.run_async(ctx):
        yield event

    # 3. 執行語法與語調檢查
    async for event in self.sequential_agent.run_async(ctx):
        yield event

    # 4. 自定義條件邏輯：如果語調檢查為負面，則重新生成
    if ctx.session.state.get("tone_check_result") == "negative":
        async for event in self.story_generator.run_async(ctx):
            yield event
```

> typescript

```typescript
async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined> {
    // 1. 執行故事生成器
    for await (const event of this.storyGenerator.runAsync(ctx)) {
        yield event;
    }

    // 2. 執行修訂迴圈
    for await (const event of this.loopAgent.runAsync(ctx)) {
        yield event;
    }

    // 3. 執行後處理器（語法與語調）
    for await (const event of this.sequentialAgent.runAsync(ctx)) {
        yield event;
    }

    // 4. 根據狀態進行條件分支
    if (ctx.session.state['tone_check_result'] === 'negative') {
        for await (const event of this.storyGenerator.runAsync(ctx)) {
            yield event;
        }
    }
}
```

> go

```go
func (a *StoryFlowAgent) Run(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
    return func(yield func(*session.Event, error) bool) {
        // 1. 執行故事生成
        for ev, err := range a.storyGenerator.Run(ctx) {
            if !yield(ev, err) { return }
        }

        // 2. 執行修訂迴圈
        for ev, err := range a.revisionLoopAgent.Run(ctx) {
            if !yield(ev, err) { return }
        }

        // 3. 執行後處理
        for ev, err := range a.postProcessorAgent.Run(ctx) {
            if !yield(ev, err) { return }
        }

        // 4. 條件式重新執行
        tone, _ := ctx.Session().State().Get("tone_check_result")
        if tone == "negative" {
            for ev, err := range a.storyGenerator.Run(ctx) {
                if !yield(ev, err) { return }
            }
        }
    }
}
```

> java

```java
@Override
protected Flowable<Event> runAsyncImpl(InvocationContext ctx) {
    // 1. 串聯基本的執行流程
    Flowable<Event> initialFlow = Flowable.concatArray(
        storyGenerator.runAsync(ctx),
        loopAgent.runAsync(ctx),
        sequentialAgent.runAsync(ctx)
    );

    // 2. 使用 defer 實作條件式邏輯
    return initialFlow.concatWith(Flowable.defer(() -> {
        if ("negative".equals(ctx.session().state().get("tone_check_result"))) {
            return storyGenerator.runAsync(ctx);
        }
        return Flowable.empty();
    }));
}
```

</details>

**邏輯說明：**

1. 初始的 `story_generator` 運行。其輸出預期在 `ctx.session.state["current_story"]` 中。
2. `loop_agent` 運行，它在內部按順序呼叫 `critic` 和 `reviser` 共 `max_iterations` 次。它們從狀態中讀取/寫入 `current_story` 和 `criticism`。
3. `sequential_agent` 運行，呼叫 `grammar_check` 然後是 `tone_check`，讀取 `current_story` 並將 `grammar_suggestions` 和 `tone_check_result` 寫入狀態。
4. **自定義部分：** `if` 語句檢查狀態中的 `tone_check_result`。如果是 "negative"，則*再次*呼叫 `story_generator`，覆寫狀態中的 `current_story`。否則，流程結束。

---

### 第 3 部分：定義 LLM 子代理

這些是標準的 `LlmAgent` 定義，負責特定的任務。它們的 `output key` 參數對於將結果放入 `session.state` 至關重要，以便其他代理或自定義編排器可以存取它們。

> [!TIP] 指令中的直接狀態注入
    請注意 `story_generator` 的指令。`{var}` 語法是一個佔位符。在指令發送到 LLM 之前，ADK 框架會自動將 (例如：`{topic}`) 替換為 `session.state['topic']` 的值。這是向代理提供上下文的推薦方式，即在指令中使用模板。有關更多詳細資訊，請參閱 [狀態文件](../sessions/state.md#accessing-session-state-in-agent-instructions)。

<details>
<summary>範例說明</summary>

> Python

```python
GEMINI_2_FLASH = "gemini-2.0-flash" # 定義模型常量

# 故事生成代理
story_gen = LlmAgent(
    name="StoryGenerator",
    model=GEMINI_2_FLASH,
    instruction="根據主題 {topic} 寫一個短篇故事。",
    output_key="current_story"
)

# 批評代理
critic = LlmAgent(
    name="Critic",
    model=GEMINI_2_FLASH,
    instruction="批評以下故事並提供改進建議：{current_story}",
    output_key="criticism"
)
```

> typescript

```typescript
// 故事生成代理
const storyGen = new LlmAgent({
  name: 'StoryGenerator',
  model: 'gemini-2.0-flash',
  instruction: '根據主題 {topic} 寫一個短篇故事。',
  outputKey: 'current_story'
});

// 語調檢查代理
const toneCheck = new LlmAgent({
  name: 'ToneCheck',
  model: 'gemini-2.0-flash',
  instruction: '評估此故事的語調：{current_story}。如果為負面請回傳 "negative"。',
  outputKey: 'tone_check_result'
});
```

> go

```go
// 故事生成代理配置
storyGen, _ := llmagent.New(llmagent.Config{
    Name:        "StoryGenerator",
    Model:       geminiModel,
    Instruction: "根據主題 {topic} 寫一個短篇故事。",
    OutputKey:   "current_story",
})

// 語法檢查代理配置
grammarCheck, _ := llmagent.New(llmagent.Config{
    Name:        "GrammarCheck",
    Model:       geminiModel,
    Instruction: "檢查此故事的語法：{current_story}。",
    OutputKey:   "grammar_suggestions",
})
```

> java

```java
// 故事生成代理
LlmAgent storyGen = LlmAgent.builder()
    .name("StoryGenerator")
    .model(model)
    .instruction("根據主題 {topic} 寫一個短篇故事。")
    .outputKey("current_story")
    .build();

// 修改代理
LlmAgent reviser = LlmAgent.builder()
    .name("Reviser")
    .model(model)
    .instruction("根據批評建議 {criticism} 修改故事：{current_story}")
    .outputKey("current_story")
    .build();
```

</details>

---

### 第 4 部分：實例化並運行自定義代理

最後，您實例化您的 `StoryFlowAgent` 並像往常一樣使用 `Runner`。

<details>
<summary>範例說明</summary>

> Python

```python
# 1. 建立自定義代理實例
flow_agent = StoryFlowAgent(
    story_generator=story_gen,
    critic=critic,
    reviser=reviser,
    grammar_check=grammar_check,
    tone_check=tone_check
)

# 2. 使用 Runner 執行
runner = Runner(agent=flow_agent)
async for event in runner.run(input="開始寫故事", state={"topic": "冒險"}):
    print(event)
```

> typescript

```typescript
// 1. 實例化自定義代理
const flowAgent = new StoryFlowAgent(storyGen, critic, reviser, grammarCheck, toneCheck);

// 2. 啟動運行器
const runner = new Runner({ agent: flowAgent });
const events = runner.run({
  input: '請開始',
  state: { topic: '科幻' }
});

for await (const event of events) {
  console.log(event);
}
```

> go

```go
// 1. 初始化自定義代理
flowAgent := NewStoryFlowAgent(storyGen, critic, reviser, grammarCheck, toneCheck)

// 2. 建立運行器並執行
r, _ := runner.New(runner.Config{
    Agent: flowAgent,
})

for ev, err := range r.Run(ctx, "開始", runner.WithState(map[string]any{"topic": "歷史"})) {
    fmt.Printf("Event: %v, Error: %v\n", ev, err)
}
```

> java

```java
// 1. 建立自定義代理
StoryFlowAgentExample flowAgent = new StoryFlowAgentExample(storyGen, critic, reviser, grammarCheck, toneCheck);

// 2. 使用 Runner 啟動
Runner runner = Runner.builder().agent(flowAgent).build();
runner.run("開始", Map.of("topic", "奇幻"))
    .doOnNext(event -> System.out.println("收到事件: " + event))
    .blockingSubscribe();
```

</details>

*(注意：完整的可執行程式碼，包括匯入和執行邏輯，可以在下面連結中找到。)*

---

### 完整範例程式碼

> [!TIP] 完整範例程式碼
> 以下提供各語言的 `StoryFlowAgent` 完整實作，方便參考與實作：
>
> **Python**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/python/snippets/agents/custom-agent/storyflow_agent.py)
>
> **TypeScript**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/typescript/snippets/agents/custom-agent/storyflow_agent.ts)
>
> **Go**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/go/snippets/agents/custom-agent/storyflow_agent.go)
>
> **Java**
> → [查看範例程式碼](https://github.com/google/adk-docs/blob/main/examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java)

---
### [程式碼] 重點說明 (以 Python 為例)

#### 1. 繼承 `BaseAgent` 與 Pydantic 整合
自定義代理必須繼承自 `google.adk.agents.BaseAgent`。由於 ADK 框架底層使用 Pydantic 進行資料驗證，因此實作時需注意：
*   **欄位宣告**：將子代理（如 `story_generator`）定義為類別屬性並提供類型標註，以便 Pydantic 進行驗證。
*   **模型配置**：設定 `model_config = {"arbitrary_types_allowed": True}`，允許在 Pydantic 模型中使用非基本類型的代理實例。

#### 2. 初始化與子代理註冊（Lifecycle Management）
在 `__init__` 方法中，除了設定實例屬性外，最重要的步驟是呼叫 `super().__init__`：
*   **`sub_agents` 列表**：必須將所有直接管理的子代理（包括內嵌的 `LoopAgent` 或 `SequentialAgent`）傳遞給 `sub_agents` 參數。
*   **框架功能支持**：這項註冊動作對於框架的生命週期管理、內省（Introspection）以及事件追蹤至關重要。

#### 3. 核心邏輯實現：`_run_async_impl`
這是自定義代理的「大腦」，決定了任務的編排流向：
*   **非同步產生器**：必須實作為 `async def` 並返回 `AsyncGenerator[Event, None]`。
*   **事件傳遞（Event Yielding）**：使用 `async for event in agent.run_async(ctx): yield event` 來執行子代理，並將產生的事件透明地向上傳遞給運行器（Runner）。
*   **流程組合**：可以在此方法中自由組合多個子代理，實現比 `SequentialAgent` 或 `LoopAgent` 更複雜的混合邏輯。

#### 4. 狀態驅動的條件決策（Conditional Logic）
自定義代理最大的優勢在於能根據執行過程中的狀態做出動態決策：
*   **Session State 存取**：透過 `ctx.session.state` 讀取子代理的執行結果（例如 `tone_check_result`）。
*   **動態分支**：範例中展示了 `if tone_check_result == "negative":` 的邏輯。當語調不符預期時，編排器可決定重新觸發 `story_generator`，實現具備自我修正能力的工作流。
*   **防錯機制**：可在執行過程中檢查狀態完整性（如檢查 `current_story` 是否存在），若資料缺失則提前中斷流程。