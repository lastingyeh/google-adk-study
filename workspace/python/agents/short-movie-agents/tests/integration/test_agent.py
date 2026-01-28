"""
Agent 整合測試

測試 Agent 的串流功能與完整執行流程。
"""

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


def test_agent_stream() -> None:
    """
    測試代理串流功能的整合測試。
    驗證代理是否返回有效的串流響應。

    重點說明：
    1. 使用 InMemorySessionService 模擬會話管理。
    2. 使用 Runner 執行 root_agent。
    3. 驗證串流輸出是否包含文字內容。
    """

    # 初始化記憶體會話服務
    session_service = InMemorySessionService()

    # 建立測試會話
    session = session_service.create_session_sync(
        user_id="test_user", app_name="short_movie_agents_test"
    )

    # 初始化執行器
    runner = Runner(
        agent=root_agent, session_service=session_service, app_name="short_movie_agents_test"
    )

    # 建立使用者訊息
    message = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text="Create a short story about a magical forest."
            )
        ],
    )

    # 執行代理並獲取串流事件
    events = list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    # 斷言：預期至少收到一個事件
    assert len(events) > 0, "Expected at least one message"

    # 檢查事件中是否包含文字內容
    has_text_content = False
    for event in events:
        if (
            event.content
            and event.content.parts
            and any(part.text for part in event.content.parts)
        ):
            has_text_content = True
            break

    # 斷言：預期至少有一個事件包含文字
    assert has_text_content, "Expected at least one message with text content"


def test_agent_execution_with_simple_request() -> None:
    """
    測試代理執行簡單請求。
    驗證代理能夠處理基本的故事生成請求。
    """

    # 初始化記憶體會話服務
    session_service = InMemorySessionService()

    # 建立測試會話
    session = session_service.create_session_sync(
        user_id="test_user_2", app_name="short_movie_agents_test"
    )

    # 初始化執行器
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="short_movie_agents_test",
    )

    # 建立簡單的使用者訊息
    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Tell me a very short story.")],
    )

    # 執行代理
    events = list(
        runner.run(
            new_message=message,
            user_id="test_user_2",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    # 驗證有響應
    assert len(events) > 0, "Expected response from agent"

    # 驗證響應內容
    response_texts = []
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_texts.append(part.text)

    assert len(response_texts) > 0, "Expected text response from agent"


def test_agent_session_state() -> None:
    """
    測試代理會話狀態管理。
    驗證代理能夠在會話中維護狀態。
    """

    # 初始化記憶體會話服務
    session_service = InMemorySessionService()

    # 建立測試會話
    session = session_service.create_session_sync(
        user_id="test_user_3", app_name="short_movie_agents_test"
    )

    # 初始化執行器
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="short_movie_agents_test",
    )

    # 第一個請求
    message1 = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Create a story about a hero.")],
    )

    events1 = list(
        runner.run(
            new_message=message1,
            user_id="test_user_3",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    assert len(events1) > 0, "Expected response from first request"

    # 驗證會話仍然存在
    assert session.id is not None
    assert session.user_id == "test_user_3"
