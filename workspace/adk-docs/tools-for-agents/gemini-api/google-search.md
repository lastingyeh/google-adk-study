# Google Search tool for ADK

> 🔔 "更新日期：2026-01-23"
>
> 🔗 "資料來源：https://google.github.io/adk-docs/tools/gemini-api/google-search/"

[`ADK 支援`: `Python v0.1.0` | `TypeScript v0.2.0` | `Go v0.1.0` | `Java v0.2.0`]

`google_search` 工具允許代理使用 Google 搜尋進行網頁搜尋。`google_search` 工具僅與 Gemini 2 模型相容。有關該工具的進一步詳細資訊，請參閱 [瞭解 Google 搜尋接地 (grounding)](https://google.github.io/adk-docs/grounding/google_search_grounding/)。

> [!WARNING] 使用 `google_search` 工具時的額外要求
當您使用 Google 搜尋接地 (grouding)，並在回應中收到搜尋建議時，您必須在實際產品和應用程式中顯示搜尋建議。
有關 Google 搜尋接地的更多資訊，請參閱 [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) 或 [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions) 的 Google 搜尋接地 (grouding)文件。使用者介面代碼 (HTML) 會在 Gemini 回應中以 `renderedContent` 的形式傳回，您需要根據政策在應用程式中顯示該 HTML。

> [!WARNING] 警告：每個代理限制使用單一工具
此工具在代理實例中只能***單獨***使用。
有關此限制和解決方法的更多資訊，請參閱 [ADK 工具的限制](../limitations.md#每個代理程式僅限一個工具限制)。

<details>
<summary>範例說明</summary>

> Python 範例

```py
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

APP_NAME="google_search_agent"
USER_ID="user1234"
SESSION_ID="1234"

root_agent = Agent(
    name="basic_search_agent",
    model="gemini-2.0-flash",
    description="使用 Google 搜尋回答問題的代理。",
    instruction="我可以透過網路搜尋來回答您的問題，請隨時提問！",
    # google_search 是一個內建工具，允許代理執行 Google 搜尋。
    tools=[google_search]
)

# 會話與 Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
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

# 注意：在 Colab 中可於頂層直接使用 'await'。
# 若以獨立 Python 腳本執行，請使用 asyncio.run() 或管理事件迴圈。
await call_agent_async("AI 最新的新聞?")
```

> TypeScript 範例

```typescript
// 匯入必要的 ADK 組件
import {GOOGLE_SEARCH, LlmAgent} from '@google/adk';

// 定義根代理，配置使用 Google 搜尋工具
export const rootAgent = new LlmAgent({
  model: 'gemini-2.5-flash', // 使用 Gemini 2.5 Flash 模型
  name: 'root_agent',
  description:
      '一個負責執行 Google 搜尋查詢並回答有關結果問題的代理。',
  instruction:
      '你是一個負責執行 Google 搜尋查詢並回答有關結果問題的代理。',
  tools: [GOOGLE_SEARCH], // 載入 Google 搜尋工具
});
```

> Go 範例

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
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/geminitool"
    "google.golang.org/genai"
)

func createSearchAgent(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, "gemini-2.5-flash", &genai.ClientConfig{})
    if err != nil {
        return nil, fmt.Errorf("建立模型失敗: %v", err)
    }

    return llmagent.New(llmagent.Config{
        Name:        "basic_search_agent",
        Model:       model,
        Description: "使用 Google 搜尋回答問題的代理。",
        Instruction: "我可以透過網路搜尋來回答您的問題，請隨時提問！",
        Tools:       []tool.Tool{geminitool.GoogleSearch{}},
    })
}

const (
    userID  = "user1234"
    appName = "Google Search_agent"
)

func callAgent(ctx context.Context, a agent.Agent, prompt string) error {
    sessionService := session.InMemoryService()
    session, err := sessionService.Create(ctx, &session.CreateRequest{
        AppName: appName,
        UserID:  userID,
    })
    if err != nil {
        return fmt.Errorf("建立會話服務失敗: %v", err)
    }

    config := runner.Config{
        AppName:        appName,
        Agent:          a,
        SessionService: sessionService,
    }
    r, err := runner.New(config)
    if err != nil {
        return fmt.Errorf("建立 runner 失敗: %v", err)
    }

    sessionID := session.Session.ID()
    userMsg := &genai.Content{
        Parts: []*genai.Part{{Text: prompt}},
        Role:  string(genai.RoleUser),
    }

    // r.Run 會串流事件與錯誤。
    // 迴圈會即時處理到達的結果。
    for event, err := range r.Run(ctx, userID, sessionID, userMsg, agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }) {
        if err != nil {
            fmt.Printf("\n代理錯誤: %v\n", err)
        } else if event.Partial {
            for _, p := range event.LLMResponse.Content.Parts {
                fmt.Print(p.Text)
            }
        }
    }
    return nil
}

func main() {
    agent, err := createSearchAgent(context.Background())
    if err != nil {
        log.Fatalf("建立代理失敗: %v", err)
    }
    fmt.Println("代理已建立:", agent.Name())
    prompt := "what's the latest ai news?"
    fmt.Printf("\n提示: %s\n回應: ", prompt)
    if err := callAgent(context.Background(), agent, prompt); err != nil {
        log.Fatalf("呼叫代理錯誤: %v", err)
    }
    fmt.Println("\n---")
}
```

> Java 範例

```java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.GoogleSearchTool;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;

public class GoogleSearchAgentApp {

  private static final String APP_NAME = "Google Search_agent";
  private static final String USER_ID = "user1234";
  private static final String SESSION_ID = "1234";

  /**
   * 呼叫代理並列印最終回應。
   *
   * @param runner 使用的 runner。
   * @param query 要傳送給代理的查詢。
   */
  public static void callAgent(Runner runner, String query) {
    Content content =
        Content.fromParts(Part.fromText(query));

    InMemorySessionService sessionService = (InMemorySessionService) runner.sessionService();
    Session session =
        sessionService
            .createSession(APP_NAME, USER_ID, /* state= */ null, SESSION_ID)
            .blockingGet();

    runner
        .runAsync(session.userId(), session.id(), content)
        .forEach(
            event -> {
              if (event.finalResponse()
                  && event.content().isPresent()
                  && event.content().get().parts().isPresent()
                  && !event.content().get().parts().get().isEmpty()
                  && event.content().get().parts().get().get(0).text().isPresent()) {
                String finalResponse = event.content().get().parts().get().get(0).text().get();
                System.out.println("代理回應: " + finalResponse);
              }
            });
  }

  public static void main(String[] args) {
    // Google Search 是一個內建工具，允許代理執行 Google 搜尋。
    GoogleSearchTool googleSearchTool = new GoogleSearchTool();

    BaseAgent rootAgent =
        LlmAgent.builder()
            .name("basic_search_agent")
            .model("gemini-2.0-flash") // 使用 Gemini 2.0 系列模型以相容 Google Search 工具
            .description("使用 Google 搜尋回答問題的代理。")
            .instruction(
                "我可以透過網路搜尋來回答您的問題，請隨時提問！")
            .tools(ImmutableList.of(googleSearchTool))
            .build();

    // 會話與 Runner
    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(rootAgent, APP_NAME, null, sessionService);

    // 代理互動
    callAgent(runner, "what's the latest ai news?");
  }
}
```

</details>