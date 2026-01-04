"""NotChatGPT 串流回應模組 (使用 Google ADK)

提供串流生成功能，使用 ADK Runner 進行對話管理：
- 即時回應輸出
- 思考模式切換
- 安全防護整合
- 會話狀態管理
"""

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
from typing import AsyncIterator, Optional
from dotenv import load_dotenv
import os


class StreamingAgentManager:
    """串流 Agent 管理器，使用 ADK 架構"""
    
    def __init__(self):
        """初始化 Agent Manager"""
        self.session_service = InMemorySessionService()
        self.app_name = "not_chat_gpt_streaming"
        self._runner = None
        self._agent = None
    
    def create_agent(self, thinking_mode: bool = False) -> Agent:
        """建立配置好的 Agent
        
        Args:
            thinking_mode: 是否啟用思考模式
            
        Returns:
            Agent: 配置好的 ADK Agent
        """
        instruction = """
        你是 NotChatGPT，一個智慧對話助理。

        特點：
        - 友善且專業的對話風格
        - 提供準確且有幫助的資訊
        - 支援多輪對話與上下文理解
        """
        
        if thinking_mode:
            instruction += """

思考模式已啟用：
- 展示你的推理過程
- 說明你如何得出結論
- 分步驟解釋複雜問題
            """
        
        return Agent(
            name="not_chat_gpt_streaming",
            model="gemini-2.0-flash-exp",
            instruction=instruction,
            description="支援串流回應的對話助理"
        )
    
    def get_runner(self, thinking_mode: bool = False) -> Runner:
        """取得或建立 Runner
        
        Args:
            thinking_mode: 是否啟用思考模式
            
        Returns:
            Runner: ADK Runner 實例
        """
        if self._runner is None or self._agent is None:
            self._agent = self.create_agent(thinking_mode)
            self._runner = Runner(
                agent=self._agent,
                app_name=self.app_name,
                session_service=self.session_service
            )
        return self._runner
    
    async def stream_response(
        self,
        message: str,
        user_id: str = "default_user",
        session_id: Optional[str] = None,
        thinking_mode: bool = False,
        enable_safety: bool = True
    ) -> AsyncIterator[str]:
        """串流生成回應
        
        Args:
            message: 使用者訊息
            user_id: 使用者 ID
            session_id: 會話 ID（若為 None 則建立新會話）
            thinking_mode: 是否啟用思考模式
            enable_safety: 是否啟用安全防護
            
        Yields:
            str: 回應文字片段
        """
        try:
            # 安全驗證（如果啟用）
            if enable_safety:
                from backend.guardrails.safety_callbacks import validate_input
                validation = validate_input(message)
                if not validation['valid']:
                    yield f"⚠️ 輸入驗證失敗: {validation['reason']}"
                    return
            
            # 建立或使用現有會話
            if session_id is None:
                session = await self.session_service.create_session(
                    app_name=self.app_name,
                    user_id=user_id
                )
                session_id = session.id
            
            # 取得 Runner
            runner = self.get_runner(thinking_mode)
            
            # 建立訊息
            user_message = types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )
            
            # 串流執行
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message
            ):
                # 處理回應事件
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            # 如果啟用安全防護，過濾 PII
                            text = part.text
                            if enable_safety:
                                from backend.guardrails.pii_detector import filter_pii_from_text
                                text = filter_pii_from_text(text)
                            
                            yield text
                            
        except Exception as e:
            yield f"❌ 生成錯誤: {str(e)}"


# 全域實例
_manager = None

def get_streaming_manager() -> StreamingAgentManager:
    """取得全域 StreamingAgentManager 實例"""
    global _manager
    if _manager is None:
        _manager = StreamingAgentManager()
    return _manager


async def stream_response(
    message: str,
    thinking_mode: bool = False,
    enable_safety: bool = True,
    user_id: str = "default_user",
    session_id: Optional[str] = None
) -> AsyncIterator[str]:
    """串流生成回應（向後相容的介面）
    
    Args:
        message: 使用者訊息
        thinking_mode: 是否啟用思考模式
        enable_safety: 是否啟用安全防護
        user_id: 使用者 ID
        session_id: 會話 ID
        
    Yields:
        str: 回應文字片段
    """
    manager = get_streaming_manager()
    async for chunk in manager.stream_response(
        message=message,
        user_id=user_id,
        session_id=session_id,
        thinking_mode=thinking_mode,
        enable_safety=enable_safety
    ):
        yield chunk


# 測試用
if __name__ == "__main__":
    import asyncio
    
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