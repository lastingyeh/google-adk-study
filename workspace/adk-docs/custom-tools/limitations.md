# ADK 工具的限制

> 🔔 `更新日期：2026-03-09`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/limitations/

某些 ADK 工具具有限制，可能會影響您在代理工作流（agent workflow）中實作它們的方式。本頁列出了這些工具限制以及可用的解決方法（如果有的話）。

## 每個代理一個工具的限制

> [!NOTE]僅適用於 ADK Python v1.15.0 及更低版本中的搜尋功能
此限制僅適用於在 ADK Python v1.15.0 及更低版本中使用 Google Search 和 Vertex AI Search 工具。ADK Python v1.16.0 及更高版本提供了一個內建的解決方法來消除此限制。

通常情況下，您可以在一個代理中使用多個工具，但在代理中使用特定工具會排除在該代理中使用任何其他工具。以下 ADK 工具在單個代理對象中只能單獨使用，不能與任何其他工具一起使用：

- 搭配 Gemini API 的 [程式碼執行 (Code Execution)](../tools-and-integrations/integrations/code-execution.md)
- 搭配 Gemini API 的 [Google 搜尋 (Google Search)](../tools-and-integrations/integrations/google-search.md)
- [Vertex AI 搜尋 (Vertex AI Search)](../tools-and-integrations/integrations/vertex-ai-search.md)

例如，在單個代理中同時使用這些工具之一與其他工具的以下方法是 ***不支援的***：

<details>
<summary>範例說明</summary>

> Python

```py
# 在單個代理中同時使用自定義函數和內建程式碼執行器是不支援的
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    description="Code Agent",
    tools=[custom_function],
    code_executor=BuiltInCodeExecutor() # <-- 當與 tools 一起使用時不支援
)
```

> java

```java
 // 嘗試在單個代理中同時使用 GoogleSearchTool 和自定義工具是不支援的
 LlmAgent searchAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("SearchAgent")
            .instruction("You're a specialist in Google Search")
            .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- 不支援
            .build();
```

</details>

### 解決方法 #1：AgentTool.create() 方法

[`ADK 支援`: `Python` | `Java`]

以下程式碼範例示範了如何使用多個內建工具，或如何透過使用多個代理來將內建工具與其他工具一起使用：

<details>
<summary>範例說明</summary>

> Python

```py
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor

# 定義搜尋代理
search_agent = Agent(
    model='gemini-2.0-flash',
    name='SearchAgent',
    instruction="""
    You're a specialist in Google Search
    """,
    tools=[google_search],
)
# 定義程式碼執行代理
coding_agent = Agent(
    model='gemini-2.0-flash',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    code_executor=BuiltInCodeExecutor(),
)
# 定義根代理，將其他代理包裝為工具
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    tools=[AgentTool(agent=search_agent), AgentTool(agent=coding_agent)],
)
```

> java

```java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.AgentTool;
import com.google.adk.tools.BuiltInCodeExecutionTool;
import com.google.adk.tools.GoogleSearchTool;
import com.google.common.collect.ImmutableList;

public class NestedAgentApp {

  private static final String MODEL_ID = "gemini-2.0-flash";

  public static void main(String[] args) {

    // 定義搜尋代理 (SearchAgent)
    LlmAgent searchAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("SearchAgent")
            .instruction("You're a specialist in Google Search")
            .tools(new GoogleSearchTool()) // 實例化 GoogleSearchTool
            .build();


    // 定義程式碼代理 (CodingAgent)
    LlmAgent codingAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("CodeAgent")
            .instruction("You're a specialist in Code Execution")
            .tools(new BuiltInCodeExecutionTool()) // 實例化 BuiltInCodeExecutionTool
            .build();

    // 定義根代理 (RootAgent)，使用 AgentTool.create() 包裝 SearchAgent 和 CodingAgent
    BaseAgent rootAgent =
        LlmAgent.builder()
            .name("RootAgent")
            .model(MODEL_ID)
            .description("Root Agent")
            .tools(
                AgentTool.create(searchAgent), // 使用 create 方法
                AgentTool.create(codingAgent)   // 使用 create 方法
             )
            .build();

    // 注意：此範例僅示範代理定義。
    // 要運行這些代理，您需要將它們與 Runner 和 SessionService 整合，
    // 類似於之前的範例。
    System.out.println("Agents defined successfully:");
    System.out.println("  Root Agent: " + rootAgent.name());
    System.out.println("  Search Agent (nested): " + searchAgent.name());
    System.out.println("  Code Agent (nested): " + codingAgent.name());
  }
}
```

</details>

### 解決方法 #2：bypass_multi_tools_limit

[`ADK 支援`: `Python` | `Java`]

ADK Python 有一個內建的解決方法，可以繞過 `GoogleSearchTool` 和 `VertexAiSearchTool` 的此限制（使用 `bypass_multi_tools_limit=True` 來啟用它），如 [built_in_multi_tools](https://github.com/google/adk-python/tree/main/contributing/samples/built_in_multi_tools) 範例代理中所示。

> [!WARNING]警告
內建工具不能在子代理（sub-agent）中使用，但由於上述解決方法，ADK Python 中的 `GoogleSearchTool` 和 `VertexAiSearchTool` 除外。

例如，在子代理中使用內建工具的以下方法是 **不支援的**：

<details>
<summary>範例說明</summary>

> Python

```py
# 在子代理中使用內建工具（如 url_context）是不支援的
url_context_agent = Agent(
    model='gemini-2.5-flash',
    name='UrlContextAgent',
    instruction="""
    You're a specialist in URL Context
    """,
    tools=[url_context],
)
# 在子代理中使用內建程式碼執行器也是不支援的
coding_agent = Agent(
    model='gemini-2.5-flash',
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    code_executor=BuiltInCodeExecutor(),
)
# 定義根代理並嘗試使用包含內建工具的子代理
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    description="Root Agent",
    sub_agents=[
        url_context_agent,
        coding_agent
    ],
)
```

> java

```java
// 定義搜尋代理
LlmAgent searchAgent =
    LlmAgent.builder()
        .model("gemini-2.5-flash")
        .name("SearchAgent")
        .instruction("You're a specialist in Google Search")
        .tools(new GoogleSearchTool())
        .build();

// 定義程式碼代理
LlmAgent codingAgent =
    LlmAgent.builder()
        .model("gemini-2.5-flash")
        .name("CodeAgent")
        .instruction("You're a specialist in Code Execution")
        .tools(new BuiltInCodeExecutionTool())
        .build();


// 定義根代理，嘗試使用 subAgents 包含帶有內建工具的代理是不支援的
LlmAgent rootAgent =
    LlmAgent.builder()
        .name("RootAgent")
        .model("gemini-2.5-flash")
        .description("Root Agent")
        .subAgents(searchAgent, codingAgent) // 不支援，因為子代理使用了內建工具。
        .build();
```

</details>
