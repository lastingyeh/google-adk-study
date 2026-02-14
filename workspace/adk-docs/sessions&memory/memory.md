# 記憶 (Memory)：使用 `MemoryService` 獲得長期知識

> 🔔 `更新日期：2026-01-26`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/sessions/memory/

[`ADK 支援`: `Python v0.1.0` | `Typescript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

我們已經看到 `Session` 如何追蹤單一、持續進行對話的歷史記錄 (`events`) 和臨時數據 (`state`)。但是，如果代理 (agent) 需要回想起過去對話中的資訊該怎麼辦？這就是 **長期知識 (Long-Term Knowledge)** 和 **`MemoryService`** 概念發揮作用的地方。

可以這樣想：

* **`Session` / `State`**：就像你在一次特定聊天中的短期記憶。
* **長期知識 (`MemoryService`)**：就像一個可搜尋的檔案館或知識庫，代理可以諮詢它，其中可能包含來自許多過去聊天或其他來源的資訊。

## `MemoryService` 的角色

`BaseMemoryService` 定義了管理這個可搜尋的、長期知識庫的介面。其主要職責是：

1. **攝取資訊 (`add_session_to_memory`)**：獲取（通常已完成的）`Session` 的內容，並將相關資訊添加到長期知識庫中。
2. **搜尋資訊 (`search_memory`)**：允許代理（通常透過 `Tool`）查詢知識庫，並根據搜尋查詢檢索相關片段或上下文。

## 選擇正確的記憶服務 (Memory Service)

ADK 提供兩種不同的 `MemoryService` 實現，每種都針對不同的使用場景量身定制。使用下表來決定哪一種最適合您的代理。

| **功能** | **InMemoryMemoryService** | **VertexAiMemoryBankService** |
| :--- | :--- | :--- |
| **持久性** | 無（數據在重啟時丟失） | 有（由 Vertex AI 管理） |
| **主要使用案例** | 原型設計、本地開發和簡單測試。 | 從使用者對話中建立有意義的、不斷演進的記憶。 |
| **記憶提取** | 儲存完整對話內容 | 從對話中提取 [有意義的資訊](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories) 並將其與現有記憶整合（由 LLM 驅動） |
| **搜尋能力** | 基本關鍵字比對。 | 進階語義搜尋。 |
| **設定複雜度** | 無。這是預設設定。 | 低。需要在 Vertex AI 中建立 [Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) 實例。 |
| **依賴項** | 無。 | Google Cloud 專案、Vertex AI API |
| **何時使用** | 當您想跨多個會話的對話歷史進行搜尋以進行原型設計時。 | 當您希望代理能夠從過去的互動中學習並記住時。 |

## 記憶體內記憶 (In-Memory Memory)

`InMemoryMemoryService` 將會話資訊儲存在應用程式的記憶體中，並對搜尋執行基本關鍵字比對。它不需要任何設定，最適合不需要持久性的原型設計和簡單測試場景。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.memory import InMemoryMemoryService
# 初始化記憶體內記憶服務
memory_service = InMemoryMemoryService()
```

> go

```go
import (
  "google.golang.org/adk/memory"
  "google.golang.org/adk/session"
)

// 服務必須在運行器 (runners) 之間共享，才能共享狀態和記憶。
sessionService := session.InMemoryService()
memoryService := memory.InMemoryService()
```

</details>

**範例：添加和搜尋記憶**

此範例為了簡單起見，演示了使用 `InMemoryMemoryService` 的基本流程。

<details>
<summary>範例說明</summary>

> Python

```python
import asyncio
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.memory import InMemoryMemoryService # 匯入 MemoryService
from google.adk.runners import Runner
from google.adk.tools import load_memory # 用於查詢記憶的工具
from google.genai.types import Content, Part

# --- 常數 ---
APP_NAME = "memory_example_app"
USER_ID = "mem_user"
MODEL = "gemini-2.0-flash" # 使用有效的模型

# --- 代理定義 ---
# 代理 1：擷取資訊的簡單代理
info_capture_agent = LlmAgent(
    model=MODEL,
    name="InfoCaptureAgent",
    instruction="確認使用者的陳述。",
)

# 代理 2：可以使用記憶的代理
memory_recall_agent = LlmAgent(
    model=MODEL,
    name="MemoryRecallAgent",
    instruction="回答使用者的問題。如果答案可能在過去的對話中，請使用 'load_memory' 工具。",
    tools=[load_memory] # 提供工具給代理
)

# --- 服務 ---
# 服務必須在運行器之間共享，以共享狀態和記憶
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService() # 示範使用記憶體內儲存

async def run_scenario():
    # --- 場景 ---

    # 第 1 輪：在會話中擷取一些資訊
    print("--- 第 1 輪：擷取資訊 ---")
    runner1 = Runner(
        # 從資訊擷取代理開始
        agent=info_capture_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service # 提供記憶服務給 Runner
    )
    session1_id = "session_info"
    await runner1.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
    user_input1 = Content(parts=[Part(text="我最喜歡的專案是 Project Alpha。")], role="user")

    # 執行代理
    final_response_text = "(無最終回應)"
    async for event in runner1.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text = event.content.parts[0].text
    print(f"代理 1 回應: {final_response_text}")

    # 取得已完成的會話
    completed_session1 = await runner1.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

    # 將此會話的內容添加到記憶服務中
    print("\n--- 正在將會話 1 添加到記憶中 ---")
    await memory_service.add_session_to_memory(completed_session1)
    print("會話已添加到記憶中。")

    # 第 2 輪：在新的會話中回想資訊
    print("\n--- 第 2 輪：回想資訊 ---")
    runner2 = Runner(
        # 使用第二個代理，它擁有記憶工具
        agent=memory_recall_agent,
        app_name=APP_NAME,
        session_service=session_service, # 重複使用相同的服務
        memory_service=memory_service   # 重複使用相同的服務
    )
    session2_id = "session_recall"
    await runner2.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)
    user_input2 = Content(parts=[Part(text="我最喜歡的專案是什麼？")], role="user")

    # 執行第二個代理
    final_response_text_2 = "(無最終回應)"
    async for event in runner2.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text_2 = event.content.parts[0].text
    print(f"代理 2 回應: {final_response_text_2}")

# 要執行此範例，您可以使用以下程式碼片段：
# asyncio.run(run_scenario())

# await run_scenario()
```

> go

```go
import (
    "context"
    "fmt"
    "log"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/memory"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

const (
    appName = "go_memory_example_app"
    userID  = "go_mem_user"
    modelID = "gemini-2.5-pro"
)

// Args 定義記憶搜尋工具的輸入結構。
type Args struct {
    Query string `json:"query" jsonschema:"要在記憶中搜尋的查詢內容。"`
}

// Result 定義記憶搜尋工具的輸出結構。
type Result struct {
    Results []string `json:"results"`
}


// memorySearchToolFunc 是記憶搜尋工具的實現。
// 此函數展示了如何透過 tool.Context 存取記憶。
func memorySearchToolFunc(ctx tool.Context, args Args) (Result, error) {
    fmt.Printf("工具：正在搜尋記憶中的查詢：'%s'\n", args.Query)
    // SearchMemory 函數可在 context 中使用。
    searchResults, err := ctx.SearchMemory(context.Background(), args.Query)
    if err != nil {
        log.Printf("搜尋記憶時發生錯誤：%v", err)
        return Result{}, fmt.Errorf("記憶搜尋失敗")
    }

    var results []string
    for _, res := range searchResults.Memories {
        if res.Content != nil {
            results = append(results, textParts(res.Content)...)
        }
    }
    return Result{Results: results}, nil
}

// 定義一個可以搜尋記憶的工具。
var memorySearchTool = must(functiontool.New(
    functiontool.Config{
        Name:        "search_past_conversations",
        Description: "搜尋過去對話中的相關資訊。",
    },
    memorySearchToolFunc,
))


// 此範例演示了如何在 Go ADK 中使用 MemoryService。
// 它涵蓋了兩個主要場景：
// 1. 將已完成的會話添加到記憶中，並在新的會話中回想它。
// 2. 使用 tool.Context 從自定義工具內搜尋記憶。
func main() {
    ctx := context.Background()

    // --- 服務 ---
    // 服務必須在運行器之間共享，以共享狀態和記憶。
    sessionService := session.InMemoryService()
    memoryService := memory.InMemoryService() // 此範例使用記憶體內儲存。

    // --- 場景 1：在一個會話中擷取資訊 ---
    fmt.Println("--- 第 1 輪：擷取資訊 ---")
    infoCaptureAgent := must(llmagent.New(llmagent.Config{
        Name:        "InfoCaptureAgent",
        Model:       must(gemini.NewModel(ctx, modelID, nil)),
        Instruction: "確認使用者的陳述。",
    }))

    runner1 := must(runner.New(runner.Config{
        AppName:        appName,
        Agent:          infoCaptureAgent,
        SessionService: sessionService,
        MemoryService:  memoryService, // 提供記憶服務給 Runner
    }))

    session1ID := "session_info"
    must(sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID, SessionID: session1ID}))

    userInput1 := genai.NewContentFromText("我最喜歡的專案是 Project Alpha。", "user")
    var finalResponseText string
    for event, err := range runner1.Run(ctx, userID, session1ID, userInput1, agent.RunConfig{}) {
        if err != nil {
            log.Printf("代理 1 錯誤：%v", err)
            continue
        }
        if event.Content != nil && !event.LLMResponse.Partial {
            finalResponseText = strings.Join(textParts(event.LLMResponse.Content), "")
        }
    }
    fmt.Printf("代理 1 回應：%s\n", finalResponseText)

    // 將已完成的會話添加到記憶服務中
    fmt.Println("\n--- 正在將會話 1 添加到記憶中 ---")
    resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: session1ID})
    if err != nil {
        log.Fatalf("無法取得已完成的會話：%v", err)
    }
    if err := memoryService.AddSession(ctx, resp.Session); err != nil {
        log.Fatalf("無法將會話添加到記憶中：%v", err)
    }
    fmt.Println("會話已添加到記憶中。")

    // --- 場景 2：使用工具在新的會話中回想資訊 ---
    fmt.Println("\n--- 第 2 輪：回想資訊 ---")

    memoryRecallAgent := must(llmagent.New(llmagent.Config{
        Name:        "MemoryRecallAgent",
        Model:       must(gemini.NewModel(ctx, modelID, nil)),
        Instruction: "回答使用者的問題。如果答案可能在過去的對話中，請使用 'search_past_conversations' 工具。",
        Tools:       []tool.Tool{memorySearchTool}, // 提供工具給代理
    }))

    runner2 := must(runner.New(runner.Config{
        Agent:          memoryRecallAgent,
        AppName:        appName,
        SessionService: sessionService,
        MemoryService:  memoryService,
    }))

    session2ID := "session_recall"
    must(sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID, SessionID: session2ID}))
    userInput2 := genai.NewContentFromText("我最喜歡的專案是什麼？", "user")

    var finalResponseText2 string
    for event, err := range runner2.Run(ctx, userID, session2ID, userInput2, agent.RunConfig{}) {
        if err != nil {
            log.Printf("代理 2 錯誤：%v", err)
            continue
        }
        if event.Content != nil && !event.LLMResponse.Partial {
            finalResponseText2 = strings.Join(textParts(event.LLMResponse.Content), "")
        }
    }
    fmt.Printf("代理 2 回應：%s\n", finalResponseText2)
}
```

</details>

### 在工具內搜尋記憶

您也可以使用 `tool.Context` 從自定義工具內搜尋記憶。

<details>
<summary>範例說明</summary>

> go

```go
// memorySearchToolFunc 是記憶搜尋工具的實現。
// 此函數展示了如何透過 tool.Context 存取記憶。
func memorySearchToolFunc(ctx tool.Context, args Args) (Result, error) {
    fmt.Printf("工具：正在搜尋記憶中的查詢：'%s'\n", args.Query)
    // SearchMemory 函數可在 context 中使用。
    searchResults, err := ctx.SearchMemory(context.Background(), args.Query)
    if err != nil {
        log.Printf("搜尋記憶時發生錯誤：%v", err)
        return Result{}, fmt.Errorf("記憶搜尋失敗")
    }

    var results []string
    for _, res := range searchResults.Memories {
        if res.Content != nil {
            results = append(results, textParts(res.Content)...)
        }
    }
    return Result{Results: results}, nil
}

// 定義一個可以搜尋記憶的工具。
var memorySearchTool = must(functiontool.New(
    functiontool.Config{
        Name:        "search_past_conversations",
        Description: "搜尋過去對話中的相關資訊。",
    },
    memorySearchToolFunc,
))
```

</details>

## Vertex AI 記憶銀行 (Memory Bank)

`VertexAiMemoryBankService` 將您的代理連接到 [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)，這是一個完全託管的 Google Cloud 服務，為對話式代理提供複雜且持久的記憶功能。

### 運作原理

該服務處理兩個關鍵操作：

*   **生成記憶 (Generating Memories)**：在對話結束時，您可以將會話的事件發送到記憶銀行，它會智慧地處理並將資訊儲存為「記憶」。
*   **檢索記憶 (Retrieving Memories)**：您的代理程式碼可以針對記憶銀行發出搜尋查詢，以檢索過去對話中的相關記憶。

### 先決條件

在使用此功能之前，您必須具備：

1.  **Google Cloud 專案**：已啟用 Vertex AI API。
2.  **Agent Engine**：您需要在 Vertex AI 中建立一個 Agent Engine。您不需要將代理部署到 Agent Engine Runtime 即可使用記憶銀行。這將為您提供配置所需的 **Agent Engine ID**。
3.  **身份驗證**：確保您的本地環境已通過身份驗證以存取 Google Cloud 服務。最簡單的方法是執行：
    ```bash
    gcloud auth application-default login
    ```
4.  **環境變數**：服務需要您的 Google Cloud 專案 ID 和地點。將其設置為環境變數：
    ```bash
    export GOOGLE_CLOUD_PROJECT="您的專案-ID"
    export GOOGLE_CLOUD_LOCATION="您的地點"
    ```

### 配置

要將代理連接到記憶銀行，在啟動 ADK 伺服器（`adk web` 或 `adk api_server`）時使用 `--memory_service_uri` 旗標。URI 格式必須為 `agentengine://<agent_engine_id>`。

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

或者，您可以透過手動實例化 `VertexAiMemoryBankService` 並將其傳遞給 `Runner` 來配置您的代理以使用記憶銀行。

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.memory import VertexAiMemoryBankService

# 取得 Agent Engine ID
agent_engine_id = agent_engine.api_resource.name.split("/")[-1]

# 實例化 Vertex AI 記憶銀行服務
memory_service = VertexAiMemoryBankService(
    project="PROJECT_ID",
    location="LOCATION",
    agent_engine_id=agent_engine_id
)

runner = adk.Runner(
    ...
    memory_service=memory_service
)
```

</details>

## 在代理中使用記憶

配置記憶服務後，代理可以使用工具或回呼 (callback) 來檢索記憶。ADK 包含兩個預建的檢索記憶工具：

* `PreloadMemory`：在每輪對話開始時始終檢索記憶（類似於回呼）。
* `LoadMemory`：當您的代理認為有幫助時檢索記憶。

**範例：**

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

# 建立具有預先載入記憶工具的代理
agent = Agent(
    model=MODEL_ID,
    name='weather_sentiment_agent',
    instruction="...",
    tools=[PreloadMemoryTool()]
)
```

</details>

要從會話中提取記憶，您需要呼叫 `add_session_to_memory`。例如，您可以透過回呼來自動執行此操作：

<details>
<summary>範例說明</summary>

> Python

```python
from google import adk

# 自動將會話儲存到記憶的回呼函數
async def auto_save_session_to_memory_callback(callback_context):
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session)

agent = Agent(
    model=MODEL,
    name="Generic_QA_Agent",
    instruction="回答使用者的問題",
    tools=[adk.tools.preload_memory_tool.PreloadMemoryTool()],
    after_agent_callback=auto_save_session_to_memory_callback,
)
```

</details>

## 進階概念

### 記憶在實踐中如何運作

記憶工作流程內部涉及以下步驟：

1. **會話互動**：使用者透過 `Session` 與代理進行互動，該會話由 `SessionService` 管理。事件會被添加，狀態可能會更新。
2. **攝取到記憶中**：在某個時間點（通常是會話被認為已完成或產生了重要資訊時），您的應用程式會呼叫 `memory_service.add_session_to_memory(session)`。這會從會話事件中提取相關資訊並將其添加到長期知識庫中（記憶體內字典或 Agent Engine 記憶銀行）。
3. **稍後查詢**：在 *另一個*（或同一個）會話中，使用者可能會問一個需要過去上下文的問題（例如，「我們上週討論了關於專案 X 的什麼內容？」）。
4. **代理使用記憶工具**：配備有記憶檢索工具（如內建的 `load_memory` 工具）的代理會識別出對過去上下文的需求。它呼叫該工具，提供搜尋查詢（例如，「上週專案 X 的討論」）。
5. **執行搜尋**：該工具內部呼叫 `memory_service.search_memory(app_name, user_id, query)`。
6. **返回結果**：`MemoryService` 搜尋其儲存空間（使用關鍵字比對或語義搜尋）並將相關片段作為 `SearchMemoryResponse` 返回，其中包含 `MemoryResult` 物件清單（每個物件都可能持有來自相關過去會話的事件）。
7. **代理使用結果**：工具將這些結果返回給代理，通常作為上下文或函數回應的一部分。代理隨後可以使用這些檢索到的資訊來制定其對使用者的最終答案。

### 代理是否可以存取多個記憶服務？

*   **透過標準配置：不可以。** 框架（`adk web`, `adk api_server`）設計為每次透過 `--memory_service_uri` 旗標配置一個單一的記憶服務。然後將此單一服務提供給代理，並透過內建的 `self.search_memory()` 方法進行存取。從配置的角度來看，您只能為該進程服務的所有代理選擇一個後端（`InMemory`, `VertexAiMemoryBankService`）。

*   **在您的代理代碼中：可以，絕對沒問題。** 沒有任何因素阻止您直接在代理代碼中手動匯入並實例化另一個記憶服務。這允許您在單個代理輪次中存取多個記憶來源。

例如，您的代理可以使用框架配置的 `InMemoryMemoryService` 來回想對話歷史，同時也可以手動實例化 `VertexAiMemoryBankService` 以在技術手冊中查找資訊。

#### 範例：使用兩個記憶服務

以下是如何在代理代碼中實現這一點：

<details>
<summary>範例說明</summary>

> Python

```python
from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
from google.genai import types

class MultiMemoryAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 初始化預設的記憶體內記憶服務
        self.memory_service = InMemoryMemoryService()
        # 手動實例化第二個記憶服務用於文件查找
        self.vertexai_memorybank_service = VertexAiMemoryBankService(
            project="PROJECT_ID",
            location="LOCATION",
            agent_engine_id="AGENT_ENGINE_ID"
        )

    async def run(self, request: types.Content, **kwargs) -> types.Content:
        user_query = request.parts[0].text

        # 1. 使用框架提供的記憶搜尋對話歷史
        #    （如果已配置，這將是 InMemoryMemoryService）
        conversation_context = await self.memory_service.search_memory(query=user_query)

        # 2. 使用手動建立的服務搜尋文件知識庫
        document_context = await self.vertexai_memorybank_service.search_memory(query=user_query)

        # 結合來自兩個來源的上下文以產生更好的回應
        prompt = "從我們過去的對話中，我記得：\n"
        prompt += f"{conversation_context.memories}\n\n"
        prompt += "從技術手冊中，我找到了：\n"
        prompt += f"{document_context.memories}\n\n"
        prompt += f"基於這一切，以下是我對 '{user_query}' 的回答："

        # 使用 LLM 生成最終內容
        return await self.llm.generate_content_async(prompt)
```

</details>
