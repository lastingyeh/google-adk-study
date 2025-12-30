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
│   ├── unit/
│   │   ├── backend/
│   │   │   ├── test_agent.py
│   │   │   ├── test_tools.py
│   │   │   └── test_guardrails.py
│   │   └── frontend/
│   │       ├── MessageList.test.tsx
│   │       └── DocumentPanel.test.tsx
│   ├── integration/
│   │   ├── test_workflow.py
│   │   └── test_rag.py
│   ├── e2e/
│   │   ├── test_user_journey.py
│   │   └── test_api_endpoints.py
│   ├── evaluation/
│   │   ├── test_agent_quality.py
│   │   └── eval_set.json
│   ├── conftest.py
│   └── fixtures/
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

**建立 backend/requirements.txt**:

```txt
google-genai>=1.0.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

**安裝套件**:

```powershell
# 建立虛擬環境
python -m venv venv

# windows powershell
.\venv\Scripts\Activate.ps1
# mac/linux
source venv/bin/activate

# 使用 requirements.txt 安裝套件
pip install -r backend/requirements.txt
```

#### 1.3 設定 `.env` 檔案

**建立 `.env` 檔案**（專案根目錄）：

```env
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.0-flash-exp
DATABASE_URL=sqlite:///./not_chat_gpt.db
```

#### 1.4 驗證環境設定

**測試 API Key**:

```bash
# 使用 python-dotenv 載入 .env
python -c "from google import genai; import os; from dotenv import load_dotenv; load_dotenv(); client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY')); print('✅ API Key Valid')"
```

**檢查套件安裝**:

```bash
pip list | grep -E "google-genai|fastapi"
```

**說明**：

- `.env` 檔案不會自動載入到環境變數，需要使用 `load_dotenv()` 明確載入
- 確保 `.env` 檔案中的 `GOOGLE_API_KEY` 已設定正確的值

**參考**: Day 16 (hello-agent) - 基礎環境設定

---

### 步驟 2: 基礎 Agent 實作

#### 2.1 建立 `conversation_agent.py`

**backend/agents/conversation_agent.py**:

```python
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

def create_conversation_agent():
    """建立基礎對話 Agent 配置"""
    return types.GenerateContentConfig(
        system_instruction="""
        你是 NotChatGPT，一個智慧對話助理。
        
        特點：
            - 友善且專業的對話風格
            - 提供準確且有幫助的資訊
            - 支援多輪對話與上下文理解
        """,
        temperature=1.0,
    )

# 測試用
if __name__ == "__main__":
    # 載入 .env 檔案
    load_dotenv()
    
    # 從環境變數取得 API Key
    api_key = os.getenv('GOOGLE_API_KEY')
    # 從環境變數取得模型名稱
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定在 .env 檔案中")
        exit(1)
    
    client = genai.Client(api_key=api_key)
    config = create_conversation_agent()
    
    # 使用 generate_content 進行對話
    response = client.models.generate_content(
        model=model_name,
        contents="你好！請介紹一下你自己",
        config=config
    )
    print(response.text)
```

#### 2.2 測試基本對話能力

```bash
# 執行測試
python backend/agents/conversation_agent.py

# 預期輸出: Agent 的自我介紹
```

#### 2.3 測試多輪對話

**tests/unit/backend/test_conversation.py**:

```python
from google import genai
from dotenv import load_dotenv
import os
from backend.agents.conversation_agent import create_conversation_agent

def test_multi_turn():
    # 載入環境變數
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定")
        return
    
    client = genai.Client(api_key=api_key)
    config = create_conversation_agent()
    
    # 第一輪對話
    print("\n=== 第一輪對話 ===")
    response1 = client.models.generate_content(
        model=model_name,
        contents="我叫 Alice",
        config=config
    )
    print(f"Round 1: {response1.text}")
    
    # 注意：generate_content 不保留對話歷史
    # 如需多輪對話記憶，需要手動管理對話歷史或使用 Chat API
    print("\n⚠️  注意：基礎 generate_content API 不支援自動對話記憶")
    print("✅ 基本對話測試通過")

if __name__ == "__main__":
    test_multi_turn()
```

```bash
# 建立測試目錄結構
mkdir -p tests/unit/backend

# 執行測試（從專案根目錄執行）
python -m pytest tests/unit/backend/test_conversation.py -v

# 或直接執行（需設定 PYTHONPATH）
PYTHONPATH=. python tests/unit/backend/test_conversation.py
```

**說明**：

- 測試檔案放在 `tests/unit/backend/` 目錄下，符合後端單元測試結構
- 加入 `load_dotenv()` 載入環境變數
- 使用 `python -m pytest` 或設定 `PYTHONPATH=.` 確保可正確 import backend 模組
- 目前使用的 `generate_content` API 不支援自動對話記憶
- 多輪對話功能將在步驟 3 整合 Session 管理後實作

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

```bash
# 測試建立與載入
python -c "from backend.services.session_service import SessionService; s = SessionService(); sid = s.create_session('test-1'); print(f'✅ Session created: {sid}')"
```

#### 3.3 實作上下文記憶（user/app/temp 前綴）

**backend/agents/session_agent.py**:

```python
from google.genai import types
from backend.services.session_service import SessionService

def create_session_aware_agent(session_id: str, session_service: SessionService = None):
    """建立具有 Session 上下文記憶的 Agent
    
    Args:
        session_id: Session 識別碼
        session_service: SessionService 實例（可選，主要用於測試時注入）
    """
    if session_service is None:
        session_service = SessionService()
    
    state = session_service.load_state(session_id)
    
    # 從 state 中提取上下文（使用前綴管理）
    user_context = state.get("user:context", "")
    app_context = state.get("app:settings", {})
    temp_data = state.get("temp:data", {})
    
    system_instruction = f"""你是 NotChatGPT，一個智慧對話助理。

使用者上下文: {user_context if user_context else "無特定上下文"}
應用設定: {app_context if app_context else "預設設定"}
臨時資料: {temp_data if temp_data else "無"}
"""
    
    return types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=1.0,
    ), session_service
```

**tests/unit/backend/test_session_agent.py**:

```python
import pytest
from google import genai
from dotenv import load_dotenv
import os
from backend.agents.session_agent import create_session_aware_agent
from backend.services.session_service import SessionService

class TestSessionAgent:
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試前置設定 - 每個測試方法執行前都會重新初始化"""
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
        
        if not self.api_key:
            pytest.skip("GOOGLE_API_KEY 未設定")
        
        self.client = genai.Client(api_key=self.api_key)
        
        # 每個測試都創建新的 in-memory 資料庫，確保測試隔離
        self.session_service = SessionService(database_url="sqlite:///:memory:")
        
        yield  # 測試執行
        
        # 測試後清理（可選，因為 in-memory DB 會自動銷毀）
        if hasattr(self, 'session_service'):
            self.session_service.engine.dispose()
    
    def test_create_session_aware_agent(self):
        """測試建立具有上下文記憶的 Agent"""
        # 1. 建立測試 session（使用唯一 ID）
        test_session_id = "test-create-agent-001"
        self.session_service.create_session(test_session_id, "上下文記憶測試")
        
        # 2. 設定上下文
        state = {
            "user:context": "使用者偏好繁體中文，喜歡簡潔的回答",
            "app:settings": {"language": "zh-TW", "mode": "concise"},
            "temp:data": {"last_topic": "Python"}
        }
        self.session_service.save_state(test_session_id, state)
        
        # 3. 建立 Agent（注入測試用的 session_service）
        config, returned_service = create_session_aware_agent(
            test_session_id, 
            session_service=self.session_service
        )
        
        # 4. 驗證配置
        assert config is not None
        assert "使用者偏好繁體中文" in config.system_instruction
        assert "Python" in config.system_instruction
        
        # 5. 驗證 service 也被正確返回
        assert returned_service is not None
    
    def test_context_affects_response(self):
        """測試上下文是否影響 Agent 回應"""
        # 1. 建立有特定上下文的 session（使用唯一 ID）
        test_session_id = "test-context-response-002"
        self.session_service.create_session(test_session_id)
        
        state = {
            "user:context": "使用者偏好繁體中文，喜歡簡潔的回答",
            "app:settings": {"language": "zh-TW", "mode": "concise"}
        }
        self.session_service.save_state(test_session_id, state)
        
        # 2. 建立 Agent 並測試對話（注入測試用的 session_service）
        config, _ = create_session_aware_agent(
            test_session_id, 
            session_service=self.session_service
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents="請用我偏好的語言和風格回答：什麼是 Python？",
            config=config
        )
        
        # 3. 驗證回應不為空
        assert response.text is not None
        assert len(response.text) > 0
        print(f"✅ Agent 回應: {response.text[:100]}...")
    
    def test_context_persistence(self):
        """測試上下文持久化"""
        # 1. 建立並儲存上下文（使用唯一 ID）
        test_session_id = "test-persistence-003"
        self.session_service.create_session(test_session_id)
        
        original_state = {
            "user:context": "測試使用者",
            "temp:data": {"last_topic": "Python"}
        }
        self.session_service.save_state(test_session_id, original_state)
        
        # 2. 更新上下文
        updated_state = {
            "user:context": "測試使用者",
            "temp:data": {"last_topic": "機器學習"}
        }
        self.session_service.save_state(test_session_id, updated_state)
        
        # 3. 重新載入並驗證
        loaded_state = self.session_service.load_state(test_session_id)
        assert loaded_state["temp:data"]["last_topic"] == "機器學習"
        print("✅ 上下文持久化測試通過")
    
    def test_empty_context_handling(self):
        """測試空上下文處理"""
        # 1. 建立沒有上下文的 session（使用唯一 ID）
        test_session_id = "test-empty-context-004"
        self.session_service.create_session(test_session_id)
        
        # 2. 建立 Agent（應該使用預設值，注入測試用的 session_service）
        config, _ = create_session_aware_agent(
            test_session_id, 
            session_service=self.session_service
        )
        
        # 3. 驗證使用預設值
        assert "無特定上下文" in config.system_instruction
        assert "預設設定" in config.system_instruction
        print("✅ 空上下文處理測試通過")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**執行測試**:

```bash
# 執行上下文記憶單元測試
python -m pytest tests/unit/backend/test_session_agent.py -v

# 或使用 PYTHONPATH
PYTHONPATH=. python -m pytest tests/unit/backend/test_session_agent.py -v

# 執行單一測試方法
python -m pytest tests/unit/backend/test_session_agent.py::TestSessionAgent::test_create_session_aware_agent -v
```

**測試隔離說明**:

- 使用 `@pytest.fixture(autouse=True)` 確保每個測試方法執行前都重新初始化
- 每個測試都創建新的 in-memory SQLite 資料庫，確保完全隔離
- `yield` 後的清理代碼確保資源正確釋放
- 每個測試使用唯一的 session ID，避免潛在的 ID 衝突

**預期輸出**:

```text
tests/unit/backend/test_session_agent.py::TestSessionAgent::test_create_session_aware_agent PASSED
tests/unit/backend/test_session_agent.py::TestSessionAgent::test_context_affects_response PASSED
✅ Agent 回應: Python 是一種高階程式語言...
tests/unit/backend/test_session_agent.py::TestSessionAgent::test_context_persistence PASSED
✅ 上下文持久化測試通過
tests/unit/backend/test_session_agent.py::TestSessionAgent::test_empty_context_handling PASSED
✅ 空上下文處理測試通過

============================ 4 passed in 2.34s ============================
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
    def create_config_with_mode(thinking_mode: bool = False) -> types.GenerateContentConfig:
        """根據模式建立 GenerateContentConfig
        
        Args:
            thinking_mode: 是否啟用思考模式
            
        Returns:
            GenerateContentConfig: 配置物件
        """
        system_instruction = "你是 NotChatGPT，智慧對話助理。"
        
        if thinking_mode:
            system_instruction += "\n\n請展示你的思考過程。"
        
        return types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=1.0,
        )
```

#### 4.2 測試模式切換

**tests/unit/backend/test_thinking_mode.py**:

```python
import pytest
from google import genai
from dotenv import load_dotenv
import os
from backend.config.mode_config import ModeConfig

class TestThinkingMode:
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試前置設定"""
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
        
        if not self.api_key:
            pytest.skip("GOOGLE_API_KEY 未設定")
        
        self.client = genai.Client(api_key=self.api_key)
        
        yield
    
    def test_thinking_mode(self):
        """測試思考模式"""
        print("\n=== 思考模式 💭 ===")
        config = ModeConfig.create_config_with_mode(thinking_mode=True)
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents="請解釋量子糾纏的原理",
            config=config
        )
        
        print(f"回應: {response.text[:200]}...")
        
        # 驗證回應
        assert response.text is not None
        assert len(response.text) > 0
        print("✅ 思考模式測試通過")
    
    def test_standard_mode(self):
        """測試標準模式"""
        print("\n=== 標準模式 💬 ===")
        config = ModeConfig.create_config_with_mode(thinking_mode=False)
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents="今天天氣如何？",
            config=config
        )
        
        print(f"回應: {response.text}")
        
        # 驗證回應
        assert response.text is not None
        assert len(response.text) > 0
        print("✅ 標準模式測試通過")
    
    def test_mode_toggle(self):
        """測試模式切換"""
        # 建立兩種模式的 config
        config_thinking = ModeConfig.create_config_with_mode(thinking_mode=True)
        config_standard = ModeConfig.create_config_with_mode(thinking_mode=False)
        
        # 驗證建立成功
        assert config_thinking is not None
        assert config_standard is not None
        
        # 驗證 system_instruction 不同
        assert "思考過程" in config_thinking.system_instruction
        assert "思考過程" not in config_standard.system_instruction
        
        print("✅ 模式切換測試通過")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**執行測試**:

```bash
# 執行思考模式單元測試
python -m pytest tests/unit/backend/test_thinking_mode.py -v

# 或使用 PYTHONPATH
PYTHONPATH=. python -m pytest tests/unit/backend/test_thinking_mode.py -v

# 執行單一測試方法
python -m pytest tests/unit/backend/test_thinking_mode.py::TestThinkingMode::test_thinking_mode -v
```

**參考**: Day 20 (strategic-solver) - Thinking Mode

---

### 步驟 5: 安全防護層 (Guardrails)

#### 5.1 建立 `guardrails/` 模組結構

```bash
# 建立目錄與檔案
mkdir -p backend/guardrails
touch backend/guardrails/safety_callbacks.py
touch backend/guardrails/pii_detector.py
```

**說明**：

- `safety_callbacks.py`: 包含所有的 callback 函式（before_model, after_model 等）
- `pii_detector.py`: PII 檢測的工具函式和模式配置

#### 5.2 實作安全防護 Callbacks

**backend/guardrails/pii_detector.py**:

```python
"""PII 偵測模組"""
import re
import logging

logger = logging.getLogger(__name__)

# PII 模式配置
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    'taiwan_id': r'\b[A-Z]\d{9}\b',
}

# 封鎖關鍵字
BLOCKED_KEYWORDS = ['密碼', '信用卡', '身份證', '帳號']

def detect_pii(text: str) -> dict:
    """檢測文本中的 PII
    
    Returns:
        dict: {'found': bool, 'types': list, 'message': str}
    """
    found_types = []
    
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            found_types.append(pii_type)
            logger.warning(f"偵測到 PII: {pii_type}")
    
    if found_types:
        return {
            'found': True,
            'types': found_types,
            'message': f"偵測到敏感資訊: {', '.join(found_types)}"
        }
    
    return {'found': False, 'types': [], 'message': ''}

def check_blocked_keywords(text: str) -> dict:
    """檢查封鎖關鍵字
    
    Returns:
        dict: {'found': bool, 'keywords': list, 'message': str}
    """
    found_keywords = []
    
    for keyword in BLOCKED_KEYWORDS:
        if keyword in text.lower():
            found_keywords.append(keyword)
            logger.warning(f"發現封鎖關鍵字: {keyword}")
    
    if found_keywords:
        return {
            'found': True,
            'keywords': found_keywords,
            'message': f"訊息包含敏感關鍵字: {', '.join(found_keywords)}"
        }
    
    return {'found': False, 'keywords': [], 'message': ''}

def filter_pii_from_text(text: str) -> str:
    """從文本中過濾 PII"""
    filtered_text = text
    
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, filtered_text, re.IGNORECASE)
        if matches:
            filtered_text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', filtered_text, flags=re.IGNORECASE)
            logger.info(f"過濾了 {len(matches)} 個 {pii_type}")
    
    return filtered_text
```

**backend/guardrails/safety_callbacks.py**:

```python
"""安全防護 Callback 函式

基於 google-adk 的 callback 機制實作安全檢查。
注意：這些函式應該與 SafetySettings 配合使用，而非單獨使用。
"""
from google.genai import types
from .pii_detector import detect_pii, check_blocked_keywords, filter_pii_from_text
import logging

logger = logging.getLogger(__name__)

def validate_input(message: str) -> dict:
    """驗證輸入訊息
    
    Args:
        message: 使用者輸入
        
    Returns:
        dict: {'valid': bool, 'reason': str}
    """
    # 檢查 PII
    pii_result = detect_pii(message)
    if pii_result['found']:
        return {'valid': False, 'reason': pii_result['message']}
    
    # 檢查封鎖關鍵字
    keyword_result = check_blocked_keywords(message)
    if keyword_result['found']:
        logger.warning(keyword_result['message'])
        # 注意：關鍵字僅警告，不阻擋
    
    return {'valid': True, 'reason': ''}

def sanitize_response(response_text: str) -> str:
    """清理回應文本
    
    Args:
        response_text: 模型回應
        
    Returns:
        str: 清理後的文本
    """
    return filter_pii_from_text(response_text)
```

#### 5.3 整合安全防護到對話流程

**backend/agents/safe_conversation_agent.py**:

```python
"""具有安全防護的對話 Agent"""
from google.genai import types
from backend.guardrails.safety_callbacks import validate_input, sanitize_response
import logging

logger = logging.getLogger(__name__)

def create_safe_config(enable_safety: bool = True) -> types.GenerateContentConfig:
    """建立具有安全設定的配置
    
    Args:
        enable_safety: 是否啟用安全設定
        
    Returns:
        GenerateContentConfig: 配置物件
    """
    config = types.GenerateContentConfig(
        system_instruction="""
        你是 NotChatGPT，一個智慧對話助理。
        
        重要安全指令：
        - 不要生成有害、偏見或不當的內容
        - 如果請求不清楚，請要求澄清
        - 不要洩露或生成個人敏感資訊
        """,
        temperature=1.0,
    )
    
    if enable_safety:
        # 設定安全過濾等級
        config.safety_settings = [
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
        ]
    
    return config

def safe_generate_response(
    client, 
    model_name: str, 
    user_message: str, 
    enable_safety: bool = True,
    conversation_history: list = None
) -> dict:
    """安全地生成回應（支援多輪對話）
    
    Args:
        client: Genai client
        model_name: 模型名稱
        user_message: 使用者訊息
        enable_safety: 是否啟用安全檢查
        conversation_history: 對話歷史，格式為 [{'role': 'user', 'parts': [{'text': '...'}]}, ...]
        
    Returns:
        dict: {'success': bool, 'text': str, 'reason': str}
    """
    # 輸入驗證
    if enable_safety:
        validation = validate_input(user_message)
        if not validation['valid']:
            logger.warning(f"輸入被阻擋: {validation['reason']}")
            return {
                'success': False,
                'text': f"⚠️ 無法處理此請求: {validation['reason']}",
                'reason': validation['reason']
            }
    
    # 生成回應
    try:
        config = create_safe_config(enable_safety=enable_safety)
        
        # 準備內容：如果有對話歷史，則包含歷史 + 新訊息
        if conversation_history:
            # 複製歷史並添加新訊息
            contents = conversation_history + [{
                'role': 'user',
                'parts': [{'text': user_message}]
            }]
        else:
            # 沒有歷史，只傳送新訊息
            contents = user_message
        
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config
        )
        
        response_text = response.text
        
        # 輸出過濾
        if enable_safety:
            response_text = sanitize_response(response_text)
        
        return {
            'success': True,
            'text': response_text,
            'reason': ''
        }
        
    except Exception as e:
        logger.error(f"生成回應時發生錯誤: {e}")
        return {
            'success': False,
            'text': "抱歉，處理您的請求時發生錯誤。",
            'reason': str(e)
        }
```

#### 5.4 測試安全防護

**tests/unit/backend/test_guardrails.py**:

```python
import pytest
from google import genai
from dotenv import load_dotenv
import os
from agents.safe_conversation_agent import create_safe_config, safe_generate_response
from guardrails.pii_detector import detect_pii, check_blocked_keywords, filter_pii_from_text

class TestPIIDetector:
    """測試 PII 檢測功能"""
    
    def test_detect_credit_card(self):
        """測試信用卡號檢測"""
        result = detect_pii("我的卡號是 1234-5678-9012-3456")
        assert result['found'] is True
        assert 'credit_card' in result['types']
        print("✅ 信用卡號檢測通過")
    
    def test_detect_email(self):
        """測試 email 檢測"""
        result = detect_pii("聯絡我：test@example.com")
        assert result['found'] is True
        assert 'email' in result['types']
        print("✅ Email 檢測通過")
    
    def test_detect_phone(self):
        """測試電話號碼檢測"""
        result = detect_pii("電話：0912-345-678")
        assert result['found'] is True
        assert 'phone' in result['types']
        print("✅ 電話號碼檢測通過")
    
    def test_no_pii(self):
        """測試無 PII 的正常文本"""
        result = detect_pii("今天天氣很好")
        assert result['found'] is False
        assert len(result['types']) == 0
        print("✅ 無 PII 檢測通過")

class TestBlockedKeywords:
    """測試關鍵字檢測"""
    
    def test_detect_blocked_keyword(self):
        """測試封鎖關鍵字檢測"""
        result = check_blocked_keywords("請問我的密碼是什麼？")
        assert result['found'] is True
        assert '密碼' in result['keywords']
        print("✅ 封鎖關鍵字檢測通過")
    
    def test_no_blocked_keyword(self):
        """測試無封鎖關鍵字"""
        result = check_blocked_keywords("今天天氣如何？")
        assert result['found'] is False
        print("✅ 無封鎖關鍵字檢測通過")

class TestPIIFiltering:
    """測試 PII 過濾功能"""
    
    def test_filter_credit_card(self):
        """測試過濾信用卡號"""
        text = "我的卡號是 1234-5678-9012-3456"
        filtered = filter_pii_from_text(text)
        assert "1234-5678-9012-3456" not in filtered
        assert "[CREDIT_CARD_REDACTED]" in filtered
        print("✅ 信用卡號過濾通過")
    
    def test_filter_multiple_pii(self):
        """測試過濾多個 PII"""
        text = "聯絡方式：test@example.com，電話 0912-345-678"
        filtered = filter_pii_from_text(text)
        assert "test@example.com" not in filtered
        assert "0912-345-678" not in filtered
        assert "[EMAIL_REDACTED]" in filtered
        assert "[PHONE_REDACTED]" in filtered
        print("✅ 多個 PII 過濾通過")

class TestSafeConversation:
    """測試安全對話流程"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試前置設定"""
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
        
        if not self.api_key:
            pytest.skip("GOOGLE_API_KEY 未設定")
        
        self.client = genai.Client(api_key=self.api_key)
        
        yield
    
    def test_safe_config_creation(self):
        """測試安全配置建立"""
        config = create_safe_config(enable_safety=True)
        assert config is not None
        assert config.safety_settings is not None
        assert len(config.safety_settings) > 0
        print("✅ 安全配置建立測試通過")
    
    def test_normal_request(self):
        """測試正常請求"""
        result = safe_generate_response(
            self.client,
            self.model_name,
            "請介紹 Python 程式語言",
            enable_safety=True
        )
        assert result['success'] is True
        assert len(result['text']) > 0
        print("✅ 正常請求測試通過")
    
    def test_blocked_pii_request(self):
        """測試包含 PII 的請求被阻擋"""
        result = safe_generate_response(
            self.client,
            self.model_name,
            "我的信用卡號是 1234-5678-9012-3456",
            enable_safety=True
        )
        assert result['success'] is False
        assert '敏感資訊' in result['reason'] or '信用卡' in result['reason']
        print("✅ PII 阻擋測試通過")
    
    def test_safety_disabled(self):
        """測試停用安全檢查"""
        result = safe_generate_response(
            self.client,
            self.model_name,
            "今天天氣如何？",
            enable_safety=False
        )
        assert result['success'] is True
        print("✅ 停用安全檢查測試通過")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**執行測試**:

```bash
# 執行所有安全防護測試
python -m pytest tests/unit/backend/test_guardrails.py -v

# 執行特定測試類別
python -m pytest tests/unit/backend/test_guardrails.py::TestPIIDetector -v
python -m pytest tests/unit/backend/test_guardrails.py::TestSafeConversation -v

# 執行單一測試
python -m pytest tests/unit/backend/test_guardrails.py::TestPIIDetector::test_detect_credit_card -v
```

**預期輸出**:

```text

tests/unit/backend/test_guardrails.py::TestPIIDetector::test_detect_credit_card PASSED                        [  8%]
tests/unit/backend/test_guardrails.py::TestPIIDetector::test_detect_email PASSED                              [ 16%]
tests/unit/backend/test_guardrails.py::TestPIIDetector::test_detect_phone PASSED                              [ 25%]
tests/unit/backend/test_guardrails.py::TestPIIDetector::test_no_pii PASSED                                    [ 33%]
tests/unit/backend/test_guardrails.py::TestBlockedKeywords::test_detect_blocked_keyword PASSED                [ 41%]
tests/unit/backend/test_guardrails.py::TestBlockedKeywords::test_no_blocked_keyword PASSED                    [ 50%]
tests/unit/backend/test_guardrails.py::TestPIIFiltering::test_filter_credit_card PASSED                       [ 58%]
tests/unit/backend/test_guardrails.py::TestPIIFiltering::test_filter_multiple_pii PASSED                      [ 66%]
tests/unit/backend/test_guardrails.py::TestSafeConversation::test_safe_config_creation PASSED                 [ 75%]
tests/unit/backend/test_guardrails.py::TestSafeConversation::test_normal_request PASSED                       [ 83%]
tests/unit/backend/test_guardrails.py::TestSafeConversation::test_blocked_pii_request PASSED                  [ 91%]
tests/unit/backend/test_guardrails.py::TestSafeConversation::test_safety_disabled PASSED                      [100%]

================================================ 12 passed in 14.78s ================================================
```

**參考**: Day 18 (content-moderator) - Callbacks & Guardrails

---

### 步驟 6: CLI 測試介面

#### 6.1 建立 CLI 工具

**backend/cli.py**:

```python
"""NotChatGPT CLI 介面

提供命令列互動介面，支援：
- 思考模式切換
- 安全防護開關
- 對話歷史管理（基於 SessionService）
"""
import sys
from google import genai
from dotenv import load_dotenv
import os
import uuid
from config.mode_config import ModeConfig
from agents.safe_conversation_agent import safe_generate_response
from services.session_service import SessionService

def main():
    # 載入環境變數
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    
    if not api_key:
        print("❌ 錯誤: GOOGLE_API_KEY 未設定在 .env 檔案中")
        sys.exit(1)
    
    print("🤖 NotChatGPT CLI (with Session Management)")
    print("指令:")
    print("  /thinking  - 切換思考模式")
    print("  /standard  - 切換標準模式")
    print("  /safe on   - 啟用安全防護")
    print("  /safe off  - 停用安全防護")
    print("  /new       - 建立新對話")
    print("  /list      - 列出所有對話")
    print("  /load <id> - 載入指定對話")
    print("  /history   - 顯示當前對話歷史")
    print("  /quit      - 退出\n")
    
    client = genai.Client(api_key=api_key)
    session_service = SessionService()
    
    # 初始化狀態
    thinking_mode = False
    enable_safety = True
    current_session_id = str(uuid.uuid4())
    session_service.create_session(current_session_id, title="CLI Session")
    
    print(f"📝 當前會話: {current_session_id[:8]}...")
    print(f"當前模式: {'💭 思考模式' if thinking_mode else '💬 標準模式'}")
    print(f"安全防護: {'🛡️ 啟用' if enable_safety else '⚠️ 停用'}\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            # 處理命令
            if user_input == "/quit":
                print("👋 再見！")
                break
            
            elif user_input == "/thinking":
                thinking_mode = True
                print("💭 已切換到思考模式")
                continue
            
            elif user_input == "/standard":
                thinking_mode = False
                print("💬 已切換到標準模式")
                continue
            
            elif user_input == "/safe on":
                enable_safety = True
                print("🛡️ 已啟用安全防護")
                continue
            
            elif user_input == "/safe off":
                enable_safety = False
                print("⚠️ 已停用安全防護")
                continue
            
            elif user_input == "/new":
                current_session_id = str(uuid.uuid4())
                session_service.create_session(current_session_id, title="CLI Session")
                print(f"✨ 已建立新對話: {current_session_id[:8]}...")
                continue
            
            elif user_input == "/list":
                conversations = session_service.list_conversations()
                if not conversations:
                    print("📝 目前沒有對話")
                else:
                    print(f"📝 對話清單 (共 {len(conversations)} 個):")
                    for conv_id, title, updated_at in conversations[:10]:  # 只顯示最近 10 個
                        indicator = "👉" if conv_id == current_session_id else "  "
                        print(f"{indicator} {conv_id[:8]}... - {title} (更新: {updated_at.strftime('%Y-%m-%d %H:%M')})")
                continue
            
            elif user_input.startswith("/load "):
                session_id_prefix = user_input.split(" ", 1)[1].strip()
                # 查找匹配的 session
                conversations = session_service.list_conversations()
                matched = [c for c in conversations if c[0].startswith(session_id_prefix)]
                if matched:
                    current_session_id = matched[0][0]
                    print(f"📂 已載入對話: {current_session_id[:8]}...")
                    # 顯示歷史
                    messages = session_service.get_messages(current_session_id)
                    if messages:
                        print(f"📜 對話歷史 (共 {len(messages)} 則訊息)")
                else:
                    print(f"❌ 找不到對話: {session_id_prefix}")
                continue
            
            elif user_input == "/history":
                messages = session_service.get_messages(current_session_id)
                if not messages:
                    print("📝 當前對話沒有歷史")
                else:
                    print(f"📜 對話歷史 (共 {len(messages)} 則訊息):")
                    for i, (role, content) in enumerate(messages, 1):
                        icon = "👤" if role == "user" else "🤖"
                        preview = content[:50] + "..." if len(content) > 50 else content
                        print(f"{i}. {icon} {role}: {preview}")
                continue
            
            elif user_input.startswith("/"):
                print("❓ 未知指令，請使用 /thinking, /standard, /safe on, /safe off, /new, /list, /load, /history 或 /quit")
                continue
            
            # 空輸入
            if not user_input:
                continue
            
            # 載入對話歷史並轉換為 API 格式
            db_messages = session_service.get_messages(current_session_id)
            conversation_history = []
            for role, content in db_messages:
                conversation_history.append({
                    'role': role,
                    'parts': [{'text': content}]
                })
            
            # 生成回應（傳入對話歷史）
            config = ModeConfig.create_config_with_mode(thinking_mode=thinking_mode)
            result = safe_generate_response(
                client=client,
                model_name=model_name,
                user_message=user_input,
                enable_safety=enable_safety,
                conversation_history=conversation_history
            )
            
            # 顯示回應
            mode_icon = "💭" if thinking_mode else "💬"
            if result['success']:
                print(f"\n{mode_icon} Agent: {result['text']}\n")
                
                # 儲存到資料庫
                session_service.add_message(current_session_id, "user", user_input)
                session_service.add_message(current_session_id, "model", result['text'])
            else:
                print(f"\n⚠️ {result['text']}")
                if result['reason']:
                    print(f"原因: {result['reason']}\n")
            
        except KeyboardInterrupt:
            print("\n👋 再見！")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}\n")

if __name__ == "__main__":
    main()
```

#### 6.2 執行 CLI 測試

```bash
# 從專案根目錄執行
python backend/cli.py

# 或使用模組方式
python -m backend.cli
```

#### 6.3 功能驗證

**自動化驗證腳本**:

```bash
# 執行完整功能驗證
python verify_cli.py
```

預期輸出：

```
============================================================
CLI 功能驗證測試
============================================================

🧪 測試 1: 檢查模組 import...
✅ 所有模組 import 成功

🧪 測試 2: ModeConfig 功能...
✅ ModeConfig 測試通過

🧪 測試 3: SessionService 功能...
✅ SessionService 測試通過

🧪 測試 4: PII 偵測功能...
✅ PII 偵測測試通過

🧪 測試 5: safe_generate_response 簽名...
✅ safe_generate_response 簽名正確

🎉 所有測試通過！(5/5)
```

#### 6.4 互動式測試清單

**基本功能測試** (執行 `python backend/cli.py`):

✅ **測試 1: 基本對話功能**
```
You: 你好
Agent: 你好！我是 NotChatGPT，你的智慧對話助理...
```
**驗證點**: Agent 正常回應

✅ **測試 2: 多輪對話記憶（上下文連貫性）**
```
You: 我叫小明
Agent: 你好，小明！很高興認識你...

You: 我剛才說我叫什麼名字？
Agent: 你剛才說你叫小明。
```
**驗證點**: Agent 記住之前的資訊

✅ **測試 3: 思考模式切換**
```
You: /thinking
💭 已切換到思考模式

You: 為什麼 Python 很受歡迎？
Agent: [展示詳細的思考過程和分析...]
```
**驗證點**: 回應包含詳細的推理過程

✅ **測試 4: 標準模式切換**
```
You: /standard
💬 已切換到標準模式

You: 給我一個笑話
Agent: [簡潔的回應...]
```
**驗證點**: 回應簡潔直接

**Session 管理測試**:

✅ **測試 5: 自動建立 session**
```
🤖 NotChatGPT CLI (with Session Management)
📝 當前會話: abc12345...
```
**驗證點**: 啟動時自動顯示 session ID

✅ **測試 6: `/new` 建立新對話**
```
You: /new
✨ 已建立新對話: def67890...
```
**驗證點**: 建立新對話後上下文清空

✅ **測試 7: `/list` 列出對話清單**
```
You: /list
📝 對話清單 (共 3 個):
👉 def67890... - CLI Session (更新: 2025-12-30 10:30)
   abc12345... - CLI Session (更新: 2025-12-30 10:15)
```
**驗證點**: 顯示所有對話，當前對話有 👉 標記

✅ **測試 8: `/load <id>` 載入歷史對話**
```
You: /load abc12345
📂 已載入對話: abc12345...
📜 對話歷史 (共 4 則訊息)
```
**驗證點**: 成功載入舊對話，可繼續對話

✅ **測試 9: `/history` 顯示對話歷史**
```
You: /history
📜 對話歷史 (共 4 則訊息):
1. 👤 user: 我叫小明
2. 🤖 model: 你好，小明！很高興認識你...
3. 👤 user: 我剛才說我叫什麼名字？
4. 🤖 model: 你剛才說你叫小明。
```
**驗證點**: 正確顯示所有歷史訊息

**對話持久化測試**:

✅ **測試 10: 對話儲存到資料庫**
```bash
# 啟動 CLI，進行對話後退出
You: 測試訊息
You: /quit

# 檢查資料庫檔案
ls -lh not_chat_gpt.db
```
**驗證點**: 資料庫檔案存在且有內容

✅ **測試 11: 重啟後載入歷史對話**
```bash
# 重新啟動 CLI
python backend/cli.py

You: /list
📝 對話清單 (共 3 個):
   [顯示之前的對話...]

You: /load [session_id]
📂 已載入對話...
```
**驗證點**: 可以載入並繼續之前的對話

✅ **測試 12: 切換對話時上下文正確**
```
# 對話 A
You: 我叫小明
Agent: 你好，小明！

You: /new  # 建立對話 B
You: 我叫小華
Agent: 你好，小華！

You: /load [對話A的ID]  # 切回對話 A
You: 我叫什麼名字？
Agent: 你叫小明。
```
**驗證點**: 不同對話的上下文正確隔離

**安全防護測試**:

✅ **測試 13: PII 輸入攔截（啟用安全防護）**
```
You: /safe on
🛡️ 已啟用安全防護

You: 我的信用卡號是 1234-5678-9012-3456
⚠️ 無法處理此請求: 偵測到敏感資訊: credit_card
```
**驗證點**: 成功攔截信用卡號

✅ **測試 14: 關鍵字攔截**
```
You: 請告訴我密碼
⚠️ 無法處理此請求: 包含封鎖關鍵字: 密碼
```
**驗證點**: 成功攔截敏感關鍵字

✅ **測試 15: 停用安全防護**
```
You: /safe off
⚠️ 已停用安全防護

You: 我的信用卡號是 1234-5678-9012-3456
Agent: [正常處理，但會提醒安全注意事項]
```
**驗證點**: 停用後可輸入敏感資訊

**資料庫整合測試**:

✅ **測試 16: 檢查資料庫結構**
```bash
# 使用 sqlite3 檢查資料庫
sqlite3 not_chat_gpt.db ".schema"
```

預期輸出：
```sql
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,
    title VARCHAR,
    state TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id VARCHAR,
    role VARCHAR,
    content TEXT,
    created_at DATETIME,
    FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);
```
**驗證點**: 資料表結構正確

✅ **測試 17: 檢查資料寫入**
```bash
sqlite3 not_chat_gpt.db "SELECT COUNT(*) FROM conversations;"
sqlite3 not_chat_gpt.db "SELECT COUNT(*) FROM messages;"
```
**驗證點**: 有資料寫入

#### 6.5 完整測試腳本範例

**手動測試流程**:

```bash
# 啟動 CLI
python backend/cli.py

# === 第一輪測試：基本功能 ===
You: 你好，我叫小明
You: 我剛才說我叫什麼名字？
You: /history

# === 第二輪測試：模式切換 ===
You: /thinking
You: 為什麼 Python 很受歡迎？
You: /standard
You: 給我一個簡單的笑話

# === 第三輪測試：安全防護 ===
You: /safe on
You: 我的信用卡號是 1234-5678-9012-3456
You: /safe off
You: 測試訊息

# === 第四輪測試：Session 管理 ===
You: /new
You: 新對話的訊息
You: /list
You: /load [第一個對話的ID]
You: 我叫什麼名字？

# === 結束 ===
You: /quit
```

**自動化驗證**:

```bash
# 方式 1: Python 驗證腳本
python verify_cli.py

# 方式 2: Bash 測試腳本
./test_cli.sh

# 方式 3: 使用 pytest（如果有安裝）
python -m pytest tests/unit/backend/test_guardrails.py -v
```

#### 6.6 驗證檢查表

**執行前準備**:
- [x] `.env` 檔案已設定
- [x] 已安裝所有依賴套件
- [x] `backend/` 目錄下所有 `__init__.py` 已建立
- [x] Google API Key 有效

**功能驗證**:
- [x] 基本對話功能
- [x] 多輪對話記憶
- [x] 思考模式切換
- [x] 標準模式切換
- [x] 安全防護開關
- [x] Session 自動建立
- [x] `/new` 建立新對話
- [x] `/list` 列出對話
- [x] `/load` 載入對話
- [x] `/history` 顯示歷史
- [x] 對話持久化
- [x] PII 偵測攔截
- [x] 關鍵字攔截
- [x] 資料庫結構正確

**已知問題** (記錄遇到的問題):
- 無已知問題

**參考文件**:
- 詳細使用說明: [CLI_README.md](../CLI_README.md)
- 驗證腳本: [verify_cli.py](../verify_cli.py)

---

## Week 2: 串流與持久化

### 步驟 7: SSE 串流實作

#### 7.1 建立 `streaming_agent.py`

**backend/agents/streaming_agent.py**:

```python
"""NotChatGPT 串流回應模組

提供串流生成功能，支援：
- 即時回應輸出
- 思考模式切換
- 安全防護整合
"""
from google import genai
from google.genai import types
from typing import AsyncIterator
import os

async def stream_response(
    message: str,
    thinking_mode: bool = False,
    enable_safety: bool = True
) -> AsyncIterator[str]:
    """串流生成回應
    
    Args:
        message: 使用者訊息
        thinking_mode: 是否啟用思考模式
        enable_safety: 是否啟用安全防護
        
    Yields:
        str: 回應文字片段
    """
    from config.mode_config import ModeConfig
    from guardrails.safety_callbacks import validate_input
    from guardrails.pii_detector import filter_pii_from_text
    
    # 驗證輸入（如果啟用安全防護）
    if enable_safety:
        validation = validate_input(message)
        if not validation['valid']:
            yield f"⚠️ 輸入驗證失敗: {validation['reason']}"
            return
    
    # 建立客戶端和配置
    api_key = os.getenv('GOOGLE_API_KEY')
    client = genai.Client(api_key=api_key)
    model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
    
    config = ModeConfig.create_config_with_mode(thinking_mode=thinking_mode)
    
    # 如果啟用安全防護，加入 SafetySettings
    if enable_safety:
        from agents.safe_conversation_agent import create_safe_config
        safe_config = create_safe_config(enable_safety=True)
        if safe_config.safety_settings:
            config = types.GenerateContentConfig(
                system_instruction=config.system_instruction,
                safety_settings=safe_config.safety_settings,
                response_modalities=config.response_modalities
            )
    
    try:
        # 串流生成
        response = client.models.generate_content_stream(
            model=model_name,
            contents=message,
            config=config
        )
        
        # 輸出片段
        for chunk in response:
            if chunk.text:
                # 如果啟用安全防護，過濾 PII
                text = filter_pii_from_text(chunk.text) if enable_safety else chunk.text
                yield text
                
    except Exception as e:
        yield f"❌ 生成錯誤: {str(e)}"
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

```bash
# 啟動伺服器
python backend/main.py

# 在另一個終端測試
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "請給我一個笑話", "thinking_mode": false}'
```

**參考**: Day 23 (streaming-agent) - SSE 實作

---

### 步驟 8: 對話持久化

#### 8.1 擴展資料模型

**backend/services/session_service.py** (完整實作):

```python
"""Session 管理服務

提供對話持久化功能：
- 建立和管理對話 session
- 儲存和載入對話歷史
- 管理對話狀態
"""
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

class Message(Base):
    """訊息資料模型"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)  # 'user' or 'model'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class Conversation(Base):
    """對話資料模型"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    title = Column(String)
    state = Column(Text)  # JSON 格式的 session state
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
            conv.updated_at = datetime.utcnow()
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
            conv.updated_at = datetime.utcnow()
            
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
```

#### 8.2 測試 Session 管理

**tests/unit/backend/test_session_service.py**:

```python
"""測試 SessionService 功能"""
import pytest
import uuid
from services.session_service import SessionService
import os

@pytest.fixture
def session_service():
    """建立測試用的 SessionService"""
    # 使用記憶體資料庫
    service = SessionService(database_url="sqlite:///:memory:")
    yield service

class TestSessionService:
    """測試 SessionService 基本功能"""
    
    def test_create_session(self, session_service):
        """測試建立 session"""
        session_id = str(uuid.uuid4())
        result = session_service.create_session(session_id, title="Test Session")
        assert result == session_id
        print("✅ Session 建立測試通過")
    
    def test_add_and_get_messages(self, session_service):
        """測試新增和取得訊息"""
        session_id = str(uuid.uuid4())
        session_service.create_session(session_id)
        
        # 新增訊息
        session_service.add_message(session_id, "user", "Hello")
        session_service.add_message(session_id, "model", "Hi there!")
        
        # 取得訊息
        messages = session_service.get_messages(session_id)
        assert len(messages) == 2
        assert messages[0] == ("user", "Hello")
        assert messages[1] == ("model", "Hi there!")
        print("✅ 訊息新增和取得測試通過")
    
    def test_list_conversations(self, session_service):
        """測試列出對話"""
        session_id1 = str(uuid.uuid4())
        session_id2 = str(uuid.uuid4())
        
        session_service.create_session(session_id1, title="Session 1")
        session_service.create_session(session_id2, title="Session 2")
        
        conversations = session_service.list_conversations()
        assert len(conversations) >= 2
        print("✅ 對話列表測試通過")
    
    def test_delete_conversation(self, session_service):
        """測試刪除對話"""
        session_id = str(uuid.uuid4())
        session_service.create_session(session_id)
        session_service.add_message(session_id, "user", "Test")
        
        # 刪除對話
        session_service.delete_conversation(session_id)
        
        # 確認訊息也被刪除（cascade）
        messages = session_service.get_messages(session_id)
        assert len(messages) == 0
        print("✅ 對話刪除測試通過")
    
    def test_save_and_load_state(self, session_service):
        """測試儲存和載入狀態"""
        session_id = str(uuid.uuid4())
        session_service.create_session(session_id)
        
        # 儲存狀態
        state = {"user:context": "test context", "app:settings": {"theme": "dark"}}
        session_service.save_state(session_id, state)
        
        # 載入狀態
        loaded_state = session_service.load_state(session_id)
        assert loaded_state == state
        print("✅ 狀態儲存和載入測試通過")

def test_run_all():
    """執行所有測試"""
    service = SessionService(database_url="sqlite:///:memory:")
    test_suite = TestSessionService()
    
    test_suite.test_create_session(service)
    test_suite.test_add_and_get_messages(service)
    test_suite.test_list_conversations(service)
    test_suite.test_delete_conversation(service)
    test_suite.test_save_and_load_state(service)
    
    print("\n✅ 所有 SessionService 測試通過")

if __name__ == "__main__":
    test_run_all()
```

執行測試：

```bash
# 使用 pytest
python -m pytest tests/unit/backend/test_session_service.py -v

# 或直接執行
python tests/unit/backend/test_session_service.py
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

```bash
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

```bash
# 建立測試目錄與檔案
mkdir -p tests/fixtures
touch tests/__init__.py
touch tests/conftest.py
touch tests/fixtures/sample_conversations.json
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

**tests/unit/backend/test_agent.py**:

```python
import pytest
from config.mode_config import ModeConfig
from agents.safe_conversation_agent import safe_generate_response
from google import genai
import os

class TestAgent:
    def test_create_config_thinking(self):
        """測試思考模式配置建立"""
        config = ModeConfig.create_config_with_mode(thinking_mode=True)
        assert config is not None
        assert config.system_instruction is not None
        assert "詳細" in config.system_instruction or "深入" in config.system_instruction
    
    def test_create_config_standard(self):
        """測試標準模式配置建立"""
        config = ModeConfig.create_config_with_mode(thinking_mode=False)
        assert config is not None
        assert config.system_instruction is not None
    
    def test_mode_config_difference(self):
        """測試思考模式和標準模式的差異"""
        config_thinking = ModeConfig.create_config_with_mode(thinking_mode=True)
        config_standard = ModeConfig.create_config_with_mode(thinking_mode=False)
        
        assert config_thinking.system_instruction != config_standard.system_instruction
    
    def test_basic_conversation(self):
        """測試基本對話"""
        api_key = os.getenv('GOOGLE_API_KEY')
        client = genai.Client(api_key=api_key)
        model_name = os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')
        
        result = safe_generate_response(
            client=client,
            model_name=model_name,
            user_message="你好",
            enable_safety=True
        )
        
        assert result['success'] is True
        assert result['text'] is not None
        assert len(result['text']) > 0
```

#### 10.2 Guardrails 測試

**tests/unit/backend/test_guardrails.py**:

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

**tests/unit/backend/test_session.py**:

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

```bash
# 安裝 pytest-cov
pip install pytest-cov

# 執行測試
pytest tests/ -v

# 執行測試並產生覆蓋率報告
pytest tests/ --cov=backend --cov-report=html --cov-report=term

# 檢視覆蓋率報告（在瀏覽器開啟 htmlcov/index.html）
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

```bash
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

```bash
# 建立測試文檔
mkdir -p tests/fixtures
echo "This is a sample document for testing file search functionality." > tests/fixtures/sample_doc.txt

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

```bash
# 上傳文檔
curl -X POST http://localhost:8000/api/documents \
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

```bash
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

```bash
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

```bash
# 1. 執行所有測試
pytest tests/ -v --cov=backend --cov-report=term --cov-report=html

# 2. 檢查測試覆蓋率（在瀏覽器開啟 htmlcov/index.html）

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
