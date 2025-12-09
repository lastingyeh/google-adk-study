"""
整合測試 - 測試多個元件的協同工作。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.integration
class TestHostAgentMCPIntegration:
    """測試 HostAgent 與 MCP 整合。"""

    @pytest.mark.asyncio
    async def test_host_agent_loads_mcp_tools(self):
        """測試 HostAgent 載入 MCP 工具。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock MCPConnector.get_tools 方法回傳包含模擬工具的列表
        3. 呼叫 agent._build_agent() 觸發工具載入
        4. 驗證 agent.tools 列表長度（應包含 function tools 和 MCP tools）
        5. 驗證 mock_get_tools 方法被呼叫一次
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock MCP tools
        with patch.object(
            agent.MCPConnector, "get_tools", new_callable=AsyncMock
        ) as mock_get_tools:
            # 模擬 MCP 工具回傳
            mock_tool = Mock()
            mock_tool.name = "test_mcp_tool"
            mock_get_tools.return_value = [mock_tool]

            llm_agent = await agent._build_agent()

            # 驗證工具被載入
            assert len(llm_agent.tools) >= 3  # 2 個 function tools + 1 個 MCP tool
            mock_get_tools.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_connector_discovery_integration(self):
        """測試 MCP Connector 與 Discovery 整合。

        重點說明：
        1. 建立 MCPConnector 實例
        2. 驗證 connector.discovery 屬性已初始化
        3. 驗證 discovery 物件包含 list_servers 方法
        """
        from utilities.mcp.mcp_connect import MCPConnector

        connector = MCPConnector()

        # 驗證 discovery 已初始化
        assert connector.discovery is not None
        assert hasattr(connector.discovery, "list_servers")


@pytest.mark.integration
class TestHostAgentA2AIntegration:
    """測試 HostAgent 與 A2A 整合。"""

    @pytest.mark.asyncio
    async def test_agent_discovery_integration(self):
        """測試 Agent Discovery 整合。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock AgentDiscovery.list_agent_cards 回傳模擬的 agent card
        3. 呼叫 agent._list_agents()
        4. 驗證回傳的列表長度和內容是否正確
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock AgentDiscovery
        with patch.object(
            agent.AgentDiscovery, "list_agent_cards", new_callable=AsyncMock
        ) as mock_list_cards:
            from a2a.types import AgentCard, AgentCapabilities

            mock_card = AgentCard(
                name="test_agent",
                url="http://localhost:10001",
                version="1.0.0",
                description="Test",
                capabilities=AgentCapabilities(streaming=True),
                defaultInputModes=["text/plain"],
                defaultOutputModes=["text/plain"],
                skills=[],
            )
            mock_list_cards.return_value = [mock_card]

            # 測試 list_agents
            result = await agent._list_agents()

            assert len(result) == 1
            assert result[0]["name"] == "test_agent"

    @pytest.mark.asyncio
    async def test_delegate_task_to_child_agent(self, mock_agent_card):
        """測試任務委派到子 Agent。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock AgentDiscovery 回傳有效的 agent cards
        3. Mock AgentConnector 及其 send_task 方法回傳成功結果
        4. 呼叫 agent._delgate_task()
        5. 驗證回傳結果包含預期的成功訊息
        6. 驗證 send_task 方法被呼叫一次
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock AgentDiscovery 和 AgentConnector
        with patch.object(
            agent.AgentDiscovery, "list_agent_cards", new_callable=AsyncMock
        ) as mock_list_cards:
            with patch(
                "agents.host_agent.agent.AgentConnector"
            ) as mock_connector_class:
                mock_list_cards.return_value = [mock_agent_card]

                mock_connector = AsyncMock()
                mock_connector.send_task = AsyncMock(
                    return_value="Task completed successfully"
                )
                mock_connector_class.return_value = mock_connector

                result = await agent._delgate_task(
                    agent_name="test_website_builder",
                    message="Build a homepage",
                )

                assert "completed" in result.lower()
                mock_connector.send_task.assert_called_once()


@pytest.mark.integration
class TestAgentExecutorIntegration:
    """測試 AgentExecutor 整合。"""

    @pytest.mark.asyncio
    async def test_host_agent_executor_execute(self):
        """測試 HostAgentExecutor 執行。

        重點說明：
        1. 建立 HostAgentExecutor 實例並初始化
        2. Mock RequestContext 和 EventQueue
        3. Mock agent.invoke 方法回傳模擬的回應
        4. 呼叫 executor.execute()
        5. 驗證 event_queue.enqueue_event 方法被呼叫，確認事件已加入佇列
        """
        from agents.host_agent.agent_executor import HostAgentExecutor
        from a2a.server.events import EventQueue
        from a2a.server.agent_execution import RequestContext
        from a2a.types import Message, Part

        executor = HostAgentExecutor()

        # Mock 所有相依
        with patch.object(
            executor.agent.MCPConnector, "get_tools", new_callable=AsyncMock
        ) as mock_get_tools:
            mock_get_tools.return_value = []

            await executor.create()

        # Mock context 和 event_queue
        mock_context = Mock(spec=RequestContext)
        mock_context.get_user_input.return_value = "Test query"
        mock_context.current_task = None

        # 建立完整的 Message 物件
        mock_context.message = Message(
            messageId="test-message-id",
            taskId="test-task-id",
            contextId="test-context-id",
            role="user",
            parts=[Part(text="Test query")],
        )

        mock_event_queue = AsyncMock(spec=EventQueue)

        # Mock agent.invoke
        async def mock_invoke(*args, **kwargs):
            yield {"is_task_complete": True, "content": "Test response"}

        with patch.object(executor.agent, "invoke", side_effect=mock_invoke):
            # 執行 execute
            await executor.execute(mock_context, mock_event_queue)

            # 驗證事件被加入佇列
            assert mock_event_queue.enqueue_event.called

    @pytest.mark.asyncio
    async def test_website_builder_executor_execute(self):
        """測試 WebsiteBuilderSimpleAgentExecutor 執行。

        重點說明：
        1. 建立 WebsiteBuilderSimpleAgentExecutor 實例
        2. Mock RequestContext 和 EventQueue
        3. Mock agent.invoke 方法回傳模擬的回應
        4. 呼叫 executor.execute()
        5. 驗證 event_queue.enqueue_event 方法被呼叫，確認事件已加入佇列
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
        mock_context.get_user_input.return_value = "Build a website"
        mock_context.current_task = None

        # 建立完整的 Message 物件
        mock_context.message = Message(
            messageId="test-message-id",
            taskId="test-task-id",
            contextId="test-context-id",
            role="user",
            parts=[Part(text="Build a website")],
        )

        mock_event_queue = AsyncMock(spec=EventQueue)

        # Mock agent.invoke
        async def mock_invoke(*args, **kwargs):
            yield {
                "is_task_complete": True,
                "content": "<html>Test Website</html>",
            }

        with patch.object(executor.agent, "invoke", side_effect=mock_invoke):
            # 執行 execute
            await executor.execute(mock_context, mock_event_queue)

            # 驗證事件被加入佇列
            assert mock_event_queue.enqueue_event.called


@pytest.mark.integration
class TestUtilitiesIntegration:
    """測試 Utilities 整合。"""

    @pytest.mark.asyncio
    async def test_agent_connector_with_discovery(self, mock_agent_card):
        """測試 AgentConnector 與 Discovery 整合。

        重點說明：
        1. 建立 AgentDiscovery 實例
        2. Mock list_agent_cards 方法回傳模擬的 agent card
        3. 呼叫 discovery.list_agent_cards()
        4. 使用取得的 agent card 建立 AgentConnector
        5. 驗證 connector.agent_card 不為 None
        """
        from utilities.a2a.agent_connect import AgentConnector
        from utilities.a2a.agent_discovery import AgentDiscovery

        discovery = AgentDiscovery()

        # Mock discovery
        with patch.object(
            discovery, "list_agent_cards", new_callable=AsyncMock
        ) as mock_list_cards:
            mock_list_cards.return_value = [mock_agent_card]

            cards = await discovery.list_agent_cards()
            assert len(cards) >= 1

            # 使用第一個 card 建立 connector
            if len(cards) > 0:
                connector = AgentConnector(agent_card=cards[0])
                assert connector.agent_card is not None

    @pytest.mark.asyncio
    async def test_mcp_connector_with_discovery(self):
        """測試 MCPConnector 與 Discovery 整合。

        重點說明：
        1. 建立 MCPConnector 實例
        2. 驗證 discovery 屬性被正確設定
        3. 呼叫 discovery.list_servers()
        4. 驗證回傳結果為字典型別
        """
        from utilities.mcp.mcp_connect import MCPConnector

        connector = MCPConnector()

        # 測試 discovery 被正確設定
        assert connector.discovery is not None

        # 測試 list_servers
        servers = connector.discovery.list_servers()
        assert isinstance(servers, dict)


@pytest.mark.integration
class TestEndToEndWorkflow:
    """測試端對端工作流程（簡化版）。"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_complete_workflow_with_mocks(self):
        """測試完整工作流程（使用 mocks）。

        重點說明：
        1. 初始化 HostAgent
        2. Mock MCPConnector 和 AgentDiscovery 以模擬外部相依
        3. 呼叫 agent.create() 建立 agent
        4. Mock runner.run_async 回傳模擬的對話事件
        5. 呼叫 agent.invoke() 執行完整工作流程
        6. 驗證執行結果包含 is_task_complete=True
        """
        from agents.host_agent.agent import HostAgent

        # 步驟 1: 初始化 HostAgent
        agent = HostAgent()

        # 步驟 2: Mock 所有外部相依
        with patch.object(
            agent.MCPConnector, "get_tools", new_callable=AsyncMock
        ) as mock_mcp_tools:
            with patch.object(
                agent.AgentDiscovery, "list_agent_cards", new_callable=AsyncMock
            ) as mock_a2a_discovery:
                # 設定 mocks
                mock_mcp_tools.return_value = []
                mock_a2a_discovery.return_value = []

                # 步驟 3: 建立 Agent
                await agent.create()

                # 驗證 Agent 被正確建立
                assert agent._agent is not None
                assert agent._runner is not None

                # 步驟 4: Mock Runner 回應
                with patch.object(agent._runner, "run_async") as mock_run:

                    async def mock_run_generator(*args, **kwargs):
                        mock_event = Mock()
                        mock_event.is_final_response.return_value = True
                        mock_event.content = Mock()
                        mock_event.content.parts = [Mock()]
                        mock_event.content.parts[0].text = "Workflow completed"
                        yield mock_event

                    mock_run.return_value = mock_run_generator()

                    # 步驟 5: 執行查詢
                    results = []
                    async for item in agent.invoke("Test workflow", "test-session"):
                        results.append(item)

                    # 步驟 6: 驗證結果
                    assert len(results) > 0
                    assert results[-1]["is_task_complete"] is True
