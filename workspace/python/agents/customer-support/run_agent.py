# 教學 20：YAML 設定 - 代理人執行器
# 從 YAML 設定載入並執行代理人

import asyncio
import os
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.agents import config_agent_utils

# ADK 環境設定
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = os.environ.get('GOOGLE_CLOUD_PROJECT', 'your-project-id')
os.environ['GOOGLE_CLOUD_LOCATION'] = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')


async def main():
    """載入設定並使用測試查詢執行代理人。"""

    print("🤖 正在載入 YAML 設定的客戶支援代理人...")
    print("=" * 70)

    try:
        # 從 YAML 設定載入代理人
        # 這展示了如何從宣告式設定檔實例化代理人
        agent = config_agent_utils.from_config('root_agent.yaml')
        print(f"✅ 設定載入成功：{agent.name}")
        print(f"   工具：{len(agent.tools) if hasattr(agent, 'tools') else 0}")
        print()

    except Exception as e:
        print(f"❌ 載入設定失敗：{e}")
        return

    # 建立工作階段服務和執行器
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="yaml_config_demo",
        agent=agent,
        session_service=session_service
    )

    # 建立工作階段
    session_id = "demo_session"
    user_id = "demo_user"
    await session_service.create_session(
        session_id=session_id,
        user_id=user_id,
        app_name="yaml_config_demo"
    )

    # 展示不同工具功能的測試查詢
    queries = [
        "檢查客戶 CUST-001 的狀態",
        "訂單 ORD-001 的狀態為何？",
        "你能追蹤訂單 ORD-001 的運送狀況嗎？",
        "搜尋知識庫以解決登入問題",
        "針對連線問題執行診斷",
        "取得客戶 CUST-001 的帳單歷史記錄",
        "處理訂單 ORD-002 的 $50 退款"
    ]

    for i, query in enumerate(queries, 1):
        print(f"查詢 {i}: {query}")
        print("-" * 70)

        try:
            # 建立訊息內容
            from google.genai import types
            message = types.Content(
                parts=[types.Part(text=query)],
                role="user"
            )

            # 使用 ADK Runner 執行查詢
            response_events = []
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message
            ):
                response_events.append(event)
                if hasattr(event, 'content') and event.content:
                    print(f"事件: {event.content}")

            print(f"收到 {len(response_events)} 個事件")
            print()

        except Exception as e:
            print(f"❌ 執行查詢時發生錯誤：{e}")
            print()

        # 查詢之間的短暫延遲
        if i < len(queries):
            await asyncio.sleep(2)

    print("=" * 70)
    print("🎉 演示完成！YAML 設定的代理人運作正常。")


if __name__ == '__main__':
    asyncio.run(main())

# 重點摘要
# - **核心概念**：示範如何使用 `config_agent_utils` 從 YAML 檔案載入代理人並執行。
# - **關鍵技術**：`google.adk.runners.Runner`, `google.adk.agents.config_agent_utils`, `asyncio`。
# - **重要結論**：程式碼展示了宣告式代理人的加載、Session 服務的初始化以及非同步查詢處理流程。
# - **行動項目**：執行此腳本以驗證 YAML 設定是否正確並觀察代理人回應。

