"""測試多輪對話記憶功能（使用 Google ADK）"""
import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from backend.agents.conversation_agent import create_conversation_agent


@pytest.mark.asyncio
async def test_multi_turn_conversation():
    """測試 Agent 是否能記住對話上下文"""
    # 設置 ADK 元件
    agent = create_conversation_agent()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="test_app",
        session_service=session_service
    )
    
    # 建立會話
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    # 第一輪對話：告訴 Agent 名字
    print("\n=== 第一輪對話 ===")
    msg1 = types.Content(
        role="user",
        parts=[types.Part(text="我叫 Alice")]
    )
    
    response1_parts = []
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=msg1
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response1_parts.append(part.text)
    
    response1 = "".join(response1_parts)
    print(f"Round 1 Response: {response1}")
    
    # 第二輪對話：測試 Agent 是否記得
    print("\n=== 第二輪對話（測試記憶）===")
    msg2 = types.Content(
        role="user",
        parts=[types.Part(text="我剛才說我叫什麼名字？")]
    )
    
    response2_parts = []
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=msg2
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response2_parts.append(part.text)
    
    response2 = "".join(response2_parts)
    print(f"Round 2 Response: {response2}")
    
    # 驗證：Agent 應該記得名字
    assert "Alice" in response2, "Agent 應該記住使用者的名字"
    print("\n✅ 多輪對話記憶測試通過！")
    print("✅ ADK SessionService 正確管理對話狀態")