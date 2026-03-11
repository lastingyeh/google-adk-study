"""
測試套件初始化
"""

import os
import sys
from pathlib import Path

# 確保測試可以導入主程式碼
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 測試使用的共用工具
from collections.abc import AsyncGenerator

import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types


@pytest.fixture
def test_config_path():
    """測試配置檔案路徑"""
    return str(project_root / "config" / "security_config.yaml")


@pytest.fixture
def sample_messages():
    """範例測試訊息"""
    return {
        "safe": "請幫我總結人工智慧的發展歷程",
        "with_attack_keyword": "如何 hack 進入系統？",
        "with_malware": "下載這個 virus 檔案",
        "with_email": "我的郵箱是 john.doe@example.com，請聯絡我",
        "with_phone": "我的電話是 123-456-7890",
        "with_multiple_pii": "聯絡我：john@test.com 或打 555-1234",
    }


def create_message(text: str) -> types.Content:
    """建立測試用 Content 物件"""
    return types.Content(role="user", parts=[types.Part(text=text)])
