# Callbacks：觀察、自定義與控制代理行為

> 🔔 `更新日期：2026-01-30`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/callbacks/


[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

Callbacks（回呼）是 ADK 的核心功能，提供了一種強大的機制來掛鉤（hook）到代理的執行過程中。它們允許您在特定的、預定義的點觀察、自定義甚至控制代理的行為，而無需修改 ADK 框架的核心程式碼。

**它們是什麼？** 從本質上講，回呼是您定義的標準函數。接著，您在建立代理時將這些函數與代理關聯。ADK 框架會自動在關鍵階段呼叫您的函數，讓您進行觀察或干預。可以將其想像為代理處理過程中的檢查點：

* **在代理開始處理請求的主要工作之前，以及完成之後：** 當您要求代理執行某些操作（例如：回答問題）時，它會運行其內部邏輯來找出回應。
  * `Before Agent`（代理前）回呼在該特定請求的主要工作開始*之前*立即執行。
  * `After Agent`（代理後）回呼在代理完成該請求的所有步驟並準備好最終結果*之後*立即執行，但在結果返回之前。
  * 這個「主要工作」涵蓋了代理處理單個請求的*整個*過程。這可能涉及決定呼叫 LLM、實際呼叫 LLM、決定使用工具、使用工具、處理結果，以及最後組合答案。這些回呼本質上封裝了從接收輸入到為該次互動產生最終輸出的整個序列。
* **在向大型語言模型 (LLM) 發送請求之前，或從其接收回應之後：** 這些回呼（`Before Model`、`After Model`）允許您專門檢查或修改發往 LLM 以及來自 LLM 的數據。
* **在執行工具（如 Python 函數或其他代理）之前，或在其完成之後：** 同樣地，`Before Tool` 和 `After Tool` 回呼專門針對代理所呼叫工具的執行提供了控制點。

![intro_components.png](https://google.github.io/adk-docs/assets/callback_flow.png)

**為什麼要使用它們？** 回呼解鎖了顯著的靈活性並實現了高級的代理能力：

* **觀察與偵錯 (Observe & Debug)：** 在關鍵步驟記錄詳細資訊，以便進行監控和故障排除。
* **自定義與控制 (Customize & Control)：** 修改流經代理的數據（如 LLM 請求或工具結果），甚至根據您的邏輯完全繞過某些步驟。
* **實現護欄 (Implement Guardrails)：** 執行安全規則、驗證輸入/輸出，或防止不被允許的操作。
* **管理狀態 (Manage State)：** 在執行期間讀取或動態更新代理的會話狀態（session state）。
* **整合與增強 (Integrate & Enhance)：** 觸發外部操作（API 呼叫、通知）或添加快取等功能。

> [!TIP]
在實現安全護欄和策略時，建議使用 ADK 插件 (Plugins)，這比回呼 (Callbacks) 具有更好的模組化和靈活性。更多詳情請參閱 [安全護欄的回呼與插件](../safety-and-security/index.md#安全護欄的回呼與插件)。

**如何添加：**

<details>
<summary>程式碼</summary>

> Python

```python
# 基本回呼範例
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional

# --- 定義您的回呼函數 ---
def my_before_model_logic(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    print(f"代理 {callback_context.agent_name} 在模型呼叫前執行回呼")
    # ... 您的自定義邏輯放在這裡 ...
    return None # 允許模型呼叫繼續進行

# --- 在建立代理時註冊回呼 ---
my_agent = LlmAgent(
    name="MyCallbackAgent",
    model="gemini-2.0-flash", # 或您想要的模型
    instruction="請提供協助。",
    # 其他代理參數...
    before_model_callback=my_before_model_logic # 在此傳遞函數
)
```

> Typescript

```typescript
// 基本回呼範例
import {
  LlmAgent,
  InMemoryRunner,
  CallbackContext,
  LlmRequest,
  LlmResponse,
  Event,
  isFinalResponse,
} from "@google/adk";
import { createUserContent } from "@google/genai";
import type { Content } from "@google/genai";

const MODEL_NAME = "gemini-2.5-flash";
const APP_NAME = "basic_callback_app";
const USER_ID = "test_user_basic";
const SESSION_ID = "session_basic_001";


// --- 定義您的回呼函數 ---
function myBeforeModelLogic({
  context,
  request,
}: {
  context: CallbackContext;
  request: LlmRequest;
}): LlmResponse | undefined {
  console.log(
    `代理 ${context.agentName} 在模型呼叫前執行回呼`
  );
  // ... 您的自定義邏輯放在這裡 ...
  return undefined; // 允許模型呼叫繼續進行
}

// --- 在建立代理時註冊回呼 ---
const myAgent = new LlmAgent({
  name: "MyCallbackAgent",
  model: MODEL_NAME,
  instruction: "請提供協助。",
  beforeModelCallback: myBeforeModelLogic,
});
```

> Go

```go
package main

import (
    "context"
    "fmt"
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

// onBeforeModel 是在 LLM 呼叫前觸發的回呼函數。
func onBeforeModel(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
    log.Println("--- onBeforeModel 回呼已觸發 ---")
    log.Printf("即將發送的模型請求：%v\n", req)
    // 返回 nil 允許預設的 LLM 呼叫繼續進行。
    return nil, nil
}

func runBasicExample() {
    const (
        appName = "CallbackBasicApp"
        userID  = "test_user_123"
    )
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("建立模型失敗：%v", err)
    }

    // 在代理配置中註冊回呼函數。
    agentCfg := llmagent.Config{
        Name:                 "SimpleAgent",
        Model:                geminiModel,
        BeforeModelCallbacks: []llmagent.BeforeModelCallback{onBeforeModel},
    }
    simpleAgent, err := llmagent.New(agentCfg)
    if err != nil {
        log.Fatalf("建立代理失敗：%v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          simpleAgent,
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("建立執行器失敗：%v", err)
    }
}
```

> Java

```java
// 初始化帶有 BeforeModel 回呼的代理
import com.google.adk.agents.CallbackContext;
import com.google.adk.agents.Callbacks;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.LlmRequest;
import java.util.Optional;

public class AgentWithBeforeModelCallback {

  public static void main(String[] args) {
    // --- 定義您的回呼邏輯 ---
    Callbacks.BeforeModelCallbackSync myBeforeModelLogic =
        (CallbackContext callbackContext, LlmRequest llmRequest) -> {
          System.out.println(
              "代理 " + callbackContext.agentName() + " 在模型呼叫前執行回呼");
          // ... 您的自定義邏輯放在這裡 ...

          // 返回 Optional.empty() 以允許模型呼叫繼續進行，
          // 類似於 Python 範例中返回 None。
          // 如果您想要返回回應並跳過模型呼叫，
          // 您應該返回 Optional.of(yourLlmResponse)。
          return Optional.empty();
        };

    // --- 在建立代理時註冊回呼 ---
    LlmAgent myAgent =
        LlmAgent.builder()
            .name("MyCallbackAgent")
            .model("gemini-2.0-flash") // 或您想要的模型
            .instruction("請提供協助。")
            // 其他代理參數...
            .beforeModelCallbackSync(myBeforeModelLogic) // 在此傳遞回呼實作
            .build();
  }
}
```

</details>

## 回呼機制：攔截與控制

當 ADK 框架遇到可以運行回呼的點（例如：在呼叫 LLM 之前）時，它會檢查您是否為該代理提供了對應的回呼函數。如果您提供了，框架就會執行您的函數。

**上下文是關鍵 (Context is Key)：** 您的回呼函數並非在孤立狀態下被呼叫。框架會提供特殊的 **上下文對象** (`CallbackContext` 或 `ToolContext`) 作為參數。這些對象包含有關代理當前執行狀態的重要資訊，包括調用細節、會話狀態，以及可能引用的服務（如 artifact 或 memory）。您可以使用這些上下文對象來瞭解情況並與框架互動。（詳情請參閱專門的「上下文對象」章節）。

**控制流程（核心機制）：** 回呼最強大的地方在於其 **返回值** 如何影響代理後續的操作。這就是您攔截並控制執行流程的方式：

1. **`return None` (允許預設行為)：**

    * 具體的返回類型可能因語言而異。在 Java 中，等效的返回類型是 `Optional.empty()`。請參閱 API 文檔以獲取特定語言的指南。
    * 這是發出訊號的標準方式，表示您的回呼已完成工作（例如：記錄日誌、檢查、對 `llm_request` 等*可變*輸入參數進行細微修改），並且 ADK 代理應該 **繼續其正常操作**。
    * 對於 `before_*` 回呼（`before_agent`、`before_model`、`before_tool`），返回 `None` 意味著序列中的下一步（運行代理邏輯、呼叫 LLM、執行工具）將會發生。
    * 對於 `after_*` 回呼（`after_agent`、`after_model`、`after_tool`），返回 `None` 意味著將原封不動地使用前一步產生的結果（代理的輸出、LLM 的回應、工具的結果）。

2. **`return <特定對象>` (覆蓋預設行為)：**

    * 返回 *特定類型的對象*（而非 `None`）是您 **覆蓋** ADK 代理預設行為的方式。框架將使用您返回的對象，並*跳過*通常隨後進行的步驟，或*替換*剛剛生成的結果。
    * **`before_agent_callback` → `types.Content`**：跳過代理的主要執行邏輯 (`_run_async_impl` / `_run_live_impl`)。返回的 `Content` 對象會立即被視為代理在該輪的最終輸出。這對於直接處理簡單請求或執行訪問控制非常有用。
    * **`before_model_callback` → `LlmResponse`**：跳過對外部大型語言模型的呼叫。返回的 `LlmResponse` 對象將像來自 LLM 的實際回應一樣被處理。非常適合實現輸入護欄、提示詞驗證或提供快取的回應。
    * **`before_tool_callback` → `dict` 或 `Map`**：跳過實際工具函數（或子代理）的執行。返回的 `dict` 將作為工具呼叫的結果，通常隨後會傳回給 LLM。非常適合驗證工具參數、套用策略限制或返回模擬/快取的工具結果。
    * **`after_agent_callback` → `types.Content`**：*替換*代理運行邏輯剛產生的 `Content`。
    * **`after_model_callback` → `LlmResponse`**：*替換*從 LLM 接收到的 `LlmResponse`。對於清理輸出、添加標準免責聲明或修改 LLM 的回應結構非常有用。
    * **`after_tool_callback` → `dict` 或 `Map`**：*替換*工具返回的 `dict` 結果。允許在將工具輸出發送回 LLM 之前進行後處理或標準化。

**概念程式碼範例 (護欄)：**

此範例展示了使用 `before_model_callback` 實現護欄的常見模式。

<details>
<summary>程式碼</summary>

> Python

```python
# 使用 Before Model 回呼實現護欄
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.runners import Runner
from typing import Optional
from google.genai import types
from google.adk.sessions import InMemorySessionService

GEMINI_2_FLASH="gemini-2.0-flash"

# --- 定義回呼函數 ---
def simple_before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """檢查/修改 LLM 請求或跳過呼叫。"""
    agent_name = callback_context.agent_name
    print(f"[回呼] 代理 {agent_name} 在模型呼叫前執行")

    # 檢查請求內容中的最後一則使用者訊息
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
         if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[回呼] 檢查最後一則使用者訊息：'{last_user_message}'")

    # --- 修改範例 ---
    # 在系統指令中添加前綴
    original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
    prefix = "[由回呼修改] "
    # 確保 system_instruction 是 Content 且 parts 列表存在
    if not isinstance(original_instruction, types.Content):
         # 處理可能是字串的情況（雖然 config 期望是 Content）
         original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
    if not original_instruction.parts:
        original_instruction.parts.append(types.Part(text="")) # 如果不存在則添加空 part

    # 修改第一個 part 的文字
    modified_text = prefix + (original_instruction.parts[0].text or "")
    original_instruction.parts[0].text = modified_text
    llm_request.config.system_instruction = original_instruction
    print(f"[回呼] 已將系統指令修改為：'{modified_text}'")

    # --- 跳過範例 ---
    # 檢查最後一則使用者訊息是否包含 "BLOCK"
    if "BLOCK" in last_user_message.upper():
        print("[回呼] 發現 'BLOCK' 關鍵字。跳過 LLM 呼叫。")
        # 返回 LlmResponse 以跳過實際的 LLM 呼叫
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="LLM 呼叫已被 before_model_callback 阻擋。")],
            )
        )
    else:
        print("[回呼] 繼續進行 LLM 呼叫。")
        # 返回 None 允許（已修改的）請求發送到 LLM
        return None


# 建立 LlmAgent 並指派回呼
my_llm_agent = LlmAgent(
        name="ModelCallbackAgent",
        model=GEMINI_2_FLASH,
        instruction="你是一個有幫助的助理。", # 基礎指令
        description="展示 before_model_callback 的 LLM 代理",
        before_model_callback=simple_before_model_modifier # 在此指派函數
)

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# 會話與執行器
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# 代理互動
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理回應：", final_response)

# 注意：在 Colab 中，您可以直接在最上層使用 'await'。
# 如果將此程式碼作為獨立的 Python 腳本執行，您需要使用 asyncio.run() 或管理事件循環。
await call_agent_async("寫一個關於 BLOCK 的笑話")
```

> Typescript

```typescript
// 使用 Before Model 回呼實現護欄
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

// --- 定義回呼函數 ---
function simpleBeforeModelModifier({
    context,
    request,
}: {
    context: CallbackContext;
    request: any;
}): any | undefined {
    console.log(`[回呼] 代理 ${context.agentName} 在模型呼叫前執行`);

    // 檢查請求內容中的最後一則使用者訊息
    const lastUserMessage = request.contents?.at(-1)?.parts?.[0]?.text ?? "";
    console.log(`[回呼] 檢查最後一則使用者訊息：'${lastUserMessage}'`);

    // --- 修改範例 ---
    // 在系統指令中添加前綴。
    // 建立深拷貝以避免修改原始 agent 的 config 物件。
    const modifiedConfig = JSON.parse(JSON.stringify(request.config));
    const originalInstructionText =
        modifiedConfig.systemInstruction?.parts?.[0]?.text ?? "";
    const prefix = "[由回呼修改] ";
    modifiedConfig.systemInstruction = {
        role: "system",
        parts: [{ text: prefix + originalInstructionText }],
    };
    request.config = modifiedConfig; // 將修改後的 config 指派回 request
    console.log(
        `[回呼] 已將系統指令修改為：'${modifiedConfig.systemInstruction.parts[0].text}'`
    );

    // --- 跳過範例 ---
    // 檢查最後一則使用者訊息是否包含 "BLOCK"
    if (lastUserMessage.toUpperCase().includes("BLOCK")) {
        console.log("[回呼] 發現 'BLOCK' 關鍵字。跳過 LLM 呼叫。");
        // 回傳 LlmResponse 以跳過實際的 LLM 呼叫
        return {
            content: {
                role: "model",
                parts: [
                    { text: "LLM 呼叫已被 before_model_callback 阻擋。" },
                ],
            },
        };
    }

    console.log("[回呼] 繼續進行 LLM 呼叫。");
    // 回傳 undefined 允許（已修改的）請求發送到 LLM
    return undefined;
}

// --- 建立 LlmAgent 並指派回呼 ---
const myLlmAgent = new LlmAgent({
    name: "ModelCallbackAgent",
    model: MODEL_NAME,
    instruction: "你是一個有幫助的助理。", // 基礎指令
    description: "展示 before_model_callback 的 LLM 代理",
    beforeModelCallback: simpleBeforeModelModifier, // 在此指派函數
});

// --- 代理互動邏輯 ---
async function callAgentAndPrint(
    runner: InMemoryRunner,
    query: string,
    sessionId: string
) {
    console.log(`\n>>> 呼叫代理，查詢內容: "${query}"`);

    let finalResponseContent = "未收到最終回應。";
    const events = runner.runAsync({ userId: USER_ID, sessionId, newMessage: createUserContent(query) });

    for await (const event of events) {
        if (isFinalResponse(event) && event.content?.parts?.length) {
            finalResponseContent = event.content.parts
                .map((part: { text?: string }) => part.text ?? "")
                .join("");
        }
    }
    console.log("<<< 代理回應：", finalResponseContent);
}

// --- 執行互動 ---
async function main() {
    const runner = new InMemoryRunner({ agent: myLlmAgent, appName: APP_NAME });

    // 情境 1：回呼發現 "BLOCK" 並跳過模型呼叫
    await runner.sessionService.createSession({
        appName: APP_NAME,
        userId: USER_ID,
        sessionId: SESSION_ID_BLOCK,
    });
    await callAgentAndPrint(
        runner,
        "寫一個關於 BLOCK 的笑話",
        SESSION_ID_BLOCK
    );

    // 情境 2：回呼僅修改指令並繼續
    await runner.sessionService.createSession({
        appName: APP_NAME,
        userId: USER_ID,
        sessionId: SESSION_ID_NORMAL,
    });
    await callAgentAndPrint(runner, "寫一首短詩", SESSION_ID_NORMAL);
}

main();
```

> Go
```go
// 匯入回呼相關套件
package main

import (
    "context"
    "fmt"
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

// onBeforeModelGuardrail 是一個回呼函數，用於檢查 LLM 請求內容。
// 若內容包含禁止主題，則阻擋請求並回傳預設回應；否則允許請求繼續。
func onBeforeModelGuardrail(ctx agent.CallbackContext, req *model.LLMRequest) (*model.LLMResponse, error) {
    log.Println("--- onBeforeModelGuardrail 回呼已觸發 ---")

    // 檢查請求內容是否包含禁止主題
    for _, content := range req.Contents {
        for _, part := range content.Parts {
            if strings.Contains(part.Text, "finance") {
                log.Println("偵測到禁止主題 'finance'，阻擋 LLM 呼叫。")
                // 回傳非 nil 物件以覆蓋預設行為，阻止實際的 LLM 呼叫
                return &model.LLMResponse{
                    Content: &genai.Content{
                        Parts: []*genai.Part{{Text: "很抱歉，我無法討論財經相關主題。"}},
                        Role:  "model",
                    },
                }, nil
            }
        }
    }

    log.Println("未發現禁止主題，允許 LLM 呼叫繼續。")
    // 回傳 nil 允許預設的 LLM 呼叫繼續進行
    return nil, nil
}

func runGuardrailExample() {
    const (
        appName = "GuardrailApp"
        userID  = "test_user_456"
    )
    ctx := context.Background()
    geminiModel, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        log.Fatalf("建立模型失敗：%v", err)
    }

    agentCfg := llmagent.Config{
        Name:                 "ChatAgent",
        Model:                geminiModel,
        BeforeModelCallbacks: []llmagent.BeforeModelCallback{onBeforeModelGuardrail},
    }
    chatAgent, err := llmagent.New(agentCfg)
    if err != nil {
        log.Fatalf("建立代理失敗：%v", err)
    }

    sessionService := session.InMemoryService()
    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          chatAgent,
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("建立執行器失敗：%v", err)
    }
}
```

> Java

```java
// 初始化 Before Model 護欄範例
import com.google.adk.agents.CallbackContext;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.models.LlmRequest;
import com.google.adk.models.LlmResponse;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class BeforeModelGuardrailExample {

    private static final String MODEL_ID = "gemini-2.0-flash";
    private static final String APP_NAME = "guardrail_app";
    private static final String USER_ID = "user_1";

    public static void main(String[] args) {
        BeforeModelGuardrailExample example = new BeforeModelGuardrailExample();
        example.defineAgentAndRun("請介紹量子運算。這是一個測試。");
    }

    // --- 定義回呼邏輯 ---
    // 檢查使用者輸入是否包含 "BLOCK"，若有則阻擋 LLM 呼叫，否則照常執行。
    public Optional<LlmResponse> simpleBeforeModelModifier(
            CallbackContext callbackContext, LlmRequest llmRequest) {
        System.out.println("[回呼] 代理 " + callbackContext.agentName() + " 在模型呼叫前執行");

        // 檢查請求內容中的最後一則使用者訊息
        String lastUserMessageText = "";
        List<Content> requestContents = llmRequest.contents();
        if (requestContents != null && !requestContents.isEmpty()) {
            Content lastContent = requestContents.get(requestContents.size() - 1);
            if (lastContent.role().isPresent() && "user".equals(lastContent.role().get())) {
                lastUserMessageText =
                        lastContent.parts().orElse(List.of()).stream()
                                .flatMap(part -> part.text().stream())
                                .collect(Collectors.joining(" "));
            }
        }
        System.out.println("[回呼] 檢查最後一則使用者訊息：'" + lastUserMessageText + "'");

        String prefix = "[由回呼修改] ";
        GenerateContentConfig currentConfig =
                llmRequest.config().orElse(GenerateContentConfig.builder().build());
        Optional<Content> optOriginalSystemInstruction = currentConfig.systemInstruction();

        Content conceptualModifiedSystemInstruction;
        if (optOriginalSystemInstruction.isPresent()) {
            Content originalSystemInstruction = optOriginalSystemInstruction.get();
            List<Part> originalParts =
                    new ArrayList<>(originalSystemInstruction.parts().orElse(List.of()));
            String originalText = "";

            if (!originalParts.isEmpty()) {
                Part firstPart = originalParts.get(0);
                if (firstPart.text().isPresent()) {
                    originalText = firstPart.text().get();
                }
                originalParts.set(0, Part.fromText(prefix + originalText));
            } else {
                originalParts.add(Part.fromText(prefix));
            }
            conceptualModifiedSystemInstruction =
                    originalSystemInstruction.toBuilder().parts(originalParts).build();
        } else {
            conceptualModifiedSystemInstruction =
                    Content.builder()
                            .role("system")
                            .parts(List.of(Part.fromText(prefix)))
                            .build();
        }

        // 示範如何建立帶有修改後 config 的新 LlmRequest
        llmRequest =
                llmRequest.toBuilder()
                        .config(
                                currentConfig.toBuilder()
                                        .systemInstruction(conceptualModifiedSystemInstruction)
                                        .build())
                        .build();

        System.out.println(
                "[回呼] 已將系統指令修改為：'"
                        + llmRequest.config().get().systemInstruction().get().parts().get().get(0).text().get());

        // --- 跳過範例 ---
        // 檢查最後一則使用者訊息是否包含 "BLOCK"
        if (lastUserMessageText.toUpperCase().contains("BLOCK")) {
            System.out.println("[回呼] 發現 'BLOCK' 關鍵字。跳過 LLM 呼叫。");
            LlmResponse skipResponse =
                    LlmResponse.builder()
                            .content(
                                    Content.builder()
                                            .role("model")
                                            .parts(
                                                    List.of(
                                                            Part.builder()
                                                                    .text("LLM 呼叫已被 before_model_callback 阻擋。")
                                                                    .build()))
                                            .build())
                            .build();
            return Optional.of(skipResponse);
        }
        System.out.println("[回呼] 繼續進行 LLM 呼叫。");
        // 回傳 Optional.empty() 允許（已修改的）請求送往 LLM
        return Optional.empty();
    }

    public void defineAgentAndRun(String prompt) {
        // --- 建立 LlmAgent 並指派回呼 ---
        LlmAgent myLlmAgent =
                LlmAgent.builder()
                        .name("ModelCallbackAgent")
                        .model(MODEL_ID)
                        .instruction("你是一個有幫助的助理。") // 基礎指令
                        .description("展示 before_model_callback 的 LLM 代理")
                        .beforeModelCallbackSync(this::simpleBeforeModelModifier) // 指派回呼
                        .build();

        // 會話與執行器
        InMemoryRunner runner = new InMemoryRunner(myLlmAgent, APP_NAME);
        // InMemoryRunner 會自動建立 session service。使用該 service 建立會話
        Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
        Content userMessage =
                Content.fromParts(Part.fromText(prompt));

        // 執行代理
        Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

        // 串流事件回應
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

透過理解這種返回 `None` 與返回特定對象的機制，您可以精確控制代理的執行路徑，使回呼成為使用 ADK 構建複雜且可靠代理的重要工具。

## 更多說明
### 回呼機制整理說明

下表將「回呼回傳值」如何影響流程做成速查：

| 回傳值 | 適用回呼類別 | 框架行為（流程影響） | 常見用途 |
| --- | --- | --- | --- |
| `None`（或語言等效值） | `before_*`（`before_agent` / `before_model` / `before_tool`） | 表示回呼只做觀察/微調；框架**繼續**下一步（跑代理邏輯 / 呼叫 LLM / 執行工具）。 | 記錄日誌、驗證、對「可變」入參做小幅修改（例如調整 `llm_request`）。 |
| `None`（或語言等效值） | `after_*`（`after_agent` / `after_model` / `after_tool`） | 表示回呼不覆寫結果；框架**原封不動**沿用上一步的輸出（代理輸出 / LLM 回應 / 工具結果）。 | 觀察、監控、計量（metrics）紀錄，不改動結果。 |
| **特定型別物件**（非 `None`） | `before_*` | 以「回呼回傳物件」作為結果，並**跳過**通常接下來會做的步驟。 | 護欄、快取、參數策略、模擬/短路（short-circuit）行為。 |
| **特定型別物件**（非 `None`） | `after_*` | 以「回呼回傳物件」**替換**上一步產生的結果。 | 結果清理/標準化、補充免責聲明、統一輸出格式。 |

各回呼點在「回傳非 `None`」時，可用來覆寫/替換的型別與效果如下：

| 回呼點 | 回傳型別（非 `None`） | 影響 |
| --- | --- | --- |
| `before_agent_callback` | `types.Content` | **跳過**代理主要執行邏輯（`_run_async_impl` / `_run_live_impl`），直接把回傳的 `Content` 視為該輪最終輸出。 |
| `before_model_callback` | `LlmResponse` | **跳過**實際 LLM 呼叫，改用回傳的 `LlmResponse` 當作「模型已回覆」。 |
| `before_tool_callback` | `dict` / `Map` | **跳過**工具（或子代理）執行，直接把回傳值當作工具結果（通常接著回傳給 LLM）。 |
| `after_agent_callback` | `types.Content` | **替換**代理運行邏輯剛產生的 `Content`。 |
| `after_model_callback` | `LlmResponse` | **替換**從 LLM 收到的 `LlmResponse`。 |
| `after_tool_callback` | `dict` / `Map` | **替換**工具回傳的 `dict` 結果（送回 LLM 前可先標準化/後處理）。 |

> 補充：不同語言的「允許預設行為」等效回傳值可能不同，例如 Java 常用 `Optional.empty()` 作為 `None` 的等效。
