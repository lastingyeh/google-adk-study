"""
A2A Agent 實作的測試套件。

**重點說明：**
- 測試 Agent 的設定、工具以及 A2A 的設定。
- 確保 `root_agent` 存在且設定正確。
- 驗證 `root_agent` 包含必要的子 Agent 和工具。
- 測試工具函式的行為是否符合預期。
"""

import pytest
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent


class TestA2AAgent:
    """測試主要的 A2A Agent 設定。"""

    def test_root_agent_exists(self):
        """測試 `root_agent` 是否存在且設定正確。"""
        from a2a_orchestrator.agent import root_agent

        assert isinstance(root_agent, Agent)
        assert root_agent.name == "a2a_orchestrator"
        assert root_agent.description == "Coordinates multiple remote specialized agents using official ADK A2A"

    def test_root_agent_has_sub_agents(self):
        """測試 `root_agent` 是否擁有正確的子 Agent。"""
        from a2a_orchestrator.agent import root_agent

        assert hasattr(root_agent, 'sub_agents')
        assert len(root_agent.sub_agents) == 3

        agent_names = [agent.name for agent in root_agent.sub_agents]
        assert "research_specialist" in agent_names
        assert "data_analyst" in agent_names
        assert "content_writer" in agent_names

    def test_root_agent_has_tools(self):
        """測試 `root_agent` 是否擁有必要的工具。"""
        from a2a_orchestrator.agent import root_agent

        assert hasattr(root_agent, 'tools')
        assert len(root_agent.tools) >= 2

        # 使用工具的 name 屬性檢查工具名稱
        tool_names = [tool.name for tool in root_agent.tools]
        assert "check_agent_availability" in tool_names
        assert "log_coordination_step" in tool_names

    def test_check_agent_availability_function(self):
        """測試 `check_agent_availability` 工具函式。"""
        from a2a_orchestrator.agent import check_agent_availability

        # 使用無效的 URL 進行測試 (應返回錯誤)
        result = check_agent_availability("test_agent", "http://invalid-url:9999")
        assert result["status"] == "error"
        assert result["available"] is False


class TestAgentConfiguration:
    """測試 Agent 的設定與安裝。"""

    def test_agent_model_configuration(self):
        """測試 Agent 是否使用正確的模型。"""
        from a2a_orchestrator.agent import root_agent

        assert root_agent.model == "gemini-2.0-flash"

    def test_agent_instruction_exists(self):
        """測試 Agent 是否有指令。"""
        from a2a_orchestrator.agent import root_agent

        assert hasattr(root_agent, 'instruction')
        assert root_agent.instruction is not None
        assert len(root_agent.instruction.strip()) > 0

    def test_sub_agent_configurations(self):
        """測試子 Agent 是否有正確的設定。"""
        from a2a_orchestrator.agent import root_agent

        for sub_agent in root_agent.sub_agents:
            assert isinstance(sub_agent, RemoteA2aAgent)
            # RemoteA2aAgent 使用 agent_card 參數而非 base_url
            assert hasattr(sub_agent, 'name')
            assert hasattr(sub_agent, 'description')
            # 檢查它是否為遠端 Agent (具有遠端連線能力)


class TestTools:
    """測試 Agent 的工具。"""

    def test_check_agent_availability_returns_dict(self):
        """測試 `check_agent_availability` 是否返回正確的格式。"""
        from a2a_orchestrator.agent import check_agent_availability

        result = check_agent_availability("test", "http://invalid:9999")

        assert isinstance(result, dict)
        assert "status" in result
        assert "available" in result
        assert "report" in result

    def test_log_coordination_step_returns_dict(self):
        """測試 `log_coordination_step` 是否返回正確的格式。"""
        from a2a_orchestrator.agent import log_coordination_step

        result = log_coordination_step("test step", "test_agent")

        assert isinstance(result, dict)
        assert "status" in result
        assert "report" in result
        assert "step" in result
        assert "agent" in result
        assert result["status"] == "success"
