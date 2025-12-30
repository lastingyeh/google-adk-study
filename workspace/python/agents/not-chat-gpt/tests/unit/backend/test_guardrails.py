import pytest
from google import genai
from dotenv import load_dotenv
import os
from backend.agents.safe_conversation_agent import create_safe_config, safe_generate_response
from backend.guardrails.pii_detector import detect_pii, check_blocked_keywords, filter_pii_from_text

class TestPIIDetector:
    """測試 PII 檢測功能"""
    
    def test_detect_credit_card(self):
        """測試信用卡號檢測"""
        result = detect_pii("我的卡號是 1234-5678-9012-3456")
        assert result['found'] is True
        assert 'credit_card' in result['types']
        print("✅ 信用卡號檢測通過")
    
    def test_detect_email(self):
        """測試 email 檢測"""
        result = detect_pii("聯絡我：test@example.com")
        assert result['found'] is True
        assert 'email' in result['types']
        print("✅ Email 檢測通過")
    
    def test_detect_phone(self):
        """測試電話號碼檢測"""
        result = detect_pii("電話：0912-345-678")
        assert result['found'] is True
        assert 'phone' in result['types']
        print("✅ 電話號碼檢測通過")
    
    def test_no_pii(self):
        """測試無 PII 的正常文本"""
        result = detect_pii("今天天氣很好")
        assert result['found'] is False
        assert len(result['types']) == 0
        print("✅ 無 PII 檢測通過")

class TestBlockedKeywords:
    """測試關鍵字檢測"""
    
    def test_detect_blocked_keyword(self):
        """測試封鎖關鍵字檢測"""
        result = check_blocked_keywords("請問我的密碼是什麼？")
        assert result['found'] is True
        assert '密碼' in result['keywords']
        print("✅ 封鎖關鍵字檢測通過")
    
    def test_no_blocked_keyword(self):
        """測試無封鎖關鍵字"""
        result = check_blocked_keywords("今天天氣如何？")
        assert result['found'] is False
        print("✅ 無封鎖關鍵字檢測通過")

class TestPIIFiltering:
    """測試 PII 過濾功能"""
    
    def test_filter_credit_card(self):
        """測試過濾信用卡號"""
        text = "我的卡號是 1234-5678-9012-3456"
        filtered = filter_pii_from_text(text)
        assert "1234-5678-9012-3456" not in filtered
        assert "[CREDIT_CARD_REDACTED]" in filtered
        print("✅ 信用卡號過濾通過")
    
    def test_filter_multiple_pii(self):
        """測試過濾多個 PII"""
        text = "聯絡方式：test@example.com，電話 0912-345-678"
        filtered = filter_pii_from_text(text)
        assert "test@example.com" not in filtered
        assert "0912-345-678" not in filtered
        assert "[EMAIL_REDACTED]" in filtered
        assert "[PHONE_REDACTED]" in filtered
        print("✅ 多個 PII 過濾通過")

class TestSafeConversation:
    """測試安全對話流程"""
    
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
    
    def test_safe_config_creation(self):
        """測試安全配置建立"""
        config = create_safe_config(enable_safety=True)
        assert config is not None
        assert config.safety_settings is not None
        assert len(config.safety_settings) > 0
        print("✅ 安全配置建立測試通過")
    
    def test_normal_request(self):
        """測試正常請求"""
        result = safe_generate_response(
            self.client,
            self.model_name,
            "請介紹 Python 程式語言",
            enable_safety=True
        )
        assert result['success'] is True
        assert len(result['text']) > 0
        print("✅ 正常請求測試通過")
    
    def test_blocked_pii_request(self):
        """測試包含 PII 的請求被阻擋"""
        result = safe_generate_response(
            self.client,
            self.model_name,
            "我的信用卡號是 1234-5678-9012-3456",
            enable_safety=True
        )
        assert result['success'] is False
        assert '敏感資訊' in result['reason'] or '信用卡' in result['reason']
        print("✅ PII 阻擋測試通過")
    
    def test_safety_disabled(self):
        """測試停用安全檢查"""
        result = safe_generate_response(
            self.client,
            self.model_name,
            "今天天氣如何？",
            enable_safety=False
        )
        assert result['success'] is True
        print("✅ 停用安全檢查測試通過")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])