"""
Pytest 配置與共用 fixtures。

此檔案提供測試的全域配置和可重複使用的 fixtures。
"""

import pytest
import os
import sys


def pytest_configure(config):
    """配置 pytest。"""
    # 註冊自訂標記
    config.addinivalue_line("markers", "unit: 單元測試")
    config.addinivalue_line("markers", "integration: 整合測試")
    config.addinivalue_line("markers", "skill: 技能相關測試")
    config.addinivalue_line("markers", "slow: 執行緩慢的測試")


@pytest.fixture(scope="session")
def test_config():
    """測試配置 fixture。"""
    return {
        "test_mode": True,
        "mock_external_services": True,
    }


@pytest.fixture(scope="session")
def project_root():
    """取得專案根目錄。"""
    # 從 tests 目錄往上一層
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def skills_dir(project_root):
    """取得技能目錄路徑。"""
    return os.path.join(project_root, 'skills_agent', 'skills')


@pytest.fixture
def weather_skill_dir(skills_dir):
    """取得天氣技能目錄路徑。"""
    return os.path.join(skills_dir, 'weather-skill')


@pytest.fixture(autouse=True)
def reset_environment():
    """每個測試後重置環境。"""
    yield
    # 清理邏輯（如有需要）
    pass


@pytest.fixture
def mock_skill():
    """建立模擬的技能物件用於測試。"""
    from google.adk.skills.models import Skill, Frontmatter, Resources

    return Skill(
        frontmatter=Frontmatter(
            name="test-skill",
            description="A test skill for testing purposes",
        ),
        instructions="Step 1: Do something. Step 2: Do something else.",
        resources=Resources(
            references={
                "test_reference.txt": "Test content",
            },
        ),
    )


# 設定 Python 路徑以確保可以匯入專案模組
def pytest_sessionstart(session):
    """在測試開始前執行。"""
    # 將專案根目錄加入 Python 路徑
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
