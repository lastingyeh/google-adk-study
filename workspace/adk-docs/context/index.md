# 上下文 (Context)

🔔 `更新日期：2026 年 1 月 10 日`

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

在 Agent Development Kit (ADK) 中，「上下文」(context) 指的是在特定操作期間，提供給您的代理 (agent) 及其工具的關鍵資訊包。您可以將其視為有效處理當前任務或對話輪次所需背景知識與資源。

代理通常不僅需要最新的使用者訊息才能表現良好。上下文 (Context)至關重要，因為它實現了：

1. **維持狀態 (Maintaining State)：** 記住跨多個對話步驟的詳細資訊（例如：使用者偏好、先前的計算結果、購物車中的物品）。這主要透過 **對話狀態 (session state)** 進行管理。
2. **傳遞資料 (Passing Data)：** 將在一個步驟中（如 LLM 調用或工具執行）發現或產生的資訊，與後續步驟共享。對話狀態在這裡也是關鍵。
3. **存取服務 (Accessing Services)：** 與框架功能互動，例如：
    * **構件儲存 (Artifact Storage)：** 儲存或載入與對話關聯的文件或資料區塊（如 PDF、圖片、設定檔）。
    * **記憶 (Memory)：** 從過去的互動或與使用者連接的外部知識來源中搜尋相關資訊。
    * **驗證 (Authentication)：** 請求並檢索工具安全存取外部 API 所需的憑證。
4. **身分與追蹤 (Identity and Tracking)：** 瞭解當前正在執行的代理 (`agent.name`)，並唯一識別當前的請求-響應週期 (`invocation_id`)，以便於記錄和偵錯。
5. **工具特定操作 (Tool-Specific Actions)：** 在工具內啟用專門操作，例如請求驗證或搜尋記憶，這些操作需要存取當前互動的詳細資訊。


將單個完整的使用者請求到最終響應週期（一次 **調用 (invocation)**）的所有資訊彙整在一起的核心部分是 `InvocationContext`。然而，您通常不會直接建立或管理此物件。ADK 框架會在調用開始時（例如：透過 `runner.run_async`）建立它，並隱式地將相關上下文資訊傳遞給您的代理程式碼、回呼 (callbacks) 和工具。

<details>
<summary>範例說明</summary>

> Python

```python
# 概念虛擬程式碼：框架如何提供上下文（內部邏輯）

# runner = Runner(agent=my_root_agent, session_service=..., artifact_service=...)
# user_message = types.Content(...)
# session = session_service.get_session(...) # 或建立新的

# --- runner.run_async(...) 內部 ---
# 1. 框架為此次特定執行建立主要上下文
# invocation_context = InvocationContext(
#     invocation_id="unique-id-for-this-run",
#     session=session,
#     user_content=user_message,
#     agent=my_root_agent, # 起始代理
#     session_service=session_service,
#     artifact_service=artifact_service,
#     memory_service=memory_service,
#     # ... 其他必要的欄位 ...
# )
#
# 2. 框架調用代理的 run 方法，隱式傳遞上下文
#    （代理的方法簽名將接收它，例如 runAsyncImpl(InvocationContext invocationContext)）
# await my_root_agent.run_async(invocation_context)
#   --- 內部邏輯結束 ---
#
# 作為開發者，您可以使用方法參數中提供的上下文物件。
```

> TypeScript

```typescript
/* 概念虛擬程式碼：框架如何提供上下文（內部邏輯） */

const runner = new InMemoryRunner({ agent: myRootAgent });
const session = await runner.sessionService.createSession({ ... });
const userMessage = createUserContent(...);

// --- runner.runAsync(...) 內部 ---
// 1. 框架為此次特定執行建立主要上下文
const invocationContext = new InvocationContext({
  invocationId: "unique-id-for-this-run",
  session: session,
  userContent: userMessage,
  agent: myRootAgent, // 起始代理
  sessionService: runner.sessionService,
  pluginManager: runner.pluginManager,
  // ... 其他必要的欄位 ...
});
//
// 2. 框架調用代理的 run 方法，隱式傳遞上下文
await myRootAgent.runAsync(invocationContext);
//   --- 內部邏輯結束 ---

// 作為開發者，您可以使用方法參數中提供的上下文物件。
```

> Go

```go
/* 概念虛擬程式碼：框架如何提供上下文（內部邏輯） */
/* Conceptual Pseudocode: How the framework provides context (Internal Logic) */
sessionService := session.InMemoryService()

r, err := runner.New(runner.Config{
    AppName:        appName,
    Agent:          myAgent,
    SessionService: sessionService,
})
if err != nil {
    log.Fatalf("Failed to create runner: %v", err)
}

s, err := sessionService.Create(ctx, &session.CreateRequest{
    AppName: appName,
    UserID:  userID,
})
if err != nil {
    log.Fatalf("FATAL: Failed to create session: %v", err)
}

scanner := bufio.NewScanner(os.Stdin)
for {
    fmt.Print("\nYou > ")
    if !scanner.Scan() {
        break
    }
    userInput := scanner.Text()
    if strings.EqualFold(userInput, "quit") {
        break
    }
    userMsg := genai.NewContentFromText(userInput, genai.RoleUser)
    events := r.Run(ctx, s.Session.UserID(), s.Session.ID(), userMsg, agent.RunConfig{
        StreamingMode: agent.StreamingModeNone,
    })
    fmt.Print("\nAgent > ")
    for event, err := range events {
        if err != nil {
            log.Printf("ERROR during agent execution: %v", err)
            break
        }
        fmt.Print(event.Content.Parts[0].Text)
    }
}
```

> Java

```java
/* 概念虛擬程式碼：框架如何提供上下文（內部邏輯） */
InMemoryRunner runner = new InMemoryRunner(agent);
Session session = runner
    .sessionService()
    .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
    .blockingGet();

try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
  while (true) {
    System.out.print("\nYou > ");
  }
  String userInput = scanner.nextLine();
  if ("quit".equalsIgnoreCase(userInput)) {
    break;
  }
  Content userMsg = Content.fromParts(Part.fromText(userInput));
  Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg);
  System.out.print("\nAgent > ");
  events.blockingForEach(event -> System.out.print(event.stringifyContent()));
}
```

</details>

## 不同類型的上下文

### 類型整理

| 類型                | 主要使用場景（由框架提供給誰）                                                                               | 狀態（state）寫入                                 | 構件（Artifacts）                           | 記憶（Memory）搜尋                          | 驗證（Auth）                                 | 重點能力 / 典型用途                                                                                                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------- | ------------------------------------------- | ------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `InvocationContext` | 代理核心實作方法：`_run_async_impl`、`_run_live_impl`（作為 `ctx` 參數）                                     | 直接透過 `ctx.session.state` 存取（完整會話層級） | 可透過已設定服務引用操作（偏框架/底層使用） | 可透過已設定服務引用操作（偏框架/底層使用） | 可透過已設定服務引用操作（偏框架/底層使用）  | 最「全面」的上下文容器：可存取 `session`（含 `state`/`events`）、`agent`、`invocation_id`、`user_content`、各種 service 引用；也可用於控制調用（例如 `ctx.end_invocation = True`）。 |
| `ReadonlyContext`   | 僅需要讀取基本資訊的情境（例如 `InstructionProvider`）                                                       | ✗（唯讀視圖）                                     | ✗                                           | ✗                                           | ✗                                            | 安全的唯讀視角：提供 `invocation_id`、`agent_name` 與唯讀 `state` 視圖，避免在不該改狀態的地方造成副作用。                                                                           |
| `CallbackContext`   | 生命週期/模型回呼：`before_*`、`after_*` callbacks（作為 `callback_context`）                                | ✓（可讀可寫且會被追蹤）                           | ✓ `load_artifact` / `save_artifact`         | ✗                                           | ✗                                            | 專為「回呼」設計：允許在回呼內檢查/修改狀態、讀寫構件、存取 `user_content`，並讓狀態變更能與事件正確關聯。                                                                           |
| `ToolContext`       | `FunctionTool` 內的工具函數 + 工具回呼：`before_tool_callback`、`after_tool_callback`（作為 `tool_context`） | ✓（繼承 `CallbackContext`）                       | ✓（含列出：`list_artifacts()`）             | ✓ `search_memory(query)`                    | ✓ `request_credential` / `get_auth_response` | 專為「工具執行」設計：在 `CallbackContext` 基礎上加入驗證流程、記憶搜尋、構件列表；並提供 `function_call_id` 與 `actions` 以便把驗證/狀態等動作正確連回本次工具呼叫。                |


雖然 `InvocationContext` 作為全面的內部容器，但 ADK 提供了針對特定情況量身定制的專門上下文物件。這確保了您擁有處理當前任務所需的正確工具和權限，而無需在各處處理內部上下文的完整複雜性。以下是您將遇到的不同「風味」：

1.  **`InvocationContext`**
    *   **使用場景：** 在代理的核心實作方法（`_run_async_impl`、`_run_live_impl`）中直接作為 `ctx` 參數接收。
    *   **目的：** 提供對當前調用 *整個* 狀態的存取。這是最全面的上下文物件。
    *   **關鍵內容：** 直接存取 `session`（包括 `state` 和 `events`）、當前 `agent` 實例、`invocation_id`、初始 `user_content`、對已設定服務（`artifact_service`、`memory_service`、`session_service`）的引用，以及與即時/串流模式相關的欄位。
    *   **案例：** 主要用於代理的核心邏輯需要直接存取整體對話或服務時，儘管狀態和構件互動通常會委託給使用其自身上下文的回呼/工具。也用於控制調用本身（例如：設置 `ctx.end_invocation = True`）。

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：接收 InvocationContext 的代理實作
    from google.adk.agents import BaseAgent
    from google.adk.agents.invocation_context import InvocationContext
    from google.adk.events import Event
    from typing import AsyncGenerator

    class MyAgent(BaseAgent):
        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            # 直接存取範例
            agent_name = ctx.agent.name
            session_id = ctx.session.id
            print(f"代理 {agent_name} 正在對話 {session_id} 中執行，調用 ID 為 {ctx.invocation_id}")
            # ... 使用 ctx 的代理邏輯 ...
            yield # ... 事件 ...
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：接收 InvocationContext 的代理實作
    import { BaseAgent, InvocationContext, Event } from '@google/adk';

    class MyAgent extends BaseAgent {
      async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined> {
        // 直接存取範例
        const agentName = ctx.agent.name;
        const sessionId = ctx.session.id;
        console.log(`代理 ${agentName} 正在對話 ${sessionId} 中執行，調用 ID 為 ${ctx.invocationId}`);
        // ... 使用 ctx 的代理邏輯 ...
        yield; // ... 事件 ...
      }
    }
    ```

    > Go

    ```go
    import (
    "google.golang.org/adk/agent"
    "google.golang.org/adk/session"
    )

    // Pseudocode: Agent implementation receiving InvocationContext
    type MyAgent struct {
    }

    func (a *MyAgent) Run(ctx agent.InvocationContext) iter.Seq2[*session.Event, error] {
        return func(yield func(*session.Event, error) bool) {
            // Direct access example
            agentName := ctx.Agent().Name()
            sessionID := ctx.Session().ID()
            fmt.Printf("Agent %s running in session %s for invocation %s\n", agentName, sessionID, ctx.InvocationID())
            // ... agent logic using ctx ...
            yield(&session.Event{Author: agentName}, nil)
        }
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：接收 InvocationContext 的代理實作
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.InvocationContext;

    LlmAgent root_agent =
        LlmAgent.builder()
            .model("gemini-***")
            .name("sample_agent")
            .description("回答使用者的問題。")
            .instruction(
                """
                在此提供代理的指令。
                """
            )
            .tools(sampleTool)
            .outputKey("YOUR_KEY")
            .build();

    ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
    initialState.put("YOUR_KEY", "");

    InMemoryRunner runner = new InMemoryRunner(agent);
    Session session =
            runner
                .sessionService()
                .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
                .blockingGet();

    try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
        while (true) {
            System.out.print("\nYou > ");
            String userInput = scanner.nextLine();

            if ("quit".equalsIgnoreCase(userInput)) {
            break;
            }

            Content userMsg = Content.fromParts(Part.fromText(userInput));
            Flowable<Event> events =
                    runner.runAsync(session.userId(), session.id(), userMsg);

            System.out.print("\nAgent > ");
            events.blockingForEach(event ->
                    System.out.print(event.stringifyContent()));
        }

    protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
        // 直接存取範例
        String agentName = invocationContext.agent.name
        String sessionId = invocationContext.session.id
        String invocationId = invocationContext.invocationId
        System.out.println("代理 " + agent_name + " 正在對話 " + session_id + " 中執行，調用 ID 為 " + invocationId)
        // ... 使用 ctx 的代理邏輯 ...
    }
    ```

    </details>

2.  **`ReadonlyContext`**
    *   **使用場景：** 提供於僅需要對基本資訊進行讀取存取且不允許變更的情境（例如：`InstructionProvider` 函數）。它也是其他上下文的基底類別。
    *   **目的：** 提供基本上下文詳細資訊的安全、唯讀視圖。
    *   **關鍵內容：** `invocation_id`、`agent_name` 以及當前 `state` 的唯讀 *視圖*。

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：接收 ReadonlyContext 的指令提供者
    from google.adk.agents.readonly_context import ReadonlyContext

    def my_instruction_provider(context: ReadonlyContext) -> str:
        # 唯讀存取範例
        user_tier = context.state().get("user_tier", "standard") # 可以讀取狀態
        # context.state['new_key'] = 'value' # 這通常會導致錯誤或無效
        return f"為 {user_tier} 使用者處理請求。"
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：接收 ReadonlyContext 的指令提供者
    import { ReadonlyContext } from '@google/adk';

    function myInstructionProvider(context: ReadonlyContext): string {
      // 唯讀存取範例
      // 狀態物件是唯讀的
      const userTier = context.state.get('user_tier') ?? 'standard';
      // context.state.set('new_key', 'value'); // 這將失敗或拋出錯誤
      return `為 ${userTier} 使用者處理請求。`;
    }
    ```

    > Go

    ```go
    import "google.golang.org/adk/agent"

    // Pseudocode: Instruction provider receiving ReadonlyContext
    func myInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
        // Read-only access example
        userTier, err := ctx.ReadonlyState().Get("user_tier")
        if err != nil {
            userTier = "standard" // Default value
        }
        // ctx.ReadonlyState() has no Set method since State() is read-only.
        return fmt.Sprintf("Process the request for a %v user.", userTier), nil
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：接收 ReadonlyContext 的指令提供者
    import com.google.adk.agents.ReadonlyContext;

    public String myInstructionProvider(ReadonlyContext context){
        // 唯讀存取範例
        String userTier = context.state().get("user_tier", "standard");
        context.state().put('new_key', 'value'); // 這通常會導致錯誤
        return "為 " + userTier + " 使用者處理請求。"
    }
    ```

    </details>

3.  **`CallbackContext`**
    *   **使用場景：** 作為 `callback_context` 傳遞給代理生命週期回呼（`before_agent_callback`、`after_agent_callback`）和模型互動回呼（`before_model_callback`、`after_model_callback`）。
    *   **目的：** 促進在 *回呼內部* 檢查和修改狀態、與構件互動以及存取調用詳細資訊。
    *   **關鍵功能（繼承自 `ReadonlyContext`）：**
        *   **可變 `state` 屬性：** 允許讀取 *和寫入* 對話狀態。此處所做的更改（`callback_context.state['key'] = value`）會被追蹤，並與框架在回呼後產生的事件相關聯。
        *   **構件方法：** 用於與配置的 `artifact_service` 互動的 `load_artifact(filename)` 和 `save_artifact(filename, part)` 方法。
        *   直接存取 `user_content`。

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：接收 CallbackContext 的回呼
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models import LlmRequest
    from google.genai import types
    from typing import Optional

    def my_before_model_cb(callback_context: CallbackContext, request: LlmRequest) -> Optional[types.Content]:
        # 讀取/寫入狀態範例
        call_count = callback_context.state.get("model_calls", 0)
        callback_context.state["model_calls"] = call_count + 1 # 修改狀態

        # 選擇性地載入構件
        # config_part = callback_context.load_artifact("model_config.json")
        print(f"正在為調用 {callback_context.invocation_id} 準備第 #{call_count + 1} 次模型調用")
        return None # 允許模型調用繼續
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：接收 CallbackContext 的回呼
    import { CallbackContext, LlmRequest } from '@google/adk';
    import { Content } from '@google/genai';

    function myBeforeModelCb(callbackContext: CallbackContext, request: LlmRequest): Content | undefined {
      // 讀取/寫入狀態範例
      const callCount = (callbackContext.state.get('model_calls') as number) || 0;
      callbackContext.state.set('model_calls', callCount + 1); // 修改狀態

      // 選擇性地載入構件
      // const configPart = await callbackContext.loadArtifact('model_config.json');
      console.log(`正在為調用 {callbackContext.invocationId} 準備第 #{callCount + 1} 次模型調用`);
      return undefined; // 允許模型調用繼續
    }
    ```

    > Go

    ```go
    import (
    "google.golang.org/adk/agent"
    "google.golang.org/adk/model"
    )

    // Pseudocode: Callback receiving CallbackContext
    func myBeforeModelCb(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
        // Read/Write state example
        callCount, err := ctx.State().Get("model_calls")
        if err != nil {
            callCount = 0 // Default value
        }
        newCount := callCount.(int) + 1
        if err := ctx.State().Set("model_calls", newCount); err != nil {
            return nil, err
        }

        // Optionally load an artifact
        // configPart, err := ctx.Artifacts().Load("model_config.json")
        fmt.Printf("Preparing model call #%d for invocation %s\n", newCount, ctx.InvocationID())
        return nil, nil // Allow model call to proceed
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：接收 CallbackContext 的回呼
    import com.google.adk.agents.CallbackContext;
    import com.google.adk.models.LlmRequest;
    import com.google.genai.types.Content;
    import java.util.Optional;

    public Maybe<LlmResponse> myBeforeModelCb(CallbackContext callbackContext, LlmRequest request){
        // 讀取/寫入狀態範例
        callCount = callbackContext.state().get("model_calls", 0)
        callbackContext.state().put("model_calls") = callCount + 1 # 修改狀態

        // 選擇性地載入構件
        // Maybe<Part> configPart = callbackContext.loadArtifact("model_config.json");
        System.out.println("正在準備第 " + callCount + 1 + " 次模型調用");
        return Maybe.empty(); // 允許模型調用繼續
    }
    ```

    </details>

4.  **`ToolContext`**
    *   **使用場景：** 作為 `tool_context` 傳遞給支援 `FunctionTool` 的函數以及工具執行回呼（`before_tool_callback`、`after_tool_callback`）。
    *   **目的：** 提供 `CallbackContext` 的所有功能，外加工具執行必不可少的專門方法，如處理驗證、搜尋記憶和列出構件。
    *   **關鍵功能（繼承自 `CallbackContext`）：**
        *   **驗證方法 (Authentication Methods)：** 觸發驗證流程的 `request_credential(auth_config)`，以及檢索使用者/系統提供的憑證的 `get_auth_response(auth_config)`。
        *   **構件列表 (Artifact Listing)：** 用於發現對話中可用構件的 `list_artifacts()`。
        *   **記憶搜尋 (Memory Search)：** 用於查詢配置的 `memory_service` 的 `search_memory(query)`。
        *   **`function_call_id` 屬性：** 識別觸發此工具執行的 LLM 特定函數調用，這對於將驗證請求或響應正確連結回去至關重要。
        *   **`actions` 屬性：** 直接存取此步驟的 `EventActions` 物件，允許工具發出狀態更改、驗證請求等信號。

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：接收 ToolContext 的工具函數
    from google.adk.tools import ToolContext
    from typing import Dict, Any

    # 假設此函數由 FunctionTool 包裝
    def search_external_api(query: str, tool_context: ToolContext) -> Dict[str, Any]:
        api_key = tool_context.state.get("api_key")
        if not api_key:
            # 定義所需的驗證配置
            # auth_config = AuthConfig(...)
            # tool_context.request_credential(auth_config) # 請求憑證
            # 使用 'actions' 屬性來發出驗證請求已發出的信號
            # tool_context.actions.requested_auth_configs[tool_context.function_call_id] = auth_config
            return {"status": "需要驗證"}

        # 使用 API 金鑰...
        print(f"正在為查詢 '{query}' 執行工具。調用 ID：{tool_context.invocation_id}")

        # 選擇性地搜尋記憶或列出構件
        # relevant_docs = tool_context.search_memory(f"與 {query} 相關的資訊")
        # available_files = tool_context.list_artifacts()

        return {"result": f"已獲取 {query} 的資料。"}
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：接收 ToolContext 的工具函數
    import { ToolContext } from '@google/adk';

    // __假設此函數由 FunctionTool 包裝__
    function searchExternalApi(query: string, toolContext: ToolContext): { [key: string]: string } {
      const apiKey = toolContext.state.get('api_key') as string;
      if (!apiKey) {
         // 定義所需的驗證配置
         // const authConfig = new AuthConfig(...);
         // toolContext.requestCredential(authConfig); // 請求憑證
         // 'actions' 屬性現在由 requestCredential 自動更新
         return { status: '需要驗證' };
      }

      // 使用 API 金鑰...
      console.log(`正在為查詢 '${query}' 執行工具。調用 ID：{toolContext.invocationId}`);

      // 選擇性地搜尋記憶或列出構件
      // 注意：在 TS 中存取記憶/構件等服務通常是異步的，
      // 因此如果您重複使用它們，則需要將此函數標記為 'async'。
      // toolContext.searchMemory(`與 ${query} 相關的資訊`).then(...)
      // toolContext.listArtifacts().then(...)

      return { result: `已獲取 ${query} 的資料。` };
    }
    ```

    > Go

    ```go
    import "google.golang.org/adk/tool"

    // Pseudocode: Tool function receiving ToolContext
    type searchExternalAPIArgs struct {
        Query string `json:"query" jsonschema:"The query to search for."`
    }

    func searchExternalAPI(tc tool.Context, input searchExternalAPIArgs) (string, error) {
        apiKey, err := tc.State().Get("api_key")
        if err != nil || apiKey == "" {
            // In a real scenario, you would define and request credentials here.
            // This is a conceptual placeholder.
            return "", fmt.Errorf("auth required")
        }

        // Use the API key...
        fmt.Printf("Tool executing for query '%s' using API key. Invocation: %s\n", input.Query, tc.InvocationID())

        // Optionally search memory or list artifacts
        // relevantDocs, _ := tc.SearchMemory(tc, "info related to %s", input.Query))
        // availableFiles, _ := tc.Artifacts().List()

        return fmt.Sprintf("Data for %s fetched.", input.Query), nil
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：接收 ToolContext 的工具函數
    import com.google.adk.tools.ToolContext;
    import java.util.HashMap;
    import java.util.Map;

    // 假設此函數由 FunctionTool 包裝
    public Map<String, Object> searchExternalApi(String query, ToolContext toolContext){
        String apiKey = toolContext.state.get("api_key");
        if(apiKey.isEmpty()){
            // 定義所需的驗證配置
            // authConfig = AuthConfig(...);
            // toolContext.requestCredential(authConfig); # 請求憑證
            // 使用 'actions' 屬性來發出驗證請求已發出的信號
            ...
            return Map.of("status", "需要驗證");

        // 使用 API 金鑰...
        System.out.println("正在使用 API 金鑰為查詢 " + query + " 執行工具。");

        // 選擇性地列出構件
        // Single<List<String>> availableFiles = toolContext.listArtifacts();

        return Map.of("result", "已獲取 " + query + " 的資料");
    }
    ```

    </details>

瞭解這些不同的上下文物件以及何時使用它們，是有效管理狀態、存取服務以及控制 ADK 應用程式流程的關鍵。下一節將詳細介紹您可以使用這些上下文執行的常見任務。


## 使用上下文的常見任務

現在您已經瞭解了不同的上下文物件，讓我們專注於在構建代理和工具時如何將它們用於常見任務。

### 任務整理

| 常見任務                      | 說明（何時用）                                                                                                                                         | 相關欄位 / 方法（範例）                                                         |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| 讀取狀態（Session State）     | 在 `ToolContext` / `CallbackContext` 透過 `state` 讀取先前步驟寫入的資料；可用 `app:` / `user:` / `temp:` 前綴區分應用層、使用者層與單次調用暫存資料。 | `state.get(...)`、鍵前綴：`app:*` / `user:*` / `temp:*`                         |
| 取得當前識別碼                | 做日誌、追蹤與關聯特定工具呼叫時使用。                                                                                                                 | `agent_name` / `invocation_id` / `function_call_id`（工具情境）                 |
| 存取初始使用者輸入            | 需要「回看本輪是由哪句話啟動」時使用。                                                                                                                 | `user_content` / `userContent`；或在代理核心用 `InvocationContext`              |
| 工具之間傳遞資料              | 多工具流程中共享中間結果（例如先取得使用者 ID，再用它查詢訂單）。                                                                                      | `state['temp:...']` / `state.set('temp:...')`                                   |
| 更新使用者偏好                | 需要跨對話/長期保存偏好時（搭配持久性 `SessionService` 更適合）。                                                                                      | `state['user:...']` / `state.set('user:...')`                                   |
| 使用 Artifact 處理文件/大資料 | 對話中需要處理文件或大型資料區塊時：先存「引用（路徑/URI）」或大內容，後續再取回並在 ADK 上下文外完成讀檔與處理（如摘要）。                            | `save_artifact`/`saveArtifact`、`load_artifact`/`loadArtifact`                  |
| 列出可用 Artifacts            | 需要發現目前有哪些構件可用、或除錯構件流程時使用。                                                                                                     | `list_artifacts`/`listArtifacts`                                                |
| 處理工具驗證（Auth）          | 工具需要 API 金鑰/OAuth 等憑證時：無憑證就觸發驗證流程；後續取回並寫回狀態供重用。                                                                     | `request_credential`/`requestCredential`、`get_auth_response`/`getAuthResponse` |
| 利用記憶（Memory）            | 需要從過去或外部來源找相關資訊時；並處理「無結果」或「服務未配置」情境。                                                                               | `search_memory`/`searchMemory`                                                  |
| 進階控制整體流程              | 代理核心邏輯需要直接控制流程時（例如依條件提前停止整個請求-響應週期）。                                                                                | `InvocationContext`、`end_invocation`/`endInvocation`                           |


### 存取資訊

您將經常需要讀取儲存在上下文中的資訊。

*   **讀取對話狀態 (Reading Session State)：** 存取在先前步驟中儲存的資料或使用者/應用程式層級的設定。在 `state` 屬性上使用類似字典的存取方式。

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：在工具函數中
    from google.adk.tools import ToolContext

    def my_tool(tool_context: ToolContext, **kwargs):
        user_pref = tool_context.state.get("user_display_preference", "default_mode")
        api_endpoint = tool_context.state.get("app:api_endpoint") # 讀取應用程式層級狀態

        if user_pref == "dark_mode":
            # ... 應用深色模式邏輯 ...
            pass
        print(f"正在使用 API 端點：{api_endpoint}")
        # ... 工具其餘邏輯 ...

    # 虛擬程式碼：在回呼函數中
    from google.adk.agents.callback_context import CallbackContext

    def my_callback(callback_context: CallbackContext, **kwargs):
        last_tool_result = callback_context.state.get("temp:last_api_result") # 讀取臨時狀態
        if last_tool_result:
            print(f"從上次工具中找到臨時結果：{last_tool_result}")
        # ... 回呼邏輯 ...
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：在工具函數中
    import { ToolContext } from '@google/adk';

    async function myTool(toolContext: ToolContext) {
      const userPref = toolContext.state.get('user_display_preference', 'default_mode');
      const apiEndpoint = toolContext.state.get('app:api_endpoint'); // 讀取應用程式層級狀態

      if (userPref === 'dark_mode') {
        // ... 應用深色模式邏輯 ...
      }
      console.log(`正在使用 API 端點：${apiEndpoint}`);
      // ... 工具其餘邏輯 ...
    }

    // 虛擬程式碼：在回呼函數中
    import { CallbackContext } from '@google/adk';

    function myCallback(callbackContext: CallbackContext) {
      const lastToolResult = callbackContext.state.get('temp:last_api_result'); // 讀取臨時狀態
      if (lastToolResult) {
        console.log(`從上次工具中找到臨時結果：${lastToolResult}`);
      }
      // ... 回呼邏輯 ...
    }
    ```

    > Go

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/session"
        "google.golang.org/adk/tool"
        "google.golang.org/genai"
    )

    // Pseudocode: In a Tool function
    type toolArgs struct {
        // Define tool-specific arguments here
    }

    type toolResults struct {
        // Define tool-specific results here
    }

    // Example tool function demonstrating state access
    func myTool(tc tool.Context, input toolArgs) (toolResults, error) {
        userPref, err := tc.State().Get("user_display_preference")
        if err != nil {
            userPref = "default_mode"
        }
        apiEndpoint, _ := tc.State().Get("app:api_endpoint") // Read app-level state

        if userPref == "dark_mode" {
            // ... apply dark mode logic ...
        }
        fmt.Printf("Using API endpoint: %v\n", apiEndpoint)
        // ... rest of tool logic ...
        return toolResults{}, nil
    }


    // Pseudocode: In a Callback function
    func myCallback(ctx agent.CallbackContext) (*genai.Content, error) {
        lastToolResult, err := ctx.State().Get("temp:last_api_result") // Read temporary state
        if err == nil {
            fmt.Printf("Found temporary result from last tool: %v\n", lastToolResult)
        } else {
            fmt.Println("No temporary result found.")
        }
        // ... callback logic ...
        return nil, nil
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：在工具函數中
    import com.google.adk.tools.ToolContext;

    public void myTool(ToolContext toolContext){
       String userPref = toolContext.state().get("user_display_preference");
       String apiEndpoint = toolContext.state().get("app:api_endpoint"); // 讀取應用程式層級狀態
       if(userPref.equals("dark_mode")){
            // ... 應用深色模式邏輯 ...
            pass
        }
       System.out.println("正在使用 API 端點：" + api_endpoint);
       // ... 工具其餘邏輯 ...
    }


    // 虛擬程式碼：在回呼函數中
    import com.google.adk.agents.CallbackContext;

        public void myCallback(CallbackContext callbackContext){
            String lastToolResult = (String) callbackContext.state().get("temp:last_api_result"); // 讀取臨時狀態
        }
        if(!(lastToolResult.isEmpty())){
            System.out.println("從上次工具中找到臨時結果：" + lastToolResult);
        }
        // ... 回呼邏輯 ...
    ```

    </details>

*   **獲取當前識別碼 (Getting Current Identifiers)：** 對於記錄或根據當前操作實作自定義邏輯很有用。

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：在任何上下文中（以 ToolContext 為例）
    from google.adk.tools import ToolContext

    def log_tool_usage(tool_context: ToolContext, **kwargs):
        agent_name = tool_context.agent_name
        inv_id = tool_context.invocation_id
        func_call_id = getattr(tool_context, 'function_call_id', 'N/A') # ToolContext 特有

        print(f"日誌：調用={inv_id}, 代理={agent_name}, 函數調用 ID={func_call_id} - 工具已執行。")
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：在任何上下文中（以 ToolContext 為例）
    import { ToolContext } from '@google/adk';

    function logToolUsage(toolContext: ToolContext) {
      const agentName = toolContext.agentName;
      const invId = toolContext.invocationId;
      const functionCallId = toolContext.functionCallId ?? 'N/A'; // ToolContext 特有

      console.log(`日誌：調用=${invId}, 代理=${agentName}, 函數調用 ID=${functionCallId} - 工具已執行。`);
    }
    ```

    > Go

    ```go
    import "google.golang.org/adk/tool"

    // Pseudocode: In any context (ToolContext shown)
    type logToolUsageArgs struct{}
    type logToolUsageResult struct {
        Status string `json:"status"`
    }

    func logToolUsage(tc tool.Context, args logToolUsageArgs) (logToolUsageResult, error) {
        agentName := tc.AgentName()
        invID := tc.InvocationID()
        funcCallID := tc.FunctionCallID()

        fmt.Printf("Log: Invocation=%s, Agent=%s, FunctionCallID=%s - Tool Executed.\n", invID, agentName, funcCallID)
        return logToolUsageResult{Status: "Logged successfully"}, nil
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：在任何上下文中（以 ToolContext 為例）
     import com.google.adk.tools.ToolContext;

     public void logToolUsage(ToolContext toolContext){
                String agentName = toolContext.agentName;
                String invId = toolContext.invocationId;
                String functionCallId = toolContext.functionCallId().get(); // ToolContext 特有
                System.out.println("日誌：調用= " + invId + " 代理= " + agentName);
            }
    ```

    </details>

*   **存取初始使用者輸入 (Accessing the Initial User Input)：** 引用啟動當前調用的訊息。

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：在回呼中
    from google.adk.agents.callback_context import CallbackContext

    def check_initial_intent(callback_context: CallbackContext, **kwargs):
        initial_text = "N/A"
        if callback_context.user_content and callback_context.user_content.parts:
            initial_text = callback_context.user_content.parts[0].text or "非文字輸入"

        print(f"此調用始於使用者輸入：'{initial_text}'")

    # 虛擬程式碼：在代理的 _run_async_impl 中
    # async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
    #     if ctx.user_content and ctx.user_content.parts:
    #         initial_text = ctx.user_content.parts[0].text
    #         print(f"代理邏輯記住初始查詢：{initial_text}")
    #     ...
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：在回呼中
    import { CallbackContext } from '@google/adk';

    function checkInitialIntent(callbackContext: CallbackContext) {
      let initialText = 'N/A';
      const userContent = callbackContext.userContent;
      if (userContent?.parts?.length) {
        initialText = userContent.parts[0].text ?? '非文字輸入';
      }

      console.log(`此調用始於使用者輸入：'${initialText}'`);
    }
    ```

    > Go

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/genai"
    )

    // Pseudocode: In a Callback
    func logInitialUserInput(ctx agent.CallbackContext) (*genai.Content, error) {
        userContent := ctx.UserContent()
        if userContent != nil && len(userContent.Parts) > 0 {
            if text := userContent.Parts[0].Text; text != "" {
                fmt.Printf("User's initial input for this turn: '%s'\n", text)
            }
        }
        return nil, nil // No modification
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：在回呼中
    import com.google.adk.agents.CallbackContext;

    public void checkInitialIntent(CallbackContext callbackContext){
        String initialText = "N/A";
        if((!(callbackContext.userContent().isEmpty())) && (!(callbackContext.userContent().parts.isEmpty()))){
            initialText = cbx.userContent().get().parts().get().get(0).text().get();
            ...
            System.out.println("此調用始於使用者輸入：" + initialText)
        }
    }
    ```

    </details>

### 管理狀態

狀態對於記憶和資料流至關重要。當您使用 `CallbackContext` 或 `ToolContext` 修改狀態時，框架會自動追蹤並持久化這些更改。

*   **工作原理：** 寫入 `callback_context.state['my_key'] = my_value` 或 `tool_context.state['my_key'] = my_value` 會將此更改添加到與當前步驟事件相關聯的 `EventActions.state_delta` 中。然後 `SessionService` 在持久化事件時應用這些 delta。

*  **在工具之間傳遞資料**

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：工具 1 - 獲取使用者 ID
    from google.adk.tools import ToolContext
    import uuid

    def get_user_profile(tool_context: ToolContext) -> dict:
        user_id = str(uuid.uuid4()) # 模擬獲取 ID
        # 將 ID 儲存到狀態中以供下一個工具使用
        tool_context.state["temp:current_user_id"] = user_id
        return {"profile_status": "ID 已產生"}

    # 虛擬程式碼：工具 2 - 使用狀態中的使用者 ID
    def get_user_orders(tool_context: ToolContext) -> dict:
        user_id = tool_context.state.get("temp:current_user_id")
        if not user_id:
            return {"error": "狀態中找不到使用者 ID"}

        print(f"正在為使用者 ID：{user_id} 獲取訂單")
        # ... 使用 user_id 獲取訂單的邏輯 ...
        return {"orders": ["order123", "order456"]}
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：工具 1 - 獲取使用者 ID
    import { ToolContext } from '@google/adk';
    import { v4 as uuidv4 } from 'uuid';

    function getUserProfile(toolContext: ToolContext): Record<string, string> {
      const userId = uuidv4(); // 模擬獲取 ID
      // 將 ID 儲存到狀態中以供下一個工具使用
      toolContext.state.set('temp:current_user_id', userId);
      return { profile_status: 'ID 已產生' };
    }

    // 虛擬程式碼：工具 2 - 使用狀態中的使用者 ID
    function getUserOrders(toolContext: ToolContext): Record<string, string | string[]> {
      const userId = toolContext.state.get('temp:current_user_id');
      if (!userId) {
        return { error: '狀態中找不到使用者 ID' };
      }

      console.log(`正在為使用者 ID：${userId} 獲取訂單`);
      // ... 使用 user_id 獲取訂單的邏輯 ...
      return { orders: ['order123', 'order456'] };
    }
    ```

    > Go

    ```go
    import "google.golang.org/adk/tool"

    // Pseudocode: Tool 1 - Fetches user ID
    type GetUserProfileArgs struct {
    }

    func getUserProfile(tc tool.Context, input GetUserProfileArgs) (string, error) {
        // A random user ID for demonstration purposes
        userID := "random_user_456"

        // Save the ID to state for the next tool
        if err := tc.State().Set("temp:current_user_id", userID); err != nil {
            return "", fmt.Errorf("failed to set user ID in state: %w", err)
        }
        return "ID generated", nil
    }


    // Pseudocode: Tool 2 - Uses user ID from state
    type GetUserOrdersArgs struct {
    }

    type getUserOrdersResult struct {
        Orders []string `json:"orders"`
    }

    func getUserOrders(tc tool.Context, input GetUserOrdersArgs) (*getUserOrdersResult, error) {
        userID, err := tc.State().Get("temp:current_user_id")
        if err != nil {
            return &getUserOrdersResult{}, fmt.Errorf("user ID not found in state")
        }

        fmt.Printf("Fetching orders for user ID: %v\n", userID)
        // ... logic to fetch orders using user_id ...
        return &getUserOrdersResult{Orders: []string{"order123", "order456"}}, nil
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：工具 1 - 獲取使用者 ID
    import com.google.adk.tools.ToolContext;
    import java.util.UUID;

    public Map<String, String> getUserProfile(ToolContext toolContext){
        String userId = UUID.randomUUID().toString();
        // 將 ID 儲存到狀態中以供下一個工具使用
        toolContext.state().put("temp:current_user_id", user_id);
        return Map.of("profile_status", "ID 已產生");
    }

    // 虛擬程式碼：工具 2 - 使用狀態中的使用者 ID
    public Map<String, String> getUserOrders(ToolContext toolContext){
        String userId = toolContext.state().get("temp:current_user_id");
        if(userId.isEmpty()){
            return Map.of("error", "狀態中找不到使用者 ID");
        }
        System.out.println("正在為使用者 ID：" + userId + " 獲取訂單");
         // ... 使用 user_id 獲取訂單的邏輯 ...
        return Map.of("orders", "order123");
    }
    ```

    </details>

*   **更新使用者偏好 (Updating User Preferences)：**

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：工具或回呼識別偏好
    from google.adk.tools import ToolContext # 或 CallbackContext

    def set_user_preference(tool_context: ToolContext, preference: str, value: str) -> dict:
        # 使用 'user:' 前綴表示使用者層級狀態（如果使用持久性 SessionService）
        state_key = f"user:{preference}"
        tool_context.state[state_key] = value
        print(f"將使用者偏好 '{preference}' 設置為 '{value}'")
        return {"status": "偏好已更新"}
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：工具或回呼識別偏好
    import { ToolContext } from '@google/adk'; // 或 CallbackContext

    function setUserPreference(toolContext: ToolContext, preference: string, value: string): Record<string, string> {
      // 使用 'user:' 前綴表示使用者層級狀態（如果使用持久性 SessionService）
      const stateKey = `user:${preference}`;
      toolContext.state.set(stateKey, value);
      console.log(`將使用者偏好 '${preference}' 設置為 '${value}'`);
      return { status: '偏好已更新' };
    }
    ```

    > Go

    ```go
    import "google.golang.org/adk/tool"

    // Pseudocode: Tool or Callback identifies a preference
    type setUserPreferenceArgs struct {
        Preference string `json:"preference" jsonschema:"The name of the preference to set."`
        Value      string `json:"value" jsonschema:"The value to set for the preference."`
    }

    type setUserPreferenceResult struct {
        Status string `json:"status"`
    }

    func setUserPreference(tc tool.Context, args setUserPreferenceArgs) (setUserPreferenceResult, error) {
        // Use 'user:' prefix for user-level state (if using a persistent SessionService)
        stateKey := fmt.Sprintf("user:%s", args.Preference)
        if err := tc.State().Set(stateKey, args.Value); err != nil {
            return setUserPreferenceResult{}, fmt.Errorf("failed to set preference in state: %w", err)
        }
        fmt.Printf("Set user preference '%s' to '%s'\n", args.Preference, args.Value)
        return setUserPreferenceResult{Status: "Preference updated"}, nil
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：工具或回呼識別偏好
    import com.google.adk.tools.ToolContext; // 或 CallbackContext

    public Map<String, String> setUserPreference(ToolContext toolContext, String preference, String value){
        // 使用 'user:' 前綴表示使用者層級狀態（如果使用持久性 SessionService）
        String stateKey = "user:" + preference;
        toolContext.state().put(stateKey, value);
        System.out.println("將使用者偏好 '" + preference + "' 設置為 '" + value + "'");
        return Map.of("status", "偏好已更新");
    }
    ```

    </details>

*   **狀態前綴 (State Prefixes)：** 雖然基本狀態是對話特定的，但前綴如 `app:` 和 `user:` 可以與持久性 `SessionService` 實作（如 `DatabaseSessionService` 或 `VertexAiSessionService`）結合使用，以指示更廣泛的範圍（跨對話的應用程式範圍或使用者範圍）。`temp:` 可以表示僅在當前調用中相關的資料。

### 使用構件 (Working with Artifacts)

使用構件來處理與對話關聯的文件或大型資料區塊。常見使用案例：處理上傳的文件。

*   **文件摘要工具範例流程：**

    1.  **攝取引用 (Ingest Reference)（例如：在設置工具或回呼中）：** 將文件的 *路徑或 URI*（而非全部內容）儲存為構件。

        <details>
        <summary>範例說明</summary>

        > Python

        ```python
        # 虛擬程式碼：在回呼或初始工具中
        from google.adk.agents.callback_context import CallbackContext # 或 ToolContext
        from google.genai import types

        def save_document_reference(context: CallbackContext, file_path: str) -> None:
            # 假設 file_path 類似於 "gs://my-bucket/docs/report.pdf" 或 "/local/path/to/report.pdf"
            try:
                # 建立包含路徑/URI 文字的 Part
                artifact_part = types.Part(text=file_path)
                version = context.save_artifact("document_to_summarize.txt", artifact_part)
                print(f"已將文件引用 '{file_path}' 儲存為構件版本 {version}")
                # 如果其他工具需要，將檔名儲存在狀態中
                context.state["temp:doc_artifact_name"] = "document_to_summarize.txt"
            except ValueError as e:
                print(f"儲存構件時出錯：{e}") # 例如：未配置構件服務
            except Exception as e:
                print(f"儲存構件引用時發生非預期錯誤：{e}")

        # 使用範例：
        # save_document_reference(callback_context, "gs://my-bucket/docs/report.pdf")
        ```

        > TypeScript

        ```typescript
        // 虛擬程式碼：在回呼或初始工具中
        import { CallbackContext } from '@google/adk'; // 或 ToolContext
        import type { Part } from '@google/genai';

        async function saveDocumentReference(context: CallbackContext, filePath: string) {
          // 假設 filePath 類似於 "gs://my-bucket/docs/report.pdf" 或 "/local/path/to/report.pdf"
          try {
            // 建立包含路徑/URI 文字的 Part
            const artifactPart: Part = { text: filePath };
            const version = await context.saveArtifact('document_to_summarize.txt', artifactPart);
            console.log(`已將文件引用 '${filePath}' 儲存為構件版本 ${version}`);
            // 如果其他工具需要，將檔名儲存在狀態中
            context.state.set('temp:doc_artifact_name', 'document_to_summarize.txt');
          } catch (e) {
            console.error(`儲存構件引用時發生非預期錯誤：{e}`);
          }
        }

        // 使用範例：
        // saveDocumentReference(callbackContext, "gs://my-bucket/docs/report.pdf");
        ```

        > Go

        ```go
        import (
                "google.golang.org/adk/tool"
                "google.golang.org/genai"
            )

            // Adapt the saveDocumentReference callback into a tool for this example.
            type saveDocRefArgs struct {
                FilePath string `json:"file_path" jsonschema:"The path to the file to save."`
            }

            type saveDocRefResult struct {
                Status string `json:"status"`
            }

            func saveDocRef(tc tool.Context, args saveDocRefArgs) (saveDocRefResult, error) {
                artifactPart := genai.NewPartFromText(args.FilePath)
                _, err := tc.Artifacts().Save(tc, "document_to_summarize.txt", artifactPart)
                if err != nil {
                    return saveDocRefResult{}, err
                }
                fmt.Printf("Saved document reference '%s' as artifact\n", args.FilePath)
                if err := tc.State().Set("temp:doc_artifact_name", "document_to_summarize.txt"); err != nil {
                    return saveDocRefResult{}, fmt.Errorf("failed to set artifact name in state")
                }
                return saveDocRefResult{"Reference saved"}, nil
            }
        ```

        > Java

        ```java
        // 虛擬程式碼：在回呼或初始工具中
        import com.google.adk.agents.CallbackContext;
        import com.google.genai.types.Content;
        import com.google.genai.types.Part;


        pubic void saveDocumentReference(CallbackContext context, String filePath){
            // 假設 file_path 類似於 "gs://my-bucket/docs/report.pdf" 或 "/local/path/to/report.pdf"
            try{
                // 建立包含路徑/URI 文字的 Part
                Part artifactPart = types.Part(filePath)
                Optional<Integer> version = context.saveArtifact("document_to_summarize.txt", artifactPart)
                System.out.println("已將文件引用 " + filePath + " 儲存為構件版本 " + version);
                // 如果其他工具需要，將檔名儲存在狀態中
                context.state().put("temp:doc_artifact_name", "document_to_summarize.txt");
            } catch(Exception e){
                System.out.println("儲存構件引用時發生非預期錯誤：" + e);
            }
        }

        // 使用範例：
        // saveDocumentReference(context, "gs://my-bucket/docs/report.pdf")
        ```

        </details>

    2.  **摘要工具 (Summarizer Tool)：** 載入構件 (Artifact) 以獲取路徑/URI，使用適當的函式庫讀取實際文件內容，進行摘要並返回結果。

        <details>
        <summary>範例說明</summary>

        > Python

        ```python
        # 虛擬程式碼：在摘要工具函數中
        from google.adk.tools import ToolContext
        from google.genai import types
        # 假設可使用 google.cloud.storage 或內建的 open 等函式庫
        # 假設存在 'summarize_text' 函數
        # from my_summarizer_lib import summarize_text

        def summarize_document_tool(tool_context: ToolContext) -> dict:
            artifact_name = tool_context.state.get("temp:doc_artifact_name")
            if not artifact_name:
                return {"error": "狀態中找不到文件構件名稱。"}

            try:
                # 1. 載入包含路徑/URI 的構件部分
                artifact_part = tool_context.load_artifact(artifact_name)
                if not artifact_part or not artifact_part.text:
                    return {"error": f"無法載入構件或構件沒有文字路徑：{artifact_name}"}

                file_path = artifact_part.text
                print(f"已載入文件引用：{file_path}")

                # 2. 讀取實際文件內容（在 ADK 上下文之外）
                document_content = ""
                if file_path.startswith("gs://"):
                    # 範例：使用 GCS 用戶端函式庫下載/讀取
                    # from google.cloud import storage
                    # client = storage.Client()
                    # blob = storage.Blob.from_string(file_path, client=client)
                    # document_content = blob.download_as_text() # 或根據格式使用 bytes
                    pass # 替換為實際的 GCS 讀取邏輯
                elif file_path.startswith("/"):
                     # 範例：使用本地文件系統
                     with open(file_path, 'r', encoding='utf-8') as f:
                         document_content = f.read()
                else:
                    return {"error": f"不支援的文件路徑配置：{file_path}"}

                # 3. 摘要內容
                if not document_content:
                     return {"error": "讀取文件內容失敗。"}

                # summary = summarize_text(document_content) # 調用您的摘要邏輯
                summary = f"來自 {file_path} 的內容摘要" # 佔位符

                return {"summary": summary}

            except ValueError as e:
                 return {"error": f"構件服務錯誤：{e}"}
            except FileNotFoundError:
                 return {"error": f"找不到本地文件：{file_path}"}
            # except Exception as e: # 捕捉 GCS 等特定的異常
            #      return {"error": f"讀取文件 {file_path} 時出錯：{e}"}
        ```

        > TypeScript

        ```typescript
        // 虛擬程式碼：在摘要工具函數中
        import { ToolContext } from '@google/adk';

        async function summarizeDocumentTool(toolContext: ToolContext): Promise<Record<string, string>> {
          const artifactName = toolContext.state.get('temp:doc_artifact_name') as string;
          if (!artifactName) {
            return { error: '狀態中找不到文件構件名稱。' };
          }

          try {
            // 1. 載入包含路徑/URI 的構件部分
            const artifactPart = await toolContext.loadArtifact(artifactName);
            if (!artifactPart?.text) {
              return { error: `無法載入構件或構件沒有文字路徑：${artifactName}` };
            }

            const filePath = artifactPart.text;
            console.log(`已載入文件引用：${filePath}`);

            // 2. 讀取實際文件內容（在 ADK 上下文之外）
            let documentContent = '';
            if (filePath.startsWith('gs://')) {
              // 範例：使用 GCS 用戶端函式庫下載/讀取
              // const storage = new Storage();
              // const bucket = storage.bucket('my-bucket');
              // const file = bucket.file(filePath.replace('gs://my-bucket/', ''));
              // const [contents] = await file.download();
              // documentContent = contents.toString();
            } else if (filePath.startsWith('/')) {
              // 範例：使用本地文件系統
              // import { readFile } from 'fs/promises';
              // documentContent = await readFile(filePath, 'utf8');
            } else {
              return { error: `不支援的文件路徑配置：${filePath}` };
            }

            // 3. 摘要內容
            if (!documentContent) {
               return { error: '讀取文件內容失敗。' };
            }

            // const summary = summarizeText(documentContent); # 調用您的摘要邏輯
            const summary = `來自 ${filePath} 的內容摘要`; // 佔位符

            return { summary };

          } catch (e) {
             return { error: `處理構件時出錯：${e}` };
          }
        }
        ```

        > Go

        ```go
        import "google.golang.org/adk/tool"

        // Pseudocode: In the Summarizer tool function
        type summarizeDocumentArgs struct{}

        type summarizeDocumentResult struct {
            Summary string `json:"summary"`
        }

        func summarizeDocumentTool(tc tool.Context, input summarizeDocumentArgs) (summarizeDocumentResult, error) {
            artifactName, err := tc.State().Get("temp:doc_artifact_name")
            if err != nil {
                return summarizeDocumentResult{}, fmt.Errorf("No document artifact name found in state")
            }

            // 1. Load the artifact part containing the path/URI
            artifactPart, err := tc.Artifacts().Load(tc, artifactName.(string))
            if err != nil {
                return summarizeDocumentResult{}, err
            }

            if artifactPart.Part.Text == "" {
                return summarizeDocumentResult{}, fmt.Errorf("Could not load artifact or artifact has no text path.")
            }
            filePath := artifactPart.Part.Text
            fmt.Printf("Loaded document reference: %s\n", filePath)

            // 2. Read the actual document content (outside ADK context)
            // In a real implementation, you would use a GCS client or local file reader.
            documentContent := "This is the fake content of the document at " + filePath
            _ = documentContent // Avoid unused variable error.

            // 3. Summarize the content
            summary := "Summary of content from " + filePath // Placeholder

            return summarizeDocumentResult{Summary: summary}, nil
        }
        ```

        > Java

        ```java
        // 虛擬程式碼：在摘要工具函數中
        import com.google.adk.tools.ToolContext;
        import com.google.genai.types.Content;
        import com.google.genai.types.Part;

        public Map<String, String> summarizeDocumentTool(ToolContext toolContext){
            String artifactName = toolContext.state().get("temp:doc_artifact_name");
            if(artifactName.isEmpty()){
                return Map.of("error", "狀態中找不到文件構件名稱。");
            }
            try{
                // 1. 載入包含路徑/URI 的構件部分
                Maybe<Part> artifactPart = toolContext.loadArtifact(artifactName);
                if((artifactPart == null) || (artifactPart.text().isEmpty())){
                    return Map.of("error", "無法載入構件或構件沒有文字路徑：" + artifactName);
                }
                filePath = artifactPart.text();
                System.out.println("已載入文件引用：" + filePath);

                // 2. 讀取實際文件內容（在 ADK 上下文之外）
                String documentContent = "";
                if(filePath.startsWith("gs://")){
                    // 範例：使用 GCS 用戶端函式庫下載/讀取到 documentContent
                    pass; // 替換為實際的 GCS 讀取邏輯
                } else if(){
                    // 範例：使用本地文件系統下載/讀取到 documentContent
                } else{
                    return Map.of("error", "不支援的文件路徑配置：" + filePath);
                }

                // 3. 摘要內容
                if(documentContent.isEmpty()){
                    return Map.of("error", "讀取文件內容失敗。");
                }

                // summary = summarizeText(documentContent) # 調用您的摘要邏輯
                summary = "來自 " + filePath + " 的內容摘要"; // 佔位符

                return Map.of("summary", summary);
            } catch(IllegalArgumentException e){
                return Map.of("error", "構件服務錯誤 " + filePath + e);
            } catch(FileNotFoundException e){
                return Map.of("error", "找不到本地文件 " + filePath + e);
            } catch(Exception e){
                return Map.of("error", "讀取文件時出錯 " + filePath + e);
            }
        }
        ```

        </details>

*   **列出構件 (Listing Artifacts)：** 發現有哪些可用的文件。

    <details>
    <summary>範例說明</summary>

    > Python

    ```python
    # 虛擬程式碼：在工具函數中
    from google.adk.tools import ToolContext

    def check_available_docs(tool_context: ToolContext) -> dict:
        try:
            artifact_keys = tool_context.list_artifacts()
            print(f"可用構件：{artifact_keys}")
            return {"available_docs": artifact_keys}
        except ValueError as e:
            return {"error": f"構件 (Artifact)服務錯誤：{e}"}
    ```

    > TypeScript

    ```typescript
    // 虛擬程式碼：在工具函數中
    import { ToolContext } from '@google/adk';

    async function checkAvailableDocs(toolContext: ToolContext): Promise<Record<string, string[] | string>> {
      try {
        const artifactKeys = await toolContext.listArtifacts();
        console.log(`可用構件：${artifactKeys}`);
        return { available_docs: artifactKeys };
      } catch (e) {
        return { error: `構件服務錯誤：${e}` };
      }
    }
    ```

    > Go

    ```go
    import "google.golang.org/adk/tool"

    // Pseudocode: In a tool function
    type checkAvailableDocsArgs struct{}

    type checkAvailableDocsResult struct {
        AvailableDocs []string `json:"available_docs"`
    }

    func checkAvailableDocs(tc tool.Context, args checkAvailableDocsArgs) (checkAvailableDocsResult, error) {
        artifactKeys, err := tc.Artifacts().List(tc)
        if err != nil {
            return checkAvailableDocsResult{}, err
        }
        fmt.Printf("Available artifacts: %v\n", artifactKeys)
        return checkAvailableDocsResult{AvailableDocs: artifactKeys.FileNames}, nil
    }
    ```

    > Java

    ```java
    // 虛擬程式碼：在工具函數中
    import com.google.adk.tools.ToolContext;

    public Map<String, String> checkAvailableDocs(ToolContext toolContext){
        try{
            Single<List<String>> artifactKeys = toolContext.listArtifacts();
            System.out.println("可用構件" + artifactKeys.tostring());
            return Map.of("availableDocs", "artifactKeys");
        } catch(IllegalArgumentException e){
            return Map.of("error", "構件服務錯誤：" + e);
        }
    }
    ```

    </details>

### 處理工具驗證 (Handling Tool Authentication)

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0`]

安全地管理工具所需的 API 金鑰或其他憑證。

<details>
<summary>範例說明</summary>

> Python

```python
# 虛擬程式碼：需要驗證的工具
from google.adk.tools import ToolContext
from google.adk.auth import AuthConfig # 假設已定義適當的 AuthConfig

# 定義所需的驗證配置（例如：OAuth、API 金鑰）
MY_API_AUTH_CONFIG = AuthConfig(...)
AUTH_STATE_KEY = "user:my_api_credential" # 用於儲存檢索到的憑證的鍵

def call_secure_api(tool_context: ToolContext, request_data: str) -> dict:
    # 1. 檢查狀態中是否已存在憑證
    credential = tool_context.state.get(AUTH_STATE_KEY)

    if not credential:
        # 2. 如果不存在，則請求它
        print("找不到憑證，正在請求...")
        try:
            tool_context.request_credential(MY_API_AUTH_CONFIG)
            # 框架處理事件的產生。工具執行在此輪次停止。
            return {"status": "需要驗證。請提供憑證。"}
        except ValueError as e:
            return {"error": f"驗證錯誤：{e}"} # 例如：缺少 function_call_id
        except Exception as e:
            return {"error": f"請求憑證失敗：{e}"}

    # 3. 如果憑證存在（可能是請求後的先前輪次）
    #    或者如果這是在外部完成驗證流程後的後續調用
    try:
        # 選擇性地重新驗證/檢索（如果需要），或直接使用
        # 如果外部流程剛剛完成，這可能會檢索憑證
        auth_credential_obj = tool_context.get_auth_response(MY_API_AUTH_CONFIG)
        api_key = auth_credential_obj.api_key # 或 access_token 等

        # 將其儲存回狀態中，以便在對話中的未來調用中使用
        tool_context.state[AUTH_STATE_KEY] = auth_credential_obj.model_dump() # 持久化檢索到的憑證

        print(f"正在使用檢索到的憑證調用 API，資料為：{request_data}")
        # ... 使用 api_key 進行實際的 API 調用 ...
        api_result = f"{request_data} 的 API 結果"

        return {"result": api_result}
    except Exception as e:
        # 處理檢索/使用憑證時的錯誤
        print(f"使用憑證時出錯：{e}")
        # 如果憑證無效，或許可以清除狀態鍵？
        # tool_context.state[AUTH_STATE_KEY] = None
        return {"error": "使用憑證失敗"}
```

> TypeScript

```typescript
// 虛擬程式碼：需要驗證的工具
import { ToolContext } from '@google/adk'; // 來自 ADK 或自定義的 AuthConfig

// 定義局部 AuthConfig 介面，因為它不被 ADK 公開導出
interface AuthConfig {
  credentialKey: string;
  authScheme: { type: string }; // 範例的最小表示
  // 如果與範例相關，請添加其他屬性
}

// 定義所需的驗證配置（例如：OAuth、API 金鑰）
const MY_API_AUTH_CONFIG: AuthConfig = {
  credentialKey: 'my-api-key', // 範例鍵
  authScheme: { type: 'api-key' }, // 範例方案類型
};
const AUTH_STATE_KEY = 'user:my_api_credential'; // 用於儲存檢索到的憑證的鍵

async function callSecureApi(toolContext: ToolContext, requestData: string): Promise<Record<string, string>> {
  // 1. 檢查狀態中是否已存在憑證
  const credential = toolContext.state.get(AUTH_STATE_KEY);

  if (!credential) {
    // 2. 如果不存在，則請求它
    console.log('找不到憑證，正在請求...');
    try {
      toolContext.requestCredential(MY_API_AUTH_CONFIG);
      // 框架處理事件的產生。工具執行在此輪次停止。
      return { status: '需要驗證。請提供憑證。' };
    } catch (e) {
      return { error: `驗證或憑證請求錯誤：${e}` };
    }
  }

  // 3. 如果憑證存在（可能是請求後的先前輪次）
  //    或者如果這是在外部完成驗證流程後的後續調用
  try {
    // 選擇性地重新驗證/檢索（如果需要），或直接使用
    // 如果外部流程剛剛完成，這可能會檢索憑證
    const authCredentialObj = toolContext.getAuthResponse(MY_API_AUTH_CONFIG);
    const apiKey = authCredentialObj?.apiKey; // 或 accessToken 等

    // 將其儲存回狀態中，以便在對話中的未來調用中使用
    // 注意：在嚴格的 TS 中，可能需要轉型或序列化 authCredentialObj
    toolContext.state.set(AUTH_STATE_KEY, JSON.stringify(authCredentialObj));

    console.log(`正在使用檢索到的憑證調用 API，資料為：${requestData}`);
    // ... 使用 apiKey 進行實際的 API 調用 ...
    const apiResult = `${requestData} 的 API 結果`;

    return { result: apiResult };
  } catch (e) {
    // 處理檢索/使用憑證時的錯誤
    console.error(`使用憑證時出錯：${e}`);
    // 如果憑證無效，或許可以清除狀態鍵？
    // toolContext.state.set(AUTH_STATE_KEY, null);
    return { error: '使用憑證失敗' };
  }
}
```

</details>

*請記住：`request_credential` 會暫停工具並發出需要驗證的信號。使用者/系統提供憑證，在隨後的調用中，`get_auth_response`（或再次檢查狀態）允許工具繼續執行。* `tool_context.function_call_id` 由框架隱式使用，以連結請求和響應。

### 利用記憶 (Leveraging Memory)

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0`]

存取來自過去或外部來源的相關資訊。

<details>
<summary>範例說明</summary>

> Python

```python
# 虛擬程式碼：使用記憶搜尋的工具
from google.adk.tools import ToolContext

def find_related_info(tool_context: ToolContext, topic: str) -> dict:
    try:
        search_results = tool_context.search_memory(f"關於 {topic} 的資訊")
        if search_results.results:
            print(f"為 '{topic}' 找到 {len(search_results.results)} 條記憶結果")
            # 處理 search_results.results (其為 SearchMemoryResponseEntry)
            top_result_text = search_results.results[0].text
            return {"memory_snippet": top_result_text}
        else:
            return {"message": "找不到相關記憶。"}
    except ValueError as e:
        return {"error": f"記憶服務錯誤：{e}"} # 例如：服務未配置
    except Exception as e:
        return {"error": f"搜尋記憶時發生非預期錯誤：{e}"}
```

> TypeScript

```typescript
// 虛擬程式碼：使用記憶搜尋的工具
import { ToolContext } from '@google/adk';

async function findRelatedInfo(toolContext: ToolContext, topic: string): Promise<Record<string, string>> {
  try {
    const searchResults = await toolContext.searchMemory(`關於 ${topic} 的資訊`);
    if (searchResults.results?.length) {
      console.log(`為 '${topic}' 找到 ${searchResults.results.length} 條記憶結果`);
      // 處理 searchResults.results
      const topResultText = searchResults.results[0].text;
      return { memory_snippet: topResultText };
    } else {
      return { message: '找不到相關記憶。' };
    }
  } catch (e) {
     return { error: `記憶服務錯誤：${e}` }; // 例如：服務未配置
  }
}
```

</details>

### 進階：直接使用 `InvocationContext`

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0`]

雖然大多數互動都是透過 `CallbackContext` 或 `ToolContext` 進行的，但有時代理的核心邏輯（`_run_async_impl`/`_run_live_impl`）需要直接存取。

<details>
<summary>範例說明</summary>

> Python

```python
# 虛擬程式碼：在代理的 _run_async_impl 內部
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator

class MyControllingAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 範例：檢查特定服務是否可用
        if not ctx.memory_service:
            print("此調用無法使用記憶服務。")
            # 潛在地改變代理行為

        # 範例：基於某些條件提前終止
        if ctx.session.state.get("critical_error_flag"):
            print("檢測到嚴重錯誤，正在結束調用。")
            ctx.end_invocation = True # 通知框架停止處理
            yield Event(author=self.name, invocation_id=ctx.invocation_id, content="因嚴重錯誤而停止。")
            return # 停止此代理的執行

        # ... 正常代理處理 ...
        yield # ... 事件 ...
```

> TypeScript

```typescript
// 虛擬程式碼：在代理的 runAsyncImpl 內部
import { BaseAgent, InvocationContext } from '@google/adk';
import type { Event } from '@google/adk';

class MyControllingAgent extends BaseAgent {
  async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined> {
    // 範例：檢查特定服務是否可用
    if (!ctx.memoryService) {
      console.log('此調用無法使用記憶服務。');
      // 潛在地改變代理行為
    }

    // 範例：基於某些條件提前終止
    // 透過 ctx.session.state 直接存取狀態，或者如果被包裝則透過 ctx.session.state 屬性存取
    if ((ctx.session.state as { 'critical_error_flag': boolean })['critical_error_flag']) {
      console.log('檢測到嚴重錯誤，正在結束調用。');
      ctx.endInvocation = true; // 通知框架停止處理
      yield {
        author: this.name,
        invocationId: ctx.invocationId,
        content: { parts: [{ text: '因嚴重錯誤而停止。' }] }
      } as Event;
      return; // 停止此代理的執行
    }

    // ... 正常代理處理 ...
    yield; // ... 事件 ...
  }
}
```

</details>

設置 `ctx.end_invocation = True` 是一種從代理及其回呼/工具中優雅停止整個請求-響應週期的方法（透過它們各自的上下文物件，這些物件也可以存取以修改底層 `InvocationContext` 的標記）。

## 關鍵要點與最佳實踐

*   **使用正確的上下文：** 始終使用提供的最特定上下文物件（工具/工具回呼中的 `ToolContext`、代理/模型回呼中的 `CallbackContext`、適用時的 `ReadonlyContext`）。僅在必要時於 `_run_async_impl` / `_run_live_impl` 中直接使用完整的 `InvocationContext` (`ctx`)。
*   **狀態用於資料流：** `context.state` 是在調用 *內部* 共享資料、記住偏好以及管理對話記憶的主要方式。使用持久儲存時，請深思熟慮地使用前綴（`app:`、`user:`、`temp:`）。
*   **構件 (Artifact)用於文件：** 使用 `context.save_artifact` 和 `context.load_artifact` 來管理文件引用（如路徑或 URI）或較大的資料區塊。儲存引用，按需載入內容。
*   **追蹤的更改：** 透過上下文方法對狀態或構件所做的修改會自動連結到當前步驟的 `EventActions`，並由 `SessionService` 處理。
*   **從簡單開始：** 先專注於 `state` 和基本構件用法。隨著需求變得更加複雜，再探索驗證、記憶和進階 `InvocationContext` 欄位（如用於即時串流的欄位）。

透過理解並有效使用這些上下文物件，您可以使用 ADK 構建更複雜、具備狀態且功能強大的代理。
