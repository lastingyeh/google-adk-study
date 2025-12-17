"""
Interactions API 互動展示 (Interactive Demo)

本腳本展示 Interactions API 的主要功能。
執行方式：python -m interactions_basic_agent.demo
"""

import os
import sys


def check_api_key():
    """檢查 API 金鑰是否已設定。"""
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ 未設定 GOOGLE_API_KEY！")
        print("")
        print("請設定您的 API 金鑰：")
        print("  export GOOGLE_API_KEY='your-key-here'")
        print("")
        print("取得金鑰： https://aistudio.google.com/apikey")
        sys.exit(1)


def run_basic_demo():
    """執行基礎互動展示。"""
    from . import create_basic_interaction

    print("=" * 60)
    print("1️⃣  基礎互動 (BASIC INTERACTION)")
    print("=" * 60)
    print("")
    print("發送中：'說個簡短的程式設計笑話。'")
    print("")

    try:
        result = create_basic_interaction(
            "說個簡短的程式設計笑話。"
        )
        print(f"📝 回應： {result['text']}")
        print(f"🆔 互動 ID： {result['id'][:20]}...")
        print("")
    except Exception as e:
        print(f"❌ 錯誤： {e}")
        print("")


def run_stateful_demo():
    """執行狀態對話展示。"""
    from . import create_stateful_conversation

    print("=" * 60)
    print("2️⃣  狀態對話 (STATEFUL CONVERSATION - 伺服器端狀態)")
    print("=" * 60)
    print("")
    print("此展示顯示 API 如何跨回合記住上下文。")
    print("")

    messages = [
        "我最喜歡的程式語言是 Python。",
        "我最喜歡的程式語言是什麼？",
    ]

    try:
        results = create_stateful_conversation(messages)

        for i, (msg, result) in enumerate(zip(messages, results), 1):
            print(f"👤 第 {i} 回合： {msg}")
            print(f"🤖 模型： {result['text']}")
            if result['previous_id']:
                print(f"   (連結至前次互動： {result['previous_id'][:20]}...)")
            print("")

    except Exception as e:
        print(f"❌ 錯誤： {e}")
        print("")


def run_streaming_demo():
    """執行串流展示。"""
    from . import create_streaming_interaction

    print("=" * 60)
    print("3️⃣  串流回應 (STREAMING RESPONSE)")
    print("=" * 60)
    print("")
    print("發送中：'從 1 數到 5，慢慢數。'")
    print("")
    print("🤖 回應 (串流中)： ", end="", flush=True)

    try:
        for chunk in create_streaming_interaction(
            "從 1 數到 5，每個數字之間加上簡短的暫停描述。"
        ):
            print(chunk, end="", flush=True)
        print("")
        print("")
    except Exception as e:
        print(f"\n❌ 錯誤： {e}")
        print("")


def run_function_calling_demo():
    """
    執行函數呼叫展示。

    Mermaid 流程圖：
    <div style='text-align: left;'>
    ```mermaid
    sequenceDiagram
        participant Demo
        participant API
        participant Tool

        Demo->>API: 詢問東京天氣
        API-->>Demo: 請求執行工具 (Tool Call)
        Demo->>Tool: 執行 get_weather
        Tool-->>Demo: 返回天氣資料
        Demo->>API: 傳送工具結果
        API-->>Demo: 最終天氣回答
    ```
    </div>
    """
    from . import create_function_calling_interaction, get_weather_tool
    from .tools import execute_tool

    print("=" * 60)
    print("4️⃣  函數呼叫 (FUNCTION CALLING)")
    print("=" * 60)
    print("")
    print("發送中：'東京的天氣如何？'")
    print("工具： get_weather")
    print("")

    try:
        result = create_function_calling_interaction(
            "東京的天氣如何？",
            tools=[get_weather_tool()],
            tool_executor=execute_tool
        )

        if result["tool_calls"]:
            print("🔧 工具呼叫 (Tool Calls)：")
            for call in result["tool_calls"]:
                print(f"   - {call['name']}({call['arguments']})")
            print("")

        if result["tool_results"]:
            print("📊 工具結果 (Tool Results)：")
            for res in result["tool_results"]:
                print(f"   - {res}")
            print("")

        print(f"🤖 最終回應： {result['text']}")
        print("")

    except Exception as e:
        print(f"❌ 錯誤： {e}")
        print("")


def main():
    """執行所有展示。"""
    print("")
    print("🚀 Interactions API 展示 (Demo)")
    print("========================")
    print("")
    print("此展示呈現 Google Interactions API 的主要功能。")
    print("")

    # 檢查 API 金鑰
    check_api_key()

    # 執行展示
    run_basic_demo()
    run_stateful_demo()
    run_streaming_demo()
    run_function_calling_demo()

    print("=" * 60)
    print("✅ 展示完成！")
    print("=" * 60)
    print("")
    print("了解更多：")
    print("- Interactions API 文件： https://ai.google.dev/gemini-api/docs/interactions")
    print("- Deep Research Agent： https://ai.google.dev/gemini-api/docs/deep-research")
    print("")


if __name__ == "__main__":
    main()

"""
=== 重點摘要 ===
- **核心概念**：透過實際程式碼展示 API 的各項功能運作方式。
- **關鍵技術**：
  - **環境檢查**：確保執行前具備必要的 API 金鑰。
  - **模組化展示**：將不同功能 (基礎、狀態、串流、工具) 分離為獨立函數，易於理解。
  - **錯誤處理**：使用 try-except 區塊捕捉並顯示執行錯誤。
- **重要結論**：此腳本可作為開發者快速驗證環境與理解 API 用法的起點。
- **行動項目**：
  - 設定 `GOOGLE_API_KEY` 後直接執行此腳本以驗證安裝。
"""
