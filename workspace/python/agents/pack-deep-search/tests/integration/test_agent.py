# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


def test_agent_stream() -> None:
    """
    代理串流功能的整合測試。
    測試代理是否返回有效的串流響應。

    重點說明：
    1. 使用 InMemorySessionService 模擬會話管理。
    2. 使用 Runner 執行 root_agent。
    3. 驗證串流輸出是否包含文字內容。
    """

    # 初始化記憶體會話服務
    session_service = InMemorySessionService()

    # 建立測試會話
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    # 初始化執行器
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    # 建立使用者訊息
    message = types.Content(
        role="user", parts=[types.Part.from_text(text="Why is the sky blue?")]
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
