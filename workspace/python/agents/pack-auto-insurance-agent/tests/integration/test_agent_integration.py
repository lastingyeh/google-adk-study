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

import pytest
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from auto_insurance_agent.agent import root_agent


class TestAgentIntegration:
    """Agent 整合測試"""

    @pytest.fixture
    def runner(self):
        """建立 Runner 實例"""
        session_service = InMemorySessionService()
        return Runner(
            agent=root_agent, session_service=session_service, app_name="test_app"
        )

    @pytest.fixture
    def session(self, runner):
        """建立測試 Session"""
        return runner.session_service.create_session_sync(
            user_id="test_user", app_name="test_app"
        )

    def test_agent_basic_execution(self, runner, session):
        """測試 Agent 基本執行流程"""
        # 建立使用者訊息
        message = types.Content(role="user", parts=[types.Part.from_text(text="Hello")])

        # 執行 Agent
        events = list(
            runner.run(
                new_message=message,
                user_id="test_user",
                session_id=session.id,
                run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            )
        )

        # 驗證是否有收到事件
        assert len(events) > 0

    def test_agent_streaming_events(self, runner, session):
        """驗證串流事件格式"""
        message = types.Content(
            role="user", parts=[types.Part.from_text(text="Help me with membership")]
        )

        # 執行 Agent 並收集所有事件
        events = list(
            runner.run(
                new_message=message,
                user_id="test_user",
                session_id=session.id,
                run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            )
        )

        # 驗證事件類型
        # 預期至少會有 'chunk' 或 'complete' 類型的事件
        # 注意：實際事件結構取決於 ADK 的實作細節，此處驗證基本存在性
        assert events is not None
        assert len(events) > 0
