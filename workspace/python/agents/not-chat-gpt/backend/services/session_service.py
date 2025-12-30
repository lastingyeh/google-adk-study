from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    title = Column(String)
    state = Column(Text)  # JSON 格式的 session state
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SessionService:
    def __init__(self, database_url="sqlite:///./not_chat_gpt.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_session(self, session_id: str, title: str = "New Chat"):
        """建立新會話"""
        db = self.SessionLocal()
        conv = Conversation(id=session_id, title=title, state=json.dumps({}))
        db.add(conv)
        db.commit()
        db.close()
        return session_id
    
    def save_state(self, session_id: str, state: dict):
        """儲存會話狀態"""
        db = self.SessionLocal()
        conv = db.query(Conversation).filter_by(id=session_id).first()
        if conv:
            conv.state = json.dumps(state)
            conv.updated_at = datetime.utcnow()
            db.commit()
        db.close()
    
    def load_state(self, session_id: str) -> dict:
        """載入會話狀態"""
        db = self.SessionLocal()
        conv = db.query(Conversation).filter_by(id=session_id).first()
        db.close()
        return json.loads(conv.state) if conv else {}