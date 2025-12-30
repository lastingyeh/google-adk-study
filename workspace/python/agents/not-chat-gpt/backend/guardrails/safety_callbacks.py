"""安全防護 Callback 函式

基於 google-adk 的 callback 機制實作安全檢查。
注意：這些函式應該與 SafetySettings 配合使用，而非單獨使用。
"""
from google.genai import types
from .pii_detector import detect_pii, check_blocked_keywords, filter_pii_from_text
import logging

logger = logging.getLogger(__name__)

def validate_input(message: str) -> dict:
    """驗證輸入訊息
    
    Args:
        message: 使用者輸入
        
    Returns:
        dict: {'valid': bool, 'reason': str}
    """
    # 檢查 PII
    pii_result = detect_pii(message)
    if pii_result['found']:
        return {'valid': False, 'reason': pii_result['message']}
    
    # 檢查封鎖關鍵字
    keyword_result = check_blocked_keywords(message)
    if keyword_result['found']:
        logger.warning(keyword_result['message'])
        # 注意：關鍵字僅警告，不阻擋
    
    return {'valid': True, 'reason': ''}

def sanitize_response(response_text: str) -> str:
    """清理回應文本
    
    Args:
        response_text: 模型回應
        
    Returns:
        str: 清理後的文本
    """
    return filter_pii_from_text(response_text)