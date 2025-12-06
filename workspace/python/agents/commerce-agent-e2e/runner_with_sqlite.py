#!/usr/bin/env python3
"""
Commerce Agent Runner with SQLite Session Persistence
具備 SQLite 會話持久性的商務代理人 Runner

This demonstrates using DatabaseSessionService with SQLite for persistent session storage.
Sessions and user preferences survive application restarts.
這展示了使用 DatabaseSessionService 搭配 SQLite 進行持久化會話儲存。
會話和使用者偏好在應用程式重啟後仍然存在。

Usage:
    python runner_with_sqlite.py

Features:
    - SQLite database for session persistence (sessions.db) (使用 SQLite 資料庫進行會話持久化)
    - Multi-user support with complete isolation (具備完整隔離的多用戶支援)
    - Conversation history preserved across restarts (跨重啟保存對話歷史記錄)
    - User preferences persisted in database (使用者偏好持久化於資料庫中)
    - Grounding metadata callback enabled (啟用接地元數據回調)

Database:
    - Location: ./commerce_agent_sessions.db
    - WAL mode enabled for better concurrency (啟用 WAL 模式以獲得更好的並行性)
    - Automatic schema creation (自動建立架構)
"""

import asyncio
import os
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from commerce_agent import root_agent, create_grounding_callback


async def create_session_for_user(
    session_service: DatabaseSessionService,
    user_id: str,
    app_name: str = "commerce_agent"
):
    """
    為使用者建立或檢索會話。

    Args:
        session_service: DatabaseSessionService instance (DatabaseSessionService 實例)
        user_id: Unique user identifier (唯一使用者識別碼)
        app_name: Application name (default: commerce_agent) (應用程式名稱)

    Returns:
        Session object with user's state and conversation history
        (包含使用者狀態和對話歷史記錄的 Session 物件)
    """
    # List existing sessions for user (列出使用者的現有會話)
    sessions = await session_service.list_sessions(
        app_name=app_name,
        user_id=user_id
    )

    if sessions['total_count'] > 0:
        # Use most recent session (使用最近的會話)
        latest_session = sessions['sessions'][0]
        print(f"📋 Found existing session (找到現有會話): {latest_session.id}")
        print(f"   State (狀態): {latest_session.state}")
        print(f"   Events (事件數): {len(latest_session.events)}")
        return latest_session
    else:
        # Create new session (建立新會話)
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            state={}  # Empty initial state (空的初始狀態)
        )
        print(f"✨ Created new session (建立新會話): {session.id}")
        return session


async def run_agent_with_sqlite():
    """
    使用 SQLite 持久化會話執行商務代理人。

    This demonstrates (這展示了):
    1. DatabaseSessionService initialization with SQLite (使用 SQLite 初始化 DatabaseSessionService)
    2. Session creation/retrieval (會話建立/檢索)
    3. Running agent with persistent state (使用持久化狀態執行代理人)
    4. Verifying persistence across invocations (驗證跨調用的持久性)
    """

    # ============================================================
    # 步驟 1：使用 SQLite 初始化 DatabaseSessionService
    # ============================================================

    # 使用具備 Write-Ahead Logging (WAL) 模式的 SQLite 以獲得更好的並行性
    db_url = "sqlite:///./commerce_agent_sessions.db?mode=wal"

    session_service = DatabaseSessionService(db_url=db_url)
    print(f"✅ DatabaseSessionService initialized (DatabaseSessionService 已初始化)")
    print(f"   Database (資料庫): {db_url}")

    # ============================================================
    # 步驟 2：使用會話服務建立 Runner
    # ============================================================

    runner = Runner(
        agent=root_agent,
        app_name="commerce_agent",
        session_service=session_service,
        after_model_callbacks=[create_grounding_callback(verbose=True)]
    )
    print(f"✅ Runner initialized with SQLite session service (Runner 已使用 SQLite 會話服務初始化)")

    # ============================================================
    # 步驟 3：為使用者建立/檢索會話
    # ============================================================

    user_id = "athlete_test_001"
    session = await create_session_for_user(session_service, user_id)

    print(f"\n{'='*60}")
    print(f"Starting conversation with session (開始會話): {session.id}")
    print(f"{'='*60}\n")

    # ============================================================
    # 步驟 4：首次互動 - 設定偏好
    # ============================================================

    message_1 = "I want running shoes under €150. I'm a beginner."

    print(f"👤 User (使用者): {message_1}\n")

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message={
            "role": "user",
            "parts": [{"text": message_1}]
        }
    ):
        if event.is_final_response():
            print(f"🤖 Agent (代理人): {event.content}\n")

    # ============================================================
    # 步驟 5：驗證狀態已持久化至 SQLite
    # ============================================================

    session_after_first = await session_service.get_session(
        app_name="commerce_agent",
        user_id=user_id,
        session_id=session.id
    )

    print(f"\n{'='*60}")
    print(f"Session state after first interaction (首次互動後的會話狀態):")
    print(f"{'='*60}")
    print(f"State (狀態): {session_after_first.state}")
    print(f"Events (事件數): {len(session_after_first.events)}")
    print(f"Last update (最後更新): {session_after_first.last_update_time}")

    # ============================================================
    # 步驟 6：第二次互動 - 使用已儲存的偏好
    # ============================================================

    message_2 = "Show me some options"

    print(f"\n{'='*60}")
    print(f"Second interaction (preferences should be remembered) (第二次互動 - 應記住偏好):")
    print(f"{'='*60}\n")
    print(f"👤 User (使用者): {message_2}\n")

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message={
            "role": "user",
            "parts": [{"text": message_2}]
        }
    ):
        if event.is_final_response():
            print(f"🤖 Agent (代理人): {event.content}\n")

    # ============================================================
    # 步驟 7：驗證最終狀態持久性
    # ============================================================

    session_final = await session_service.get_session(
        app_name="commerce_agent",
        user_id=user_id,
        session_id=session.id
    )

    print(f"\n{'='*60}")
    print(f"Final session state (persisted in SQLite) (最終會話狀態 - 持久化於 SQLite):")
    print(f"{'='*60}")
    print(f"Session ID: {session_final.id}")
    print(f"User ID: {session_final.user_id}")
    print(f"State: {session_final.state}")
    print(f"Total events: {len(session_final.events)}")
    print(f"Last update: {session_final.last_update_time}")

    # ============================================================
    # 步驟 8：展示跨「重啟」的持久性
    # ============================================================

    print(f"\n{'='*60}")
    print(f"Simulating application restart... (模擬應用程式重啟...)")
    print(f"{'='*60}\n")

    # Create new session service (simulating app restart)
    # 建立新的會話服務 (模擬應用程式重啟)
    new_session_service = DatabaseSessionService(db_url=db_url)

    # Retrieve session from database
    # 從資料庫檢索會話
    restored_session = await new_session_service.get_session(
        app_name="commerce_agent",
        user_id=user_id,
        session_id=session.id
    )

    if restored_session:
        print(f"✅ Session restored from SQLite database! (已從 SQLite 資料庫恢復會話！)")
        print(f"   Session ID: {restored_session.id}")
        print(f"   User preferences preserved (使用者偏好已保存):")

        for key, value in restored_session.state.items():
            if key.startswith("user:"):
                print(f"      - {key}: {value}")

        print(f"   Conversation history: {len(restored_session.events)} events (對話歷史記錄：{len(restored_session.events)} 個事件)")
    else:
        print(f"❌ Failed to restore session (恢復會話失敗)")

    print(f"\n{'='*60}")
    print(f"SQLite Session Persistence Demo Complete! (SQLite 會話持久性展示完成！)")
    print(f"{'='*60}")
    print(f"Database location (資料庫位置): ./commerce_agent_sessions.db")
    print(f"You can inspect the database with (您可以使用以下指令檢查資料庫): sqlite3 commerce_agent_sessions.db")


async def demo_multi_user():
    """
    展示使用 SQLite 的多用戶隔離。

    顯示不同使用者擁有完全隔離的會話和狀態。
    """

    print(f"\n{'='*60}")
    print(f"MULTI-USER ISOLATION DEMO (多用戶隔離展示)")
    print(f"{'='*60}\n")

    db_url = "sqlite:///./commerce_agent_sessions.db?mode=wal"
    session_service = DatabaseSessionService(db_url=db_url)

    # Create sessions for two different users
    # 為兩個不同使用者建立會話
    alice_session = await session_service.create_session(
        app_name="commerce_agent",
        user_id="alice@example.com",
        state={
            "user:sport": "running",
            "user:budget": 150,
            "user:experience": "advanced"
        }
    )

    bob_session = await session_service.create_session(
        app_name="commerce_agent",
        user_id="bob@example.com",
        state={
            "user:sport": "cycling",
            "user:budget": 300,
            "user:experience": "beginner"
        }
    )

    print(f"✅ Alice's session: {alice_session.id}")
    print(f"   State: {alice_session.state}")

    print(f"\n✅ Bob's session: {bob_session.id}")
    print(f"   State: {bob_session.state}")

    # 檢索並驗證隔離
    alice_restored = await session_service.get_session(
        app_name="commerce_agent",
        user_id="alice@example.com",
        session_id=alice_session.id
    )

    bob_restored = await session_service.get_session(
        app_name="commerce_agent",
        user_id="bob@example.com",
        session_id=bob_session.id
    )

    print(f"\n{'='*60}")
    print(f"Verification: Complete isolation between users (驗證：使用者間完全隔離)")
    print(f"{'='*60}")
    print(f"Alice's sport: {alice_restored.state['user:sport']}")
    print(f"Bob's sport: {bob_restored.state['user:sport']}")

    assert alice_restored.state['user:sport'] == 'running'
    assert bob_restored.state['user:sport'] == 'cycling'

    print(f"\n✅ Multi-user isolation verified! (多用戶隔離已驗證！)")


if __name__ == "__main__":
    # Set API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY not set")
        print("   Export your API key: export GOOGLE_API_KEY=your_key")
        exit(1)

    print(f"\n{'='*60}")
    print(f"COMMERCE AGENT - SQLITE SESSION PERSISTENCE (商務代理人 - SQLite 會話持久性)")
    print(f"{'='*60}\n")

    # Run main demo
    asyncio.run(run_agent_with_sqlite())

    # Run multi-user demo
    asyncio.run(demo_multi_user())
