# TIL: 在 Google ADK 1.17 中註冊自定義對話服務 (Registering Custom Session Services in Google ADK 1.17)

> 📝 **原文翻譯自 Raphaël MANSUY 的 Blog**：[TIL: Registering Custom Session Services in Google ADK 1.17](https://raphaelmansuy.github.io/adk_training/blog/til-custom-session-services)


## 簡介 (Overview)
使用自定義對話存儲（Redis、MongoDB 等）擴展 ADK (Extend ADK with custom session storage (Redis, MongoDB, etc))

### 為什麼自定義對話服務很重要 (Why Custom Session Services Matter)

**問題 (The Problem)**：預設情況下，ADK 將對話存儲在記憶體中。對於生產環境，您需要：

- 持久化存儲（在伺服器重啟後保留）
- 分散式存儲（多伺服器部署）
- 自定義後端（您的特定基礎架構）

**一句話總結 (In one sentence)**：自定義對話服務讓您可以將任何存儲後端（Redis、MongoDB、PostgreSQL）註冊到 ADK 的服務註冊表，以便 `adk web` 和代理程式可以無縫使用它們。

### 為什麼您應該關注？ (Why Should You Care?)

**解決的問題：**

- 💾 **持久化對話 (Persistent Sessions)** - 在伺服器重啟後繼續存在
- 📊 **分散式系統 (Distributed Systems)** - 在多個伺服器之間共享
- 🏢 **企業整合 (Enterprise Integration)** - 使用您現有的存儲
- 🔧 **自定義後端 (Custom Backends)** - Redis、MongoDB、PostgreSQL、DynamoDB
- 🎛️ **CLI 支援 (CLI Support)** - 透過 URI 方案與 `adk web` 配合使用
- ⚡ **零代碼更改 (Zero Code Changes)** - 註冊一次，隨處使用

**非常適合：**

- 具有持久化要求的生產環境部署
- 使用特定資料庫的團隊（MongoDB 商店、Redis 快取）
- 多伺服器代理程式部署
- 具有特殊功能的自定義存儲（加密、分片）
- 雲端基礎架構（Google Cloud Storage、AWS DynamoDB）

### 快速範例 (Quick Example)

```python
from google.adk.cli import cli_tools_click
from google.adk.cli.service_registry import get_service_registry
from google.adk.sessions import BaseSessionService, Session

class RedisSessionService(BaseSessionService):
    """將對話存儲在 Redis 中，並設置 24 小時自動過期。"""

    def __init__(self, uri: str = "redis://localhost:6379", **kwargs):
        self.redis_uri = uri
        self.redis_client = redis.from_url(uri, decode_responses=True)

    async def create_session(self, *, app_name: str, user_id: str, **kwargs):
        """在 Redis 中建立並存儲對話。"""
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, app_name=app_name, user_id=user_id)
        # 存儲到 Redis，TTL 為 24 小時
        self.redis_client.set(f"session:{app_name}:{user_id}:{session_id}",
                            json.dumps(session.dict()), ex=86400)
        return session

    async def get_session(self, *, app_name: str, user_id: str,
                        session_id: str, **kwargs):
        """從 Redis 檢索對話。"""
        data = self.redis_client.get(f"session:{app_name}:{user_id}:{session_id}")
        return Session(**json.loads(data)) if data else None

    async def append_event(self, session: Session, event):
        """關鍵：當對話更新時將事件保存到 Redis。"""
        event = await super().append_event(session=session, event=event)
        # 將包含所有事件的更新後對話保存到 Redis
        key = f"session:{session.app_name}:{session.user_id}:{session.id}"
        self.redis_client.set(key, json.dumps(session.dict()), ex=86400)
        return event

# 註冊到服務註冊表
def redis_factory(uri: str, **kwargs):
    kwargs_copy = kwargs.copy()
    kwargs_copy.pop("agents_dir", None)
    return RedisSessionService(uri=uri, **kwargs_copy)

registry = get_service_registry()
registry.register_session_service("redis", redis_factory)

if __name__ == '__main__':
    cli_tools_click.main()
```

**然後執行：**

```bash
# 從 CLI 使用 Redis 對話
python app.py web agents/ --session_service_uri=redis://localhost:6379

# 對話將自動持久化到 Redis！
```

### 運作原理 (3 個關鍵概念) (How It Works (3 Key Concepts))

#### 1. 服務註冊表模式 (Service Registry Pattern)

ADK 有一個**全域服務註冊表**，將 URI 方案映射到工廠。流程如下：

```mermaid
graph TD
    subgraph "服務註冊表"
        subgraph "(get_service_registry())"
            Registry["'redis'  → redis_factory()<br/>建立 RedisSessionService 實例<br/>從 Redis 加載對話"]
        end
    end

    Run["執行: adk web --session_service_uri=redis://localhost:6379"]
    Parse["解析 URI 方案: 'redis'"]
    Lookup["查找工廠: registry.get_session_service_factory('redis')"]
    Call["調用工廠: redis_factory(uri='redis://localhost:6379')"]
    Return["返回: 準備就緒的 RedisSessionService 實例"]

    Run --> Parse
    Parse --> Lookup
    Lookup --> Call
    Call --> Return
```

#### 2. 工廠函數模式 (Factory Function Pattern)

您的工廠接收 **URI 字串** 並返回一個 **對話服務實例**：

```python
def redis_factory(uri: str, **kwargs):
    """
    工廠從 CLI 接收完整的 URI。

    參數：
        uri: 完整的 URI 字串 (例如, "redis://localhost:6379")
        **kwargs: 來自 ADK 的額外選項

    返回：
        準備就緒的 RedisSessionService 實例
    """
    kwargs_copy = kwargs.copy()
    kwargs_copy.pop("agents_dir", None)  # 移除不屬於服務的參數
    return RedisSessionService(uri=uri, **kwargs_copy)
```

#### 3. 繼承自 BaseSessionService (Inherit from BaseSessionService)

您的自定義服務必須繼承自 `BaseSessionService`：

```python
from google.adk.sessions import BaseSessionService, Session, Event
import redis
import json
import uuid

class RedisSessionService(BaseSessionService):
    """在 Redis 中存儲 ADK 對話。"""

    def __init__(self, uri: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(uri, decode_responses=True)

    async def create_session(self, *, app_name: str, user_id: str,
                           **kwargs):
        """在 Redis 中建立並存儲對話。"""
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, app_name=app_name,
                        user_id=user_id)
        # 存儲到 Redis，24 小時後過期
        self.redis_client.set(f"session:{session_id}",
                            json.dumps(session.dict()),
                            ex=86400)
        return session

    async def get_session(self, *, app_name: str, user_id: str,
                        session_id: str, **kwargs):
        """從 Redis 檢索對話。"""
        data = self.redis_client.get(f"session:{session_id}")
        if not data:
            return None
        return Session(**json.loads(data))

    async def list_sessions(self, *, app_name: str, user_id: str,
                          **kwargs):
        """列出使用者的所有對話。"""
        pattern = f"session:*"
        sessions = []
        for key in self.redis_client.keys(pattern):
            data = self.redis_client.get(key)
            if data:
                session_dict = json.loads(data)
                if (session_dict.get("app_name") == app_name and
                    session_dict.get("user_id") == user_id):
                    sessions.append(Session(**session_dict))
        return {"sessions": sessions, "total_count": len(sessions)}

    async def delete_session(self, *, app_name: str, user_id: str,
                           session_id: str, **kwargs):
        """從 Redis 刪除對話。"""
        self.redis_client.delete(f"session:{session_id}")

    async def append_event(self, session: Session, event):
        """關鍵：將事件和完整的對話保存到 Redis。"""
        # 調用父類別方法將事件新增到 session.events
        event = await super().append_event(session=session, event=event)
        # 重要：在新增事件後將整個對話保存到 Redis
        self.redis_client.set(f"session:{session.id}",
                            json.dumps(session.dict()),
                            ex=86400)
        return event
```

### 使用案例：Redis 對話服務 (Use Case: Redis Session Service)

**場景**：您正在生產環境中執行代理程式，並希望獲得具有自動過期功能的快速、持久對話。

```python
# main.py
from google.adk.cli import cli_tools_click
from google.adk.cli.service_registry import get_service_registry
import redis
import json
import uuid
from google.adk.sessions import BaseSessionService, Session

class RedisSessionService(BaseSessionService):
    """在 Redis 中存儲 ADK 對話。"""

    def __init__(self, uri: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(uri, decode_responses=True)

    async def create_session(self, *, app_name: str, user_id: str,
                           **kwargs):
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, app_name=app_name,
                        user_id=user_id)
        self.redis_client.set(f"session:{session_id}",
                            json.dumps(session.dict()), ex=86400)
        return session

    async def append_event(self, session: Session, event):
        event = await super().append_event(session=session, event=event)
        self.redis_client.set(f"session:{session.id}",
                            json.dumps(session.dict()), ex=86400)
        return event

    async def get_session(self, *, app_name: str, user_id: str,
                        session_id: str, **kwargs):
        data = self.redis_client.get(f"session:{session_id}")
        if not data:
            return None
        return Session(**json.loads(data))

    async def list_sessions(self, *, app_name: str, user_id: str,
                          **kwargs):
        sessions = []
        for key in self.redis_client.keys("session:*"):
            data = self.redis_client.get(key)
            if data:
                s = Session(**json.loads(data))
                if s.app_name == app_name and s.user_id == user_id:
                    sessions.append(s)
        return {"sessions": sessions, "total_count": len(sessions)}

    async def delete_session(self, *, app_name: str, user_id: str,
                           session_id: str, **kwargs):
        self.redis_client.delete(f"session:{session_id}")

# 註冊服務
def redis_factory(uri: str, **kwargs):
    kwargs_copy = kwargs.copy()
    kwargs_copy.pop("agents_dir", None)
    return RedisSessionService(uri=uri, **kwargs_copy)

registry = get_service_registry()
registry.register_session_service("redis", redis_factory)

if __name__ == '__main__':
    cli_tools_click.main()
```

**執行命令：**

```bash
# 預設 Redis (localhost:6379)
python main.py web agents/

# 自定義 Redis 位置
python main.py web agents/ \
  --session_service_uri=redis://redis.prod.example.com:6379

# 結果：所有對話都持久化到 Redis 並具有自動過期功能 ✅
```

**會發生什麼：**

1. 在第一次互動時建立對話
2. 每個事件（使用者訊息、代理程式回應）都會觸發 `append_event()`
3. 完整的對話狀態被保存到 Redis（24 小時 TTL）
4. 對話在頁面刷新、伺服器重啟後依然存在
5. 24 小時後，對話從 Redis 中自動過期

```bash
# 為快速代理程式使用 Redis
adk web agents/ --session_service_uri=redis://localhost:6379

# 為關鍵代理程式使用 PostgreSQL
adk web agents/   --session_service_uri=postgres://user:pass@localhost/adk_db
```

## 配置參考 (Configuration Reference)

```python
registry.register_session_service(
    scheme: str,                    # URI 方案 ("redis", "mongodb" 等)
    factory: Callable[..., Any]     # 工廠函數
)
```

| 參數 (Parameter) | 類型 (Type) | 用途 (Purpose)                            |
| ---------------- | ----------- | ----------------------------------------- |
| `scheme`         | str         | URI 方案識別碼 (例如, "redis")            |
| `factory`        | Callable    | 接收 `(uri: str, **kwargs)` 的函數        |
| `uri`            | str         | 完整 URI (例如, "redis://localhost:6379") |
| `**kwargs`       | dict        | 額外選項 (需移除 `agents_dir`)            |

### 專業提示 (Pro Tips)

💡 **提示 1 - 始終處理 agents_dir**：CLI 會將 `agents_dir` 傳遞給您的工廠，但您的對話服務不需要它。始終從 kwargs 中彈出它：

```python
def my_factory(uri: str, **kwargs):
    kwargs_copy = kwargs.copy()
    kwargs_copy.pop("agents_dir", None)  # ← 這樣做！
    return MySessionService(**kwargs_copy)
```

💡 **提示 2 - URI 解析**：建立一個輔助函數來解析自定義 URI 方案：

```python
from urllib.parse import urlparse

def custom_factory(uri: str, **kwargs):
    parsed = urlparse(uri)
    # parsed.scheme = "myservice"
    # parsed.netloc = "localhost:9999"
    # parsed.path = "/path"

    kwargs_copy = kwargs.copy()
    kwargs_copy.pop("agents_dir", None)
    return CustomService(
        host=parsed.hostname,
        port=parsed.port,
        **kwargs_copy
    )
```

💡 **提示 3 - 在 adk web 中測試**：註冊後，啟動 `adk web` 並檢查 UI。對話應該在瀏覽器頁面重新載入後保持不變：

```bash
# 啟動您的註冊指令碼
python my_setup.py web agents/

# 在瀏覽器中：http://localhost:8000
# 向代理程式發送訊息 → 刷新頁面 → 對話持久存在 ✅
```

💡 **提示 4 - 非同步優先**：始終使 `write()`、`read()`、`delete()` 成為非同步。ADK 期望非同步 I/O：

```python
class MySessionService(BaseSessionStorage):
    async def write(self, session_id: str, data: dict) -> None:
        # 非同步操作：await db.save() 等。
        pass
```

### 何時不應使用它 (When NOT to Use It)

⚠️ **避免使用場景：**

- 簡單開發（使用預設的記憶體中對話）
- 不需要持久化（一次性聊天機器人）
- 單伺服器、單進程部署

⚠️ **考慮替代方案：**

- **預設對話**：適用於本地開發和示範
- **資料庫對話服務**：如果您需要簡單的 SQL 後端
- **快取 + 資料庫混合**：Redis 用於速度，PostgreSQL 用於備份

### 完整的運作實現 (Complete Working Implementation)

此 TIL 包含一個生產就緒的 Redis 對話服務，您可以直接使用：

**啟動範例：**

```bash
cd til_implementation/til_custom_session_services_20251023/

make setup       # 安裝依賴 + Docker
make docker-up   # 啟動 Redis 容器
make dev         # 啟動帶有自定義對話的 Web UI
```

**實現中的關鍵文件：**

- `custom_session_agent/agent.py` - 具有所有 5 個方法的 RedisSessionService
- `custom_session_agent/__main__.py` - 註冊服務的進入點
- `tests/` - 工廠和服務方法的完整測試套件
- `view_sessions.py` - 檢查 Redis 對話資料的工具
- `Makefile` - 簡化的命令（setup, docker-up, dev, test）

**執行測試：**

```bash
cd til_implementation/til_custom_session_services_20251023/
pytest tests/ -v

# 預期輸出：
# test_agent.py::test_agent_config_valid PASSED
# test_imports.py::test_required_env_vars PASSED
# test_tools.py::test_show_service_registry_info PASSED
# ...
# 26 passed ✅
```

### 持久化在實踐中如何運作 (How Persistence Works in Practice)

**使用 Redis 的對話生命週期：**

```text
1. 使用者向代理程式發送訊息
   ↓
2. ADK 建立/加載對話
   ↓
3. 對話服務加載對話資料
   RedisSessionService.get_session() 從 Redis 加載
   ↓
4. 代理程式處理帶有對話上下文的訊息
   ↓
5. 生成回應 + 建立事件
   ↓
6. 對話保存到 Redis
   RedisSessionService.append_event() 保存完整對話
   （這是關鍵方法！）
   ↓
7. 使用者刷新瀏覽器
   ↓
8. 對相同 session_id 的新請求
   ↓
9. 對話服務加載對話
   RedisSessionService.get_session() → 從 Redis 檢索
   資料持久存在！ ✅
   ↓
10. 代理程式具有完整的上下文（對話歷史、狀態） ✅
```

**驗證步驟：**

1. 使用 Redis 對話啟動您的代理程式：

   ```bash
   make setup
   make docker-up
   make dev
   ```

2. 開啟瀏覽器並造訪 `localhost:8000`

3. 向代理程式發送訊息（"您的名字是什麼？"）

4. 直接檢查 Redis：

   ```bash
   # 查看存儲在 Redis 中的所有對話
   cd workspace/python/agents/custom-session-agent/
   python view_sessions.py
   ```

5. 您應該看到帶有對話歷史記錄的對話 ✅

6. 刷新瀏覽器 - 代理程式記住了對話 ✅

### 學習後的後續步驟 (Next Steps After Learning)

1. 📖 **複製模式**：使用 `custom_session_agent/agent.py` 作為您自己服務的模板
2. 🚀 **適配您的後端**：將 Redis 客戶端替換為您的存儲系統
3. 💬 **註冊服務**：在您的 CLI 中使用工廠模式
4. 🔄 **部署**：在生產環境中使用 `adk web --session_service_uri=your_uri`

## 關鍵要點 (Key Takeaway)

**自定義對話服務解鎖了生產等級的 ADK 部署。**

註冊一次自定義後端，即可隨處使用。無論您偏好 Redis 的速度、MongoDB 的文件、PostgreSQL 的 SQL 還是您自己的自定義存儲，ADK 的服務註冊表都能實現無縫整合。

這個模式非常強大：一個工廠函數和一個註冊調用，您的整個 ADK 生態系統（CLI、Web UI、代理程式）就會自動使用您的後端。 ✨

---

## 程式碼實現 (Code Implementation)

- custom-session-agent：[程式碼連結](../../../python/agents/custom-session-agent/)

---

## 參閱 (See Also)

### 相關 TIL (Related TILs)

- **[TIL: 上下文壓縮 (Context Compaction)](../blog/2025-10-19-til-context-compaction.md)** - 優化長對話中的記憶體使用（與持久化對話配合良好！）
- **[TIL: 暫停與恢復調用 (Pause and Resume Invocations)](../blog/2025-10-20-til-pause-resume.md)** - 檢查點代理程式執行狀態
- **[返回 TIL 索引 (/blog/tags/til)](../blog/README.md)** - 瀏覽所有快速學習指南

### 相關 ADK 教學 (Related ADK Tutorials)

- **[教學 01: Hello World 代理程式 (hello_world_agent)](../adk_training/01-hello_world_agent.md)** - 如果您是 ADK 新手，請從這裡開始；自定義對話適用於所有代理程式
- **[教學 08: 狀態與記憶 (state_memory)](../adk_training/08-state_memory.md)** - 了解對話狀態管理和持久化模式
- **[教學 15: 建立多伺服器系統 (live_api_audio)](../adk_training/15-live_api_audio.md)** - 為分散式部署使用自定義持久化對話

### ADK 官方文件 (ADK Official Documentation)

- **BaseSessionService API** - 完整的 API 參考和抽象方法（見 google.adk.sessions 模組）
- **服務註冊表 (Service Registry)** - google.adk.cli.service_registry 中的服務註冊表實現
- **ADK 社群對話 (ADK Community Sessions)** - adk-python-community 中的運作中 Redis 實現

### 相關資源與模式 (Related Resources & Patterns)

- **生產代理程式模式 (Production Agent Patterns)** - 對話持久化對於生產代理程式至關重要
- **自定義對話服務實現 (Custom Session Services Implementation)** - 帶有完整測試套件的運作代碼範例（見 [custom-session-agent](../../../python/agents/custom-session-agent/) 目錄）
