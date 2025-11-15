"""用於測試音訊回應的快速偵錯腳本。"""
import asyncio
import os
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def test():
    # 定義使用的模型
    model = 'gemini-2.0-flash-live-preview-04-09'
    # 初始化 Agent，設定模型、名稱和指示
    agent = Agent(
        model=model,
        name='test_agent',
        instruction='請讓回應非常簡短 - 只要說「哈囉」就好。'
    )

    # 設定執行組態
    run_config = RunConfig(
        # 使用雙向串流模式
        streaming_mode=StreamingMode.BIDI,
        # 設定語音組態
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                # 使用預先建立的語音設定
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Puck')
            )
        ),
        # 設定回應的模式為音訊
        response_modalities=[types.Modality.AUDIO],
    )

    # 建立一個 LiveRequestQueue 用於即時請求
    queue = LiveRequestQueue()
    # 建立一個 App，將 agent 設為根代理人
    app = App(name='test_app', root_agent=agent)
    # 使用記憶體內的會話服務
    session_service = InMemorySessionService()
    # 建立 Runner
    runner = Runner(app=app, session_service=session_service)
    # 建立一個新的會話
    session = await runner.session_service.create_session(app_name=app.name, user_id='test')

    # 傳送一個內容為 "Hello" 的使用者訊息到佇列
    queue.send_content(types.Content(role='user', parts=[types.Part.from_text(text='Hello')]))
    # 關閉佇列，表示沒有更多請求
    queue.close()

    print('正在開始 run_live...')
    event_count = 0
    # 非同步地執行 live run，並處理事件
    async for event in runner.run_live(
        live_request_queue=queue,
        user_id='test',
        session_id=session.id,
        run_config=run_config
    ):
        event_count += 1
        print(f'事件 {event_count}: {type(event).__name__}')
        # 檢查事件是否有伺服器內容
        if hasattr(event, 'server_content') and event.server_content:
            print(f'  包含 {len(event.server_content.parts)} 個部分的 server_content')
            for i, part in enumerate(event.server_content.parts):
                # 檢查部分是否包含文字或內嵌資料
                has_text = bool(getattr(part, 'text', None))
                has_inline = bool(getattr(part, 'inline_data', None))
                print(f'  部分 {i}: text={has_text}, inline_data={has_inline}')
                if has_inline:
                    # 如果有內嵌資料，印出音訊資料的大小
                    print(f'    音訊資料大小: {len(part.inline_data.data)} 位元組')
        # 設定一個上限，避免無限迴圈
        if event_count > 50:
            print('處理 50 個事件後停止')
            break
    print(f'總事件數: {event_count}')

if __name__ == '__main__':
    # 執行非同步測試函式
    asyncio.run(test())
