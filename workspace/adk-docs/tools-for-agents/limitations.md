# ADK 工具限制

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源：https://google.github.io/adk-docs/tools/limitations/`

某些 ADK 工具具有一些限制，可能會影響您在代理程式 (agent) 工作流程中實作它們的方式。本頁列出了這些工具限制以及可用的解決方案（若有）。

## 每個代理程式僅限一個工具限制

一般來說，您可以在代理程式中使用多個工具，但在代理程式中使用特定工具時，會排除在該代理程式中使用任何其他工具。以下 ADK 工具在單個代理程式物件中只能單獨使用，不能與任何其他工具共用：

*   使用 Gemini API 的 [程式碼執行 (Code Execution)](./gemini-api/code-execution.md)
*   使用 Gemini API 的 [Google 搜尋 (Google Search)](./gemini-api/google-search.md)
*   [Vertex AI 搜尋 (Vertex AI Search)](https://google.github.io/adk-docs/tools/google-cloud/vertex-ai-search/)

例如，以下在單個代理程式中將這些工具之一與其他工具結合使用的方法是 ***不支援*** 的：

<details>
<summary>範例說明</summary>

> Python

```py
# 建立一個 Agent
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    description="Code Agent",
    tools=[custom_function],
    # 當與其他 tools 一起使用時，不支援內建程式碼執行器
    code_executor=BuiltInCodeExecutor() # <-- 不支援
)
```

> Java

```java
// 建立搜尋代理程式
 LlmAgent searchAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("SearchAgent")
            .instruction("You're a specialist in Google Search")
            // 不支援同時使用 GoogleSearchTool 和自定義工具
            .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- 不支援
            .build();
```

</details>

### 解決方案 #1：AgentTool.create() 方法

[`ADK 支援`: `Python` | `Java`]

以下程式碼範例示範了如何透過使用多個代理程式來使用多個內建工具，或將內建工具與其他工具結合使用：

<details>
<summary>範例說明</summary>

> Python

```py
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor

# 定義搜尋代理程式
search_agent = Agent(
    model='gemini-2.0-flash',
    name='SearchAgent',
    instruction="""
    你是使用 Google Search 的專家
    """,
    tools=[google_search],
)
# 定義程式碼執行代理程式
coding_agent = Agent(
    model='gemini-2.0-flash',
    name='CodeAgent',
    instruction="""
    你是 Code Execution 的專家
    """,
    code_executor=BuiltInCodeExecutor(),
)
# 定義根代理程式，將其他代理程式封裝為工具
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    tools=[AgentTool(agent=search_agent), AgentTool(agent=coding_agent)],
)
```

> Java

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

    // 定義搜尋代理程式 (SearchAgent)
    LlmAgent searchAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("SearchAgent")
            .instruction("你是使用 Google Search 的專家")
            .tools(new GoogleSearchTool()) // 實體化 GoogleSearchTool
            .build();


    // 定義程式碼代理程式 (CodingAgent)
    LlmAgent codingAgent =
        LlmAgent.builder()
            .model(MODEL_ID)
            .name("CodeAgent")
            .instruction("You're a specialist in Code Execution")
            .tools(new BuiltInCodeExecutionTool()) // 實體化 BuiltInCodeExecutionTool
            .build();

    // 定義根代理程式 (RootAgent)，使用 AgentTool.create() 封裝 SearchAgent 和 CodingAgent
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

    // 注意：此範例僅示範代理程式定義。
    // 要執行這些代理程式，您需要將它們與 Runner 和 SessionService 整合，
    // 類似於之前的範例。
    System.out.println("Agents defined successfully:");
    System.out.println("  Root Agent: " + rootAgent.name());
    System.out.println("  Search Agent (nested): " + searchAgent.name());
    System.out.println("  Code Agent (nested): " + codingAgent.name());
  }
}
```

</details>

### 解決方案 #2：bypass_multi_tools_limit

[`ADK 支援`: `Python` | `Java`]

ADK Python 有一個內建的解決方案，可以繞過 `GoogleSearchTool` 和 `VertexAiSearchTool` 的此限制（使用 `bypass_multi_tools_limit=True` 來啟用它），如 [built_in_multi_tools](https://github.com/google/adk-python/tree/main/contributing/samples/built_in_multi_tools) 範例代理程式所示。

> [!WARNING] 警告
內建工具不能在子代理程式 (sub-agent) 中使用，但在 ADK Python 中的 `GoogleSearchTool` 和 `VertexAiSearchTool` 除外，因為有上述提到的解決方案。

例如，以下在子代理程式中使用內建工具的方法是 **不支援** 的：

<details>
<summary>範例說明</summary>

> Python

```py
# 定義 URL 上下文代理程式
url_context_agent = Agent(
    model='gemini-2.5-flash',
    name='UrlContextAgent',
    instruction="""
    You're a specialist in URL Context
    """,
    tools=[url_context],
)
# 定義程式碼代理程式
coding_agent = Agent(
    model='gemini-2.5-flash',
    name='CodeAgent',
    instruction="""
    你是 Code Execution 的專家
    """,
    code_executor=BuiltInCodeExecutor(),
)
# 定義根代理程式
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    description="Root Agent",
    # 在子代理程式中使用內建工具是不支援的
    sub_agents=[
        url_context_agent,
        coding_agent
    ],
)
```

> Java

```java
// 定義搜尋代理程式
LlmAgent searchAgent =
    LlmAgent.builder()
        .model("gemini-2.5-flash")
        .name("SearchAgent")
        .instruction("你是使用 Google Search 的專家")
        .tools(new GoogleSearchTool())
        .build();

// 定義程式碼代理程式
LlmAgent codingAgent =
    LlmAgent.builder()
        .model("gemini-2.5-flash")
        .name("CodeAgent")
        .instruction("你是 Code Execution 的專家")
        .tools(new BuiltInCodeExecutionTool())
        .build();


// 定義根代理程式
LlmAgent rootAgent =
    LlmAgent.builder()
        .name("RootAgent")
        .model("gemini-2.5-flash")
        .description("Root Agent")
        // 不支援，因為子代理程式使用了內建工具
        .subAgents(searchAgent, codingAgent)
        .build();
```

</details>

## 更多說明

### Q & A

### 說明：sub_agents 與 AgentTool（封裝於 tools）之差異

概述
在 google/adk-python 中，sub_agents 與 AgentTool 都能讓代理協作，但用途與耦合方式不同：sub_agents 建立父子內部結構並由父代理直接協調；AgentTool 將代理抽象為可呼叫的工具，透過工具介面解耦與重用。

| 項目 | sub_agents（子代理） | AgentTool（封裝於 tools） |
|---|---|---|
| 定義位置 | Agent 的 `sub_agents` 屬性（google/adk-python/src/google/adk/agents/base_agent.py） | `AgentTool` 類別（google/adk-python/src/google/adk/tools/agent_tool.py） |
| 角色與關係 | 建立父子（內部）關係，子代理成為父代理架構一部分 | 將代理包裝成標準工具介面，作為可呼叫的外部工具 |
| 執行控制 | 由父代理直接協調執行（可序列或並行，如 SequentialAgent/ParallelAgent） | 由呼叫者（通常是 LLM）決定是否及何時呼叫 |
| 上下文與隔離 | 在隔離上下文中運行，但可透過父代理的 InvocationContext 共享狀態或服務 | 以工具介面運作，與呼叫方解耦，透過明確的介面交換資料 |
| 配置方式 | 在 Agent 實例的 `sub_agents` 列表或 YAML/config 中引用（範例：samples/a2a_basic/agent.py） | 在 Agent 的 `tools` 屬性加入 `AgentTool(agent=...)` 或 `AgentTool.create(...)`（範例：adk_answering_agent、mcp_in_agent_tool_*） |
| 適用情境 | 需緊密整合、層次化任務分工或由父代理統一管理的工作流 | 將代理作為可重用功能性服務，降低耦合並允許按需呼叫 |
| 耦合性 | 緊密耦合（父子內部結構） | 鬆散耦合、抽象化（工具介面） |
| 重用性 | 偏向特定父代理，不易跨多代理重用 | 高重用性，可被多個代理重複使用 |
| 注意事項 | 內建工具通常不支援在子代理中使用（見 bypass_multi_tools_limit 節） | 可保留隔離與安全邊界，使用時檢視 InvocationContext 與工具權限 |
