"""
測試 WebsiteBuilderSimple Agent 的核心功能與配置。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestWebsiteBuilderConfiguration:
    """測試 WebsiteBuilderSimple 配置。"""

    def test_agent_initialization(self):
        """測試 Agent 初始化。

        重點說明：
        1. 匯入 WebsiteBuilderSimple 類別
        2. 建立實例
        3. 驗證實例建立成功且不為 None
        """
        from agents.website_builder_simple.agent import WebsiteBuilderSimple

        agent = WebsiteBuilderSimple()
        assert agent is not None

    def test_system_instruction_loaded(self):
        """測試系統指令是否載入。

        重點說明：
        1. 建立 WebsiteBuilderSimple 實例
        2. 檢查 system_instruction 屬性是否存在
        3. 驗證 system_instruction 是否為字串且不為空
        """
        from agents.website_builder_simple.agent import WebsiteBuilderSimple

        agent = WebsiteBuilderSimple()
        assert hasattr(agent, "system_instruction")
        assert isinstance(agent.system_instruction, str)
        assert len(agent.system_instruction) > 0

    def test_description_loaded(self):
        """測試描述是否載入。

        重點說明：
        1. 建立 WebsiteBuilderSimple 實例
        2. 檢查 description 屬性是否存在
        3. 驗證 description 是否為字串且不為空
        """
        from agents.website_builder_simple.agent import WebsiteBuilderSimple

        agent = WebsiteBuilderSimple()
        assert hasattr(agent, "description")
        assert isinstance(agent.description, str)
        assert len(agent.description) > 0

    def test_response_model_exists(self):
        """測試 AgentResponse 模型是否存在。

        重點說明：
        1. 嘗試匯入 AgentResponse 類別
        2. 驗證類別是否存在
        """
        from agents.website_builder_simple.agent import AgentResponse

        assert AgentResponse is not None

    def test_response_model_validation(self):
        """測試 AgentResponse 模型驗證。

        重點說明：
        1. 建立包含所有必要欄位的 AgentResponse 實例
        2. 驗證各欄位值是否正確 (is_task_complete, updates, content)
        """
        from agents.website_builder_simple.agent import AgentResponse

        # 測試建立有效的 response
        response = AgentResponse(
            is_task_complete=True, updates="Test update", content="Test content"
        )

        assert response.is_task_complete is True
        assert response.updates == "Test update"
        assert response.content == "Test content"

    def test_initial_state(self):
        """測試初始狀態。

        重點說明：
        1. 建立 WebsiteBuilderSimple 實例
        2. 驗證 _agent 屬性已初始化且為 LlmAgent 實例
        3. 驗證 _runner 屬性已初始化且為 Runner 實例
        """
        from agents.website_builder_simple.agent import WebsiteBuilderSimple
        from google.adk.agents import LlmAgent
        from google.adk import Runner

        agent = WebsiteBuilderSimple()
        assert agent._agent is not None
        assert isinstance(agent._agent, LlmAgent)
        assert agent._runner is not None
        assert isinstance(agent._runner, Runner)


class TestWebsiteBuilderCreation:
    """測試 WebsiteBuilderSimple 建立流程。"""

    def test_build_agent_creates_llm_agent(self):
        """測試 _build_agent 建立 LLM Agent。

        重點說明：
        1. 建立 WebsiteBuilderSimple 實例
        2. 呼叫 _build_agent() 方法
        3. 驗證回傳物件為 LlmAgent 實例
        """
        from agents.website_builder_simple.agent import WebsiteBuilderSimple
        from google.adk.agents import LlmAgent

        agent = WebsiteBuilderSimple()
        llm_agent = agent._build_agent()

        assert llm_agent is not None
        assert isinstance(llm_agent, LlmAgent)

    def test_agent_model_configuration(self):
        """測試 Agent 模型配置。

        重點說明：
        1. 建立 WebsiteBuilderSimple 實例
        2. 呼叫 _build_agent()
        3. 驗證 agent 名稱是否為 "website_builder_simple"
        4. 驗證 agent 使用的模型是否在允許的清單中
        """
        from agents.website_builder_simple.agent import WebsiteBuilderSimple

        agent = WebsiteBuilderSimple()
        llm_agent = agent._build_agent()

        assert llm_agent.name == "website_builder_simple"
        assert llm_agent.model in [
            "gemini-2.5-flash",
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]

    def test_agent_has_system_instruction(self):
        """測試 Agent 是否有系統指令。

        重點說明：
        1. 建立 WebsiteBuilderSimple 實例
        2. 呼叫 _build_agent()
        3. 驗證 agent.instruction 不為 None 且長度大於 0
        """
        from agents.website_builder_simple.agent import WebsiteBuilderSimple

        agent = WebsiteBuilderSimple()
        llm_agent = agent._build_agent()

        assert llm_agent.instruction is not None
        assert len(llm_agent.instruction) > 0


class TestWebsiteBuilderFunctionality:
    """測試 WebsiteBuilderSimple 功能。"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_invoke_returns_generator(self, sample_queries):
        """測試 invoke 回傳 generator。

        重點說明：
        1. 建立 WebsiteBuilderSimple 實例
        2. Mock runner.run_async 方法回傳模擬的對話事件
        3. 呼叫 agent.invoke()
        4. 驗證 invoke 過程回傳了結果
        """
        from agents.website_builder_simple.agent import WebsiteBuilderSimple

        agent = WebsiteBuilderSimple()

        # Mock runner
        with patch.object(agent._runner, "run_async") as mock_run:

            async def mock_run_generator(*args, **kwargs):
                mock_event = Mock()
                mock_event.is_final_response.return_value = True
                mock_event.content = Mock()
                mock_event.content.parts = [Mock()]
                mock_event.content.parts[0].text = '{"is_task_complete": true, "content": "Test HTML"}'
                yield mock_event

            mock_run.return_value = mock_run_generator()

            # 測試 invoke
            query = sample_queries[0]
            results = []
            async for item in agent.invoke(query, "test-session"):
                results.append(item)

            assert len(results) > 0

    def test_query_length_validation(self):
        """測試查詢長度驗證。

        重點說明：
        1. 匯入查詢長度常數
        2. 驗證 MAX_QUERY_LENGTH > 0
        3. 驗證 MIN_QUERY_LENGTH > 0
        4. 驗證 MAX_QUERY_LENGTH > MIN_QUERY_LENGTH
        """
        from agents.website_builder_simple.agent import (
            WebsiteBuilderSimple,
            MAX_QUERY_LENGTH,
            MIN_QUERY_LENGTH,
        )

        agent = WebsiteBuilderSimple()

        # 測試常數存在
        assert MAX_QUERY_LENGTH > 0
        assert MIN_QUERY_LENGTH > 0
        assert MAX_QUERY_LENGTH > MIN_QUERY_LENGTH


class TestWebsiteBuilderExecutor:
    """測試 WebsiteBuilderSimpleAgentExecutor。"""

    def test_executor_initialization(self):
        """測試 Executor 初始化。

        重點說明：
        1. 匯入 WebsiteBuilderSimpleAgentExecutor
        2. 建立實例
        3. 驗證實例建立成功
        4. 驗證 agent 屬性存在
        5. 驗證 _cancel_requested 屬性存在
        """
        from agents.website_builder_simple.agent_executor import (
            WebsiteBuilderSimpleAgentExecutor,
        )

        executor = WebsiteBuilderSimpleAgentExecutor()
        assert executor is not None
        assert hasattr(executor, "agent")
        assert hasattr(executor, "_cancel_requested")

    def test_executor_cancel_flag_initial_state(self):
        """測試 Executor 取消旗標初始狀態。

        重點說明：
        1. 建立 WebsiteBuilderSimpleAgentExecutor 實例
        2. 驗證 _cancel_requested 初始值為 False
        """
        from agents.website_builder_simple.agent_executor import (
            WebsiteBuilderSimpleAgentExecutor,
        )

        executor = WebsiteBuilderSimpleAgentExecutor()
        assert executor._cancel_requested is False

    @pytest.mark.asyncio
    async def test_executor_execute_with_mock(self):
        """測試 Executor execute 方法（使用 mock）。

        重點說明：
        1. 建立 Executor 實例
        2. Mock RequestContext 和 EventQueue
        3. Mock agent.invoke 方法回傳模擬的回應
        4. 呼叫 executor.execute()
        5. 驗證 agent.invoke 方法被呼叫一次
        """
        from agents.website_builder_simple.agent_executor import (
            WebsiteBuilderSimpleAgentExecutor,
        )
        from a2a.server.events import EventQueue
        from a2a.server.agent_execution import RequestContext
        from a2a.types import Message, Part

        executor = WebsiteBuilderSimpleAgentExecutor()

        # Mock context 和 event_queue
        mock_context = Mock(spec=RequestContext)
        mock_context.get_user_input.return_value = "Build a test website"
        mock_context.current_task = None

        # 建立完整的 Message 物件
        mock_context.message = Message(
            messageId="test-message-id",
            taskId="test-task-id",
            contextId="test-context-id",
            role="user",
            parts=[Part(text="Build a test website")],
        )

        mock_event_queue = AsyncMock(spec=EventQueue)

        # Mock agent.invoke
        async def mock_invoke(*args, **kwargs):
            yield {"is_task_complete": True, "content": "Test response"}

        with patch.object(
            executor.agent, "invoke", side_effect=mock_invoke
        ) as mock_agent_invoke:
            # 執行 execute
            await executor.execute(mock_context, mock_event_queue)

            # 驗證 invoke 被呼叫
            mock_agent_invoke.assert_called_once()

    def test_executor_timeout_constant(self):
        """測試 Executor 超時常數。

        重點說明：
        1. 匯入 TASK_EXECUTION_TIMEOUT
        2. 驗證超時值大於 0 且為整數
        """
        from agents.website_builder_simple.agent_executor import (
            TASK_EXECUTION_TIMEOUT,
        )

        assert TASK_EXECUTION_TIMEOUT > 0
        assert isinstance(TASK_EXECUTION_TIMEOUT, int)


class TestAgentResponseModel:
    """測試 AgentResponse Pydantic 模型。"""

    def test_response_with_all_fields(self):
        """測試包含所有欄位的 response。

        重點說明：
        1. 使用所有欄位建立 AgentResponse 實例
        2. 驗證各欄位值是否正確
        """
        from agents.website_builder_simple.agent import AgentResponse

        response = AgentResponse(
            is_task_complete=True,
            updates="Processing",
            content="<html>Test</html>",
        )

        assert response.is_task_complete is True
        assert response.updates == "Processing"
        assert response.content == "<html>Test</html>"

    def test_response_default_values(self):
        """測試預設值。

        重點說明：
        1. 只使用必要欄位建立 AgentResponse 實例
        2. 驗證必要欄位值是否正確
        """
        from agents.website_builder_simple.agent import AgentResponse

        # 測試只提供必要欄位
        response = AgentResponse(is_task_complete=False)

        assert response.is_task_complete is False
        # 檢查其他欄位的預設值
