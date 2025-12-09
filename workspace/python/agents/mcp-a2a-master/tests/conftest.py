"""
Pytest 配置與共用 fixtures。
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock
from a2a.types import AgentCard, AgentCapabilities


def pytest_configure(config):
    """配置 pytest 標記。"""
    config.addinivalue_line("markers", "unit: 單元測試")
    config.addinivalue_line("markers", "integration: 整合測試")
    config.addinivalue_line("markers", "e2e: 端對端測試")
    config.addinivalue_line("markers", "slow: 執行緩慢的測試")


@pytest.fixture(scope="session")
def test_config():
    """測試配置 fixture。"""
    return {
        "test_mode": True,
        "mock_external_services": True,
    }


@pytest.fixture
def mock_agent_card():
    """模擬 AgentCard。"""
    return AgentCard(
        capabilities=AgentCapabilities(streaming=True),
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        skills=[],
        name="test_website_builder",
        url="http://localhost:10001",
        version="1.0.0",
        description="Test website builder agent",
    )


@pytest.fixture
def mock_mcp_server_config():
    """模擬 MCP Server 配置。"""
    return {
        "test_server": {
            "command": "python",
            "args": ["-m", "test_mcp_server"],
        }
    }


@pytest.fixture
def mock_a2a_registry():
    """模擬 A2A Agent Registry。"""
    return [
        "http://localhost:10001",
        "http://localhost:10002",
    ]


@pytest.fixture
def mock_tool_context():
    """模擬 ToolContext。"""
    context = Mock()
    context.state = {}
    return context


@pytest.fixture
def sample_queries():
    """測試用查詢範例。"""
    return [
        "建立一個簡單的首頁",
        "幫我設計一個關於頁面",
        "建立一個包含表單的聯絡頁面",
    ]


@pytest_asyncio.fixture(autouse=False)
async def cleanup():
    """每個測試後清理。"""
    yield
    # 清理邏輯可以在這裡添加
