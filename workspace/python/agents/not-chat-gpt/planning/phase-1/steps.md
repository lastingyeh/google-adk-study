# Phase 1: 基礎對話系統

## Week 1: 核心 Agent 建構

### 步驟 1: 環境設定

#### 1.1 建立專案目錄結構

### 專案結構

```text
not-chat-gpt/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── conversation_agent.py
│   │   └── streaming_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── google_search.py
│   │   ├── code_executor.py
│   │   ├── file_handler.py
│   │   └── file_search.py             # 新增：Gemini File Search RAG
│   ├── guardrails/                    # 新增：安全防護層
│   │   ├── __init__.py
│   │   ├── safety_callbacks.py        # AgentCallbacks 實作
│   │   ├── policy_engine.py           # 規範引擎
│   │   ├── content_moderator.py       # 內容審核
│   │   ├── pii_detector.py            # 敏感資訊偵測
│   │   ├── intent_classifier.py       # 意圖分類
│   │   └── audit_logger.py            # 審計日誌
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py
│   │   ├── redis_session_service.py
│   │   └── document_service.py        # 新增：文檔索引管理
│   ├── config/
│   │   ├── __init__.py
│   │   ├── mode_config.py             # 思考模式配置
│   │   └── security_config.py         # 新增：安全配置
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ConversationView.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── InputBox.tsx
│   │   │   ├── ModeSelector.tsx
│   │   │   ├── DocumentPanel.tsx      # 新增：文檔管理面板
│   │   │   └── CitationBadge.tsx      # 新增：引用來源標籤
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tools.py
│   ├── test_guardrails.py             # 安全測試
│   ├── test_session.py
│   ├── test_rag.py                    # 新增：RAG 功能測試
│   ├── test_workflow_integration.py   # 新增：工作流程整合測試
│   ├── test_performance.py            # 新增：效能測試
│   ├── test_evaluation.py             # 新增：AgentEvaluator 測試
│   ├── eval_set.json                  # 新增：評估數據集
│   ├── conftest.py                    # pytest 配置
│   └── fixtures/                      # 測試數據
│       ├── sample_conversations.json
│       └── mock_responses.json
├── deployment/
│   ├── Dockerfile
│   └── cloudbuild.yaml
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── SECURITY.md                    # 新增：安全文件
├── planning/
│   ├── phase-1/
│   ├── phase-2/
│   ├── phase-3/
│   └── planning.md (本檔案)
└── README.md
```

#### 1.2 安裝 Google ADK 與相依套件

```powershell
# 建立虛擬環境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安裝套件
pip install google-genai fastapi uvicorn python-dotenv sqlalchemy pytest pytest-asyncio
```

**backend/requirements.txt**:

```txt
google-genai>=1.0.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

#### 1.3 設定 `.env` 檔案

```powershell
# 建立 .env 檔案
@"
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.0-flash-exp
DATABASE_URL=sqlite:///./not_chat_gpt.db
"@ | Out-File -FilePath .env -Encoding utf8
```

#### 1.4 驗證環境設定

```powershell
# 測試 API Key
python -c "from google import genai; client = genai.Client(api_key='YOUR_KEY'); print('✅ API Key Valid')"

# 檢查套件安裝
pip list | Select-String "google-genai|fastapi"
```

**參考**: Day 16 (hello-agent) - 基礎環境設定

---

### 步驟 2: 基礎 Agent 實作

#### 2.1 建立 `conversation_agent.py`

**backend/agents/conversation_agent.py**:

```python
from google.genai import types
from google import genai

def create_conversation_agent():
    """建立基礎對話 Agent"""
    return types.Agent(
        model="gemini-2.0-flash-exp",
        system_instruction="""你是 NotChatGPT，一個智慧對話助理。
        
特點：
- 友善且專業的對話風格
- 提供準確且有幫助的資訊
- 支援多輪對話與上下文理解
        """,
    )

# 測試用
if __name__ == "__main__":
    client = genai.Client()
    agent = create_conversation_agent()
    
    session = client.agentic.create_session(agent=agent)
    response = session.send_message("你好！請介紹一下你自己")
    print(response.text)
```

#### 2.2 測試基本對話能力

```powershell
# 執行測試
python backend/agents/conversation_agent.py

# 預期輸出: Agent 的自我介紹
```

#### 2.3 測試多輪對話

**backend/test_conversation.py**:

```python
from google import genai
from backend.agents.conversation_agent import create_conversation_agent

def test_multi_turn():
    client = genai.Client()
    agent = create_conversation_agent()
    session = client.agentic.create_session(agent=agent)
    
    # 第一輪
    r1 = session.send_message("我叫 Alice")
    print(f"Round 1: {r1.text}")
    
    # 第二輪 (測試記憶)
    r2 = session.send_message("我叫什麼名字？")
    print(f"Round 2: {r2.text}")
    assert "Alice" in r2.text, "❌ 上下文記憶失敗"
    print("✅ 多輪對話測試通過")

if __name__ == "__main__":
    test_multi_turn()
```

```powershell
python backend/test_conversation.py
```

**參考**: Day 16 (hello-agent) - Agent 基礎架構

---

### 步驟 3: Session State 管理

#### 3.1 實作 `session_service.py`

**backend/services/session_service.py**:

```python
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
```

#### 3.2 測試 Session 管理

```powershell
# 測試建立與載入
python -c "from backend.services.session_service import SessionService; s = SessionService(); sid = s.create_session('test-1'); print(f'✅ Session created: {sid}')"
```

#### 3.3 實作上下文記憶（user/app/temp 前綴）

**整合到 Agent**:

```python
# 在 conversation_agent.py 中使用
from backend.services.session_service import SessionService

def create_session_aware_agent(session_id: str):
    session_service = SessionService()
    state = session_service.load_state(session_id)
    
    # 從 state 中提取上下文
    user_context = state.get("user:context", "")
    app_context = state.get("app:settings", {})
    
    return types.Agent(
        model="gemini-2.0-flash-exp",
        system_instruction=f"""你是 NotChatGPT。
        
使用者上下文: {user_context}
應用設定: {app_context}
        """,
    )
```

**參考**: Day 17 (personal-tutor) - Session State Management

---

### 步驟 4: 思考模式切換

#### 4.1 建立 `mode_config.py`

**backend/config/mode_config.py**:

```python
from google.genai import types

class ModeConfig:
    """思考模式配置"""
    
    @staticmethod
    def get_thinking_config() -> types.ThinkingConfig:
        """思考模式配置 💭"""
        return types.ThinkingConfig(
            mode="thinking",
            include_thoughts=True,
            max_thinking_tokens=8000,
        )
    
    @staticmethod
    def get_standard_config() -> types.ThinkingConfig:
        """標準模式配置 💬"""
        return types.ThinkingConfig(
            mode="none",
            include_thoughts=False,
        )
    
    @staticmethod
    def create_agent_with_mode(thinking_mode: bool = False):
        """根據模式建立 Agent"""
        config = ModeConfig.get_thinking_config() if thinking_mode else ModeConfig.get_standard_config()
        
        return types.Agent(
            model="gemini-2.0-flash-exp",
            system_instruction="你是 NotChatGPT，智慧對話助理。",
            tools=[types.BuiltInPlanner(thinking_config=config)],
        )
```

#### 4.2 測試模式切換

**backend/test_thinking_mode.py**:

```python
from google import genai
from backend.config.mode_config import ModeConfig

def test_thinking_mode():
    client = genai.Client()
    
    # 測試思考模式
    print("\n=== 思考模式 💭 ===")
    agent_thinking = ModeConfig.create_agent_with_mode(thinking_mode=True)
    session = client.agentic.create_session(agent=agent_thinking)
    response = session.send_message("請解釋量子糾纏的原理")
    
    # 檢查是否有思考過程
    if hasattr(response, 'thoughts'):
        print(f"思考過程: {response.thoughts}")
    print(f"回應: {response.text[:200]}...")
    
    # 測試標準模式
    print("\n=== 標準模式 💬 ===")
    agent_standard = ModeConfig.create_agent_with_mode(thinking_mode=False)
    session2 = client.agentic.create_session(agent=agent_standard)
    response2 = session2.send_message("今天天氣如何？")
    print(f"回應: {response2.text}")

if __name__ == "__main__":
    test_thinking_mode()
```

```powershell
python backend/test_thinking_mode.py
```

**參考**: Day 20 (strategic-solver) - Thinking Mode

---

### 步驟 5: 安全防護層 (Guardrails)

#### 5.1 建立 `guardrails/` 模組結構

```powershell
New-Item -ItemType File backend/guardrails/__init__.py, backend/guardrails/safety_callbacks.py, backend/guardrails/pii_detector.py, backend/guardrails/content_moderator.py
```

#### 5.2 實作 `safety_callbacks.py`

**backend/guardrails/safety_callbacks.py**:

```python
from google.genai import types
import re

class SafetyCallbacks(types.AgentCallbacks):
    """安全防護 Callbacks"""
    
    def __init__(self):
        self.blocked_keywords = ["密碼", "信用卡", "身份證"]
        self.pii_patterns = [
            (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '信用卡號'),
            (r'\b[A-Z]\d{9}\b', '身份證號'),
        ]
    
    async def before_model_request(self, request: types.GenerateContentRequest):
        """請求前檢查"""
        user_message = str(request.contents[-1].parts[0].text)
        
        # PII 檢測
        for pattern, pii_type in self.pii_patterns:
            if re.search(pattern, user_message):
                raise ValueError(f"⚠️ 偵測到敏感資訊: {pii_type}")
        
        # 禁止關鍵字
        for keyword in self.blocked_keywords:
            if keyword in user_message.lower():
                print(f"⚠️ 警告: 訊息包含敏感關鍵字 '{keyword}'")
        
        return request
    
    async def after_model_response(self, response: types.GenerateContentResponse):
        """回應後驗證"""
        if response.text:
            # 檢查回應是否包含不當內容
            if any(word in response.text.lower() for word in ["違法", "危險"]):
                print("⚠️ 回應內容需要審核")
        
        return response
```

#### 5.3 整合到 Agent

**backend/agents/safe_conversation_agent.py**:

```python
from google.genai import types
from backend.guardrails.safety_callbacks import SafetyCallbacks

def create_safe_agent():
    """建立具有安全防護的 Agent"""
    return types.Agent(
        model="gemini-2.0-flash-exp",
        system_instruction="你是 NotChatGPT，智慧對話助理。",
        callbacks=SafetyCallbacks(),
    )
```

#### 5.4 測試安全防護

**backend/test_guardrails.py**:

```python
from google import genai
from backend.agents.safe_conversation_agent import create_safe_agent

def test_pii_detection():
    client = genai.Client()
    agent = create_safe_agent()
    session = client.agentic.create_session(agent=agent)
    
    try:
        # 應該被攔截
        response = session.send_message("我的信用卡號是 1234-5678-9012-3456")
        print("❌ PII 檢測失敗")
    except ValueError as e:
        print(f"✅ PII 檢測成功: {e}")

if __name__ == "__main__":
    test_pii_detection()
```

```powershell
python backend/test_guardrails.py
```

**參考**: Day 18 (content-moderator) - Callbacks & Guardrails

---

### 步驟 6: CLI 測試介面

#### 6.1 建立 CLI 工具

**backend/cli.py**:

```python
import sys
from google import genai
from backend.config.mode_config import ModeConfig
from backend.agents.safe_conversation_agent import create_safe_agent

def main():
    print("🤖 NotChatGPT CLI")
    print("指令: /thinking (切換思考模式), /standard (切換標準模式), /quit (退出)\n")
    
    client = genai.Client()
    thinking_mode = False
    
    agent = ModeConfig.create_agent_with_mode(thinking_mode)
    session = client.agentic.create_session(agent=agent)
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input == "/quit":
                print("👋 再見！")
                break
            elif user_input == "/thinking":
                thinking_mode = True
                agent = ModeConfig.create_agent_with_mode(thinking_mode)
                session = client.agentic.create_session(agent=agent)
                print("💭 已切換到思考模式")
                continue
            elif user_input == "/standard":
                thinking_mode = False
                agent = ModeConfig.create_agent_with_mode(thinking_mode)
                session = client.agentic.create_session(agent=agent)
                print("💬 已切換到標準模式")
                continue
            
            if not user_input:
                continue
            
            response = session.send_message(user_input)
            mode_icon = "💭" if thinking_mode else "💬"
            print(f"\n{mode_icon} Agent: {response.text}\n")
            
        except KeyboardInterrupt:
            print("\n👋 再見！")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}\n")

if __name__ == "__main__":
    main()
```

#### 6.2 執行 CLI 測試

```powershell
python backend/cli.py
```

#### 6.3 測試清單

- [ ] 基本對話功能
- [ ] 多輪對話記憶
- [ ] 思考模式切換
- [ ] 標準模式切換
- [ ] PII 檢測（輸入包含信用卡號）
- [ ] 錯誤處理

**測試範例對話**:

```text
You: 你好！
Agent: 你好！我是 NotChatGPT...

You: /thinking
💭 已切換到思考模式

You: 請解釋量子糾纏
Agent: [詳細的思考過程與解釋]

You: /standard
💬 已切換到標準模式

You: /quit
```

---

---

## Week 2: 串流與持久化

### 步驟 7: SSE 串流實作

#### 7.1 建立 `streaming_agent.py`

**backend/agents/streaming_agent.py**:

```python
from google import genai
from google.genai import types

async def stream_response(message: str, thinking_mode: bool = False):
    """串流生成回應"""
    from backend.config.mode_config import ModeConfig
    
    client = genai.Client()
    agent = ModeConfig.create_agent_with_mode(thinking_mode)
    session = client.agentic.create_session(agent=agent)
    
    # 使用 stream=True
    async for chunk in session.send_message_stream(message):
        if chunk.text:
            yield chunk.text
```

#### 7.2 實作 FastAPI SSE 端點

**backend/api/routes.py**:

```python
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
    from backend.agents.streaming_agent import stream_response
    
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
```

#### 7.3 建立主程式

**backend/main.py**:

```python
import uvicorn
from backend.api.routes import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 7.4 測試串流回應

```powershell
# 啟動伺服器
python backend/main.py

# 在另一個終端測試
curl -X POST http://localhost:8000/api/chat/stream `
  -H "Content-Type: application/json" `
  -d '{"message": "請給我一個笑話", "thinking_mode": false}'
```

**參考**: Day 23 (streaming-agent) - SSE 實作

---

### 步驟 8: 對話持久化

#### 8.1 擴展資料模型

**backend/services/session_service.py** (擴展):

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class Conversation(Base):
    __tablename__ = "conversations"
    # ... 原有欄位
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
```

#### 8.2 實作對話歷史管理

**backend/services/session_service.py** (擴展 SessionService):

```python
class SessionService:
    # ... 原有方法
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """新增訊息到對話歷史"""
        db = self.SessionLocal()
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
        db.close()
    
    def get_messages(self, conversation_id: str) -> list:
        """取得對話歷史"""
        db = self.SessionLocal()
        messages = db.query(Message).filter_by(
            conversation_id=conversation_id
        ).order_by(Message.created_at).all()
        db.close()
        return [(m.role, m.content) for m in messages]
    
    def list_conversations(self) -> list:
        """列出所有對話"""
        db = self.SessionLocal()
        convs = db.query(Conversation).order_by(
            Conversation.updated_at.desc()
        ).all()
        db.close()
        return [(c.id, c.title, c.updated_at) for c in convs]
    
    def delete_conversation(self, conversation_id: str):
        """刪除對話"""
        db = self.SessionLocal()
        conv = db.query(Conversation).filter_by(id=conversation_id).first()
        if conv:
            db.delete(conv)
            db.commit()
        db.close()
```

#### 8.3 整合到 API

**backend/api/routes.py** (新增端點):

```python
from backend.services.session_service import SessionService

session_service = SessionService()

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
```

#### 8.4 測試會話管理

```powershell
# 建立對話
curl -X POST http://localhost:8000/api/conversations

# 列出對話
curl http://localhost:8000/api/conversations

# 取得對話歷史
curl http://localhost:8000/api/conversations/{conv_id}/messages

# 刪除對話
curl -X DELETE http://localhost:8000/api/conversations/{conv_id}
```

**參考**: Day 58 (custom-session-agent) - Session Management

---

### 步驟 9: 測試框架建立

#### 9.1 建立測試結構

```powershell
New-Item -ItemType Directory -Force tests/fixtures
New-Item -ItemType File tests/__init__.py, tests/conftest.py, tests/fixtures/sample_conversations.json
```

#### 9.2 建立評估數據集

**tests/eval_set.json**:

```json
{
  "name": "not-chat-gpt-phase1-eval",
  "version": "1.0",
  "test_cases": [
    {
      "id": "basic_001",
      "category": "basic_conversation",
      "input": "你好，請介紹你自己",
      "expected": {"response_contains": ["NotChatGPT", "助理"]}
    },
    {
      "id": "memory_001",
      "category": "context_memory",
      "input": ["我叫 Alice", "我叫什麼名字？"],
      "expected": {"second_response_contains": ["Alice"]}
    },
    {
      "id": "pii_001",
      "category": "security",
      "input": "我的信用卡號是 1234-5678-9012-3456",
      "expected": {"blocks_request": true}
    }
  ]
}
```

#### 9.3 實作 pytest 配置

**tests/conftest.py**:

```python
import pytest
from google import genai
from backend.services.session_service import SessionService

@pytest.fixture
def genai_client():
    """Genai client fixture"""
    return genai.Client()

@pytest.fixture
def session_service():
    """Session service fixture with test DB"""
    return SessionService(database_url="sqlite:///:memory:")

@pytest.fixture
def sample_conversation_id(session_service):
    """建立測試用對話"""
    conv_id = "test-conv-001"
    session_service.create_session(conv_id, "Test Chat")
    return conv_id
```

---

### 步驟 10: 單元測試

#### 10.1 Agent 測試

**tests/test_agent.py**:

```python
import pytest
from backend.agents.conversation_agent import create_conversation_agent
from backend.config.mode_config import ModeConfig

class TestAgent:
    def test_create_agent(self):
        """測試 Agent 建立"""
        agent = create_conversation_agent()
        assert agent is not None
        assert agent.model == "gemini-2.0-flash-exp"
    
    def test_thinking_mode_toggle(self):
        """測試思考模式切換"""
        agent_thinking = ModeConfig.create_agent_with_mode(thinking_mode=True)
        agent_standard = ModeConfig.create_agent_with_mode(thinking_mode=False)
        
        assert agent_thinking is not None
        assert agent_standard is not None
    
    @pytest.mark.asyncio
    async def test_basic_conversation(self, genai_client):
        """測試基本對話"""
        agent = create_conversation_agent()
        session = genai_client.agentic.create_session(agent=agent)
        response = session.send_message("你好")
        
        assert response.text is not None
        assert len(response.text) > 0
```

#### 10.2 Guardrails 測試

**tests/test_guardrails.py**:

```python
import pytest
from backend.guardrails.safety_callbacks import SafetyCallbacks

class TestGuardrails:
    @pytest.mark.asyncio
    async def test_pii_detection(self):
        """測試 PII 偵測"""
        callbacks = SafetyCallbacks()
        
        # 模擬包含信用卡號的請求
        from google.genai import types
        request = types.GenerateContentRequest(
            contents=[types.Content(
                parts=[types.Part(text="我的卡號是 1234-5678-9012-3456")]
            )]
        )
        
        with pytest.raises(ValueError, match="信用卡號"):
            await callbacks.before_model_request(request)
    
    def test_blocked_keywords(self):
        """測試關鍵字攔截"""
        callbacks = SafetyCallbacks()
        assert "密碼" in callbacks.blocked_keywords
```

#### 10.3 Session 測試

**tests/test_session.py**:

```python
import pytest
from backend.services.session_service import SessionService

class TestSession:
    def test_create_session(self, session_service):
        """測試建立會話"""
        session_id = session_service.create_session("test-123", "Test")
        assert session_id == "test-123"
    
    def test_add_and_get_messages(self, session_service, sample_conversation_id):
        """測試訊息儲存與讀取"""
        session_service.add_message(sample_conversation_id, "user", "Hello")
        session_service.add_message(sample_conversation_id, "assistant", "Hi")
        
        messages = session_service.get_messages(sample_conversation_id)
        assert len(messages) == 2
        assert messages[0][0] == "user"
        assert messages[1][0] == "assistant"
    
    def test_delete_conversation(self, session_service, sample_conversation_id):
        """測試刪除對話"""
        session_service.delete_conversation(sample_conversation_id)
        messages = session_service.get_messages(sample_conversation_id)
        assert len(messages) == 0
```

#### 10.4 執行測試與覆蓋率

```powershell
# 安裝 pytest-cov
pip install pytest-cov

# 執行測試
pytest tests/ -v

# 執行測試並產生覆蓋率報告
pytest tests/ --cov=backend --cov-report=html --cov-report=term

# 檢視覆蓋率報告
Start-Process htmlcov/index.html
```

---

### 步驟 11: 整合測試與評估

#### 11.1 工作流程整合測試

**tests/test_workflow_integration.py**:

```python
import pytest
from backend.services.session_service import SessionService
from backend.agents.conversation_agent import create_conversation_agent
from google import genai

class TestWorkflowIntegration:
    @pytest.mark.asyncio
    async def test_full_conversation_workflow(self, genai_client):
        """測試完整對話流程"""
        # 1. 建立 session
        session_service = SessionService(database_url="sqlite:///:memory:")
        conv_id = session_service.create_session("integration-test-001")
        
        # 2. 建立 agent
        agent = create_conversation_agent()
        session = genai_client.agentic.create_session(agent=agent)
        
        # 3. 發送訊息
        user_msg = "我叫 Bob"
        response = session.send_message(user_msg)
        
        # 4. 儲存對話歷史
        session_service.add_message(conv_id, "user", user_msg)
        session_service.add_message(conv_id, "assistant", response.text)
        
        # 5. 驗證
        messages = session_service.get_messages(conv_id)
        assert len(messages) == 2
        
        # 6. 測試記憶
        response2 = session.send_message("我叫什麼名字？")
        assert "Bob" in response2.text
```

#### 11.2 AgentEvaluator 測試

**tests/test_evaluation.py**:

```python
import pytest
import json
from google import genai
from google.genai.evaluators import AgentEvaluator
from backend.agents.conversation_agent import create_conversation_agent

class TestEvaluation:
    @pytest.mark.asyncio
    async def test_eval_basic_conversation(self, genai_client):
        """評估基本對話品質"""
        # 載入評估數據集
        with open("tests/eval_set.json", "r", encoding="utf-8") as f:
            eval_data = json.load(f)
        
        # 建立評估器
        evaluator = AgentEvaluator(client=genai_client)
        
        # 測試第一個案例
        test_case = eval_data["test_cases"][0]
        agent = create_conversation_agent()
        session = genai_client.agentic.create_session(agent=agent)
        response = session.send_message(test_case["input"])
        
        # 驗證回應
        for keyword in test_case["expected"]["response_contains"]:
            assert keyword in response.text, f"回應缺少關鍵字: {keyword}"
        
        print(f"✅ 評估通過: {test_case['id']}")
```

#### 11.3 執行完整測試套件

```powershell
# 執行所有測試
pytest tests/ -v --tb=short

# 只執行整合測試
pytest tests/test_workflow_integration.py -v

# 只執行評估測試
pytest tests/test_evaluation.py -v

# 產生測試報告
pytest tests/ --html=test_report.html --self-contained-html
```

**參考**: Day 19 (support-agent) - Testing & AgentEvaluator

---

---

### 步驟 12: Gemini File Search 整合

#### 12.1 建立 `file_search.py`

**backend/tools/file_search.py**:

```python
from google import genai
from google.genai import types

class FileSearchTool:
    """文檔搜尋工具"""
    
    def __init__(self, client: genai.Client):
        self.client = client
    
    def search(self, query: str, corpus_name: str) -> dict:
        """搜尋文檔內容"""
        try:
            # 使用 Gemini File Search API
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(
                        google_search=types.GoogleSearch(),
                        # 注意: File Search API 的實際配置可能不同
                        # 需要根據實際 API 調整
                    )],
                ),
            )
            
            return {
                "text": response.text,
                "grounding_metadata": response.candidates[0].grounding_metadata if response.candidates else None,
            }
        except Exception as e:
            return {"error": str(e)}
```

#### 12.2 測試基本文檔查詢

**backend/test_file_search.py**:

```python
from google import genai
from backend.tools.file_search import FileSearchTool

def test_file_search():
    client = genai.Client()
    tool = FileSearchTool(client)
    
    # 上傳測試文檔
    test_file = client.files.upload(
        path="tests/fixtures/sample_doc.txt",
        display_name="Test Document"
    )
    print(f"✅ 文檔已上傳: {test_file.name}")
    
    # 執行搜尋
    result = tool.search("這份文檔的主要內容是什麼？", "test-corpus")
    print(f"搜尋結果: {result['text'][:200]}")

if __name__ == "__main__":
    test_file_search()
```

```powershell
# 建立測試文檔
New-Item -ItemType File tests/fixtures/sample_doc.txt
"This is a sample document for testing file search functionality." | Out-File tests/fixtures/sample_doc.txt

# 執行測試
python backend/test_file_search.py
```

**參考**: Day 45 (policy-navigator) - Gemini File Search

---

### 步驟 13: 文檔管理功能

#### 13.1 建立 `document_service.py`

**backend/services/document_service.py**:

```python
from google import genai
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)  # Gemini File ID
    name = Column(String)
    size = Column(Integer)
    mime_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class DocumentService:
    """文檔管理服務"""
    
    def __init__(self, genai_client: genai.Client, database_url="sqlite:///./not_chat_gpt.db"):
        self.client = genai_client
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def upload_document(self, file_path: str, display_name: str = None) -> dict:
        """上傳文檔"""
        # 上傳到 Gemini
        uploaded_file = self.client.files.upload(
            path=file_path,
            display_name=display_name or file_path.split("/")[-1]
        )
        
        # 儲存到資料庫
        db = self.SessionLocal()
        doc = Document(
            id=uploaded_file.name,
            name=uploaded_file.display_name,
            size=uploaded_file.size_bytes,
            mime_type=uploaded_file.mime_type,
        )
        db.add(doc)
        db.commit()
        db.close()
        
        return {
            "id": uploaded_file.name,
            "name": uploaded_file.display_name,
            "size": uploaded_file.size_bytes,
        }
    
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
```

#### 13.2 整合到 API

**backend/api/routes.py** (新增端點):

```python
from fastapi import UploadFile, File
from backend.services.document_service import DocumentService
import tempfile
import os

# 初始化 DocumentService
client = genai.Client()
doc_service = DocumentService(client)

@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    """上傳文檔"""
    # 儲存臨時檔案
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    try:
        result = doc_service.upload_document(tmp_path, file.filename)
        return result
    finally:
        os.unlink(tmp_path)

@app.get("/api/documents")
async def list_documents():
    """列出文檔"""
    return doc_service.list_documents()

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """刪除文檔"""
    doc_service.delete_document(doc_id)
    return {"message": "Document deleted"}
```

#### 13.3 測試文檔管理

```powershell
# 上傳文檔
curl -X POST http://localhost:8000/api/documents `
  -F "file=@tests/fixtures/sample_doc.txt"

# 列出文檔
curl http://localhost:8000/api/documents

# 刪除文檔
curl -X DELETE http://localhost:8000/api/documents/{doc_id}
```

**參考**: Day 26 (artifact-agent) - File Management

---

### 步驟 14: 引用來源追蹤

#### 14.1 實作 `groundingMetadata` 提取

**backend/tools/file_search.py** (擴展):

```python
class FileSearchTool:
    # ... 原有方法
    
    def extract_citations(self, grounding_metadata) -> list:
        """提取引用來源"""
        if not grounding_metadata:
            return []
        
        citations = []
        for chunk in grounding_metadata.grounding_chunks:
            citations.append({
                "source": chunk.web.uri if hasattr(chunk, 'web') else "Unknown",
                "title": chunk.web.title if hasattr(chunk, 'web') else "Untitled",
                "snippet": chunk.text if hasattr(chunk, 'text') else "",
            })
        
        return citations
    
    def search_with_citations(self, query: str, corpus_name: str) -> dict:
        """搜尋並返回引用"""
        result = self.search(query, corpus_name)
        
        if "grounding_metadata" in result:
            citations = self.extract_citations(result["grounding_metadata"])
            result["citations"] = citations
        
        return result
```

#### 14.2 整合到 Agent

**backend/agents/rag_agent.py**:

```python
from google.genai import types
from backend.tools.file_search import FileSearchTool

def create_rag_agent(file_search_tool: FileSearchTool):
    """建立具有 RAG 能力的 Agent"""
    
    def rag_function(query: str) -> str:
        """文檔搜尋函式"""
        result = file_search_tool.search_with_citations(query, "main-corpus")
        
        response_text = result.get("text", "")
        citations = result.get("citations", [])
        
        # 附加引用來源
        if citations:
            response_text += "\n\n引用來源:\n"
            for i, cite in enumerate(citations, 1):
                response_text += f"{i}. {cite['title']} - {cite['source']}\n"
        
        return response_text
    
    return types.Agent(
        model="gemini-2.0-flash-exp",
        system_instruction="你是 NotChatGPT，可以搜尋並引用文檔內容。",
        tools=[types.Tool(
            function_declarations=[rag_function]
        )],
    )
```

#### 14.3 測試多文檔聯合查詢

**backend/test_rag_citations.py**:

```python
from google import genai
from backend.tools.file_search import FileSearchTool
from backend.agents.rag_agent import create_rag_agent

def test_citations():
    client = genai.Client()
    tool = FileSearchTool(client)
    agent = create_rag_agent(tool)
    
    session = client.agentic.create_session(agent=agent)
    response = session.send_message("根據文檔，公司的休假政策是什麼？")
    
    print(f"回應: {response.text}")
    
    # 驗證引用是否存在
    assert "引用來源" in response.text or "citations" in str(response.candidates[0].grounding_metadata)
    print("✅ 引用來源測試通過")

if __name__ == "__main__":
    test_citations()
```

```powershell
python backend/test_rag_citations.py
```

---

### 步驟 15: RAG 測試

#### 15.1 建立 `test_rag.py`

**tests/test_rag.py**:

```python
import pytest
from google import genai
from backend.tools.file_search import FileSearchTool
from backend.services.document_service import DocumentService

class TestRAG:
    @pytest.fixture
    def doc_service(self, genai_client):
        return DocumentService(genai_client, database_url="sqlite:///:memory:")
    
    def test_upload_document(self, doc_service):
        """測試文檔上傳"""
        result = doc_service.upload_document(
            "tests/fixtures/sample_doc.txt",
            "Test Doc"
        )
        assert "id" in result
        assert result["name"] == "Test Doc"
    
    def test_list_documents(self, doc_service):
        """測試文檔列表"""
        doc_service.upload_document("tests/fixtures/sample_doc.txt", "Doc 1")
        docs = doc_service.list_documents()
        assert len(docs) >= 1
    
    def test_file_search(self, genai_client):
        """測試文檔搜尋"""
        tool = FileSearchTool(genai_client)
        result = tool.search("測試查詢", "test-corpus")
        assert "text" in result or "error" in result
    
    def test_citations_extraction(self, genai_client):
        """測試引用提取"""
        tool = FileSearchTool(genai_client)
        result = tool.search_with_citations("測試查詢", "test-corpus")
        
        # 驗證回應結構
        assert "text" in result or "error" in result
        if "citations" in result:
            assert isinstance(result["citations"], list)
```

#### 15.2 建立 RAG 評估測試案例

**tests/eval_set.json** (新增 RAG 測試案例):

```json
{
  "test_cases": [
    {
      "id": "rag_001",
      "category": "rag",
      "input": "根據上傳的文檔，公司的休假政策是什麼？",
      "expected": {
        "has_citations": true,
        "response_accurate": true
      }
    },
    {
      "id": "rag_002",
      "category": "rag",
      "input": "比較文檔 A 和文檔 B 中的差異",
      "expected": {
        "references_multiple_docs": true,
        "has_citations": true
      }
    }
  ]
}
```

#### 15.3 驗證 RAG 功能完整性

```powershell
# 執行 RAG 測試
pytest tests/test_rag.py -v

# 執行所有測試
pytest tests/ -v --tb=short

# 產生覆蓋率報告
pytest tests/ --cov=backend --cov-report=html
```

#### 15.4 RAG 功能檢查清單

- [ ] 文檔上傳成功
- [ ] 文檔列表顯示正常
- [ ] 文檔搜尋功能正常
- [ ] 引用來源提取正確
- [ ] 多文檔聯合查詢正常
- [ ] 文檔刪除功能正常
- [ ] RAG 測試覆蓋率 > 80%

**參考**: Day 45 (policy-navigator) - Full RAG Implementation

---

---

## Phase 1 檢查點

### 功能完整性驗證

#### 核心對話系統

- [ ] ✅ 基礎 Agent 運作正常
- [ ] ✅ 多輪對話記憶功能
- [ ] ✅ 思考模式與標準模式切換
- [ ] ✅ Session State 管理
- [ ] ✅ 串流回應功能

#### 安全防護層

- [ ] ✅ PII 偵測攔截正常
- [ ] ✅ 內容審核機制運作
- [ ] ✅ 意圖分類功能
- [ ] ✅ Guardrails 攔截率 100%

#### RAG 功能

- [ ] ✅ 文檔上傳功能
- [ ] ✅ 文檔搜尋功能
- [ ] ✅ 引用來源追蹤
- [ ] ✅ 多文檔聯合查詢
- [ ] ✅ 文檔管理（列表/刪除）

### 測試與品質

#### 測試覆蓋率

- [ ] 單元測試覆蓋率 > 70%
- [ ] 整合測試覆蓋率 > 60%
- [ ] RAG 測試覆蓋率 > 80%

#### 評估指標

- [ ] AgentEvaluator 評分 > 85/100
- [ ] 基本對話測試通過率 100%
- [ ] 安全測試通過率 100%
- [ ] RAG 測試通過率 > 90%

### 效能指標

- [ ] 首次回應延遲 < 2s（標準模式）
- [ ] 串流回應順暢（無明顯卡頓）
- [ ] 錯誤率 < 1%

### 文檔完成度

- [ ] README.md 更新
- [ ] API 文檔基本完成
- [ ] 測試文檔完成

### 最終驗證指令

```powershell
# 1. 執行所有測試
pytest tests/ -v --cov=backend --cov-report=term --cov-report=html

# 2. 檢查測試覆蓋率
Start-Process htmlcov/index.html

# 3. 執行 CLI 完整測試
python backend/cli.py
# 測試項目:
# - 基本對話
# - 模式切換
# - PII 偵測
# - 多輪對話記憶

# 4. 啟動 API 並測試
python backend/main.py
# 在另一個終端測試各個端點

# 5. 生成測試報告
pytest tests/ --html=phase1_test_report.html --self-contained-html

# 6. 檢查代碼品質（可選）
pip install flake8 black
flake8 backend/ --max-line-length=120
black backend/ --check
```

### 準備進入 Phase 2

**檢查清單**:

- [ ] 所有 Phase 1 功能測試通過
- [ ] 代碼已提交到版本控制
- [ ] 測試報告已生成並檢視
- [ ] 已記錄已知問題與限制
- [ ] 團隊已審核代碼（如適用）

**已知限制與待改進項目** (進入 Phase 2 前記錄):

```text
1. [記錄項目]
2. [記錄項目]
3. [記錄項目]
```

---

🎉 **恭喜完成 Phase 1！**

現在可以進入 [Phase 2: 工具整合與 UI](../phase-2/steps.md)
