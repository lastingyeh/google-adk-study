"""
Tutorial 26 的測試套件：Gemini 企業級代理配置與功能。
"""

import pytest
from enterprise_agent.agent import root_agent


class TestAgentConfiguration:
    """測試企業潛在客戶資格審查代理的配置。"""

    def test_agent_exists(self):
        """測試 root_agent 是否已定義。"""
        assert root_agent is not None, "root_agent 應該要被定義"

    def test_agent_name(self):
        """測試代理是否具有正確的名稱。"""
        assert root_agent.name == "lead_qualifier"

    def test_agent_model(self):
        """測試代理是否使用正確的模型。"""
        assert root_agent.model == "gemini-2.0-flash"

    def test_agent_description(self):
        """測試代理是否有描述。"""
        assert root_agent.description is not None
        assert len(root_agent.description) > 0
        assert "enterprise" in root_agent.description.lower()
        assert "qualification" in root_agent.description.lower()

    def test_agent_instruction(self):
        """測試代理是否有指令。"""
        assert root_agent.instruction is not None
        assert len(root_agent.instruction) > 0

    def test_instruction_content(self):
        """測試指令是否包含關鍵的資格審查標準。"""
        instruction = root_agent.instruction.lower()

        # 應提及關鍵資格審查標準
        assert "company size" in instruction or "employees" in instruction
        assert "industry" in instruction or "industries" in instruction
        assert "budget" in instruction or "enterprise" in instruction

        # 應提及評分門檻
        assert "70" in instruction or "qualified" in instruction
        assert "score" in instruction

    def test_agent_has_tools(self):
        """測試代理是否已配置工具。"""
        assert hasattr(root_agent, 'tools')
        assert root_agent.tools is not None
        assert len(root_agent.tools) > 0

    def test_agent_tool_count(self):
        """測試代理是否擁有預期數量的工具。"""
        # 應至少有 check_company_size 和 score_lead
        assert len(root_agent.tools) >= 2


class TestAgentType:
    """測試代理是否為企業部署的正確類型。"""

    def test_agent_is_agent_instance(self):
        """測試 root_agent 是否為 Agent 實例。"""
        from google.adk.agents import Agent
        assert isinstance(root_agent, Agent)

    def test_not_sequential_agent(self):
        """測試這是一個簡單的代理，而不是順序工作流程。"""
        from google.adk.agents import SequentialAgent
        assert not isinstance(root_agent, SequentialAgent)

    def test_not_parallel_agent(self):
        """測試這是一個簡單的代理，而不是並行工作流程。"""
        from google.adk.agents import ParallelAgent
        assert not isinstance(root_agent, ParallelAgent)
