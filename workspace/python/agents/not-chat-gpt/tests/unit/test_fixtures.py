"""測試 conftest.py 中定義的 fixtures

這個測試文件展示如何使用共用的 fixtures
"""
import pytest


class TestFixtures:
    """測試共用 fixtures 是否正常工作"""
    
    def test_api_key_fixture(self, api_key):
        """測試 api_key fixture"""
        assert api_key is not None
        assert isinstance(api_key, str)
        assert len(api_key) > 0
        print(f"✅ API Key fixture 正常（長度: {len(api_key)}）")
    
    def test_model_name_fixture(self, model_name):
        """測試 model_name fixture"""
        assert model_name is not None
        assert isinstance(model_name, str)
        assert "gemini" in model_name.lower()
        print(f"✅ Model name fixture 正常: {model_name}")
    
    def test_genai_client_fixture(self, genai_client):
        """測試 genai_client fixture"""
        assert genai_client is not None
        from google import genai
        assert isinstance(genai_client, genai.Client)
        print("✅ GenAI Client fixture 正常")
    
    def test_session_service_fixture(self, session_service):
        """測試 session_service fixture"""
        assert session_service is not None
        
        # 測試可以建立 session
        session_id = "fixture-test-001"
        result = session_service.create_session(session_id, "Fixture Test")
        assert result == session_id
        
        # 測試可以載入 state
        state = session_service.load_state(session_id)
        assert isinstance(state, dict)
        print("✅ SessionService fixture 正常")
    
    def test_sample_conversation_fixture(self, session_service, sample_conversation_id):
        """測試 sample_conversation_id fixture"""
        assert sample_conversation_id is not None
        assert isinstance(sample_conversation_id, str)
        
        # 驗證對話確實存在
        state = session_service.load_state(sample_conversation_id)
        assert isinstance(state, dict)
        print(f"✅ Sample conversation fixture 正常: {sample_conversation_id}")
    
    def test_conversation_with_messages_fixture(
        self, 
        session_service, 
        sample_conversation_with_messages
    ):
        """測試 sample_conversation_with_messages fixture"""
        conv_id, expected_messages = sample_conversation_with_messages
        
        # 驗證對話存在
        assert conv_id is not None
        
        # 驗證訊息已儲存
        messages = session_service.get_messages(conv_id)
        assert len(messages) == len(expected_messages)
        
        # 驗證訊息內容
        for i, (role, content) in enumerate(messages):
            expected_role, expected_content = expected_messages[i]
            assert role == expected_role
            assert content == expected_content
        
        print(f"✅ Conversation with messages fixture 正常（{len(messages)} 則訊息）")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
