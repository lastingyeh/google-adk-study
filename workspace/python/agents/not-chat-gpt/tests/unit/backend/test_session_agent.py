import pytest
from google import genai
from dotenv import load_dotenv
import os
from backend.agents.session_agent import create_session_aware_agent
from backend.services.session_service import SessionService

class TestSessionAgent:
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試前置設定 - 每個測試方法執行前都會重新初始化"""
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
        
        if not self.api_key:
            pytest.skip("GOOGLE_API_KEY 未設定")
        
        self.client = genai.Client(api_key=self.api_key)
        
        # 每個測試都創建新的 in-memory 資料庫，確保測試隔離
        self.session_service = SessionService(database_url="sqlite:///:memory:")
        
        yield  # 測試執行
        
        # 測試後清理（可選，因為 in-memory DB 會自動銷毀）
        if hasattr(self, 'session_service'):
            self.session_service.engine.dispose()
    
    def test_create_session_aware_agent(self):
        """測試建立具有上下文記憶的 Agent"""
        # 1. 建立測試 session（使用唯一 ID）
        test_session_id = "test-create-agent-001"
        self.session_service.create_session(test_session_id, "上下文記憶測試")
        
        # 2. 設定上下文
        state = {
            "user:context": "使用者偏好繁體中文，喜歡簡潔的回答",
            "app:settings": {"language": "zh-TW", "mode": "concise"},
            "temp:data": {"last_topic": "Python"}
        }
        self.session_service.save_state(test_session_id, state)
        
        # 3. 建立 Agent（注入測試用的 session_service）
        config, returned_service = create_session_aware_agent(
            test_session_id, 
            session_service=self.session_service
        )
        
        # 4. 驗證配置
        assert config is not None
        assert "使用者偏好繁體中文" in config.system_instruction
        assert "Python" in config.system_instruction
        
        # 5. 驗證 service 也被正確返回
        assert returned_service is not None
    
    def test_context_affects_response(self):
        """測試上下文是否影響 Agent 回應"""
        # 1. 建立有特定上下文的 session（使用唯一 ID）
        test_session_id = "test-context-response-002"
        self.session_service.create_session(test_session_id)
        
        state = {
            "user:context": "使用者偏好繁體中文，喜歡簡潔的回答",
            "app:settings": {"language": "zh-TW", "mode": "concise"}
        }
        self.session_service.save_state(test_session_id, state)
        
        # 2. 建立 Agent 並測試對話（注入測試用的 session_service）
        config, _ = create_session_aware_agent(
            test_session_id, 
            session_service=self.session_service
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents="請用我偏好的語言和風格回答：什麼是 Python？",
            config=config
        )
        
        # 3. 驗證回應不為空
        assert response.text is not None
        assert len(response.text) > 0
        print(f"✅ Agent 回應: {response.text[:100]}...")
    
    def test_context_persistence(self):
        """測試上下文持久化"""
        # 1. 建立並儲存上下文（使用唯一 ID）
        test_session_id = "test-persistence-003"
        self.session_service.create_session(test_session_id)
        
        original_state = {
            "user:context": "測試使用者",
            "temp:data": {"last_topic": "Python"}
        }
        self.session_service.save_state(test_session_id, original_state)
        
        # 2. 更新上下文
        updated_state = {
            "user:context": "測試使用者",
            "temp:data": {"last_topic": "機器學習"}
        }
        self.session_service.save_state(test_session_id, updated_state)
        
        # 3. 重新載入並驗證
        loaded_state = self.session_service.load_state(test_session_id)
        assert loaded_state["temp:data"]["last_topic"] == "機器學習"
        print("✅ 上下文持久化測試通過")
    
    def test_empty_context_handling(self):
        """測試空上下文處理"""
        # 1. 建立沒有上下文的 session（使用唯一 ID）
        test_session_id = "test-empty-context-004"
        self.session_service.create_session(test_session_id)
        
        # 2. 建立 Agent（應該使用預設值，注入測試用的 session_service）
        config, _ = create_session_aware_agent(
            test_session_id, 
            session_service=self.session_service
        )
        
        # 3. 驗證使用預設值
        assert "無特定上下文" in config.system_instruction
        assert "預設設定" in config.system_instruction
        print("✅ 空上下文處理測試通過")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])