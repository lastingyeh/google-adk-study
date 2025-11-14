"""
StreamingMode 設定展示 - 教學 14

展示不同的 StreamingMode 設定及其用法。
"""

import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 環境設定
os.environ.setdefault('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE')


async def demo_streaming_modes():
    """
    展示不同的串流模式設定。
    """
    print("=" * 70)
    print("串流模式設定展示")
    print("=" * 70)

    # 建立 agent
    agent = Agent(
        model='gemini-2.0-flash',
        name='config_demo_agent',
        instruction='為設定測試提供簡潔、有幫助的回應。'
    )

    # 建立會話服務和 runner
    session_service = InMemorySessionService()
    runner = Runner(app_name="config_demo", agent=agent, session_service=session_service)

    # 建立會話
    session = await session_service.create_session(
        app_name="config_demo",
        user_id="demo_user"
    )

    query = "用一句話解釋 SSE 和阻塞式回應的區別。"

    # 展示 1: SSE 串流
    print("\n1. SSE 串流模式:")
    print("-" * 30)

    sse_config = RunConfig(
        streaming_mode=StreamingMode.SSE
    )

    print("使用者: " + query)
    print("Agent (SSE): ", end='', flush=True)

    async for event in runner.run_async(
        user_id="demo_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)]),
        run_config=sse_config
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end='', flush=True)
        if event.turn_complete:
            break

    print("\n")

    # 展示 2: 無串流 (阻塞式)
    print("\n2. 阻塞模式 (無串流):")
    print("-" * 35)

    blocking_config = RunConfig(
        streaming_mode=StreamingMode.NONE
    )

    print("使用者: " + query)
    print("Agent (阻塞式): ", end='', flush=True)

    # 收集完整回應
    response_parts = []
    async for event in runner.run_async(
        user_id="demo_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)]),
        run_config=blocking_config
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_parts.append(part.text)
        if event.turn_complete:
            break

    # 一次性印出完整回應
    complete_response = ''.join(response_parts)
    print(complete_response)

    print("\n" + "=" * 70)
    print("可用的串流模式:")
    print("- StreamingMode.SSE: Server-Sent Events (單向串流)")
    print("- StreamingMode.BIDI: 雙向串流 (雙向，用於 Live API)")
    print("- StreamingMode.NONE: 無串流 (預設，阻塞式)")
    print("=" * 70)


async def main():
    """執行串流模式設定展示。"""
    await demo_streaming_modes()


if __name__ == '__main__':
    asyncio.run(main())
