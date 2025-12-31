"""pytest 共用配置與 fixtures

此檔案提供所有測試共用的 fixtures，避免在每個測試文件中重複定義。
"""
import pytest
from google import genai
from dotenv import load_dotenv
import os
from backend.services.session_service import SessionService

# 載入環境變數
load_dotenv()


@pytest.fixture(scope="session")
def api_key():
    """提供 Google API Key"""
    key = os.getenv('GOOGLE_API_KEY')
    if not key:
        pytest.skip("GOOGLE_API_KEY 未設定")
    return key


@pytest.fixture(scope="session")
def model_name():
    """提供模型名稱"""
    return os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')


@pytest.fixture
def genai_client(api_key):
    """提供 GenAI Client fixture
    
    每個測試都會獲得一個新的 client 實例
    """
    return genai.Client(api_key=api_key)


@pytest.fixture
def session_service():
    """提供 SessionService fixture (使用記憶體資料庫)
    
    每個測試都會獲得一個全新的記憶體資料庫，確保測試隔離
    """
    service = SessionService(database_url="sqlite:///:memory:")
    yield service
    # 清理
    service.engine.dispose()


@pytest.fixture
def sample_conversation_id(session_service):
    """建立測試用對話並返回 ID
    
    這個 fixture 依賴 session_service fixture
    """
    conv_id = "test-conv-fixture-001"
    session_service.create_session(conv_id, "Test Chat from Fixture")
    return conv_id


@pytest.fixture
def sample_conversation_with_messages(session_service, sample_conversation_id):
    """建立包含訊息的測試對話
    
    返回: (conversation_id, messages_list)
    """
    messages = [
        ("user", "你好"),
        ("model", "你好！我是 NotChatGPT"),
        ("user", "請介紹你自己"),
        ("model", "我是一個智慧對話助理，專注於提供有用的資訊。"),
    ]
    
    for role, content in messages:
        session_service.add_message(sample_conversation_id, role, content)
    
    return sample_conversation_id, messages