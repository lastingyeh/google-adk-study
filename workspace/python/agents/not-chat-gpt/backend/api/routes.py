from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

app = FastAPI(title="NotChatGPT API")

class ChatRequest(BaseModel):
    message: str
    thinking_mode: bool = False

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE 串流端點"""
    from agents.streaming_agent import stream_response
    
    async def event_generator():
        try:
            async for chunk in stream_response(request.message, request.thinking_mode):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

@app.get("/")
async def root():
    return {"message": "NotChatGPT API is running"}