from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..services.session_service import SessionService

app = FastAPI(title="NotChatGPT API")

session_service = SessionService()

class ChatRequest(BaseModel):
    message: str
    thinking_mode: bool = False

@app.get("/")
async def root():
    return {"message": "NotChatGPT API is running"}

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE 串流端點"""
    from ..agents.streaming_agent import stream_response
    
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

@app.post("/api/conversations")
async def create_conversation():
    import uuid
    conv_id = str(uuid.uuid4())
    session_service.create_session(conv_id)
    return {"id": conv_id, "title": "New Chat"}

@app.get("/api/conversations")
async def list_conversations():
    convs = session_service.list_conversations()
    return [{"id": c[0], "title": c[1], "updated_at": c[2].isoformat()} for c in convs]

@app.get("/api/conversations/{conv_id}/messages")
async def get_conversation_history(conv_id: str):
    messages = session_service.get_messages(conv_id)
    return [{"role": m[0], "content": m[1]} for m in messages]

@app.delete("/api/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    session_service.delete_conversation(conv_id)
    return {"message": "Conversation deleted"}