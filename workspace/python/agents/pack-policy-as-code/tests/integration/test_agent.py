"""測試代理是否能處理簡單的查詢。"""

import pytest
from google.adk.artifacts import InMemoryArtifactService
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from policy_as_code_agent import agent


@pytest.fixture
def runner() -> Runner:
    return Runner(
        app_name="test",
        agent=agent.root_agent,
        session_service=InMemorySessionService(),
        artifact_service=InMemoryArtifactService(),
    )


@pytest.mark.asyncio
async def test_agent_responds_to_greeting(runner: Runner) -> None:
    """檢查代理是否能成功回應問候語。"""

    question = "hi"

    events = await invoke(question=question, runner=runner)
    assert events, "預期至少有一個事件"

    content = events[-1].content
    assert content, "預期至少有一個內容"

    text = "\n\n".join(part.text for part in content.parts or [] if part.text)
    assert text


async def invoke(question: str, runner: Runner) -> list[Event]:
    """調用代理並返回結果事件序列。"""

    # 準備使用者輸入
    user = "test-user"
    input_content = types.UserContent(question)

    # 建立工作階段
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id=user
    )

    # 執行代理
    event_aiter = runner.run_async(
        user_id=user, session_id=session.id, new_message=input_content
    )
    events = [event async for event in event_aiter]

    return events
