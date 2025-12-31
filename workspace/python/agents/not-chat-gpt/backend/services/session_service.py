"""Session 管理服務

提供對話持久化功能：
- 建立和管理對話 session
- 儲存和載入對話歷史
- 管理對話狀態
"""
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, UTC
import json

Base = declarative_base()

class Message(Base):
    """訊息資料模型"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)  # 'user' or 'model'
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    
    conversation = relationship("Conversation", back_populates="messages")

class Conversation(Base):
    """對話資料模型"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    title = Column(String)
    state = Column(Text)  # JSON 格式的 session state
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class SessionService:
    """Session 管理服務"""
    
    def __init__(self, database_url="sqlite:///./not_chat_gpt.db"):
        """初始化 SessionService
        
        Args:
            database_url: 資料庫連線 URL
        """
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_session(self, session_id: str, title: str = "New Chat"):
        """建立新會話
        
        Args:
            session_id: Session 識別碼
            title: 對話標題
            
        Returns:
            str: Session ID
        """
        db = self.SessionLocal()
        conv = Conversation(id=session_id, title=title, state=json.dumps({}))
        db.add(conv)
        db.commit()
        db.close()
        return session_id
    
    def save_state(self, session_id: str, state: dict):
        """儲存會話狀態
        
        Args:
            session_id: Session 識別碼
            state: 狀態字典
        """
        db = self.SessionLocal()
        conv = db.query(Conversation).filter_by(id=session_id).first()
        if conv:
            conv.state = json.dumps(state)
            conv.updated_at = datetime.now(UTC)
            db.commit()
        db.close()
    
    def load_state(self, session_id: str) -> dict:
        """載入會話狀態
        
        Args:
            session_id: Session 識別碼
            
        Returns:
            dict: 狀態字典
        """
        db = self.SessionLocal()
        conv = db.query(Conversation).filter_by(id=session_id).first()
        db.close()
        return json.loads(conv.state) if conv else {}
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """新增訊息到對話歷史
        
        Args:
            conversation_id: 對話 ID
            role: 角色 ('user' 或 'model')
            content: 訊息內容
        """
        db = self.SessionLocal()
        # 更新對話的 updated_at
        conv = db.query(Conversation).filter_by(id=conversation_id).first()
        if conv:
            conv.updated_at = datetime.now(UTC)
            
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
        db.close()
    
    def get_messages(self, conversation_id: str) -> list:
        """取得對話歷史
        
        Args:
            conversation_id: 對話 ID
            
        Returns:
            list: [(role, content), ...] 格式的訊息列表
        """
        db = self.SessionLocal()
        messages = db.query(Message).filter_by(
            conversation_id=conversation_id
        ).order_by(Message.created_at).all()
        db.close()
        return [(m.role, m.content) for m in messages]
    
    def list_conversations(self) -> list:
        """列出所有對話
        
        Returns:
            list: [(id, title, updated_at), ...] 格式的對話列表
        """
        db = self.SessionLocal()
        convs = db.query(Conversation).order_by(
            Conversation.updated_at.desc()
        ).all()
        db.close()
        return [(c.id, c.title, c.updated_at) for c in convs]
    
    def delete_conversation(self, conversation_id: str):
        """刪除對話（包含所有訊息）
        
        Args:
            conversation_id: 對話 ID
        """
        db = self.SessionLocal()
        conv = db.query(Conversation).filter_by(id=conversation_id).first()
        if conv:
            db.delete(conv)  # cascade 會自動刪除相關的 messages
            db.commit()
        db.close()