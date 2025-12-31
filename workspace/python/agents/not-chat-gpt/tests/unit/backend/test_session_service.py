"""測試 SessionService 功能"""
import pytest
import uuid
from backend.services.session_service import SessionService
import os

@pytest.fixture
def session_service():
    """建立測試用的 SessionService"""
    # 使用記憶體資料庫
    service = SessionService(database_url="sqlite:///:memory:")
    yield service

class TestSessionService:
    """測試 SessionService 基本功能"""
    
    def test_create_session(self, session_service):
        """測試建立 session"""
        session_id = str(uuid.uuid4())
        result = session_service.create_session(session_id, title="Test Session")
        assert result == session_id
        print("✅ Session 建立測試通過")
    
    def test_add_and_get_messages(self, session_service):
        """測試新增和取得訊息"""
        session_id = str(uuid.uuid4())
        session_service.create_session(session_id)
        
        # 新增訊息
        session_service.add_message(session_id, "user", "Hello")
        session_service.add_message(session_id, "model", "Hi there!")
        
        # 取得訊息
        messages = session_service.get_messages(session_id)
        assert len(messages) == 2
        assert messages[0] == ("user", "Hello")
        assert messages[1] == ("model", "Hi there!")
        print("✅ 訊息新增和取得測試通過")
    
    def test_list_conversations(self, session_service):
        """測試列出對話"""
        session_id1 = str(uuid.uuid4())
        session_id2 = str(uuid.uuid4())
        
        session_service.create_session(session_id1, title="Session 1")
        session_service.create_session(session_id2, title="Session 2")
        
        conversations = session_service.list_conversations()
        assert len(conversations) >= 2
        print("✅ 對話列表測試通過")
    
    def test_delete_conversation(self, session_service):
        """測試刪除對話"""
        session_id = str(uuid.uuid4())
        session_service.create_session(session_id)
        session_service.add_message(session_id, "user", "Test")
        
        # 刪除對話
        session_service.delete_conversation(session_id)
        
        # 確認訊息也被刪除（cascade）
        messages = session_service.get_messages(session_id)
        assert len(messages) == 0
        print("✅ 對話刪除測試通過")
    
    def test_save_and_load_state(self, session_service):
        """測試儲存和載入狀態"""
        session_id = str(uuid.uuid4())
        session_service.create_session(session_id)
        
        # 儲存狀態
        state = {"user:context": "test context", "app:settings": {"theme": "dark"}}
        session_service.save_state(session_id, state)
        
        # 載入狀態
        loaded_state = session_service.load_state(session_id)
        assert loaded_state == state
        print("✅ 狀態儲存和載入測試通過")

def test_run_all():
    """執行所有測試"""
    service = SessionService(database_url="sqlite:///:memory:")
    test_suite = TestSessionService()
    
    test_suite.test_create_session(service)
    test_suite.test_add_and_get_messages(service)
    test_suite.test_list_conversations(service)
    test_suite.test_delete_conversation(service)
    test_suite.test_save_and_load_state(service)
    
    print("\n✅ 所有 SessionService 測試通過")

if __name__ == "__main__":
    test_run_all()