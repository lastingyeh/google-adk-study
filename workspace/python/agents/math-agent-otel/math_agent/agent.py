"""
具有 OpenTelemetry 儀表化的 ADK 數學代理。
展示使用 Jaeger 後端的分散式追蹤與結構化日誌。

主要功能：
- 自動擷取所有代理調用的追蹤 (trace capture)
- 與追蹤相關聯的結構化日誌
- 工具執行追蹤
- LLM 請求/回應記錄

**OTel 如何設定**：
- 對於 `adk web`：設定 OTEL 環境變數，ADK 處理其餘部分
- 對於獨立示範：我們明確呼叫 initialize_otel_env() 以求清晰
"""

import asyncio
import logging
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from math_agent.tools import add_numbers, subtract_numbers, multiply_numbers, divide_numbers

# 首先初始化 OpenTelemetry (在任何 ADK 匯入之前)
#
# 對於 adk web：使用 initialize_otel_env() 設定環境變數 (ADK 處理設定)
# 對於 demo：使用 initialize_otel() 手動設定 TracerProvider
#
# 我們透過檢查 __name__ == "__main__" (demo) 或不是 (adk web) 來偵測情境
from math_agent.otel_config import initialize_otel_env, initialize_otel, force_flush

# 當以 "python -m math_agent.agent" 執行時，__name__ 將是 "__main__"
# 當由 adk web 匯入時，__name__ 將是 "math_agent.agent"
# 我們在此模組完全載入後偵測這一點
def _init_otel():
    """使用適當的方法初始化 OTel。"""
    # 檢查我們是作為主程式執行 (demo) 還是作為匯入模組執行 (adk web)
    is_demo = __name__ == "__main__"

    if is_demo:
        # 對於 demo：手動初始化 TracerProvider 以匯出追蹤
        initialize_otel(
            service_name="google-adk-math-agent",
            service_version="0.1.0",
            jaeger_endpoint="http://localhost:4318/v1/traces",
        )
    else:
        # 對於 adk web：僅設定環境變數，ADK 將處理其餘部分
        initialize_otel_env(
            service_name="google-adk-math-agent",
            service_version="0.1.0",
            jaeger_endpoint="http://localhost:4318/v1/traces",
        )

# 呼叫初始化
_init_otel()

# 在 OTel 初始化後取得 logger
logger = logging.getLogger("math_agent")
logger.info("OpenTelemetry 已透過環境變數設定")


# 建立工具 (描述來自函式 docstrings)
add_tool = FunctionTool(func=add_numbers)
subtract_tool = FunctionTool(func=subtract_numbers)
multiply_tool = FunctionTool(func=multiply_numbers)
divide_tool = FunctionTool(func=divide_numbers)

logger.info("已建立 4 個數學工具：加、減、乘、除")

# 建立 root agent
root_agent = Agent(
    name="math_assistant",
    model="gemini-2.5-flash",
    description="一個有用的數學助理，可以執行基本的算術運算。",
    instruction="""你是一個有用的數學助理。你可以對數字進行加、減、乘和除。
    當被要求執行數學運算時，請使用適當的工具。
    務必展示你的計算過程並清楚解釋答案。
    如果使用者要求除以零，請禮貌地解釋這是不可能的。""",
    tools=[add_tool, subtract_tool, multiply_tool, divide_tool],
)

logger.info("已建立使用 gemini-2.5-flash 模型的 math_assistant 代理")


async def run_agent(query: str) -> str:
    """
    使用給定的查詢執行代理並傳回回應。

    使用 InMemoryRunner 來管理調用。每次調用會自動
    建立一個包含以下內容的追蹤：
    - 代理調用詳細資訊
    - 工具執行 spans
    - LLM 請求/回應資料
    - 用於 gen_ai 的 OpenTelemetry 語意慣例

    ⚠️  對 adk web 至關重要：Spans 在執行後刷新，以確保
    它們在此函式傳回之前被發送到 Jaeger。

    參數:
        query: 使用者問題

    傳回:
        代理的回應文字
    """
    logger.info(f"正在執行代理，查詢為：{query}")
    try:
        # 為此調用建立 runner
        runner = InMemoryRunner(agent=root_agent, app_name="math-agent-demo")

        # 為此使用者建立 session
        session = await runner.session_service.create_session(
            user_id="demo_user",
            app_name="math-agent-demo"
        )

        # 準備使用者訊息
        user_message = Content(role="user", parts=[Part(text=query)])

        # 執行代理並收集回應
        response_text = ""

        async for event in runner.run_async(
            session_id=session.id,
            user_id="demo_user",
            new_message=user_message
        ):
            # 從回應事件中擷取文字
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text

        logger.info("代理回應成功")

        # ⚠️  至關重要：在傳回之前將 spans/logs 刷新到 Jaeger
        # 這對於 adk web 特別重要，因為我們處於一個會立即傳回的非同步
        # 處理常式中。沒有這個，追蹤可能無法在請求完成前到達 Jaeger。
        force_flush(timeout_millis=5000)

        return response_text if response_text else "無回應"
    except Exception as e:
        logger.error(f"代理調用失敗: {e}", exc_info=True)
        # 即使出錯也要嘗試刷新
        force_flush(timeout_millis=5000)
        raise


async def main():
    """示範的主要進入點。"""
    logger.info("開始數學代理示範")

    queries = [
        "What is 123 + 456?",
        "Calculate 1000 - 234",
        "Multiply 12 by 15",
        "What is 100 divided by 4?"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] 查詢: {query}")
        try:
            result = await run_agent(query)
            print(f"回應: {result}")
        except Exception as e:
            print(f"錯誤: {e}")

    logger.info("數學代理示範完成")

    # 給予時間讓最後的 spans 匯出
    await asyncio.sleep(1)

    # 最後刷新以確保所有資料到達 Jaeger
    force_flush(timeout_millis=5000)


if __name__ == "__main__":
    asyncio.run(main())
