from backend.config.mode_config import ModeConfig
from backend.agents.safe_conversation_agent import safe_generate_response

class TestAgent:
    def test_create_config_thinking(self):
        """測試思考模式配置建立"""
        config = ModeConfig.create_config_with_mode(thinking_mode=True)
        assert config is not None
        assert config.system_instruction is not None
        # 檢查思考模式相關的關鍵字
        assert "思考" in config.system_instruction or "展示" in config.system_instruction
        print("✅ 思考模式配置測試通過")
    
    def test_create_config_standard(self):
        """測試標準模式配置建立"""
        config = ModeConfig.create_config_with_mode(thinking_mode=False)
        assert config is not None
        assert config.system_instruction is not None
        print("✅ 標準模式配置測試通過")
    
    def test_mode_config_difference(self):
        """測試思考模式和標準模式的差異"""
        config_thinking = ModeConfig.create_config_with_mode(thinking_mode=True)
        config_standard = ModeConfig.create_config_with_mode(thinking_mode=False)
        
        assert config_thinking.system_instruction != config_standard.system_instruction
        print("✅ 模式差異測試通過")
    
    def test_basic_conversation(self, api_key, genai_client, model_name):
        """測試基本對話（使用 fixtures）"""
        result = safe_generate_response(
            client=genai_client,
            model_name=model_name,
            user_message="你好",
            enable_safety=True
        )
        
        assert result['success'] is True
        assert result['text'] is not None
        assert len(result['text']) > 0
        print("✅ 基本對話測試通過")