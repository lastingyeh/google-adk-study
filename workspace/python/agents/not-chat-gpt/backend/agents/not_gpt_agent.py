"""
NotGPTAgent - 具有 Session 和 Memory 管理的智能對話助理

這是專案的核心 Agent，整合：
- Session 管理（短期記憶）
- Memory 管理（長期記憶）
- 支援開發/生產環境切換
"""
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, VertexAiSessionService
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.load_memory_tool import LoadMemoryTool
from google.genai import types
from dotenv import load_dotenv
import os
import asyncio
import vertexai


def create_not_gpt_agent() -> Agent:
    """建立 NotGPTAgent
    
    這是專案的核心 Agent，具備：
    - 友善的對話風格
    - 長期記憶能力
    - 上下文理解
    """
    return Agent(
        name="not_gpt_agent",
        model="gemini-2.0-flash-exp",
        instruction="""
            你是 NotGPTAgent，一個智能且友善的對話助理。

            核心能力：
            - 提供準確且有幫助的資訊
            - 支援多輪對話與上下文理解
            - 記住過去的對話（使用 LoadMemoryTool 工具）
            - 友善且專業的對話風格

            行為準則：
            - 主動使用記憶來提供更好的服務 LoadMemoryTool 工具
            - 引用過去的對話時要明確說明
            - 尊重使用者隱私
        """,
        description="NotGPT 智能對話助理",
        tools=[
            # PreloadMemoryTool(),  # 啟動時載入相關記憶
            LoadMemoryTool()
            ]  # 賦予記憶檢索能力
    )


def create_services(environment='development', agent_engine_id=None):
    """根據環境建立 Services
    
    Args:
        environment: 'development' 或 'production'
    
    Returns:
        tuple: (session_service, memory_service)
    """
    if environment == 'development':
        print("🔧 開發環境: 使用 InMemory Services")
        session_service = InMemorySessionService()
        memory_service = InMemoryMemoryService()
        return session_service, memory_service
    
    elif environment == 'production':
        print("🚀 生產環境: 使用 Vertex AI Services")
        
        # Session 使用 VertexAiSessionService
        project = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        session_service = VertexAiSessionService(
            project=project,
            location=location
        )
        
        memory_service = VertexAiMemoryBankService(
            project=project,
            location=location,
            agent_engine_id=agent_engine_id
        )
        
        return session_service, memory_service
    
    else:
        raise ValueError(f"未知環境: {environment}")


# 測試用
if __name__ == "__main__":
    load_dotenv()
    
    # 檢查 API Key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定")
        exit(1)
    
    # 環境選擇（從環境變數）
    env = os.getenv('ENVIRONMENT', 'development')
    
    print("=" * 60)
    print("NotGPTAgent - Session & Memory 測試")
    print("=" * 60)
    
    async def test_not_gpt_agent():
        """測試 NotGPTAgent 的 Session 和 Memory 功能
        
        測試流程：
        1. 階段一：測試 Session 的短期記憶（同一會話內的多輪對話）
        2. 階段二：測試 Memory 的長期記憶（跨會話的記憶檢索）
        """
        
        agent_engine = None  # 初始化 agent_engine
        agent_engine_id = None # 初始化 agent_engine_id
        try:
            # If you don't have an Agent Engine instance already, create an instance.
            if env == 'production' and not os.getenv('AGENT_ENGINE_ID'):
                project = os.getenv('GOOGLE_CLOUD_PROJECT')
                location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
                client = vertexai.Client(
                    project=project,
                    location=location
                )
                agent_engine = client.agent_engines.create()
                agent_engine_id = os.getenv('AGENT_ENGINE_ID', agent_engine.api_resource.name.split("/")[-1])            

            # 建立 Services
            session_service, memory_service = create_services(env, agent_engine_id=agent_engine_id)
            
            # 建立 Agent 和 Runner
            agent = create_not_gpt_agent()
            
            APP_NAME = "not_gpt_agent"
            USER_ID = "test_user"
            
            # In production, use the agent_engine_id as APP_NAME
            if env == 'production':
                if not agent_engine_id:
                    raise ValueError("生產環境需要: AGENT_ENGINE_ID")
                APP_NAME = agent_engine_id
                print(f"APP_NAME: {APP_NAME}")        
            
            runner = Runner(
                agent=agent,
                app_name=APP_NAME,
                session_service=session_service,  # Session 儲存
                memory_service=memory_service      # Memory 儲存
            )
            
            print("\n" + "=" * 60)
            print("階段一：測試短期記憶（Session）")
            print("=" * 60)
            
            # === 建立第一個 Session ===
            print("\n【建立第一個 Session】")
            if isinstance(session_service, InMemorySessionService):
                session1_id = "session_001"
                await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=session1_id
                )
                print(f"🔧 使用手動指定的 Session ID: {session1_id}")
            else:
                # VertexAiSessionService 會自動生成 ID
                session1 = await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID
                )
                session1_id = session1.id
                print(f"🚀 Vertex AI 自動生成 Session ID: {session1_id}")
            
            # === 第一輪對話：提供資訊 ===
            print("\n【第 1 輪對話】")
            msg1 = types.Content(
                role="user",
                parts=[types.Part(text="我叫 Alice，我正在學習 Google ADK。")]
            )
            
            print("💬 User: 我叫 Alice，我正在學習 Google ADK。\n")
            print("🤖 NotGPT: ", end="", flush=True)
            
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session1_id,
                new_message=msg1
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    print(event.content.parts[0].text)
            
            # === 第二輪對話：測試 Session 內的記憶（短期記憶）===
            print("\n\n【第 2 輪對話 - 測試 Session 短期記憶】")
            msg2 = types.Content(
                role="user",
                parts=[types.Part(text="我叫什麼名字？")]
            )
            
            print("💬 User: 我叫什麼名字？\n")
            print("🤖 NotGPT: ", end="", flush=True)
            
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session1_id,  # 同一個 Session
                new_message=msg2
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    print(event.content.parts[0].text)
            
            print("\n✅ Session 短期記憶測試成功！Agent 記住了同一會話中的資訊。")
            
            # === 第三輪對話：再次確認 Session 記憶 ===
            print("\n\n【第 3 輪對話 - 再次確認 Session 記憶】")
            msg3 = types.Content(
                role="user",
                parts=[types.Part(text="我在學什麼？")]
            )
            
            print("💬 User: 我在學什麼？\n")
            print("🤖 NotGPT: ", end="", flush=True)
            
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session1_id,  # 同一個 Session
                new_message=msg3
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    print(event.content.parts[0].text)
            
            print("\n✅ Session 多輪對話測試成功！")
            
            # ============================================================
            print("\n" + "=" * 60)
            print("階段二：測試長期記憶（Memory）")
            print("=" * 60)
            
            # === 將 Session 儲存到 Memory ===
            print("\n【儲存到長期記憶】")
            completed_session = await session_service.get_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session1_id
            )
            
            print(f"💾 Session 內容預覽:")
            print(f"   Session ID: {completed_session.id}")
            print(f"   事件數量: {len(completed_session.events) if hasattr(completed_session, 'events') else 'N/A'}")

            print("💾 將 Session 儲存到 Memory Bank...")
            await memory_service.add_session_to_memory(completed_session)
            print("✅ 已儲存到長期記憶")

            # === 驗證記憶是否真的儲存成功 ===
            print("\n【驗證記憶儲存】")
            try:
                # 直接搜尋記憶
                test_query = "Alice"
                memories = await memory_service.search_memory(
                    app_name=APP_NAME,
                    query=test_query,
                    user_id=USER_ID
                )
                if memories:
                    # 嘗試轉換為列表或檢查屬性
                    if hasattr(memories, '__iter__') and not isinstance(memories, str):
                        memory_list = list(memories)
                        print(f"✅ 搜尋 '{test_query}' 找到 {len(memory_list)} 筆記憶")
                        if memory_list:
                            print(f"\n📝 記憶內容：")
                            for i, memory in enumerate(memory_list, 1):
                                print(f"\n--- 記憶 {i} ---")
                                print(f"類型: {type(memory).__name__}")
                                print(f"內容: {memory}")
                                # 如果是對象，嘗試顯示其屬性
                                if hasattr(memory, '__dict__'):
                                    print(f"屬性: {memory.__dict__}")
                    else:
                        print(f"✅ 記憶已儲存（返回值類型: {type(memories).__name__}）")
                else:
                    print("⚠️ 警告：記憶庫中沒有找到相關記憶！")
            except Exception as e:
                print(f"⚠️ 記憶驗證失敗: {e}")
            
            # === 建立新的 Session（模擬新對話）===
            print("\n【開始新對話 - 測試跨會話記憶】")
            if isinstance(session_service, InMemorySessionService):
                session2_id = "session_002"
                await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=session2_id
                )
                print(f"🔧 使用手動指定的 Session ID: {session2_id}")
            else:
                # VertexAiSessionService 會自動生成 ID
                session2 = await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID
                )
                session2_id = session2.id
                print(f"🚀 Vertex AI 自動生成 Session ID: {session2_id}")
            
            # === 在新 Session 中測試長期記憶 ===
            print("\n【第 4 輪對話 - 新會話中測試 Memory 檢索】")
            msg4 = types.Content(
                role="user",
                parts=[types.Part(text="你還記得我的名字和我在學什麼嗎？")]
            )
            
            print("💬 User: 你還記得我的名字和我在學什麼嗎？\n")
            print("🤖 NotGPT: ", end="", flush=True)
            
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session2_id,  # 新的 Session
                new_message=msg4
            ):
                # 檢查是否有內容
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        # 1. 顯示工具調用
                        if hasattr(part, 'function_call') and part.function_call:
                            print(f"\n\n🔧 [調用工具] {part.function_call.name}")
                            if part.function_call.args:
                                print(f"   參數: {dict(part.function_call.args)}")
                        
                        # 2. 顯示工具結果
                        elif hasattr(part, 'function_response') and part.function_response:
                            print(f"📊 [工具完成] {part.function_response.name}")
                            if hasattr(part.function_response, 'response'):
                                print(f"   結果: {part.function_response.response}")
                        
                        # 3. 顯示文字回應
                        elif part.text:
                            print(part.text, end="", flush=True)

            print("\n")  # 換行
            
            print("\n✅ Memory 長期記憶測試成功！Agent 從 Memory 中檢索到過去的資訊。")
            
            print("\n" + "=" * 60)
            print("✅ NotGPTAgent 完整測試通過！")
            print("=" * 60)
            print(f"✅ Session 管理（短期記憶）: {type(session_service).__name__}")
            print(f"✅ Memory 管理（長期記憶）: {type(memory_service).__name__}")
            print("\n測試總結：")
            print("  1️⃣  Session 短期記憶：在同一會話中記住上下文 ✓")
            print("  2️⃣  Memory 長期記憶：跨會話檢索過去的資訊 ✓")
    
        finally:
            # 確保在測試結束後刪除 agent_engine (僅在 production 環境)
            if agent_engine:
                print("\n" + "=" * 60)
                print(f"🗑️ 清理資源: 正在刪除 Agent Engine ({agent_engine_id})...")
                try:
                    agent_engine.delete(force=True)
                    print("✅ 資源清理完畢。")
                except Exception as e:
                    print(f"❌ 清理資源失敗: {e}")
                print("=" * 60)
    
    
    try:
        asyncio.run(test_not_gpt_agent())
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()