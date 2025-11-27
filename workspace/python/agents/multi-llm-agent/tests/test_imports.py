# 教學 28：使用其他 LLM - 匯入測試
# 驗證所有必要的匯入是否能正常運作

import pytest


class TestImports:
    """測試所有必要的匯入是否能正常運作。"""

    def test_adk_imports(self):
        """測試 ADK 核心匯入是否能正常運作。"""
        from google.adk.agents import Agent
        from google.adk.runners import InMemoryRunner
        from google.adk.models.lite_llm import LiteLlm
        from google.adk.tools import FunctionTool

        assert Agent is not None
        assert InMemoryRunner is not None
        assert LiteLlm is not None
        assert FunctionTool is not None

    def test_litellm_import(self):
        """測試 LiteLLM 匯入是否能正常運作。"""
        import litellm
        assert litellm is not None

    def test_openai_import(self):
        """測試 OpenAI 匯入是否能正常運作。"""
        import openai
        assert openai is not None

    def test_anthropic_import(self):
        """測試 Anthropic 匯入是否能正常運作。"""
        import anthropic
        assert anthropic is not None

    def test_agent_package_import(self):
        """測試 agent 套件是否可以被匯入。"""
        from multi_llm_agent import agent
        assert agent is not None

    def test_root_agent_import(self):
        """測試 root_agent 是否可以被匯入。"""
        from multi_llm_agent.agent import root_agent
        assert root_agent is not None

    def test_alternative_agents_import(self):
        """測試替代 agents 是否可以被匯入。"""
        from multi_llm_agent.agent import gpt4o_agent, claude_agent, ollama_agent
        assert gpt4o_agent is not None
        assert claude_agent is not None
        assert ollama_agent is not None

    def test_tool_functions_import(self):
        """測試工具函式是否可以被匯入。"""
        from multi_llm_agent.agent import calculate_square, get_weather, analyze_sentiment
        assert calculate_square is not None
        assert get_weather is not None
        assert analyze_sentiment is not None
