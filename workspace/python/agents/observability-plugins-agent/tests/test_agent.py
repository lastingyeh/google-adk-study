"""
測試 Agent 設定與基本功能。
"""

import pytest
from observability_plugins_agent.agent import root_agent


class TestAgentConfig:
    """測試 Agent 的設定與安裝。"""

    def test_agent_name(self):
        """測試 Agent 是否擁有正確的名稱。"""
        # 驗證 Agent 名稱是否為 "observability_plugins_agent"
        assert root_agent.name == "observability_plugins_agent"

    def test_agent_model(self):
        """測試 Agent 是否使用正確的模型。"""
        # 驗證模型版本是否為 "gemini-2.5-flash"
        assert root_agent.model == "gemini-2.5-flash"

    def test_agent_description(self):
        """測試 Agent 是否有描述說明。"""
        # 驗證描述中包含 "observability" 或 "monitoring" 以及 "production"
        assert "observability" in root_agent.description.lower() or "monitoring" in root_agent.description.lower()
        assert "production" in root_agent.description.lower()

    def test_agent_instruction(self):
        """測試 Agent 是否有完整的指令說明。"""
        # 驗證指令中包含 "production" 或 "assistant" 以及 "helpful"
        assert "production" in root_agent.instruction.lower() or "assistant" in root_agent.instruction.lower()
        assert "helpful" in root_agent.instruction.lower()

    def test_agent_generate_config(self):
        """測試 Agent 是否有生成配置。"""
        # 驗證生成內容配置是否存在，且參數正確 (temperature=0.5, max_output_tokens=1024)
        assert root_agent.generate_content_config is not None
        assert root_agent.generate_content_config.temperature == 0.5
        assert root_agent.generate_content_config.max_output_tokens == 1024
