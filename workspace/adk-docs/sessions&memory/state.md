# 狀態（State）：工作階段的暫存草稿

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/sessions/state/

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

在每個 `Session`（我們的對話執行緒）中，**`state`** 屬性就像是代理（Agent）針對該次特定互動的專用暫存草稿。雖然 `session.events` 保存了完整的歷史記錄，但 `session.state` 是代理存儲和更新對話 *期間* 所需動態詳細資訊的地方。

## 什麼是 `session.state`？

從概念上講，`session.state` 是一個保存鍵值對（key-value pairs）的集合（字典或 Map）。它旨在存放代理需要回想或追蹤的資訊，以使當前對話更有效率：

* **個人化互動：** 記住稍早提到的使用者偏好（例如：`'user_preference_theme': 'dark'`）。
* **追蹤任務進度：** 掌握多輪流程中的步驟（例如：`'booking_step': 'confirm_payment'`）。
* **累積資訊：** 建立清單或摘要（例如：`'shopping_cart_items': ['book', 'pen']`）。
* **做出知情決策：** 存儲影響下一個回應的標記或數值（例如：`'user_is_authenticated': True`）。

### `State` 的關鍵特性

1. **結構：可序列化的鍵值對**

    * 資料以 `key: value` 形式存儲。
    * **鍵（Keys）：** 始終為字串（`str`）。請使用清晰的名稱（例如：`'departure_city'`、`'user:language_preference'`）。
    * **值（Values）：** 必須是**可序列化的**。這意味著它們可以輕鬆地被 `SessionService` 儲存和載入。請使用特定語言（Python/Go/Java/TypeScript）中的基本類型，如字串、數字、布林值，以及僅包含這些基本類型的簡單列表或字典。（詳情請參閱 API 文件）。
    * **⚠️ 避免複雜對象：** **請勿直接在狀態中存儲不可序列化的對象**（自定義類別實例、函式、連線等）。如果需要，請存儲簡單的識別碼，並在其他地方檢索複雜對象。

2. **可變性：它是會改變的**

    * 隨著對話的演進，`state` 的內容預計會發生變化。

3. **持久性：取決於 `SessionService`**

    * 狀態是否能在應用程式重啟後留存，取決於您選擇的服務：

      * `InMemorySessionService`：**非持久性。** 狀態在重啟時會遺失。
      * `DatabaseSessionService` / `VertexAiSessionService`：**持久性。** 狀態會被可靠地保存。

> [!NOTE]
基本操作的特定參數或方法名稱可能會因 SDK 語言而略有不同（例如：Python 中的 `session.state['current_intent'] = 'book_flight'`，Go 中的 `context.State().Set("current_intent", "book_flight")`，Java 中的 `session.state().put("current_intent", "book_flight")`，或 TypeScript 中的 `context.state.set("current_intent", "book_flight")`）。詳情請參閱各語言專屬的 API 文件。

### 使用前綴設計編排：範圍很重要 (Scope Matters)

狀態鍵上的前綴定義了它們的範圍和持久化行為，特別是在使用持久性服務時：

* **無前綴（工作階段狀態）：**

    * **範圍：** 僅限於當前工作階段（`id`）。
    * **持久性：** 僅當 `SessionService` 是持久性的（`Database`、`VertexAI`）時才會持久化。
    * **使用場景：** 追蹤當前任務內的進度（例如：`'current_booking_step'`）、此互動的臨時標記（例如：`'needs_clarification'`）。
    * **範例：** `session.state['current_intent'] = 'book_flight'`

* **`user:` 前綴（使用者狀態）：**

    * **範圍：** 繫結到 `user_id`，在該使用者的 *所有* 工作階段中共享（在同一個 `app_name` 內）。
    * **持久性：** 在 `Database` 或 `VertexAI` 中持久化。（由 `InMemory` 存儲但重啟後遺失）。
    * **使用場景：** 使用者偏好（例如：`'user:theme'`）、個人資料詳情（例如：`'user:name'`）。
    * **範例：** `session.state['user:preferred_language'] = 'fr'`

* **`app:` 前綴（應用程式狀態）：**

    * **範圍：** 繫結到 `app_name`，在該應用程式的 *所有* 使用者和工作階段中共享。
    * **持久性：** 在 `Database` 或 `VertexAI` 中持久化。（由 `InMemory` 存儲但重啟後遺失）。
    * **使用場景：** 全域設定（例如：`'app:api_endpoint'`）、共享模板。
    * **範例：** `session.state['app:global_discount_code'] = 'SAVE10'`

* **`temp:` 前綴（臨時調用狀態）：**

    * **範圍：** 僅限於當前的**調用（invocation）**（從代理接收使用者輸入到為該輸入生成最終輸出的完整過程）。
    * **持久性：** **非持久性。** 調用完成後會被捨棄，且不會轉移到下一次調用。
    * **使用場景：** 在單次調用中存儲工具呼叫之間的計算中間值、標記或資料。
    * **何時不應使用：** 對於必須跨不同調用持久化的資訊，如使用者偏好、對話歷史摘要或累積資料。
    * **範例：** `session.state['temp:raw_api_response'] = {...}`

> [!NOTE] 子代理與調用上下文
當父代理呼叫子代理（例如使用 `SequentialAgent` 或 `ParallelAgent`）時，它會將其 `InvocationContext` 傳遞給子代理。這意味著整個代理呼叫鏈共享相同的調用 ID，因此也共享相同的 `temp:` 狀態。

**代理如何看待它：** 您的代理程式碼透過單一的 `session.state` 集合（字典/Map）與 *合併後的* 狀態進行互動。`SessionService` 負責根據前綴從正確的底層存儲中獲取/合併狀態。

### 在代理指令中存取工作階段狀態

在使用 `LlmAgent` 實例時，您可以使用簡單的模板語法將工作階段狀態值直接注入代理的指令字串中。這使您能夠建立動態且具有上下文意識的指令，而無需完全依賴自然語言指令。

#### 使用 `{key}` 模板

要從工作階段狀態注入值，請將所需狀態變數的鍵括在大括號內：`{key}`。框架在將指令傳遞給 LLM 之前，會自動將此佔位符替換為來自 `session.state` 的對應值。

**範例：**

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent

# 初始化 LlmAgent 並在指令中使用 {topic} 佔位符
story_generator = LlmAgent(
    name="StoryGenerator",
    model="gemini-2.0-flash",
    instruction="""寫一個關於貓的短篇故事，重點主題是：{topic}。"""
)

# 假設 session.state['topic'] 被設置為 "friendship"（友誼），
# LLM 將收到以下指令：
# "寫一個關於貓的短篇故事，重點主題是：friendship。"
```

> TypeScript

```typescript
import { LlmAgent } from "@google/adk";

// 初始化 LlmAgent 並在指令中使用 {topic} 佔位符
const storyGenerator = new LlmAgent({
    name: "StoryGenerator",
    model: "gemini-2.5-flash",
    instruction: "寫一個關於貓的短篇故事，重點主題是：{topic}."
});

// 假設 session.state['topic'] 被設置為 "friendship"（友誼），
// LLM 將收到以下指令：
// "寫一個關於貓的短篇故事，重點主題是：friendship。"
```

> Go

```go
func main() {
    ctx := context.Background()
    sessionService := session.InMemoryService()

    // 1. 初始化一個狀態中包含 'topic' 的工作階段。
    _, err := sessionService.Create(ctx, &session.CreateRequest{
        AppName:   appName,
        UserID:    userID,
        SessionID: sessionID,
        State: map[string]any{
            "topic": "friendship",
        },
    })
    if err != nil {
        log.Fatalf("建立工作階段失敗: %v", err)
    }

    // 2. 建立一個指令中使用 {topic} 佔位符的代理。
    //    ADK 在呼叫 LLM 之前，會自動將工作階段狀態中 "topic" 的值注入指令中。
    model, err := gemini.NewModel(ctx, modelID, nil)
    if err != nil {
        log.Fatalf("建立 Gemini 模型失敗: %v", err)
    }
    storyGenerator, err := llmagent.New(llmagent.Config{
        Name:        "StoryGenerator",
        Model:       model,
        Instruction: "寫一個關於貓的短篇故事，重點主題是：{topic}。",
    })
    if err != nil {
        log.Fatalf("建立代理失敗: %v", err)
    }

    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          agent.Agent(storyGenerator),
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("建立執行器（runner）失敗: %v", err)
    }
}
```

</details>

#### 重要考量因素

* 鍵的存在性：確保您在指令字串中引用的鍵存在於 `session.state` 中。如果缺少該鍵，代理將拋出錯誤。要使用可能存在也可能不存在的鍵，您可以在鍵後加上問號（?）（例如 `{topic?}`）。
* 資料類型：與鍵關聯的值應為字串或可以輕鬆轉換為字串的類型。
* 逸出（Escaping）：如果您需要在指令中使用字面意義的大括號（例如 JSON 格式化），則需要對其進行逸出。

#### 使用 `InstructionProvider` 繞過狀態注入

在某些情況下，您可能希望在指令中字面使用 `{{` 和 `}}`，而不觸發狀態注入機制。例如，您可能正在為一個幫助處理使用相同語法的模板語言的代理撰寫指令。

為了實現這一點，您可以向 `instruction` 參數提供一個函式而不是字串。這個函式被稱為 `InstructionProvider`。當您使用 `InstructionProvider` 時，ADK 將不會嘗試注入狀態，您的指令字串將原封不動地傳遞給模型。

`InstructionProvider` 函式接收一個 `ReadonlyContext` 對象，如果您需要動態構建指令，可以使用它來存取工作階段狀態或其他上下文資訊。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

# 這是一個 InstructionProvider
def my_instruction_provider(context: ReadonlyContext) -> str:
    # 您可以選擇性地使用 context 來構建指令
    # 在此範例中，我們將返回一個帶有字面意義大括號的靜態字串。
    return "這是一個帶有 {{literal_braces}} 且不會被替換的指令。"

agent = LlmAgent(
    model="gemini-2.0-flash",
    name="template_helper_agent",
    instruction=my_instruction_provider
)
```

> TypeScript

```typescript
import { LlmAgent, ReadonlyContext } from "@google/adk";

// 這是一個 InstructionProvider
function myInstructionProvider(context: ReadonlyContext): string {
    // 您可以選擇性地使用 context 來構建指令
    // 在此範例中，我們將返回一個帶有字面意義大括號的靜態字串。
    return "這是一個帶有 {{literal_braces}} 且不會被替換的指令。";
}

const agent = new LlmAgent({
    model: "gemini-2.5-flash",
    name: "template_helper_agent",
    instruction: myInstructionProvider
});
```

> Go

```go
//  1. 此 InstructionProvider 返回一個靜態字串。
//     因為它是一個提供者函式，ADK 將不會嘗試注入狀態，
//     指令將原封不動地傳遞給模型，保留字面意義的大括號。
func staticInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
    return "這是一個帶有 {{literal_braces}} 且不會被替換的指令。", nil
}
```

</details>

如果您希望同時使用 `InstructionProvider` *並* 在指令中注入狀態，可以使用 `inject_session_state` 工具函式。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.utils import instructions_utils

async def my_dynamic_instruction_provider(context: ReadonlyContext) -> str:
    template = "這是一個 {adjective} 的指令，帶有 {{literal_braces}}。"
    # 這將注入 'adjective' 狀態變數，但保留字面意義的大括號。
    return await instructions_utils.inject_session_state(template, context)

agent = LlmAgent(
    model="gemini-2.0-flash",
    name="dynamic_template_helper_agent",
    instruction=my_dynamic_instruction_provider
)
```

> Go

```go
//  2. 此 InstructionProvider 演示了如何在手動注入狀態的同時保留字面意義的大括號。
//     它使用了 instructionutil 輔助工具。
func dynamicInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
    template := "這是一個 {adjective} 的指令，帶有 {{literal_braces}}。"
    // 這將注入 'adjective' 狀態變數，但保留字面意義的大括號。
    return instructionutil.InjectSessionState(ctx, template)
}
```

</details>

**直接注入的優點**

* 清晰度：明確指出指令的哪些部分是動態的且基於工作階段狀態。
* 可靠性：避免完全依賴 LLM 正確解讀存取狀態的自然語言指令。
* 可維護性：簡化指令字串，並降低更新狀態變數名稱時出現錯誤的風險。

**與其他狀態存取方法的關係**

此直接注入方法僅適用於 `LlmAgent` 指令。有關其他狀態存取方法的更多資訊，請參閱下一節。

### 狀態如何更新：推薦的方法

> [!NOTE] 修改狀態的正確方式
當您需要更改工作階段狀態時，正確且最安全的方法是**直接修改提供給函式的 `Context` 上的 `state` 對象**（例如：`callback_context.state['my_key'] = 'new_value'`）。這被認為是以正確方式進行的「直接狀態操作」，因為框架會自動追蹤這些更改。
這與直接修改從 `SessionService` 獲取的 `Session` 對象上的 `state` 有本質上的不同（例如：`my_session.state['my_key'] = 'new_value'`）。**您應該避免這樣做**，因為它繞過了 ADK 的事件追蹤，並可能導致資料遺失。本頁末尾的「警告」部分有關於此重要區別的更多詳細資訊。

狀態應**始終**作為使用 `session_service.append_event()` 向工作階段歷史記錄添加 `Event` 的一部分進行更新。這確保了更改被追蹤、持久化正常運作，且更新是執行緒安全的。

**1. 簡單的方法：`output_key`（用於代理文字回應）**

這是將代理的最終文字回應直接保存到狀態中的最簡單方法。在定義 `LlmAgent` 時，指定 `output_key`：

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part

# 定義帶有 output_key 的代理
greeting_agent = LlmAgent(
    name="Greeter",
    model="gemini-2.0-flash", # 使用有效的模型
    instruction="生成一段簡短且友好的問候語。",
    output_key="last_greeting" # 將回應保存到 state['last_greeting']
)

# --- 設定執行器（Runner）和工作階段 ---
app_name, user_id, session_id = "state_app", "user1", "session1"
session_service = InMemorySessionService()
runner = Runner(
    agent=greeting_agent,
    app_name=app_name,
    session_service=session_service
)
session = await session_service.create_session(app_name=app_name,
                                        user_id=user_id,
                                        session_id=session_id)
print(f"初始狀態: {session.state}")

# --- 執行代理 ---
# 執行器處理 append_event 的呼叫，
# 它會使用 output_key 自動建立 state_delta。
user_message = Content(parts=[Part(text="Hello")])
for event in runner.run(user_id=user_id,
                            session_id=session_id,
                            new_message=user_message):
    if event.is_final_response():
      print(f"代理已回應。") # 回應文字也存在於 event.content 中

# --- 檢查更新後的狀態 ---
updated_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
print(f"代理執行後的狀態: {updated_session.state}")
# 預期輸出可能包含：{'last_greeting': 'Hello there! How can I help you today?'}
```

> TypeScript

```typescript
import { LlmAgent, Runner, InMemorySessionService, isFinalResponse } from "@google/adk";
import { Content } from "@google/genai";

// 定義帶有 outputKey 的代理
const greetingAgent = new LlmAgent({
    name: "Greeter",
    model: "gemini-2.5-flash",
    instruction: "生成一段簡短且友好的問候語。",
    outputKey: "last_greeting" // 將回應保存到 state['last_greeting']
});

// --- 設定執行器（Runner）和工作階段 ---
const appName = "state_app";
const userId = "user1";
const sessionId = "session1";
const sessionService = new InMemorySessionService();
const runner = new Runner({
    agent: greetingAgent,
    appName: appName,
    sessionService: sessionService
});
const session = await sessionService.createSession({
    appName,
    userId,
    sessionId
});
console.log(`初始狀態: ${JSON.stringify(session.state)}`);

// --- 執行代理 ---
// 執行器處理 appendEvent 的呼叫，
// 它會使用 outputKey 自動建立 stateDelta。
const userMessage: Content = { parts: [{ text: "Hello" }] };
for await (const event of runner.runAsync({
    userId,
    sessionId,
    newMessage: userMessage
})) {
    if (isFinalResponse(event)) {
      console.log("代理已回應。"); // 回應文字也存在於 event.content 中
    }
}

// --- 檢查更新後的狀態 ---
const updatedSession = await sessionService.getSession({ appName, userId, sessionId });
console.log(`代理執行後的狀態: ${JSON.stringify(updatedSession?.state)}`);
# 預期輸出可能包含：{"last_greeting":"Hello there! How can I help you today?"}
```

> Go

```go
//  1. GreetingAgent 演示了如何使用 `OutputKey`
//     將代理的最終文字回應直接保存到工作階段狀態中。
func greetingAgentExample(sessionService session.Service) {
    fmt.Println("--- 執行 GreetingAgent (output_key) 範例 ---")
    ctx := context.Background()

    modelGreeting, err := gemini.NewModel(ctx, modelID, nil)
    if err != nil {
        log.Fatalf("為問候代理建立 Gemini 模型失敗: %v", err)
    }
    greetingAgent, err := llmagent.New(llmagent.Config{
        Name:        "Greeter",
        Model:       modelGreeting,
        Instruction: "生成一段簡短且友好的問候語。",
        OutputKey:   "last_greeting",
    })
    if err != nil {
        log.Fatalf("建立問候代理失敗: %v", err)
    }

    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          agent.Agent(greetingAgent),
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("建立執行器失敗: %v", err)
    }

    // 執行代理
    userMessage := genai.NewContentFromText("Hello", "user")
    for event, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
        if err != nil {
            log.Printf("代理錯誤: %v", err)
            continue
        }
        if isFinalResponse(event) {
            if event.LLMResponse.Content != nil {
                fmt.Printf("代理回應內容: %q\n", textParts(event.LLMResponse.Content))
            } else {
                fmt.Println("代理已回應。")
            }
        }
    }

    // 檢查更新後的狀態
    resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("獲取工作階段失敗: %v", err)
    }
    lastGreeting, _ := resp.Session.State().Get("last_greeting")
    fmt.Printf("代理執行後的狀態: last_greeting = %q\n\n", lastGreeting)
}
```

> Java

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.events.Event;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.List;
import java.util.Optional;

public class GreetingAgentExample {
    public static void main(String[] args) {
        // 定義帶有 output_key 的代理
        LlmAgent greetingAgent =
            LlmAgent.builder()
                .name("Greeter")
                .model("gemini-2.0-flash")
                .instruction("生成一段簡短且友好的問候語。")
                .description("問候代理")
                .outputKey("last_greeting") // 將回應保存到 state['last_greeting']
                .build();

        // --- 設定執行器（Runner）和工作階段 ---
        String appName = "state_app";
        String userId = "user1";
        String sessionId = "session1";

        InMemorySessionService sessionService = new InMemorySessionService();
        Runner runner = new Runner(greetingAgent, appName, null, sessionService); // 如果不使用，artifactService 可為 null

        Session session =
            sessionService.createSession(appName, userId, null, sessionId).blockingGet();
        System.out.println("初始狀態: " + session.state().entrySet());

        // --- 執行代理 ---
        // 執行器處理 appendEvent 的呼叫，
        // 它會使用 output_key 自動建立 stateDelta。
        Content userMessage = Content.builder().parts(List.of(Part.fromText("Hello"))).build();

        // Java 中的 runner.runAsync 需要 RunConfig
        RunConfig runConfig = RunConfig.builder().build();

        for (Event event : runner.runAsync(userId, sessionId, userMessage, runConfig).blockingIterable()) {
            if (event.finalResponse()) {
                System.out.println("代理已回應。"); // 回應文字也存在於 event.content 中
            }
        }

        // --- 檢查更新後的狀態 ---
        Session updatedSession =
            sessionService.getSession(appName, userId, sessionId, Optional.empty()).blockingGet();
        assert updatedSession != null;
        System.out.println("代理執行後的狀態: " + updatedSession.state().entrySet());
        // 預期輸出可能包含：{'last_greeting': 'Hello there! How can I help you today?'}
    }
}
```

</details>

在背景進行，`Runner` 使用 `output_key` 來建立帶有 `state_delta` 的必要 `EventActions` 並呼叫 `append_event`。

**2. 標準方法：`EventActions.state_delta`（用於複雜更新）**

對於更複雜的情境（更新多個鍵、非字串值、特定範圍如 `user:` 或 `app:`，或不直接與代理最終文字掛鉤的更新），您可以在 `EventActions` 中手動構建 `state_delta`。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.sessions import InMemorySessionService, Session
from google.adk.events import Event, EventActions
from google.genai.types import Part, Content
import time

# --- 設定 ---
session_service = InMemorySessionService()
app_name, user_id, session_id = "state_app_manual", "user2", "session2"
session = await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id,
    state={"user:login_count": 0, "task_status": "idle"}
)
print(f"初始狀態: {session.state}")

# --- 定義狀態更改 ---
current_time = time.time()
state_changes = {
    "task_status": "active",              # 更新工作階段狀態
    "user:login_count": session.state.get("user:login_count", 0) + 1, # 更新使用者狀態
    "user:last_login_ts": current_time,   # 新增使用者狀態
    "temp:validation_needed": True        # 新增臨時狀態（將被捨棄）
}

# --- 建立帶有動作（Actions）的事件 ---
actions_with_update = EventActions(state_delta=state_changes)
# 此事件可能代表內部系統動作，而不僅僅是代理回應
system_event = Event(
    invocation_id="inv_login_update",
    author="system", # 或 'agent', 'tool' 等。
    actions=actions_with_update,
    timestamp=current_time
    # content 可能為 None 或代表所採取的動作
)

# --- 附加事件（這會更新狀態） ---
await session_service.append_event(session, system_event)
print("呼叫了帶有顯式狀態增量（state delta）的 `append_event`。")

# --- 檢查更新後的狀態 ---
updated_session = await session_service.get_session(app_name=app_name,
                                                user_id=user_id,
                                                session_id=session_id)
print(f"事件後的狀態: {updated_session.state}")
# 預期：{'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp>}
# 注意：'temp:validation_needed' 不存在。
```

> TypeScript

```typescript
import { InMemorySessionService, createEvent, createEventActions } from "@google/adk";

// --- 設定 ---
const sessionService = new InMemorySessionService();
const appName = "state_app_manual";
const userId = "user2";
const sessionId = "session2";
const session = await sessionService.createSession({
    appName,
    userId,
    sessionId,
    state: { "user:login_count": 0, "task_status": "idle" }
});
console.log(`初始狀態: ${JSON.stringify(session.state)}`);

// --- 定義狀態更改 ---
const currentTime = Date.now();
const stateChanges = {
    "task_status": "active",              // 更新工作階段狀態
    "user:login_count": (session.state["user:login_count"] as number || 0) + 1, // 更新使用者狀態
    "user:last_login_ts": currentTime,   // 新增使用者狀態
    "temp:validation_needed": true        // 新增臨時狀態（將被捨棄）
};

// --- 建立帶有動作（Actions）的事件 ---
const actionsWithUpdate = createEventActions({
    stateDelta: stateChanges,
});
// 此事件可能代表內部系統動作，而不僅僅是代理回應
const systemEvent = createEvent({
    invocationId: "inv_login_update",
    author: "system", // 或 'agent', 'tool' 等。
    actions: actionsWithUpdate,
    timestamp: currentTime
    // content 可能為 null 或代表所採取的動作
});

// --- 附加事件（這會更新狀態） ---
await sessionService.appendEvent({ session, event: systemEvent });
console.log("呼叫了帶有顯式狀態增量（state delta）的 `appendEvent`。");

// --- 檢查更新後的狀態 ---
const updatedSession = await sessionService.getSession({
    appName,
    userId,
    sessionId
});
console.log(`事件後的狀態: ${JSON.stringify(updatedSession?.state)}`);
# 預期：{"user:login_count":1,"task_status":"active","user:last_login_ts":<timestamp>}
# 注意：'temp:validation_needed' 不存在。
```

> Go

```go
//  2. manualStateUpdateExample 演示了如何建立一個帶有顯式狀態更改
//     ("state_delta") 的事件，以更新多個鍵，包括帶有
//     user- 和 temp- 前綴的鍵。
func manualStateUpdateExample(sessionService session.Service) {
    fmt.Println("--- 執行手動狀態更新 (EventActions) 範例 ---")
    ctx := context.Background()
    s, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("獲取工作階段失敗: %v", err)
    }
    retrievedSession := s.Session

    // 定義狀態更改
    loginCount, _ := retrievedSession.State().Get("user:login_count")
    newLoginCount := 1
    if lc, ok := loginCount.(int); ok {
        newLoginCount = lc + 1
    }

    stateChanges := map[string]any{
        "task_status":            "active",
        "user:login_count":       newLoginCount,
        "user:last_login_ts":     time.Now().Unix(),
        "temp:validation_needed": true,
    }

    // 建立帶有狀態更改的事件
    systemEvent := session.NewEvent("inv_login_update")
    systemEvent.Author = "system"
    systemEvent.Actions.StateDelta = stateChanges

    // 附加事件以更新狀態
    if err := sessionService.AppendEvent(ctx, retrievedSession, systemEvent); err != nil {
        log.Fatalf("附加事件失敗: %v", err)
    }
    fmt.Println("呼叫了帶有顯式狀態增量的 `append_event`。")

    // 檢查更新後的狀態
    updatedResp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("獲取工作階段失敗: %v", err)
    }
    taskStatus, _ := updatedResp.Session.State().Get("task_status")
    loginCount, _ = updatedResp.Session.State().Get("user:login_count")
    lastLogin, _ := updatedResp.Session.State().Get("user:last_login_ts")
    temp, err := updatedResp.Session.State().Get("temp:validation_needed") // 這應該會失敗或為 nil

    fmt.Printf("事件後的狀態: task_status=%q, user:login_count=%v, user:last_login_ts=%v\n", taskStatus, loginCount, lastLogin)
    if err != nil {
        fmt.Printf("正如預期，臨時狀態未被持久化: %v\n\n", err)
    } else {
        fmt.Printf("意外的臨時狀態值: %v\n\n", temp)
    }
}
```

> Java

```java
import com.google.adk.events.Event;
import com.google.adk.events.EventActions;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class ManualStateUpdateExample {
    public static void main(String[] args) {
        // --- 設定 ---
        InMemorySessionService sessionService = new InMemorySessionService();
        String appName = "state_app_manual";
        String userId = "user2";
        String sessionId = "session2";

        ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
        initialState.put("user:login_count", 0);
        initialState.put("task_status", "idle");

        Session session =
            sessionService.createSession(appName, userId, initialState, sessionId).blockingGet();
        System.out.println("初始狀態: " + session.state().entrySet());

        // --- 定義狀態更改 ---
        long currentTimeMillis = Instant.now().toEpochMilli(); // Java 事件使用毫秒

        ConcurrentMap<String, Object> stateChanges = new ConcurrentHashMap<>();
        stateChanges.put("task_status", "active"); // 更新工作階段狀態

        // 獲取並增加 login_count
        Object loginCountObj = session.state().get("user:login_count");
        int currentLoginCount = 0;
        if (loginCountObj instanceof Number) {
        currentLoginCount = ((Number) loginCountObj).intValue();
        }
        stateChanges.put("user:login_count", currentLoginCount + 1); // 更新使用者狀態

        stateChanges.put("user:last_login_ts", currentTimeMillis); // 新增使用者狀態 (long 類型毫秒)
        stateChanges.put("temp:validation_needed", true); // 新增臨時狀態

        // --- 建立帶有動作（Actions）的事件 ---
        EventActions actionsWithUpdate = EventActions.builder().stateDelta(stateChanges).build();

        // 此事件可能代表內部系統動作，而不僅僅是代理回應
        Event systemEvent =
            Event.builder()
                .invocationId("inv_login_update")
                .author("system") // 或 'agent', 'tool' 等。
                .actions(actionsWithUpdate)
                .timestamp(currentTimeMillis)
                // content 可能為 None 或代表所採取的動作
                .build();

        // --- 附加事件（這會更新狀態） ---
        sessionService.appendEvent(session, systemEvent).blockingGet();
        System.out.println("呼叫了帶有顯式狀態增量的 `appendEvent`。");

        // --- 檢查更新後的狀態 ---
        Session updatedSession =
            sessionService.getSession(appName, userId, sessionId, Optional.empty()).blockingGet();
        assert updatedSession != null;
        System.out.println("事件後的狀態: " + updatedSession.state().entrySet());
        // 預期：{'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp_millis>}
        // 注意：'temp:validation_needed' 不存在，因為 InMemorySessionService 的 appendEvent
        // 如果鍵帶有前綴，會將增量套用到其內部的 user/app 狀態 Map，
        // 並套用到工作階段自身的狀態 Map（然後在 getSession 時合併）。
    }
}
```

</details>

**3. 透過 `CallbackContext` 或 `ToolContext`（推薦用於回調和工具）**

在代理回調（例如 `on_before_agent_call`、`on_after_agent_call`）或工具函式中修改狀態，最好使用提供給函式的 `CallbackContext` 或 `ToolContext` 的 `state` 屬性。

*   `callback_context.state['my_key'] = my_value`
*   `tool_context.state['my_key'] = my_value`

這些上下文對象專門設計用於在其各自的執行範圍內管理狀態更改。當您修改 `context.state` 時，ADK 框架會確保這些更改自動被捕獲並正確路由到由回調或工具生成的事件的 `EventActions.state_delta` 中。然後，在附加事件時，`SessionService` 會處理此增量，確保正確的持久化和追蹤。

這種方法為回調和工具中最常見的狀態更新情境抽象掉了手動建立 `EventActions` 和 `state_delta` 的過程，使您的程式碼更簡潔且更不容易出錯。

有關上下文對象的更多詳細資訊，請參閱 [Context 文件](../context/index.md)。

<details>
<summary>範例說明</summary>

> Python

```python
# 在代理回調或工具函式中
from google.adk.agents import CallbackContext # 或 ToolContext

def my_callback_or_tool_function(context: CallbackContext, # 或 ToolContext
                                 # ... 其他參數 ...
                                ):
    # 更新現有狀態
    count = context.state.get("user_action_count", 0)
    context.state["user_action_count"] = count + 1

    # 新增狀態
    context.state["temp:last_operation_status"] = "success"

    # 狀態更改會自動成為事件 state_delta 的一部分
    # ... 回調/工具的其他邏輯 ...
```

> TypeScript

```typescript
// 在代理回調或工具函式中
import { CallbackContext } from "@google/adk"; // 或 ToolContext

function myCallbackOrToolFunction(
    context: CallbackContext, // 或 ToolContext
    // ... 其他參數 ...
) {
    // 更新現有狀態
    const count = context.state.get("user_action_count", 0);
    context.state.set("user_action_count", count + 1);

    // 新增狀態
    context.state.set("temp:last_operation_status", "success");

    // 狀態更改會自動成為事件 stateDelta 的一部分
    // ... 回調/工具的其他邏輯 ...
}
```

> Go

```go
//  3. contextStateUpdateExample 演示了在工具函式中
//     使用提供的 `tool.Context` 修改狀態的推薦方式。
func contextStateUpdateExample(sessionService session.Service) {
    fmt.Println("--- 執行上下文狀態更新 (ToolContext) 範例 ---")
    ctx := context.Background()

    // 定義修改狀態的工具
    updateActionCountTool, err := functiontool.New(
        functiontool.Config{Name: "update_action_count", Description: "更新狀態中的使用者動作計數。"},
        func(tctx tool.Context, args struct{}) (struct{}, error) {
            actx, ok := tctx.(agent.CallbackContext)
            if !ok {
                log.Fatalf("tool.Context 類型不是 agent.CallbackContext")
            }
            s, err := actx.State().Get("user_action_count")
            if err != nil {
                log.Printf("無法獲取 user_action_count: %v", err)
            }
            newCount := 1
            if c, ok := s.(int); ok {
                newCount = c + 1
            }
            if err := actx.State().Set("user_action_count", newCount); err != nil {
                log.Printf("無法設置 user_action_count: %v", err)
            }
            if err := actx.State().Set("temp:last_operation_status", "來自工具的成功訊息"); err != nil {
                log.Printf("無法設置 temp:last_operation_status: %v", err)
            }
            fmt.Println("工具：已透過 agent.CallbackContext 更新狀態。")
            return struct{}{}, nil
        },
    )
    if err != nil {
        log.Fatalf("建立工具失敗: %v", err)
    }

    // 定義使用該工具的代理
    modelTool, err := gemini.NewModel(ctx, modelID, nil)
    if err != nil {
        log.Fatalf("為工具代理建立 Gemini 模型失敗: %v", err)
    }
    toolAgent, err := llmagent.New(llmagent.Config{
        Name:        "ToolAgent",
        Model:       modelTool,
        Instruction: "使用 update_action_count 工具。",
        Tools:       []tool.Tool{updateActionCountTool},
    })
    if err != nil {
        log.Fatalf("建立工具代理失敗: %v", err)
    }

    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          agent.Agent(toolAgent),
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("建立執行器失敗: %v", err)
    }

    // 執行代理以觸發工具
    userMessage := genai.NewContentFromText("請更新動作計數。", "user")
    for _, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
        if err != nil {
            log.Printf("代理錯誤: %v", err)
        }
    }

    // 檢查更新後的狀態
    resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("獲取工作階段失敗: %v", err)
    }
    actionCount, _ := resp.Session.State().Get("user_action_count")
    fmt.Printf("工具執行後的狀態: user_action_count = %v\n", actionCount)
}
```

> Java

```java
// 在代理回調或工具方法中
import com.google.adk.agents.CallbackContext; // 或 ToolContext
// ... 其他匯入 ...

public class MyAgentCallbacks {
    public void onAfterAgent(CallbackContext callbackContext) {
        // 更新現有狀態
        Integer count = (Integer) callbackContext.state().getOrDefault("user_action_count", 0);
        callbackContext.state().put("user_action_count", count + 1);

        // 新增狀態
        callbackContext.state().put("temp:last_operation_status", "success");

        // 狀態更改會自動成為事件 state_delta 的一部分
        // ... 回調的其他邏輯 ...
    }
}
```

</details>

**`append_event` 的功用：**

* 將 `Event` 添加到 `session.events`。
* 從事件的 `actions` 中讀取 `state_delta`。
* 將這些更改套用到由 `SessionService` 管理的狀態，根據服務類型正確處理前綴和持久化。
* 更新工作階段的 `last_update_time`。
* 確保並行更新的執行緒安全。

### ⚠️ 關於直接修改狀態的警告

避免在代理調用的管理生命週期 *之外*（即不是透過 `CallbackContext` 或 `ToolContext`），直接修改從 `SessionService` 直接獲取的 `Session` 對象（例如透過 `session_service.get_session()` 或 `session_service.create_session()`）上的 `session.state` 集合（字典/Map）。例如，像 `retrieved_session = await session_service.get_session(...); retrieved_session.state['key'] = value` 這樣的程式碼是有問題的。

在回調或工具中 *使用* `CallbackContext.state` 或 `ToolContext.state` 修改狀態是確保更改被追蹤的正確方式，因為這些上下文對象處理了與事件系統必要的整合。

**為何強烈不建議進行直接修改（在上下文之外）：**

1. **繞過事件歷史記錄：** 更改不會被記錄為 `Event`，從而失去了稽核性（auditability）。
2. **破壞持久化：** 以這種方式進行的更改**很可能不會被** `DatabaseSessionService` 或 `VertexAiSessionService` 保存。它們依賴於 `append_event` 來觸發保存。
3. **非執行緒安全：** 可能導致競態條件（race conditions）和遺失更新。
4. **忽略時間戳記/邏輯：** 不會更新 `last_update_time` 或觸發相關的事件邏輯。

**建議：** 堅持透過 `output_key`、`EventActions.state_delta`（手動建立事件時）或在各自範圍內修改 `CallbackContext` 或 `ToolContext` 對象的 `state` 屬性來更新狀態。這些方法確保了可靠、可追蹤且持久的狀態管理。僅在 *讀取* 狀態時才使用對 `session.state`（從 `SessionService` 獲取的工作階段）的直接存取。

### 狀態設計最佳實務回顧

* **極簡主義：** 僅存儲必要的動態資料。
* **序列化：** 使用基本、可序列化的類型。
* **描述性鍵與前綴：** 使用清晰的名稱和適當的前綴（`user:`、`app:`、`temp:` 或不使用）。
* **淺層結構：** 盡可能避免深層嵌套。
* **標準更新流程：** 依賴於 `append_event`。
