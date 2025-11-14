"""
教學 14：使用伺服器發送事件 (SSE) 的串流代理人

此代理人展示如何使用 ADK 的伺服器發送事件 (Server-Sent Events, SSE)
來實現串流回應，以提供即時、漸進式的輸出，從而改善使用者體驗。
"""

import os
from typing import AsyncIterator, Dict, Any
from google.adk.agents import Agent
from google.adk.runners import Runner, LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types


# 設定 Google AI 的環境變數
# 設定預設值，指示 ADK 不要使用 Vertex AI
os.environ.setdefault('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE')


def create_streaming_agent() -> Agent:
    """
    建立一個用於即時回應的串流代理人。

    返回:
        Agent: 設定為串流回應的代理人
    """
    # 建立並設定代理人
    return Agent(
        model='gemini-2.0-flash',  # 使用的模型
        name='streaming_assistant',  # 代理人名稱
        description='一個提供即時聊天串流回應的實用助理',  # 代理人描述
        instruction="""
        您是一位樂於助人、友善的助理，能以串流輸出方式提供詳細的回應。

        指南：
        - 保持對話性和吸引力
        - 當被問到時，提供詳細的解釋
        - 如有需要，提出澄清問題
        - 記住對話上下文
        - 對於簡單的查詢，回答要簡潔；對於複雜的查詢，回答要詳細
        - 在適當時，使用章節清晰地組織您的回應
        """.strip(),
        generate_content_config=types.GenerateContentConfig(
            temperature=0.7,  # 設定溫度以獲得更具對話性的回應
            max_output_tokens=2048,  # 最大輸出 token 數
            top_p=0.8,  # top-p 核新取樣
            top_k=40  # top-k token 排序取樣
        )
    )

# 簡單說明 top_k 和 top_p 的差異：
# | 特性    | top_k       | top_p      |
# | ----- | ----------- | ---------- |
# | 控制方式  | 限制 token 數量 | 限制機率總和     |
# | 自適應能力 | ❌ 低         | ✅ 高        |
# | 創意度控制 | 中等          | 高          |
# | 生成穩定性 | 穩定（限制選項）    | 更靈活        |
# | 適合    | 程式碼、精準任務    | 自然語言、高創意場景 |



# 全域代理人實例
# 建立一個可在整個應用程式中使用的代理人實例
root_agent = create_streaming_agent()


async def stream_agent_response(query: str) -> AsyncIterator[str]:
    """
    使用 ADK 的實際串流 API 將代理人對查詢的回應進行串流。

    參數:
        query: 要處理的使用者查詢

    產生:
        str: 由 AI 模型產生的文字區塊
    """
    # 建立 runner 和 session 服務
    session_service = InMemorySessionService()  # 使用記憶體內的 session 服務
    runner = Runner(app_name="streaming_agent", agent=root_agent, session_service=session_service)

    # 為此對話建立一個 session
    session = await session_service.create_session(
        app_name="streaming_agent",
        user_id="demo_user"
    )

    # 設定為 SSE 串流模式
    run_config = RunConfig(
        streaming_mode=StreamingMode.SSE,  # 指定串流模式為 SSE
        max_llm_calls=50  # 設定大型語言模型 (LLM) 的最大呼叫次數
    )

    try:
        # 使用 run_async 以串流方式執行代理人
        async for event in runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=query)]),
            run_config=run_config
        ):
            # 處理不同的事件類型
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        # 產生文字區塊
                        yield part.text

            # 檢查是否完成
            if event.turn_complete:
                break

    except Exception as e:
        # 如果實際串流失敗，則退回到模擬串流
        print(f"警告：實際串流失敗 ({e})，退回到模擬模式")
        mock_response = f"我了解您問了：'{query}'。這段文字展示了透過漸進式文字輸出來實現串流的概念。"

        words = mock_response.split()
        for word in words:
            yield word + " "
            import asyncio
            await asyncio.sleep(0.01)


async def get_complete_response(query: str) -> str:
    """
    取得完整的回應（非串流），用於測試或不需要串流的場景。

    參數:
        query: 使用者查詢

    返回:
        str: 完整的 回應文字
    """
    # 建立 runner 和 session 服務
    session_service = InMemorySessionService()
    runner = Runner(app_name="streaming_agent", agent=root_agent, session_service=session_service)

    # 建立一個 session
    session = await session_service.create_session(
        app_name="streaming_agent",
        user_id="demo_user"
    )

    # 設定為非串流模式
    run_config = RunConfig(
        streaming_mode=StreamingMode.NONE,  # 停用串流
        max_llm_calls=50
    )

    # 收集所有回應部分
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

    return ''.join(response_parts)


def create_demo_session():
    """
    建立一個用於測試的演示 session。

    返回:
        Session: 用於演示的 Session 物件
    """
    import asyncio
    session_service = InMemorySessionService()

    # 為了演示目的，同步建立 session
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        session = loop.run_until_complete(
            session_service.create_session(
                app_name="streaming_agent",
                user_id="demo_user"
            )
        )
        return session
    finally:
        loop.close()


# 用於增強功能的工具函式
def format_streaming_info() -> Dict[str, Any]:
    """
    提供有關串流功能的資訊。

    返回:
        Dict[str, Any]: 包含串流資訊的字典
    """
    return {
        'status': 'success',
        'report': '成功檢索串流資訊',
        'data': {
            'streaming_modes': ['SSE', 'BIDI', 'OFF'],
            'current_mode': 'SSE',
            'benefits': [
                '即時使用者回饋',
                '更好的感知效能',
                '漸進式輸出顯示',
                '可提早中斷回應'
            ],
            'use_cases': [
                '聊天應用程式',
                '長文內容生成',
                '互動式助理',
                '即時分析'
            ]
        }
    }


def analyze_streaming_performance(query_length: int = 100) -> Dict[str, Any]:
    """
    分析串流效能特性。

    參數:
        query_length: 要分析的查詢長度

    返回:
        Dict[str, Any]: 效能分析資料
    """
    try:
        # 模擬效能分析
        estimated_chunks = max(1, query_length // 50)  # 粗略估計
        estimated_time = query_length * 0.1  # 粗略時間估計

        return {
            'status': 'success',
            'report': f'查詢長度 {query_length} 的效能分析',
            'data': {
                'estimated_chunks': estimated_chunks,
                'estimated_total_time_seconds': estimated_time,
                'chunk_size_range': '10-100 字元',
                'recommended_buffer_size': 1024,
                'memory_efficient': True
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': '分析串流效能失敗'
        }


# 將工具新增至代理人
root_agent.tools = [format_streaming_info, analyze_streaming_performance]
