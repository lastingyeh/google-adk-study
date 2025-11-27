# 教學 28：使用其他 LLM - Agent 測試
# 驗證 Agent 設定與工具功能

import pytest
from unittest.mock import patch, MagicMock


class TestAgentConfiguration:
    """測試 Agent 是否正確設定。"""

    def test_root_agent_import(self):
        """測試 root_agent 是否可以被匯入。"""
        from multi_llm_agent.agent import root_agent
        assert root_agent is not None

    def test_root_agent_is_agent_instance(self):
        """測試 root_agent 是否為 Agent 的一個實例。"""
        from multi_llm_agent.agent import root_agent
        from google.adk.agents import Agent
        assert isinstance(root_agent, Agent)

    def test_root_agent_name(self):
        """測試 root_agent 是否有正確的名稱。"""
        from multi_llm_agent.agent import root_agent
        assert hasattr(root_agent, 'name')
        assert root_agent.name == "multi_llm_agent"

    def test_root_agent_model(self):
        """測試 root_agent 是否有正確的模型。"""
        from multi_llm_agent.agent import root_agent
        from google.adk.models.lite_llm import LiteLlm
        assert hasattr(root_agent, 'model')
        assert isinstance(root_agent.model, LiteLlm)

    def test_root_agent_description(self):
        """測試 root_agent 是否有描述。"""
        from multi_llm_agent.agent import root_agent
        assert hasattr(root_agent, 'description')
        assert "Multi-LLM agent" in root_agent.description
        assert "LiteLLM" in root_agent.description

    def test_root_agent_instruction(self):
        """測試 root_agent 是否有指令。"""
        from multi_llm_agent.agent import root_agent
        assert hasattr(root_agent, 'instruction')
        assert len(root_agent.instruction) > 100
        assert "versatile AI assistant" in root_agent.instruction

    def test_root_agent_has_tools(self):
        """測試 root_agent 是否擁有工具。"""
        from multi_llm_agent.agent import root_agent
        assert hasattr(root_agent, 'tools')
        assert len(root_agent.tools) == 3  # calculate_square, get_weather, analyze_sentiment


class TestAlternativeAgents:
    """測試替代 Agent 設定。"""

    def test_gpt4o_agent_exists(self):
        """測試 gpt4o_agent 是否可以被匯入。"""
        from multi_llm_agent.agent import gpt4o_agent
        assert gpt4o_agent is not None

    def test_gpt4o_agent_has_correct_model(self):
        """測試 gpt4o_agent 是否使用正確的模型。"""
        from multi_llm_agent.agent import gpt4o_agent
        from google.adk.models.lite_llm import LiteLlm
        assert isinstance(gpt4o_agent.model, LiteLlm)
        # 注意：無法輕易檢查內部模型字串，而不存取私有屬性

    def test_claude_agent_exists(self):
        """測試 claude_agent 是否可以被匯入。"""
        from multi_llm_agent.agent import claude_agent
        assert claude_agent is not None

    def test_claude_agent_name(self):
        """測試 claude_agent 是否有正確的名稱。"""
        from multi_llm_agent.agent import claude_agent
        assert claude_agent.name == "claude_agent"

    def test_ollama_agent_exists(self):
        """測試 ollama_agent 是否可以被匯入。"""
        from multi_llm_agent.agent import ollama_agent
        assert ollama_agent is not None

    def test_ollama_agent_description_mentions_privacy(self):
        """測試 ollama_agent 的描述中是否提及隱私。"""
        from multi_llm_agent.agent import ollama_agent
        assert "privacy" in ollama_agent.description.lower()
        assert "local" in ollama_agent.description.lower()

    def test_all_agents_have_same_tools(self):
        """測試所有 Agent 是否擁有相同的工具集。"""
        from multi_llm_agent.agent import root_agent, gpt4o_agent, claude_agent, ollama_agent

        tool_count = len(root_agent.tools)
        assert len(gpt4o_agent.tools) == tool_count
        assert len(claude_agent.tools) == tool_count
        assert len(ollama_agent.tools) == tool_count


class TestToolFunctions:
    """測試工具函式是否能正常運作。"""

    def test_calculate_square_basic(self):
        """測試 calculate_square 函式搭配基本輸入。"""
        from multi_llm_agent.agent import calculate_square
        assert calculate_square(5) == 25
        assert calculate_square(10) == 100
        assert calculate_square(0) == 0

    def test_calculate_square_negative(self):
        """測試 calculate_square 函式搭配負數輸入。"""
        from multi_llm_agent.agent import calculate_square
        assert calculate_square(-5) == 25

    def test_get_weather_returns_dict(self):
        """測試 get_weather 是否回傳一個字典。"""
        from multi_llm_agent.agent import get_weather
        result = get_weather("San Francisco")
        assert isinstance(result, dict)

    def test_get_weather_has_required_fields(self):
        """測試 get_weather 的回傳值是否包含必要欄位。"""
        from multi_llm_agent.agent import get_weather
        result = get_weather("New York")
        assert 'city' in result
        assert 'temperature' in result
        assert 'condition' in result
        assert 'humidity' in result

    def test_get_weather_city_name(self):
        """測試 get_weather 是否保留城市名稱。"""
        from multi_llm_agent.agent import get_weather
        result = get_weather("London")
        assert result['city'] == "London"

    def test_analyze_sentiment_returns_dict(self):
        """測試 analyze_sentiment 是否回傳一個字典。"""
        from multi_llm_agent.agent import analyze_sentiment
        result = analyze_sentiment("This is great!")
        assert isinstance(result, dict)

    def test_analyze_sentiment_has_required_fields(self):
        """測試 analyze_sentiment 的回傳值是否包含必要欄位。"""
        from multi_llm_agent.agent import analyze_sentiment
        result = analyze_sentiment("Amazing product!")
        assert 'sentiment' in result
        assert 'confidence' in result
        assert 'key_phrases' in result

    def test_analyze_sentiment_confidence_is_float(self):
        """測試信賴度是否為浮點數。"""
        from multi_llm_agent.agent import analyze_sentiment
        result = analyze_sentiment("Wonderful experience")
        assert isinstance(result['confidence'], float)
        assert 0 <= result['confidence'] <= 1

    def test_analyze_sentiment_key_phrases_is_list(self):
        """測試 key_phrases 是否為一個列表。"""
        from multi_llm_agent.agent import analyze_sentiment
        result = analyze_sentiment("Excellent service")
        assert isinstance(result['key_phrases'], list)
        assert len(result['key_phrases']) > 0


class TestModelTypes:
    """測試模型類型驗證。"""

    def test_root_agent_uses_litellm(self):
        """測試 root_agent 是否使用 LiteLlm 模型。"""
        from multi_llm_agent.agent import root_agent
        from google.adk.models.lite_llm import LiteLlm
        assert isinstance(root_agent.model, LiteLlm)

    def test_all_alternative_agents_use_litellm(self):
        """測試所有替代 Agent 是否都使用 LiteLlm 模型。"""
        from multi_llm_agent.agent import gpt4o_agent, claude_agent, ollama_agent
        from google.adk.models.lite_llm import LiteLlm

        assert isinstance(gpt4o_agent.model, LiteLlm)
        assert isinstance(claude_agent.model, LiteLlm)
        assert isinstance(ollama_agent.model, LiteLlm)


@pytest.mark.integration
class TestAgentIntegration:
    """需要真實 ADK 元件的整合測試（可選）。"""

    def test_agent_can_be_created_without_error(self):
        """測試 Agent 是否可以在不引發例外的情況下被建立。"""
        try:
            from multi_llm_agent.agent import root_agent
            assert root_agent is not None
        except Exception as e:
            pytest.fail(f"Agent 建立失敗：{e}")

    def test_all_agents_can_be_created(self):
        """測試所有 Agent 變體是否都可以被建立。"""
        try:
            from multi_llm_agent.agent import (
                root_agent,
                gpt4o_agent,
                claude_agent,
                ollama_agent
            )
            assert root_agent is not None
            assert gpt4o_agent is not None
            assert claude_agent is not None
            assert ollama_agent is not None
        except Exception as e:
            pytest.fail(f"Agent 建立失敗：{e}")

    def test_tools_are_function_tools(self):
        """測試工具是否被正確包裝為 FunctionTools。"""
        from multi_llm_agent.agent import root_agent
        from google.adk.tools import FunctionTool

        for tool in root_agent.tools:
            assert isinstance(tool, FunctionTool)

    def test_tool_functions_are_callable(self):
        """測試所有工具函式是否都可呼叫。"""
        from multi_llm_agent.agent import calculate_square, get_weather, analyze_sentiment

        assert callable(calculate_square)
        assert callable(get_weather)
        assert callable(analyze_sentiment)
