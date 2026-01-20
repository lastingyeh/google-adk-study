# 回調類型 (Types of Callbacks)
🔔 `更新日期：2026-01-20`

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

該框架提供不同類型的回調 (callbacks)，這些回調會在代理 (agent) 執行的各個階段觸發。了解每個回調何時觸發以及它接收什麼上下文，是有效使用它們的關鍵。

## 代理生命週期回調 (Agent Lifecycle Callbacks)

這些回調可用於繼承自 `BaseAgent` 的 *任何* 代理（包括 `LlmAgent`、`SequentialAgent`、`ParallelAgent`、`LoopAgent` 等）。

> [!NOTE]
    具體的方法名稱或返回類型可能會因 SDK 語言而略有不同（例如，在 Python 中返回 `None`，在 Java 中返回 `Optional.empty()` 或 `Maybe.empty()`）。詳情請參閱特定語言的 API 文件。

### 代理前置回調 (Before Agent Callback)

**觸發時機：** 在代理的 `_run_async_impl` (或 `_run_live_impl`) 方法執行 *之前* 立即調用。它在代理的 `InvocationContext` 創建之後，但在其核心邏輯開始 *之前* 運行。

**用途：** 非常適合設置僅用於此特定代理運行的資源或狀態、在執行開始前對對話狀態 (callback_context.state) 執行驗證檢查、記錄代理活動的入口點，或者在核心邏輯使用它之前修改調用上下文 (invocation context)。

<details>
<summary>程式碼範例</summary>

> Python

```python
# --- 設定步驟 ---
# 1. 安裝 ADK 套件：
# !pip install google-adk
# # 若在 colab/jupyter notebooks 請記得重啟 kernel

# 2. 設定 Gemini API 金鑰：
#    - 從 Google AI Studio 取得金鑰：https://aistudio.google.com/app/apikey
#    - 設為環境變數：
# import os
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" # <--- 請替換為你的實際金鑰
# # 其他驗證方式（如 Vertex AI）請參考：
# # https://google.github.io/adk-docs/agents/models/

# ADK 匯入
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner # 使用 InMemoryRunner
from google.genai import types # 用於 types.Content
from typing import Optional

# 定義模型名稱
GEMINI_2_FLASH="gemini-2.0-flash"

# --- 1. 定義回調函式 ---
def check_if_agent_should_run(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    紀錄進入點並檢查 session state 中的 'skip_llm_agent'。
    若為 True，回傳 Content 以跳過代理執行。
    若為 False 或未設置，回傳 None 允許執行。
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    print(f"\n[Callback] 進入代理: {agent_name} (Inv: {invocation_id})")
    print(f"[Callback] 目前狀態: {current_state}")

    # 檢查 session state 字典中的條件
    if current_state.get("skip_llm_agent", False):
        print(f"[Callback] 狀態條件 'skip_llm_agent=True' 成立：跳過代理 {agent_name}。")
        # 回傳 Content 以跳過代理執行
        return types.Content(
            parts=[types.Part(text=f"代理 {agent_name} 已因 before_agent_callback 狀態判斷而被跳過。")],
            role="model" # 指定 model 角色
        )
    else:
        print(f"[Callback] 狀態條件不成立：繼續執行代理 {agent_name}。")
        # 回傳 None 允許 LlmAgent 正常執行
        return None

# --- 2. 設定帶有回調的代理 ---
llm_agent_with_before_cb = LlmAgent(
    name="MyControlledAgent",
    model=GEMINI_2_FLASH,
    instruction="You are a concise assistant.",
    description="展示具狀態判斷 before_agent_callback 的 LLM 代理",
    before_agent_callback=check_if_agent_should_run # 指定回調
)

# --- 3. 使用 InMemoryRunner 建立 Runner 與 Session ---
async def main():
    app_name = "before_agent_demo"
    user_id = "test_user"
    session_id_run = "session_will_run"
    session_id_skip = "session_will_skip"

    # 使用 InMemoryRunner（內含 InMemorySessionService）
    runner = InMemoryRunner(agent=llm_agent_with_before_cb, app_name=app_name)
    # 取得 session service 以建立 session
    session_service = runner.session_service

    # 建立 session 1：代理會執行（預設空狀態）
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_run
        # 無初始 state，callback 檢查時 skip_llm_agent 為 False
    )

    # 建立 session 2：代理會被跳過（state 設 skip_llm_agent=True）
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_skip,
        state={"skip_llm_agent": True} # 設定狀態旗標
    )

    # --- 情境 1：callback 允許代理執行 ---
    print("\n" + "="*20 + f" 情境 1：Session '{session_id_run}' 執行代理（應正常執行） " + "="*20)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_run,
        new_message=types.Content(role="user", parts=[types.Part(text="Hello, please respond.")])
    ):
        # 印出最終輸出（來自 LLM 或 callback 覆蓋）
        if event.is_final_response() and event.content:
            print(f"最終輸出: [{event.author}] {event.content.parts[0].text.strip()}")
        elif event.is_error():
             print(f"錯誤事件: {event.error_details}")

    # --- 情境 2：callback 攔截並跳過代理 ---
    print("\n" + "="*20 + f" 情境 2：Session '{session_id_skip}' 執行代理（應被跳過） " + "="*20)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_skip,
        new_message=types.Content(role="user", parts=[types.Part(text="This message won't reach the LLM.")])
    ):
         # 印出最終輸出（來自 LLM 或 callback 覆蓋）
         if event.is_final_response() and event.content:
            print(f"最終輸出: [{event.author}] {event.content.parts[0].text.strip()}")
         elif event.is_error():
             print(f"錯誤事件: {event.error_details}")

# --- 4. 執行 ---
# 在 Python 腳本中：
# import asyncio
# if __name__ == "__main__":
#     # 請確認已設 GOOGLE_API_KEY 環境變數（若未用 Vertex AI 驗證）
#     # 或已設定 Application Default Credentials (ADC) 用於 Vertex AI
#     asyncio.run(main())

# 在 Jupyter Notebook 或類似環境：
await main()
```

> typescript

```typescript
import {
    LlmAgent,
    InMemoryRunner,
    CallbackContext,
    isFinalResponse,
} from "@google/adk";
import { Content, createUserContent } from "@google/genai";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "before_agent_callback_app";
const USER_ID = "test_user_before_agent";
const SESSION_ID_RUN = "session_will_run";
const SESSION_ID_SKIP = "session_will_skip";

// --- 1. 定義回調函式 ---
function checkIfAgentShouldRun(
    callbackContext: CallbackContext
): Content | undefined {
    /**
     * 紀錄進入點並檢查 session state 中的 'skip_llm_agent'。
     * 若為 true，回傳 Content 以跳過代理執行。
     * 若為 false 或未設置，回傳 undefined 允許正常執行。
     */
    const agentName = callbackContext.agentName;
    const invocationId = callbackContext.invocationId;
    const currentState = callbackContext.state;

    console.log(`\n[回調] 進入代理：${agentName}（Inv：${invocationId}）`);
    console.log(`[回調] 目前狀態：`, currentState);

    // 檢查 session state 中的條件
    if (currentState.get("skip_llm_agent") === true) {
        console.log(
            `[回調] 狀態條件 'skip_llm_agent=true' 成立：跳過代理 ${agentName}。`
        );
        // 回傳 Content 以跳過代理執行
        return {
            parts: [
                {
                    text: `代理 ${agentName} 已因 before_agent_callback 的狀態判斷而被跳過。`,
                },
            ],
            role: "model", // 指定 model 角色作為覆寫回應
        };
    } else {
        console.log(`[回調] 狀態條件不成立：繼續執行代理 ${agentName}。`);
        // 回傳 undefined 以允許 LlmAgent 正常執行
        return undefined;
    }
}

// --- 2. 設定帶有回調的 Agent ---
const llmAgentWithBeforeCb = new LlmAgent({
    name: "MyControlledAgent",
    model: MODEL_NAME,
    instruction: "You are a concise assistant.",
    description: "示範具狀態判斷 before_agent_callback 的 LLM 代理",
    beforeAgentCallback: checkIfAgentShouldRun, // 指定回調
});

// --- 3. 使用 InMemoryRunner 建立 Runner 與 Sessions ---
async function main() {
    // 使用 InMemoryRunner（內含 InMemorySessionService）
    const runner = new InMemoryRunner({
        agent: llmAgentWithBeforeCb,
        appName: APP_NAME,
    });

    // 建立 session 1：代理會執行（預設空狀態）
    await runner.sessionService.createSession({
        appName: APP_NAME,
        userId: USER_ID,
        sessionId: SESSION_ID_RUN,
        // 無初始 state，callback 檢查時 skip_llm_agent 為 false
    });

    // 建立 session 2：代理會被跳過（state 設 skip_llm_agent=true）
    await runner.sessionService.createSession({
        appName: APP_NAME,
        userId: USER_ID,
        sessionId: SESSION_ID_SKIP,
        state: { skip_llm_agent: true }, // 在此設定狀態旗標
    });

    // --- 情境 1：callback 允許代理執行 ---
    console.log(
        `\n==================== 情境 1：以 Session「${SESSION_ID_RUN}」執行代理（應正常執行） ====================`
    );
    const eventsRun = runner.runAsync({
        userId: USER_ID,
        sessionId: SESSION_ID_RUN,
        newMessage: createUserContent("Hello, please respond."),
    });

    for await (const event of eventsRun) {
        // 印出最終輸出（來自 LLM 或 callback 覆寫）
        if (isFinalResponse(event) && event.content?.parts?.length) {
            const finalResponse = event.content.parts
                .map((part: any) => part.text ?? "")
                .join("");
            console.log(`最終輸出：[${event.author}] ${finalResponse.trim()}`);
        } else if (event.errorMessage) {
            console.log(`錯誤事件：${event.errorMessage}`);
        }
    }

    // --- 情境 2：callback 攔截並跳過代理 ---
    console.log(
        `\n==================== 情境 2：以 Session「${SESSION_ID_SKIP}」執行代理（應被跳過） ====================`
    );
    const eventsSkip = runner.runAsync({
        userId: USER_ID,
        sessionId: SESSION_ID_SKIP,
        newMessage: createUserContent("This message won't reach the LLM."),
    });

    for await (const event of eventsSkip) {
        // 印出最終輸出（來自 LLM 或 callback 覆寫）
        if (isFinalResponse(event) && event.content?.parts?.length) {
            const finalResponse = event.content.parts
                .map((part: any) => part.text ?? "")
                .join("");
            console.log(`最終輸出：[${event.author}] ${finalResponse.trim()}`);
        } else if (event.errorMessage) {
            console.log(`錯誤事件：${event.errorMessage}`);
        }
    }
}

// --- 4. 執行 ---
main();
```

> go

```go
package main

import (
    "context"
    "fmt"
    "log"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/genai"
)

// 1. 定義回調函式
func onBeforeAgent(ctx agent.CallbackContext) (*genai.Content, error) {
    agentName := ctx.AgentName()
    log.Printf("[回調] 進入代理：%s", agentName)

    if skip, _ := ctx.State().Get("skip_llm_agent"); skip == true {
        log.Printf("[回調] 狀態條件成立：跳過代理 %s", agentName)
        return genai.NewContentFromText(
                fmt.Sprintf("代理 %s 已被 before_agent_callback 跳過。", agentName),
                genai.RoleModel,
            ),
            nil
    }

    log.Printf("[回調] 狀態條件不成立：執行代理 %s", agentName)
    return nil, nil
}

// 2. 定義設定並執行代理（含回調）的函式
func runBeforeAgentExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("致命錯誤：建立模型失敗：%v", err)
    }

    // 3. 在代理設定中註冊回調
    llmCfg := llmagent.Config{
        Name:                 "AgentWithBeforeAgentCallback",
        BeforeAgentCallbacks: []agent.BeforeAgentCallback{onBeforeAgent},
        Model:                geminiModel,
        Instruction:          "你是一個簡潔的助理。",
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("致命錯誤：建立代理失敗：%v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("致命錯誤：建立 Runner 失敗：%v", err)
    }

    // 4. 執行情境以示範回調行為
    log.Println("--- 情境 1：代理應正常執行 ---")
    runScenario(ctx, r, sessionService, appName, "session_normal", nil, "你好，世界！")

    log.Println("\n--- 情境 2：代理應被跳過 ---")
    runScenario(ctx, r, sessionService, appName, "session_skip", map[string]any{"skip_llm_agent": true}, "這段應該會被跳過。")
}
```

> java

```java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.CallbackContext;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.sessions.State;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class BeforeAgentCallbackExample {

    private static final String APP_NAME = "AgentWithBeforeAgentCallback";
    private static final String USER_ID = "test_user_456";
    private static final String SESSION_ID = "session_id_123";
    private static final String MODEL_NAME = "gemini-2.0-flash";

    public static void main(String[] args) {
        BeforeAgentCallbackExample callbackAgent = new BeforeAgentCallbackExample();
        callbackAgent.defineAgent("請寫一篇關於貓的文章");
    }

    // --- 1. 定義回調函式 ---
    /**
     * 紀錄進入點並檢查 session state 中的「skip_llm_agent」。
     * 若為 true，回傳 Content 以跳過代理執行；
     * 若為 false 或未設置，回傳 Maybe.empty() 允許正常執行。
     */
    public Maybe<Content> checkIfAgentShouldRun(CallbackContext callbackContext) {
        String agentName = callbackContext.agentName();
        String invocationId = callbackContext.invocationId();
        State currentState = callbackContext.state();

        System.out.printf("%n[回調] 進入代理：%s（Inv：%s）%n", agentName, invocationId);
        System.out.printf("[回調] 目前狀態：%s%n", currentState.entrySet());

        // 檢查 session state 中的條件
        if (Boolean.TRUE.equals(currentState.get("skip_llm_agent"))) {
            System.out.printf("[回調] 狀態條件「skip_llm_agent=true」成立：跳過代理 %s%n", agentName);

            // 回傳 Content 以跳過代理主流程
            return Maybe.just(
                    Content.fromParts(
                            Part.fromText(
                                    String.format("代理 %s 已因 before_agent_callback 的狀態判斷而被跳過。", agentName))));
        }

        System.out.printf("[回調] 狀態條件不成立：繼續執行代理 %s%n", agentName);

        // 回傳空值以允許 LlmAgent 正常執行
        return Maybe.empty();
    }

    public void defineAgent(String prompt) {
        // --- 2. 設定帶有回調的 Agent ---
        BaseAgent llmAgentWithBeforeCallback =
                LlmAgent.builder()
                        .model(MODEL_NAME)
                        .name(APP_NAME)
                        .instruction("你是一個簡潔的助理。")
                        .description("示範具狀態判斷 before_agent_callback 的 LLM 代理")
                        // 也可以使用同步版本的回調：beforeAgentCallbackSync
                        .beforeAgentCallback(this::checkIfAgentShouldRun)
                        .build();

        // --- 3. 使用 InMemoryRunner 建立 Runner 與 Sessions ---

        // 使用 InMemoryRunner（內含 InMemorySessionService）
        InMemoryRunner runner = new InMemoryRunner(llmAgentWithBeforeCallback, APP_NAME);

        // 情境 1：初始狀態為 null，callback 檢查時 skip_llm_agent 視為 false（應正常執行）
        runAgent(runner, null, prompt);

        // 情境 2：代理會被跳過（state 設 skip_llm_agent=true）
        runAgent(runner, new ConcurrentHashMap<>(Map.of("skip_llm_agent", true)), prompt);
    }

    public void runAgent(
            InMemoryRunner runner, ConcurrentHashMap<String, Object> initialState, String prompt) {

        // InMemoryRunner 會自動建立 session service；透過 service 建立 session
        Session session =
                runner
                        .sessionService()
                        .createSession(APP_NAME, USER_ID, initialState, SESSION_ID)
                        .blockingGet();

        Content userMessage = Content.fromParts(Part.fromText(prompt));

        // 執行代理
        Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

        // 印出最終輸出（來自 LLM 或 callback 覆寫）
        eventStream.blockingForEach(
                event -> {
                    if (event.finalResponse()) {
                        System.out.println(event.stringifyContent());
                    }
                });
    }
}
```

</details>

**關於 `before_agent_callback` 範例的說明：**

* **展示內容：** 此範例演示了 `before_agent_callback`。此回調在給定請求的代理主處理邏輯開始 *之前* 運行。
* **運作方式：** 回調函數 (`check_if_agent_should_run`) 查看對話狀態中的一個標記 (`skip_llm_agent`)。
    * 如果標記為 `True`，回調將返回一個 `types.Content` 對象。這告訴 ADK 框架完全 **跳過** 代理的主要執行，並將回調返回的內容作為最終響應。
    * 如果標記為 `False` (或未設置)，回調將返回 `None` 或空對象。這告訴 ADK 框架 **繼續** 執行代理的正常流程（在這種情況下是調用 LLM）。
* **預期結果：** 您將看到兩種情況：
    1. 在狀態為 `skip_llm_agent: True` 的對話中，代理的 LLM 調用被繞過，輸出直接來自回調（"Agent... skipped..."）。
    2. 在沒有該狀態標記的對話中，回調允許代理運行，您會看到來自 LLM 的實際響應（例如 "Hello!"）。
* **理解回調：** 這突顯了 `before_` 回調如何充當 **守門員 (gatekeepers)**，允許您在重大步驟 *之前* 攔截執行，並可能根據檢查（如狀態、輸入驗證、權限）阻止它。


### 代理後置回調 (After Agent Callback)

**觸發時機：** 在代理的 `_run_async_impl` (或 `_run_live_impl`) 方法成功完成後 *立即* 調用。如果代理因為 `before_agent_callback` 返回內容而被跳過，或者在代理運行期間設置了 `end_invocation`，則該回調 *不會* 運行。

**用途：** 用於清理任務、執行後驗證、記錄代理活動的完成、修改最終狀態或增強/替換代理的最終輸出。

<details>
<summary>程式碼範例</summary>

> Python

```python
# --- 設定步驟 ---
# 1. 安裝 ADK 套件：
# !pip install google-adk
# # 若在 colab/jupyter notebooks 請記得重啟 kernel

# 2. 設定 Gemini API 金鑰：
#    - 從 Google AI Studio 取得金鑰：https://aistudio.google.com/app/apikey
#    - 設為環境變數：
# import os
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" # <--- 請替換為你的實際金鑰
# # 其他驗證方式（如 Vertex AI）請參考：
# # https://google.github.io/adk-docs/agents/models/

# ADK 匯入
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner  # 使用 InMemoryRunner
from google.genai import types  # 用於 types.Content
from typing import Optional

# 定義模型名稱
GEMINI_2_FLASH = "gemini-2.0-flash"

# --- 1. 定義回調函式 ---
def modify_output_after_agent(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    紀錄代理結束點並檢查 session state 中的「add_concluding_note」。
    若為 True，回傳新的 Content 以「取代」代理原始輸出。
    若為 False 或未設置，回傳 None，讓代理原始輸出繼續使用。
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    print(f"\n[回調] 離開代理：{agent_name}（Inv：{invocation_id}）")
    print(f"[回調] 目前狀態：{current_state}")

    # 範例：檢查狀態以決定是否修改最終輸出
    if current_state.get("add_concluding_note", False):
        print(
            f"[回調] 狀態條件「add_concluding_note=True」成立：取代代理 {agent_name} 的輸出。"
        )
        # 回傳 Content 以「取代」代理自身輸出
        return types.Content(
            parts=[
                types.Part(
                    text="由 after_agent_callback 加上的結語註記（已取代原始輸出）。"
                )
            ],
            role="model",  # 指定 model 角色作為覆寫回應
        )
    else:
        print(f"[回調] 狀態條件不成立：使用代理 {agent_name} 的原始輸出。")
        # 回傳 None：使用代理在此回調之前產生的輸出
        return None


# --- 2. 設定帶有回調的代理 ---
llm_agent_with_after_cb = LlmAgent(
    name="MySimpleAgentWithAfter",
    model=GEMINI_2_FLASH,
    instruction="你是一個簡單的代理。只要回覆「處理完成！」即可。",
    description="示範 after_agent_callback 用於修改輸出的 LLM 代理",
    after_agent_callback=modify_output_after_agent,  # 指定回調
)


# --- 3. 使用 InMemoryRunner 建立 Runner 與 Sessions ---
async def main():
    app_name = "after_agent_demo"
    user_id = "test_user_after"
    session_id_normal = "session_run_normally"
    session_id_modify = "session_modify_output"

    # 使用 InMemoryRunner（內含 InMemorySessionService）
    runner = InMemoryRunner(agent=llm_agent_with_after_cb, app_name=app_name)
    # 取得 session service 以建立 sessions
    session_service = runner.session_service

    # 建立 session 1：輸出不做修改（預設空狀態）
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_normal
        # 無初始 state，callback 檢查時 add_concluding_note 為 False
    )

    # 建立 session 2：輸出會被回調取代（state 設 add_concluding_note=True）
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_modify,
        state={"add_concluding_note": True},  # 設定狀態旗標
    )

    # --- 情境 1：callback 允許使用代理原始輸出 ---
    print(
        "\n"
        + "=" * 20
        + f" 情境 1：以 Session「{session_id_normal}」執行代理（應使用原始輸出） "
        + "=" * 20
    )
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_normal,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="請幫我處理一下。")],
        ),
    ):
        # 印出最終輸出（來自 LLM 或 callback 覆寫）
        if event.is_final_response() and event.content:
            print(f"最終輸出：[{event.author}] {event.content.parts[0].text.strip()}")
        elif event.is_error():
            print(f"錯誤事件：{event.error_details}")

    # --- 情境 2：callback 取代代理輸出 ---
    print(
        "\n"
        + "=" * 20
        + f" 情境 2：以 Session「{session_id_modify}」執行代理（應取代輸出） "
        + "=" * 20
    )
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_modify,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="請處理並加上結語。")],
        ),
    ):
        # 印出最終輸出（來自 LLM 或 callback 覆寫）
        if event.is_final_response() and event.content:
            print(f"最終輸出：[{event.author}] {event.content.parts[0].text.strip()}")
        elif event.is_error():
            print(f"錯誤事件：{event.error_details}")


# --- 4. 執行 ---
# 在 Python 腳本中：
# import asyncio
# if __name__ == "__main__":
#     # 請確認已設 GOOGLE_API_KEY 環境變數（若未用 Vertex AI 驗證）
#     # 或已設定 Application Default Credentials (ADC) 用於 Vertex AI
#     asyncio.run(main())

# 在 Jupyter Notebook 或類似環境：
await main()
```

> typescript

```typescript
import {
    LlmAgent,
    CallbackContext,
    isFinalResponse,
    InMemoryRunner,
} from "@google/adk";
import { createUserContent } from "@google/genai";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "after_agent_callback_app";
const USER_ID = "test_user_after_agent";
const SESSION_NORMAL_ID = "session_run_normally_ts";
const SESSION_MODIFY_ID = "session_modify_output_ts";

// --- 1. 定義回調函式 ---
/**
 * 紀錄代理結束點並檢查 session state 中的「add_concluding_note」。
 * 若為 true，回傳新的 Content 以「取代」代理原始輸出。
 * 若為 false 或未設置，回傳 undefined，讓代理原始輸出繼續使用。
 */
function modifyOutputAfterAgent(context: CallbackContext): any {
    const agentName = context.agentName;
    const invocationId = context.invocationId;
    const currentState = context.state;

    console.log(`[回調] 離開代理：${agentName}（Inv：${invocationId}）`);
    console.log(`[回調] 目前狀態：`, currentState);

    // 範例：檢查狀態以決定是否修改最終輸出
    if (currentState.get("add_concluding_note") === true) {
        console.log(
            `[回調] 狀態條件「add_concluding_note=true」成立：取代代理 ${agentName} 的輸出。`
        );

        // 回傳 Content 以「取代」代理自身輸出（以 model 角色覆寫回應）
        return {
            role: "model",
            parts: [
                {
                    text: "由 after_agent_callback 加上的結語註記（已取代原始輸出）。",
                },
            ],
        };
    } else {
        console.log(`[回調] 狀態條件不成立：使用代理 ${agentName} 的原始輸出。`);
        // 回傳 undefined：使用代理在此回調之前產生的輸出
        return undefined;
    }
}

// --- 2. 設定帶有回調的 Agent ---
const llmAgentWithAfterCb = new LlmAgent({
    name: "MySimpleAgentWithAfter",
    model: MODEL_NAME,
    instruction: '你是一個簡單的代理。只要回覆「處理完成！」即可。',
    description: "示範 after_agent_callback 用於修改輸出的 LLM 代理",
    afterAgentCallback: modifyOutputAfterAgent, // 指定回調
});

// --- 3. 執行代理 ---
async function main() {
    const runner = new InMemoryRunner({
        agent: llmAgentWithAfterCb,
        appName: APP_NAME,
    });

    // 建立 session 1：輸出不做修改（預設空狀態）
    await runner.sessionService.createSession({
        appName: APP_NAME,
        userId: USER_ID,
        sessionId: SESSION_NORMAL_ID,
    });

    // 建立 session 2：輸出會被回調取代（state 設 add_concluding_note=true）
    await runner.sessionService.createSession({
        appName: APP_NAME,
        userId: USER_ID,
        sessionId: SESSION_MODIFY_ID,
        state: { add_concluding_note: true }, // 在此設定狀態旗標
    });

    // --- 情境 1：callback 允許使用代理原始輸出 ---
    console.log(
        `==================== 情境 1：以 Session「${SESSION_NORMAL_ID}」執行代理（應使用原始輸出） ====================`
    );
    const eventsNormal = runner.runAsync({
        userId: USER_ID,
        sessionId: SESSION_NORMAL_ID,
        newMessage: createUserContent("請幫我處理一下。"),
    });

    for await (const event of eventsNormal) {
        if (isFinalResponse(event) && event.content?.parts?.length) {
            const finalResponse = event.content.parts
                .map((part: any) => part.text ?? "")
                .join("");
            console.log(`最終輸出：[${event.author}] ${finalResponse.trim()}`);
        } else if (event.errorMessage) {
            console.log(`錯誤事件：${event.errorMessage}`);
        }
    }

    // --- 情境 2：callback 取代代理輸出 ---
    console.log(
        `==================== 情境 2：以 Session「${SESSION_MODIFY_ID}」執行代理（應取代輸出） ====================`
    );
    const eventsModify = runner.runAsync({
        userId: USER_ID,
        sessionId: SESSION_MODIFY_ID,
        newMessage: createUserContent("請處理並加上結語。"),
    });

    for await (const event of eventsModify) {
        if (isFinalResponse(event) && event.content?.parts?.length) {
            const finalResponse = event.content.parts
                .map((part: any) => part.text ?? "")
                .join("");
            console.log(`最終輸出：[${event.author}] ${finalResponse.trim()}`);
        } else if (event.errorMessage) {
            console.log(`錯誤事件：${event.errorMessage}`);
        }
    }
}

main();
```

> go

```go
package main

import (
    "context"
    "log"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/genai"
)

func onAfterAgent(ctx agent.CallbackContext) (*genai.Content, error) {
    agentName := ctx.AgentName()
    invocationID := ctx.InvocationID()
    state := ctx.State()

    log.Printf("\n[回調] 離開代理：%s（Inv：%s）", agentName, invocationID)
    log.Printf("[回調] 目前狀態：%v", state)

    if addNote, _ := state.Get("add_concluding_note"); addNote == true {
        log.Printf("[回調] 狀態條件「add_concluding_note=true」成立：取代代理 %s 的輸出。", agentName)
        return genai.NewContentFromText(
            "由 after_agent_callback 加上的結語註記（已取代原始輸出）。",
            genai.RoleModel,
        ), nil
    }

    log.Printf("[回調] 狀態條件不成立：使用代理 %s 的原始輸出。", agentName)
    return nil, nil
}

func runAfterAgentExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("致命錯誤：建立模型失敗：%v", err)
    }

    llmCfg := llmagent.Config{
        Name:                "AgentWithAfterAgentCallback",
        AfterAgentCallbacks: []agent.AfterAgentCallback{onAfterAgent},
        Model:               geminiModel,
        Instruction:         "你是一個簡單的代理。只要回覆「處理完成！」即可。",
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("致命錯誤：建立代理失敗：%v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{
        AppName:         appName,
        Agent:          testAgent,
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("致命錯誤：建立 Runner 失敗：%v", err)
    }

    log.Println("--- 情境 1：應使用原始輸出 ---")
    runScenario(ctx, r, sessionService, appName, "session_normal", nil, "請幫我處理一下。")

    log.Println("\n--- 情境 2：應取代輸出 ---")
    runScenario(ctx, r, sessionService, appName, "session_modify", map[string]any{"add_concluding_note": true}, "請處理並加上結語。")
}
```

> java

```java
import com.google.adk.agents.CallbackContext;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.State;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class AfterAgentCallbackExample {

    // --- 常數 ---
    private static final String APP_NAME = "after_agent_demo";
    private static final String USER_ID = "test_user_after";
    private static final String SESSION_ID_NORMAL = "session_run_normally";
    private static final String SESSION_ID_MODIFY = "session_modify_output";
    private static final String MODEL_NAME = "gemini-2.0-flash";

    public static void main(String[] args) {
        AfterAgentCallbackExample demo = new AfterAgentCallbackExample();
        demo.defineAgentAndRunScenarios();
    }

    // --- 1. 定義回調函式 ---
    /**
     * 紀錄離開代理 (agent) 的時間點，並檢查 session state 中的「add_concluding_note」。
     *
     * <p>若為 true，回傳新的 Content 以「取代」代理原始輸出。
     *
     * <p>若為 false 或未設置，回傳 Maybe.empty()，讓代理原始輸出繼續使用。
     */
    public Maybe<Content> modifyOutputAfterAgent(CallbackContext callbackContext) {
        String agentName = callbackContext.agentName();
        String invocationId = callbackContext.invocationId();
        State currentState = callbackContext.state();

        System.out.printf("%n[回調] 離開代理：%s（Inv：%s）%n", agentName, invocationId);
        System.out.printf("[回調] 目前狀態：%s%n", currentState.entrySet());

        Object addNoteFlag = currentState.get("add_concluding_note");

        // 範例：檢查狀態以決定是否修改最終輸出
        if (Boolean.TRUE.equals(addNoteFlag)) {
            System.out.printf(
                    "[回調] 狀態條件「add_concluding_note=true」成立：取代代理 %s 的輸出。%n", agentName);

            // 回傳 Content 以「取代」代理自身輸出
            return Maybe.just(
                    Content.builder()
                            .parts(
                                    List.of(
                                            Part.fromText(
                                                    "由 after_agent_callback 加上的結語註記（已取代原始輸出）。")))
                            .role("model") // 指定 model 角色作為覆寫回應
                            .build());

        } else {
            System.out.printf("[回調] 狀態條件不成立：使用代理 %s 的原始輸出。%n", agentName);
            // 回傳空值：使用代理在此回調之前產生的輸出
            return Maybe.empty();
        }
    }

    // --- 2. 設定帶有回調的 Agent ---
    public void defineAgentAndRunScenarios() {
        LlmAgent llmAgentWithAfterCb =
                LlmAgent.builder()
                        .name(APP_NAME)
                        .model(MODEL_NAME)
                        .description("示範 after_agent_callback 用於修改輸出的 LLM 代理")
                        .instruction("你是一個簡單的代理。只要回覆「處理完成！」即可。")
                        .afterAgentCallback(this::modifyOutputAfterAgent) // 在此指定回調
                        .build();

        // --- 3. 使用 InMemoryRunner 建立 Runner 與 Sessions ---
        // 使用 InMemoryRunner（內含 InMemorySessionService）
        InMemoryRunner runner = new InMemoryRunner(llmAgentWithAfterCb, APP_NAME);

        // --- 情境 1：callback 允許使用代理原始輸出 ---
        System.out.printf(
                "%n%s 情境 1：執行代理（應使用原始輸出） %s%n", "=".repeat(20), "=".repeat(20));
        // 無初始 state，callback 檢查時 add_concluding_note 視為 false
        runScenario(
                runner,
                llmAgentWithAfterCb.name(), // 使用 agent name 以維持 runner 的 appName 一致性
                SESSION_ID_NORMAL,
                null,
                "請幫我處理一下。");

        // --- 情境 2：callback 取代代理輸出 ---
        System.out.printf(
                "%n%s 情境 2：執行代理（應取代輸出） %s%n", "=".repeat(20), "=".repeat(20));
        Map<String, Object> modifyState = new HashMap<>();
        modifyState.put("add_concluding_note", true); // 設定狀態旗標
        runScenario(
                runner,
                llmAgentWithAfterCb.name(), // 使用 agent name 以維持 runner 的 appName 一致性
                SESSION_ID_MODIFY,
                new ConcurrentHashMap<>(modifyState),
                "請處理並加上結語。");
    }

    // --- 3. 執行單一情境的方法 ---
    public void runScenario(
            InMemoryRunner runner,
            String appName,
            String sessionId,
            ConcurrentHashMap<String, Object> initialState,
            String userQuery) {

        // 使用 runner 內建的 session service 建立 session
        runner.sessionService().createSession(appName, USER_ID, initialState, sessionId).blockingGet();

        System.out.printf("執行情境：session=%s，初始狀態=%s%n", sessionId, initialState);
        Content userMessage =
                Content.builder().role("user").parts(List.of(Part.fromText(userQuery))).build();

        Flowable<Event> eventStream = runner.runAsync(USER_ID, sessionId, userMessage);

        // 印出最終輸出
        eventStream.blockingForEach(
                event -> {
                    if (event.finalResponse() && event.content().isPresent()) {
                        String author = event.author() != null ? event.author() : "UNKNOWN";
                        String text =
                                event
                                        .content()
                                        .flatMap(Content::parts)
                                        .filter(parts -> !parts.isEmpty())
                                        .map(parts -> parts.get(0).text().orElse("").trim())
                                        .orElse("[最終回應中沒有文字內容]");
                        System.out.printf("最終輸出（%s）：[%s] %s%n", sessionId, author, text);
                    } else if (event.errorCode().isPresent()) {
                        System.out.printf(
                                "錯誤事件（%s）：%s%n", sessionId, event.errorMessage().orElse("未知錯誤"));
                    }
                });
    }
}
```

</details>

**關於 `after_agent_callback` 範例的說明：**

* **展示內容：** 此範例演示了 `after_agent_callback`。此回調在代理的主要處理邏輯完成並產生結果後 *立即* 運行，但在該結果被最終確定並返回 *之前*。
* **運作方式：** 回調函數 (`modify_output_after_agent`) 檢查對話狀態中的一個標記 (`add_concluding_note`)。
    * 如果標記為 `True`，回調將返回一個 *新的* `types.Content` 對象。這告訴 ADK 框架使用回調返回的內容 **替換** 代理的原始輸出。
    * 如果標記為 `False` (或未設置)，回調將返回 `None` 或空對象。這告訴 ADK 框架 **使用** 代理生成的原始輸出。
*   **預期結果：** 您將看到兩種情況：
    1. 在沒有 `add_concluding_note: True` 狀態的對話中，回調允許使用代理的原始輸出（"Processing complete!"）。
    2. 在具有該狀態標記的對話中，回調攔截代理的原始輸出，並將其替換為自己的消息（"Concluding note added..."）。
* **理解回調：** 這突顯了 `after_` 回調如何允許 **後處理 (post-processing)** 或 **修改 (modification)**。您可以檢查步驟的結果（代理的運行）並根據您的邏輯決定是讓它通過、更改它還是完全替換它。

## LLM 交互回調 (LLM Interaction Callbacks)

這些回調是 `LlmAgent` 特有的，並在與大語言模型 (LLM) 交互前後提供掛鉤 (hooks)。

### 模型前置回調 (Before Model Callback)

**觸發時機：** 在 `LlmAgent` 流程中將 `generate_content_async` (或同等) 請求發送到 LLM 之前調用。

**用途：** 允許檢查和修改發往 LLM 的請求。用例包括添加動態指令、根據狀態注入少樣本範例 (few-shot examples)、修改模型配置、實施護欄 (guardrails)（如過濾髒話）或實施請求級別的緩存。

**返回值影響：**
如果回調返回 `None`（或 Java 中的 `Maybe.empty()` 對象），LLM 將繼續其正常工作流程。如果回調返回 `LlmResponse` 對象，則對 LLM 的調用將被 **跳過**。返回的 `LlmResponse` 將直接被使用，就像它來自模型一樣。這對於實施護欄或緩存非常強大。

<details>
<summary>程式碼範例</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.runners import Runner
from typing import Optional
from google.genai import types
from google.adk.sessions import InMemorySessionService

GEMINI_2_FLASH = "gemini-2.0-flash"

# --- 定義回調函式 ---
def simple_before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """檢查/修改 LLM request，或直接跳過本次模型呼叫。"""
    agent_name = callback_context.agent_name
    print(f"[回調] 即將呼叫模型（agent）：{agent_name}")

    # 檢查 request.contents 中最後一則使用者訊息
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == "user":
        if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[回調] 最後一則使用者訊息：'{last_user_message}'")

    # --- 修改範例 ---
    # 在 system instruction 前加上前綴
    original_instruction = (
        llm_request.config.system_instruction
        or types.Content(role="system", parts=[])
    )
    prefix = "[由回調修改] "

    # 確保 system_instruction 為 Content 且 parts 存在
    if not isinstance(original_instruction, types.Content):
        original_instruction = types.Content(
            role="system",
            parts=[types.Part(text=str(original_instruction))],
        )
    if not original_instruction.parts:
        original_instruction.parts.append(types.Part(text=""))

    modified_text = prefix + (original_instruction.parts[0].text or "")
    original_instruction.parts[0].text = modified_text
    llm_request.config.system_instruction = original_instruction
    print(f"[回調] 已修改 system instruction：'{modified_text}'")

    # --- 阻擋/跳過範例 ---
    # 若最後一則使用者訊息包含 "BLOCK"，則跳過模型呼叫
    if "BLOCK" in last_user_message.upper():
        print("[回調] 偵測到關鍵字 'BLOCK'，跳過本次 LLM 呼叫。")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="此 LLM 呼叫已被 before_model_callback 阻擋。")],
            )
        )

    print("[回調] 未觸發阻擋條件，繼續呼叫 LLM。")
    return None


# 建立 LlmAgent 並指定回調
my_llm_agent = LlmAgent(
    name="ModelCallbackAgent",
    model=GEMINI_2_FLASH,
    instruction="你是一位樂於助人的助理。",  # 基礎 instruction
    description="示範 before_model_callback 的 LLM 代理",
    before_model_callback=simple_before_model_modifier,
)

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Session 與 Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# 互動呼叫
async def call_agent_async(query: str):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理回應：", final_response)


# 注意：在 Colab 可直接在頂層使用 `await`。
# 若在一般 Python 腳本執行，請使用 asyncio.run() 或自行管理 event loop。
await call_agent_async("請寫一個關於 BLOCK 的笑話")
```

> typescript

```typescript
import {
  LlmAgent,
  InMemoryRunner,
  CallbackContext,
  isFinalResponse,
} from "@google/adk";
import { createUserContent } from "@google/genai";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "before_model_callback_app";
const USER_ID = "test_user_before_model";
const SESSION_ID_BLOCK = "session_block_model_call";
const SESSION_ID_NORMAL = "session_normal_model_call";

// --- 定義回調函式 ---
function simpleBeforeModelModifier({
  context,
  request,
}: {
  context: CallbackContext;
  request: any;
}): any | undefined {
  console.log(`[回調] 即將呼叫模型（agent）：${context.agentName}`);

  // 取得 request.contents 最後一則使用者訊息
  const lastUserMessage = request.contents?.at(-1)?.parts?.[0]?.text ?? "";
  console.log(`[回調] 最後一則使用者訊息：'${lastUserMessage}'`);

  // --- 修改範例 ---
  // 在 system instruction 前加上前綴（深拷貝避免修改到原始 config 物件）
  const modifiedConfig = JSON.parse(JSON.stringify(request.config));
  const originalInstructionText =
    modifiedConfig.systemInstruction?.parts?.[0]?.text ?? "";
  const prefix = "[由回調修改] ";
  modifiedConfig.systemInstruction = {
    role: "system",
    parts: [{ text: prefix + originalInstructionText }],
  };
  request.config = modifiedConfig;
  console.log(
    `[回調] 已修改 system instruction：'${modifiedConfig.systemInstruction.parts[0].text}'`
  );

  // --- 阻擋/跳過範例 ---
  if (lastUserMessage.toUpperCase().includes("BLOCK")) {
    console.log("[回調] 偵測到關鍵字 'BLOCK'，跳過本次 LLM 呼叫。");
    return {
      content: {
        role: "model",
        parts: [{ text: "此 LLM 呼叫已被 before_model_callback 阻擋。" }],
      },
    };
  }

  console.log("[回調] 未觸發阻擋條件，繼續呼叫 LLM。");
  return undefined;
}

// --- 建立 LlmAgent 並指定回調 ---
const myLlmAgent = new LlmAgent({
  name: "ModelCallbackAgent",
  model: MODEL_NAME,
  instruction: "你是一位樂於助人的助理。", // 基礎 instruction
  description: "示範 before_model_callback 的 LLM 代理",
  beforeModelCallback: simpleBeforeModelModifier,
});

// --- 代理互動邏輯 ---
async function callAgentAndPrint(
  runner: InMemoryRunner,
  query: string,
  sessionId: string
) {
  console.log(`\n>>> 呼叫代理，輸入："${query}"`);

  let finalResponseContent = "未收到最終回應。";
  const events = runner.runAsync({
    userId: USER_ID,
    sessionId,
    newMessage: createUserContent(query),
  });

  for await (const event of events) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      finalResponseContent = event.content.parts
        .map((part: { text?: string }) => part.text ?? "")
        .join("");
    }
  }
  console.log("<<< 代理回應：", finalResponseContent);
}

// --- 執行示範 ---
async function main() {
  const runner = new InMemoryRunner({ agent: myLlmAgent, appName: APP_NAME });

  // 情境 1：包含 "BLOCK" → 跳過模型呼叫
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_BLOCK,
  });
  await callAgentAndPrint(runner, "請寫一個關於 BLOCK 的笑話", SESSION_ID_BLOCK);

  // 情境 2：不包含 "BLOCK" → 修改 instruction 後照常呼叫
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_NORMAL,
  });
  await callAgentAndPrint(runner, "請寫一首短詩", SESSION_ID_NORMAL);
}

main();
```

> go

```go
package main

import (
    "context"
    "log"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/genai"
)

func onBeforeModel(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
    log.Printf("[回調] BeforeModel 觸發（agent=%q）。", ctx.AgentName())

    // --- 修改範例：在 system instruction 前加上前綴 ---
    if req.Config.SystemInstruction != nil {
        prefix := "[由回調修改] "
        // 這是簡化示範；正式環境可能需要更完整的檢查/深拷貝。
        if len(req.Config.SystemInstruction.Parts) > 0 {
            req.Config.SystemInstruction.Parts[0].Text =
                prefix + req.Config.SystemInstruction.Parts[0].Text
        } else {
            req.Config.SystemInstruction.Parts =
                append(req.Config.SystemInstruction.Parts, &genai.Part{Text: prefix})
        }
        log.Printf("[回調] 已修改 system instruction。")
    }

    // --- 阻擋/跳過範例：若使用者輸入包含 "BLOCK" 則跳過模型呼叫 ---
    for _, content := range req.Contents {
        for _, part := range content.Parts {
            if strings.Contains(strings.ToUpper(part.Text), "BLOCK") {
                log.Println("[回調] 偵測到關鍵字 'BLOCK'，跳過本次 LLM 呼叫。")
                return &model.LLMResponse{
                    Content: &genai.Content{
                        Role:  "model",
                        Parts: []*genai.Part{{Text: "此 LLM 呼叫已被 before_model_callback 阻擋。"}},
                    },
                }, nil
            }
        }
    }

    log.Println("[回調] 未觸發阻擋條件，繼續呼叫 LLM。")
    return nil, nil
}

func runBeforeModelExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("致命錯誤：建立模型失敗：%v", err)
    }

    llmCfg := llmagent.Config{
        Name:                 "AgentWithBeforeModelCallback",
        Model:                geminiModel,
        BeforeModelCallbacks: []llmagent.BeforeModelCallback{onBeforeModel},
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("致命錯誤：建立代理失敗：%v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("致命錯誤：建立 Runner 失敗：%v", err)
    }

    log.Println("--- 情境 1：應正常呼叫 LLM ---")
    runScenario(ctx, r, sessionService, appName, "session_normal", nil, "請告訴我一個有趣的冷知識。")

    log.Println("\n--- 情境 2：應被回調阻擋 ---")
    runScenario(ctx, r, sessionService, appName, "session_blocked", nil, "請寫一個關於 BLOCK 的笑話")
}
```

> java

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.CallbackContext;
import com.google.adk.events.Event;
import com.google.adk.models.LlmRequest;
import com.google.adk.models.LlmResponse;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterables;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.ArrayList;
import java.util.List;

public class BeforeModelCallbackExample {

  // --- 常數 ---
  private static final String AGENT_NAME = "ModelCallbackAgent";
  private static final String MODEL_NAME = "gemini-2.0-flash";
  private static final String AGENT_INSTRUCTION = "你是一位樂於助人的助理。";
  private static final String AGENT_DESCRIPTION = "示範 before_model_callback 的 LLM 代理";

  // Session 與 Runner
  private static final String APP_NAME = "guardrail_app_java";
  private static final String USER_ID = "user_1_java";

  public static void main(String[] args) {
    BeforeModelCallbackExample demo = new BeforeModelCallbackExample();
    demo.defineAgentAndRun();
  }

  // --- 1. 定義回調函式 ---
  // 檢查/修改 LLM request，或直接跳過本次模型呼叫。
  public Maybe<LlmResponse> simpleBeforeModelModifier(
      CallbackContext callbackContext, LlmRequest llmRequest) {

    String agentName = callbackContext.agentName();
    System.out.printf("%n[回調] 即將呼叫模型（agent）：%s%n", agentName);

    String lastUserMessage = "";
    if (llmRequest.contents() != null && !llmRequest.contents().isEmpty()) {
      Content lastContentItem = Iterables.getLast(llmRequest.contents());
      if ("user".equals(lastContentItem.role().orElse(null))
          && lastContentItem.parts().isPresent()
          && !lastContentItem.parts().get().isEmpty()) {
        lastUserMessage = lastContentItem.parts().get().get(0).text().orElse("");
      }
    }
    System.out.printf("[回調] 最後一則使用者訊息：'%s'%n", lastUserMessage);

    // --- 修改範例：在 system instruction 前加上前綴 ---
    Content systemInstructionFromRequest = Content.builder().parts(ImmutableList.of()).build();
    if (llmRequest.config().isPresent()) {
      systemInstructionFromRequest =
          llmRequest
              .config()
              .get()
              .systemInstruction()
              .orElseGet(() -> Content.builder().role("system").parts(ImmutableList.of()).build());
    }

    List<Part> currentSystemParts =
        new ArrayList<>(systemInstructionFromRequest.parts().orElse(ImmutableList.of()));

    if (currentSystemParts.isEmpty()) {
      currentSystemParts.add(Part.fromText(""));
    }

    String prefix = "[由回調修改] ";
    String modifiedText = prefix + currentSystemParts.get(0).text().orElse("");

    // 注意：此處以 toBuilder 產生「概念上」修改後的 request（示範用）。
    llmRequest =
        llmRequest.toBuilder()
            .config(
                GenerateContentConfig.builder()
                    .systemInstruction(
                        Content.builder()
                            .role("system")
                            .parts(List.of(Part.fromText(modifiedText)))
                            .build())
                    .build())
            .build();

    System.out.printf("[回調] 已修改 system instruction：%s%n",
        llmRequest.config().get().systemInstruction().orElse(null));

    // --- 阻擋/跳過範例 ---
    if (lastUserMessage.toUpperCase().contains("BLOCK")) {
      System.out.println("[回調] 偵測到關鍵字 'BLOCK'，跳過本次 LLM 呼叫。");
      return Maybe.just(
          LlmResponse.builder()
              .content(
                  Content.builder()
                      .role("model")
                      .parts(
                          ImmutableList.of(
                              Part.fromText("此 LLM 呼叫已被 before_model_callback 阻擋。")))
                      .build())
              .build());
    }

    System.out.println("[回調] 未觸發阻擋條件，繼續呼叫 LLM。");
    return Maybe.empty();
  }

  // --- 2. 建立 Agent 並執行 ---
  public void defineAgentAndRun() {
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(AGENT_NAME)
            .model(MODEL_NAME)
            .instruction(AGENT_INSTRUCTION)
            .description(AGENT_DESCRIPTION)
            .beforeModelCallback(this::simpleBeforeModelModifier)
            .build();

    InMemoryRunner runner = new InMemoryRunner(myLlmAgent, APP_NAME);
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();

    Content userMessage =
        Content.fromParts(Part.fromText("請介紹量子運算。這是測試，所以 BLOCK。"));

    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
```

</details>

### 模型後置回調 (After Model Callback)

**觸發時機：** 在收到來自 LLM 的響應 (`LlmResponse`) 後立即調用，隨後才由調用代理進一步處理。

**用途：** 允許檢查或修改原始 LLM 響應。用例包括：

* 記錄模型輸出
* 重新格式化響應
* 審查模型生成的敏感資訊
* 從 LLM 響應中解析結構化數據並將其存儲在 `callback_context.state` 中
* 或處理特定的錯誤代碼。

<details>
<summary>程式碼範例</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from typing import Optional
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.models import LlmResponse
from copy import deepcopy

GEMINI_2_FLASH = "gemini-2.0-flash"

# --- 定義回調函式 ---
def simple_after_model_modifier(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """在收到 LLM 回應後進行檢查/修改。"""
    agent_name = callback_context.agent_name
    print(f"[回調] 模型呼叫結束（agent）：{agent_name}")

    # --- 檢查 ---
    original_text = ""
    if llm_response.content and llm_response.content.parts:
        # 此範例假設是簡單的文字回應
        if llm_response.content.parts[0].text:
            original_text = llm_response.content.parts[0].text
            print(
                f"[回調] 檢查到原始回應文字：'{original_text[:100]}...'"
            )  # 只印片段
        elif llm_response.content.parts[0].function_call:
            print(
                f"[回調] 檢查到回應包含 function call：'{llm_response.content.parts[0].function_call.name}'。此範例不修改工具呼叫。"
            )
            return None
        else:
            print("[回調] 檢查到回應沒有可用的文字內容。")
            return None
    elif llm_response.error_message:
        print(f"[回調] 檢查到回應包含錯誤：'{llm_response.error_message}'。不進行修改。")
        return None
    else:
        print("[回調] 檢查到空的 LlmResponse。")
        return None

    # --- 修改示範 ---
    # 將 "joke" 替換為 "funny story"（不區分大小寫）
    search_term = "joke"
    replace_term = "funny story"
    if search_term in original_text.lower():
        print(f"[回調] 偵測到 '{search_term}'，開始修改回應。")

        # 先做簡單替換，再處理首字母大寫的情況
        modified_text = original_text.replace(search_term, replace_term)
        modified_text = modified_text.replace(
            search_term.capitalize(), replace_term.capitalize()
        )

        # 建立一個「新的」LlmResponse，避免影響原始物件（如還有其他回調要用）
        modified_parts = [deepcopy(part) for part in llm_response.content.parts]
        modified_parts[0].text = modified_text

        new_response = LlmResponse(
            content=types.Content(role="model", parts=modified_parts),
            # 需要的話可拷貝其他欄位，例如 grounding_metadata
            grounding_metadata=llm_response.grounding_metadata,
        )
        print("[回調] 回傳修改後的回應。")
        return new_response

    print(f"[回調] 未偵測到 '{search_term}'，沿用原始回應。")
    return None


# 建立 LlmAgent 並註冊回調
my_llm_agent = LlmAgent(
    name="AfterModelCallbackAgent",
    model=GEMINI_2_FLASH,
    instruction="你是一位樂於助人的助理。",
    description="示範 after_model_callback 的 LLM 代理",
    after_model_callback=simple_after_model_modifier,
)

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Session 與 Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# 與代理互動
async def call_agent_async(query: str):
    _, runner = await setup_session_and_runner()

    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理回應：", final_response)


# 注意：在 Colab 可直接在頂層使用 `await`。
# 若在一般 Python 腳本執行，請使用 asyncio.run() 或自行管理 event loop。
await call_agent_async("請寫一段文字，並多次使用單字「joke」。")
```

> typescript

```typescript
import {
  LlmAgent,
  InMemoryRunner,
  CallbackContext,
  isFinalResponse,
} from "@google/adk";
import { createUserContent } from "@google/genai";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "after_model_callback_app";
const USER_ID = "test_user_after_model";
const SESSION_ID_JOKE = "session_modify_model_call";
const SESSION_ID_POEM = "session_normal_model_call";

// --- 定義回調函式 ---
function simpleAfterModelModifier({
  context,
  response,
}: {
  context: CallbackContext;
  response: any;
}): any | undefined {
  console.log(`[回調] 模型呼叫結束（agent）：${context.agentName}`);

  const modelResponseText = response.content?.parts?.[0]?.text ?? "";
  console.log(
    `[回調] 檢查模型回應："${modelResponseText.substring(0, 50)}..."`
  );

  // --- 修改示範 ---
  // 將 "joke" 替換為 "funny story"（不區分大小寫）
  const searchTerm = "joke";
  const replaceTerm = "funny story";

  if (modelResponseText.toLowerCase().includes(searchTerm)) {
    console.log(`[回調] 偵測到 '${searchTerm}'，開始修改回應。`);

    // 深拷貝避免修改原始 response 物件
    const modifiedResponse = JSON.parse(JSON.stringify(response));

    if (modifiedResponse.content?.parts?.[0]) {
      const regex = new RegExp(searchTerm, "gi");
      modifiedResponse.content.parts[0].text = modelResponseText.replace(
        regex,
        replaceTerm
      );
    }

    console.log("[回調] 回傳修改後的回應。");
    return modifiedResponse;
  }

  console.log("[回調] 未偵測到關鍵字，沿用原始模型回應。");
  return undefined;
}

// --- 建立 LlmAgent 並註冊回調 ---
const myLlmAgent = new LlmAgent({
  name: "AfterModelCallbackAgent",
  model: MODEL_NAME,
  instruction: "你是一位樂於助人的助理。",
  description: "示範 after_model_callback 的 LLM 代理",
  afterModelCallback: simpleAfterModelModifier,
});

// --- 與代理互動 ---
async function callAgentAndPrint({
  runner,
  query,
  sessionId,
}: {
  runner: InMemoryRunner;
  query: string;
  sessionId: string;
}) {
  console.log(`\n>>> 呼叫代理，輸入："${query}"`);

  let finalResponseContent = "未收到最終回應。";
  const events = runner.runAsync({
    userId: USER_ID,
    sessionId,
    newMessage: createUserContent(query),
  });

  for await (const event of events) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      finalResponseContent = event.content.parts
        .map((part: { text?: string }) => part.text ?? "")
        .join("");
    }
  }
  console.log("<<< 代理回應：", finalResponseContent);
}

// --- 執行示範 ---
async function main() {
  const runner = new InMemoryRunner({ agent: myLlmAgent, appName: APP_NAME });

  // 情境 1：回調會偵測到 "joke" 並修改回應
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_JOKE,
  });
  await callAgentAndPrint({
    runner,
    query: "請寫一個短笑話（joke），內容要包含單字 joke。",
    sessionId: SESSION_ID_JOKE,
  });

  // 情境 2：回調找不到 "joke"，回應將不被修改
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID_POEM,
  });
  await callAgentAndPrint({
    runner,
    query: "請寫一首關於寫程式的短詩。",
    sessionId: SESSION_ID_POEM,
  });
}

main();
```

> go

```go
package main

import (
    "context"
    "log"
    "regexp"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/genai"
)

func onAfterModel(ctx agent.CallbackContext, resp *model.LLMResponse, respErr error) (*model.LLMResponse, error) {
    log.Printf("[回調] AfterModel 觸發（agent=%q）。", ctx.AgentName())

    if respErr != nil {
        log.Printf("[回調] 模型回傳錯誤：%v。沿用錯誤結果。", respErr)
        return nil, respErr
    }

    if resp == nil || resp.Content == nil || len(resp.Content.Parts) == 0 {
        log.Println("[回調] 回應為 nil 或沒有 parts，無法處理。")
        return nil, nil
    }

    // 若為 function call，則不修改。
    if resp.Content.Parts[0].FunctionCall != nil {
        log.Println("[回調] 回應為 function call（工具呼叫）。此範例不修改。")
        return nil, nil
    }

    originalText := resp.Content.Parts[0].Text

    // 使用不分大小寫、含單字邊界的正則來找 "joke"
    re := regexp.MustCompile(`(?i)\bjoke\b`)
    if !re.MatchString(originalText) {
        log.Println("[回調] 未偵測到 'joke'，沿用原始回應。")
        return nil, nil
    }

    log.Println("[回調] 偵測到 'joke'，開始修改回應。")

    // 以 replacer 處理大小寫（簡化示範）
    modifiedText := re.ReplaceAllStringFunc(originalText, func(s string) string {
        // s 可能是 "joke" / "Joke" / "JOKE" 等
        if strings.ToUpper(s) == "JOKE" {
            if s == "Joke" {
                return "Funny story"
            }
            return "funny story"
        }
        return s
    })

    resp.Content.Parts[0].Text = modifiedText
    log.Println("[回調] 已回傳修改後的回應。")
    return resp, nil
}

func runAfterModelExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("致命錯誤：建立模型失敗：%v", err)
    }

    llmCfg := llmagent.Config{
        Name:                "AgentWithAfterModelCallback",
        Model:               geminiModel,
        AfterModelCallbacks: []llmagent.AfterModelCallback{onAfterModel},
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("致命錯誤：建立代理失敗：%v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("致命錯誤：建立 Runner 失敗：%v", err)
    }

    log.Println("--- 情境 1：回應應被修改 ---")
    runScenario(ctx, r, sessionService, appName, "session_modify", nil, "請給我一段描述不同類型 joke 的段落。")
}
```

> java

```java
import com.google.adk.agents.CallbackContext;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.models.LlmResponse;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class AfterModelCallbackExample {

  // --- 常數 ---
  private static final String AGENT_NAME = "AfterModelCallbackAgent";
  private static final String MODEL_NAME = "gemini-2.0-flash";
  private static final String AGENT_INSTRUCTION = "你是一位樂於助人的助理。";
  private static final String AGENT_DESCRIPTION = "示範 after_model_callback 的 LLM 代理";

  // Session 與 Runner
  private static final String APP_NAME = "AfterModelCallbackAgentApp";
  private static final String USER_ID = "user_1";

  // 文字替換用
  private static final String SEARCH_TERM = "joke";
  private static final String REPLACE_TERM = "funny story";
  private static final Pattern SEARCH_PATTERN =
      Pattern.compile("\\b" + Pattern.quote(SEARCH_TERM) + "\\b", Pattern.CASE_INSENSITIVE);

  public static void main(String[] args) {
    AfterModelCallbackExample example = new AfterModelCallbackExample();
    example.defineAgentAndRun();
  }

  // --- 定義回調函式 ---
  // 在收到 LLM 回應後進行檢查/修改。
  public Maybe<LlmResponse> simpleAfterModelModifier(
      CallbackContext callbackContext, LlmResponse llmResponse) {

    String agentName = callbackContext.agentName();
    System.out.printf("%n[回調] 模型呼叫結束（agent）：%s%n", agentName);

    // --- 檢查階段 ---
    if (llmResponse.errorMessage().isPresent()) {
      System.out.printf("[回調] 回應包含錯誤：'%s'。不進行修改。%n", llmResponse.errorMessage().get());
      return Maybe.empty();
    }

    Optional<Part> firstTextPartOpt =
        llmResponse
            .content()
            .flatMap(Content::parts)
            .filter(parts -> !parts.isEmpty() && parts.get(0).text().isPresent())
            .map(parts -> parts.get(0));

    if (!firstTextPartOpt.isPresent()) {
      // 可能是 function call、空內容、或第一個 part 沒有文字
      llmResponse
          .content()
          .flatMap(Content::parts)
          .filter(parts -> !parts.isEmpty() && parts.get(0).functionCall().isPresent())
          .ifPresent(
              parts ->
                  System.out.printf(
                      "[回調] 回應為 function call（'%s'）。此範例不修改。%n",
                      parts.get(0).functionCall().get().name().orElse("N/A")));

      if (!llmResponse.content().isPresent()
          || !llmResponse.content().flatMap(Content::parts).isPresent()
          || llmResponse.content().flatMap(Content::parts).get().isEmpty()) {
        System.out.println("[回調] 回應內容為空或沒有 parts。不進行修改。");
      } else {
        System.out.println("[回調] 第一個 part 沒有文字內容。不進行修改。");
      }

      return Maybe.empty();
    }

    String originalText = firstTextPartOpt.get().text().get();
    System.out.printf("[回調] 檢查到原始文字：'%.100s...'%n", originalText);

    // --- 修改階段 ---
    Matcher matcher = SEARCH_PATTERN.matcher(originalText);
    if (!matcher.find()) {
      System.out.printf("[回調] 未偵測到 '%s'，沿用原始回應。%n", SEARCH_TERM);
      return Maybe.empty();
    }

    System.out.printf("[回調] 偵測到 '%s'，開始修改回應。%n", SEARCH_TERM);

    // 依找到的詞彙首字母大小寫，調整替換詞首字母（簡化示範）
    String foundTerm = matcher.group(0); // 例如 "joke" 或 "Joke"
    String actualReplaceTerm = REPLACE_TERM;
    if (Character.isUpperCase(foundTerm.charAt(0)) && REPLACE_TERM.length() > 0) {
      actualReplaceTerm = Character.toUpperCase(REPLACE_TERM.charAt(0)) + REPLACE_TERM.substring(1);
    }
    String modifiedText = matcher.replaceFirst(Matcher.quoteReplacement(actualReplaceTerm));

    // 建立新的 LlmResponse（用修改後內容取代第一個 part）
    Content originalContent = llmResponse.content().get();
    List<Part> originalParts = originalContent.parts().orElse(ImmutableList.of());

    List<Part> modifiedPartsList = new ArrayList<>(originalParts.size());
    if (!originalParts.isEmpty()) {
      modifiedPartsList.add(Part.fromText(modifiedText));
      for (int i = 1; i < originalParts.size(); i++) {
        modifiedPartsList.add(originalParts.get(i));
      }
    } else {
      modifiedPartsList.add(Part.fromText(modifiedText));
    }

    LlmResponse.Builder newResponseBuilder =
        LlmResponse.builder()
            .content(
                originalContent.toBuilder().parts(ImmutableList.copyOf(modifiedPartsList)).build())
            .groundingMetadata(llmResponse.groundingMetadata());

    System.out.println("[回調] 回傳修改後的回應。");
    return Maybe.just(newResponseBuilder.build());
  }

  // --- 建立 Agent 並執行 ---
  public void defineAgentAndRun() {
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(AGENT_NAME)
            .model(MODEL_NAME)
            .instruction(AGENT_INSTRUCTION)
            .description(AGENT_DESCRIPTION)
            .afterModelCallback(this::simpleAfterModelModifier)
            .build();

    InMemoryRunner runner = new InMemoryRunner(myLlmAgent, APP_NAME);
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();

    Content userMessage =
        Content.fromParts(Part.fromText("請講一個笑話（joke），並在回應中包含單字 joke。"));

    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
```

</details>

## 工具執行回調 (Tool Execution Callbacks)

這些回調也是 `LlmAgent` 特有的，並圍繞著 LLM 可能請求的工具（包括 `FunctionTool`、`AgentTool` 等）的執行觸發。

### 工具前置回調 (Before Tool Callback)

**觸發時機：** 在特定工具的 `run_async` 方法被調用 *之前* 調用，此時 LLM 已經為其生成了函數調用。

**用途：** 允許檢查和修改工具參數、在執行前執行授權檢查、記錄工具使用嘗試或實施工具級別的緩存。

**返回值影響：**

1. 如果回調返回 `None`（或 Java 中的 `Maybe.empty()` 對象），則使用（可能已修改的）`args` 執行工具的 `run_async` 方法。
2. 如果返回字典（或 Java 中的 `Map`），則 **跳過** 工具的 `run_async` 方法。返回的字典將直接作為工具調用的結果。這對於緩存或覆蓋工具行為非常有用。

<details>
<summary>程式碼範例</summary>

> Python

```python
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from typing import Optional, Dict, Any
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool

GEMINI_2_FLASH = "gemini-2.0-flash"

# --- 定義一個簡單的工具函式 ---
def get_capital_city(country: str) -> str:
    """取得指定國家的首都。"""
    print(f"--- 工具 'get_capital_city' 執行中，country: {country} ---")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "germany": "Berlin",
    }
    return country_capitals.get(country.lower(), f"找不到 {country} 的首都")

capital_tool = FunctionTool(func=get_capital_city)

# --- 定義回調函式 ---
def simple_before_tool_modifier(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """檢查/修改工具參數，或跳過工具呼叫。"""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[回調] 工具呼叫前觸發：tool='{tool_name}'，agent='{agent_name}'")
    print(f"[回調] 原始 args：{args}")

    # 範例 1：若輸入 Canada，將參數改為 France
    if tool_name == "get_capital_city" and args.get("country", "").lower() == "canada":
        print("[回調] 偵測到 'Canada'：將參數改為 'France'。")
        args["country"] = "France"
        print(f"[回調] 修改後 args：{args}")
        return None

    # 範例 2：若輸入 BLOCK，跳過工具執行並直接回傳結果
    if tool_name == "get_capital_city" and args.get("country", "").upper() == "BLOCK":
        print("[回調] 偵測到 'BLOCK'：跳過工具執行。")
        return {"result": "工具執行已被 before_tool_callback 阻擋。"}

    print("[回調] 繼續使用原始或已修改的 args 來執行工具。")
    return None

# --- 建立 LlmAgent 並指定回調 ---
my_llm_agent = LlmAgent(
    name="ToolCallbackAgent",
    model=GEMINI_2_FLASH,
    instruction="你是一個可以查詢首都的代理。請使用 get_capital_city 工具。",
    description="示範 before_tool_callback 的 LLM 代理",
    tools=[capital_tool],
    before_tool_callback=simple_before_tool_modifier,
)

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Session 與 Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# 與代理互動
async def call_agent_async(query: str):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    _, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理回應：", final_response)

# 注意：在 Colab 可直接在頂層使用 `await`。
# 若要以一般 Python 腳本執行，請使用 asyncio.run() 或自行管理 event loop。
await call_agent_async("Canada")
```

> typescript

```typescript
import {
  LlmAgent,
  InMemoryRunner,
  FunctionTool,
  ToolContext,
  isFinalResponse,
  BaseTool,
} from "@google/adk";
import { createUserContent } from "@google/genai";
import { z } from "zod";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "before_tool_callback_app";
const USER_ID = "test_user_before_tool";

// --- 定義一個簡單的工具函式 ---
const CountryInput = z.object({
  country: z.string().describe("要查詢首都的國家名稱。"),
});

async function getCapitalCity(
  params: z.infer<typeof CountryInput>
): Promise<{ result: string }> {
  console.log(`\n-- 工具呼叫：getCapitalCity(country='${params.country}') --`);
  const capitals: Record<string, string> = {
    "united states": "Washington, D.C.",
    canada: "Ottawa",
    france: "Paris",
    japan: "Tokyo",
  };
  const result =
    capitals[params.country.toLowerCase()] ??
    `抱歉，我找不到 ${params.country} 的首都。`;
  console.log(`-- 工具結果：'${result}' --`);
  return { result };
}

const getCapitalCityTool = new FunctionTool({
  name: "get_capital_city",
  description: "取得指定國家的首都",
  parameters: CountryInput,
  execute: getCapitalCity,
});

// --- 定義回調函式 ---
function simpleBeforeToolModifier({
  tool,
  args,
  context,
}: {
  tool: BaseTool;
  args: Record<string, any>;
  context: ToolContext;
}) {
  const agentName = context.agentName;
  const toolName = tool.name;
  console.log(`[回調] 工具呼叫前觸發：tool='${toolName}'，agent='${agentName}'`);
  console.log(`[回調] 原始 args：${JSON.stringify(args)}`);

  // 範例 1：若輸入 Canada，將參數改為 France
  if (toolName === "get_capital_city" && args["country"]?.toLowerCase() === "canada") {
    console.log("[回調] 偵測到 'Canada'：將參數改為 'France'。");
    args["country"] = "France";
    console.log(`[回調] 修改後 args：${JSON.stringify(args)}`);
    return undefined;
  }

  // 範例 2：若輸入 BLOCK，跳過工具執行並直接回傳結果
  if (toolName === "get_capital_city" && args["country"]?.toUpperCase() === "BLOCK") {
    console.log("[回調] 偵測到 'BLOCK'：跳過工具執行。");
    return { result: "工具執行已被 before_tool_callback 阻擋。" };
  }

  console.log("[回調] 繼續使用原始或已修改的 args 來執行工具。");
  return;
}

// --- 建立 LlmAgent 並指定回調 ---
const myLlmAgent = new LlmAgent({
  name: "ToolCallbackAgent",
  model: MODEL_NAME,
  instruction: "你是一個可以查詢首都的代理。請使用 get_capital_city 工具。",
  description: "示範 before_tool_callback 的 LLM 代理",
  tools: [getCapitalCityTool],
  beforeToolCallback: simpleBeforeToolModifier,
});

// --- 代理互動邏輯 ---
async function callAgentAndPrint(runner: InMemoryRunner, query: string, sessionId: string) {
  console.log(`\n>>> 呼叫代理（session='${sessionId}'）| 輸入："${query}"`);

  for await (const event of runner.runAsync({
    userId: USER_ID,
    sessionId,
    newMessage: createUserContent(query),
  })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const finalResponseContent = event.content.parts
        .map((part) => part.text ?? "")
        .join("");
      console.log(`<<< 最終輸出：${finalResponseContent}`);
    }
  }
}

// --- 執行示範 ---
async function main() {
  const runner = new InMemoryRunner({ agent: myLlmAgent, appName: APP_NAME });

  // 情境 1：回調將參數從 "Canada" 修改為 "France"
  const canadaSessionId = "session_canada_test";
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: canadaSessionId,
  });
  await callAgentAndPrint(runner, "What is the capital of Canada?", canadaSessionId);

  // 情境 2：回調跳過工具呼叫
  const blockSessionId = "session_block_test";
  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: blockSessionId,
  });
  await callAgentAndPrint(runner, "What is the capital of BLOCK?", blockSessionId);
}

main();
```

> go

```go
package main

import (
    "context"
    "fmt"
    "log"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

// GetCapitalCityArgs 定義 getCapitalCity 工具的參數
type GetCapitalCityArgs struct {
    Country string `json:"country" jsonschema:"要查詢首都的國家名稱。"`
}

// getCapitalCity：回傳指定國家的首都
func getCapitalCity(ctx tool.Context, args *GetCapitalCityArgs) (string, error) {
    capitals := map[string]string{
        "canada":        "Ottawa",
        "france":        "Paris",
        "germany":       "Berlin",
        "united states": "Washington, D.C.",
    }
    capital, ok := capitals[strings.ToLower(args.Country)]
    if !ok {
        return "", fmt.Errorf("未知國家：%s", args.Country)
    }
    return capital, nil
}

// onBeforeTool：工具呼叫前回調
func onBeforeTool(ctx tool.Context, t tool.Tool, args map[string]any) (map[string]any, error) {
    log.Printf("[回調] BeforeTool 觸發：tool=%q，agent=%q。", t.Name(), ctx.AgentName())
    log.Printf("[回調] 原始 args：%v", args)

    if t.Name() == "getCapitalCity" {
        if country, ok := args["country"].(string); ok {
            if strings.ToLower(country) == "canada" {
                log.Println("[回調] 偵測到 'Canada'：將參數改為 'France'。")
                args["country"] = "France"
                return args, nil // 使用修改後參數繼續執行工具
            } else if strings.ToUpper(country) == "BLOCK" {
                log.Println("[回調] 偵測到 'BLOCK'：跳過工具執行。")
                // 跳過工具，直接回傳自訂結果
                return map[string]any{"result": "工具執行已被 before_tool_callback 阻擋。"}, nil
            }
        }
    }

    log.Println("[回調] 繼續使用原始或已修改的 args 來執行工具。")
    return nil, nil // nil 表示不跳過工具，照常執行
}

func runBeforeToolExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("致命錯誤：建立模型失敗：%v", err)
    }

    capitalTool, err := functiontool.New(functiontool.Config{
        Name:        "getCapitalCity",
        Description: "取得指定國家的首都。",
    }, getCapitalCity)
    if err != nil {
        log.Fatalf("致命錯誤：建立 FunctionTool 失敗：%v", err)
    }

    llmCfg := llmagent.Config{
        Name:                "AgentWithBeforeToolCallback",
        Model:               geminiModel,
        Tools:               []tool.Tool{capitalTool},
        BeforeToolCallbacks: []llmagent.BeforeToolCallback{onBeforeTool},
        Instruction:         "你是一個可以查詢首都的代理。請使用 getCapitalCity 工具。",
    }

    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("致命錯誤：建立代理失敗：%v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{AppName: appName, Agent: testAgent, SessionService: sessionService})
    if err != nil {
        log.Fatalf("致命錯誤：建立 Runner 失敗：%v", err)
    }

    log.Println("--- 情境 1：參數應被修改 ---")
    runScenario(ctx, r, sessionService, appName, "session_tool_modify", nil, "What is the capital of Canada?")

    log.Println("--- 情境 2：工具呼叫應被阻擋 ---")
    runScenario(ctx, r, sessionService, appName, "session_tool_block", nil, "capital of BLOCK")
}
```

> java

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.InvocationContext;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.BaseTool;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.common.collect.ImmutableMap;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class BeforeToolCallbackExample {

  private static final String APP_NAME = "ToolCallbackAgentApp";
  private static final String USER_ID = "user_1";
  private static final String SESSION_ID = "session_001";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    BeforeToolCallbackExample example = new BeforeToolCallbackExample();
    example.runAgent("capital of canada");
  }

  // --- 定義一個簡單的工具函式 ---
  // Schema 很重要，讓 callback 的 args 能正確辨識輸入欄位。
  public static Map<String, Object> getCapitalCity(
      @Schema(name = "country", description = "要查詢首都的國家名稱。") String country) {

    System.out.printf("--- 工具 'getCapitalCity' 執行中，country: %s ---%n", country);

    Map<String, String> countryCapitals = new HashMap<>();
    countryCapitals.put("united states", "Washington, D.C.");
    countryCapitals.put("canada", "Ottawa");
    countryCapitals.put("france", "Paris");
    countryCapitals.put("germany", "Berlin");

    String capital =
        countryCapitals.getOrDefault(country.toLowerCase(), "找不到 " + country + " 的首都");

    // FunctionTool 期望回傳 Map<String, Object>
    return ImmutableMap.of("capital", capital);
  }

  // --- 定義回調函式 ---
  public Maybe<Map<String, Object>> simpleBeforeToolModifier(
      InvocationContext invocationContext,
      BaseTool tool,
      Map<String, Object> args,
      ToolContext toolContext) {

    String agentName = invocationContext.agent().name();
    String toolName = tool.name();

    System.out.printf("[回調] 工具呼叫前觸發：tool='%s'，agent='%s'%n", toolName, agentName);
    System.out.printf("[回調] 原始 args：%s%n", args);

    if ("getCapitalCity".equals(toolName)) {
      String countryArg = (String) args.get("country");
      if (countryArg != null) {
        // 範例 1：修改參數
        if ("canada".equalsIgnoreCase(countryArg)) {
          System.out.println("[回調] 偵測到 'Canada'：將參數改為 'France'。");
          args.put("country", "France");
          System.out.printf("[回調] 修改後 args：%s%n", args);
          return Maybe.empty(); // 使用修改後 args 繼續執行工具
        }

        // 範例 2：跳過工具呼叫
        if ("BLOCK".equalsIgnoreCase(countryArg)) {
          System.out.println("[回調] 偵測到 'BLOCK'：跳過工具執行。");
          return Maybe.just(
              ImmutableMap.of("result", "工具執行已被 before_tool_callback 阻擋。"));
        }
      }
    }

    System.out.println("[回調] 繼續使用原始或已修改的 args 來執行工具。");
    return Maybe.empty();
  }

  public void runAgent(String query) {
    // --- 將函式包裝成 Tool ---
    FunctionTool capitalTool = FunctionTool.create(this.getClass(), "getCapitalCity");

    // --- 建立 LlmAgent 並指定回調 ---
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(APP_NAME)
            .model(MODEL_NAME)
            .instruction("你是一個可以查詢首都的代理。請使用 getCapitalCity 工具。")
            .description("示範 before_tool_callback 的 LLM 代理")
            .tools(capitalTool)
            .beforeToolCallback(this::simpleBeforeToolModifier)
            .build();

    // Session 與 Runner
    InMemoryRunner runner = new InMemoryRunner(myLlmAgent);
    Session session =
        runner.sessionService().createSession(APP_NAME, USER_ID, null, SESSION_ID).blockingGet();

    Content userMessage = Content.fromParts(Part.fromText(query));

    System.out.printf("%n--- 呼叫代理，輸入：\"%s\" ---%n", query);
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
```

</details>

### 工具後置回調 (After Tool Callback)

**觸發時機：** 在工具的 `run_async` 方法成功完成後立即調用。

**用途：** 允許在工具結果發回給 LLM 之前（可能在總結之後）對其進行檢查和修改。可用於記錄工具結果、對結果進行後處理或格式化，或者將結果的特定部分保存到對話狀態中。

**返回值影響：**

1. 如果回調返回 `None`（或 Java 中的 `Maybe.empty()` 對象），則使用原始的 `tool_response`。
2. 如果返回一個新字典，它將 **替換** 原始的 `tool_response`。這允許修改或過濾 LLM 看到的結果。

<details>
<summary>程式碼範例</summary>

> Python

```python
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

GEMINI_2_FLASH = "gemini-2.0-flash"


# --- 定義一個簡單工具函式 ---
def get_capital_city(country: str) -> str:
    """取得指定國家的首都。"""
    print(f"--- 工具 'get_capital_city' 執行中，country: {country} ---")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "germany": "Berlin",
    }
    return country_capitals.get(country.lower(), f"找不到 {country} 的首都")


# --- 將函式包裝成 Tool ---
capital_tool = FunctionTool(func=get_capital_city)


# --- 定義回調函式（工具後置回調）---
def simple_after_tool_modifier(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """在工具執行完成後，檢查/修改工具回傳結果。"""
    agent_name = tool_context.agent_name
    tool_name = tool.name

    print(f"[回調] 工具呼叫後觸發：tool='{tool_name}'，agent='{agent_name}'")
    print(f"[回調] 使用的 args：{args}")
    print(f"[回調] 原始 tool_response：{tool_response}")

    # FunctionTool 的預設回傳結構：{"result": <tool_return_value>}
    original_result_value = tool_response.get("result", "")

    # --- 修改範例 ---
    if tool_name == "get_capital_city" and original_result_value == "Washington, D.C.":
        print("[回調] 偵測到 'Washington, D.C.'：修改工具回傳結果。")

        # 重要：請回傳「新的」dict（或修改副本），避免影響原始物件
        modified_response = deepcopy(tool_response)
        modified_response["result"] = (
            f"{original_result_value}（註：這是美國首都）"
        )
        modified_response["note_added_by_callback"] = True

        print(f"[回調] 修改後 tool_response：{modified_response}")
        return modified_response

    print("[回調] 不修改，沿用原始工具結果。")
    return None


# --- 建立 Agent 並指定回調 ---
my_llm_agent = LlmAgent(
    name="AfterToolCallbackAgent",
    model=GEMINI_2_FLASH,
    instruction="你是一個會使用 get_capital_city 工具查詢首都的代理。請清楚回報結果。",
    description="示範 after_tool_callback 的 LLM 代理",
    tools=[capital_tool],
    after_tool_callback=simple_after_tool_modifier,
)

APP_NAME = "after_tool_callback_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


async def setup_session_and_runner():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return runner


async def call_agent_async(query: str):
    runner = await setup_session_and_runner()
    content = types.Content(role="user", parts=[types.Part(text=query)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    ):
        if event.is_final_response() and event.content:
            final_response = event.content.parts[0].text
            print("代理回應：", final_response)


# 在 Colab 可直接使用 `await`；
# 若是一般 Python 腳本，請用 asyncio.run() 或自行管理 event loop。
await call_agent_async("united states")
```

> TypeScript

```typescript
import {
  BaseTool,
  FunctionTool,
  InMemoryRunner,
  LlmAgent,
  ToolContext,
  isFinalResponse,
} from "@google/adk";
import { createUserContent } from "@google/genai";
import { z } from "zod";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "after_tool_callback_app";
const USER_ID = "test_user_after_tool";
const SESSION_ID = "session_001";

// --- 定義一個簡單工具函式 ---
const CountryInput = z.object({
  country: z.string().describe("要查詢首都的國家名稱。"),
});

async function getCapitalCity(
  params: z.infer<typeof CountryInput>
): Promise<{ result: string }> {
  console.log(`--- 工具 'get_capital_city' 執行中，country: ${params.country} ---`);
  const countryCapitals: Record<string, string> = {
    "united states": "Washington, D.C.",
    canada: "Ottawa",
    france: "Paris",
    germany: "Berlin",
  };

  const result =
    countryCapitals[params.country.toLowerCase()] ??
    `找不到 ${params.country} 的首都`;

  return { result };
}

// --- 將函式包裝成 Tool ---
const capitalTool = new FunctionTool({
  name: "get_capital_city",
  description: "取得指定國家的首都",
  parameters: CountryInput,
  execute: getCapitalCity,
});

// --- 定義回調函式（工具後置回調）---
function simpleAfterToolModifier({
  tool,
  args,
  context,
  response,
}: {
  tool: BaseTool;
  args: Record<string, any>;
  context: ToolContext;
  response: Record<string, any>;
}) {
  const agentName = context.agentName;
  const toolName = tool.name;

  console.log(`[回調] 工具呼叫後觸發：tool='${toolName}'，agent='${agentName}'`);
  console.log(`[回調] 使用的 args：${JSON.stringify(args)}`);
  console.log(`[回調] 原始 response：${JSON.stringify(response)}`);

  const originalResultValue = response?.result ?? "";

  // --- 修改範例 ---
  if (toolName === "get_capital_city" && originalResultValue === "Washington, D.C.") {
    const modifiedResponse = structuredClone(response);
    modifiedResponse.result = `${originalResultValue}（註：這是美國首都）`;
    modifiedResponse.note_added_by_callback = true;

    console.log(`[回調] 修改後 response：${JSON.stringify(modifiedResponse)}`);
    return modifiedResponse;
  }

  console.log("[回調] 不修改，沿用原始工具結果。");
  return undefined;
}

// --- 建立 Agent 並指定回調 ---
const myLlmAgent = new LlmAgent({
  name: "AfterToolCallbackAgent",
  model: MODEL_NAME,
  instruction: "你是一個會使用 get_capital_city 工具查詢首都的代理。請清楚回報結果。",
  description: "示範 after_tool_callback 的 LLM 代理",
  tools: [capitalTool],
  afterToolCallback: simpleAfterToolModifier,
});

async function main() {
  const runner = new InMemoryRunner({ appName: APP_NAME, agent: myLlmAgent });

  await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID,
  });

  const events = runner.runAsync({
    userId: USER_ID,
    sessionId: SESSION_ID,
    newMessage: createUserContent("united states"),
  });

  for await (const event of events) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const finalText = event.content.parts.map((p: any) => p.text ?? "").join("");
      console.log("代理回應：", finalText.trim());
    } else if (event.errorMessage) {
      console.log(`錯誤：${event.errorMessage}`);
    }
  }
}

main();
```

> Go

```go
package main

import (
    "context"
    "fmt"
    "log"
    "strings"

    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

// GetCapitalCityArgs 定義 getCapitalCity 工具的參數
type GetCapitalCityArgs struct {
    Country string `json:"country" jsonschema:"要查詢首都的國家名稱。"`
}

// getCapitalCity：回傳指定國家的首都
func getCapitalCity(ctx tool.Context, args *GetCapitalCityArgs) (string, error) {
    capitals := map[string]string{
        "canada":        "Ottawa",
        "france":        "Paris",
        "germany":       "Berlin",
        "united states": "Washington, D.C.",
    }
    capital, ok := capitals[strings.ToLower(args.Country)]
    if !ok {
        return "", fmt.Errorf("未知國家：%s", args.Country)
    }
    return capital, nil
}

// onAfterTool：工具後置回調
func onAfterTool(
    ctx tool.Context,
    t tool.Tool,
    args map[string]any,
    result map[string]any,
    err error,
) (map[string]any, error) {
    log.Printf("[回調] AfterTool 觸發：tool=%q，agent=%q。", t.Name(), ctx.AgentName())
    log.Printf("[回調] 原始 result：%v", result)

    if err != nil {
        log.Printf("[回調] 工具執行發生錯誤：%v。沿用錯誤結果。", err)
        return nil, err
    }

    // FunctionTool 的預設回傳結構：{"result": <tool_return_value>}
    if t.Name() == "getCapitalCity" {
        if original, ok := result["result"].(string); ok && original == "Washington, D.C." {
            log.Println("[回調] 偵測到 'Washington, D.C.'：修改工具回傳結果。")

            modified := make(map[string]any, len(result)+1)
            for k, v := range result {
                modified[k] = v
            }
            modified["result"] = fmt.Sprintf("%s（註：這是美國首都）", original)
            modified["note_added_by_callback"] = true
            return modified, nil
        }
    }

    log.Println("[回調] 不修改，沿用原始工具結果。")
    return nil, nil
}

func runAfterToolExample() {
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("致命錯誤：建立模型失敗：%v", err)
    }

    capitalTool, err := functiontool.New(functiontool.Config{
        Name:        "getCapitalCity",
        Description: "取得指定國家的首都。",
    }, getCapitalCity)
    if err != nil {
        log.Fatalf("致命錯誤：建立 FunctionTool 失敗：%v", err)
    }

    llmCfg := llmagent.Config{
        Name:               "AgentWithAfterToolCallback",
        Model:              geminiModel,
        Tools:              []tool.Tool{capitalTool},
        AfterToolCallbacks: []llmagent.AfterToolCallback{onAfterTool},
        Instruction:        "你是一個會查詢首都的代理。請使用 getCapitalCity 工具。",
    }
    testAgent, err := llmagent.New(llmCfg)
    if err != nil {
        log.Fatalf("致命錯誤：建立代理失敗：%v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{
        AppName:         appName,
        Agent:          testAgent,
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("致命錯誤：建立 Runner 失敗：%v", err)
    }

    log.Println("--- 情境：結果應被修改 ---")
    runScenario(ctx, r, sessionService, appName, "session_tool_after_modify", nil, "capital of united states")
}
```

> Java

```java
import com.google.adk.agents.InvocationContext;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.BaseTool;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.common.collect.ImmutableMap;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import io.reactivex.rxjava3.core.Maybe;
import java.util.HashMap;
import java.util.Map;

public class AfterToolCallbackExample {

  private static final String APP_NAME = "AfterToolCallbackAgentApp";
  private static final String USER_ID = "user_1";
  private static final String SESSION_ID = "session_001";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    AfterToolCallbackExample example = new AfterToolCallbackExample();
    example.runAgent("What is the capital of the United States?");
  }

  // --- 定義一個簡單工具函式 ---
  @Schema(description = "取得指定國家的首都。")
  public static Map<String, Object> getCapitalCity(
      @Schema(description = "要查詢首都的國家名稱。") String country) {

    System.out.printf("--- 工具 'getCapitalCity' 執行中，country: %s ---%n", country);

    Map<String, String> capitals = new HashMap<>();
    capitals.put("united states", "Washington, D.C.");
    capitals.put("canada", "Ottawa");
    capitals.put("france", "Paris");
    capitals.put("germany", "Berlin");

    String capital = capitals.getOrDefault(country.toLowerCase(), "找不到 " + country + " 的首都");
    return ImmutableMap.of("result", capital);
  }

  // --- 定義回調函式（工具後置回調）---
  public Maybe<Map<String, Object>> simpleAfterToolModifier(
      InvocationContext invocationContext,
      BaseTool tool,
      Map<String, Object> args,
      ToolContext toolContext,
      Object toolResponse) {

    String agentName = invocationContext.agent().name();
    String toolName = tool.name();

    System.out.printf("[回調] 工具呼叫後觸發：tool='%s'，agent='%s'%n", toolName, agentName);
    System.out.printf("[回調] 使用的 args：%s%n", args);
    System.out.printf("[回調] 原始 toolResponse：%s%n", toolResponse);

    if (!(toolResponse instanceof Map)) {
      System.out.println("[回調] toolResponse 不是 Map，無法處理；直接沿用原始結果。");
      return Maybe.empty();
    }

    @SuppressWarnings("unchecked")
    Map<String, Object> responseMap = (Map<String, Object>) toolResponse;
    Object originalResultValue = responseMap.get("result");

    // --- 修改範例 ---
    if ("getCapitalCity".equals(toolName) && "Washington, D.C.".equals(originalResultValue)) {
      System.out.println("[回調] 偵測到 'Washington, D.C.'：修改工具回傳結果。");

      Map<String, Object> modifiedResponse = new HashMap<>(responseMap);
      modifiedResponse.put("result", originalResultValue + "（註：這是美國首都）");
      modifiedResponse.put("note_added_by_callback", true);

      System.out.printf("[回調] 修改後 toolResponse：%s%n", modifiedResponse);
      return Maybe.just(modifiedResponse);
    }

    System.out.println("[回調] 不修改，沿用原始工具結果。");
    return Maybe.empty();
  }

  public void runAgent(String query) {
    // --- 將函式包裝成 Tool ---
    FunctionTool capitalTool = FunctionTool.create(this.getClass(), "getCapitalCity");

    // --- 建立 Agent 並指定回調 ---
    LlmAgent myLlmAgent =
        LlmAgent.builder()
            .name(APP_NAME)
            .model(MODEL_NAME)
            .instruction("你是一個會使用 getCapitalCity 工具查詢首都的代理。請清楚回報結果。")
            .description("示範 after_tool_callback 的 LLM 代理")
            .tools(capitalTool)
            .afterToolCallback(this::simpleAfterToolModifier)
            .build();

    InMemoryRunner runner = new InMemoryRunner(myLlmAgent);

    Session session =
        runner.sessionService().createSession(APP_NAME, USER_ID, null, SESSION_ID).blockingGet();

    Content userMessage = Content.fromParts(Part.fromText(query));

    System.out.printf("%n--- 呼叫代理，輸入：\"%s\" ---%n", query);
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
```

</details>

## 更多說明

### 回調類型整合參考表

下表整合了所有回調類型的關鍵資訊，包含觸發時機、主要用途與回傳行為。

| 回調類型 | 觸發時機 | 主要用途 | 回傳值影響 |
|---------|---------|---------|-----------|
| **Before Agent** | 代理執行前（`_run_async_impl` 之前） | • 設置資源或狀態<br>• 執行驗證檢查<br>• 記錄入口點<br>• 修改調用上下文 | • 回傳 `Content`：跳過代理執行<br>• 回傳 `None`：允許繼續執行 |
| **After Agent** | 代理成功完成後（`_run_async_impl` 之後） | • 清理任務<br>• 執行後驗證<br>• 記錄完成<br>• 修改/替換最終輸出 | • 回傳 `Content`：取代代理原始輸出<br>• 回傳 `None`：使用代理原始輸出 |
| **Before Model** | LLM 模型呼叫前（僅 `LlmAgent`） | • 檢查/修改提示內容<br>• 記錄模型輸入<br>• 實施內容過濾<br>• 條件性跳過 LLM 呼叫 | • 回傳 `Content`：跳過 LLM，使用此內容作為回應<br>• 回傳 `None`：正常呼叫 LLM |
| **After Model** | LLM 模型回應後（僅 `LlmAgent`） | • 內容過濾與審核<br>• 增強/修改回應<br>• 記錄模型輸出<br>• 儲存快取 | • 回傳 `Content`：取代 LLM 原始回應<br>• 回傳 `None`：使用 LLM 原始回應 |
| **Before Tool** | 工具呼叫前（僅 `LlmAgent` 使用工具時） | • 驗證工具參數<br>• 記錄工具呼叫<br>• 修改/覆蓋參數<br>• 條件性跳過工具執行 | • 回傳修改後的 `args` dict：使用新參數<br>• 回傳 `{"_skip": True, "result": ...}`：跳過工具，使用 result<br>• 回傳 `None`：使用原始參數執行 |
| **After Tool** | 工具執行後（僅 `LlmAgent` 使用工具時） | • 驗證工具結果<br>• 增強/修改工具回應<br>• 記錄工具輸出<br>• 錯誤處理與重試邏輯 | • 回傳修改後的 dict：取代工具原始結果<br>• 回傳 `None`：使用工具原始結果 |

### 回調使用情境建議

**代理層級回調**（Before/After Agent）：
- ✅ 適合：全局性的流程控制、權限驗證、整體日誌記錄
- ❌ 不適合：LLM 特定的內容操作、工具執行細節

**模型層級回調**（Before/After Model）：
- ✅ 適合：提示工程、內容過濾、快取機制、LLM 輸出增強
- ❌ 不適合：工具執行流程控制、非 LLM 代理

**工具層級回調**（Before/After Tool）：
- ✅ 適合：參數驗證、工具結果增強、錯誤處理、工具特定日誌
- ❌ 不適合：LLM 提示修改、代理整體流程控制

### 回調執行順序

當一個 `LlmAgent` 執行並呼叫工具時，回調的觸發順序為：

```
1. Before Agent Callback
   ↓
2. Before Model Callback (第一次 LLM 呼叫)
   ↓
3. After Model Callback (第一次 LLM 呼叫)
   ↓
4. Before Tool Callback (若 LLM 決定呼叫工具)
   ↓
5. [工具執行]
   ↓
6. After Tool Callback
   ↓
7. Before Model Callback (第二次 LLM 呼叫，處理工具結果)
   ↓
8. After Model Callback (第二次 LLM 呼叫)
   ↓
9. After Agent Callback
```

### 回傳值處理原則

| 回調類型 | `None` / `empty()` | 回傳有效值 |
|---------|-------------------|----------|
| Before Agent | 繼續執行代理 | 跳過代理，使用回傳值作為輸出 |
| After Agent | 使用代理原始輸出 | 取代代理輸出 |
| Before Model | 正常呼叫 LLM | 跳過 LLM，使用回傳值 |
| After Model | 使用 LLM 原始回應 | 取代 LLM 回應 |
| Before Tool | 使用原始參數執行工具 | 使用修改參數 / 跳過工具（含 `_skip`） |
| After Tool | 使用工具原始結果 | 取代工具結果 |
