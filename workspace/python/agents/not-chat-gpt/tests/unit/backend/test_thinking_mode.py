import pytest
from google import genai
from dotenv import load_dotenv
import os
from backend.config.mode_config import ModeConfig

class TestThinkingMode:
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試前置設定"""
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
        
        if not self.api_key:
            pytest.skip("GOOGLE_API_KEY 未設定")
        
        self.client = genai.Client(api_key=self.api_key)
        
        yield
    
    def test_thinking_mode(self):
        """測試思考模式"""
        print("\n=== 思考模式 💭 ===")
        config = ModeConfig.create_config_with_mode(thinking_mode=True)
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents="請解釋量子糾纏的原理",
            config=config
        )
        
        print(f"回應: {response.text[:200]}...")
        
        # 驗證回應
        assert response.text is not None
        assert len(response.text) > 0
        print("✅ 思考模式測試通過")
    
    def test_standard_mode(self):
        """測試標準模式"""
        print("\n=== 標準模式 💬 ===")
        config = ModeConfig.create_config_with_mode(thinking_mode=False)
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents="今天天氣如何？",
            config=config
        )
        
        print(f"回應: {response.text}")
        
        # 驗證回應
        assert response.text is not None
        assert len(response.text) > 0
        print("✅ 標準模式測試通過")
    
    def test_mode_toggle(self):
        """測試模式切換"""
        # 建立兩種模式的 config
        config_thinking = ModeConfig.create_config_with_mode(thinking_mode=True)
        config_standard = ModeConfig.create_config_with_mode(thinking_mode=False)
        
        # 驗證建立成功
        assert config_thinking is not None
        assert config_standard is not None
        
        # 驗證 system_instruction 不同
        assert "思考過程" in config_thinking.system_instruction
        assert "思考過程" not in config_standard.system_instruction
        
        print("✅ 模式切換測試通過")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
