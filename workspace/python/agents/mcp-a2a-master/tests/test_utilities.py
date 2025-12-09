"""
測試 Utilities 模組的功能。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
import httpx
from pathlib import Path


class TestFileLoader:
    """測試 file_loader 工具。"""

    def test_load_instructions_file_success(self):
        """測試成功載入檔案。

        重點說明：
        1. 匯入 load_instructions_file 函式
        2. 呼叫函式載入存在的檔案
        3. 驗證回傳結果不為 None
        4. 驗證回傳結果為字串且長度大於 0
        """
        from utilities.common.file_loader import load_instructions_file

        # 測試載入實際存在的檔案
        result = load_instructions_file("agents/host_agent/description.txt")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_load_instructions_file_not_found(self):
        """測試檔案不存在時的行為。

        重點說明：
        1. 匯入 load_instructions_file 函式
        2. 呼叫函式載入不存在的檔案
        3. 驗證回傳結果為預設值
        """
        from utilities.common.file_loader import load_instructions_file

        result = load_instructions_file("nonexistent_file.txt", default="default_value")
        assert result == "default_value"

    def test_load_instructions_file_with_default(self):
        """測試使用預設值。

        重點說明：
        1. 匯入 load_instructions_file 函式
        2. 呼叫函式載入不存在的檔案並指定預設值
        3. 驗證回傳結果為指定的預設值
        """
        from utilities.common.file_loader import load_instructions_file

        result = load_instructions_file(
            "definitely_not_exists.txt", default="fallback"
        )
        assert result == "fallback"


class TestAgentConnector:
    """測試 AgentConnector 類別。"""

    def test_connector_initialization(self, mock_agent_card):
        """測試 AgentConnector 初始化。

        重點說明：
        1. 匯入 AgentConnector
        2. 使用 mock_agent_card 初始化 AgentConnector
        3. 驗證實例建立成功且 agent_card 屬性正確
        """
        from utilities.a2a.agent_connect import AgentConnector

        connector = AgentConnector(agent_card=mock_agent_card)
        assert connector is not None
        assert connector.agent_card == mock_agent_card

    def test_connector_with_valid_agent_card(self, mock_agent_card):
        """測試使用有效的 AgentCard 初始化。

        重點說明：
        1. 建立 AgentConnector 實例
        2. 驗證 agent_card 的 name 和 url 屬性是否正確
        """
        from utilities.a2a.agent_connect import AgentConnector

        connector = AgentConnector(agent_card=mock_agent_card)
        assert connector.agent_card.name == "test_website_builder"
        assert connector.agent_card.url == "http://localhost:10001"

    @pytest.mark.asyncio
    async def test_send_task_with_mocked_client(self, mock_agent_card):
        """測試 send_task（使用 mock）。

        重點說明：
        1. 建立 AgentConnector 實例
        2. Mock httpx.AsyncClient 和 A2AClient
        3. 設定 mock 回應
        4. 呼叫 connector.send_task()
        5. 驗證回傳結果不為 None
        """
        from utilities.a2a.agent_connect import AgentConnector

        connector = AgentConnector(agent_card=mock_agent_card)

        # Mock httpx.AsyncClient 和 A2AClient
        with patch("utilities.a2a.agent_connect.httpx.AsyncClient") as mock_httpx:
            with patch("utilities.a2a.agent_connect.A2AClient") as mock_a2a_client:
                # 設定 mock 回應
                mock_response = Mock()
                mock_response.text = "Test response"

                mock_client_instance = AsyncMock()
                mock_a2a_client.return_value.send_message = AsyncMock(
                    return_value=mock_response
                )

                # 測試 send_task
                # 注意：這個測試需要根據實際的 send_task 實作調整
                result = await connector.send_task(
                    message="Test message", session_id="test-session"
                )

                assert result is not None


class TestAgentDiscovery:
    """測試 AgentDiscovery 類別。"""

    def test_discovery_initialization(self):
        """測試 AgentDiscovery 初始化。

        重點說明：
        1. 匯入 AgentDiscovery
        2. 建立實例
        3. 驗證實例建立成功
        """
        from utilities.a2a.agent_discovery import AgentDiscovery

        discovery = AgentDiscovery()
        assert discovery is not None

    def test_discovery_with_custom_registry(self, tmp_path):
        """測試使用自訂 registry 檔案。

        重點說明：
        1. 建立臨時 registry 檔案
        2. 寫入測試資料
        3. 使用自訂 registry 檔案路徑初始化 AgentDiscovery
        4. 驗證實例建立成功
        """
        from utilities.a2a.agent_discovery import AgentDiscovery

        # 建立臨時 registry 檔案
        registry_file = tmp_path / "test_registry.json"
        registry_data = ["http://localhost:10001", "http://localhost:10002"]
        registry_file.write_text(json.dumps(registry_data))

        discovery = AgentDiscovery(registry_file=str(registry_file))
        assert discovery is not None

    def test_load_registry_success(self):
        """測試載入 registry 成功。

        重點說明：
        1. 建立 AgentDiscovery 實例
        2. 呼叫 _load_registry() 方法
        3. 驗證回傳結果為列表
        """
        from utilities.a2a.agent_discovery import AgentDiscovery

        discovery = AgentDiscovery()
        registry = discovery._load_registry()

        assert isinstance(registry, list)

    @pytest.mark.asyncio
    async def test_list_agent_cards_with_mock(self):
        """測試 list_agent_cards（使用 mock）。

        重點說明：
        1. 建立 AgentDiscovery 實例
        2. Mock _fetch_agent_card 方法回傳模擬的 agent card
        3. (此測試目前尚未完成完整的 assertion，需根據實際情況補充)
        """
        from utilities.a2a.agent_discovery import AgentDiscovery
        from a2a.types import AgentCard

        discovery = AgentDiscovery()

        # Mock _fetch_agent_card
        with patch.object(
            discovery, "_fetch_agent_card", new_callable=AsyncMock
        ) as mock_fetch:
            from a2a.types import AgentCapabilities

            mock_card = AgentCard(
                name="test_agent",
                url="http://localhost:10001",
                version="1.0.0",
                description="Test",
                capabilities=AgentCapabilities(streaming=True),
                defaultInputModes=["text/plain"],
                defaultOutputModes=["text/plain"],
                skills=[],
            )
            mock_fetch.return_value = mock_card

            # 測試 list_agent_cards
            # 注意：這個測試需要根據實際的實作調整


class TestMCPDiscovery:
    """測試 MCPDiscovery 類別。"""

    def test_discovery_initialization(self):
        """測試 MCPDiscovery 初始化。

        重點說明：
        1. 匯入 MCPDiscovery
        2. 建立實例
        3. 驗證實例建立成功
        """
        from utilities.mcp.mcp_discovery import MCPDiscovery

        discovery = MCPDiscovery()
        assert discovery is not None

    def test_discovery_with_custom_config(self, tmp_path, mock_mcp_server_config):
        """測試使用自訂配置檔案。

        重點說明：
        1. 建立臨時配置檔案
        2. 寫入測試配置資料
        3. 使用自訂配置檔案路徑初始化 MCPDiscovery
        4. 驗證實例建立成功
        """
        from utilities.mcp.mcp_discovery import MCPDiscovery

        # 建立臨時配置檔案
        config_file = tmp_path / "test_mcp_config.json"
        config_file.write_text(json.dumps({"mcpServers": mock_mcp_server_config}))

        discovery = MCPDiscovery(config_file=str(config_file))
        assert discovery is not None

    def test_load_config_success(self):
        """測試載入配置成功。

        重點說明：
        1. 建立 MCPDiscovery 實例
        2. 呼叫 _load_config() 方法
        3. 驗證回傳結果為字典
        """
        from utilities.mcp.mcp_discovery import MCPDiscovery

        discovery = MCPDiscovery()
        config = discovery._load_config()

        assert isinstance(config, dict)

    def test_list_servers_returns_dict(self):
        """測試 list_servers 回傳字典。

        重點說明：
        1. 建立 MCPDiscovery 實例
        2. 呼叫 list_servers() 方法
        3. 驗證回傳結果為字典
        """
        from utilities.mcp.mcp_discovery import MCPDiscovery

        discovery = MCPDiscovery()
        servers = discovery.list_servers()

        assert isinstance(servers, dict)


class TestMCPConnector:
    """測試 MCPConnector 類別。"""

    def test_connector_initialization(self):
        """測試 MCPConnector 初始化。

        重點說明：
        1. 匯入 MCPConnector
        2. 建立實例
        3. 驗證實例建立成功
        4. 驗證 tools 屬性為列表
        """
        from utilities.mcp.mcp_connect import MCPConnector

        connector = MCPConnector()
        assert connector is not None
        assert isinstance(connector.tools, list)

    def test_connector_with_custom_config(self, tmp_path, mock_mcp_server_config):
        """測試使用自訂配置初始化。

        重點說明：
        1. 建立臨時配置檔案
        2. 寫入測試配置資料
        3. 使用自訂配置檔案路徑初始化 MCPConnector
        4. 驗證實例建立成功
        """
        from utilities.mcp.mcp_connect import MCPConnector

        # 建立臨時配置檔案
        config_file = tmp_path / "test_mcp_config.json"
        config_file.write_text(json.dumps({"mcpServers": mock_mcp_server_config}))

        connector = MCPConnector(config_file=str(config_file))
        assert connector is not None

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_get_tools_returns_list(self):
        """測試 get_tools 回傳列表。

        重點說明：
        1. 建立 MCPConnector 實例
        2. 直接存取 tools 屬性 (此處測試名稱與實作略有不同，但意圖是驗證 tools)
        3. 驗證 tools 為列表型別
        """
        from utilities.mcp.mcp_connect import MCPConnector

        connector = MCPConnector()

        # 不實際載入工具（避免連接真實 MCP Server）
        # 只測試方法存在且回傳型別正確
        tools = connector.tools
        assert isinstance(tools, list)

    @pytest.mark.asyncio
    async def test_load_all_tools_with_mock(self):
        """測試 _load_all_tools（使用 mock）。

        重點說明：
        1. 建立 MCPConnector 實例
        2. Mock discovery.list_servers 方法回傳空字典
        3. 呼叫 _load_all_tools()
        4. 驗證 tools 屬性仍為列表型別
        """
        from utilities.mcp.mcp_connect import MCPConnector

        connector = MCPConnector()

        # Mock MCPDiscovery
        with patch.object(connector.discovery, "list_servers") as mock_list_servers:
            mock_list_servers.return_value = {}

            # 測試載入工具（空的伺服器列表）
            await connector._load_all_tools()

            assert isinstance(connector.tools, list)
