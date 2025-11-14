"""
基本串流展示 - 教學 14

展示使用 ADK 的真實串流 API 的基本串流實作。
"""

import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 環境設定
# 設定預設值，指示 ADK 不使用 Vertex AI
os.environ.setdefault('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE')


async def stream_response(query: str):
    """
    使用真實 ADK API 串流 agent 回應。

    Args:
        query: 要處理的使用者查詢
    """
    # 建立 agent
    agent = Agent(
        model='gemini-2.0-flash',
        name='streaming_assistant',
        instruction='提供詳細、有幫助的回應。'
    )

    # 設定串流
    run_config = RunConfig(
        streaming_mode=StreamingMode.SSE
    )

    # 建立會話服務和 runner
    session_service = InMemorySessionService()
    runner = Runner(app_name="streaming_demo", agent=agent, session_service=session_service)

    # 建立會話
    session = await session_service.create_session(
        app_name="streaming_demo",
        user_id="demo_user"
    )

    print(f"使用者: {query}\n")
    print("Agent: ", end='', flush=True)

    # 執行串流
    async for event in runner.run_async(
        user_id="demo_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)]),
        run_config=run_config
    ):
        # 當每個字塊到達時印出
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end='', flush=True)

        # 檢查是否完成
        if event.turn_complete:
            break

    print("\n")


async def main():
    """執行基本串流展示。"""
    print("=" * 60)
    print("基本串流展示 - 教學 14")
    print("=" * 60)

    # 展示查詢
    queries = [
        "解釋神經網路如何運作",
        "串流回應有什麼好處？",
        "Server-Sent Events 如何運作？"
    ]

    for query in queries:
        await stream_response(query)
        await asyncio.sleep(0.5)  # 查詢之間短暫暫停

    print("=" * 60)
    print("展示完成！")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
