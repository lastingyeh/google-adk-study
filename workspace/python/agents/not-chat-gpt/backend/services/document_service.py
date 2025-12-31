from google import genai
from google.genai import types
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, UTC
import os

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)  # Gemini File ID
    name = Column(String)
    size = Column(Integer)
    mime_type = Column(String)
    uri = Column(String)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(UTC))

class DocumentService:
    """文檔管理服務"""
    
    def __init__(self, genai_client: genai.Client, database_url="sqlite:///./not_chat_gpt.db"):
        self.client = genai_client
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def upload_document(self, file_path: str, display_name: str = None) -> dict:
        """上傳文檔
        
        Args:
            file_path: 文件路徑
            display_name: 顯示名稱（可選，預設使用檔名）
            
        Returns:
            dict: 包含 id, name, size, uri 的文檔資訊
        """
        # 上傳到 Gemini（使用正確的 API）
        uploaded_file = self.client.files.upload(
            file=file_path,
            config=types.UploadFileConfig(
                display_name=display_name or os.path.basename(file_path)
            )
        )
        
        # 儲存到資料庫
        db = self.SessionLocal()
        try:
            doc = Document(
                id=uploaded_file.name,
                name=uploaded_file.display_name,
                size=uploaded_file.size_bytes,
                mime_type=uploaded_file.mime_type,
                uri=uploaded_file.uri,
            )
            db.add(doc)
            db.commit()
            
            return {
                "id": uploaded_file.name,
                "name": uploaded_file.display_name,
                "size": uploaded_file.size_bytes,
                "uri": uploaded_file.uri,
                "mime_type": uploaded_file.mime_type,
            }
        finally:
            db.close()
    
    def list_documents(self) -> list:
        """列出所有文檔"""
        db = self.SessionLocal()
        docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
        db.close()
        return [
            {
                "id": d.id,
                "name": d.name,
                "size": d.size,
                "uploaded_at": d.uploaded_at.isoformat(),
            }
            for d in docs
        ]
    
    def get_document(self, document_id: str) -> dict:
        """獲取單一文檔資訊
        
        Args:
            document_id: 文檔 ID
            
        Returns:
            dict: 文檔詳細資訊，如果不存在則返回 None
        """
        db = self.SessionLocal()
        try:
            doc = db.query(Document).filter_by(id=document_id).first()
            if not doc:
                return None
            return {
                "id": doc.id,
                "name": doc.name,
                "size": doc.size,
                "mime_type": doc.mime_type,
                "uri": doc.uri,
                "uploaded_at": doc.uploaded_at.isoformat(),
            }
        finally:
            db.close()
    
    def delete_document(self, document_id: str):
        """刪除文檔"""
        # 從 Gemini 刪除
        self.client.files.delete(name=document_id)
        
        # 從資料庫刪除
        db = self.SessionLocal()
        doc = db.query(Document).filter_by(id=document_id).first()
        if doc:
            db.delete(doc)
            db.commit()
        db.close()