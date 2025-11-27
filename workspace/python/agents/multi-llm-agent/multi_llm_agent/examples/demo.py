#!/usr/bin/env python3
"""
教學 28 範例：Multi-LLM Agent 範例
展示如何透過 LiteLLM 搭配範例查詢使用不同的 LLM
"""

import asyncio
import os
import sys
from typing import Dict, Any

# 將父目錄加入 Python 路徑以便匯入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types

from multi_llm_agent.agent import root_agent, gpt4o_agent, claude_agent, ollama_agent


async def run_query(agent, query: str, description: str) -> Dict[str, Any]:
    """使用指定的 agent 執行查詢並返回結果。"""
    print(f"\n🤖 {description}")
    print(f"💬 查詢: {query}")
    print("-" * 50)

    try:
        # 建立 runner 和 session 服務
        session_service = InMemorySessionService()
        runner = Runner(app_name="multi_llm_demo", agent=agent, session_service=session_service)

        # 為此對話建立一個 session
        session = await session_service.create_session(
            app_name="multi_llm_demo",
            user_id="demo_user"
        )

        # 設定為非串流模式 (取得完整回應)
        run_config = RunConfig(
            streaming_mode=StreamingMode.NONE,
            max_llm_calls=50
        )

        # 收集所有回應片段
        response_parts = []

        # 使用查詢執行 agent
        async for event in runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=query)]),
            run_config=run_config
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_parts.append(part.text)

            if event.turn_complete:
                break

        result = ''.join(response_parts)
        print(f"📝 回應: {result}")
        return {"success": True, "result": result, "description": description}

    except Exception as e:
        error_msg = f"❌ 使用 {description} 時發生錯誤: {str(e)}"
        print(error_msg)
        return {"success": False, "error": str(e), "description": description}


async def demo_basic_math():
    """展示使用不同 LLM 進行基本數學計算。"""
    print("\n" + "="*60)
    print("🧮 範例 1: 數學計算")
    print("="*60)

    query = "15 的平方是多少？請使用 calculate_square 工具。"

    # 使用不同的 agent 進行測試
    agents = [
        (root_agent, "OpenAI GPT-4o-mini (預設)"),
        (gpt4o_agent, "OpenAI GPT-4o-mini (替代方案)"),
        (claude_agent, "Claude 3.7 Sonnet"),
        (ollama_agent, "Ollama Granite 4 (本地)"),
    ]

    results = []
    for agent, desc in agents:
        result = await run_query(agent, query, desc)
        results.append(result)

    return results


async def demo_weather_info():
    """展示天氣資訊檢索。"""
    print("\n" + "="*60)
    print("🌤️  範例 2: 天氣資訊")
    print("="*60)

    query = "舊金山目前的天氣如何？請使用 get_weather 工具。"

    agents = [
        (root_agent, "OpenAI GPT-4o-mini"),
        (claude_agent, "Claude 3.7 Sonnet"),
        (ollama_agent, "Ollama Granite 4 (本地)"),
    ]

    results = []
    for agent, desc in agents:
        result = await run_query(agent, query, desc)
        results.append(result)

    return results


async def demo_sentiment_analysis():
    """展示文字情緒分析。"""
    print("\n" + "="*60)
    print("😊 範例 3: 情緒分析")
    print("="*60)

    query = "分析這段文字的情緒：'我非常喜歡這個新的人工智慧技術！它極具創新性，徹底改變了我的工作方式。'"

    agents = [
        (root_agent, "OpenAI GPT-4o-mini"),
        (gpt4o_agent, "OpenAI GPT-4o-mini"),
        (claude_agent, "Claude 3.7 Sonnet"),
        (ollama_agent, "Ollama Granite 4 (本地)"),
    ]

    results = []
    for agent, desc in agents:
        result = await run_query(agent, query, desc)
        results.append(result)

    return results


async def demo_comparison():
    """展示比較不同 LLM 的回應。"""
    print("\n" + "="*60)
    print("⚖️  範例 4: LLM 比較")
    print("="*60)

    query = "用一個 10 歲小孩能理解的簡單詞彙解釋量子計算。"

    print(f"🎯 查詢: {query}")
    print("\n" + "-"*60)

    agents = [
        (root_agent, "OpenAI GPT-4o-mini"),
        (claude_agent, "Claude 3.7 Sonnet"),
        (ollama_agent, "Ollama Granite 4 (本地)"),
    ]

    responses = {}
    for agent, desc in agents:
        try:
            # 建立 runner 和 session 服務
            session_service = InMemorySessionService()
            runner = Runner(app_name="multi_llm_demo", agent=agent, session_service=session_service)

            # 建立一個 session
            session = await session_service.create_session(
                app_name="multi_llm_demo",
                user_id="demo_user"
            )

            # 設定為非串流模式
            run_config = RunConfig(
                streaming_mode=StreamingMode.NONE,
                max_llm_calls=50
            )

            # 收集回應
            response_parts = []
            async for event in runner.run_async(
                user_id="demo_user",
                session_id=session.id,
                new_message=types.Content(role="user", parts=[types.Part(text=query)]),
                run_config=run_config
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)

                if event.turn_complete:
                    break

            result = ''.join(response_parts)
            responses[desc] = result
            print(f"\n🤖 {desc}:")
            print(f"   {result}")
        except Exception as e:
            print(f"\n❌ {desc}: 錯誤 - {str(e)}")

    return responses


async def main():
    """主要範例函式。"""
    print("🚀 教學 28: Multi-LLM Agent 範例")
    print("使用 LiteLLM 存取 OpenAI, Claude, 以及其他 LLM")
    print("="*60)

    # 檢查必要的 API 金鑰
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_ollama = True  # 假設 Ollama 在本地可用

    print("🔑 API 金鑰狀態:")
    print(f"   OpenAI: {'✅' if has_openai else '❌'} (GPT 模型需要)")
    print(f"   Anthropic: {'✅' if has_anthropic else '❌'} (Claude 需要)")
    print(f"   Ollama: {'✅' if has_ollama else '❌'} (本地 Granite 4 模型)")
    print()

    if not has_openai and not has_anthropic and not has_ollama:
        print("⚠️  警告：未偵測到 API 金鑰或本地模型。範例可能會執行失敗。")
        print("   請設定 OPENAI_API_KEY, ANTHROPIC_API_KEY, 或確保 Ollama 正在執行。")
        print()

    # 執行範例
    try:
        await demo_basic_math()
        await demo_weather_info()
        await demo_sentiment_analysis()
        await demo_comparison()

        print("\n" + "="*60)
        print("✅ 範例執行完畢！")
        print("="*60)
        print("💡 核心要點:")
        print("   • LiteLLM 讓切換 LLM 供應商變得簡單")
        print("   • 每個 LLM 都有不同的優勢 (成本、速度、推理能力)")
        print("   • 工具在不同模型之間能一致地運作")
        print("   • 像 Ollama (Granite 4) 這樣的本地模型提供隱私和離線能力")

    except KeyboardInterrupt:
        print("\n⏹️  使用者中斷範例執行")
    except Exception as e:
        print(f"\n❌ 範例因錯誤而失敗: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
