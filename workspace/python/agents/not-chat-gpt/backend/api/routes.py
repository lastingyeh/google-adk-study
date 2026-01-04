"""NotChatGPT API Routes (使用 Google ADK)

本模組使用 Google ADK 提供 RESTful API 端點：
- 對話端點：使用 ADK Runner 管理對話
- 會話管理：使用 ADK SessionService
- 文檔管理：整合 Gemini Files API
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

# ADK 核心元件
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from backend.services.session_service import SessionService
from backend.services.document_service import DocumentService
from backend.agents.conversation_agent import create_conversation_agent
from backend.agents.streaming_agent import get_streaming_manager

import tempfile
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 檢查 API Key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment")

# 初始化服務
genai_client = genai.Client(api_key=api_key)  # 僅用於 DocumentService
doc_service = DocumentService(genai_client)
session_service = SessionService()

# 初始化 ADK 元件
adk_session_service = InMemorySessionService()
conversation_agent = create_conversation_agent()
conversation_runner = Runner(
    agent=conversation_agent,
    app_name="not_chat_gpt_api",
    session_service=adk_session_service
)

# 初始化 FastAPI
app = FastAPI(title="NotChatGPT API")


class ChatRequest(BaseModel):
    message: str
    thinking_mode: bool = False
    session_id: str = None  # 可選的會話 ID

# 基本健康檢查端點
@app.get("/")
async def root():
    return {
        "message": "NotChatGPT API is running",
        "architecture": "Google ADK",
        "version": "1.0.0"
    }

# 聊天端點 (使用 ADK Runner)
@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE 串流端點 (使用 ADK Runner)
    
    使用 Google ADK StreamingAgentManager 進行串流對話
    """
    streaming_manager = get_streaming_manager()
    
    async def event_generator():
        try:
            # 使用 ADK 的串流 API
            async for chunk in streaming_manager.stream_response(
                message=request.message,
                user_id="api_user",
                session_id=request.session_id,
                thinking_mode=request.thinking_mode,
                enable_safety=True
            ):
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

# 會話相關端點

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

# 文檔相關端點

@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    """上傳文檔到 Gemini Files API
    
    Args:
        file: 上傳的文件
        
    Returns:
        dict: 包含文檔資訊的字典
    """
    # 建立臨時檔案
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        result = doc_service.upload_document(tmp_path, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文檔上傳失敗: {str(e)}")
    finally:
        # 清理臨時檔案
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.get("/api/documents")
async def list_documents():
    """列出所有已上傳的文檔
    
    Returns:
        list: 文檔列表
    """
    try:
        return doc_service.list_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取文檔列表失敗: {str(e)}")

@app.delete("/api/documents/{doc_id:path}")
async def delete_document(doc_id: str):
    """刪除指定文檔
    
    Args:
        doc_id: 文檔 ID（例如：files/abc123...）
                注意：使用 :path 轉換器以支持包含斜線的 ID
        
    Returns:
        dict: 刪除結果
    """
    try:
        doc_service.delete_document(doc_id)
        return {"message": "Document deleted successfully", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文檔刪除失敗: {str(e)}")

@app.get("/api/documents/{doc_id:path}")
async def get_document(doc_id: str):
    """獲取指定文檔的詳細資訊
    
    Args:
        doc_id: 文檔 ID（例如：files/abc123...）
                注意：使用 :path 轉換器以支持包含斜線的 ID
    
    Args:
        doc_id: 文檔 ID
        
    Returns:
        dict: 文檔詳細資訊
    """
    try:
        doc_info = doc_service.get_document(doc_id)
        if not doc_info:
            raise HTTPException(status_code=404, detail="文檔不存在")
        return doc_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取文檔資訊失敗: {str(e)}")