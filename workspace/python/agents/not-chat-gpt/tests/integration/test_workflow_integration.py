import pytest
from backend.services.session_service import SessionService
from backend.agents.conversation_agent import create_conversation_agent
from google import genai

class TestWorkflowIntegration:
    """整合測試：測試多個組件協作的完整工作流程"""
    
    def test_full_conversation_workflow(self, genai_client, model_name):
        """測試完整對話流程（使用 SessionService + Agent Config）"""
        # 1. 建立 session
        session_service = SessionService(database_url="sqlite:///:memory:")
        conv_id = session_service.create_session("integration-test-001", "Integration Test")
        
        # 2. 建立 agent config
        config = create_conversation_agent()
        
        # 3. 第一輪對話：發送訊息
        user_msg = "我叫 Bob"
        response = genai_client.models.generate_content(
            model=model_name,
            contents=user_msg,
            config=config
        )
        
        # 4. 儲存對話歷史
        session_service.add_message(conv_id, "user", user_msg)
        session_service.add_message(conv_id, "model", response.text)
        
        # 5. 驗證訊息已儲存
        messages = session_service.get_messages(conv_id)
        assert len(messages) == 2
        assert messages[0][0] == "user"
        assert messages[0][1] == user_msg
        assert messages[1][0] == "model"
        assert len(messages[1][1]) > 0
        print("✅ 對話歷史儲存驗證通過")
        
        # 6. 測試對話持久化：載入對話
        loaded_messages = session_service.get_messages(conv_id)
        assert len(loaded_messages) == 2
        assert loaded_messages[0][1] == user_msg
        print("✅ 對話持久化驗證通過")
        
        # 7. 測試第二輪對話（需手動提供上下文以測試記憶）
        # 注意：generate_content 不會自動保留記憶，需手動構建對話歷史
        history = [
            {"role": "user", "parts": [{"text": user_msg}]},
            {"role": "model", "parts": [{"text": response.text}]}
        ]
        
        user_msg2 = "我叫什麼名字？"
        response2 = genai_client.models.generate_content(
            model=model_name,
            contents=history + [{"role": "user", "parts": [{"text": user_msg2}]}],
            config=config
        )
        
        # 8. 儲存第二輪對話
        session_service.add_message(conv_id, "user", user_msg2)
        session_service.add_message(conv_id, "model", response2.text)
        
        # 9. 驗證完整對話歷史
        all_messages = session_service.get_messages(conv_id)
        assert len(all_messages) == 4
        print("✅ 多輪對話儲存驗證通過")
        
        # 10. 驗證回應包含名字（測試記憶功能）
        assert "Bob" in response2.text or "bob" in response2.text.lower()
        print("✅ 對話記憶功能驗證通過")
        
        # 11. 清理：刪除測試對話
        session_service.delete_conversation(conv_id)
        deleted_messages = session_service.get_messages(conv_id)
        assert len(deleted_messages) == 0
        print("✅ 對話刪除驗證通過")