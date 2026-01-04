"""
NotChatGPT - 對話 Agent (使用 Google ADK)

這個模組使用 Google Agent Development Kit (ADK) 建立一個智慧對話助理。
ADK 提供了完整的 Agent 框架，包括：
- Agent: 定義 Agent 的行為和能力
- Runner: 編排 Agent 的執行
- SessionService: 管理對話狀態
"""

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os


def create_conversation_agent() -> Agent:
    """
    建立基礎對話 Agent
    
    Returns:
        Agent: 配置好的 ADK Agent 實例
    """
    return Agent(
        name="not_chat_gpt",
        model="gemini-2.0-flash-exp",
        instruction="""
            你是 NotChatGPT，一個智慧對話助理。

            特點：
            - 友善且專業的對話風格
            - 提供準確且有幫助的資訊
            - 支援多輪對話與上下文理解
            - 能夠理解並回應各種問題

            行為準則：
            - 保持禮貌和尊重
            - 承認不確定的事情
            - 提供結構化且易於理解的回答
            - 適時詢問澄清問題
        """,
        description="一個智慧且友善的對話助理",
    )


# 測試用
if __name__ == "__main__":
    import asyncio
    
    # 載入 .env 檔案
    load_dotenv()
    
    # 檢查 API Key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定在 .env 檔案中")
        exit(1)
    
    print("✅ 使用 Google ADK 建立 Agent")
    
    # 建立 Agent
    agent = create_conversation_agent()
    
    # 建立 SessionService
    session_service = InMemorySessionService()
    
    # 建立 Runner
    runner = Runner(
        agent=agent,
        app_name="not_chat_gpt",
        session_service=session_service
    )
    
    async def test_agent():
        """測試 Agent 是否正常運作"""
        print("\n開始測試對話...")
        
        # 建立會話
        session = await session_service.create_session(
            app_name="not_chat_gpt",
            user_id="test_user"
        )
        
        # 建立訊息
        message = types.Content(
            role="user",
            parts=[types.Part(text="你好！請介紹一下你自己")]
        )
        
        # 執行對話
        print("\n💬 User: 你好！請介紹一下你自己\n")
        print("🤖 Assistant: ", end="")
        
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=message
        ):
            # 處理回應事件
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        
        print("\n\n✅ 測試完成！")
    
    # 執行測試
    asyncio.run(test_agent())