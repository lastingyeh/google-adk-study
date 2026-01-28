"""
Pytest 配置與共用 fixtures

提供測試執行的全域配置和共用的 fixture。
"""

import pytest
import os


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
    from unittest.mock import Mock

    context = Mock()
    context.state = {}
    context._invocation_context = Mock()
    context._invocation_context.session = Mock()
    context._invocation_context.session.id = "test-session-id"
    return context


@pytest.fixture
def mock_storage_client():
    """模擬 Google Cloud Storage 客戶端。"""
    from unittest.mock import Mock

    client = Mock()
    bucket = Mock()
    client.bucket.return_value = bucket
    return client


@pytest.fixture
def mock_logging_client():
    """模擬 Google Cloud Logging 客戶端。"""
    from unittest.mock import Mock

    client = Mock()
    logger = Mock()
    client.logger.return_value = logger
    return client


@pytest.fixture
def sample_content():
    """建立測試用的 Content 物件。"""
    from google.genai.types import Content, Part

    return Content(
        role="user",
        parts=[Part.from_text(text="Test message")],
    )


@pytest.fixture
def sample_request(sample_content):
    """建立測試用的 Request 物件。"""
    from app.utils.typing import Request

    return Request(
        message=sample_content,
        events=[],
        user_id="test-user-123",
        session_id="test-session-456",
    )


@pytest.fixture
def sample_feedback():
    """建立測試用的 Feedback 物件。"""
    from app.utils.typing import Feedback

    return Feedback(
        score=5,
        text="Great result",
        invocation_id="test-invocation-123",
        user_id="test-user-456",
    )


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
def mock_vertexai_init():
    """模擬 Vertex AI 初始化。"""
    from unittest.mock import patch

    with patch("vertexai.init") as mock:
        yield mock


@pytest.fixture
def mock_image_generation_model():
    """模擬影像生成模型。"""
    from unittest.mock import Mock

    model = Mock()
    response = Mock()
    response.images = []
    model.generate_images.return_value = response
    return model


@pytest.fixture
def mock_video_generation_client():
    """模擬影片生成客戶端。"""
    from unittest.mock import Mock

    client = Mock()
    operation = Mock()
    operation.done = True
    operation.response = False
    client.models.generate_videos.return_value = operation
    client.operations.get.return_value = operation
    return client


@pytest.fixture(scope="session")
def test_environment_variables():
    """設定測試環境變數。"""
    test_env = {
        "GOOGLE_CLOUD_PROJECT": "test-project-123",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        "GOOGLE_CLOUD_BUCKET_NAME": "test-bucket",
    }
    return test_env


# 測試資料 fixtures

@pytest.fixture
def sample_story():
    """測試用的故事文本。"""
    return """
    Once upon a time, in a magical forest, there lived a brave hero.
    The hero embarked on a quest to save the kingdom.
    """


@pytest.fixture
def sample_screenplay():
    """測試用的劇本文本。"""
    return """
    Scene 1: The Magical Forest

    NARRATOR (voiceover)
      Once upon a time...

    HERO (determined)
      I must save the kingdom!
    """


@pytest.fixture
def sample_storyboard_prompt():
    """測試用的分鏡圖提示詞。"""
    return "A brave hero standing in a magical forest at sunset"


@pytest.fixture
def sample_video_prompt():
    """測試用的影片提示詞。"""
    return "A cinematic shot of a hero walking through a magical forest"
