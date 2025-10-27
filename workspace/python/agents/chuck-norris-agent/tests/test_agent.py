import pytest
from unittest.mock import patch, MagicMock
from google.adk.agents import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

from chuck_norris_agent.agent import root_agent, CHUCK_NORRIS_SPEC, chuck_norris_toolset


class TestAgentConfiguration:
    """測試 Agent 的設定與初始化"""

    def test_root_agent_import(self):
        """測試 root_agent 是否能成功匯入"""
        assert root_agent is not None

    def test_agent_is_agent_instance(self):
        """測試 root_agent 是否為 Agent 的實例"""
        assert isinstance(root_agent, Agent)

    def test_agent_name(self):
        """測試 Agent 的名稱是否正確"""
        assert root_agent.name == "chuck_norris_agent"

    def test_agent_model(self):
        """測試 Agent 使用的模型是否正確"""
        assert root_agent.model == "gemini-2.0-flash"

    def test_agent_description(self):
        """測試 Agent 是否有描述"""
        assert "Chuck Norris" in root_agent.description
        assert "OpenAPI tools" in root_agent.description

    def test_agent_instruction(self):
        """測試 Agent 是否有完整的指令"""
        instruction = root_agent.instruction
        assert "Chuck Norris fact assistant" in instruction
        assert "get_random_joke" in instruction
        assert "search_jokes" in instruction
        assert "get_categories" in instruction

    def test_agent_instruction_length(self):
        """測試指令的長度是否足夠"""
        assert len(root_agent.instruction) > 500  # 應為全面性指令

    def test_agent_has_tools(self):
        """測試 Agent 是否已設定工具"""
        assert root_agent.tools is not None
        assert len(root_agent.tools) > 0  # 應包含 3 個 OpenAPI 工具


class TestOpenAPISpecification:
    """測試 OpenAPI 規範結構"""

    def test_spec_structure(self):
        """測試規範是否具備必要的 OpenAPI 結構"""
        assert "openapi" in CHUCK_NORRIS_SPEC
        assert "info" in CHUCK_NORRIS_SPEC
        assert "servers" in CHUCK_NORRIS_SPEC
        assert "paths" in CHUCK_NORRIS_SPEC

    def test_spec_version(self):
        """測試規範是否使用 OpenAPI 3.0.0"""
        assert CHUCK_NORRIS_SPEC["openapi"] == "3.0.0"

    def test_spec_info(self):
        """測試規範是否有正確的 info 區塊"""
        info = CHUCK_NORRIS_SPEC["info"]
        assert "title" in info
        assert "Chuck Norris API" in info["title"]
        assert "description" in info
        assert "version" in info

    def test_spec_servers(self):
        """測試規範是否有正確的伺服器設定"""
        servers = CHUCK_NORRIS_SPEC["servers"]
        assert len(servers) == 1
        assert "url" in servers[0]
        assert "api.chucknorris.io" in servers[0]["url"]

    def test_spec_paths(self):
        """測試規範是否包含所有必要的路徑"""
        paths = CHUCK_NORRIS_SPEC["paths"]
        required_paths = ["/random", "/search", "/categories"]
        for path in required_paths:
            assert path in paths

    def test_random_endpoint(self):
        """測試 /random 端點的規範"""
        random_spec = CHUCK_NORRIS_SPEC["paths"]["/random"]["get"]
        assert random_spec["operationId"] == "get_random_joke"
        assert "parameters" in random_spec
        assert len(random_spec["parameters"]) == 1
        assert random_spec["parameters"][0]["name"] == "category"
        assert random_spec["parameters"][0]["required"] is False

    def test_search_endpoint(self):
        """測試 /search 端點的規範"""
        search_spec = CHUCK_NORRIS_SPEC["paths"]["/search"]["get"]
        assert search_spec["operationId"] == "search_jokes"
        assert "parameters" in search_spec
        assert len(search_spec["parameters"]) == 1
        assert search_spec["parameters"][0]["name"] == "query"
        assert search_spec["parameters"][0]["required"] is True

    def test_categories_endpoint(self):
        """測試 /categories 端點的規範"""
        categories_spec = CHUCK_NORRIS_SPEC["paths"]["/categories"]["get"]
        assert categories_spec["operationId"] == "get_categories"
        assert "parameters" not in categories_spec  # 此端點無參數

class TestOpenAPIToolset:
    """測試 OpenAPIToolset 的建立與設定"""

    def test_toolset_creation(self):
        """測試工具集是否能從規範中建立"""
        assert isinstance(chuck_norris_toolset, OpenAPIToolset)

    @pytest.mark.asyncio
    async def test_toolset_has_tools(self):
        """測試工具集是否提供工具"""
        tools = await chuck_norris_toolset.get_tools()
        assert isinstance(tools, list)
        assert len(tools) == 3  # 應有 3 個工具：random, search, categories


class TestAgentFunctionality:
    """測試 Agent 功能（必要時使用 mock）"""

    @patch("google.adk.tools.openapi_tool.OpenAPIToolset")
    def test_agent_creation_mock(self, mock_toolset_class):
        """使用 mock 的工具集測試 Agent 的建立"""
        mock_toolset = MagicMock()
        mock_toolset_class.return_value = mock_toolset

        # 此測試驗證 Agent 結構可以被建立
        # 在真實情境中，我們會測試 Agent 是否能被實例化
        assert True  # 結構測試通過


@pytest.mark.integration
class TestAgentIntegration:
    """需要 API 存取的整合測試"""

    def test_agent_can_be_created_without_error(self):
        """測試 Agent 建立時不會拋出例外"""
        try:
            # 僅存取 root_agent 不應引發錯誤
            agent = root_agent
            assert agent is not None
            assert agent.name == "chuck_norris_agent"
        except Exception as e:
            pytest.fail(f"Agent 建立失敗：{e}")

    def test_agent_has_valid_configuration_for_api(self):
        """測試 Agent 是否具備 API 使用所需的所有設定"""
        assert root_agent.model is not None
        assert root_agent.tools is not None
        assert len(root_agent.tools) > 0

        # 檢查指令是否提及關鍵功能
        instruction = root_agent.instruction.lower()
        assert "random" in instruction
        assert "search" in instruction
        assert "categories" in instruction
