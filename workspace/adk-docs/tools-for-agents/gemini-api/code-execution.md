# 使用 Gemini API 執行程式碼

> 🔔 `更新日期：2026-01-23`
>
> 🔗 `資料來源`：https://google.github.io/adk-docs/tools/gemini-api/code-execution/

[`ADK 支援`: `Python v0.1.0` | `Java v0.2.0`]

`built_in_code_execution` 工具可讓代理程式執行程式碼，特別是在使用 Gemini 2 及更高版本的模型時。這使得模型能夠執行諸如計算、數據處理或執行小型腳本等任務。

> [!WARNING] 警告：每個代理程式僅限單一工具
此工具在代理程式實例中只能***單獨使用***。
如需更多關於此限制及解決辦法的資訊，請參閱
[ADK 工具的限制](../limitations.md#adk-工具限制)。

<details>
<summary>範例說明</summary>

> Python

```py
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor
from google.genai import types

AGENT_NAME = "calculator_agent"
APP_NAME = "calculator"
USER_ID = "user1234"
SESSION_ID = "session_code_exec_async"
GEMINI_MODEL = "gemini-2.0-flash"

# 代理定義
code_agent = LlmAgent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    code_executor=BuiltInCodeExecutor(),
    instruction="""你是計算器代理。
    當收到數學表達式時，撰寫並執行 Python 程式碼以計算結果。
    僅以純文字回傳最終數值結果，不要包含 Markdown 或程式碼區塊。
    """,
    description="執行 Python 程式碼以進行計算。",
)

# 會話與 Runner
session_service = InMemorySessionService()
session = asyncio.run(session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
))
runner = Runner(agent=code_agent, app_name=APP_NAME,
                session_service=session_service)

# 代理互動（非同步）
async def call_agent_async(query):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(f"\n--- 執行查詢：{query} ---")
    final_response_text = "未擷取到最終文字回應。"
    try:
        # 使用 run_async
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            print(f"事件 ID: {event.id}, 作者: {event.author}")

            # --- 優先檢查特定部分 ---
            has_specific_part = False
            if event.content and event.content.parts:
                for part in event.content.parts:  # 逐一檢視所有部分
                    if part.executable_code:
                        # 透過 .code 存取實際程式碼字串
                        print(f"偵錯：代理產生的程式碼：\n```python\n{part.executable_code.code}\n```")
                        has_specific_part = True
                    elif part.code_execution_result:
                        # 正確存取結果與輸出
                        print(f"偵錯：程式碼執行結果：{part.code_execution_result.outcome} - 輸出：\n{part.code_execution_result.output}")
                        has_specific_part = True
                    # 也列印任何文字部分以供偵錯
                    elif part.text and not part.text.isspace():
                        print(f"  文字：'{part.text.strip()}'")
                        # 此處不設 has_specific_part=True，以便下方的最終回應邏輯運作

            # --- 在特定部分處理後檢查最終回應 ---
            # 只有在沒有上述特定程式碼部分時才視為最終回應
            if not has_specific_part and event.is_final_response():
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    final_response_text = event.content.parts[0].text.strip()
                    print(f"==> 代理最終回應：{final_response_text}")
                else:
                    print("==> 代理最終回應：[最終事件無文字內容]")

    except Exception as e:
        print(f"執行代理時出錯：{e}")
    print("-" * 30)


# 執行範例的主非同步函式
async def main():
    await call_agent_async("計算 (5 + 7) * 3 的值")
    await call_agent_async("10 的階乘是多少？")

# 執行主非同步函式
try:
    asyncio.run(main())
except RuntimeError as e:
    # 處理在已存在的事件迴圈中呼叫 asyncio.run 的特定錯誤（例如 Jupyter/Colab）
    if "cannot be called from a running event loop" in str(e):
        print("\n偵測到正在執行的 event loop（例如 Colab/Jupyter）。")
        print("請在 notebook 格式中執行 `await main()`。")
        # 若在互動式環境（如 notebook），可改用：
        # await main()
    else:
        raise e  # 重新拋出其他 RuntimeError
```

> Java

```java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.BuiltInCodeExecutionTool;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Content;
import com.google.genai.types.Part;

public class CodeExecutionAgentApp {

  private static final String AGENT_NAME = "calculator_agent";
  private static final String APP_NAME = "calculator";
  private static final String USER_ID = "user1234";
  private static final String SESSION_ID = "session_code_exec_sync";
  private static final String GEMINI_MODEL = "gemini-2.0-flash";

  /**
   * 以查詢呼叫代理並列印互動事件與最終回應。
   *
   * @param runner 執行代理的 runner 實例。
   * @param query 要傳送給代理的查詢。
   */
  public static void callAgent(Runner runner, String query) {
    Content content =
        Content.builder().role("user").parts(ImmutableList.of(Part.fromText(query))).build();

    InMemorySessionService sessionService = (InMemorySessionService) runner.sessionService();
    Session session =
        sessionService
            .createSession(APP_NAME, USER_ID, /* state= */ null, SESSION_ID)
            .blockingGet();

    System.out.println("\n--- 執行查詢： " + query + " ---");
    final String[] finalResponseText = {"未擷取到最終文字回應。"};

    try {
      runner
          .runAsync(session.userId(), session.id(), content)
          .forEach(
              event -> {
                System.out.println("事件 ID: " + event.id() + ", 作者: " + event.author());

                boolean hasSpecificPart = false;
                if (event.content().isPresent() && event.content().get().parts().isPresent()) {
                  for (Part part : event.content().get().parts().get()) {
                    if (part.executableCode().isPresent()) {
                      System.out.println(
                          "偵錯：代理產生的程式碼：\n```python\n"
                              + part.executableCode().get().code()
                              + "\n```");
                      hasSpecificPart = true;
                    } else if (part.codeExecutionResult().isPresent()) {
                      System.out.println(
                          "偵錯：程式碼執行結果："
                              + part.codeExecutionResult().get().outcome()
                              + " - 輸出：\n"
                              + part.codeExecutionResult().get().output());
                      hasSpecificPart = true;
                    } else if (part.text().isPresent() && !part.text().get().trim().isEmpty()) {
                      System.out.println("  文字：'" + part.text().get().trim() + "'");
                    }
                  }
                }

                if (!hasSpecificPart && event.finalResponse()) {
                  if (event.content().isPresent()
                      && event.content().get().parts().isPresent()
                      && !event.content().get().parts().get().isEmpty()
                      && event.content().get().parts().get().get(0).text().isPresent()) {
                    finalResponseText[0] =
                        event.content().get().parts().get().get(0).text().get().trim();
                    System.out.println("==> 代理最終回應： " + finalResponseText[0]);
                  } else {
                    System.out.println(
                        "==> 代理最終回應：[最終事件無文字內容]");
                  }
                }
              });
    } catch (Exception e) {
      System.err.println("執行代理時發生錯誤： " + e.getMessage());
      e.printStackTrace();
    }
    System.out.println("------------------------------");
  }

  public static void main(String[] args) {
    BuiltInCodeExecutionTool codeExecutionTool = new BuiltInCodeExecutionTool();

    BaseAgent codeAgent =
        LlmAgent.builder()
            .name(AGENT_NAME)
            .model(GEMINI_MODEL)
            .tools(ImmutableList.of(codeExecutionTool))
            .instruction("""
                你是計算器代理。
                當收到數學表達式時，撰寫並執行 Python 程式碼以計算結果。
                僅以純文字回傳最終數值結果，不要包含 Markdown 或程式碼區塊。""")
            .description("執行 Python 程式碼以進行計算。")
            .build();

    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(codeAgent, APP_NAME, null, sessionService);

    callAgent(runner, "計算 (5 + 7) * 3 的值");
    callAgent(runner, "10 的階乘是多少？");
  }
}
```

</details>
