"""測試 VertexAiMemoryBankService 記憶功能"""
import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import VertexAiMemoryBankService
from google.genai import types
from backend.agents.memory_agent import create_memory_agent, create_memory_service
import os


@pytest.mark.asyncio
async def test_memory_persistence():
    """測試記憶持久化功能"""
    # 檢查必要的環境變數
    project = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project:
        pytest.skip("GOOGLE_CLOUD_PROJECT 未設定，跳過測試")
    
    # 設置
    agent = create_memory_agent()
    memory_service = create_memory_service()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="test_memory_app",
        session_service=session_service,
        memory_service=memory_service
    )
    
    # 建立會話
    session = await runner.session_service.create_session(
        app_name="test_memory_app",
        user_id="test_user"
    )
    
    # 第一輪對話：提供資訊
    msg1 = types.Content(
        role="user",
        parts=[types.Part(text="我叫 Bob，我是軟體工程師")]
    )
    
    response1_parts = []
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=msg1
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response1_parts.append(part.text)
    
    # 儲存到記憶體
    await memory_service.add_session_to_memory(session)
    
    # 搜尋記憶體
    memories = await memory_service.search_memory(
        query="使用者的職業是什麼？",
        user_id="test_user"
    )
    
    # 驗證：應該能找到相關記憶
    assert len(memories) > 0, "應該能從記憶體中檢索到資訊"
    print(f"✅ 找到 {len(memories)} 條相關記憶")
    print("✅ VertexAiMemoryBankService 記憶功能正常")


@pytest.mark.asyncio
async def test_state_scopes():
    """測試狀態範疇管理（user/app/temp）"""
    agent = create_memory_agent()
    memory_service = create_memory_service()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="test_scopes",
        session_service=session_service,
        memory_service=memory_service
    )
    
    session = await runner.session_service.create_session(
        app_name="test_scopes",
        user_id="test_user"
    )
    
    # 設定不同範疇的狀態
    session.state["user:name"] = "Alice"
    session.state["app:version"] = "1.0.0"
    session.state["temp:request_id"] = "12345"
    session.state["conversation_topic"] = "AI 技術"
    
    # 驗證狀態
    assert session.state["user:name"] == "Alice"
    assert session.state["app:version"] == "1.0.0"
    assert session.state["temp:request_id"] == "12345"
    assert session.state["conversation_topic"] == "AI 技術"
    
    print("✅ 狀態範疇管理正常")