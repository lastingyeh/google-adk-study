import os
from dotenv import load_dotenv

# 在所有其他匯入之前，從 .env 檔案載入環境變數
load_dotenv()


from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app

# 匯入您的 DocumentService
from backend.service.document_service import DocumentService

# 獲取 backend 目錄的路徑
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化 FastAPI 應用程式，使用 ADK 提供的 get_fast_api_app
app: FastAPI = get_fast_api_app(
    agents_dir=BACKEND_DIR,
    web=True,
)
app.title = "not-chat-gpt"
app.description = "與 not-chat-gpt 代理互動的 API"

# 建立 DocumentService 的實例
# 確保您的 GOOGLE_API_KEY 環境變數已設定
try:
    document_service = DocumentService()
except ValueError as e:
    print(f"無法初始化 DocumentService: {e}")
    document_service = None

# 定義查詢請求的資料模型
class QueryRequest(BaseModel):
    query: str

# --- 新增的 API 端點 ---

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    執行健康檢查並回傳應用程式狀態。
    """
    return {"status": "ok"}

@app.post("/documents/upload", tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    """
    上傳一個文件到 FileSearchStore。
    """
    if not document_service:
        raise HTTPException(status_code=500, detail="DocumentService 未成功初始化。")
    try:
        # ADK 的 upload_file 方法需要 file_name 和 file_data (file-like object)
        document_service.upload_file(file_name=file.filename, file_data=file.file)
        return {"filename": file.filename, "message": "文件上傳並匯入成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上傳失敗: {str(e)}")

@app.get("/documents", tags=["Documents"])
async def list_documents():
    """
    列出 FileSearchStore 中的所有文件。
    """
    if not document_service:
        raise HTTPException(status_code=500, detail="DocumentService 未成功初始化。")
    try:
        files = document_service.list_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法列出文件: {str(e)}")

@app.post("/documents/query", tags=["Documents"])
async def query_document(request: QueryRequest):
    """
    對已上傳的文件進行查詢。
    """
    if not document_service:
        raise HTTPException(status_code=500, detail="DocumentService 未成功初始化。")
    try:
        response_text = document_service.query_document(request.query)
        return {"query": request.query, "response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")

@app.delete("/documents/{document_id:path}", tags=["Documents"])
async def delete_document(document_id: str):
    """
    從 FileSearchStore 中刪除一個文件。
    
    - **document_id**: 文件的唯一資源名稱 (例如: corpora/my-corpus-123/documents/my-document-456)
    """
    if not document_service:
        raise HTTPException(status_code=500, detail="DocumentService 未成功初始化。")
    try:
        # FastAPI 會自動 URL 解碼 document_id，所以我們直接傳遞
        document_service.delete_document(document_id)
        return {"message": f"Document '{document_id}' deleted successfully."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除文件失敗: {str(e)}")

# --- 結束新增的 API 端點 ---

# 主程式進入點
if __name__ == "__main__":
    import uvicorn

    # 啟動 Uvicorn 伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)