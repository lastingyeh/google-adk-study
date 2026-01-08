# State：Session 的暫存記事本 (Scratchpad)

🔔 `更新日期：2026 年 1 月 5 日`

在每個 `Session`（我們的對話執行緒）中，**`state`** 屬性扮演著 Agent 在該次互動中的專用記事本角色。雖然 `session.events` 保存了完整的歷史記錄，但 `session.state` 才是 Agent 用於存取與更新對話期間所需**動態細節**的地方。

## 什麼是 `session.state`？

從概念上來說，`session.state` 是一個包含「鍵值對」（Key-Value Pairs）的集合（Dictionary 或 Map）。它專門設計用於存儲 Agent 為了讓對話更有效率而需要記住或追蹤的資訊：

| 用途         | 說明                           | 範例                                     |
| ------------ | ------------------------------ | ---------------------------------------- |
| 個性化互動   | 記住使用者先前提到的偏好       | `'user_preference_theme': 'dark'`        |
| 追蹤任務進度 | 記錄多輪對話過程中的步驟       | `'booking_step': 'confirm_payment'`      |
| 累積資訊     | 建立列表或摘要                 | `'shopping_cart_items': ['book', 'pen']` |
| 輔助決策     | 存儲影響下一個回應的標記或數值 | `'user_is_authenticated': True`          |

### `State` 的關鍵特性

| 特性             | 說明                                                                                                                                                                                                                                                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 可序列化的鍵值對 | - 資料以 `key: value` 形式儲存。<br>- **鍵 (Keys)：** 必須為字串，建議具描述性（如 `'departure_city'`、`'user:language_preference'`）。<br>- **值 (Values)：** 必須可序列化，僅使用基本型別（字串、數字、布林值、簡單列表/字典）。<br>- ⚠️ 請勿存儲不可序列化物件（如自定義類別、函式、資料庫連線等），可存識別碼以便後續查詢。 |
| 可變性           | - `state` 內容會隨對話進行動態變化。                                                                                                                                                                                                                                                                                            |
| 持久性           | - 是否持久取決於所用的 `SessionService`：<br>　- `InMemorySessionService`：不具持久性，重啟後資料消失。<br>　- `DatabaseSessionService` / `VertexAiSessionService`：具持久性，資料可可靠保存。                                                                                                                                  |

> [!NOTE]開發提示
> 各語言 Session State 操作對照表

| 語言       | 取得 State 值                | 設定 State 值                       | 備註              |
| ---------- | ---------------------------- | ----------------------------------- | ----------------- |
| Python     | `session.state['key']`       | `session.state['key'] = value`      | 直接存取字典      |
| TypeScript | `context.state.get('key')`   | `context.state.set('key', value)`   | 使用 Map-like API |
| Go         | `context.State().Get("key")` | `context.State().Set("key", value)` | 方法存取          |
| Java       | `session.state().get("key")` | `session.state().put("key", value)` | 使用 Map 方法     |

---

### 使用前綴組織 State：作用域 (Scope) 很重要

State 鍵值的前綴定義了它們的作用域與持久化行為，這在搭配持久化服務時尤為重要：

| 前綴    | 作用域說明                                    | 持久性說明                                 | 常見用途/案例                    | 範例程式碼                                             |
| ------- | --------------------------------------------- | ------------------------------------------ | -------------------------------- | ------------------------------------------------------ |
| 無前綴  | 僅限於**當前 Session** (`id`)                 | 僅在 `SessionService` 具備持久化能力時保存 | 追蹤任務進度、臨時標記           | `session.state['current_intent'] = 'book_flight'`      |
| `user:` | 與 `user_id` 綁定，該使用者所有 Session 共享  | 在 `Database` 或 `VertexAI` 模式下具持久性 | 使用者偏好、個人資料             | `session.state['user:preferred_language'] = 'zh-TW'`   |
| `app:`  | 與 `app_name` 綁定，所有使用者與 Session 共享 | 在持久化服務中會被保存                     | 全域設定、共享模板               | `session.state['app:global_discount_code'] = 'SAVE10'` |
| `temp:` | 僅限於**當前調用 (Invocation)**               | **不具持久性**，調用完成後即丟棄           | 中間計算結果、工具間臨時數據傳遞 | `session.state['temp:raw_api_response'] = {...}`       |

> [!NOTE] 子 Agent 與調用上下文
> 當父 Agent 調用子 Agent（如使用 `SequentialAgent`）時，它會傳遞 `InvocationContext`。這意味著整個 Agent 調用鏈共享相同的 `temp:` state。

---

## 在 Agent 指令中存取 Session State

在定義 `LlmAgent` 時，您可以使用簡單的樣板語法將 Session State 的值直接注入到 Agent 的指令字串中。

### 使用 `{key}` 樣板

要從 Session State 注入值，請將鍵名括在花括號中：`{key}`。框架會在將指令傳遞給 LLM 之前，自動將其替換為 `session.state` 中的對應值。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent

story_generator = LlmAgent(
    name="StoryGenerator",
    model="gemini-2.0-flash",
    instruction="""請寫一個關於貓的短篇故事，重點主題是：{topic}。"""
)
# 若 session.state['topic'] 為 "友情"，LLM 接收到的指令將是：
# "請寫一個關於貓的短篇故事，重點主題是：友情。"
```

> typescript

```typescript
import { LlmAgent } from '@google/adk';

const storyGenerator = new LlmAgent({
  name: 'StoryGenerator',
  model: 'gemini-2.5-flash',
  instruction: '請寫一個關於貓的短篇故事，重點主題是：{topic}。',
});
```

> go

```go
func main() {
ctx := context.Background()
sessionService := session.InMemoryService()

// 1. Initialize a session with a 'topic' in its state.
_, err := sessionService.Create(ctx, &session.CreateRequest{
    AppName:   appName,
    UserID:    userID,
    SessionID: sessionID,
    State: map[string]any{
        "topic": "friendship",
    },
})
if err != nil {
    log.Fatalf("Failed to create session: %v", err)
}

// 2. Create an agent with an instruction that uses a {topic} placeholder.
//    The ADK will automatically inject the value of "topic" from the
//    session state into the instruction before calling the LLM.
model, err := gemini.NewModel(ctx, modelID, nil)
if err != nil {
    log.Fatalf("Failed to create Gemini model: %v", err)
}
storyGenerator, err := llmagent.New(llmagent.Config{
    Name:        "StoryGenerator",
    Model:       model,
    Instruction: "Write a short story about a cat, focusing on the theme: {topic}.",
})
if err != nil {
    log.Fatalf("Failed to create agent: %v", err)
}

r, err := runner.New(runner.Config{
    AppName:        appName,
    Agent:          agent.Agent(storyGenerator),
    SessionService: sessionService,
})
if err != nil {
    log.Fatalf("Failed to create runner: %v", err)
}
```

</details>

#### 重要考量事項

- **鍵值存在性：** 確保指令中引用的鍵存在於 `session.state` 中，否則會報錯。若該鍵可能不存在，請使用 `{topic?}` 語法。
- **數據類型：** 關聯的值應為字串，或可輕易轉換為字串的類型。
- **轉義：** 如果指令中需要使用字面上的花括號（如 JSON 格式），則需要進行轉義。

#### 通過 InstructionProvider 過濾狀態注入

在某些情況下，您可能希望在您的指令(instructions) 中直接使用 {{ and }} 而不觸發狀態注入機制。例如，您可能正在編寫為代理撰寫的指令，該代理用於幫助使用相同語法的模板語言。

為了達到這一點，您可以為 instruction 參數提供一個函數而不是字串。這個函數被稱為 InstructionProvider 。當您使用 InstructionProvider 時，ADK 會嘗試注入狀態，並將您的指令字串原封不動地傳遞給模型。

InstructionProvider 函式接收一個 ReadonlyContext 物件，您可以使用此物件來存取工作階段狀態或其他相關資訊，如果您需要動態建立指令。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

# 這是一個 InstructionProvider（指令產生器函式）
def my_instruction_provider(context: ReadonlyContext) -> str:
    # 你可以選擇性地利用 context 動態產生指令
    # 此範例直接回傳帶有雙大括號的靜態字串，ADK 不會進行狀態注入
    return "This is an instruction with {{literal_braces}} that will not be replaced."

agent = LlmAgent(
    model="gemini-2.0-flash",
    name="template_helper_agent",
    instruction=my_instruction_provider
)
# 重點註解：
# - 使用 InstructionProvider 函式時，指令中的 {{...}} 會被原樣保留，不會被 state 替換
# - 適合需要產生模板語法或避免自動注入的場景
```

> TypeScript

```typescript
import { LlmAgent, ReadonlyContext } from '@google/adk';

// 這是一個 InstructionProvider（指令產生器函式）
function myInstructionProvider(context: ReadonlyContext): string {
  // 你可以選擇性地利用 context 動態產生指令
  // 此範例直接回傳帶有雙大括號的靜態字串，ADK 不會進行狀態注入
  return 'This is an instruction with {{literal_braces}} that will not be replaced.';
}

const agent = new LlmAgent({
  model: 'gemini-2.5-flash',
  name: 'template_helper_agent',
  instruction: myInstructionProvider,
});
// 重點註解：
// - 使用 InstructionProvider 函式時，指令中的 {{...}} 會被原樣保留，不會被 state 替換
// - 適合需要產生模板語法或避免自動注入的場景
```

> Go

```go
// 這是一個 InstructionProvider（指令產生器函式）
// 此函式直接回傳帶有雙大括號的靜態字串，ADK 不會進行狀態注入，指令會原樣傳遞給模型
func staticInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
    return "This is an instruction with {{literal_braces}} that will not be replaced.", nil
}
// 重點註解：
// - 使用 InstructionProvider 函式時，指令中的 {{...}} 會被原樣保留，不會被 state 替換
// - 適合需要產生模板語法或避免自動注入的場景
```

</details>

---

如果您想同時使用 InstructionProvider 和將狀態注入您的指令中，您可以使用 inject_session_state 工具函數。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.utils import instructions_utils

# 這是一個動態 InstructionProvider 範例
# - 使用 inject_session_state 工具函式，可同時：
#   1. 將 session.state['adjective'] 注入 {adjective} 樣板
#   2. 保留 {{literal_braces}} 為字面大括號，不會被替換
async def my_dynamic_instruction_provider(context: ReadonlyContext) -> str:
    template = "This is a {adjective} instruction with {{literal_braces}}."
    # 會將 'adjective' 狀態變數注入，但保留雙大括號
    return await instructions_utils.inject_session_state(template, context)

agent = LlmAgent(
    model="gemini-2.0-flash",
    name="dynamic_template_helper_agent",
    instruction=my_dynamic_instruction_provider
)
```

> Go

```go
// 這是一個動態 InstructionProvider 範例
// - 使用 instructionutil.InjectSessionState 工具函式，可同時：
//   1. 將 session state 的 "adjective" 注入 {adjective} 樣板
//   2. 保留 {{literal_braces}} 為字面大括號，不會被替換
func dynamicInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
    template := "This is a {adjective} instruction with {{literal_braces}}."
    // 會將 'adjective' 狀態變數注入，但保留雙大括號
    return instructionutil.InjectSessionState(ctx, template)
}
```

</details>

| **優點：直接注入 Session State** |                                                             |
| -------------------------------- | ----------------------------------------------------------- |
| **清晰性 (Clarity)**             | 明確標示哪些指令部分來自 session state，動態內容一目了然。  |
| **可靠性 (Reliability)**         | 不需依賴 LLM 理解自然語言描述，直接由框架注入正確的狀態值。 |
| **可維護性 (Maintainability)**   | 指令字串簡潔，變更 state 變數名稱時更容易維護與追蹤。       |

> **補充說明**
> 此直接注入方法僅適用於 LlmAgent 的 instruction。其他存取 state 的方式，請參考下節說明。

---

## 更新 State 的建議方法

> [!NOTE] 修改 State 的正確方式
> 當您需要更改 Session State 時，最安全的方法是直接修改傳遞給函數的 **`Context` 物件上的 `state` 屬性**（例如：`callback_context.state['my_key'] = 'new_value'`）。這是受框架控管的直接操作，ADK 會自動追蹤這些變更。
> 這與直接修改從 SessionService 獲取的 Session 對象上的 state 顯著不同（例如， my_session.state['my_key'] = 'new_value' ）。您應該避免這種做法，因為它會跳過 ADK 的事件追蹤，並可能導致數據丟失。此頁面末尾的“警告”部分有更多有關這項重要區分的詳細信息。

工作階段應該始終作為使用 `session_service.append_event()` 添加到會話歷史的一部分來更新狀態。這確保變更被追蹤，持久性正確運作，並且更新是線程安全的。

### State 模式定義說明表

| 方式                                  | 定義                                                   | 描述                                                                                    | 使用場景                                                                                                                               |
| :------------------------------------ | :----------------------------------------------------- | :-------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| **`output_key`**                      | `LlmAgent` 的 `output_key` 屬性。                      | 將 Agent 的最終文本回應自動保存到 State 的指定鍵。                                      | 適用於最簡單的場景：將 Agent 的文字輸出直接存為一個狀態值。                                                                            |
| **`EventActions.state_delta`**        | 手動在 `EventActions` 中構建 `state_delta` 字典。      | 提供最完整的控制權，可一次更新多個鍵、複雜資料類型，並管理不同生命週期的狀態。          | 1. 需一次更新多個狀態值。<br>2. 需儲存非字串值。<br>3. 由系統邏輯觸發的狀態更新。<br>4. 需精確控制狀態生命週期 (如 `user:`, `temp:`)。 |
| **`CallbackContext` / `ToolContext`** | 在回呼或工具的 `context` 物件上直接修改 `state` 屬性。 | ADK 框架會自動將 `context.state` 的變更轉換為 `state_delta`，是為開發者提供的便利抽象。 | **在回呼 (Callback) 和工具 (Tool) 內部**更新狀態的**建議方法**。                                                                       |

---
### 1. 簡單方式：`output_key` (適用於 Agent 文本回應)

這是將 Agent 的最終文本回應直接保存到 State 的最簡單方法。

<details>
<summary>範例說明</summary>

> Python

```python
# 定義具備 output_key 的 Agent
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part

# 1. 建立 Agent，設定 output_key，回應會自動儲存到 state['last_greeting']

greeting_agent = LlmAgent(
    name="Greeter",
    model="gemini-2.0-flash", # 使用有效模型名稱
    instruction="產生一則簡短且友善的問候語。",
    output_key="last_greeting" # 回應自動存入 state['last_greeting']
)

# --- 建立 Runner 與 Session ---

app_name, user_id, session_id = "state_app", "user1", "session1"
session_service = InMemorySessionService()

runner = Runner(
    agent=greeting_agent,
    app_name=app_name,
    session_service=session_service
)

session = await session_service.create_session(app_name=app_name,user_id=user_id,session_id=session_id)
print(f"初始 state: {session.state}")

# --- 執行 Agent ---

# Runner 會自動呼叫 append_event，並根據 output_key 建立 state_delta

user_message = Content(parts=[Part(text="Hello")])

for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
    if event.is_final_response():
    print(f"Agent 已回應。") # 回應內容也可從 event.content 取得

# --- 檢查更新後的 State ---

updated_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
print(f"Agent 執行後的 state: {updated_session.state}")

# 預期輸出範例：{'last_greeting': 'Hello there! How can I help you today?'}

```

---

> TypeScript

```typescript
import {
  LlmAgent,
  Runner,
  InMemorySessionService,
  isFinalResponse,
} from '@google/adk';
import { Content } from '@google/genai';

// 1. 建立 Agent，設定 outputKey，回應自動存入 state['last_greeting']
const greetingAgent = new LlmAgent({
  name: 'Greeter',
  model: 'gemini-2.5-flash',
  instruction: '產生一則簡短且友善的問候語。',
  outputKey: 'last_greeting',
});

// --- 建立 Runner 與 Session ---
const appName = 'state_app';
const userId = 'user1';
const sessionId = 'session1';
const sessionService = new InMemorySessionService();
const runner = new Runner({
  agent: greetingAgent,
  appName: appName,
  sessionService: sessionService,
});
const session = await sessionService.createSession({
  appName,
  userId,
  sessionId,
});
console.log(`初始 state: ${JSON.stringify(session.state)}`);

// --- 執行 Agent ---
// Runner 會自動呼叫 appendEvent，並根據 outputKey 建立 stateDelta
const userMessage: Content = { parts: [{ text: 'Hello' }] };
for await (const event of runner.runAsync({
  userId,
  sessionId,
  newMessage: userMessage,
})) {
  if (isFinalResponse(event)) {
    console.log('Agent 已回應。'); // 回應內容也可從 event.content 取得
  }
}

// --- 檢查更新後的 State ---
const updatedSession = await sessionService.getSession({
  appName,
  userId,
  sessionId,
});
console.log(`Agent 執行後的 state: ${JSON.stringify(updatedSession?.state)}`);
// 預期輸出範例：{"last_greeting":"Hello there! How can I help you today?"}
```

---

> Go

```go
// 1. GreetingAgent 示範使用 OutputKey，將 Agent 最終回應直接存入 session state。
func greetingAgentExample(sessionService session.Service) {
    fmt.Println("--- 執行 GreetingAgent (output_key) 範例 ---")
    ctx := context.Background()

    modelGreeting, err := gemini.NewModel(ctx, modelID, nil)
    if err != nil {
        log.Fatalf("建立 Gemini 模型失敗: %v", err)
    }
    greetingAgent, err := llmagent.New(llmagent.Config{
        Name:        "Greeter",
        Model:       modelGreeting,
        Instruction: "產生一則簡短且友善的問候語。",
        OutputKey:   "last_greeting",
    })
    if err != nil {
        log.Fatalf("建立 greeting agent 失敗: %v", err)
    }

    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          agent.Agent(greetingAgent),
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("建立 runner 失敗: %v", err)
    }

    // 執行 Agent
    userMessage := genai.NewContentFromText("Hello", "user")
    for event, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
        if err != nil {
            log.Printf("Agent 錯誤: %v", err)
            continue
        }
        if isFinalResponse(event) {
            if event.LLMResponse.Content != nil {
                fmt.Printf("Agent 回應: %q\n", textParts(event.LLMResponse.Content))
            } else {
                fmt.Println("Agent 已回應。")
            }
        }
    }

    // 檢查更新後的 state
    resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("取得 session 失敗: %v", err)
    }
    lastGreeting, _ := resp.Session.State().Get("last_greeting")
    fmt.Printf("Agent 執行後的 state: last_greeting = %q\n\n", lastGreeting)
}
```

---

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
    // 1. 建立 Agent，設定 output_key，回應自動存入 state['last_greeting']
    LlmAgent greetingAgent =
        LlmAgent.builder()
            .name("Greeter")
            .model("gemini-2.0-flash")
            .instruction("產生一則簡短且友善的問候語。")
            .description("Greeting agent")
            .outputKey("last_greeting")
            .build();

    // --- 建立 Runner 與 Session ---
    String appName = "state_app";
    String userId = "user1";
    String sessionId = "session1";

    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(greetingAgent, appName, null, sessionService);

    Session session =
        sessionService.createSession(appName, userId, null, sessionId).blockingGet();
    System.out.println("初始 state: " + session.state().entrySet());

    // --- 執行 Agent ---
    // Runner 會自動呼叫 appendEvent，並根據 output_key 建立 stateDelta
    Content userMessage = Content.builder().parts(List.of(Part.fromText("Hello"))).build();

    RunConfig runConfig = RunConfig.builder().build();

    for (Event event : runner.runAsync(userId, sessionId, userMessage, runConfig).blockingIterable()) {
      if (event.finalResponse()) {
        System.out.println("Agent 已回應。"); // 回應內容也可從 event.content 取得
      }
    }

    // --- 檢查更新後的 State ---
    Session updatedSession =
        sessionService.getSession(appName, userId, sessionId, Optional.empty()).blockingGet();
    assert updatedSession != null;
    System.out.println("Agent 執行後的 state: " + updatedSession.state().entrySet());
    // 預期輸出範例：{'last_greeting': 'Hello there! How can I help you today?'}
  }
}
```

</details>

### 2. 標準方式：`EventActions.state_delta` (適用於複雜更新)

對於更複雜的場景（如更新多個鍵、非字串值或特定前綴），您可以手動在 `EventActions` 中構建 `state_delta`。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.sessions import InMemorySessionService, Session
from google.adk.events import Event, EventActions
from google.genai.types import Part, Content
import time

# --- 初始化 Session 服務 ---
session_service = InMemorySessionService()
app_name, user_id, session_id = "state_app_manual", "user2", "session2"
session = await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id,
    state={"user:login_count": 0, "task_status": "idle"}  # 初始狀態
)
print(f"初始 state: {session.state}")

# --- 定義要變更的 State ---
current_time = time.time()
state_changes = {
    "task_status": "active",              # 更新 session 層級狀態
    "user:login_count": session.state.get("user:login_count", 0) + 1, # 更新 user 層級狀態
    "user:last_login_ts": current_time,   # 新增 user 層級狀態
    "temp:validation_needed": True        # 新增 temp 層級狀態（僅暫存，不會持久化）
}

# --- 建立帶有 State 變更的 Event ---
actions_with_update = EventActions(state_delta=state_changes)
# 此事件可代表系統內部動作，不僅限於 agent 回應
system_event = Event(
    invocation_id="inv_login_update",
    author="system", # 也可為 'agent'、'tool' 等
    actions=actions_with_update,
    timestamp=current_time
    # content 可為 None 或描述此次動作
)

# --- 實際寫入事件（會更新狀態） ---
await session_service.append_event(session, system_event)
print("已呼叫 `append_event` 並套用明確 state delta。")

# --- 檢查更新後的 State ---
updated_session = await session_service.get_session(app_name=app_name,
                                            user_id=user_id,
                                            session_id=session_id)
print(f"事件後 state: {updated_session.state}")
# 預期結果：{'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp>}
# 注意：'temp:validation_needed' 不會被持久化
```

> TypeScript

```typescript
import {
  InMemorySessionService,
  createEvent,
  createEventActions,
} from '@google/adk';

// --- 初始化 Session 服務 ---
const sessionService = new InMemorySessionService();
const appName = 'state_app_manual';
const userId = 'user2';
const sessionId = 'session2';
const session = await sessionService.createSession({
  appName,
  userId,
  sessionId,
  state: { 'user:login_count': 0, task_status: 'idle' }, // 初始狀態
});
console.log(`初始 state: ${JSON.stringify(session.state)}`);

// --- 定義要變更的 State ---
const currentTime = Date.now();
const stateChanges = {
  task_status: 'active', // 更新 session 層級狀態
  'user:login_count': ((session.state['user:login_count'] as number) || 0) + 1, // 更新 user 層級狀態
  'user:last_login_ts': currentTime, // 新增 user 層級狀態
  'temp:validation_needed': true, // 新增 temp 層級狀態（僅暫存，不會持久化）
};

// --- 建立帶有 State 變更的 Event ---
const actionsWithUpdate = createEventActions({
  stateDelta: stateChanges,
});
// 此事件可代表系統內部動作，不僅限於 agent 回應
const systemEvent = createEvent({
  invocationId: 'inv_login_update',
  author: 'system', // 也可為 'agent'、'tool' 等
  actions: actionsWithUpdate,
  timestamp: currentTime,
  // content 可為 null 或描述此次動作
});

// --- 實際寫入事件（會更新狀態） ---
await sessionService.appendEvent({ session, event: systemEvent });
console.log('已呼叫 `appendEvent` 並套用明確 state delta。');

// --- 檢查更新後的 State ---
const updatedSession = await sessionService.getSession({
  appName,
  userId,
  sessionId,
});
console.log(`事件後 state: ${JSON.stringify(updatedSession?.state)}`);
// 預期結果：{"user:login_count":1,"task_status":"active","user:last_login_ts":<timestamp>}
// 注意：'temp:validation_needed' 不會被持久化
```

> Go

```go
//  2. manualStateUpdateExample 示範如何建立帶有明確 state_delta 的事件，
//     可同時更新多個 key（包含 user: 與 temp: 前綴）。
func manualStateUpdateExample(sessionService session.Service) {
    fmt.Println("--- 執行手動 State 更新 (EventActions) 範例 ---")
    ctx := context.Background()
    s, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("取得 session 失敗: %v", err)
    }
    retrievedSession := s.Session

    // 定義要變更的 state
    loginCount, _ := retrievedSession.State().Get("user:login_count")
    newLoginCount := 1
    if lc, ok := loginCount.(int); ok {
        newLoginCount = lc + 1
    }

    stateChanges := map[string]any{
        "task_status":            "active",                // 更新 session 層級狀態
        "user:login_count":       newLoginCount,           // 更新 user 層級狀態
        "user:last_login_ts":     time.Now().Unix(),       // 新增 user 層級狀態
        "temp:validation_needed": true,                    // 新增 temp 層級狀態（僅暫存，不會持久化）
    }

    // 建立帶有 state 變更的事件
    systemEvent := session.NewEvent("inv_login_update")
    systemEvent.Author = "system"
    systemEvent.Actions.StateDelta = stateChanges

    // 實際寫入事件（會更新狀態）
    if err := sessionService.AppendEvent(ctx, retrievedSession, systemEvent); err != nil {
        log.Fatalf("append event 失敗: %v", err)
    }
    fmt.Println("已呼叫 `append_event` 並套用明確 state delta。")

    // 檢查更新後的 state
    updatedResp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("取得 session 失敗: %v", err)
    }
    taskStatus, _ := updatedResp.Session.State().Get("task_status")
    loginCount, _ = updatedResp.Session.State().Get("user:login_count")
    lastLogin, _ := updatedResp.Session.State().Get("user:last_login_ts")
    temp, err := updatedResp.Session.State().Get("temp:validation_needed") // 預期為 nil 或錯誤

    fmt.Printf("事件後 state: task_status=%q, user:login_count=%v, user:last_login_ts=%v\n", taskStatus, loginCount, lastLogin)
    if err != nil {
        fmt.Printf("如預期，temp 狀態未被持久化: %v\n\n", err)
    } else {
        fmt.Printf("意外發現 temp 狀態: %v\n\n", temp)
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
    // --- 初始化 Session 服務 ---
    InMemorySessionService sessionService = new InMemorySessionService();
    String appName = "state_app_manual";
    String userId = "user2";
    String sessionId = "session2";

    ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
    initialState.put("user:login_count", 0);
    initialState.put("task_status", "idle");

    Session session =
        sessionService.createSession(appName, userId, initialState, sessionId).blockingGet();
    System.out.println("初始 state: " + session.state().entrySet());

    // --- 定義要變更的 State ---
    long currentTimeMillis = Instant.now().toEpochMilli(); // Java 事件時間戳（毫秒）

    ConcurrentMap<String, Object> stateChanges = new ConcurrentHashMap<>();
    stateChanges.put("task_status", "active"); // 更新 session 層級狀態

    // 取得並遞增 login_count
    Object loginCountObj = session.state().get("user:login_count");
    int currentLoginCount = 0;
    if (loginCountObj instanceof Number) {
      currentLoginCount = ((Number) loginCountObj).intValue();
    }
    stateChanges.put("user:login_count", currentLoginCount + 1); // 更新 user 層級狀態

    stateChanges.put("user:last_login_ts", currentTimeMillis); // 新增 user 層級狀態
    stateChanges.put("temp:validation_needed", true); // 新增 temp 層級狀態（僅暫存，不會持久化）

    // --- 建立帶有 State 變更的 Event ---
    EventActions actionsWithUpdate = EventActions.builder().stateDelta(stateChanges).build();

    // 此事件可代表系統內部動作，不僅限於 agent 回應
    Event systemEvent =
        Event.builder()
            .invocationId("inv_login_update")
            .author("system") // 也可為 'agent'、'tool' 等
            .actions(actionsWithUpdate)
            .timestamp(currentTimeMillis)
            // content 可為 None 或描述此次動作
            .build();

    // --- 實際寫入事件（會更新狀態） ---
    sessionService.appendEvent(session, systemEvent).blockingGet();
    System.out.println("已呼叫 `appendEvent` 並套用明確 state delta。");

    // --- 檢查更新後的 State ---
    Session updatedSession =
        sessionService.getSession(appName, userId, sessionId, Optional.empty()).blockingGet();
    assert updatedSession != null;
    System.out.println("事件後 state: " + updatedSession.state().entrySet());
    // 預期結果：{'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp_millis>}
    // 注意：'temp:validation_needed' 不會被持久化，因為 InMemorySessionService 只會將有前綴的 key
    // 寫入對應 user/app state map，session state 會合併回傳，但 temp: 僅暫存於事件生命週期。
  }
}
```

</details>

### 3. 透過 `CallbackContext` 或 `ToolContext` (推薦用於 Callback 與 Tool)

在 Agent 回調或工具函數內部，建議使用 `state` 屬性：

- `callback_context.state['my_key'] = my_value`
- `tool_context.state['my_key'] = my_value`

當您修改 `context.state` 時，ADK 框架會確保這些變更自動封裝進 `EventActions.state_delta` 並記錄在事件中，從而實現正確的追蹤與持久化。

這些上下文物件特別設計用於管理其相關執行範圍內的狀態變更。當您修改 `context.state` 時，ADK 框架確保這些變更會自動捕捉並正確路由到由回調或工具生成的事件的 `EventActions.state_delta` 中。這個變化差異然後在事件附加時由 `SessionService` 處理，確保正確的持久性和追蹤。

此方法抽象出在回調和工具中對於大多數常見狀態更新情況的 `EventActions` 和 `state_delta` 的手動創建，使您的代碼更簡潔且錯誤率更低。

<details>
<summary>範例說明</summary>

> Python

```python
# 在 Agent 回呼或工具函式中操作 State
from google.adk.agents import CallbackContext # 或 ToolContext

def my_callback_or_tool_function(context: CallbackContext, # 或 ToolContext
                                 # ... 其他參數 ...
                                ):
    # 更新現有狀態值
    count = context.state.get("user_action_count", 0)
    context.state["user_action_count"] = count + 1  # 累加使用者動作次數

    # 新增暫存狀態（temp: 前綴不會持久化）
    context.state["temp:last_operation_status"] = "success"

    # 這些狀態變更會自動被框架封裝進事件的 state_delta
    # ... 其餘回呼/工具邏輯 ...
```

> TypeScript

```typescript
// 在 Agent 回呼或工具函式中操作 State
import { CallbackContext } from '@google/adk'; // 或 ToolContext

function myCallbackOrToolFunction(
  context: CallbackContext // 或 ToolContext
  // ... 其他參數 ...
) {
  // 更新現有狀態值
  const count = context.state.get('user_action_count', 0);
  context.state.set('user_action_count', count + 1); // 累加使用者動作次數

  // 新增暫存狀態（temp: 前綴不會持久化）
  context.state.set('temp:last_operation_status', 'success');

  // 這些狀態變更會自動被框架封裝進事件的 stateDelta
  // ... 其餘回呼/工具邏輯 ...
}
```

> Go

```go
//  3. contextStateUpdateExample 示範如何在工具函式 (tool.Context) 內正確修改 state
func contextStateUpdateExample(sessionService session.Service) {
    fmt.Println("--- 執行 Context State Update (ToolContext) 範例 ---")
    ctx := context.Background()

    // 定義會修改 state 的工具
    updateActionCountTool, err := functiontool.New(
        functiontool.Config{Name: "update_action_count", Description: "更新 state 中的 user_action_count。"},
        func(tctx tool.Context, args struct{}) (struct{}, error) {
            actx, ok := tctx.(agent.CallbackContext)
            if !ok {
                log.Fatalf("tool.Context 型別錯誤")
            }
            s, err := actx.State().Get("user_action_count")
            if err != nil {
                log.Printf("無法取得 user_action_count: %v", err)
            }
            newCount := 1
            if c, ok := s.(int); ok {
                newCount = c + 1
            }
            if err := actx.State().Set("user_action_count", newCount); err != nil {
                log.Printf("無法設定 user_action_count: %v", err)
            }
            if err := actx.State().Set("temp:last_operation_status", "success from tool"); err != nil {
                log.Printf("無法設定 temp:last_operation_status: %v", err)
            }
            fmt.Println("Tool: 已透過 agent.CallbackContext 更新 state。")
            return struct{}{}, nil
        },
    )
    if err != nil {
        log.Fatalf("建立工具失敗: %v", err)
    }

    // 定義會呼叫該工具的 Agent
    modelTool, err := gemini.NewModel(ctx, modelID, nil)
    if err != nil {
        log.Fatalf("建立 Gemini 模型失敗: %v", err)
    }
    toolAgent, err := llmagent.New(llmagent.Config{
        Name:        "ToolAgent",
        Model:       modelTool,
        Instruction: "使用 update_action_count 工具。",
        Tools:       []tool.Tool{updateActionCountTool},
    })
    if err != nil {
        log.Fatalf("建立 tool agent 失敗: %v", err)
    }

    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          agent.Agent(toolAgent),
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("建立 runner 失敗: %v", err)
    }

    // 執行 agent 觸發工具
    userMessage := genai.NewContentFromText("請更新動作次數。", "user")
    for _, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
        if err != nil {
            log.Printf("Agent 錯誤: %v", err)
        }
    }

    // 檢查更新後的 state
    resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("取得 session 失敗: %v", err)
    }
    actionCount, _ := resp.Session.State().Get("user_action_count")
    fmt.Printf("工具執行後 state: user_action_count = %v\n", actionCount)
}
```

> Java

```java
// 在 Agent 回呼或工具方法中操作 State
import com.google.adk.agents.CallbackContext; // 或 ToolContext
// ... 其他 import ...

public class MyAgentCallbacks {
    public void onAfterAgent(CallbackContext callbackContext) {
        // 更新現有狀態值
        Integer count = (Integer) callbackContext.state().getOrDefault("user_action_count", 0);
        callbackContext.state().put("user_action_count", count + 1); // 累加使用者動作次數

        // 新增暫存狀態（temp: 前綴不會持久化）
        callbackContext.state().put("temp:last_operation_status", "success");

        // 這些狀態變更會自動被框架封裝進事件的 state_delta
        // ... 其餘回呼邏輯 ...
    }
}
```

</details>

**append_event** 做了什麼：

- 加入 Event 至 `session.events` 。
- 從事件的 actions 讀取 state_delta 。
- 將這些變更應用到由 SessionService 管理的狀態，正確處理前綴和基於服務類型的持續性。
- 更新會話的 last_update_time 。
- 確保多線程更新之 thread-safety。

---

## ⚠️ 重要警告：關於直接修改 State

避免直接修改從 SessionService 取得的 Session 物件上的 `session.state` 集合（dictionary/Map），尤其是在代理執行週期之外（即不是透過 `CallbackContext` 或 `ToolContext`）

例如，以下代碼是有問題的：
`retrieved_session = await session_service.get_session(...); retrieved_session.state['key'] = value`

**為什麼不應該這樣做：**

1.  **繞過事件歷史：** 變更不會記錄為 `Event`，失去審計追蹤。
2.  **破壞持久性：** 這種修改**極可能不會被儲存**，因為持久化服務依賴 `append_event` 來觸發存檔。
3.  **非執行緒安全：** 可能導致競爭條件（Race Conditions）。
4.  **忽略時間戳/更新：** 不更新 last_update_time 或觸發相關事件邏輯。

**建議：** 始終透過 `output_key`、`state_delta` 或 `Context` 物件來更新 State。僅將從 `SessionService` 獲取的 `session.state` 用於**讀取**。

## 狀態設計最佳實踐

| 原則             | 說明                                                               |
| ---------------- | ------------------------------------------------------------------ |
| 極簡主義         | 只儲存必要且動態的資料。                                           |
| 可序列化         | 使用基本且可序列化的型別。                                         |
| 描述性鍵名與前綴 | 採用清楚的名稱及適當前綴（如 `user:`、`app:`、`temp:` 或無前綴）。 |
| 淺層結構         | 儘量避免深層巢狀結構。                                             |
| 標準更新流程     | 所有狀態變更皆透過 `append_event` 處理。                           |

---

## 參考資源

- [Session 管理概覽](../sessions&memory/sessions.md) - 了解 Session 的生命週期。
