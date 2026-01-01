from unittest.mock import MagicMock, patch

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


@patch(
    "app.agent.retrieve_docs",
    return_value="dummy content",
)
def test_agent_stream(mock_retrieve: MagicMock) -> None:
    """
    代理串流功能的整合測試。
    測試代理是否傳回有效的串流回應。
    """

    # 初始化記憶體中的工作階段服務，用於測試環境不依賴外部資料庫
    session_service = InMemorySessionService()

    # 同步建立一個測試用的工作階段 (Session)
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    # 初始化執行器 (Runner)，連結代理 (Agent) 與工作階段服務
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    # 建立使用者訊息物件，模擬使用者輸入
    message = types.Content(
        role="user", parts=[types.Part.from_text(text="Why is the sky blue?")]
    )

    # 執行代理並獲取串流事件列表
    # 使用 SSE (Server-Sent Events) 模式進行串流
    events = list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    # 驗證是否收到至少一個事件
    assert len(events) > 0, "Expected at least one message"

    has_text_content = False
    # 檢查事件中是否包含文字內容
    for event in events:
        if (
            event.content
            and event.content.parts
            and any(part.text for part in event.content.parts)
        ):
            has_text_content = True
            break
    # 驗證是否至少有一個事件包含文字內容
    assert has_text_content, "Expected at least one message with text content"
