import re
from typing import Optional
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse


# 示範用的簡化封鎖清單
BLOCKED_WORDS = [
    '大樹', 'cathay' # 請用真實詞彙替換
]

# 用於過濾的 PII 模式
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
}

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """在向 LLM 發送請求前呼叫。
    用途：
    1. 護欄：阻擋不適當的請求。
    2. 修改：新增安全指令。
    3. 快取：返回快取的回應。
    4. 日誌：追蹤 LLM 使用情況。
    返回：
        None: 允許 LLM 呼叫繼續。
        LlmResponse: 跳過 LLM 呼叫，改用此回應。
    """
    # Inspect the last user message in the request contents
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
         if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[Callback] Inspecting last user message: '{last_user_message}'")

    # 護欄：檢查封鎖詞彙
    for word in BLOCKED_WORDS:
        # 支援中英文：同時檢查原文和小寫版本
        if last_user_message and \
            (word in last_user_message or word.lower() in last_user_message.lower()):
            # 返回錯誤回應（跳過 LLM 呼叫）
            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(
                        text="抱歉，我無法處理包含不當內容的請求。請重新措辭並以尊重的方式表達。"
                    )],
                    role="model"
                )
            )

    # 護欄：檢查 PII（個人識別資訊）
    for pii_type, pattern in PII_PATTERNS.items():
        if last_user_message and re.search(pattern, last_user_message):
            # 返回 PII 警告回應（跳過 LLM 呼叫）
            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(
                        text=f"抱歉，您的訊息中包含個人識別資訊（{pii_type}）。為了保護您的隱私，我無法處理包含個人資訊的請求。請移除個人資訊後重新提交。"
                    )],
                    role="model"
                )
            )

    return None  # 允許 LLM 呼叫（帶有修改）


