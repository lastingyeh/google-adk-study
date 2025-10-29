"""
測試匯入功能
"""

import pytest


class TestImports:
    """測試所有必要的匯入是否正常運作"""

    def test_import_agent_module(self):
        """測試匯入 agent 模組"""
        from mcp_agent import agent

        assert agent is not None

    def test_import_root_agent(self):
        """測試匯入 root_agent"""
        from mcp_agent import root_agent

        assert root_agent is not None

    def test_import_create_function(self):
        """測試匯入建立函式"""
        from mcp_agent.agent import create_mcp_filesystem_agent

        assert create_mcp_filesystem_agent is not None

    def test_import_document_organizer(self):
        """測試匯入文件整理器"""
        from mcp_agent.document_organizer import create_document_organizer_agent

        assert create_document_organizer_agent is not None

    def test_import_adk_core(self):
        """測試匯入 ADK 核心模組"""
        from google.adk.agents import Agent
        from google.adk import Runner

        assert Agent is not None
        assert Runner is not None

    def test_import_mcp_tools(self):
        """測試匯入 MCP 工具"""
        from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams

        assert MCPToolset is not None
        assert StdioConnectionParams is not None

    def test_import_mcp_connection_types(self):
        """測試匯入 MCP 連線類型 (ADK 1.16.0+)"""
        from google.adk.tools.mcp_tool import (
            SseConnectionParams,
            StreamableHTTPConnectionParams,
        )

        assert SseConnectionParams is not None
        assert StreamableHTTPConnectionParams is not None

    def test_import_auth_credential(self):
        """測試匯入驗證憑證類別 (ADK 1.16.0+)"""
        try:
            from google.adk.auth.auth_credential import (
                AuthCredential,
                AuthCredentialTypes,
            )

            assert AuthCredential is not None
            assert AuthCredentialTypes is not None
        except ImportError:
            pytest.skip("此 ADK 版本中未提供驗證憑證類別")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
