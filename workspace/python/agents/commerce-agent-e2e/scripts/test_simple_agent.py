#!/usr/bin/env python3
"""Test script for simplified commerce agent. (簡化版商務代理人的測試腳本)"""

import asyncio
import os
import sys

# Add parent directory to path (將父目錄加入路徑)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from commerce_agent.agent import root_agent  # Updated import path (更新匯入路徑)


async def test_agent():
    """Test the simplified agent with a sample query. (使用範例查詢測試簡化版代理人)"""

    print("\n" + "="*60)
    print("Testing Simplified Commerce Agent (正在測試簡化版商務代理人)")
    print("="*60 + "\n")

    # Use in-memory session service for testing (使用記憶體內會話服務進行測試)
    session_service = InMemorySessionService()
    runner = Runner(
        session_service=session_service,
        app_name="commerce_agent",
        agent=root_agent
    )

    # Test 1: Simple product search (測試 1：簡單產品搜尋)
    print("Test 1: Simple Search (測試 1：簡單搜尋)")
    print("-" * 40)
    result = await runner.run_async(
        "I want to buy trail running shoes under 100 euros"
    )

    print("\n🤖 Agent Response (代理人回應):")
    print(result.content.parts[0].text)
    print("\n" + "="*60 + "\n")

    # Test 2: With preferences (測試 2：帶有偏好)
    print("Test 2: Save Preferences (測試 2：儲存偏好)")
    print("-" * 40)
    result2 = await runner.run_async(
        "I'm a beginner runner, budget is 100 euros max, interested in trail running",
        session_id="test_session_123"
    )

    print("\n🤖 Agent Response (代理人回應):")
    print(result2.content.parts[0].text)
    print("\n" + "="*60 + "\n")

    # Test 3: Search using saved preferences (測試 3：使用已儲存的偏好進行搜尋)
    print("Test 3: Search with Saved Preferences (測試 3：使用已儲存的偏好搜尋)")
    print("-" * 40)
    result3 = await runner.run_async(
        "Show me some shoes based on my preferences",
        session_id="test_session_123"
    )

    print("\n🤖 Agent Response (代理人回應):")
    print(result3.content.parts[0].text)

    print("\n" + "="*60)
    print("✅ Test Complete! (測試完成！)")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Check for API key (檢查 API 金鑰)
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable not set (錯誤：未設定 GOOGLE_API_KEY 環境變數)")
        print("Set it with: export GOOGLE_API_KEY=your_key (請使用 export GOOGLE_API_KEY=your_key 設定)")
        sys.exit(1)

    asyncio.run(test_agent())
