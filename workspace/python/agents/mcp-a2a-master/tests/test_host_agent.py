"""
測試 HostAgent 的核心功能與配置。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock


class TestHostAgentConfiguration:
    """測試 HostAgent 配置。"""

    def test_agent_initialization(self):
        """測試 HostAgent 初始化。

        重點說明：
        1. 匯入 HostAgent 類別
        2. 建立 HostAgent 實例
        3. 驗證實例是否成功建立且不為 None
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()
        assert agent is not None

    def test_system_instruction_loaded(self):
        """測試系統指令是否載入。

        重點說明：
        1. 建立 HostAgent 實例
        2. 檢查 system_instruction 屬性是否存在
        3. 驗證 system_instruction 是否為字串且不為空
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()
        assert hasattr(agent, "system_instruction")
        assert isinstance(agent.system_instruction, str)
        assert len(agent.system_instruction) > 0

    def test_description_loaded(self):
        """測試描述是否載入。

        重點說明：
        1. 建立 HostAgent 實例
        2. 檢查 description 屬性是否存在
        3. 驗證 description 是否為字串且不為空
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()
        assert hasattr(agent, "description")
        assert isinstance(agent.description, str)
        assert len(agent.description) > 0

    def test_mcp_connector_initialized(self):
        """測試 MCP Connector 是否初始化。

        重點說明：
        1. 建立 HostAgent 實例
        2. 檢查 MCPConnector 屬性是否存在
        3. 驗證 MCPConnector 是否已初始化
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()
        assert hasattr(agent, "MCPConnector")
        assert agent.MCPConnector is not None

    def test_agent_discovery_initialized(self):
        """測試 Agent Discovery 是否初始化。

        重點說明：
        1. 建立 HostAgent 實例
        2. 檢查 AgentDiscovery 屬性是否存在
        3. 驗證 AgentDiscovery 是否已初始化
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()
        assert hasattr(agent, "AgentDiscovery")
        assert agent.AgentDiscovery is not None

    def test_initial_state(self):
        """測試初始狀態。

        重點說明：
        1. 建立 HostAgent 實例
        2. 驗證 _agent 屬性初始為 None
        3. 驗證 _runner 屬性初始為 None
        4. 驗證 _user_id 屬性初始值正確
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()
        assert agent._agent is None
        assert agent._runner is None
        assert agent._user_id == "host_agent_user"


class TestHostAgentCreation:
    """測試 HostAgent 建立流程。"""

    @pytest.mark.asyncio
    async def test_create_agent(self):
        """測試 create 方法。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock MCPConnector.get_tools 方法以避免外部連接
        3. 呼叫 agent.create() 方法
        4. 驗證 _agent 和 _runner 屬性是否已建立
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock MCP tools 以避免實際連接
        with patch.object(
            agent.MCPConnector, "get_tools", new_callable=AsyncMock
        ) as mock_get_tools:
            mock_get_tools.return_value = []

            await agent.create()

            assert agent._agent is not None
            assert agent._runner is not None

    @pytest.mark.asyncio
    async def test_build_agent_creates_llm_agent(self):
        """測試 _build_agent 建立 LLM Agent。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock MCPConnector.get_tools 方法
        3. 呼叫 agent._build_agent() 方法
        4. 驗證回傳物件是否為 LlmAgent 實例
        """
        from agents.host_agent.agent import HostAgent
        from google.adk.agents import LlmAgent

        agent = HostAgent()

        # Mock MCP tools
        with patch.object(
            agent.MCPConnector, "get_tools", new_callable=AsyncMock
        ) as mock_get_tools:
            mock_get_tools.return_value = []

            llm_agent = await agent._build_agent()

            assert llm_agent is not None
            assert isinstance(llm_agent, LlmAgent)

    @pytest.mark.asyncio
    async def test_agent_includes_function_tools(self):
        """測試 Agent 是否包含 Function Tools。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock MCPConnector.get_tools 方法
        3. 呼叫 agent._build_agent()
        4. 驗證生成的 agent 是否包含 tools 屬性
        5. 驗證 tools 數量是否正確 (至少包含 _delegate_task 和 _list_agents)
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock MCP tools
        with patch.object(
            agent.MCPConnector, "get_tools", new_callable=AsyncMock
        ) as mock_get_tools:
            mock_get_tools.return_value = []

            llm_agent = await agent._build_agent()

            # 檢查是否有工具
            assert hasattr(llm_agent, "tools")
            assert len(llm_agent.tools) >= 2  # 至少有 _delegate_task 和 _list_agents

    @pytest.mark.asyncio
    async def test_agent_model_configuration(self):
        """測試 Agent 模型配置。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock MCPConnector.get_tools 方法
        3. 呼叫 agent._build_agent()
        4. 驗證 agent 名稱是否為 "host_agent"
        5. 驗證 agent 使用的模型是否在允許的清單中
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock MCP tools
        with patch.object(
            agent.MCPConnector, "get_tools", new_callable=AsyncMock
        ) as mock_get_tools:
            mock_get_tools.return_value = []

            llm_agent = await agent._build_agent()

            assert llm_agent.name == "host_agent"
            assert llm_agent.model in [
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-pro",
            ]


class TestHostAgentTools:
    """測試 HostAgent 的工具函式。"""

    @pytest.mark.asyncio
    async def test_list_agents_returns_list(self):
        """測試 _list_agents 回傳列表。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock AgentDiscovery.list_agent_cards 方法回傳空列表
        3. 呼叫 agent._list_agents()
        4. 驗證回傳結果是否為列表型別
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock AgentDiscovery
        with patch.object(
            agent.AgentDiscovery, "list_agent_cards", new_callable=AsyncMock
        ) as mock_list_cards:
            mock_list_cards.return_value = []

            result = await agent._list_agents()

            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_list_agents_with_mock_cards(self, mock_agent_card):
        """測試 _list_agents 與 mock agent cards。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock AgentDiscovery.list_agent_cards 方法回傳包含 mock_agent_card 的列表
        3. 呼叫 agent._list_agents()
        4. 驗證回傳列表長度為 1
        5. 驗證回傳的 agent 名稱是否正確
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock AgentDiscovery
        with patch.object(
            agent.AgentDiscovery, "list_agent_cards", new_callable=AsyncMock
        ) as mock_list_cards:
            mock_list_cards.return_value = [mock_agent_card]

            result = await agent._list_agents()

            assert len(result) == 1
            assert result[0]["name"] == "test_website_builder"

    @pytest.mark.asyncio
    async def test_delegate_task_success(self, mock_agent_card):
        """測試 _delegate_task 成功委派。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock AgentDiscovery 回傳有效的 agent cards
        3. Mock AgentConnector 及其 send_task 方法回傳成功訊息
        4. 呼叫 agent._delgate_task() 委派任務
        5. 驗證回傳結果與預期相符
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
                mock_connector.send_task = AsyncMock(return_value="Task completed")
                mock_connector_class.return_value = mock_connector

                result = await agent._delgate_task(
                    agent_name="test_website_builder", message="Test task"
                )

                assert result == "Task completed"

    @pytest.mark.asyncio
    async def test_delegate_task_agent_not_found(self):
        """測試 _delegate_task 找不到 Agent。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock AgentDiscovery 回傳空列表
        3. 呼叫 agent._delgate_task() 嘗試委派給不存在的 agent
        4. 驗證回傳錯誤訊息包含 "Agent not found"
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock AgentDiscovery 回傳空列表
        with patch.object(
            agent.AgentDiscovery, "list_agent_cards", new_callable=AsyncMock
        ) as mock_list_cards:
            mock_list_cards.return_value = []

            result = await agent._delgate_task(
                agent_name="nonexistent_agent", message="Test task"
            )

            assert result == "找不到代理 (Agent not found)"


class TestHostAgentInvoke:
    """測試 HostAgent 的 invoke 功能。"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_invoke_creates_session(self):
        """測試 invoke 建立 session。

        重點說明：
        1. 建立 HostAgent 實例
        2. Mock MCPConnector.get_tools
        3. 呼叫 agent.create()
        4. Mock runner.run_async 方法以回傳生成器
        5. 呼叫 agent.invoke()
        6. 驗證 invoke 過程回傳了結果
        """
        from agents.host_agent.agent import HostAgent

        agent = HostAgent()

        # Mock 所有相依
        with patch.object(
            agent.MCPConnector, "get_tools", new_callable=AsyncMock
        ) as mock_get_tools:
            mock_get_tools.return_value = []

            await agent.create()

            # Mock runner
            with patch.object(agent._runner, "run_async") as mock_run:

                async def mock_run_generator(*args, **kwargs):
                    # 模擬回傳一個 final response
                    mock_event = Mock()
                    mock_event.is_final_response.return_value = True
                    mock_event.content = Mock()
                    mock_event.content.parts = [Mock()]
                    mock_event.content.parts[0].text = "Test response"
                    yield mock_event

                mock_run.return_value = mock_run_generator()

                results = []
                async for item in agent.invoke("Test query", "test-session"):
                    results.append(item)

                # 驗證至少有一個結果
                assert len(results) > 0


class TestHostAgentExecutor:
    """測試 HostAgentExecutor。"""

    def test_executor_initialization(self):
        """測試 Executor 初始化。

        重點說明：
        1. 匯入 HostAgentExecutor
        2. 建立實例
        3. 驗證實例是否存在且包含 agent 屬性
        """
        from agents.host_agent.agent_executor import HostAgentExecutor

        executor = HostAgentExecutor()
        assert executor is not None
        assert hasattr(executor, "agent")

    @pytest.mark.asyncio
    async def test_executor_create(self):
        """測試 Executor create 方法。

        重點說明：
        1. 建立 HostAgentExecutor 實例
        2. Mock executor.agent.create 方法
        3. 呼叫 executor.create()
        4. 驗證 agent.create 方法被呼叫一次
        """
        from agents.host_agent.agent_executor import HostAgentExecutor

        executor = HostAgentExecutor()

        # Mock agent.create
        with patch.object(
            executor.agent, "create", new_callable=AsyncMock
        ) as mock_create:
            await executor.create()
            mock_create.assert_called_once()
