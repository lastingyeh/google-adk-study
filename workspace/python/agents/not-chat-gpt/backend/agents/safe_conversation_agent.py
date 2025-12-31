"""具有安全防護的對話 Agent"""
from google.genai import types
from backend.guardrails.safety_callbacks import validate_input, sanitize_response
import logging

logger = logging.getLogger(__name__)

def create_safe_config(enable_safety: bool = True) -> types.GenerateContentConfig:
    """建立具有安全設定的配置
    
    Args:
        enable_safety: 是否啟用安全設定
        
    Returns:
        GenerateContentConfig: 配置物件
    """
    config = types.GenerateContentConfig(
        system_instruction="""
        你是 NotChatGPT，一個智慧對話助理。
        
        重要安全指令：
        - 不要生成有害、偏見或不當的內容
        - 如果請求不清楚，請要求澄清
        - 不要洩露或生成個人敏感資訊
        """,
        temperature=1.0,
    )
    
    if enable_safety:
        # 設定安全過濾等級
        config.safety_settings = [
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
        ]
    
    return config

def safe_generate_response(
    client, 
    model_name: str, 
    user_message: str, 
    enable_safety: bool = True,
    conversation_history: list = None
) -> dict:
    """安全地生成回應（支援多輪對話）
    
    Args:
        client: Genai client
        model_name: 模型名稱
        user_message: 使用者訊息
        enable_safety: 是否啟用安全檢查
        conversation_history: 對話歷史，格式為 [{'role': 'user', 'parts': [{'text': '...'}]}, ...]
        
    Returns:
        dict: {'success': bool, 'text': str, 'reason': str}
    """
    # 輸入驗證
    if enable_safety:
        validation = validate_input(user_message)
        if not validation['valid']:
            logger.warning(f"輸入被阻擋: {validation['reason']}")
            return {
                'success': False,
                'text': f"⚠️ 無法處理此請求: {validation['reason']}",
                'reason': validation['reason']
            }
    
    # 生成回應
    try:
        config = create_safe_config(enable_safety=enable_safety)
        
        # 準備內容：如果有對話歷史，則包含歷史 + 新訊息
        if conversation_history:
            # 複製歷史並添加新訊息
            contents = conversation_history + [{
                'role': 'user',
                'parts': [{'text': user_message}]
            }]
        else:
            # 沒有歷史，只傳送新訊息
            contents = user_message
        
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config
        )
        
        response_text = response.text
        
        # 輸出過濾
        if enable_safety:
            response_text = sanitize_response(response_text)
        
        return {
            'success': True,
            'text': response_text,
            'reason': ''
        }
        
    except Exception as e:
        logger.error(f"生成回應時發生錯誤: {e}")
        return {
            'success': False,
            'text': "抱歉，處理您的請求時發生錯誤。",
            'reason': str(e)
        }