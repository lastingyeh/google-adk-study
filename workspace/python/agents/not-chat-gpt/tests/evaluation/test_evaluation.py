import pytest
import json
import os
from google import genai
from backend.agents.conversation_agent import create_conversation_agent

class TestEvaluation:
    """評估測試：使用評估數據集驗證 AI 回應品質
    
    注意：本測試暫時使用基本斷言驗證，未來可整合 Google ADK AgentEvaluator
    """
    
    def test_eval_basic_conversation(self, genai_client, model_name):
        """評估基本對話品質"""
        # 載入評估數據集
        eval_set_path = os.path.join(os.path.dirname(__file__), "..", "eval_set.json")
        with open(eval_set_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
        
        # 測試第一個案例：基本對話
        test_case = eval_data["test_cases"][0]
        config = create_conversation_agent()
        
        response = genai_client.models.generate_content(
            model=model_name,
            contents=test_case["input"],
            config=config
        )
        
        # 驗證回應
        assert response.text is not None, "回應不應為空"
        assert len(response.text) > 0, "回應長度應大於 0"
        
        # 驗證關鍵字
        for keyword in test_case["expected"]["response_contains"]:
            assert keyword in response.text, f"回應缺少關鍵字: {keyword}"
        
        # 驗證最小長度
        if "min_length" in test_case["expected"]:
            assert len(response.text) >= test_case["expected"]["min_length"], \
                f"回應長度 {len(response.text)} 小於最小要求 {test_case['expected']['min_length']}"
        
        print(f"✅ 評估通過: {test_case['id']} - {test_case['description']}")
    
    def test_eval_multiple_cases(self, genai_client, model_name):
        """評估多個測試案例"""
        eval_set_path = os.path.join(os.path.dirname(__file__), "..", "eval_set.json")
        with open(eval_set_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
        
        config = create_conversation_agent()
        passed = 0
        failed = 0
        
        # 只測試基本對話案例（非記憶類）
        basic_cases = [tc for tc in eval_data["test_cases"] 
                       if tc["category"] == "basic_conversation"]
        
        for test_case in basic_cases:
            try:
                response = genai_client.models.generate_content(
                    model=model_name,
                    contents=test_case["input"],
                    config=config
                )
                
                # 驗證回應不為空
                assert response.text and len(response.text) > 0
                
                # 驗證關鍵字（如果有）
                if "response_contains" in test_case["expected"]:
                    for keyword in test_case["expected"]["response_contains"]:
                        assert keyword in response.text
                
                passed += 1
                print(f"✅ {test_case['id']}: {test_case['description']}")
                
            except AssertionError as e:
                failed += 1
                print(f"❌ {test_case['id']}: {str(e)}")
        
        print(f"\n📊 評估結果: {passed} 通過 / {failed} 失敗 / {len(basic_cases)} 總計")
        assert passed > 0, "至少應有一個測試通過"