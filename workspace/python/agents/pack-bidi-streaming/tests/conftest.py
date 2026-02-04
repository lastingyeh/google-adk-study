"""
Pytest 配置與共用 fixtures

此檔案包含 pack-bidi-streaming 專案的測試配置與共用的測試 fixtures。
"""

import os
from unittest.mock import Mock

import pytest


def pytest_configure(config):
    """配置 pytest。"""
    # 註冊自訂標記
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
def mock_tool_context():
    """模擬 ToolContext。"""
    context = Mock()
    context.state = {}
    return context


@pytest.fixture(autouse=True)
def reset_environment():
    """每個測試後重置環境。"""
    # 儲存原始環境變數
    original_env = os.environ.copy()

    yield

    # 恢復原始環境變數
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_feedback_data():
    """提供測試用的 Feedback 資料。"""
    return {
        "score": 5,
        "text": "Excellent response",
        "type": "rating",
        "service_name": "bidi_demo",
    }


@pytest.fixture
def sample_request_data():
    """提供測試用的 Request 資料。"""
    from google.genai.types import Content

    return {
        "message": Content(parts=[{"text": "Hello, how can you help?"}]),
        "events": [],
    }
