#!/usr/bin/env python3
"""
測試 guardrails 功能
"""

import sys
import os
from typing import List

# 添加 backend 路徑以便匯入
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend')
sys.path.append(backend_path)

from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from guardrails.guardrails import before_model_callback

def create_test_request(text: str) -> LlmRequest:
    """創建測試用的 LLM 請求"""
    return LlmRequest(
        contents=[
            types.Content(
                parts=[types.Part(text=text)],
                role="user"
            )
        ]
    )

def create_test_context() -> CallbackContext:
    """創建測試用的回調上下文"""
    # 創建最小化的測試上下文 - 可能需要根據實際 API 調整
    try:
        return CallbackContext()
    except Exception:
        # 如果 CallbackContext 需要參數，返回 None 並在測試中處理
        return None

def test_blocked_words():
    """測試封鎖詞彙功能"""
    print("=== 測試封鎖詞彙 ===")
    
    test_cases = [
        # 中文測試
        ("我喜歡大樹", True, "中文封鎖詞彙"),
        ("今天天氣很好，大樹很綠", True, "中文封鎖詞彙在句子中"),
        ("大家好", False, "相似但不同的中文詞"),
        
        # 英文測試
        ("I work at Cathay", True, "英文封鎖詞彙"),
        ("cathay pacific", True, "小寫英文封鎖詞彙"),
        ("CATHAY bank", True, "大寫英文封鎖詞彙"),
        ("category", False, "相似但不同的英文詞"),
        
        # 正常測試
        ("Hello, how are you?", False, "正常英文"),
        ("你好，今天天氣如何？", False, "正常中文"),
    ]
    
    context = create_test_context()
    
    for text, should_block, description in test_cases:
        request = create_test_request(text)
        result = before_model_callback(context, request)
        
        is_blocked = result is not None
        status = "✅ PASS" if is_blocked == should_block else "❌ FAIL"
        
        print(f"{status} {description}")
        print(f"   輸入: '{text}'")
        print(f"   預期: {'封鎖' if should_block else '通過'}, 實際: {'封鎖' if is_blocked else '通過'}")
        
        if is_blocked and result:
            print(f"   回應: {result.content.parts[0].text}")
        print()

def test_pii_detection():
    """測試 PII 檢測功能"""
    print("=== 測試 PII 檢測 ===")
    
    test_cases = [
        # Email 測試
        ("我的郵箱是 john@example.com", True, "email", "Email 檢測"),
        ("聯繫方式：user.test+tag@domain.co.uk", True, "email", "複雜 Email 檢測"),
        ("email 格式錯誤 john@", False, None, "無效 Email 不應檢測"),
        
        # 電話號碼測試
        ("我的電話是 123-456-7890", True, "phone", "電話號碼檢測"),
        ("手機 123.456.7890", True, "phone", "點號分隔電話"),
        ("號碼 1234567890", True, "phone", "無分隔電話"),
        ("12345", False, None, "短數字不應檢測為電話"),
        
        # SSN 測試
        ("SSN: 123-45-6789", True, "ssn", "SSN 檢測"),
        ("社會安全號碼 987-65-4321", True, "ssn", "中文描述的 SSN"),
        
        # 信用卡測試
        ("信用卡號: 1234 5678 9012 3456", True, "credit_card", "信用卡號檢測"),
        ("卡號 1234-5678-9012-3456", True, "credit_card", "破折號分隔信用卡"),
        ("1234567890123456", True, "credit_card", "連續信用卡號"),
        
        # 正常測試
        ("今天很熱", False, None, "正常中文"),
        ("What's the weather today?", False, None, "正常英文"),
    ]
    
    context = create_test_context()
    
    for text, should_detect, expected_type, description in test_cases:
        request = create_test_request(text)
        result = before_model_callback(context, request)
        
        is_detected = result is not None
        status = "✅ PASS" if is_detected == should_detect else "❌ FAIL"
        
        print(f"{status} {description}")
        print(f"   輸入: '{text}'")
        print(f"   預期: {'檢測到 ' + expected_type if should_detect else '通過'}")
        print(f"   實際: {'檢測到 PII' if is_detected else '通過'}")
        
        if is_detected and result:
            print(f"   回應: {result.content.parts[0].text}")
        print()

def main():
    """主測試函數"""
    print("開始測試 Guardrails 功能...")
    print()
    
    try:
        test_blocked_words()
        test_pii_detection()
        
        print("=== 測試完成 ===")
        print("如果看到 ❌ FAIL，表示該功能未正常運作")
        print("如果全部顯示 ✅ PASS，表示 guardrails 功能正常")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()