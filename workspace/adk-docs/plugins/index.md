# 外掛程式 (Plugins)

🔔 `更新日期：2026-01-18`

[`ADK 支援`: `Python v1.7.0`]

Agent Development Kit (ADK) 中的外掛程式 (Plugin) 是一個自定義程式碼模組，可以使用回呼掛鉤 (callback hooks) 在代理 (agent) 工作流生命週期的各個階段執行。您可以使用外掛程式來實現適用於整個代理工作流的功能。外掛程式的一些典型應用如下：

-   **記錄與追蹤 (Logging and tracing)**：建立代理、工具和生成式 AI 模型活動的詳細日誌，用於偵錯和效能分析。
-   **原則強制執行 (Policy enforcement)**：實作安全防護欄 (guardrails)，例如檢查使用者是否有權使用特定工具並在其沒有權限時阻止執行的函式。
-   **監控與指標 (Monitoring and metrics)**：收集並匯出 Token 使用量、執行時間和調用次數等指標到 [Google Cloud Observability](https://cloud.google.com/stackdriver/docs) (原名 Stackdriver) 或 Prometheus 等監控系統。
-   **回應快取 (Response caching)**：檢查請求是否曾發出過，以便返回快取的回應，從而跳過昂貴或耗時的 AI 模型或工具調用。
-   **請求或回應修改 (Request or response modification)**：動態地為 AI 模型提示 (prompts) 增加資訊，或標準化工具輸出回應。

> [!TIP] 提示
    在實作安全防護欄和原則時，使用 ADK 外掛程式比使用回呼 (Callbacks) 具有更好的模組化和靈活性。更多詳細資訊，請參閱 [安全防護欄的回呼與外掛程式](https://google.github.io/adk-docs/safety/#callbacks-and-plugins-for-security-guardrails)。

> [!WARNING] 注意
    [ADK 網路介面](../evaluation/index.md#1-adk-web---透過-web-ui-執行評估)不支援外掛程式。如果您的 ADK 工作流使用了外掛程式，則必須在不使用網路介面的情況下執行工作流。

## 外掛程式如何運作？

ADK 外掛程式擴充了 `BasePlugin` 類別，並包含一個或多個 `callback` 方法，指示外掛程式應在代理生命週期的哪個位置執行。您可以透過在代理的 `Runner` 類別中註冊外掛程式，將其整合到代理中。有關在代理應用程式中如何以及在哪裡觸發外掛程式的更多資訊，請參閱 [外掛程式回呼掛鉤](#外掛程式回呼掛鉤)。

外掛程式功能建立在 [回呼 (Callbacks)](../callbacks/index.md) 之上，這是 ADK 可擴充架構的關鍵設計元素。典型的代理回呼是針對 *單個代理、單個工具* 的 *特定任務* 進行設定的，而外掛程式只需在 `Runner` 上註冊 *一次*，其回呼就會 *全域性地* 應用於該執行器管理的所有代理、工具和 LLM 調用。外掛程式讓您可以將相關的回呼函式封裝在一起，以便在整個工作流中使用。這使得外掛程式成為實作橫跨整個代理應用程式功能的理想解決方案。

## 預建外掛程式

ADK 包含多個您可以立即加入到代理工作流的外掛程式：

*   [**反思與重試工具 (Reflect and Retry Tools)**](./reflect-and-retry.md)：追蹤工具故障並智慧地重試工具請求。
*   [**BigQuery 分析 (BigQuery Analytics)**](https://google.github.io/adk-docs/observability/bigquery-agent-analytics/)：使用 BigQuery 啟用代理日誌記錄與分析。
*   [**內容過濾器 (Context Filter)**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/context_filter_plugin.py)：過濾生成式 AI 上下文以縮減其大小。
*   [**全域指令 (Global Instruction)**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/global_instruction_plugin.py)：在應用程式層級提供全域指令功能的外掛程式。
*   [**將檔案儲存為 Artifacts (Save Files as Artifacts)**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/save_files_as_artifacts_plugin.py)：將使用者訊息中包含的檔案儲存為構件 (Artifacts)。
*   [**記錄 (Logging)**](https://github.com/google/adk-python/blame/main/src/google/adk/plugins/logging_plugin.py)：在代理工作流的每個回呼點記錄重要資訊。

## 定義與註冊外掛程式

本節說明如何定義外掛程式類別並將其註冊為代理工作流的一部分。如需完整的程式碼範例，請參閱儲存庫中的 [外掛程式基礎 (Plugin Basic)](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_basic)。

### 建立外掛程式類別

首先擴充 `BasePlugin` 類別並加入一個或多個 `callback` 方法，如下列程式碼範例所示：

<details>
<summary>範例說明</summary>

> Python

詳細可實現方法，可參考程式碼：[base_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/base_plugin.py)

```py title="count_plugin.py"
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin

class CountInvocationPlugin(BasePlugin):
    """一個用於計算代理和工具調用次數的自定義外掛程式。"""

    def __init__(self) -> None:
        """使用計數器初始化外掛程式。"""
        # 初始化父類別，設定外掛程式名稱為 "count_invocation"
        super().__init__(name="count_invocation")
        self.agent_count: int = 0
        self.tool_count: int = 0
        self.llm_request_count: int = 0

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        """計算代理執行次數。"""
        # 每次代理執行前增加計數
        self.agent_count += 1
        print(f"[Plugin] Agent run count: {self.agent_count}")

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        """計算 LLM 請求次數。"""
        # 每次 LLM 請求前增加計數
        self.llm_request_count += 1
        print(f"[Plugin] LLM request count: {self.llm_request_count}")
```

> typescript

```typescript title="count_plugin.ts"
import { BaseAgent, BasePlugin, CallbackContext } from "@google/adk";
import type { LlmRequest, LlmResponse } from "@google/adk";
import type { Content } from "@google/genai";


/**
 * 一個用於計算代理和工具調用次數的自定義外掛程式。
 */
export class CountInvocationPlugin extends BasePlugin {
    public agentCount = 0;
    public toolCount = 0;
    public llmRequestCount = 0;

    constructor() {
        // 初始化外掛程式名稱
        super("count_invocation");
    }

    /**
     * 計算代理執行次數。
     */
    async beforeAgentCallback(
        agent: BaseAgent,
        callbackContext: CallbackContext
    ): Promise<Content | undefined> {
        // 增加計數並列印資訊
        this.agentCount++;
        console.log(`[Plugin] Agent run count: ${this.agentCount}`);
        return undefined;
    }

    /**
     * 計算 LLM 請求次數。
     */
    async beforeModelCallback(
        callbackContext: CallbackContext,
        llmRequest: LlmRequest
    ): Promise<LlmResponse | undefined> {
        // 增加計數並列印資訊
        this.llmRequestCount++;
        console.log(`[Plugin] LLM request count: ${this.llmRequestCount}`);
        return undefined;
    }
}
```

</details>

此範例程式碼實作了 `before_agent_callback` 和 `before_model_callback` 的回呼，以便在代理的生命週期中計算這些任務的執行情況。

### 註冊外掛程式類別

在代理初始化期間，使用 `plugins` 參數將外掛程式類別註冊為 `Runner` 類別的一部分。您可以使用此參數指定多個外掛程式。下列程式碼範例顯示如何將前一節定義的 `CountInvocationPlugin` 外掛程式註冊到一個簡單的 ADK 代理中。

<details>
<summary>範例說明</summary>

> Python

```py
from google.adk.runners import InMemoryRunner
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import asyncio

# 匯入外掛程式。
from .count_plugin import CountInvocationPlugin

async def hello_world(tool_context: ToolContext, query: str):
    """一個簡單的工具，用於列印 hello world 與查詢內容。"""
    print(f'Hello world: query is [{query}]')

root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world',
    description='使用使用者查詢列印 hello world。',
    instruction="""使用 hello_world 工具來列印 hello world 和使用者查詢。
    """,
    tools=[hello_world],
)

async def main():
    """代理的主要進入點。"""
    prompt = 'hello world'
    runner = InMemoryRunner(
        agent=root_agent,
        app_name='test_app_with_plugin',

        # 在此處加入您的外掛程式。您可以加入多個外掛程式。
        plugins=[CountInvocationPlugin()],
    )

    # 其餘部分與啟動一般 ADK runner 相同。
    session = await runner.session_service.create_session(
        user_id='user',
        app_name='test_app_with_plugin',
    )

    # 以非同步方式執行代理並處理事件
    async for event in runner.run_async(
        user_id='user',
        session_id=session.id,
        new_message=types.Content(
            role='user', parts=[types.Part.from_text(text=prompt)]
        )
    ):
        print(f'** Got event from {event.author}')

if __name__ == "__main__":
    asyncio.run(main())
```

> typescript

```typescript
import { InMemoryRunner, LlmAgent, FunctionTool } from "@google/adk";
import type { Content } from "@google/genai";
import { z } from "zod";

// 匯入外掛程式。
import { CountInvocationPlugin } from "./count_plugin.ts";

const HelloWorldInput = z.object({
    query: z.string().describe("要列印的查詢字串。"),
});

async function helloWorld({ query }: z.infer<typeof HelloWorldInput>): Promise<{ result: string }> {
    const output = `Hello world: query is [${query}]`;
    console.log(output);
    // 工具應返回字串或 JSON 相容的物件
    return { result: output };
}

const helloWorldTool = new FunctionTool({
    name: "hello_world",
    description: "使用使用者查詢列印 hello world。",
    parameters: HelloWorldInput,
    execute: helloWorld,
});

const rootAgent = new LlmAgent({
    model: "gemini-2.5-flash", // 從您的 Python 程式碼中保留
    name: "hello_world",
    description: "使用使用者查詢列印 hello world。",
    instruction: `使用 hello_world 工具來列印 hello world 和使用者查詢。`,
    tools: [helloWorldTool],
});

/**
* 代理的主要進入點。
*/
async function main(): Promise<void> {
    const prompt = "hello world";
    const runner = new InMemoryRunner({
        agent: rootAgent,
        appName: "test_app_with_plugin",

        // 在此處加入您的外掛程式。您可以加入多個外掛程式。
        plugins: [new CountInvocationPlugin()],
    });

    // 其餘部分與啟動一般 ADK runner 相同。
    const session = await runner.sessionService.createSession({
        userId: "user",
        appName: "test_app_with_plugin",
    });

    // runAsync 在 TypeScript 中返回一個非同步可迭代串流
    const runStream = runner.runAsync({
        userId: "user",
        sessionId: session.id,
        newMessage: {
        role: "user",
        parts: [{ text: prompt }],
        },
    });

    // 使用 'for await...of' 迴圈處理非同步串流
    for await (const event of runStream) {
        console.log(`** Got event from ${event.author}`);
    }
}

main();
```

</details>

### 使用外掛程式執行代理

像平常一樣執行外掛程式。下列顯示如何在命令列執行：

<details>
<summary>範例說明</summary>

> Python

```sh
python3 -m path.to.main.py
```

> typescript

```sh
npx ts-node path.to.main.ts
```

</details>

[ADK 網路介面](../evaluation/index.md#1-adk-web---透過-web-ui-執行評估)不支援外掛程式。如果您的 ADK 工作流使用了外掛程式，則必須在不使用網路介面的情況下執行工作流。

上述代理的輸出應如下所示：

```log
[Plugin] Agent run count: 1
[Plugin] LLM request count: 1
** Got event from hello_world
Hello world: query is [hello world]
** Got event from hello_world
[Plugin] LLM request count: 2
** Got event from hello_world
```


有關執行 ADK 代理的更多資訊，請參閱 [快速入門](https://google.github.io/adk-docs/get-started/quickstart/#set-up-the-model) 指南。

## 使用外掛程式建構工作流

外掛程式回呼掛鉤是一種實作邏輯的機制，可以攔截、修改甚至控制代理的執行生命週期。每個掛鉤都是外掛程式類別中的一個特定方法，您可以實作這些方法以便在關鍵時刻執行程式碼。您可以根據掛鉤的傳回值選擇兩種作業模式：

-   **觀察 (To Observe)**：實作一個沒有傳回值 (`None`) 的掛鉤。這種方法適用於記錄或收集指標等任務，因為它允許代理的工作流繼續執行下一步而不受干擾。例如，您可以在外掛程式中使用 `after_tool_callback` 來記錄每個工具的結果以供偵錯。
-   **干預 (To Intervene)**：實作一個掛鉤並傳回一個值。這種方法會讓工作流短路。`Runner` 會停止處理，跳過任何後續的外掛程式和原本預定的動作 (例如模型調用)，並將外掛程式回呼的傳回值作為結果。一個常見的案例是實作 `before_model_callback` 來傳回快取的 `LlmResponse`，從而防止冗餘且昂貴的 API 調用。
-   **修正 (To Amend)**：實作一個掛鉤並修改 Context 物件。這種方法允許您在不中斷模組執行的情況下，修改即將執行的模組的上下文資料。例如，為 Model 物件的執行加入額外的、標準化的提示文字。

**注意：** 外掛程式回呼函式優先於在物件層級實作的回呼。這種行為意味著任何外掛程式回呼程式碼都會在任何 Agent、Model 或 Tool 物件回呼執行 *之前* 執行。此外，如果外掛程式層級的代理回呼傳回任何值 (而非空的 `None` 回應)，則 Agent、Model 或 Tool 層級的回呼將 *不會被執行* (被跳過)。

外掛程式設計建立了程式碼執行的層級結構，並將全域關注點與本地代理邏輯分離。外掛程式是您建構的有狀態 *模組* (例如 `PerformanceMonitoringPlugin`)，而回呼掛鉤則 (callback hook) 是該模組內被執行的特定 *函式*。這種架構在以下關鍵方面與標準代理回呼有根本的不同：

-   **範圍 (Scope)**：外掛程式掛鉤是 *全域的*。您在 `Runner` 上註冊一次外掛程式，其掛鉤就會普遍應用於它管理的每個 Agent、Model 和 Tool。相比之下，代理回呼是 *本地的*，在特定的代理實體上單獨設定。
-   **執行順序 (Execution Order)**：外掛程式具有 *優先權*。對於任何給定的事件，外掛程式掛鉤總是先於任何對應的代理回呼執行。這種系統行為使得外掛程式成為實作安全性原則、通用快取以及在整個應用程式中保持一致記錄等橫切關注點 (cross-cutting features) 的正確架構選擇。

### 代理回呼與外掛程式

如前所述，外掛程式和代理回呼之間存在一些功能上的相似之處。下表更詳細地比較了外掛程式和代理回呼之間的差異。

<table>
  <thead>
    <tr>
      <th></th>
      <th><strong>外掛程式 (Plugins)</strong></th>
      <th><strong>代理回呼 (Agent Callbacks)</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>範圍</strong></td>
      <td><strong>全域</strong>：應用於 <code>Runner</code> 中的所有代理/工具/LLM。</td>
      <td><strong>本地</strong>：僅應用於設定了它們的特定代理實體。</td>
    </tr>
    <tr>
      <td><strong>主要使用案例</strong></td>
      <td><strong>水平功能</strong>：日誌記錄、原則、監控、全域快取。</td>
      <td><strong>特定代理邏輯</strong>：修改單個代理的行為或狀態。</td>
    </tr>
    <tr>
      <td><strong>設定</strong></td>
      <td>在 <code>Runner</code> 上設定一次。</td>
      <td>在每個 <code>BaseAgent</code> 實體上單獨設定。</td>
    </tr>
    <tr>
      <td><strong>執行順序</strong></td>
      <td>外掛程式回呼在代理回呼 <strong>之前</strong> 執行。</td>
      <td>代理回呼在外掛程式回呼 <strong>之後</strong> 執行。</td>
    </tr>
  </tbody>
</table>

## 外掛程式回呼掛鉤 (callback hooks)

您透過在外掛程式類別中定義回呼函式來決定何時調用外掛程式。在接收到使用者訊息時、在調用 `Runner`、`Agent`、`Model` 或 `Tool` 之前和之後、對於 `Events` 以及在 `Model` 或 `Tool` 發生錯誤時，都可以使用回呼。這些回呼包含在您的 Agent、Model 和 Tool 類別中定義的任何回呼，並具有優先權。

下圖說明了在代理工作流期間您可以附加並執行外掛程式功能的各個回呼點：

![ADK 外掛程式回呼掛鉤](https://google.github.io/adk-docs/assets/workflow-plugin-hooks.svg)
**圖 1.** 包含外掛程式回呼掛鉤位置的 ADK 代理工作流圖。

下列章節更詳細地說明外掛程式可用的回呼掛鉤。

-   [使用者訊息回呼 (User message callbacks)](#使用者訊息回呼)
-   [執行器啟動回呼 (Runner start callbacks)](#執行器啟動回呼)
-   [代理執行回呼 (Agent Execution callbacks)](#代理執行回呼)
-   [模型回呼 (Model callbacks)](#模型回呼)
-   [工具回呼 (Tool callbacks)](#工具回呼)
-   [執行器結束回呼 (Runner end callbacks)](#執行器結束回呼)

### 使用者訊息回呼

*使用者訊息*回呼 (`on_user_message_callback`) 在使用者傳送訊息時發生。`on_user_message_callback` 是第一個執行的掛鉤，讓您有機會檢查或修改初始輸入。

-   **執行時機**：在 `runner.run()` 之後立即發生，在任何其他處理之前。
-   **目的**：檢查或修改使用者原始輸入的第一個機會。
-   **流程控制**：傳回一個 `types.Content` 物件以 **替換** 使用者的原始訊息。

下列程式碼範例顯示此回呼的基本語法：

<details>
<summary>範例說明</summary>

> Python

```py
async def on_user_message_callback(
    self,
    *,
    invocation_context: InvocationContext,
    user_message: types.Content,
) -> Optional[types.Content]:
    """處理使用者傳送的原始訊息。"""
    # 實作您的邏輯
    return None
```

> typescript

```typescript
async onUserMessageCallback(
    invocationContext: InvocationContext,
    user_message: Content
): Promise<Content | undefined> {
    // 在此處實作您的邏輯
    return undefined;
}
```

</details>

### 執行器啟動回呼

*執行器啟動 (Runner start)* 回呼 (`before_run_callback`) 在 `Runner` 物件獲取可能已修改的使用者訊息並準備執行時發生。`before_run_callback` 在此處觸發，允許在任何代理邏輯開始之前進行全域設定。

-   **執行時機**：在調用 `runner.run()` 後立即執行，在任何其他處理之前。
-   **目的**：檢查或修改使用者原始輸入的第一個機會。
-   **流程控制**：傳回一個 `types.Content` 物件以 **替換** 使用者的原始訊息。

下列程式碼範例顯示此回呼的基本語法：

<details>
<summary>範例說明</summary>

> Python

```py
async def before_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[types.Content]:
    """在 Runner 開始處理前執行的回呼。"""
    # 實作您的邏輯
    return None
```

> typescript

```typescript
async beforeRunCallback(invocationContext: InvocationContext): Promise<Content | undefined> {
    // 在此處實作您的邏輯
    return undefined;
}
```

</details>

### 代理執行回呼

*代理執行*回呼 (`before_agent`, `after_agent`) 在 `Runner` 物件調用代理時發生。`before_agent_callback` 在代理的主要工作開始前立即執行。主要工作涵蓋了代理處理請求的整個過程，其中可能涉及調用模型或工具。在代理完成所有步驟並準備好結果後，`after_agent_callback` 會執行。

**注意：** 實作這些回呼的外掛程式會在代理層級的回呼執行 *之前* 執行。此外，如果外掛程式層級的代理回呼傳回除了 `None` 或 null 回應之外的任何內容，則代理層級的回呼將 *不會被執行* (被跳過)。

有關作為代理物件一部分定義的代理回呼的更多資訊，請參閱 [回呼類型](../callbacks/types-of-callbacks.md#代理生命週期回調-agent-lifecycle-callbacks)。

### 模型回呼

模型回呼 **(`before_model`, `after_model`, `on_model_error`)** 在 Model 物件執行之前和之後發生。外掛程式功能也支援在發生錯誤時的回呼，詳情如下：

-   如果代理需要調用 AI 模型，會先執行 `before_model_callback`。
-   如果模型調用成功，接著執行 `after_model_callback`。
-   如果模型調用失敗並出現異常，則會觸發 `on_model_error_callback`，以便進行優雅的回復。

**注意：** 實作 **`before_model`** 和 `**after_model`** 回呼方法的外掛程式會在模型層級的回呼執行 *之前* 執行。此外，如果外掛程式層級的模型回呼傳回除了 `None` 或 null 回應之外的任何內容，則模型層級的回呼將 *不會被執行* (被跳過)。

#### 模型錯誤回呼詳情

Model 物件的錯誤回呼僅由外掛程式功能支援，運作方式如下：

-   **執行時機**：在模型調用期間引發異常時。
-   **常見使用案例**：優雅的錯誤處理、記錄特定錯誤，或傳回備用回應，例如「AI 服務目前無法使用」。
-   **流程控制**：
    -   傳回一個 `LlmResponse` 物件以 **抑制異常** 並提供備用結果。
    -   傳回 `None` 以允許引發原始異常。

**註**：如果 Model 物件的執行傳回 `LlmResponse`，系統將恢復執行流程，且 `after_model_callback` 將正常觸發。

下列程式碼範例顯示此回呼的基本語法：

<details>
<summary>範例說明</summary>

> Python

```py
async def on_model_error_callback(
    self,
    *,
    callback_context: CallbackContext,
    llm_request: LlmRequest,
    error: Exception,
) -> Optional[LlmResponse]:
    """當模型執行出錯時執行的回呼。"""
    # 處理模型錯誤
    return None
```

> typescript

```typescript
async onModelErrorCallback(
    callbackContext: CallbackContext,
    llmRequest: LlmRequest,
    error: Error
): Promise<LlmResponse | undefined> {
    // 在此處實作您的錯誤處理邏輯
    return undefined;
}
```

</details>

### 工具回呼

外掛程式的工具回呼 **(`before_tool`, `after_tool`, `on_tool_error`)** 在工具執行之前或之後，或發生錯誤時發生。外掛程式功能也支援在發生錯誤時的回呼，詳情如下：

-   當代理執行工具時，會先執行 `before_tool_callback`。
-   如果工具執行成功，接著執行 `after_tool_callback`。
-   如果工具引發異常，則會觸發 `on_tool_error_callback`，讓您有機會處理失敗。如果 `on_tool_error_callback` 傳回一個字典 (dict)，則 `after_tool_callback` 將正常觸發。

**注意：** 實作這些回呼的外掛程式會在工具層級的回呼執行 *之前* 執行。此外，如果外掛程式層級的工具回呼傳回除了 `None` 或 null 回應之外的任何內容，則工具層級的回呼將 *不會被執行* (被跳過)。

#### 工具錯誤回呼詳情

Tool 物件的錯誤回呼僅由外掛程式功能支援，運作方式如下：

-   **執行時機**：在執行工具的 `run` 方法期間引發異常時。
-   **目的**：擷取特定的工具異常 (如 `APIError`)、記錄失敗，並將使用者友好的錯誤訊息傳回給 LLM。
-   **流程控制**：傳回一個 `dict` 以 **抑制異常** 並提供備用結果。傳回 `None` 以允許引發原始異常。

**註**：藉由傳回一個 `dict`，這會恢復執行流程，且 `after_tool_callback` 將正常觸發。

下列程式碼範例顯示此回呼的基本語法：

<details>
<summary>範例說明</summary>

> Python

```py
async def on_tool_error_callback(
    self,
    *,
    tool: BaseTool,
    tool_args: dict[str, Any],
    tool_context: ToolContext,
    error: Exception,
) -> Optional[dict]:
    """當工具執行出錯時執行的回呼。"""
    # 處理工具錯誤
    return None
```

> typescript

```typescript
async onToolErrorCallback(
    tool: BaseTool,
    toolArgs: { [key: string]: any },
    toolContext: ToolContext,
    error: Error
): Promise<{ [key:string]: any } | undefined> {
    // 在此處實作您的錯誤處理邏輯
    return undefined;
}
```

</details>

### 事件回呼

*事件回呼* (`on_event_callback`) 在代理產生輸出 (例如文字回應或工具調用結果) 時發生，代理會將其作為 `Event` 物件產生。`on_event_callback` 會針對每個事件觸發，允許您在將其串流傳輸到用戶端之前對其進行修改。

-   **執行時機**：在代理產生 `Event` 之後但在傳送給使用者之前。代理的一次執行可能會產生多個事件。
-   **目的**：用於修改或豐富事件 (例如加入中繼資料) 或根據特定事件觸發副作用。
-   **流程控制**：傳回一個 `Event` 物件以 **替換** 原始事件。

下列程式碼範例顯示此回呼的基本語法：

<details>
<summary>範例說明</summary>

> Python

```py
async def on_event_callback(
    self, *, invocation_context: InvocationContext, event: Event
) -> Optional[Event]:
    """在事件發送給使用者前處理事件。"""
    # 修改或檢查事件
    return None
```

> typescript

```typescript
async onEventCallback(
    invocationContext: InvocationContext,
    event: Event
): Promise<Event | undefined> {
    // 在此處實作您的邏輯
    return undefined;
}
```

</details>

### 執行器結束回呼

*執行器結束 (Runner end)* 回呼 **(`after_run_callback`)** 在代理已完成其整個過程且所有事件都已處理完畢時發生，`Runner` 完成其執行。`after_run_callback` 是最後一個掛鉤，非常適合進行清理和最終報告。

-   **執行時機**：在 `Runner` 完全完成請求執行後。
-   **目的**：適用於全域清理任務，例如關閉連線或完成日誌與指標資料。
-   **流程控制**：此回呼僅用於拆卸 (teardown)，無法更改最終結果。

下列程式碼範例顯示此回呼的基本語法：

<details>
<summary>範例說明</summary>

> Python

```py
async def after_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[None]:
    """在 Runner 完全結束後執行的清理回呼。"""
    # 執行清理工作
    return None
```

> typescript

```typescript
async afterRunCallback(invocationContext: InvocationContext): Promise<void> {
    // 在此處執行清理工作
}
```

</details>

## 後續步驟

查看這些資源以開發外掛程式並將其應用於您的 ADK 專案：

-   如需更多 ADK 外掛程式程式碼範例，請參閱 [ADK Python 儲存庫](https://github.com/google/adk-python/tree/main/src/google/adk/plugins)。
-   有關為安全目的應用外掛程式的資訊，請參閱 [安全防護欄的回呼與外掛程式](https://google.github.io/adk-docs/safety/#callbacks-and-plugins-for-security-guardrails)。

## 更多說明

### 已實現的外掛程式回呼掛鉤清單：

下表列出了目前在 ADK 中實作的外掛程式回呼掛鉤：
| 文件                                                                                                                                           | 目的／職責                             | 主要風險／關注點                                  | 建議的改進／檢查點                                                                       | 優先級 |
| :--------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------- | :------------------------------------------------ | :--------------------------------------------------------------------------------------- | :----- |
| [base_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/base_plugin.py)                                         | 外掛基類，定義生命週期／介面           | 缺乏型別／文件、全域狀態依賴、錯誤處理不一致      | 使用 ABC／Protocol，補充型別註解與 docstring，定義錯誤契約                               | 中     |
| [bigquery_agent_analytics_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/bigquery_agent_analytics_plugin.py) | 與 BigQuery 互動，上報／寫入分析資料   | 憑證洩漏、SQL／查詢注入、效能／批次處理、缺乏測試 | 用環境憑證／最小權限、參數化查詢、模組拆分（連線／批次處理／序列化）、增加單元與整合測試 | 高     |
| [context_filter_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/context_filter_plugin.py)                     | 過濾或裁剪上下文（去識別化／長度限制） | 隱私／去識別化不完全、大輸入／編碼邊界            | 可配置白名單／黑名單、邊界測試、明確去識別化策略與範例                                   | 中     |
| [debug_logging_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/debug_logging_plugin.py)                       | 增強除錯日誌和上下文追蹤               | 生產環境洩漏敏感資料、效能與日誌量                | 提供開關關閉詳細日誌、敏感欄位遮蔽、速率限制與結構化日誌                                 | 高     |
| [global_instruction_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/global_instruction_plugin.py)             | 注入／管理全域指令（模型提示等）       | 指令可信度、衝突或無限注入                        | 明確優先順序／覆蓋策略，驗證指令來源並記錄變更                                           | 中     |
| [logging_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/logging_plugin.py)                                   | 常規日誌路由／格式化／上報             | 與 debug 外掛重疊、敏感資訊輸出                   | 明確分工，支援外部後端配置，統一去識別化策略                                             | 中     |
| [multimodal_tool_results_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/multimodal_tool_results_plugin.py)   | 處理多模態工具（影像／音訊）結果       | 二進位序列化、檔案大小、暫存檔未清理              | 限制大小與型別、清理流程、對上傳內容做掃描                                               | 中     |
| [plugin_manager.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/plugin_manager.py)                                   | 外掛發現／註冊／生命週期／調度         | 並發安全、錯誤隔離、外掛依賴／順序                | 保證執行緒／async 安全、外掛異常隔離策略、測試並發註冊／卸載                             | 高     |
| [reflect_retry_tool_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/reflect_retry_tool_plugin.py)             | 反思後重試機制（失敗後修改並重試）     | 重試策略不當導致循環或資源浪費                    | 明確重試分類、指數退避、最大次數、記錄每次重試與原因                                     | 高     |
| [save_files_as_artifacts_plugin.py](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/save_files_as_artifacts_plugin.py)   | 將檔案儲存為 artifact（上傳／持久化）  | 路徑遍歷、不受控大檔案、權限／配額問題            | 標準化檔名、大小／型別檢查、清理策略、最小權限上傳                                       | 高     |
