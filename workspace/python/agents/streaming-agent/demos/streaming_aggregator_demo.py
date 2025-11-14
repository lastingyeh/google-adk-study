"""
StreamingResponseAggregator 展示 - 教學 14

展示使用 ADK 串流 API 進行回應聚合。
注意：ADK 可能沒有 StreamingResponseAggregator 類別，因此我們手動實現聚合。
"""

import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 環境設定
os.environ.setdefault('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE')


class ManualStreamingAggregator:
    """
    手動實現串流回應聚合。
    因為目前的 ADK 中可能不提供 StreamingResponseAggregator。
    """

    def __init__(self):
        """初始化聚合器。"""
        self.chunks = []
        self.complete_text = ""

    def add_event(self, event):
        """
        將一個串流事件加入到聚合中。

        Args:
            event: 來自 runner.run_async() 的串流事件
        """
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    self.chunks.append(part.text)
                    self.complete_text += part.text

    def get_response(self):
        """
        取得完整的聚合回應。

        Returns:
            包含聚合回應資料的字典
        """
        return {
            'content': {
                'parts': [{'text': self.complete_text}]
            },
            'chunks': self.chunks,
            'total_chunks': len(self.chunks),
            'total_length': len(self.complete_text)
        }


async def stream_with_manual_aggregator(query: str, agent: Agent):
    """
    使用手動聚合以獲得更簡潔的串流程式碼。

    Args:
        query: 使用者查詢
        agent: 要使用的 agent

    Returns:
        完整的 回應字典
    """
    # 建立 runner 和 session
    session_service = InMemorySessionService()
    runner = Runner(app_name="aggregator_demo", agent=agent, session_service=session_service)

    session = await session_service.create_session(
        app_name="aggregator_demo",
        user_id="demo_user"
    )

    run_config = RunConfig(streaming_mode=StreamingMode.SSE)

    # 建立手動聚合器
    aggregator = ManualStreamingAggregator()

    print(f"查詢: {query}")
    print("使用聚合進行串流: ", end='', flush=True)

    async for event in runner.run_async(
        user_id="demo_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)]),
        run_config=run_config
    ):
        # 聚合器處理字塊收集
        aggregator.add_event(event)

        # 顯示字塊
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end='', flush=True)

        if event.turn_complete:
            break

    # 取得完整回應
    complete_response = aggregator.get_response()

    print("\n\n聚合結果:")
    print(f"- 總字塊數: {complete_response['total_chunks']}")
    print(f"- 總長度: {complete_response['total_length']} 字元")

    return complete_response


async def demo_aggregation_patterns():
    """
    展示不同的聚合方法。
    """
    print("=" * 70)
    print("串流回應聚合展示")
    print("=" * 70)

    # 建立 agent
    agent = Agent(
        model='gemini-2.0-flash',
        name='aggregator_demo_agent',
        instruction='為聚合測試提供詳細的回應。'
    )

    # 展示查詢
    queries = [
        "解釋區塊鏈技術",
        "什麼是微服務？",
        "機器學習如何運作？"
    ]

    for query in queries:
        print(f"\n{'='*50}")
        response = await stream_with_manual_aggregator(query, agent)
        print(f"{'='*50}")

        # 顯示字塊分析
        chunks = response['chunks']
        if len(chunks) > 0:
            avg_chunk_size = sum(len(chunk) for chunk in chunks) / len(chunks)
            print(f"平均字塊大小: {avg_chunk_size:.1f} 字元")
            print(f"最大字塊: {max(len(chunk) for chunk in chunks)} 字元")
            print(f"最小字塊: {min(len(chunk) for chunk in chunks)} 字元")

        await asyncio.sleep(0.5)  # 短暫暫停

    print("\n" + "=" * 70)
    print("聚合展示完成！")
    print("此展示說明如何將串流字塊收集成完整的回應。")
    print("=" * 70)


async def main():
    """執行聚合展示。"""
    await demo_aggregation_patterns()


if __name__ == '__main__':
    asyncio.run(main())
