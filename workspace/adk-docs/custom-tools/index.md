# ADK 自定義工具 (Custom Tools)

🔔 `更新日期：2026-01-12`

[`ADK 支援`: `Python v0.1.0` | `Typescript v0.2.0` | `Go v0.1.0` | `Java v0.1.0`]

在 ADK 代理程式工作流中，「工具 (Tools)」是具有結構化輸入與輸出的程式化函數，可由 ADK 代理程式呼叫以執行操作。ADK 工具的功能類似於您在 Gemini 或其他生成式 AI 模型中使用 [函數呼叫 (Function Call)](https://ai.google.dev/gemini-api/docs/function-calling) 的方式。您可以使用 ADK 工具執行各種操作和程式化功能，例如：

*   查詢資料庫
*   發送 API 請求：獲取天氣資料、預約系統
*   搜尋網頁
*   執行程式碼片段
*   從文件中檢索資訊 (RAG)
*   與其他軟體或服務互動

> [!TIP] ADK 工具列表 (ADK Tools list)
    在為 ADK 構建您自己的工具之前，請查看 **[ADK 工具列表](https://google.github.io/adk-docs/tools/)**，瞭解可用於 ADK 代理程式的預建工具。

## 什麼是工具 (Tool)？

在 ADK 的語境下，工具代表提供給 AI 代理程式的特定能力，使其能夠在核心文本生成和推理能力之外執行操作並與世界互動。區分功能強大的代理程式與基礎語言模型的關鍵通常在於它們對工具的有效利用。

從技術上講，工具通常是一個模組化程式碼組件——**如 Python、Java 或 TypeScript 函數**、類別方法，甚至是另一個專門的代理程式——旨在執行特定的、預定義的任務。這些任務通常涉及與外部系統或數據的互動。

<img src="https://google.github.io/adk-docs/assets/agent-tool-call.png" alt="代理程式工具呼叫">

### 核心特性

**行動導向 (Action-Oriented)：** 工具為代理程式執行特定操作，例如搜尋資訊、呼叫 API 或執行計算。

**擴展代理程式能力 (Extends Agent capabilities)：** 它們使代理程式能夠訪問即時資訊、影響外部系統，並克服其訓練數據中固有的知識限制。

**執行預定義邏輯 (Execute predefined logic)：** 至關重要地，工具執行特定的、由開發者定義的邏輯。它們不具備像代理程式核心大型語言模型 (LLM) 那樣的獨立推理能力。LLM 推理要使用哪個工具、何時使用以及使用什麼輸入，但工具本身僅執行其指定的函數。

## 代理程式如何使用工具

代理程式通過通常涉及函數呼叫的機制動態地利用工具。該過程通常遵循以下步驟：

1. **推理 (Reasoning)：** 代理程式的 LLM 分析其系統指令、對話歷史和用戶請求。
2. **選擇 (Selection)：** 基於分析，LLM 根據代理程式可用的工具以及描述每個工具的 docstring 來決定執行哪個工具（如果有）。
3. **調用 (Invocation)：** LLM 生成所選工具所需的參數（輸入）並觸發其執行。
4. **觀察 (Observation)：** 代理程式接收工具返回的輸出（結果）。
5. **最終化 (Finalization)：** 代理程式將工具的輸出整合到其持續的推理過程中，以制定下一個回應、決定後續步驟，或判斷目標是否已達成。

將工具視為代理程式智慧核心 (LLM) 在需要時可以訪問和利用的專門工具包，以完成複雜任務。

## ADK 中的工具類型

ADK 通過支援多種類型的工具提供靈活性：

1. **[自定義函數工具](./function-tools/overview.md)：** 由您創建，根據您的特定應用需求量身定制。
    * **[函數/方法](./function-tools/overview.md#1-function-tool)：** 在您的程式碼中定義標準同步函數或方法（例如 Python `def`）。
    * **[代理程式即工具](./function-tools/overview.md#3-agent-as-a-tool)：** 將另一個（可能是專門的）代理程式用作父代理程式的工具。
    * **[長時間運行函數工具](./function-tools/overview.md#2-long-running-function-tool)：** 支援執行非同步操作或需要大量時間完成的工具。
2. **[內建工具](https://google.github.io/adk-docs/tools/)：** 由框架提供的、可用於常見任務的現成工具。
        範例：Google 搜尋、程式碼執行、檢索增強生成 (RAG)。
3. **第三方工具：** 從流行的外部庫無縫整合工具。

瀏覽上方連結的各個文件頁面，獲取每種工具類型的詳細資訊和範例。

## 在代理程式指令中引用工具

在代理程式的指令中，您可以通過使用工具的 **函數名稱** 直接引用它。如果工具的 **函數名稱** 和 **docstring** 具有足夠的描述性，您的指令可以主要集中在 **大型語言模型 (LLM) 應何時利用該工具**。這能提高清晰度並幫助模型理解每個工具的預期用途。

**清楚地指示代理程式如何處理工具可能產生的不同返回值** 至關重要。例如，如果工具返回錯誤訊息，您的指令應指定代理程式是應重試操作、放棄任務還是向用戶請求更多資訊。

此外，ADK 支援工具的順序使用，其中一個工具的輸出可以作為另一個工具的輸入。在實現此類工作流時，重要的是在代理程式的指令中 **描述預期的工具使用順序**，以引導模型完成必要的步驟。

### 範例

以下範例展示了代理程式如何通過 **在其指令中引用函數名稱** 來使用工具。它還演示了如何引導代理程式 **處理工具的不同返回值**（如成功或錯誤訊息），以及如何編排 **多個工具的順序使用** 以完成任務。

<details>
<summary>範例說明</summary>

> Python

```py
# 引入 Python 範例：展示如何在指令中引用工具並處理返回值

import asyncio
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME="weather_sentiment_agent"  # 應用程式名稱
USER_ID="user1234"                  # 用戶 ID
SESSION_ID="1234"                   # 會話 ID
MODEL_ID="gemini-2.0-flash"         # 使用的模型 ID

# 工具 1：取得天氣報告
# Tool 1: Get weather report
def get_weather_report(city: str) -> dict:
    """取得指定城市的當前天氣報告。

    Returns:
        dict: 包含天氣資訊的字典，'status' 鍵為 'success' 或 'error'，'report' 鍵為天氣細節（成功時），或 'error_message'（錯誤時）。
    """
    if city.lower() == "london":
        return {"status": "success", "report": "倫敦當前的天氣是多雲，氣溫為攝氏 18 度，有降雨機率。"}
    elif city.lower() == "paris":
        return {"status": "success", "report": "巴黎的天氣晴朗，氣溫為攝氏 25 度。"}
    else:
        return {"status": "error", "error_message": f"無法獲取 '{city}' 的天氣資訊。"}

weather_tool = FunctionTool(func=get_weather_report)  # 將函數包裝為工具


# 工具 2：分析文字情感
# Tool 2: Analyze sentiment
def analyze_sentiment(text: str) -> dict:
    """分析給定文字的情感。

    Returns:
        dict: 包含 'sentiment'（'positive'、'negative' 或 'neutral'）和 'confidence' 分數的字典。
        dict: A dictionary with 'sentiment' ('positive', 'negative', or 'neutral') and a 'confidence' score.
    """
    if "good" in text.lower() or "sunny" in text.lower():
        return {"sentiment": "positive", "confidence": 0.8}
    elif "rain" in text.lower() or "bad" in text.lower():
        return {"sentiment": "negative", "confidence": 0.7}
    else:
        return {"sentiment": "neutral", "confidence": 0.6}

sentiment_tool = FunctionTool(func=analyze_sentiment)  # 將函數包裝為工具


# 代理程式設定
weather_sentiment_agent = Agent(
    model=MODEL_ID,
    name='weather_sentiment_agent',
    instruction="""你是一個提供天氣資訊並分析用戶回饋情感的助手。
    **當用戶詢問特定城市的天氣時，使用 'get_weather_report' 工具取得天氣細節。**

    **若 'get_weather_report' 工具回傳 'success'，則將天氣報告提供給用戶。**
    **若 'get_weather_report' 工具回傳 'error'，則告知用戶該城市無法取得天氣資訊，並詢問是否有其他城市。**

    **在提供天氣報告後，若用戶對天氣有回饋（如 'That's good' 或 'I don't like rain'），則使用 'analyze_sentiment' 工具分析其情感。** 然後簡要回應其情感。

    可依序處理這些任務。""",
    tools=[weather_tool, sentiment_tool]
)

async def main():
    """主函數，非同步執行代理程式。"""
    # 建立會話與 Runner
    session_service = InMemorySessionService()
    # 使用 'await' 正確建立會話
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    runner = Runner(agent=weather_sentiment_agent, app_name=APP_NAME, session_service=session_service)

    # 代理程式互動
    query = "weather in london?"  # 用戶查詢
    print(f"User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    # runner 的 run 方法會自動處理非同步迴圈
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response:", final_response)

# 標準方式執行主非同步函數
if __name__ == "__main__":
    asyncio.run(main())
```

> TypeScript


```typescript
// TypeScript 範例：展示如何在指令中引用工具並處理返回值
// 這個範例展示如何建立兩個工具（取得天氣、分析情感），並在代理程式指令中指定使用順序與錯誤處理。
import { LlmAgent, FunctionTool, InMemoryRunner, isFinalResponse, stringifyContent } from "@google/adk";
import { z } from "zod";
import { Content, createUserContent } from "@google/genai";

/**
 * 取得指定城市的天氣報告。
 */
function getWeatherReport(params: { city: string }): Record<string, any> {
    if (params.city.toLowerCase().includes("london")) {
        return {
            "status": "success",
            "report": "倫敦目前天氣多雲，攝氏 18 度，有降雨機率。",
        };
    }
    if (params.city.toLowerCase().includes("paris")) {
        return {
            "status": "success",
            "report": "巴黎天氣晴朗，攝氏 25 度。",
        };
    }
    return {
        "status": "error",
        "error_message": `無法取得 '${params.city}' 的天氣資訊。`,
    };
}

/**
 * 分析給定文字的情感。
 */
function analyzeSentiment(params: { text: string }): Record<string, any> {
    if (params.text.includes("cloudy") || params.text.includes("rain")) {
        return { "status": "success", "sentiment": "negative" };
    }
    if (params.text.includes("sunny")) {
        return { "status": "success", "sentiment": "positive" };
    }
    return { "status": "success", "sentiment": "neutral" };
}

// 工具註冊：將函數包裝為 FunctionTool，並提供描述與參數結構
const weatherTool = new FunctionTool({
    name: "get_weather_report",
    description: "取得指定城市的天氣報告。",
    parameters: z.object({
        city: z.string().describe("要查詢天氣的城市名稱。"),
    }),
    execute: getWeatherReport,
});

const sentimentTool = new FunctionTool({
    name: "analyze_sentiment",
    description: "分析給定文字的情感。",
    parameters: z.object({
        text: z.string().describe("要分析情感的文字內容。"),
    }),
    execute: analyzeSentiment,
});

// 代理程式指令：明確指示工具使用順序與錯誤處理方式
const instruction = `
    你是一個先查詢天氣再分析情感的助手。

    請依照以下步驟：
    1. 使用 'get_weather_report' 工具取得用戶指定城市的天氣。
    2. 若 'get_weather_report' 工具回傳錯誤，請告知用戶並結束。
    3. 若取得天氣報告，使用 'analyze_sentiment' 工具分析天氣報告的情感。
    4. 最後，向用戶摘要說明天氣報告及其情感。
    `;

const agent = new LlmAgent({
    name: "weather_sentiment_agent",
    instruction: instruction,
    tools: [weatherTool, sentimentTool],
    model: "gemini-2.5-flash"
});

async function main() {
    // 建立代理程式執行環境與會話
    const runner = new InMemoryRunner({ agent: agent, appName: "weather_sentiment_app" });

    await runner.sessionService.createSession({
        appName: "weather_sentiment_app",
        userId: "user1",
        sessionId: "session1"
    });

    const newMessage: Content = createUserContent("What is the weather in London?");

    // 執行代理程式並取得回應
    for await (const event of runner.runAsync({
        userId: "user1",
        sessionId: "session1",
        newMessage: newMessage,
    })) {
        if (isFinalResponse(event) && event.content?.parts?.length) {
            const text = stringifyContent(event).trim();
            if (text) {
                console.log(text);
            }
        }
    }
}

main();
```

> Go


```go
// Go 範例：展示如何在指令中引用工具並處理返回值
// 此範例展示如何建立兩個工具（取得天氣、分析情感），並在代理程式指令中指定使用順序與錯誤處理。
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

// 工具參數結構
type getWeatherReportArgs struct {
    City string `json:"city" jsonschema:"要查詢天氣的城市名稱。"`
}

type getWeatherReportResult struct {
    Status string `json:"status"`
    Report string `json:"report,omitempty"`
}

// 取得指定城市的天氣報告
func getWeatherReport(ctx tool.Context, args getWeatherReportArgs) (getWeatherReportResult, error) {
    if strings.ToLower(args.City) == "london" {
        return getWeatherReportResult{Status: "success", Report: "倫敦目前天氣多雲，攝氏 18 度，有降雨機率。"}, nil
    }
    if strings.ToLower(args.City) == "paris" {
        return getWeatherReportResult{Status: "success", Report: "巴黎天氣晴朗，攝氏 25 度。"}, nil
    }
    return getWeatherReportResult{}, fmt.Errorf("無法取得 '%s' 的天氣資訊。", args.City)
}

type analyzeSentimentArgs struct {
    Text string `json:"text" jsonschema:"要分析情感的文字內容。"`
}

type analyzeSentimentResult struct {
    Sentiment  string  `json:"sentiment"`
    Confidence float64 `json:"confidence"`
}

// 分析給定文字的情感
func analyzeSentiment(ctx tool.Context, args analyzeSentimentArgs) (analyzeSentimentResult, error) {
    if strings.Contains(strings.ToLower(args.Text), "good") || strings.Contains(strings.ToLower(args.Text), "sunny") {
        return analyzeSentimentResult{Sentiment: "positive", Confidence: 0.8}, nil
    }
    if strings.Contains(strings.ToLower(args.Text), "rain") || strings.Contains(strings.ToLower(args.Text), "bad") {
        return analyzeSentimentResult{Sentiment: "negative", Confidence: 0.7}, nil
    }
    return analyzeSentimentResult{Sentiment: "neutral", Confidence: 0.6}, nil
}

func main() {
    ctx := context.Background()
    model, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
    if err != nil {
        log.Fatal(err)
    }

    // 工具註冊：將函數包裝為 FunctionTool，並提供描述
    weatherTool, err := functiontool.New(
        functiontool.Config{
            Name:        "get_weather_report",
            Description: "取得指定城市的天氣報告。",
        },
        getWeatherReport,
    )
    if err != nil {
        log.Fatal(err)
    }

    sentimentTool, err := functiontool.New(
        functiontool.Config{
            Name:        "analyze_sentiment",
            Description: "分析給定文字的情感。",
        },
        analyzeSentiment,
    )
    if err != nil {
        log.Fatal(err)
    }

    // 代理程式指令：明確指示工具使用順序與錯誤處理方式
    weatherSentimentAgent, err := llmagent.New(llmagent.Config{
        Name:        "weather_sentiment_agent",
        Model:       model,
        Instruction: "你是一個提供天氣資訊並分析用戶回饋情感的助手。**當用戶詢問特定城市的天氣時，使用 'get_weather_report' 工具取得天氣細節。** **若 'get_weather_report' 工具回傳 'success'，則將天氣報告提供給用戶。** **若 'get_weather_report' 工具回傳 'error'，則告知用戶該城市無法取得天氣資訊，並詢問是否有其他城市。** **在提供天氣報告後，若用戶對天氣有回饋（如 'That's good' 或 'I don't like rain'），則使用 'analyze_sentiment' 工具分析其情感。** 然後簡要回應其情感。可依序處理這些任務。",
        Tools:       []tool.Tool{weatherTool, sentimentTool},
    })
    if err != nil {
        log.Fatal(err)
    }

    sessionService := session.InMemoryService()
    runner, err := runner.New(runner.Config{
        AppName:        "weather_sentiment_agent",
        Agent:          weatherSentimentAgent,
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatal(err)
    }

    session, err := sessionService.Create(ctx, &session.CreateRequest{
        AppName: "weather_sentiment_agent",
        UserID:  "user1234",
    })
    if err != nil {
        log.Fatal(err)
    }

    run(ctx, runner, session.Session.ID(), "weather in london?")
    run(ctx, runner, session.Session.ID(), "I don't like rain.")
}

// 執行代理程式並印出回應
func run(ctx context.Context, r *runner.Runner, sessionID string, prompt string) {
    fmt.Printf("\n> %s\n", prompt)
    events := r.Run(
        ctx,
        "user1234",
        sessionID,
        genai.NewContentFromText(prompt, genai.RoleUser),
        agent.RunConfig{
            StreamingMode: agent.StreamingModeNone,
        },
    )
    for event, err := range events {
        if err != nil {
            log.Fatalf("執行代理程式時發生錯誤: %v", err)
        }

        if event.Content.Parts[0].Text != "" {
            fmt.Printf("代理程式回應: %s\n", event.Content.Parts[0].Text)
        }
    }
}
```

> Java

```java
// Java 範例：展示如何在指令中引用工具並處理返回值
// 此範例展示如何建立兩個工具（取得天氣、分析情感），並在代理程式指令中指定使用順序與錯誤處理。
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public class WeatherSentimentAgentApp {

    private static final String APP_NAME = "weather_sentiment_agent";
    private static final String USER_ID = "user1234";
    private static final String SESSION_ID = "1234";
    private static final String MODEL_ID = "gemini-2.0-flash";

    /**
     * 取得指定城市的天氣報告。
     *
     * @param city 要查詢天氣的城市名稱。
     * @param toolContext 工具上下文。
     * @return 包含天氣資訊的字典。
     */
    public static Map<String, Object> getWeatherReport(
            @Schema(name = "city")
            String city,
            @Schema(name = "toolContext")
            ToolContext toolContext) {
        Map<String, Object> response = new HashMap<>();

        if (city.toLowerCase(Locale.ROOT).equals("london")) {
            response.put("status", "success");
            response.put(
                    "report",
                    "倫敦目前天氣多雲，攝氏 18 度，有降雨機率。"
            );
        } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
            response.put("status", "success");
            response.put(
                    "report", "巴黎天氣晴朗，攝氏 25 度。"
            );
        } else {
            response.put("status", "error");
            response.put(
                    "error_message", String.format("無法獲取 '%s' 的天氣資訊。", city));
        }
        return response;
    }

    /**
     * 分析給定文字的情感。
     *
     * @param text 要分析情感的文字內容。
     * @param toolContext 工具上下文。
     * @return 包含情感與信心分數的字典。
     */
    public static Map<String, Object> analyzeSentiment(
            @Schema(name = "text")
            String text,
            @Schema(name = "toolContext")
            ToolContext toolContext) {
        Map<String, Object> response = new HashMap<>();
        String lowerText = text.toLowerCase(Locale.ROOT);
        if (lowerText.contains("good") || lowerText.contains("sunny")) {
            response.put("sentiment", "positive");
            response.put("confidence", 0.8);
        } else if (lowerText.contains("rain") || lowerText.contains("bad")) {
            response.put("sentiment", "negative");
            response.put("confidence", 0.7);
        } else {
            response.put("sentiment", "neutral");
            response.put("confidence", 0.6);
        }
        return response;
    }

    /**
     * 呼叫代理程式並印出最終回應。
     *
     * @param runner 執行代理程式的 Runner。
     * @param query 要傳送給代理程式的查詢。
     */
    public static void callAgent(Runner runner, String query) {
        Content content = Content.fromParts(Part.fromText(query));

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
                                System.out.println("Agent 回應: " + finalResponse);
                            }
                        });
    }

    public static void main(String[] args) throws NoSuchMethodException {
        // 工具註冊：將函數包裝為 FunctionTool
        FunctionTool weatherTool =
                FunctionTool.create(
                        WeatherSentimentAgentApp.class.getMethod(
                                "getWeatherReport", String.class, ToolContext.class));
        FunctionTool sentimentTool =
                FunctionTool.create(
                        WeatherSentimentAgentApp.class.getMethod(
                                "analyzeSentiment", String.class, ToolContext.class));

        // 代理程式指令：明確指示工具使用順序與錯誤處理方式
        BaseAgent weatherSentimentAgent =
                LlmAgent.builder()
                        .model(MODEL_ID)
                        .name("weather_sentiment_agent")
                        .description("Weather Sentiment Agent")
                        .instruction("""
                                        你是一個提供天氣資訊並分析用戶回饋情感的助手。
                                        **當用戶詢問特定城市的天氣時，使用 'get_weather_report' 工具取得天氣細節。**
                                        **若 'get_weather_report' 工具回傳 'success'，則將天氣報告提供給用戶。**
                                        **若 'get_weather_report' 工具回傳 'error'，則告知用戶該城市無法取得天氣資訊，並詢問是否有其他城市。**
                                        **在提供天氣報告後，若用戶對天氣有回饋（如 'That's good' 或 'I don't like rain'），則使用 'analyze_sentiment' 工具分析其情感。** 然後簡要回應其情感。
                                        可依序處理這些任務。
                                        """)
                        .tools(ImmutableList.of(weatherTool, sentimentTool))
                        .build();

        InMemorySessionService sessionService = new InMemorySessionService();
        Runner runner = new Runner(weatherSentimentAgent, APP_NAME, null, sessionService);

        // 呼叫代理程式，確保查詢能觸發工具回傳成功
        callAgent(runner, "weather in paris");
    }
}
```

</details>

## 工具上下文 (Tool Context)

對於更進階的情景，ADK 允許您通過包含特殊參數 `tool_context: ToolContext`，在工具函數中訪問額外的上下文資訊。通過在函數簽名中包含此參數，當代理程式執行期間呼叫您的工具時，ADK 將 **自動** 提供 **ToolContext 類別的實例**。

**ToolContext** 提供對幾個關鍵資訊和控制槓桿(levers)的訪問：

* `state: State`：讀取和修改當前會話 (session) 的狀態。在此所做的更改會被追蹤並持久化。

* `actions: EventActions`：影響工具運行後代理程式的後續操作（例如：跳過摘要、轉移到另一個代理程式）。

* `function_call_id: str`：框架為此特定工具調用分配的唯一識別碼。可用於追蹤和與身份驗證回應關聯。當單個模型回應中呼叫多個工具時，這也很有幫助。

* `function_call_event_id: str`：此屬性提供觸發當前工具呼叫的 **事件 (event)** 的唯一識別碼。這對於追蹤和記錄很有用。

* `auth_response: Any`：如果在此工具呼叫之前完成了身份驗證流程，則包含身份驗證回應/憑據。

* 訪問服務：與已配置的服務（如 Artifacts 和 Memory）進行互動的方法。

> [!WARNING]
您不應在工具函數的 docstring 中包含 `tool_context` 參數。由於 `ToolContext` 是在 LLM 決定呼叫工具函數 *之後* 由 ADK 框架自動注入的，因此它與 LLM 的決策無關，包含它可能會混淆 LLM。

### **狀態管理 (State Management)**

`tool_context.state` 屬性提供對當前會話關聯狀態的直接讀寫訪問。它的行為類似於字典，但確保任何修改都作為增量 (deltas) 被追蹤並由會話服務持久化。這使工具能夠在不同的互動和代理程式步驟中維護和共享資訊。

* **讀取狀態**：使用標準字典訪問 (`tool_context.state['my_key']`) 或 `.get()` 方法 (`tool_context.state.get('my_key', default_value)`)。

* **寫入狀態**：直接分配值 (`tool_context.state['new_key'] = 'new_value'`)。這些更改會記錄在結果事件的 state_delta 中。

* **狀態前綴**：記住標準狀態前綴：

    * `app:*`：在應用程式的所有用戶之間共享。

    * `user:*`：特定於當前用戶及其所有會話。

    * (無前綴)：特定於當前會話。

    * `temp:*`：臨時的，不會在多次呼叫之間持久化（可用於在單次運行呼叫中傳遞數據，但在 LLM 呼叫之間運行的工具上下文中通常不太有用）。

<details>
<summary>範例說明</summary>

> Python

```py

# Python 狀態管理範例
from google.adk.tools import ToolContext, FunctionTool

def update_user_preference(preference: str, value: str, tool_context: ToolContext):
    """
    更新用戶特定的偏好設定。

    參數：
        preference: 偏好設定名稱（例如：主題、語言等）。
        value: 偏好設定的值（例如：dark、zh-TW）。
        tool_context: ADK 自動注入的工具上下文，允許讀寫狀態。

    回傳：
        dict，包含 'status'（執行狀態）與 'updated_preference'（已更新的偏好名稱）。
    """
    user_prefs_key = "user:preferences"  # 用戶偏好設定的狀態鍵
    # 取得目前偏好設定，若無則初始化為空字典
    preferences = tool_context.state.get(user_prefs_key, {})
    preferences[preference] = value  # 更新指定偏好名稱的值
    # 將更新後的字典寫回狀態，ADK 會自動追蹤並持久化
    tool_context.state[user_prefs_key] = preferences
    print(f"工具：已將用戶偏好 '{preference}' 更新為 '{value}'")
    return {"status": "success", "updated_preference": preference}

# 將函數包裝為 ADK 工具
pref_tool = FunctionTool(func=update_user_preference)

# 在代理程式中使用範例：
# my_agent = Agent(..., tools=[pref_tool])

# 當 LLM 呼叫 update_user_preference(preference='theme', value='dark', ...)：
# tool_context.state 會被更新，且此變更會成為工具回應事件 actions.state_delta 的一部分。
#
# 重點說明：
# - 工具函數必須有明確型別提示與 docstring，便於 LLM 理解用途。
# - 狀態管理可跨多次互動，支援用戶個人化。
# - 工具上下文 (tool_context) 由 ADK 自動注入，無需在 docstring 描述。
```

> TypeScript

```typescript
// TypeScript 狀態管理範例
// 此範例展示如何更新用戶偏好設定，並將結果寫入 ADK 狀態。
// 主要重點：
// 1. 使用 ToolContext 取得/設定狀態。
// 2. 偏好設定以 user:preferences 為鍵儲存。
// 3. 工具回傳成功狀態與更新後的偏好。

import { ToolContext } from "@google/adk";

// 更新用戶主題偏好設定。
export function updateUserThemePreference(
    value: string,
    toolContext: ToolContext
): Record<string, any> {
    const userPrefsKey = "user:preferences";

    // 取得目前偏好設定，若無則初始化為空物件
    const preferences = toolContext.state.get(userPrefsKey, {}) as Record<string, any>;
    preferences["theme"] = value;

    // 將更新後的偏好設定寫回狀態
    toolContext.state.set(userPrefsKey, preferences);
    console.log(
        `工具：已將用戶偏好 ${userPrefsKey} 更新為 ${JSON.stringify(toolContext.state.get(userPrefsKey))}`
    );

    return {
        status: "success", // 狀態標記為成功
        updated_preference: toolContext.state.get(userPrefsKey), // 回傳更新後的偏好
    };
    // 當 LLM 呼叫 updateUserThemePreference("dark") 時：
    // toolContext.state 會被更新，且此變更會成為工具回應事件 actions.stateDelta 的一部分。
}
```

> Go

```go

// Go 狀態管理範例
// 此範例展示如何更新使用者偏好設定，並將結果寫入 ADK 狀態。
// 主要重點：
// 1. 使用 ToolContext 取得/設定狀態。
// 2. 偏好設定以 user:preferences 為鍵儲存。
// 3. 工具回傳成功狀態與更新後的偏好。

import (
    "fmt"
    "google.golang.org/adk/tool"
)

// 更新使用者偏好設定的參數結構
type updateUserPreferenceArgs struct {
    Preference string `json:"preference" jsonschema:"要設定的偏好名稱。"`
    Value      string `json:"value" jsonschema:"偏好設定的值。"`
}

// 更新偏好設定後的回傳結構
type updateUserPreferenceResult struct {
    UpdatedPreference string `json:"updated_preference"`
}

// 更新使用者偏好設定的工具函式
func updateUserPreference(ctx tool.Context, args updateUserPreferenceArgs) (*updateUserPreferenceResult, error) {
    userPrefsKey := "user:preferences" // 用戶偏好設定的狀態鍵
    val, err := ctx.State().Get(userPrefsKey)
    if err != nil {
        val = make(map[string]any) // 若尚未有偏好則初始化為空 map
    }

    preferencesMap, ok := val.(map[string]any)
    if !ok {
        preferencesMap = make(map[string]any) // 型別不符時也初始化
    }

    preferencesMap[args.Preference] = args.Value // 更新指定偏好名稱的值

    // 將更新後的偏好設定寫回狀態，ADK 會自動追蹤並持久化
    if err := ctx.State().Set(userPrefsKey, preferencesMap); err != nil {
        return nil, err
    }

    fmt.Printf("工具：已將用戶偏好 '%s' 更新為 '%s'\n", args.Preference, args.Value)
    return &updateUserPreferenceResult{
        UpdatedPreference: args.Preference,
    }, nil
}
// 當 LLM 呼叫 updateUserPreference 時：
// ctx.State() 會被更新，且此變更會成為工具回應事件 actions.stateDelta 的一部分。
// 工具函式必須有明確型別提示與註解，便於 LLM 理解用途。
// 狀態管理可跨多次互動，支援用戶個人化。
// ToolContext 由 ADK 自動注入，無需在 docstring 描述。
```

> Java

```java
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;

// 更新用戶特定的偏好設置。
public Map<String, String> updateUserThemePreference(String value, ToolContext toolContext) {
  String userPrefsKey = "user:preferences:theme";

  // 獲取當前偏好或在不存在時初始化
  String preference = toolContext.state().getOrDefault(userPrefsKey, "").toString();
  if (preference.isEmpty()) {
    preference = value;
  }

  // 將更新後的字典寫回狀態
  toolContext.state().put("user:preferences", preference);
  System.out.printf("工具：將用戶偏好 %s 更新為 %s", userPrefsKey, preference);

  return Map.of("status", "success", "updated_preference", toolContext.state().get(userPrefsKey).toString());
  // 當 LLM 呼叫 updateUserThemePreference("dark") 時：
  // toolContext.state 將被更新，並且更改將成為結果工具回應事件 actions.stateDelta 的一部分。
}
```

</details>

### **控制代理程式流程 (Controlling Agent Flow)**

在 Python 和 TypeScript 中為 `tool_context.actions` 屬性，在 Java 中為 `ToolContext.actions()`，在 Go 中則為 `tool.Context.Actions()`，它們持有 **EventActions** 物件。修改此物件上的屬性允許您的工具在工具完成執行後影響代理程式或框架的操作。

* **`skip_summarization: bool`**：(預設值：False) 如果設置為 True，指示 ADK 繞過通常用於總結工具輸出的 LLM 呼叫。如果您的工具返回值已經是可供用戶閱讀的訊息，這將非常有用。

* **`transfer_to_agent: str`**：將此設置為另一個代理程式的名稱。框架將停止當前代理程式的執行，並 **將對話控制權轉移給指定的代理程式**。這允許工具動態地將任務交接給更專門的代理程式。

* **`escalate: bool`**：(預設值：False) 設置為 True 表示當前代理程式無法處理請求，應將控制權向上傳遞給其父代理程式（如果在層級結構中）。在 LoopAgent 中，在子代理程式的工具中設置 **escalate=True** 將終止循環。

#### 範例

<details>
<summary>範例說明</summary>

> Python

```py
# Python 控制代理程式流程範例
# 此範例展示如何在工具中動態轉移到另一個代理程式
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types

# 應用程式常數設定
APP_NAME="customer_support_agent"  # 應用程式名稱
USER_ID="user1234"                  # 用戶 ID
SESSION_ID="1234"                   # 會話 ID


def check_and_transfer(query: str, tool_context: ToolContext) -> str:
    """檢查查詢是否需要升級，並在必要時轉移給另一個代理程式。

    此工具分析用戶查詢中是否包含「緊急」一詞，
    若偵測到緊急情況，將透過 tool_context.actions
    將對話控制權轉移給 support_agent。
    """
    if "urgent" in query.lower():
        print("工具：偵測到緊急情況，正在轉移給支援代理程式。")
        # 關鍵：設定 transfer_to_agent 屬性以觸發代理程式轉移
        tool_context.actions.transfer_to_agent = "support_agent"
        return "正在轉移給支援代理程式..."
    else:
        return f"已處理查詢：'{query}'。無須進一步操作。"

# 將函數包裝為 ADK 工具
escalation_tool = FunctionTool(func=check_and_transfer)

# 建立主代理程式（初始接觸點）
main_agent = Agent(
    model='gemini-2.0-flash',
    name='main_agent',
    instruction="""你是分析工具的首選客戶支援聯絡點。
    回答一般查詢。若用戶表示緊急性，請使用 'check_and_transfer' 工具。""",
    tools=[check_and_transfer]
)

# 建立支援代理程式（處理緊急請求）
support_agent = Agent(
    model='gemini-2.0-flash',
    name='support_agent',
    instruction="""你是專責支援代理程式。
    請提及你是支援處理者，並幫助用戶解決其緊急問題。"""
)

# 將支援代理程式設定為主代理程式的子代理程式
main_agent.sub_agents = [support_agent]

# 非同步函數：建立會話與 Runner
async def setup_session_and_runner():
    """初始化會話服務和 Runner。"""
    session_service = InMemorySessionService()
    # 建立新會話
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    # 建立 Runner 以執行代理程式
    runner = Runner(
        agent=main_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    return session, runner

# 非同步函數：呼叫代理程式並處理回應
async def call_agent_async(query):
    """
    向代理程式發送查詢並處理回應。

    參數：
        query：用戶的查詢文本
    """
    # 建立用戶內容物件
    content = types.Content(role='user', parts=[types.Part(text=query)])
    # 設定會話與 Runner
    session, runner = await setup_session_and_runner()
    # 以非同步方式執行代理程式
    events = runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    )

    # 非同步迭代事件並取得最終回應
    async for event in events:
        if event.is_final_response():
            # 提取最終回應文本
            final_response = event.content.parts[0].text
            print("代理程式回應：", final_response)

# 註記：在 Colab 中，你可以直接在最高層級使用 'await'。
# 若以獨立 Python 指令碼執行此程式碼，
# 你需要使用 asyncio.run() 或手動管理事件迴圈。
await call_agent_async("這很緊急，我無法登入")
```

> TypeScript

```typescript
// TypeScript 控制代理程式流程範例
import { LlmAgent, FunctionTool, ToolContext, InMemoryRunner, isFinalResponse, stringifyContent } from "@google/adk";
import { z } from "zod";
import { Content, createUserContent } from "@google/genai";

// 檢查並轉移工具：若查詢緊急，則設定 transferToAgent
function checkAndTransfer(
  params: { query: string },
  toolContext?: ToolContext
): Record<string, any> {
  // 重點說明：ToolContext 是執行代理程式轉移的關鍵
  if (!toolContext) {
    // 在正常的 ADK 流程中，工具由代理程式呼叫，不應發生此情況
    throw new Error("轉移代理程式需要 ToolContext。");
  }
  // 重點說明：根據查詢內容決定是否轉移
  if (params.query.toLowerCase().includes("urgent")) {
    console.log("工具：偵測到緊急查詢，正在轉移至 support_agent。");
    // 重點說明：設定此屬性以觸發框架進行代理程式轉移
    toolContext.actions.transferToAgent = "support_agent";
    return { status: "success", message: "正在轉移至支援代理程式。" };
  }

  console.log("工具：查詢非緊急，正常處理。");
  return { status: "success", message: "查詢將由主代理程式處理。" };
}

// 將 'checkAndTransfer' 函數包裝成 ADK 工具
const transferTool = new FunctionTool({
  name: "check_and_transfer",
  description: "檢查用戶查詢，若為緊急則轉移至支援代理程式。",
  parameters: z.object({
    query: z.string().describe("要分析的用戶查詢。"),
  }),
  execute: checkAndTransfer,
});

// 支援代理程式：專門處理緊急請求
const supportAgent = new LlmAgent({
  name: "support_agent",
  description: "處理關於帳戶的緊急用戶請求。",
  instruction: "你是支援代理程式。請處理用戶的緊急請求。",
  model: "gemini-2.5-flash"
});

// 主代理程式：作為第一線，並在必要時轉移
const mainAgent = new LlmAgent({
  name: "main_agent",
  description: "路由非緊急查詢的主代理程式。",
  instruction: "你是主代理程式。使用 'check_and_transfer' 工具分析用戶查詢。若查詢不緊急，則自行處理。",
  tools: [transferTool],
  subAgents: [supportAgent], // 重點說明：將支援代理程式註冊為子代理程式
  model: "gemini-2.5-flash"
});

async function main() {
  const runner = new InMemoryRunner({ agent: mainAgent, appName: "customer_support_app" });

  console.log("--- 使用非緊急查詢運行 ---");
  await runner.sessionService.createSession({ appName: "customer_support_app", userId: "user1", sessionId: "session1" });
  const nonUrgentMessage: Content = createUserContent("我對我的帳戶有一個一般性問題。");
  for await (const event of runner.runAsync({ userId: "user1", sessionId: "session1", newMessage: nonUrgentMessage })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const text = stringifyContent(event).trim();
      if (text) {
        console.log(`最終回應: ${text}`);
      }
    }
  }

  console.log("\n--- 使用緊急查詢運行 ---");
  await runner.sessionService.createSession({ appName: "customer_support_app", userId: "user1", sessionId: "session2" });
  const urgentMessage: Content = createUserContent("我的帳戶被鎖了，這很緊急！");
  for await (const event of runner.runAsync({ userId: "user1", sessionId: "session2", newMessage: urgentMessage })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const text = stringifyContent(event).trim();
      if (text) {
        console.log(`最終回應: ${text}`);
      }
    }
  }
}

main();
```

> Go

```go
// Go 控制代理程式流程範例
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

// 'checkAndTransfer' 工具的參數結構
type checkAndTransferArgs struct {
    Query string `json:"query" jsonschema:"用戶的查詢，用於檢查緊急性。"`
}

// 'checkAndTransfer' 工具的回傳結果結構
type checkAndTransferResult struct {
    Status string `json:"status"`
}

// 檢查並轉移工具：若查詢緊急，則設定 TransferToAgent
func checkAndTransfer(ctx tool.Context, args checkAndTransferArgs) (checkAndTransferResult, error) {
    // 重點說明：根據查詢內容決定是否轉移
    if strings.Contains(strings.ToLower(args.Query), "urgent") {
        fmt.Println("工具：偵測到緊急情況，正在轉移給支援代理程式。")
        // 重點說明：透過 Actions() 設定 TransferToAgent 屬性以觸發代理程式轉移
        ctx.Actions().TransferToAgent = "support_agent"
        return checkAndTransferResult{Status: "正在轉移給支援代理程式..."}, nil
    }
    return checkAndTransferResult{Status: fmt.Sprintf("已處理查詢：'%s'。無須進一步操作。", args.Query)}, nil
}

func main() {
    ctx := context.Background()
    model, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
    if err != nil {
        log.Fatal(err)
    }

    // 支援代理程式：專門處理緊急請求
    supportAgent, err := llmagent.New(llmagent.Config{
        Name:        "support_agent",
        Model:       model,
        Instruction: "你是專責支援代理程式。請提及你是支援處理者，並幫助用戶解決其緊急問題。",
    })
    if err != nil {
        log.Fatal(err)
    }

    // 重點說明：將 'checkAndTransfer' 方法包裝成 ADK 工具
    checkAndTransferTool, err := functiontool.New(
        functiontool.Config{
            Name:        "check_and_transfer",
            Description: "檢查查詢是否需要升級，並在必要時轉移給另一個代理程式。",
        },
        checkAndTransfer,
    )
    if err != nil {
        log.Fatal(err)
    }

    // 主代理程式：作為第一線，並在必要時轉移
    mainAgent, err := llmagent.New(llmagent.Config{
        Name:        "main_agent",
        Model:       model,
        Instruction: "你是分析工具的首選客戶支援聯絡點。回答一般查詢。若用戶表示緊急性，請使用 'check_and_transfer' 工具。",
        Tools:       []tool.Tool{checkAndTransferTool},
        SubAgents:   []agent.Agent{supportAgent}, // 重點說明：將支援代理程式註冊為子代理程式
    })
    if err != nil {
        log.Fatal(err)
    }

    sessionService := session.InMemoryService()
    runner, err := runner.New(runner.Config{
        AppName:        "customer_support_agent",
        Agent:          mainAgent,
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatal(err)
    }

    session, err := sessionService.Create(ctx, &session.CreateRequest{
        AppName: "customer_support_agent",
        UserID:  "user1234",
    })
    if err != nil {
        log.Fatal(err)
    }

    // 執行包含緊急關鍵字的查詢以觸發轉移
    run(ctx, runner, session.Session.ID(), "這很緊急，我無法登入")
}

// 執行代理程式並印出回應
func run(ctx context.Context, r *runner.Runner, sessionID string, prompt string) {
    fmt.Printf("\n> %s\n", prompt)
    events := r.Run(
        ctx,
        "user1234",
        sessionID,
        genai.NewContentFromText(prompt, genai.RoleUser),
        agent.RunConfig{
            StreamingMode: agent.StreamingModeNone,
        },
    )
    for event, err := range events {
        if err != nil {
            log.Fatalf("執行代理程式時發生錯誤: %v", err)
        }

        if event.Content.Parts[0].Text != "" {
            fmt.Printf("代理程式回應: %s\n", event.Content.Parts[0].Text)
        }
    }
}
```

> Java

```java
// Java 控制代理程式流程範例
// 此範例展示客戶支援系統中如何透過工具動態轉移代理程式
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.adk.tools.ToolContext;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public class CustomerSupportAgentApp {

  // 應用程式常數設定
  private static final String APP_NAME = "customer_support_agent";  // 應用程式名稱
  private static final String USER_ID = "user1234";                  // 用戶 ID
  private static final String SESSION_ID = "1234";                   // 會話 ID
  private static final String MODEL_ID = "gemini-2.0-flash";        // 使用的模型 ID

  /**
   * 檢查查詢是否需要升級，並在必要時轉移給另一個代理程式。
   *
   * 重點說明：此工具示範如何使用 ToolContext 動態控制代理程式流程
   *
   * @param query 用戶的查詢內容
   * @param toolContext 工具上下文，用於訪問狀態和執行動作
   * @return 包含檢查和轉移結果的對應表
   */
  public static Map<String, Object> checkAndTransfer(
      @Schema(name = "query", description = "用戶查詢內容")
      String query,
      @Schema(name = "toolContext", description = "工具上下文")
      ToolContext toolContext) {
    Map<String, Object> response = new HashMap<>();
    // 重點說明：檢查查詢中是否包含「urgent」關鍵字
    if (query.toLowerCase(Locale.ROOT).contains("urgent")) {
      System.out.println("工具：偵測到緊急情況，正在轉移給支援代理程式。");
      // 重點說明：透過 toolContext.actions() 設定轉移目標代理程式
      toolContext.actions().setTransferToAgent("support_agent");
      response.put("status", "transferring");
      response.put("message", "正在轉移給支援代理程式...");
    } else {
      // 重點說明：非緊急查詢則正常處理，不進行轉移
      response.put("status", "processed");
      response.put(
          "message", String.format("已處理查詢：'%s'。無須進一步操作。", query));
    }
    return response;
  }

  /**
   * 使用給定的查詢呼叫代理程式並印出最終回應。
   *
   * @param runner 要使用的 Runner 實例
   * @param query 要發送給代理程式的查詢
   */
  public static void callAgent(Runner runner, String query) {
    // 重點說明：建立包含用戶查詢的 Content 物件
    Content content =
        Content.fromParts(Part.fromText(query));

    // 重點說明：取得會話服務並建立新會話
    InMemorySessionService sessionService = (InMemorySessionService) runner.sessionService();
    // 修正說明：session ID 不需要是 optional
    Session session =
        sessionService
            .createSession(APP_NAME, USER_ID, /* state= */ null, SESSION_ID)
            .blockingGet();

    // 重點說明：非同步執行代理程式並處理回應事件
    runner
        .runAsync(session.userId(), session.id(), content)
        .forEach(
            event -> {
              // 重點說明：檢查是否為最終回應並提取文字內容
              if (event.finalResponse()
                  && event.content().isPresent()
                  && event.content().get().parts().isPresent()
                  && !event.content().get().parts().get().isEmpty()
                  && event.content().get().parts().get().get(0).text().isPresent()) {
                String finalResponse = event.content().get().parts().get().get(0).text().get();
                System.out.println("代理程式回應：" + finalResponse);
              }
            });
  }

  public static void main(String[] args) throws NoSuchMethodException {
    // 重點說明：建立升級工具，使用反射取得 checkAndTransfer 方法
    FunctionTool escalationTool =
        FunctionTool.create(
            CustomerSupportAgentApp.class.getMethod(
                "checkAndTransfer", String.class, ToolContext.class));

    // 重點說明：建立支援代理程式，專門處理緊急請求
    LlmAgent supportAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("support_agent")
            .description("""
                專責的支援代理程式。
                會提及自己是支援處理者，並協助用戶處理緊急問題。
            """)
            .instruction("""
                你是專責的支援代理程式。
                請提及你是支援處理者，並協助用戶解決其緊急問題。
            """)
            .build();

    // 重點說明：建立主代理程式，作為第一線接觸點
    LlmAgent mainAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("main_agent")
            .description("""
                分析工具客戶支援的第一接觸點。
                回答一般查詢。
                若用戶表示緊急性，會使用 'check_and_transfer' 工具。
                """)
            .instruction("""
                你是分析工具客戶支援的第一接觸點。
                回答一般查詢。
                若用戶表示緊急性，請使用 'check_and_transfer' 工具。
                """)
            .tools(ImmutableList.of(escalationTool))  // 重點說明：註冊升級工具
            .subAgents(supportAgent)                   // 重點說明：將支援代理程式設為子代理程式
            .build();
    // 修正說明：LlmAgent.subAgents() 不需要參數。
    // 子代理程式現在透過建構器加入主代理程式，
    // 因為 `subAgents` 是一個應該在代理程式建構時設定的屬性，
    // 除非它是動態管理的。

    // 重點說明：初始化會話服務和 Runner
    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(mainAgent, APP_NAME, null, sessionService);

    // 代理程式互動
    // 重點說明：呼叫代理程式處理包含「urgent」關鍵字的緊急查詢
    callAgent(runner, "這很緊急，我無法登入");
  }
}
```
</details>

##### 解說

* 我們定義了兩個代理程式：`main_agent` 和 `support_agent`。`main_agent` 被設計為初始聯繫點。
* 當 `main_agent` 呼叫 `check_and_transfer` 工具時，該工具會檢查用戶的查詢。
* 如果查詢包含 "urgent"（緊急）一詞，該工具將訪問 `tool_context`，特別是 **`tool_context.actions`**，並將 `transfer_to_agent` 屬性設置為 `support_agent`。
* 此操作向框架發出訊號，**將對話控制權轉移給名為 `support_agent` 的代理程式**。
* 當 `main_agent` 處理緊急查詢時，`check_and_transfer` 工具會觸發轉移。隨後的響應理想情況下將來自 `support_agent`。
* 對於沒有緊急性的正常查詢，工具只是對其進行處理而不觸發轉移。

此範例說明了工具如何通過其 ToolContext 中的 EventActions，藉由將控制權轉移給另一個專門代理程式來動態影響對話流。

### **身份驗證 (Authentication)**

ToolContext 為與受身份驗證 API 互動的工具提供機制。如果您的**工具需要處理身份驗證**，您可以使用以下功能：

* **`auth_response`** (Python)：如果框架在呼叫您的工具之前已處理了身份驗證（常見於 RestApiTool 和 OpenAPI 安全方案），則包含憑據（例如：權杖 (token)）。在 TypeScript 中，這通過 getAuthResponse() 方法檢索。

* **`request_credential(auth_config: dict)`** (Python) 或 **`requestCredential(authConfig: AuthConfig)`** (TypeScript)：如果您的工具判斷需要身份驗證但憑據不可用，請呼叫此方法。這向框架發出訊號，啟動基於提供的 auth_config 的身份驗證流程。

* **`get_auth_response()`** (Python) 或 **`getAuthResponse(authConfig: AuthConfig)`** (TypeScript)：在隨後的調用中（在 request_credential 被成功處理之後）呼叫此方法，以檢索用戶提供的憑據。

有關身份驗證流程、配置和範例的詳細說明，請參閱專用的「工具身份驗證」文件頁面。

### **上下文感知數據訪問方法 (Context-Aware Data Access Methods)**

這些方法為您的工具提供了與會話或用戶關聯的持久數據進行互動的便捷方式，這些數據由配置的服務管理。

* **`list_artifacts()`** (Python) 或 **`listArtifacts()`** (Java 與 TypeScript)：返回當前會話通過 artifact_service 存儲的所有 artifact（工件）的文件名（或鍵）列表。Artifact 通常是用戶上傳的或由工具/代理程式生成的檔案（圖像、文件等）。

* **`load_artifact(filename: str)`**：通過文件名從 **artifact_service** 檢索特定的 artifact。您可以選擇指定版本；如果省略，則返回最新版本。返回包含 artifact 數據和 mime 類型的 `google.genai.types.Part` 物件，如果未找到則返回 None。

* **`save_artifact(filename: str, artifact: types.Part)`**：將新版本的 artifact 保存到 artifact_service。返回新的版本號（從 0 開始）。

* **`search_memory(query: str)`**：(ADK Python, Go 和 TypeScript 支援)
    使用配置的 `memory_service` 查詢用戶的長期記憶。這對於從過去的互動或存儲的知識中檢索相關資訊非常有用。**SearchMemoryResponse** 的結構取決於特定的記憶服務實現，但通常包含相關的文本片段或對話摘錄。

#### 範例

<details>
<summary>範例說明</summary>

> Python

```py
# Python 上下文感知數據訪問範例
# 重點說明：展示如何透過 ToolContext 存取 artifact 和記憶服務
from google.adk.tools import ToolContext, FunctionTool
from google.genai import types


def process_document(
    document_name: str, analysis_query: str, tool_context: ToolContext
) -> dict:
    """使用記憶中的上下文分析文件。"""

    # 1. 載入 artifact
    # 重點說明：使用 load_artifact() 從 artifact 服務中檢索已儲存的文件
    print(f"工具：嘗試載入 artifact：{document_name}")
    document_part = tool_context.load_artifact(document_name)

    if not document_part:
        return {"status": "error", "message": f"找不到文件 '{document_name}'。"}

    document_text = document_part.text  # 為簡化起見，假設它是文字
    print(f"工具：已載入文件 '{document_name}' ({len(document_text)} 字元)。")

    # 2. 搜尋記憶以獲取相關上下文
    # 重點說明：使用 search_memory() 從記憶服務中查詢相關的歷史資訊
    print(f"工具：搜尋與以下內容相關的記憶上下文：'{analysis_query}'")
    memory_response = tool_context.search_memory(
        f"分析關於 {analysis_query} 的文件的上下文"
    )
    memory_context = "\n".join(
        [
            m.events[0].content.parts[0].text
            for m in memory_response.memories
            if m.events and m.events[0].content
        ]
    )  # 簡化的提取方式
    print(f"工具：找到記憶上下文：{memory_context[:100]}...")

    # 3. 執行分析（佔位符）
    # 重點說明：結合文件內容和記憶上下文進行分析
    analysis_result = f"關於 '{analysis_query}' 對 '{document_name}' 的分析，使用記憶上下文：[佔位符分析結果]"
    print("工具：已執行分析。")

    # 4. 將分析結果儲存為新的 artifact
    # 重點說明：使用 save_artifact() 將結果持久化，返回版本號
    analysis_part = types.Part.from_text(text=analysis_result)
    new_artifact_name = f"analysis_{document_name}"
    version = await tool_context.save_artifact(new_artifact_name, analysis_part)
    print(f"工具：已將分析結果儲存為 '{new_artifact_name}' 版本 {version}。")

    return {
        "status": "success",
        "analysis_artifact": new_artifact_name,
        "version": version,
    }


# 重點說明：將函數包裝為 ADK 工具
doc_analysis_tool = FunctionTool(func=process_document)

# 在 Agent 中使用：
# 假設先前已儲存 artifact 'report.txt'。
# 假設記憶服務已配置並具有相關的過去資料。
# my_agent = Agent(..., tools=[doc_analysis_tool], artifact_service=..., memory_service=...)
```

> TypeScript

```typescript
// TypeScript 上下文感知數據訪問範例
// 重點說明：展示如何透過 ToolContext 存取 artifact 和記憶服務
import { Part } from "@google/genai";
import { ToolContext } from "@google/adk";

// 使用記憶中的上下文分析文件。
export async function processDocument(
  params: { documentName: string; analysisQuery: string },
  toolContext?: ToolContext
): Promise<Record<string, any>> {
  if (!toolContext) {
    throw new Error("此工具需要 ToolContext。");
  }

  // 1. 列出所有可用的 artifact
  // 重點說明：使用 listArtifacts() 查看當前會話中所有已儲存的 artifact
  const artifacts = await toolContext.listArtifacts();
  console.log(`列出所有可用的 artifact：${artifacts}`);

  // 2. 載入 artifact
  // 重點說明：使用 loadArtifact() 從 artifact 服務中檢索指定的文件
  console.log(`工具：嘗試載入 artifact：${params.documentName}`);
  const documentPart = await toolContext.loadArtifact(params.documentName);
  if (!documentPart) {
    console.log(`工具：找不到文件 '${params.documentName}'。`);
    return {
      status: "error",
      message: `找不到文件 '${params.documentName}'。`,
    };
  }

  const documentText = documentPart.text ?? "";
  console.log(
    `工具：已載入文件 '${params.documentName}' (${documentText.length} 字元)。`
  );

  // 3. 搜尋記憶以獲取相關上下文
  // 重點說明：使用 searchMemory() 從記憶服務中查詢相關的歷史資訊
  console.log(`工具：搜尋與 '${params.analysisQuery}' 相關的記憶上下文`);
  const memory_results = await toolContext.searchMemory(params.analysisQuery);
  console.log(`工具：找到 ${memory_results.memories.length} 個相關記憶。`);
  const context_from_memory = memory_results.memories
    .map((m) => m.content.parts[0].text)
    .join("\n");

  // 4. 執行分析（佔位符）
  // 重點說明：結合文件內容和記憶上下文進行分析
  const analysisResult =
    `關於 '${params.analysisQuery}' 對 '${params.documentName}' 的分析：\n` +
    `來自記憶的上下文：\n${context_from_memory}\n` +
    `[佔位符分析結果]`;
  console.log("工具：已執行分析。");

  // 5. 將分析結果儲存為新的 artifact
  // 重點說明：使用 saveArtifact() 將結果持久化
  const analysisPart: Part = { text: analysisResult };
  const newArtifactName = `analysis_${params.documentName}`;
  await toolContext.saveArtifact(newArtifactName, analysisPart);
  console.log(`工具：已將分析結果儲存至 '${newArtifactName}'。`);

  return {
    status: "success",
    analysis_artifact: newArtifactName,
  };
}
```

> Go

```go
// Go 上下文感知數據訪問範例
// 重點說明：展示如何透過 tool.Context 存取 artifact 和記憶服務
package main

import (
    "fmt"

    "google.golang.org/adk/tool"
    "google.golang.org/genai"
)

// 重點說明：定義函數參數結構，使用 jsonschema 標籤提供參數描述
type processDocumentArgs struct {
    DocumentName  string `json:"document_name" jsonschema:"要處理的文件名稱。"`
    AnalysisQuery string `json:"analysis_query" jsonschema:"分析的查詢。"`
}

// 重點說明：定義函數返回結果結構
type processDocumentResult struct {
    Status           string `json:"status"`
    AnalysisArtifact string `json:"analysis_artifact,omitempty"`
    Version          int64  `json:"version,omitempty"`
    Message          string `json:"message,omitempty"`
}

func processDocument(ctx tool.Context, args processDocumentArgs) (*processDocumentResult, error) {
    fmt.Printf("工具：嘗試載入 artifact：%s\n", args.DocumentName)

    // 列出所有 artifact
    // 重點說明：使用 Artifacts().List() 查看當前會話中所有已儲存的 artifact
    listResponse, err := ctx.Artifacts().List(ctx)
    if err != nil {
        return nil, fmt.Errorf("無法列出 artifact")
    }

    fmt.Println("工具：可用的 artifact：")
    for _, file := range listResponse.FileNames {
        fmt.Printf(" - %s\n", file)
    }

    // 重點說明：使用 Artifacts().Load() 從 artifact 服務中載入指定的文件
    documentPart, err := ctx.Artifacts().Load(ctx, args.DocumentName)
    if err != nil {
        return nil, fmt.Errorf("找不到文件 '%s'", args.DocumentName)
    }

    fmt.Printf("工具：已載入文件 '%s'，大小為 %d 位元組。\n", args.DocumentName, len(documentPart.Part.InlineData.Data))

    // 3. 搜尋記憶以獲取相關上下文
    // 重點說明：使用 SearchMemory() 從記憶服務中查詢相關的歷史資訊
    fmt.Printf("工具：搜尋與以下內容相關的記憶上下文：'%s'\n", args.AnalysisQuery)
    memoryResp, err := ctx.SearchMemory(ctx, args.AnalysisQuery)
    if err != nil {
        fmt.Printf("工具：搜尋記憶時發生錯誤：%v\n", err)
    }
    memoryResultCount := 0
    if memoryResp != nil {
        memoryResultCount = len(memoryResp.Memories)
    }
    fmt.Printf("工具：找到 %d 個記憶結果。\n", memoryResultCount)

    // 重點說明：結合文件內容和記憶上下文進行分析
    analysisResult := fmt.Sprintf("關於 '%s' 對 '%s' 的分析，使用記憶上下文：[佔位符分析結果]", args.DocumentName, args.AnalysisQuery)
    fmt.Println("工具：已執行分析。")

    // 重點說明：使用 Artifacts().Save() 將分析結果持久化，返回版本資訊
    analysisPart := genai.NewPartFromText(analysisResult)
    newArtifactName := fmt.Sprintf("analysis_%s", args.DocumentName)
    version, err := ctx.Artifacts().Save(ctx, newArtifactName, analysisPart)
    if err != nil {
        return nil, fmt.Errorf("無法儲存 artifact")
    }
    fmt.Printf("工具：已將分析結果儲存為 '%s' 版本 %d。\n", newArtifactName, version.Version)

    return &processDocumentResult{
        Status:           "success",
        AnalysisArtifact: newArtifactName,
        Version:          version.Version,
    }, nil
}
```

> Java

```java
/**
 * 使用記憶中的上下文分析文件。
 * 重點說明：展示如何透過 ToolContext 存取 artifact 和記憶服務。
 * 您也可以使用 Callback Context 或 LoadArtifacts 工具列出、載入和儲存 artifact。
 *
 * @param documentName 要分析的文件名稱。
 * @param analysisQuery 分析的查詢。
 * @param toolContext 工具上下文。
 * @return 分析結果的描述。
 */
public static @NonNull Maybe<ImmutableMap<String, Object>> processDocument(
    @Annotations.Schema(description = "要分析的文件名稱。") String documentName,
    @Annotations.Schema(description = "分析的查詢。") String analysisQuery,
    ToolContext toolContext) {

  // 1. 列出所有可用的 artifact
  // 重點說明：使用 listArtifacts() 查看當前會話中所有已儲存的 artifact
  System.out.printf(
      "列出所有可用的 artifact %s：", toolContext.listArtifacts().blockingGet());

  // 2. 將 artifact 載入到記憶體
  // 重點說明：使用 loadArtifact() 從 artifact 服務中檢索指定的文件
  System.out.println("工具：嘗試載入 artifact：" + documentName);
  Part documentPart = toolContext.loadArtifact(documentName, Optional.empty()).blockingGet();
  if (documentPart == null) {
    System.out.println("工具：找不到文件 '" + documentName + "'。");
    return Maybe.just(
        ImmutableMap.<String, Object>of(
            "status", "error", "message", "找不到文件 '" + documentName + "'。"));
  }
  String documentText = documentPart.text().orElse("");
  System.out.println(
      "工具：已載入文件 '" + documentName + "' (" + documentText.length() + " 字元)。");

  // 3. 執行分析（佔位符）
  // 重點說明：結合文件內容和記憶上下文進行分析
  String analysisResult =
      "關於 '"
          + analysisQuery
          + "' 對 '"
          + documentName
          + "' 的分析 [佔位符分析結果]";
  System.out.println("工具：已執行分析。");

  // 4. 將分析結果儲存為新的 artifact
  // 重點說明：使用 saveArtifact() 將結果持久化
  Part analysisPart = Part.fromText(analysisResult);
  String newArtifactName = "analysis_" + documentName;

  toolContext.saveArtifact(newArtifactName, analysisPart);

  return Maybe.just(
      ImmutableMap.<String, Object>builder()
          .put("status", "success")
          .put("analysis_artifact", newArtifactName)
          .build());
}
// 重點說明：建立 FunctionTool 包裝函數
// FunctionTool processDocumentTool =
//      FunctionTool.create(ToolContextArtifactExample.class, "processDocument");
// 在 Agent 中包含此函數工具。
// LlmAgent agent = LlmAgent().builder().tools(processDocumentTool).build();
```

</details>

通過利用 **ToolContext**，開發者可以創建更複雜且具備上下文感知的自定義工具，這些工具可以與 ADK 的架構無縫整合並增強代理程式的整體能力。

## 定義有效的工具函數

當將方法或函數用作 ADK 工具時，您定義它的方式會顯著影響代理程式正確使用它的能力。代理程式的大型語言模型 (LLM) 嚴重依賴函數的 **名稱**、**參數 (arguments)**、**型別提示 (type hints)** 以及 **docstring / 原始碼註釋** 來理解其用途並生成正確的調用。

以下是定義有效工具函數的關鍵指南：

* **函數名稱 (Function Name)：**
    * 使用具描述性的、基於「動詞-名詞」的名稱，清楚地指示操作（例如：`get_weather`、`searchDocuments`、`schedule_meeting`）。
    * 避免使用通用名稱如 `run`、`process`、`handle_data`，或過於模糊的名稱如 `doStuff`。即使有很好的描述，像 `do_stuff` 這樣的名稱也可能讓模型對於何時使用該工具感到困惑（相較於例如 `cancelFlight`）。
    * LLM 在工具選擇期間將函數名稱作為主要識別碼。

* **參數 (Parameters)：**
    * 您的函數可以有任意數量的參數。
    * 使用清晰且具描述性的名稱（例如：使用 `city` 而不是 `c`，使用 `search_query` 而不是 `q`）。
    * **在 Python 中為所有參數提供型別提示**（例如：`city: str`、`user_id: int`、`items: list[str]`）。這對於 ADK 為 LLM 生成正確的架構 (schema) 至關重要。
    * 確保所有參數型別都是 **JSON 可序列化的**。所有 Java 原始型別以及標準 Python 型別如 `str`、`int`、`float`、`bool`、`list`、`dict` 及其組合通常是安全的。除非具有清晰的 JSON 表示，否則請避免將複雜的自定義類別實例作為直接參數。
    * **不要為參數設置預設值**。例如：`def my_func(param1: str = "default")`。底層模型在生成函數呼叫期間無法可靠地支援或使用預設值。所有必要的資訊都應由 LLM 從上下文中推導出，或者在缺失時明確請求。
    * **`self` / `cls` 自動處理**：隱含參數如 `self`（對於實例方法）或 `cls`（對於類別方法）由 ADK 自動處理，並從顯示給 LLM 的架構中排除。您只需要為工具要求 LLM 提供的邏輯參數定義型別提示和描述。

* **返回型別 (Return Type)：**
    * 函數的返回值 **在 Python 中必須是字典 (`dict`)**，在 **Java 中必須是 Map**，在 **TypeScript 中必須是純物件 (object)**。
    * 如果您的函數返回非字典型別（例如：字串、數字、列表），ADK 框架將在將結果傳回模型之前，自動將其包裝到字典/Map 中，如 `{'result': your_original_return_value}`。
    * 將字典/Map 的鍵和值設計為 **具描述性且易於被 LLM 理解**。記住，模型讀取此輸出來決定其下一步。
    * 包含有意義的鍵。例如，不要只返回錯誤代碼如 `500`，應返回 `{'status': 'error', 'error_message': 'Database connection failed'}`。
    * **強烈建議的做法** 是包含一個 `status` 鍵（例如：`'success'`、`'error'`、`'pending'`、`'ambiguous'`），以便為模型清楚地指示工具執行的結果。

* **Docstring / 原始碼註釋：**
    * **這是至關重要的。** Docstring 是 LLM 獲取描述性資訊的主要來源。
    * **清楚地陳述工具的 *功能*。** 明確其用途和限制。
    * **解釋 *何時* 應該使用該工具。** 提供背景資訊或範例場景以引導 LLM 的決策。
    * **清楚地描述 *每個參數*。** 解釋 LLM 需要為該參數提供什麼資訊。
    * 描述 **預期 `dict` 返回值的結構和含義**，特別是不同的 `status` 值和關聯的數據鍵。
    * **不要描述注入的 ToolContext 參數**。避免在 docstring 描述中提到可選的 `tool_context: ToolContext` 參數，因為它不是 LLM 需要知道的參數。ToolContext 是在 LLM 決定呼叫它 *之後* 由 ADK 注入的。

    **良好定義的範例：**

<details>
<summary>範例說明</summary>

> Python

```python
def lookup_order_status(order_id: str) -> dict:
  """根據 ID 獲取客戶訂單的當前狀態。

  僅當用戶明確詢問特定訂單的狀態並提供訂單 ID 時，才使用此工具。
  請勿將其用於一般查詢。

  參數:
      order_id: 要查詢的訂單唯一識別碼。

  返回:
      一個指示結果的字典。
      成功時，status 鍵為 'success' 並包含一個 'order' 字典。
      失敗時，status 鍵為 'error' 並包含一個 'error_message'。
      成功範例: {'status': 'success', 'order': {'state': 'shipped', 'tracking_number': '1Z9...'}}
      錯誤範例: {'status': 'error', 'error_message': 'Order ID not found.'}
  """
  # ... 獲取狀態的函數實現 ...
  if status_details := fetch_status_from_backend(order_id):
    return {
        "status": "success",
        "order": {
            "state": status_details.state,
            "tracking_number": status_details.tracking,
        },
    }
  else:
    return {"status": "error", "error_message": f"Order ID {order_id} not found."}

```

> TypeScript

```typescript
/**
 * 根據 ID 獲取客戶訂單的當前狀態。
 *
 * 僅當用戶明確詢問特定訂單的狀態並提供訂單 ID 時，才使用此工具。
 * 請勿將其用於一般查詢。
 *
 * @param params 函數參數。
 * @param params.order_id 要查詢的訂單唯一識別碼。
 * @returns 一個指示結果的字典。
 *          成功時，status 為 'success' 並包含一個 'order' 字典。
 *          失敗時，status 為 'error' 並包含一個 'error_message'。
 *          成功範例: {'status': 'success', 'order': {'state': 'shipped', 'tracking_number': '1Z9...'}}
 *          錯誤範例: {'status': 'error', 'error_message': 'Order ID not found.'}
 */
async function lookupOrderStatus(params: { order_id: string }): Promise<Record<string, any>> {
  // ... 從後端獲取狀態的函數實現 ...
  const status_details = await fetchStatusFromBackend(params.order_id);
  if (status_details) {
    return {
      "status": "success",
      "order": {
        "state": status_details.state,
        "tracking_number": status_details.tracking,
      },
    };
  } else {
    return { "status": "error", "error_message": `Order ID ${params.order_id} not found.` };
  }
}

// 後端呼叫佔位符
async function fetchStatusFromBackend(order_id: string): Promise<{state: string, tracking: string} | null> {
    if (order_id === "12345") {
        return { state: "shipped", tracking: "1Z9..." };
    }
    return null;
}
```

> Go

```go
// Go 訂單狀態查詢範例
import (
    "fmt"

    "google.golang.org/adk/tool"
)

type lookupOrderStatusArgs struct {
    OrderID string `json:"order_id" jsonschema:"The ID of the order to look up."`
}

type order struct {
    State          string `json:"state"`
    TrackingNumber string `json:"tracking_number"`
}

type lookupOrderStatusResult struct {
    Status string `json:"status"`
    Order  order  `json:"order,omitempty"`
}

func lookupOrderStatus(ctx tool.Context, args lookupOrderStatusArgs) (*lookupOrderStatusResult, error) {
    // ... function implementation to fetch status ...
    statusDetails, ok := fetchStatusFromBackend(args.OrderID)
    if !ok {
        return nil, fmt.Errorf("order ID %s not found", args.OrderID)
    }
    return &lookupOrderStatusResult{
        Status: "success",
        Order: order{
            State:          statusDetails.State,
            TrackingNumber: statusDetails.Tracking,
        },
    }, nil
}
```

> Java

```java
/**
 * 獲取指定城市的當前天氣報告。
 *
 * @param city 要獲取天氣報告的城市。
 * @param toolContext 工具上下文。
 * @return 包含天氣資訊的字典。
 */
public static Map<String, Object> getWeatherReport(String city, ToolContext toolContext) {
    Map<String, Object> response = new HashMap<>();
    if (city.toLowerCase(Locale.ROOT).equals("london")) {
        response.put("status", "success");
        response.put(
                "report",
                "倫敦當前的天氣是多雲，氣溫為攝氏 18 度，有降雨機率。");
    } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
        response.put("status", "success");
        response.put("report", "巴黎的天氣晴朗，氣溫為攝氏 25 度。");
    } else {
        response.put("status", "error");
        response.put("error_message", String.format("無法獲取 '%s' 的天氣資訊。", city));
    }
    return response;
}
```

</details>

* **簡單與專注 (Simplicity and Focus)：**
    * **保持工具專注**：每個工具理想情況下應執行一項定義明確的任務。
    * **參數越少越好**：相較於具有許多可選或複雜參數的工具，模型通常能更可靠地處理參數較少且定義明確的工具。
    * **使用簡單的數據型別**：儘可能優先選用基本型別（**Python** 中的 `str`、`int`、`bool`、`float`、`List[str]`；**Java** 中的 `int`、`byte`、`short`、`long`、`float`、`double`、`boolean` 和 `char`；或 **TypeScript** 中的 `string`、`number`、`boolean` 以及數組如 `string[]`），而非複雜的自定義類別或深度嵌套的結構。
    * **分解複雜任務**：將執行多個不同邏輯步驟的函數分解為更小、更專注的工具。例如，不要使用單個 `update_user_profile(profile: ProfileObject)` 工具，而是考慮分開的工具如 `update_user_name(name: str)`、`update_user_address(address: str)`、`update_user_preferences(preferences: list[str])` 等。這使得 LLM 更容易選擇和使用正確的能力。

通過遵循這些指南，您為 LLM 提供了有效利用自定義函數工具所需的清晰度和結構，從而實現功能更強大且更可靠的代理程式行為。

---
### 最佳實作總結

以下表格總結了定義有效工具函數的關鍵最佳實作：

| 類別            | 最佳實作                       | 說明                                                                   | 範例                                                                                                                    |
| --------------- | ------------------------------ | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **函數名稱**    | 使用具描述性的動詞-名詞命名    | 清楚指示操作的名稱，讓 LLM 易於理解工具用途                            | ✅ `get_weather`, `searchDocuments`, `schedule_meeting`<br>❌ `run`, `process`, `doStuff`                                 |
| **參數命名**    | 使用清晰且具描述性的名稱       | 避免縮寫，讓參數意圖明確                                               | ✅ `city`, `search_query`, `user_id`<br>❌ `c`, `q`, `uid`                                                                |
| **型別提示**    | 為所有參數提供型別提示         | Python: 使用型別註解<br>Java: 原生型別系統<br>TypeScript: 使用介面定義 | Python: `city: str`, `count: int`, `items: list[str]`<br>TypeScript: `params: { city: string }`                         |
| **參數型別**    | 使用 JSON 可序列化型別         | 確保 LLM 能正確生成函數呼叫                                            | ✅ `str`, `int`, `float`, `bool`, `list`, `dict`<br>❌ 複雜自定義類別實例                                                 |
| **預設值**      | 不要設置參數預設值             | LLM 無法可靠支援預設值，所有必要資訊應從上下文推導                     | ❌ `def my_func(param: str = "default")`<br>✅ `def my_func(param: str)`                                                  |
| **返回型別**    | 返回結構化的字典/Map/物件      | Python: `dict`<br>Java: `Map`<br>TypeScript: `object`                  | `{'status': 'success', 'data': {...}}`                                                                                  |
| **返回值結構**  | 包含描述性且易於理解的鍵值     | 使用有意義的鍵，包含 `status` 欄位指示執行結果                         | ✅ `{'status': 'success', 'order': {...}}`<br>❌ `{'code': 500}`                                                          |
| **狀態指示**    | 使用 `status` 鍵表示結果       | 清楚指示工具執行的結果狀態                                             | `'success'`, `'error'`, `'pending'`, `'ambiguous'`                                                                      |
| **Docstring**   | 提供完整且清晰的文件           | 說明功能、使用時機、參數和返回值結構                                   | 包含：工具功能、使用場景、參數說明、返回值範例                                                                          |
| **功能描述**    | 清楚陳述工具的功能與限制       | 讓 LLM 理解工具的確切用途                                              | "根據 ID 獲取客戶訂單的當前狀態"                                                                                        |
| **使用時機**    | 解釋何時應該使用該工具         | 提供背景資訊或範例場景                                                 | "僅當用戶明確詢問特定訂單的狀態並提供訂單 ID 時使用"                                                                    |
| **參數文件**    | 清楚描述每個參數               | 解釋 LLM 需要為該參數提供的資訊                                        | "order_id: 要查詢的訂單唯一識別碼"                                                                                      |
| **返回值文件**  | 描述返回值的結構和含義         | 說明不同狀態值和關聯的數據鍵                                           | "成功時 status 為 'success' 並包含 'order' 字典"                                                                        |
| **ToolContext** | 不要在文件中描述注入參數       | `tool_context` 由 ADK 自動注入，不需要在 docstring 中說明              | ❌ 在 docstring 中提到 `tool_context` 參數                                                                               |
| **工具專注性**  | 每個工具執行一項定義明確的任務 | 保持工具功能單一且專注                                                 | ✅ 單一職責的工具<br>❌ 執行多個不相關操作的工具                                                                          |
| **參數數量**    | 參數越少越好                   | 減少參數數量提高 LLM 正確使用的可靠性                                  | 優先使用 2-4 個參數而非 10+ 個參數                                                                                      |
| **數據型別**    | 使用簡單的基本型別             | 避免複雜或深度嵌套的結構                                               | ✅ 基本型別和簡單列表<br>❌ 深度嵌套的自定義物件                                                                          |
| **任務分解**    | 將複雜任務分解為多個小工具     | 讓 LLM 更容易選擇和使用正確的功能                                      | ❌ `update_user_profile(profile: ProfileObject)`<br>✅ `update_user_name(name: str)`, `update_user_address(address: str)` |

**關鍵要點：**

- **清晰度優先**：函數名稱、參數和文件都應該讓 LLM 能輕鬆理解
- **結構化輸出**：始終返回包含 `status` 的結構化字典，清楚指示執行結果
- **簡單勝於複雜**：使用基本型別，保持工具專注，分解複雜任務
- **完整文件**：詳細的 docstring 是 LLM 正確使用工具的關鍵

## 工具集 (Toolsets)：分組與動態提供工具

[`ADK 支援`: `Python v0.5.0` | `Typescript v0.2.0`]

除了單個工具外，ADK 還通過 `BaseToolset` 介面（定義於 `google.adk.tools.base_toolset`）引入了 **工具集 (Toolset)** 的概念。工具集允許您管理並向代理程式提供一組 `BaseTool` 實例，通常是動態提供的。

這種方法有利於：

*   **組織相關工具**：將具有共同用途的工具進行分組（例如：所有用於數學運算的工具，或所有與特定 API 互動的工具）。
*   **動態工具可用性**：使代理程式能夠根據當前上下文（例如：用戶權限、會話狀態或其他運行時條件）提供不同的工具。工具集的 `get_tools` 方法可以決定公開哪些工具。
*   **整合外部工具提供者**：工具集可以充當來自外部系統（如 OpenAPI 規範或 MCP 伺服器）的工具的適配器，將它們轉換為 ADK 相容的 `BaseTool` 物件。

### `BaseToolset` 介面

ADK 中任何充當工具集的類別都應實現 `BaseToolset` 抽象基底類別。此介面主要定義了兩個方法：

*   **`async def get_tools(...) -> list[BaseTool]:`**
    這是工具集的核心方法。當 ADK 代理程式需要知道其可用工具時，它將呼叫其 `tools` 列表中每個 `BaseToolset` 實例的 `get_tools()`。
    *   它接收一個可選的 `readonly_context`（`ReadonlyContext` 的實例）。此上下文提供對當前會話狀態 (`readonly_context.state`)、代理程式名稱和調用 ID 等資訊的唯讀訪問。工具集可以使用此上下文來動態決定返回哪些工具。
    *   它 **必須** 返回一個 `BaseTool` 實例列表（例如：`FunctionTool`、`RestApiTool`）。

*   **`async def close(self) -> None:`**
    此非同步方法由 ADK 框架在不再需要工具集時呼叫，例如，當代理程式伺服器正在關閉或 `Runner` 正在關閉時。實現此方法以執行任何必要的清理工作，例如關閉網路連接、釋放文件句柄或清理工具集管理的其它資源。

### 在代理程式中使用工具集

您可以將 `BaseToolset` 實現的實例直接包含在 `LlmAgent` 的 `tools` 列表中，與單個 `BaseTool` 實例並列。

當代理程式初始化或需要確定其可用能力時，ADK 框架將遍歷 `tools` 列表：

*   如果一項是 `BaseTool` 實例，則直接使用。
*   如果一項是 `BaseToolset` 實例，則呼叫其 `get_tools()` 方法（使用當前的 `ReadonlyContext`），並將返回的 `BaseTool` 列表添加到代理程式的可調用工具中。

### 範例：簡單的數學工具集

讓我們創建一個提供簡單算術運算的工具集基礎範例。

<details>
<summary>範例說明</summary>

> Python

```py
# Python 簡單數學工具集範例
# 重點說明：展示如何建立自定義工具集 (Toolset) 並與單獨工具一起使用

# 1. 定義個別工具函數
# 重點說明：建立可被 FunctionTool 包裝的基礎函數
def add_numbers(a: int, b: int, tool_context: ToolContext) -> Dict[str, Any]:
    """將兩個整數相加。

    Args:
        a: 第一個數字。
        b: 第二個數字。
    Returns:
        包含總和的字典，例如：{'status': 'success', 'result': 5}
    """
    print(f"工具：add_numbers 被呼叫，參數 a={a}, b={b}")
    result = a + b
    # 重點說明：展示如何在 tool_context 狀態中儲存資訊
    tool_context.state["last_math_operation"] = "addition"
    return {"status": "success", "result": result}


def subtract_numbers(a: int, b: int) -> Dict[str, Any]:
    """從第一個數字減去第二個數字。

    Args:
        a: 第一個數字。
        b: 第二個數字。
    Returns:
        包含差值的字典，例如：{'status': 'success', 'result': 1}
    """
    print(f"工具：subtract_numbers 被呼叫，參數 a={a}, b={b}")
    return {"status": "success", "result": a - b}


# 2. 透過實作 BaseToolset 建立工具集
# 重點說明：BaseToolset 允許將多個工具組織在一起並動態提供
class SimpleMathToolset(BaseToolset):
    def __init__(self, prefix: str = "math_"):
        self.prefix = prefix
        # 重點說明：在初始化時建立 FunctionTool 實例
        self._add_tool = FunctionTool(
            func=add_numbers,
            name=f"{self.prefix}add_numbers",  # 工具集可以自訂工具名稱
        )
        self._subtract_tool = FunctionTool(
            func=subtract_numbers, name=f"{self.prefix}subtract_numbers"
        )
        print(f"SimpleMathToolset 已初始化，前綴為 '{self.prefix}'")

    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        # 重點說明：get_tools() 是工具集的核心方法，決定要提供哪些工具
        print(f"SimpleMathToolset.get_tools() 被呼叫。")
        # 動態行為範例：
        # 可以使用 readonly_context.state 來決定要返回哪些工具
        # 例如，如果 readonly_context.state.get("enable_advanced_math"):
        #    return [self._add_tool, self._subtract_tool, self._multiply_tool]

        # 在這個簡單範例中，總是返回兩個工具
        tools_to_return = [self._add_tool, self._subtract_tool]
        print(f"SimpleMathToolset 提供工具：{[t.name for t in tools_to_return]}")
        return tools_to_return

    async def close(self) -> None:
        # 重點說明：close() 方法用於清理資源
        # 在這個簡單範例中沒有資源需要清理
        print(f"SimpleMathToolset.close() 被呼叫，前綴為 '{self.prefix}'。")
        await asyncio.sleep(0)  # 如有需要，可用於非同步清理的佔位符


# 3. 定義單獨工具（不屬於工具集的一部分）
# 重點說明：展示單獨工具與工具集可以並存使用
def greet_user(name: str = "User") -> Dict[str, str]:
    """向使用者打招呼。"""
    print(f"工具：greet_user 被呼叫，參數 name={name}")
    return {"greeting": f"你好，{name}！"}


# 重點說明：將函數包裝為 FunctionTool
greet_tool = FunctionTool(func=greet_user)

# 4. 實例化工具集
# 重點說明：建立工具集實例，並使用自訂前綴
math_toolset_instance = SimpleMathToolset(prefix="calculator_")

# 5. 定義同時使用單獨工具和工具集的代理程式
# 重點說明：tools 參數可以混合使用單獨工具和工具集實例
calculator_agent = LlmAgent(
    name="CalculatorAgent",
    model="gemini-2.0-flash",  # 替換為您想要的模型
    instruction="你是一個有幫助的計算機和問候者。"
    "使用 'greet_user' 進行問候。"
    "使用 'calculator_add_numbers' 進行加法，使用 'calculator_subtract_numbers' 進行減法。"
    "如果設定了 'last_math_operation' 狀態，請宣告它。",
    tools=[greet_tool, math_toolset_instance],  # 單獨工具  # 工具集實例
)
```

> TypeScript

```typescript
// TypeScript 簡單數學工具集範例
// 重點說明：展示如何建立自定義工具集 (Toolset) 並與單獨工具一起使用
import { LlmAgent, FunctionTool, ToolContext, BaseToolset, InMemoryRunner, isFinalResponse, BaseTool, stringifyContent } from "@google/adk";
import { z } from "zod";
import { Content, createUserContent } from "@google/genai";

// 重點說明：定義加法函數，展示 ToolContext 的使用
function addNumbers(params: { a: number; b: number }, toolContext?: ToolContext): Record<string, any> {
  if (!toolContext) {
    throw new Error("此工具需要 ToolContext。");
  }
  const result = params.a + params.b;
  // 重點說明：在會話狀態中儲存計算結果
  toolContext.state.set("last_math_result", result);
  return { result: result };
}

// 重點說明：定義減法函數
function subtractNumbers(params: { a: number; b: number }): Record<string, any> {
  return { result: params.a - params.b };
}

// 重點說明：定義問候函數
function greetUser(params: { name: string }): Record<string, any> {
  return { greeting: `你好，${params.name}！` };
}

// 重點說明：繼承 BaseToolset 建立自定義工具集
class SimpleMathToolset extends BaseToolset {
  private readonly tools: BaseTool[];

  constructor(prefix = "") {
    super([]); // 無過濾器
    // 重點說明：在建構函數中初始化工具陣列
    this.tools = [
      new FunctionTool({
        name: `${prefix}add_numbers`,
        description: "將兩個數字相加並將結果儲存在會話狀態中。",
        parameters: z.object({ a: z.number(), b: z.number() }),
        execute: addNumbers,
      }),
      new FunctionTool({
        name: `${prefix}subtract_numbers`,
        description: "從第一個數字減去第二個數字。",
        parameters: z.object({ a: z.number(), b: z.number() }),
        execute: subtractNumbers,
      }),
    ];
  }

  // 重點說明：實作 getTools() 方法返回工具列表
  async getTools(): Promise<BaseTool[]> {
    return this.tools;
  }

  // 重點說明：實作 close() 方法進行資源清理
  async close(): Promise<void> {
    console.log("SimpleMathToolset 已關閉。");
  }
}

async function main() {
  // 重點說明：實例化數學工具集，使用自訂前綴
  const mathToolset = new SimpleMathToolset("calculator_");

  // 重點說明：建立單獨的問候工具
  const greetTool = new FunctionTool({
    name: "greet_user",
    description: "向使用者打招呼。",
    parameters: z.object({ name: z.string() }),
    execute: greetUser,
  });

  // 重點說明：定義代理程式的指令
  const instruction =
    `你是一個計算機和問候者。
    如果使用者要求數學運算，使用計算機工具。
    如果使用者要求問候，使用 greet_user 工具。
    最後一次數學運算的結果儲存在 'last_math_result' 狀態變數中。`;

  // 重點說明：建立 LlmAgent，混合使用單獨工具和工具集
  const calculatorAgent = new LlmAgent({
    name: "calculator_agent",
    instruction: instruction,
    tools: [greetTool, mathToolset],
    model: "gemini-2.5-flash",
  });

  // 重點說明：建立 InMemoryRunner 並初始化會話
  const runner = new InMemoryRunner({ agent: calculatorAgent, appName: "toolset_app" });
  await runner.sessionService.createSession({ appName: "toolset_app", userId: "user1", sessionId: "session1" });

  // 重點說明：建立使用者訊息
  const message: Content = createUserContent("5 加 3 等於多少？");

  // 重點說明：執行代理程式並處理回應
  for await (const event of runner.runAsync({ userId: "user1", sessionId: "session1", newMessage: message })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      const text = stringifyContent(event).trim();
      if (text) {
        console.log(`代理程式回應：${text}`);
      }
    }
  }

  // 重點說明：關閉工具集以釋放資源
  await mathToolset.close();
}

main();
```

</details>

在此範例中：

*   `SimpleMathToolset` 實現了 `BaseToolset`，其 `get_tools()` 方法返回 `add_numbers` 和 `subtract_numbers` 的 `FunctionTool` 實例。它還使用前綴自定義了它們的名稱。
*   `calculator_agent` 同時配置了單個 `greet_tool` 和 `SimpleMathToolset` 的實例。
*   當 `calculator_agent` 運行時，ADK 將呼叫 `math_toolset_instance.get_tools()`。代理程式的 LLM 隨後將能夠訪問 `greet_user`、`calculator_add_numbers` 和 `calculator_subtract_numbers` 來處理用戶請求。
*   `add_numbers` 工具演示了寫入 `tool_context.state`，且代理程式的指令中提到了讀取此狀態。
*   呼叫 `close()` 方法以確保釋放工具集持有的任何資源。

工具集提供了一種強大的方式來組織、管理並動態地向您的 ADK 代理程式提供工具集合，從而實現更具模組化、可維護性且適應性強的代理程式應用。
