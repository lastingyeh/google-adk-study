"""PII 偵測模組"""
import re
import logging

logger = logging.getLogger(__name__)

# PII 模式配置
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b09\d{2}[-.]?\d{3}[-.]?\d{3}\b',
    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    'taiwan_id': r'\b[A-Z]\d{9}\b',
}

# 封鎖關鍵字
BLOCKED_KEYWORDS = ['密碼', '信用卡', '身份證', '帳號']

def detect_pii(text: str) -> dict:
    """檢測文本中的 PII
    
    Returns:
        dict: {'found': bool, 'types': list, 'message': str}
    """
    found_types = []
    
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            found_types.append(pii_type)
            logger.warning(f"偵測到 PII: {pii_type}")
    
    if found_types:
        return {
            'found': True,
            'types': found_types,
            'message': f"偵測到敏感資訊: {', '.join(found_types)}"
        }
    
    return {'found': False, 'types': [], 'message': ''}

def check_blocked_keywords(text: str) -> dict:
    """檢查封鎖關鍵字
    
    Returns:
        dict: {'found': bool, 'keywords': list, 'message': str}
    """
    found_keywords = []
    
    for keyword in BLOCKED_KEYWORDS:
        if keyword in text.lower():
            found_keywords.append(keyword)
            logger.warning(f"發現封鎖關鍵字: {keyword}")
    
    if found_keywords:
        return {
            'found': True,
            'keywords': found_keywords,
            'message': f"訊息包含敏感關鍵字: {', '.join(found_keywords)}"
        }
    
    return {'found': False, 'keywords': [], 'message': ''}

def filter_pii_from_text(text: str) -> str:
    """從文本中過濾 PII"""
    filtered_text = text
    
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, filtered_text, re.IGNORECASE)
        if matches:
            filtered_text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', filtered_text, flags=re.IGNORECASE)
            logger.info(f"過濾了 {len(matches)} 個 {pii_type}")
    
    return filtered_text