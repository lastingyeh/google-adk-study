"""
測試代理程式的設定與基本功能。

這個檔案包含一系列的測試，旨在確保代理程式的配置正確，
並且其核心屬性（如名稱、模型、描述等）符合預期。
"""

import pytest
from artifact_agent.agent import root_agent


class TestAgentConfig:
    """測試代理程式的設定與初始化。"""

    def test_agent_name(self):
        """測試代理程式是否有正確的名稱。"""
        assert root_agent.name == "artifact_agent"

    def test_agent_model(self):
        """測試代理程式是否使用正確的模型。"""
        assert root_agent.model == "gemini-1.5-flash"

    def test_agent_description(self):
        """測試代理程式是否有描述。"""
        assert "artifact" in root_agent.description.lower()
        assert "document" in root_agent.description.lower()

    def test_agent_instruction(self):
        """測試代理程式是否有全面的指令。"""
        assert "artifacts" in root_agent.instruction.lower()
        assert "document" in root_agent.instruction.lower()
        assert "versioning" in root_agent.instruction.lower()

    def test_agent_tools(self):
        """測試代理程式是否具備預期的工具。"""
        tool_names = [tool.name for tool in root_agent.tools if hasattr(tool, 'name')]
        # 檢查是否內建 load_artifacts_tool
        assert any("load_artifacts" in name for name in tool_names)

    def test_agent_has_multiple_tools(self):
        """測試代理程式是否設定了多個工具。"""
        assert len(root_agent.tools) >= 6  # 應至少有 6 個工具
