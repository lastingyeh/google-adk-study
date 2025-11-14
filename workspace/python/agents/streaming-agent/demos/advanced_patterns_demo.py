"""
進階串流模式展示 - 教學 14

展示全部 4 種進階串流模式：
1. 回應聚合 (Response Aggregation)
2. 帶有進度指示器的串流 (Streaming with Progress Indicators)
3. 串流至多個輸出 (Streaming to Multiple Outputs)
4. 帶有超時保護的串流 (Streaming with Timeout)
"""

import asyncio
import os
import sys
from typing import List, Callable
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 環境設定
# 設定預設值，指示 ADK 不使用 Vertex AI
os.environ.setdefault('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE')


class AdvancedStreamingDemo:
    """進階串流模式的展示類別。"""

    def __init__(self):
        """初始化展示，建立 agent 和 runner。"""
        # 初始化 Agent，設定模型、名稱與指示
        self.agent = Agent(
            model='gemini-2.0-flash',
            name='advanced_streaming_demo',
            instruction='為串流模式展示提供詳細的回應。'
        )

        # 使用記憶體內的會話服務來管理對話狀態
        self.session_service = InMemorySessionService()
        # 初始化 Runner，綁定應用程式名稱、agent 和會話服務
        self.runner = Runner(app_name="advanced_demo", agent=self.agent, session_service=self.session_service)
        # 設定執行組態，指定串流模式為 SSE (Server-Sent Events)
        self.run_config = RunConfig(streaming_mode=StreamingMode.SSE)

    async def create_session(self):
        """為此展示建立一個會話。"""
        # 建立一個新的會話，用於追蹤對話上下文
        return await self.session_service.create_session(
            app_name="advanced_demo",
            user_id="demo_user"
        )

    async def pattern_1_response_aggregation(self, query: str) -> tuple[str, List[str]]:
        """
        模式 1：回應聚合
        在串流的同時收集完整的回應。

        Args:
            query: 使用者查詢

        Returns:
            一個包含 (完整文字, 字塊列表) 的元組
        """
        session = await self.create_session()
        chunks = []  # 用於儲存所有收到的字塊

        print("模式 1 - 回應聚合")
        print(f"查詢: {query}")
        print("串流中: ", end='', flush=True)

        # 非同步地執行 agent 並迭代處理串流事件
        async for event in self.runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=query)]),
            run_config=self.run_config
        ):
            # 檢查事件是否包含內容
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        chunk = part.text
                        chunks.append(chunk)  # 將字塊加入列表
                        print(chunk, end='', flush=True)  # 即時印出字塊

            # 如果對話回合完成，則跳出迴圈
            if event.turn_complete:
                break

        complete_text = ''.join(chunks)  # 將所有字塊組合成完整文字
        print(f"\n\n總字塊數: {len(chunks)}")
        print(f"總長度: {len(complete_text)} 字元")
        return complete_text, chunks

    async def pattern_2_progress_indicators(self, query: str):
        """
        模式 2：帶有進度指示器的串流
        在串流期間顯示進度。

        Args:
            query: 使用者查詢
        """
        session = await self.create_session()

        print("\n模式 2 - 進度指示器")
        print(f"查詢: {query}")
        print("Agent: ", end='', flush=True)

        chunk_count = 0

        # 非同步執行 agent
        async for event in self.runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=query)]),
            run_config=self.run_config
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        chunk = part.text
                        print(chunk, end='', flush=True)

                        chunk_count += 1

                        # 每收到 5 個字塊就顯示一個進度指示器
                        if chunk_count % 5 == 0:
                            sys.stderr.write('.')
                            sys.stderr.flush()

            if event.turn_complete:
                break

        print()  # 換行

    async def pattern_3_multiple_outputs(self, query: str, outputs: List[Callable[[str], None]]):
        """
        模式 3：串流至多個輸出
        將串流回應發送到多個目的地。

        Args:
            query: 使用者查詢
            outputs: 輸出函式的列表
        """
        session = await self.create_session()

        print("\n模式 3 - 多重輸出")
        print(f"查詢: {query}")
        print(f"正在同時發送到 {len(outputs)} 個輸出...")

        # 非同步執行 agent
        async for event in self.runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=query)]),
            run_config=self.run_config
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        chunk = part.text
                        # 將字塊發送到所有指定的輸出函式
                        for output_fn in outputs:
                            output_fn(chunk)

            if event.turn_complete:
                break

        print("\n完成串流至多個輸出。")

    async def pattern_4_timeout_protection(self, query: str, timeout_seconds: float = 10.0):
        """
        模式 4：帶有超時保護的串流
        為串流增加超時保護。

        Args:
            query: 使用者查詢
            timeout_seconds: 超時秒數
        """
        session = await self.create_session()

        print("\n模式 4 - 超時保護")
        print(f"查詢: {query}")
        print(f"超時設定: {timeout_seconds} 秒")
        print("Agent: ", end='', flush=True)

        try:
            # 使用 asyncio.timeout 設定非同步操作的超時時間
            async with asyncio.timeout(timeout_seconds):
                async for event in self.runner.run_async(
                    user_id="demo_user",
                    session_id=session.id,
                    new_message=types.Content(role="user", parts=[types.Part(text=query)]),
                    run_config=self.run_config
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                chunk = part.text
                                print(chunk, end='', flush=True)

                    if event.turn_complete:
                        break

        except asyncio.TimeoutError:
            # 捕獲超時錯誤並印出提示訊息
            print(f"\n\n[超時: 回應時間超過 {timeout_seconds} 秒]")

        print()


# 模式 3 的輸出處理函式
def console_output(chunk: str):
    """輸出到控制台。"""
    print(chunk, end='', flush=True)

def file_output(chunk: str):
    """輸出到檔案。"""
    with open('streaming_output.txt', 'a', encoding='utf-8') as f:
        f.write(chunk)

def counter_output(chunk: str):
    """計算字元數（展示多個處理器）。"""
    # 使用函式屬性來儲存計數器狀態
    if not hasattr(counter_output, 'count'):
        counter_output.count = 0
    counter_output.count += len(chunk)
    # 每 50 個字元印出一次計數
    if counter_output.count % 50 == 0:
        print(f"[{counter_output.count} chars]", end='', flush=True)


async def main():
    """執行所有進階串流模式的展示。"""
    print("=" * 80)
    print("進階串流模式展示 - 教學 14")
    print("=" * 80)

    demo = AdvancedStreamingDemo()

    # 模式 1: 回應聚合
    complete, chunks = await demo.pattern_1_response_aggregation(
        "簡要解釋機器學習"
    )

    # 模式 2: 進度指示器
    await demo.pattern_2_progress_indicators(
        "寫一段關於人工智慧的短文"
    )

    # 模式 3: 多重輸出
    # 首先清空輸出檔案
    with open('streaming_output.txt', 'w', encoding='utf-8') as f:
        f.write("串流輸出日誌:\n")

    await demo.pattern_3_multiple_outputs(
        "再生能源有哪些好處？",
        outputs=[console_output, file_output, counter_output]
    )

    # 顯示檔案內容
    print("\n檔案輸出內容:")
    try:
        with open('streaming_output.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            # 如果內容過長，只顯示前 200 個字元
            print(content[:200] + "..." if len(content) > 200 else content)
    except FileNotFoundError:
        print("找不到檔案輸出。")

    # 模式 4: 超時保護
    await demo.pattern_4_timeout_protection(
        "詳細解釋相對論",
        timeout_seconds=5.0  # 為了展示，設定一個較短的超時
    )

    print("=" * 80)
    print("所有進階串流模式已展示完畢！")
    print("=" * 80)


if __name__ == '__main__':
    # 執行主函式
    asyncio.run(main())
