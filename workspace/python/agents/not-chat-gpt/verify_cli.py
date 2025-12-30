#!/usr/bin/env python
"""CLI 功能驗證腳本

測試所有 CLI 功能是否正常運作
"""
import sys
import os

# 設定路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """測試所有模組是否可以正常 import"""
    print("🧪 測試 1: 檢查模組 import...")
    try:
        from config.mode_config import ModeConfig
        from agents.safe_conversation_agent import safe_generate_response, create_safe_config
        from services.session_service import SessionService
        from guardrails.pii_detector import detect_pii, check_blocked_keywords, filter_pii_from_text
        from guardrails.safety_callbacks import validate_input, sanitize_response
        print("✅ 所有模組 import 成功\n")
        return True
    except Exception as e:
        print(f"❌ Import 失敗: {e}\n")
        return False

def test_mode_config():
    """測試模式配置"""
    print("🧪 測試 2: ModeConfig 功能...")
    try:
        from config.mode_config import ModeConfig
        
        config_standard = ModeConfig.create_config_with_mode(thinking_mode=False)
        config_thinking = ModeConfig.create_config_with_mode(thinking_mode=True)
        
        assert config_standard is not None
        assert config_thinking is not None
        assert config_standard.system_instruction != config_thinking.system_instruction
        
        print("✅ ModeConfig 測試通過\n")
        return True
    except Exception as e:
        print(f"❌ ModeConfig 測試失敗: {e}\n")
        return False

def test_session_service():
    """測試 SessionService"""
    print("🧪 測試 3: SessionService 功能...")
    try:
        from services.session_service import SessionService
        import uuid
        
        # 使用記憶體資料庫測試
        service = SessionService(database_url="sqlite:///:memory:")
        
        # 測試建立 session
        session_id = str(uuid.uuid4())
        service.create_session(session_id, title="Test Session")
        
        # 測試新增訊息
        service.add_message(session_id, "user", "Hello")
        service.add_message(session_id, "model", "Hi there!")
        
        # 測試取得訊息
        messages = service.get_messages(session_id)
        assert len(messages) == 2
        assert messages[0] == ("user", "Hello")
        assert messages[1] == ("model", "Hi there!")
        
        # 測試列出對話
        conversations = service.list_conversations()
        assert len(conversations) >= 1
        
        print("✅ SessionService 測試通過\n")
        return True
    except Exception as e:
        print(f"❌ SessionService 測試失敗: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_pii_detection():
    """測試 PII 偵測"""
    print("🧪 測試 4: PII 偵測功能...")
    try:
        from guardrails.pii_detector import detect_pii, check_blocked_keywords, filter_pii_from_text
        
        # 測試信用卡偵測
        result = detect_pii("我的卡號是 1234-5678-9012-3456")
        assert result['found'] is True
        assert 'credit_card' in result['types']
        
        # 測試 email 偵測
        result = detect_pii("聯絡我：test@example.com")
        assert result['found'] is True
        assert 'email' in result['types']
        
        # 測試關鍵字偵測
        result = check_blocked_keywords("請問我的密碼是什麼？")
        assert result['found'] is True
        
        # 測試過濾
        filtered = filter_pii_from_text("我的卡號是 1234-5678-9012-3456")
        assert "1234-5678-9012-3456" not in filtered
        assert "[CREDIT_CARD_REDACTED]" in filtered
        
        print("✅ PII 偵測測試通過\n")
        return True
    except Exception as e:
        print(f"❌ PII 偵測測試失敗: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_safe_generate_response():
    """測試安全生成回應（不實際調用 API）"""
    print("🧪 測試 5: safe_generate_response 簽名...")
    try:
        from agents.safe_conversation_agent import safe_generate_response
        import inspect
        
        # 檢查函數簽名
        sig = inspect.signature(safe_generate_response)
        params = list(sig.parameters.keys())
        
        assert 'client' in params
        assert 'model_name' in params
        assert 'user_message' in params
        assert 'enable_safety' in params
        assert 'conversation_history' in params
        
        print("✅ safe_generate_response 簽名正確\n")
        return True
    except Exception as e:
        print(f"❌ safe_generate_response 測試失敗: {e}\n")
        return False

def main():
    """執行所有測試"""
    print("=" * 60)
    print("CLI 功能驗證測試")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("模組 Import", test_imports()))
    results.append(("ModeConfig", test_mode_config()))
    results.append(("SessionService", test_session_service()))
    results.append(("PII 偵測", test_pii_detection()))
    results.append(("safe_generate_response", test_safe_generate_response()))
    
    print("=" * 60)
    print("測試結果摘要")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{name:30s} {status}")
    
    print()
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    if passed == total:
        print(f"🎉 所有測試通過！({passed}/{total})")
        return 0
    else:
        print(f"⚠️  部分測試失敗 ({passed}/{total})")
        return 1

if __name__ == "__main__":
    sys.exit(main())
