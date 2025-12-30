from google.genai import types
from backend.services.session_service import SessionService

def create_session_aware_agent(session_id: str, session_service: SessionService = None):
    """建立具有 Session 上下文記憶的 Agent
    
    Args:
        session_id: Session 識別碼
        session_service: SessionService 實例（可選，主要用於測試時注入）
    """
    if session_service is None:
        session_service = SessionService()
    
    state = session_service.load_state(session_id)
    
    # 從 state 中提取上下文（使用前綴管理）
    user_context = state.get("user:context", "")
    app_context = state.get("app:settings", {})
    temp_data = state.get("temp:data", {})
    
    system_instruction = f"""你是 NotChatGPT，一個智慧對話助理。

使用者上下文: {user_context if user_context else "無特定上下文"}
應用設定: {app_context if app_context else "預設設定"}
臨時資料: {temp_data if temp_data else "無"}
"""
    
    return types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=1.0,
    ), session_service