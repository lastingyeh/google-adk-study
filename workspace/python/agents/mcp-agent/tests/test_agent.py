"""
測試 Agent 的設定與功能
"""

import pytest
import os
import tempfile
from mcp_agent.agent import create_mcp_filesystem_agent, root_agent


class TestAgentConfig:
    """測試 Agent 的基本設定"""

    def test_root_agent_exists(self):
        """測試 root_agent 變數是否存在"""
        assert root_agent is not None

    def test_agent_has_correct_model(self):
        """測試 Agent 是否使用正確的模型"""
        assert root_agent.model == "gemini-2.0-flash-exp"

    def test_agent_has_name(self):
        """測試 Agent 是否有正確的名稱"""
        assert root_agent.name == "mcp_file_assistant"

    def test_agent_has_description(self):
        """測試 Agent 是否有描述"""
        assert root_agent.description is not None
        assert len(root_agent.description) > 0

    def test_agent_has_instruction(self):
        """測試 Agent 是否有指令"""
        assert root_agent.instruction is not None
        assert "filesystem" in root_agent.instruction.lower()

    def test_agent_has_tools(self):
        """測試 Agent 是否已設定工具"""
        assert root_agent.tools is not None
        assert len(root_agent.tools) > 0


class TestAgentCreation:
    """測試 Agent 的建立函式"""

    def test_create_agent_with_default_directory(self):
        """測試使用預設目錄建立 Agent"""
        agent = create_mcp_filesystem_agent()
        assert agent is not None
        assert agent.name == "mcp_file_assistant"

    def test_create_agent_with_custom_directory(self):
        """測試使用自訂目錄建立 Agent"""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = create_mcp_filesystem_agent(tmpdir)
            assert agent is not None

    def test_create_agent_with_invalid_directory(self):
        """測試使用不存在的目錄建立 Agent 會引發錯誤"""
        with pytest.raises(ValueError, match="Directory does not exist"):
            create_mcp_filesystem_agent("/nonexistent/directory/path")


class TestMCPToolset:
    """測試 MCP 工具集的設定"""

    def test_mcp_imports_available(self):
        """測試 MCP 的匯入是否可用"""
        from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams

        assert McpToolset is not None
        assert StdioConnectionParams is not None

    def test_stdio_connection_params(self):
        """測試 StdioConnectionParams 是否可以被建立"""
        from google.adk.tools.mcp_tool import StdioConnectionParams
        from mcp.client.stdio import StdioServerParameters

        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        )
        params = StdioConnectionParams(server_params=server_params)
        assert params is not None
        assert params.server_params.command == "npx"

    @pytest.mark.skipif(
        os.environ.get("SKIP_MCP_INTEGRATION") == "true",
        reason="MCP 整合測試已跳過 (需要 Node.js 和 npx)",
    )
    def test_mcp_toolset_creation(self):
        """測試 MCPToolset 是否可以透過 StdioConnectionParams 建立"""
        from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
        from mcp.client.stdio import StdioServerParameters

        with tempfile.TemporaryDirectory() as tmpdir:
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", tmpdir],
            )
            mcp_tools = McpToolset(
                connection_params=StdioConnectionParams(server_params=server_params)
            )
            assert mcp_tools is not None


class TestADKVersion:
    """測試 ADK 版本的相容性"""

    def test_adk_1_16_features(self):
        """測試 ADK 1.16.0+ 的功能是否可用"""
        # 測試 SSE 連線參數
        from google.adk.tools.mcp_tool import SseConnectionParams

        assert SseConnectionParams is not None

        # 測試 HTTP 連線參數
        from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams

        assert StreamableHTTPConnectionParams is not None

    def test_sse_connection_params(self):
        """測試 SseConnectionParams 是否可以被建立"""
        from google.adk.tools.mcp_tool import SseConnectionParams

        params = SseConnectionParams(
            url="https://api.example.com/sse", timeout=30.0, sse_read_timeout=300.0
        )
        assert params is not None
        assert params.url == "https://api.example.com/sse"

    def test_http_connection_params(self):
        """測試 StreamableHTTPConnectionParams 是否可以被建立"""
        from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams

        params = StreamableHTTPConnectionParams(
            url="https://api.example.com/http", timeout=30.0, sse_read_timeout=300.0
        )
        assert params is not None
        assert params.url == "https://api.example.com/http"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
