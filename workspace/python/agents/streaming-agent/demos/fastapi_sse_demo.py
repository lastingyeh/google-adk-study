"""
FastAPI SSE 端點展示 - 教學 14

展示如何使用串流 Server-Sent Events (SSE) 建立 Web API。
"""

import asyncio
import os
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 環境設定
os.environ.setdefault('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE')

# 建立 FastAPI 應用程式
app = FastAPI(title="串流聊天 API", description="使用 SSE 的 ADK 串流聊天 API")

# 建立 agent (為方便展示設為全域)
agent = Agent(
    model='gemini-2.0-flash',
    name='api_assistant',
    instruction='你是一個有幫助的 API 助理。請提供清晰、簡潔的回應。'
)

# 全域的 runner 和 session_service
session_service = InMemorySessionService()
runner = Runner(app_name="fastapi_demo", agent=agent, session_service=session_service)


async def generate_stream(query: str):
    """
    為查詢產生 SSE 串流。

    Args:
        query: 使用者查詢

    Yields:
        SSE 格式的資料字塊
    """
    # 為此請求建立會話
    session = await session_service.create_session(
        app_name="fastapi_demo",
        user_id=f"api_user_{hash(query) % 10000}"  # 簡單的使用者 ID
    )

    run_config = RunConfig(streaming_mode=StreamingMode.SSE)

    try:
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=query)]),
            run_config=run_config
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        # 格式化為 SSE
                        chunk = part.text
                        data = json.dumps({'text': chunk, 'type': 'chunk'})
                        yield f"data: {data}\n\n"

            if event.turn_complete:
                break

        # 發送完成信號
        completion_data = json.dumps({'type': 'done', 'message': '回應完成'})
        yield f"data: {completion_data}\n\n"

    except Exception as e:
        # 發送錯誤信號
        error_data = json.dumps({'type': 'error', 'message': str(e)})
        yield f"data: {error_data}\n\n"


@app.get("/")
async def root():
    """根端點。"""
    return {"message": "串流聊天 API", "endpoints": ["/chat/stream", "/docs"]}


@app.post("/chat/stream")
async def chat_stream(query: str):
    """
    串流聊天端點。

    Args:
        query: 使用者的問題

    Returns:
        帶有 SSE 的 StreamingResponse
    """
    return StreamingResponse(
        generate_stream(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@app.get("/chat/stream")
async def chat_stream_get(query: str):
    """
    串流聊天端點的 GET 版本，用於瀏覽器測試。

    Args:
        query: 使用者的問題

    Returns:
        帶有 SSE 的 StreamingResponse
    """
    return StreamingResponse(
        generate_stream(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


# 用於測試的客戶端 JavaScript
CLIENT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>串流聊天客戶端</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #messages { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: auto; }
        #input { width: 300px; padding: 5px; }
        button { padding: 5px 10px; }
    </style>
</head>
<body>
    <h1>串流聊天客戶端</h1>
    <div id="messages"></div>
    <br>
    <input type="text" id="input" placeholder="問一個問題...">
    <button onclick="sendMessage()">傳送</button>

    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        let eventSource = null;

        function sendMessage() {
            const query = input.value.trim();
            if (!query) return;

            // 關閉現有連線
            if (eventSource) {
                eventSource.close();
            }

            // 清除先前的訊息
            messages.innerHTML = '';

            // 新增使用者訊息
            addMessage('你', query);

            // 開始新的 SSE 連線
            eventSource = new EventSource(`/chat/stream?query=${encodeURIComponent(query)}`);

            eventSource.onmessage = (event) => {
                if (event.data === "[DONE]") {
                    eventSource.close();
                    return;
                }

                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'chunk') {
                        addToAgentMessage(data.text);
                    } else if (data.type === 'done') {
                        // 回應完成
                    } else if (data.type === 'error') {
                        addMessage('錯誤', data.message);
                    }
                } catch (e) {
                    console.error('解析錯誤:', e);
                }
            };

            eventSource.onerror = (error) => {
                console.error('SSE 錯誤:', error);
                addMessage('錯誤', '連線失敗');
                eventSource.close();
            };

            input.value = '';
        }

        function addMessage(sender, text) {
            const div = document.createElement('div');
            div.innerHTML = `<strong>${sender}:</strong> ${text}`;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function addToAgentMessage(text) {
            let agentDiv = messages.querySelector('.agent-message');
            if (!agentDiv) {
                agentDiv = document.createElement('div');
                agentDiv.className = 'agent-message';
                agentDiv.innerHTML = '<strong>Agent:</strong> ';
                messages.appendChild(agentDiv);
            }
            agentDiv.innerHTML += text;
            messages.scrollTop = messages.scrollHeight;
        }

        // 按下 Enter 鍵傳送訊息
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""


@app.get("/client")
async def client_page():
    """提供客戶端 HTML 頁面。"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=CLIENT_HTML)


async def demo_server():
    """
    展示 API 如何運作的函式。
    通常這會透過指令執行：uvicorn fastapi_sse_demo:app --reload
    """
    print("=" * 70)
    print("FASTAPI SSE 端點展示")
    print("=" * 70)
    print("此展示說明如何使用 FastAPI 建立串流 SSE 端點。")
    print("\n要執行伺服器：")
    print("  uvicorn demos.fastapi_sse_demo:app --reload")
    print("\n然後造訪：")
    print("  http://localhost:8000/docs    - API 文件")
    print("  http://localhost:8000/client  - 測試客戶端")
    print("\n或直接測試：")
    print("  curl \"http://localhost:8000/chat/stream?query=Hello\"")
    print("=" * 70)


if __name__ == '__main__':
    # 執行展示而非伺服器
    asyncio.run(demo_server())
