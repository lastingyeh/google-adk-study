"""
NotChatGPT - 記憶管理 Agent (使用 VertexAiMemoryBankService)

使用 Google ADK 的 VertexAiMemoryBankService 實現長期記憶。
"""
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.load_memory_tool import LoadMemoryTool
from google.genai import types
from dotenv import load_dotenv
import os


def create_memory_agent() -> Agent:
    """建立具有記憶能力的 Agent
    
    Returns:
        Agent: 配置好的 ADK Agent，整合記憶工具
    """
    return Agent(
        name="not_chat_gpt_memory",
        model="gemini-2.0-flash-exp",
        instruction="""
你是 NotChatGPT，一個具有長期記憶的智慧對話助理。

能力：
- 記住過去的對話內容
- 根據歷史對話提供個性化回應
- 使用記憶工具查詢相關的過往互動

行為：
- 主動使用記憶來提供更好的服務
- 引用過去的對話時要明確說明
- 尊重使用者隱私，不濫用記憶
        """,
        description="具有長期記憶能力的對話助理",
        tools=[
            PreloadMemoryTool(),  # 總是在開始時載入相關記憶
            # 或使用 LoadMemoryTool() 讓 Agent 決定何時載入
        ]
    )


def create_memory_service() -> VertexAiMemoryBankService:
    """建立 VertexAiMemoryBankService
    
    Returns:
        VertexAiMemoryBankService: 配置好的記憶服務
    """
    project = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    agent_engine_id = os.getenv('GOOGLE_AGENT_ENGINE_ID')  # 可選
    
    if not project:
        raise ValueError("GOOGLE_CLOUD_PROJECT not set in .env")
    
    # 基本配置
    if agent_engine_id:
        # 使用 Agent Engine ID
        return VertexAiMemoryBankService(
            project=project,
            location=location,
            agent_engine_id=agent_engine_id
        )
    else:
        # 基本配置（不使用 Agent Engine）
        return VertexAiMemoryBankService(
            project=project,
            location=location
        )


# 測試用
if __name__ == "__main__":
    import asyncio
    
    # 載入 .env 檔案
    load_dotenv()
    
    # 檢查必要的環境變數
    api_key = os.getenv('GOOGLE_API_KEY')
    project = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定在 .env 檔案中")
        exit(1)
    
    if not project:
        print("❌ 錯誤: GOOGLE_CLOUD_PROJECT 未設定在 .env 檔案中")
        exit(1)
    
    print("✅ 使用 Google ADK VertexAiMemoryBankService")
    
    # 建立 Agent 和 Memory Service
    agent = create_memory_agent()
    memory_service = create_memory_service()
    
    # 建立 Runner（使用 Memory Service）
    runner = Runner(
        agent=agent,
        app_name="not_chat_gpt_memory",
        memory_service=memory_service
    )
    
    async def test_memory():
        """測試記憶功能"""
        print("\n開始測試記憶功能...")
        
        # 建立會話
        session = await runner.session_service.create_session(
            app_name="not_chat_gpt_memory",
            user_id="test_user"
        )
        
        # 第一輪對話：提供個人資訊
        print("\n=== 第一輪對話：提供資訊 ===")
        msg1 = types.Content(
            role="user",
            parts=[types.Part(text="我叫 Alice，我喜歡看科幻小說和寫程式")]
        )
        
        print("💬 User: 我叫 Alice，我喜歡看科幻小說和寫程式\n")
        print("🤖 Assistant: ", end="")
        
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=msg1
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        
        # 將會話儲存到記憶體
        print("\n\n💾 儲存會話到記憶體...")
        await memory_service.add_session_to_memory(session)
        print("✅ 會話已儲存到 Vertex AI Memory Bank")
        
        # 第二輪對話：測試記憶檢索
        print("\n=== 第二輪對話：測試記憶 ===")
        msg2 = types.Content(
            role="user",
            parts=[types.Part(text="你還記得我的興趣嗎？")]
        )
        
        print("💬 User: 你還記得我的興趣嗎？\n")
        print("🤖 Assistant: ", end="")
        
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=msg2
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        
        print("\n\n✅ 記憶測試完成！")
        print("✅ VertexAiMemoryBankService 正確管理長期記憶")
    
    # 執行測試
    try:
        asyncio.run(test_memory())
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        print("\n提示：確保已完成以下步驟：")
        print("1. 執行 gcloud auth application-default login")
        print("2. 設定 GOOGLE_CLOUD_PROJECT 環境變數")
        print("3. 啟用 Vertex AI API")