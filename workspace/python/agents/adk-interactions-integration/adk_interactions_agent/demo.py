#!/usr/bin/env python3
"""
ADK Interactions Agent 演示腳本

此腳本展示如何透過 ADK 網頁介面及程式化方式，
執行整合 Interactions API 的 ADK 代理。

用法：
    # 互動式演示
    python -m adk_interactions_agent.demo

    # 或直接執行模組
    python demo.py

    # 啟動 ADK 網頁介面
    make dev
"""

import asyncio
import os
import sys
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def check_environment() -> bool:
    """檢查是否設定了必要的環境變數。"""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 錯誤: 未設定 GOOGLE_API_KEY 環境變數")
        print("\n修正方式：")
        print("  1. 複製 .env.example 為 .env")
        print("  2. 填入您的 Google API Key")
        print("  3. 再次執行此腳本")
        return False
    print("✅ GOOGLE_API_KEY 已設定")
    return True


def print_demo_header():
    """列印演示標題與資訊。"""
    print("=" * 60)
    print("  ADK Interactions Agent 演示")
    print("  展示 Google Interactions API + ADK 整合")
    print("=" * 60)
    print()


def print_demo_prompts():
    """列印建議的演示提示詞。"""
    prompts = [
        ("🌤️ 天氣查詢", "What's the weather like in Tokyo?"),
        ("🔢 數學計算", "Calculate 15% of 250 plus 100"),
        ("🔍 知識搜尋", "Tell me about machine learning"),
        ("🔄 多重工具", "What's the weather in Paris? Also calculate 20% tip on $85"),
        ("💭 推理能力", "Compare the weather in New York and London"),
    ]

    print("📋 建議的演示提示詞 (Suggested Demo Prompts)：\n")
    for emoji_name, prompt in prompts:
        print(f"  {emoji_name}:")
        print(f"    \"{prompt}\"\n")


def print_adk_web_instructions():
    """列印 ADK 網頁介面使用說明。"""
    print("🌐 ADK 網頁介面 (ADK Web Interface)：\n")
    print("  啟動互動式網頁 UI：")
    print("    make dev")
    print("    # 或")
    print("    adk web")
    print()
    print("  然後在瀏覽器開啟 http://localhost:8000")
    print("  從下拉選單選擇 'adk_interactions_agent'")
    print()


def print_programmatic_example():
    """列印程式化使用範例。"""
    print("💻 程式化使用範例 (Programmatic Usage Example)：\n")
    code = '''
from adk_interactions_agent import root_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# 建立 Session 與 Runner
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name="demo",
    user_id="user_1"
)

runner = Runner(
    agent=root_agent,
    session_service=session_service
)

# 執行查詢
response = runner.run(
    session_id=session.id,
    user_message="What's the weather in Tokyo?"
)

print(response.output)
'''
    print(code)


async def run_interactive_demo():
    """如果 API Key 可用，則執行互動式演示。"""
    try:
        from google import genai
        from google.genai import types

        print("🚀 執行互動式演示 (Interactive Demo)...\n")

        client = genai.Client()

        # 直接演示 Interactions API
        print("📨 測試 Interactions API 連線...")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello! Please respond with a brief greeting.",
        )

        print(f"✅ 連線成功！")
        print(f"   回覆: {response.text[:100]}...")
        print()

        return True

    except ImportError:
        print("⚠️ 無法載入 google-genai 套件以進行互動式演示")
        return False
    except Exception as e:
        print(f"⚠️ 互動式演示錯誤: {e}")
        return False


def main():
    """演示主要入口點。"""
    print_demo_header()

    # 檢查環境
    if not check_environment():
        print()
        sys.exit(1)

    print()

    # 列印可用演示
    print_demo_prompts()
    print("-" * 60)
    print()

    print_adk_web_instructions()
    print("-" * 60)
    print()

    print_programmatic_example()
    print("-" * 60)
    print()

    # 詢問是否執行互動式演示
    print("🎯 快速測試 (Quick Test)：\n")
    try:
        asyncio.run(run_interactive_demo())
    except KeyboardInterrupt:
        print("\n\n演示已取消。")

    print()
    print("=" * 60)
    print("  演示完成！嘗試執行 'make dev' 以啟動網頁介面。")
    print("=" * 60)


if __name__ == "__main__":
    main()

# 重點摘要
#
# - **核心概念**：提供使用者驗證環境與體驗代理功能的演示腳本。
# - **關鍵技術**：asyncio, google-genai Client, Environment Validation。
# - **重要結論**：在開始開發前，透過此腳本確認 API Key 與基本連線功能正常。
# - **行動項目**：執行 `python -m adk_interactions_agent.demo` 進行測試。
