# 教程 20：YAML 設定 - 代理測試
# 驗證 YAML 設定載入與代理設置

import pytest
from unittest.mock import patch


class TestYAMLConfiguration:
    """測試 YAML 設定是否正確載入。"""

    def test_config_file_exists(self):
        """測試 root_agent.yaml 是否存在。"""
        import os
        config_path = 'customer_support/root_agent.yaml'
        assert os.path.exists(config_path), "customer_support/root_agent.yaml 應該存在"

    def test_config_agent_loading(self):
        """測試是否能從 YAML 設定載入代理。"""
        try:
            from google.adk.agents import config_agent_utils
            agent = config_agent_utils.from_config('customer_support/root_agent.yaml')
            assert agent is not None
        except Exception as e:
            pytest.fail(f"從 YAML 載入代理失敗：{e}")

    def test_agent_basic_properties(self):
        """測試載入的代理是否具有正確的基本屬性。"""
        from google.adk.agents import config_agent_utils

        agent = config_agent_utils.from_config('customer_support/root_agent.yaml')

        # 驗證代理名稱
        assert hasattr(agent, 'name')
        assert agent.name == "customer_support"

        # 驗證使用的模型
        assert hasattr(agent, 'model')
        assert agent.model == "gemini-2.0-flash"

        # 驗證描述內容
        assert hasattr(agent, 'description')
        assert "customer support agent" in agent.description.lower()

    def test_agent_instruction(self):
        """測試代理是否具有適當的指令。"""
        from google.adk.agents import config_agent_utils

        agent = config_agent_utils.from_config('customer_support/root_agent.yaml')

        assert hasattr(agent, 'instruction')
        instruction = agent.instruction
        assert "customer support agent" in instruction.lower()
        assert "available tools" in instruction.lower()

    def test_agent_has_no_sub_agents(self):
        """測試代理是否沒有子代理（單一代理設定）。"""
        from google.adk.agents import config_agent_utils

        agent = config_agent_utils.from_config('customer_support/root_agent.yaml')

        assert hasattr(agent, 'sub_agents')
        assert len(agent.sub_agents) == 0  # 單一代理設定

    def test_agent_has_tools(self):
        """測試代理是否已設定工具。"""
        from google.adk.agents import config_agent_utils

        agent = config_agent_utils.from_config('customer_support/root_agent.yaml')

        assert hasattr(agent, 'tools')
        assert len(agent.tools) == 11  # 所有客戶支援工具

    def test_agent_tools_are_functions(self):
        """測試代理工具是否為可呼叫的函式。"""
        from google.adk.agents import config_agent_utils

        agent = config_agent_utils.from_config('customer_support/root_agent.yaml')

        assert hasattr(agent, 'tools')
        for tool in agent.tools:
            assert callable(tool)


class TestConfigurationValidation:
    """測試設定驗證與錯誤處理。"""

    def test_invalid_config_path(self):
        """測試不存在設定檔的錯誤處理。"""
        from google.adk.agents import config_agent_utils

        with pytest.raises(Exception):
            config_agent_utils.from_config('non_existent.yaml')

    @patch('google.adk.agents.config_agent_utils.from_config')
    def test_config_loading_error_handling(self, mock_from_config):
        """測試設定載入過程中的錯誤處理。"""
        mock_from_config.side_effect = Exception("YAML parsing error")

        with pytest.raises(Exception):
            from google.adk.agents import config_agent_utils
            config_agent_utils.from_config('customer_support/root_agent.yaml')


@pytest.mark.integration
class TestAgentIntegration:
    """需要真實 ADK 的整合測試（選填）。"""

    def test_agent_creation_without_error(self):
        """測試代理建立時是否未引發異常。"""
        try:
            from google.adk.agents import config_agent_utils
            agent = config_agent_utils.from_config('customer_support/root_agent.yaml')
            # 如果執行到此處無異常，表示基本建立成功
            assert True
        except Exception as e:
            pytest.fail(f"代理建立失敗：{e}")

    @pytest.mark.skipif(
        not hasattr(pytest, 'env') or not pytest.env.get('GOOGLE_API_KEY'),
        reason="需要 GOOGLE_API_KEY 環境變數"
    )
    def test_agent_has_valid_configuration_for_api(self):
        """測試代理設定是否對 API 呼叫有效。"""
        from google.adk.agents import config_agent_utils

        agent = config_agent_utils.from_config('root_agent.yaml')

        # 這些屬性應該存在且合理
        assert hasattr(agent, 'model')
        assert hasattr(agent, 'instruction')
        assert len(agent.instruction) > 20

        # 模型應為已知的 Gemini 模型
        valid_models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
        assert agent.model in valid_models

        # 應無子代理（單一代理設定）
        assert hasattr(agent, 'sub_agents')
        assert len(agent.sub_agents) == 0
