"""
使用 SSE 的串流聊天應用程式 - 教學 14

具有漸進式回應的即時互動聊天。
來自教學的 StreamingChatApp 類別的完整實作。
"""

import asyncio
import os
from datetime import datetime
from typing import AsyncIterator
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 環境設定
os.environ.setdefault('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE')


class StreamingChatApp:
    """互動式串流聊天應用程式。"""

    def __init__(self):
        """初始化聊天應用程式。"""

        # 建立聊天 agent
        self.agent = Agent(
            model='gemini-2.0-flash',
            name='chat_assistant',
            description='一個能進行自然對話的助理。',
            instruction="""
你是一個有幫助、友善的助理，能進行自然的對話。

指導方針：
- 保持對話性和吸引力
- 當被問到時提供詳細的解釋
- 如有需要，提出澄清問題
- 記住對話上下文
- 對於簡單的查詢要簡潔，對於複雜的查詢要詳細
            """.strip(),
            generate_content_config=types.GenerateContentConfig(
                temperature=0.7,  # 對話式
                max_output_tokens=2048
            )
        )

        # 建立用於對話上下文的會話
        self.session_service = InMemorySessionService()
        self.session = None
        self.runner = Runner(app_name="streaming_chat", agent=self.agent, session_service=self.session_service)

        # 設定串流
        self.run_config = RunConfig(
            streaming_mode=StreamingMode.SSE,
            max_llm_calls=50
        )

    async def initialize_session(self):
        """初始化或取得現有會話。"""
        if self.session is None:
            self.session = await self.session_service.create_session(
                app_name="streaming_chat",
                user_id="chat_user"
            )

    async def stream_response(self, user_message: str) -> AsyncIterator[str]:
        """
        將 agent 回應串流至使用者訊息。

        Args:
            user_message: 使用者的輸入訊息

        Yields:
            生成時的文字字塊
        """
        await self.initialize_session()

        # 執行 agent 串流
        async for event in self.runner.run_async(
            user_id="chat_user",
            session_id=self.session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=user_message)]),
            run_config=self.run_config
        ):
            # 從事件中提取文字
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        yield part.text

            # 檢查是否完成
            if event.turn_complete:
                break

    async def chat_turn(self, user_message: str):
        """
        執行一次帶有串流顯示的聊天回合。

        Args:
            user_message: 使用者的輸入訊息
        """

        # 顯示使用者訊息
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{timestamp}] 使用者: {user_message}")

        # 顯示 agent 回應（串流）
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] Agent: ", end='', flush=True)

        # 串流回應字塊
        async for chunk in self.stream_response(user_message):
            print(chunk, end='', flush=True)

        print()  # 完整回應後換行

    async def run_interactive(self):
        """執行互動式聊天迴圈。"""

        print("="*70)
        print("串流聊天應用程式")
        print("="*70)
        print("輸入 'exit' 或 'quit' 結束對話")
        print("="*70)

        while True:
            try:
                # 取得使用者輸入
                user_input = input("\n你: ").strip()

                if not user_input:
                    continue

                # 檢查是否退出
                if user_input.lower() in ['exit', 'quit']:
                    print("\n再見！")
                    break

                # 處理聊天回合
                await self.chat_turn(user_input)

            except KeyboardInterrupt:
                print("\n\n已中斷。再見！")
                break
            except Exception as e:
                print(f"\n錯誤: {e}")

    async def run_demo(self):
        """執行展示對話。"""

        print("="*70)
        print("串流聊天展示")
        print("="*70)

        demo_messages = [
            "你好！你能幫我什麼嗎？",
            "用簡單的術語解釋量子計算",
            "有哪些實際應用？",
            "它與傳統計算有何不同？"
        ]

        for message in demo_messages:
            await self.chat_turn(message)
            await asyncio.sleep(1)  # 回合之間暫停


async def main():
    """主進入點。"""

    chat = StreamingChatApp()

    # 執行展示
    await chat.run_demo()

    # 若要進入互動模式，請取消註解以下這行：
    # await chat.run_interactive()


if __name__ == '__main__':
    asyncio.run(main())
