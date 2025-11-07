# 教學 01: Hello World Agent - Agent 測試
# 驗證 Agent 的設定與基本功能

import pytest
from unittest.mock import patch, MagicMock


class TestAgentConfiguration:
    """測試 Agent 是否正確設定。"""

    def test_root_agent_import(self):
        """測試 root_agent 是否可以被匯入。"""
        from hello_agent.agent import root_agent
        assert root_agent is not None, "root_agent 應該可以被匯入"

    def test_agent_is_agent_instance(self):
        """測試 root_agent 是否為 Agent 的一個實例。"""
        from hello_agent.agent import root_agent
        from google.adk.agents import Agent

        assert isinstance(root_agent, Agent), "root_agent 應該是 Agent 的一個實例"

    def test_agent_name(self):
        """測試 Agent 是否有正確的名稱。"""
        from hello_agent.agent import root_agent

        assert hasattr(root_agent, 'name'), "Agent 應該有名稱屬性"
        assert root_agent.name == "hello_assistant", "Agent 的名稱不正確"

    def test_agent_model(self):
        """測試 Agent 是否有正確的模型。"""
        from hello_agent.agent import root_agent

        assert hasattr(root_agent, 'model'), "Agent 應該有模型屬性"
        assert root_agent.model == "gemini-2.0-flash", "Agent 的模型不正確"

    def test_agent_description(self):
        """測試 Agent 是否有描述。"""
        from hello_agent.agent import root_agent

        assert hasattr(root_agent, 'description'), "Agent 應該有描述屬性"
        assert "friendly AI assistant" in root_agent.description, "Agent 的描述內容不正確"

    def test_agent_instruction(self):
        """測試 Agent 是否有指令。"""
        from hello_agent.agent import root_agent

        assert hasattr(root_agent, 'instruction'), "Agent 應該有指令屬性"
        assert "warm and helpful assistant" in root_agent.instruction, "Agent 的指令內容不正確"
        assert "Greet users enthusiastically" in root_agent.instruction, "Agent 的指令內容不正確"

    def test_agent_instruction_length(self):
        """測試指令的長度是否合理。"""
        from hello_agent.agent import root_agent

        instruction = root_agent.instruction
        assert len(instruction) > 50, "指令長度應足夠"
        assert len(instruction) < 1000, "指令長度不應過長"


class TestAgentFunctionality:
    """測試基本的 Agent 功能（模擬）。"""

    @patch('google.adk.agents.Agent')
    def test_agent_creation_mock(self, mock_agent_class):
        """使用模擬的 Agent 類別測試 Agent 的建立。"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # 重新匯入以觸發建立
        import importlib
        import hello_agent.agent
        importlib.reload(hello_agent.agent)

        # 驗證 Agent 是否被正確的參數呼叫
        mock_agent_class.assert_called_once()
        call_args = mock_agent_class.call_args

        assert call_args[1]['name'] == 'hello_assistant', "傳遞給 Agent 的名稱不正確"
        assert call_args[1]['model'] == 'gemini-2.0-flash', "傳遞給 Agent 的模型不正確"
        assert 'friendly' in call_args[1]['description'], "傳遞給 Agent 的描述不正確"
        assert 'warm and helpful' in call_args[1]['instruction'], "傳遞給 Agent 的指令不正確"


@pytest.mark.integration
class TestAgentIntegration:
    """需要真實 ADK 的整合測試（可選）。"""

    def test_agent_can_be_created_without_error(self):
        """測試 Agent 是否可以在不引發例外的情況下被建立。"""
        try:
            from hello_agent.agent import root_agent
            # 如果沒有例外，表示基本建立成功
            assert True
        except Exception as e:
            pytest.fail(f"Agent 建立失敗: {e}")

    @pytest.mark.skipif(
        not hasattr(pytest, 'env') or not pytest.env.get('GOOGLE_API_KEY'),
        reason="需要 GOOGLE_API_KEY 環境變數"
    )
    def test_agent_has_valid_configuration_for_api(self):
        """測試 Agent 的設定對於 API 呼叫是否有效。"""
        from hello_agent.agent import root_agent

        # 這些屬性應該存在且合理
        assert hasattr(root_agent, 'model'), "Agent 應有模型屬性"
        assert hasattr(root_agent, 'instruction'), "Agent 應有指令屬性"
        assert len(root_agent.instruction) > 20, "指令長度應足夠"

        # 模型應該是已知的 Gemini 模型
        valid_models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
        assert root_agent.model in valid_models, "Agent 的模型不是有效的 Gemini 模型"
