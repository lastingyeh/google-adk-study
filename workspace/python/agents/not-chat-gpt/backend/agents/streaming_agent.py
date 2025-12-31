"""NotChatGPT 串流回應模組

提供串流生成功能，支援：
- 即時回應輸出
- 思考模式切換
- 安全防護整合
"""
from google import genai
from google.genai import types
from typing import AsyncIterator
from dotenv import load_dotenv
import os
import asyncio

async def stream_response(
    message: str,
    thinking_mode: bool = False,
    enable_safety: bool = True
) -> AsyncIterator[str]:
    """串流生成回應
    
    Args:
        message: 使用者訊息
        thinking_mode: 是否啟用思考模式
        enable_safety: 是否啟用安全防護
        
    Yields:
        str: 回應文字片段
    """
    from backend.config.mode_config import ModeConfig
    from backend.guardrails.safety_callbacks import validate_input
    from backend.guardrails.pii_detector import filter_pii_from_text
    
    # 驗證輸入（如果啟用安全防護）
    if enable_safety:
        validation = validate_input(message)
        if not validation['valid']:
            yield f"⚠️ 輸入驗證失敗: {validation['reason']}"
            return
    
    # 建立客戶端和配置
    api_key = os.getenv('GOOGLE_API_KEY')
    client = genai.Client(api_key=api_key)
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    
    config = ModeConfig.create_config_with_mode(thinking_mode=thinking_mode)
    
    # 如果啟用安全防護，加入 SafetySettings
    if enable_safety:
        from backend.agents.safe_conversation_agent import create_safe_config
        safe_config = create_safe_config(enable_safety=True)
        if safe_config.safety_settings:
            config = types.GenerateContentConfig(
                system_instruction=config.system_instruction,
                safety_settings=safe_config.safety_settings,
                response_modalities=config.response_modalities
            )
    
    try:
        # 串流生成
        response = client.models.generate_content_stream(
            model=model_name,
            contents=message,
            config=config
        )
        
        # 輸出片段
        for chunk in response:
            if chunk.text:
                # 如果啟用安全防護，過濾 PII
                text = filter_pii_from_text(chunk.text) if enable_safety else chunk.text
                yield text
                
    except Exception as e:
        yield f"❌ 生成錯誤: {str(e)}"


# 測試用
if __name__ == "__main__":
    # 載入 .env 檔案
    load_dotenv()
    
    # 從環境變數取得 API Key
    api_key = os.getenv('GOOGLE_API_KEY')
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定在 .env 檔案中")
        exit(1)
    
    print(f"✅ 使用模型: {model_name}")
    print("=" * 60)
    
    async def test_streaming():
        """測試串流功能"""
        test_cases = [
            {
                "message": "請用一句話解釋什麼是機器學習",
                "thinking_mode": False,
                "enable_safety": True
            },
            {
                "message": "分析量子計算的未來發展",
                "thinking_mode": True,
                "enable_safety": True
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n📝 測試 {i}: {test['message']}")
            print(f"   思考模式: {'✓' if test['thinking_mode'] else '✗'}")
            print(f"   安全防護: {'✓' if test['enable_safety'] else '✗'}")
            print("-" * 60)
            
            async for chunk in stream_response(
                message=test['message'],
                thinking_mode=test['thinking_mode'],
                enable_safety=test['enable_safety']
            ):
                print(chunk, end='', flush=True)
            
            print("\n" + "=" * 60)
    
    # 執行測試
    asyncio.run(test_streaming())