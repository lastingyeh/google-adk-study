# 使用 Google ADK 的 SQLite 會話持久性 (SQLite Session Persistence)

**DatabaseSessionService 的官方實作指南**

## 概述

ADK 提供了內建的 `DatabaseSessionService`，用於使用 SQLite、PostgreSQL、MySQL 或 Cloud Spanner 進行持久化會話儲存。本指南說明如何為生產部署實作基於 SQLite 的會話持久性。

## 為什麼選擇 DatabaseSessionService？

### 與 InMemorySessionService 比較

| 功能 | InMemorySessionService | DatabaseSessionService (SQLite) |
| ---------------- | ----------------------- | ------------------------------- |
| **持久性** | ❌ 重啟後遺失 | ✅ 重啟後仍存在 |
| **多用戶** | ⚠️ 可能但受限 | ✅ 推薦 |
| **並行性** | ❌ 受限 | ✅ 良好 (WAL 模式) |
| **狀態範圍** | ✅ 僅 session | ✅ 全部 (session/user/app/temp) |
| **設定** | ✅ 一行程式碼 | ⚠️ 需要資料庫 URL |
| **生產環境** | ❌ 絕不使用 | ✅ 推薦 |

### 與 ADK 狀態 (user: 前綴) 比較

| 功能 | ADK 狀態 (`user:`) | DatabaseSessionService |
| --------------- | ----------------------- | -------------------------- |
| **持久性** | ✅ 跨會話 | ✅ 永久儲存 |
| **複雜度** | ✅ 簡單的 get/set | ⚠️ DB 架構、連線 |
| **查詢** | ❌ 僅鍵值 (Key-value) | ✅ SQL 查詢、JOINs |
| **可擴展性** | ✅ 適合簡單資料 | ✅ 適合複雜資料 |
| **使用案例** | ✅ 使用者偏好 | ✅ 完整的應用程式資料 |

**建議**：對於簡單的偏好使用 ADK 狀態 (`user:` 前綴)，對於具有多用戶的複雜應用程式使用 `DatabaseSessionService`。

## 快速開始 (5 分鐘)

### 1. 基本設定

```python
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from commerce_agent import root_agent

# 使用 SQLite 建立會話服務
session_service = DatabaseSessionService(
    db_url="sqlite:///./commerce_agent_sessions.db"
)

# 使用會話服務初始化 runner
runner = Runner(
    agent=root_agent,
    app_name="commerce_agent",
    session_service=session_service
)
```

### 2. 建立會話

```python
# 為使用者建立會話
session = await session_service.create_session(
    app_name="commerce_agent",
    user_id="athlete_123",
    session_id="session_001",  # 可選：若未提供則自動產生
    state={
        "user:sport": "running",
        "user:budget": 200,
        "user:experience": "advanced"
    }
)

print(f"Created session: {session.id}")
print(f"State: {session.state}")
```

### 3. 使用持久化會話執行代理人

```python
# 執行代理人 - 會話自動持久化
async for event in runner.run_async(
    user_id="athlete_123",
    session_id="session_001",
    new_message={"role": "user", "parts": [{"text": "I want running shoes"}]}
):
    if event.is_final_response():
        print(event.content)
```

### 4. 驗證持久性

```python
# 重啟應用程式，檢索會話
session_restored = await session_service.get_session(
    app_name="commerce_agent",
    user_id="athlete_123",
    session_id="session_001"
)

# 資料仍然存在！
assert session_restored.state["user:sport"] == "running"
assert len(session_restored.events) > 0  # 對話歷史記錄已保存
```

## DatabaseSessionService API

### 連線字串 (Connection Strings)

```python
# SQLite (本地開發，單一伺服器)
db_url = "sqlite:///./sessions.db"

# PostgreSQL (生產環境，多伺服器)
db_url = "postgresql://user:password@localhost:5432/adk_sessions"

# MySQL (生產環境)
db_url = "mysql://user:password@localhost:3306/adk_sessions"

# Cloud Spanner (Google Cloud 生產環境)
db_url = "spanner:///projects/my-project/instances/my-instance/databases/adk-db"
```

### 核心方法

#### 建立會話 (Create Session)

```python
session = await session_service.create_session(
    app_name: str,              # 必填：代理人應用程式名稱
    user_id: str,               # 必填：使用者識別碼
    session_id: str = None,     # 可選：若未提供則自動產生 UUID
    state: dict = None,         # 可選：初始狀態
    **kwargs
) -> Session
```

#### 取得會話 (Get Session)

```python
session = await session_service.get_session(
    app_name: str,
    user_id: str,
    session_id: str,
    **kwargs
) -> Session | None
```

#### 列出會話 (List Sessions)

```python
sessions = await session_service.list_sessions(
    app_name: str,
    user_id: str,
    **kwargs
) -> dict[str, Any]  # 回傳 {"sessions": [...], "total_count": N}
```

#### 刪除會話 (Delete Session)

```python
await session_service.delete_session(
    app_name: str,
    user_id: str,
    session_id: str,
    **kwargs
)
```

#### 附加事件 (Append Event) (內部 - 自動)

```python
# 當代理人處理訊息時由 Runner 自動呼叫
event = await session_service.append_event(
    session: Session,
    event: Event
) -> Event
```

## 會話模型結構 (Session Model Structure)

```python
from google.adk.sessions import Session, Event

# Session 物件
session = Session(
    id="uuid-string",                    # 唯一會話 ID
    app_name="commerce_agent",          # 代理人應用程式名稱
    user_id="athlete_123",              # 使用者識別碼
    state={                              # 會話狀態 (持久化)
        "user:sport": "running",        # 使用者範圍 (跨會話)
        "session:cart": [...],          # 會話範圍 (本次對話)
        "app:config": {...},            # 應用程式範圍 (全域)
        "temp:cache": {...}             # 臨時 (不持久化)
    },
    events=[                             # 對話歷史記錄
        Event(id="...", timestamp=..., author="user", ...),
        Event(id="...", timestamp=..., author="agent", ...)
    ],
    last_update_time=1761575199.519     # Unix 時間戳記
)
```

## 狀態持久化流程

### 狀態更新如何儲存

```mermaid
sequenceDiagram
    participant User as 使用者
    participant Agent as 代理人
    participant Tool as 工具
    participant Runner as Runner
    participant DB as SQLite 資料庫

    User->>Agent: 發送訊息 "I want running shoes"
    Agent->>Tool: 呼叫 save_preferences
    Tool->>Runner: 修改 tool_context.state
    Note over Runner: 捕捉狀態差異 (State Delta)
    Runner->>DB: 透過 Session Service 儲存
    DB-->>Runner: 更新 session.state
    Runner-->>Agent: 繼續執行
```

```python
# 步驟 1：使用者發送訊息
new_message = {"role": "user", "parts": [{"text": "I want running shoes"}]}

# 步驟 2：代理人處理並透過工具修改狀態
def save_preferences(sport: str, tool_context: ToolContext):
    tool_context.state["user:sport"] = sport  # 狀態修改被追蹤
    return {"status": "success"}

# 步驟 3：Runner 捕捉狀態差異 (state delta)
# EventActions.state_delta = {"user:sport": "running"}

# 步驟 4：會話服務將差異合併到 session.state
await session_service.append_event(session, event)
# → 使用差異更新 session.state
# → 寫入 SQLite 資料庫
# → 更新 last_update_time

# 步驟 5：下一次調用讀取持久化狀態
session = await session_service.get_session(...)
# session.state["user:sport"] == "running" ✅
```

### 關鍵模式

```python
# ✅ 正確 - 狀態會持久化
def my_tool(value: str, tool_context: ToolContext):
    tool_context.state["key"] = value  # 在 state_delta 中捕捉 → 持久化
    return {"status": "success"}

# ❌ 錯誤 - 狀態不會持久化
session = await session_service.get_session(...)
session.state["key"] = value  # 直接修改繞過了事件系統
# 未持久化！請改用 tool_context.state
```

## 生產範例：商務代理人

### 檔案結構

```
commerce-agent-e2e/
├── commerce_agent/
│   ├── agent.py           # 代理人定義
│   └── tools/
│       └── preferences.py # 修改狀態的工具
├── runner.py              # 使用 DatabaseSessionService 設定 Runner
└── sessions.db            # SQLite 資料庫 (自動建立)
```

### runner.py

```python
import asyncio
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from commerce_agent import root_agent

async def main():
    # 初始化會話服務
    session_service = DatabaseSessionService(
        db_url="sqlite:///./commerce_agent_sessions.db"
    )

    # 建立 runner
    runner = Runner(
        agent=root_agent,
        app_name="commerce_agent",
        session_service=session_service
    )

    # 建立或取得會話
    user_id = "athlete_123"
    session = await session_service.create_session(
        app_name="commerce_agent",
        user_id=user_id
    )

    print(f"Session ID: {session.id}")

    # 執行代理人
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message={
            "role": "user",
            "parts": [{"text": "I want running shoes under €150"}]
        }
    ):
        if event.is_final_response():
            print(f"Agent: {event.content}")

    # 驗證持久性
    restored_session = await session_service.get_session(
        app_name="commerce_agent",
        user_id=user_id,
        session_id=session.id
    )

    print(f"State persisted: {restored_session.state}")
    print(f"Events count: {len(restored_session.events)}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 具備狀態持久性的工具

```python
from google.adk.tools import ToolContext
from typing import Dict, Any

def save_preferences(
    sport: str,
    budget_max: int,
    experience_level: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """將使用者偏好儲存至持久狀態。"""
    try:
        # 修改狀態 - 透過 DatabaseSessionService 自動持久化
        tool_context.state["user:sport"] = sport
        tool_context.state["user:budget"] = budget_max
        tool_context.state["user:experience"] = experience_level

        return {
            "status": "success",
            "report": f"✓ Saved: {sport}, max €{budget_max}, {experience_level}"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_preferences(tool_context: ToolContext) -> Dict[str, Any]:
    """從持久狀態檢索已儲存的偏好。"""
    try:
        state = tool_context.state

        prefs = {
            "sport": state.get("user:sport"),
            "budget_max": state.get("user:budget"),
            "experience_level": state.get("user:experience")
        }

        # 過濾 None 值
        prefs = {k: v for k, v in prefs.items() if v is not None}

        return {
            "status": "success",
            "data": prefs,
            "report": f"Retrieved: {', '.join(f'{k}={v}' for k, v in prefs.items())}"
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "data": {}}
```

## 與 adk web 一起使用

### 基本用法

```bash
# 使用預設的 InMemorySessionService 啟動 ADK web (開發用)
adk web

# 重啟後會話遺失 ❌
```

### 使用 DatabaseSessionService (SQLite 持久性)

**✅ 官方支援：** `adk web` 支援 `--session_service_uri` 旗標用於 SQLite！

```bash
# 目前目錄中的 SQLite
adk web --session_service_uri sqlite:///./sessions.db

# 使用絕對路徑的 SQLite
adk web --session_service_uri sqlite:////absolute/path/to/sessions.db

# 使用 WAL 模式的 SQLite (推薦用於生產環境)
adk web --session_service_uri "sqlite:///./sessions.db?mode=wal"

# 會話在重啟後仍然存在！ ✅
```

**其他資料庫選項：**

```bash
# PostgreSQL (推薦用於生產環境)
adk web --session_service_uri postgresql://user:password@localhost/adk_sessions

# MySQL
adk web --session_service_uri mysql://user:password@localhost/adk_sessions

# Cloud Spanner (Google Cloud)
adk web --session_service_uri spanner:///projects/my-project/instances/my-instance/databases/adk-db

# Agent Engine sessions (Google Cloud)
adk web --session_service_uri agentengine://<agent_engine_resource_id>
```

**包含所有選項的完整範例：**

```bash
adk web \
  --port 8000 \
  --host 0.0.0.0 \
  --session_service_uri "sqlite:///./sessions.db?mode=wal" \
  --artifact_service_uri gs://my-artifacts-bucket \
  --log_level INFO \
  --reload_agents
```

**參考：** [ADK CLI 文件](https://google.github.io/adk-docs/api-reference/cli/cli.html#web)

### 進階：自定義進入點腳本 (用於自定義會話服務)

如果您需要 **自定義會話服務** (Redis, MongoDB 等)，請使用此模式：

```python
# entry_point.py
from google.adk.cli import cli_tools_click
from google.adk.cli.service_registry import get_service_registry
from google.adk.sessions import DatabaseSessionService

# 註冊 DatabaseSessionService 為預設
def db_session_factory(uri: str = None, **kwargs):
    db_url = uri or "sqlite:///./adk_sessions.db"
    return DatabaseSessionService(db_url=db_url)

registry = get_service_registry()
registry.register_session_service("sqlite", db_session_factory)

if __name__ == '__main__':
    cli_tools_click.main()
```

```bash
# 使用自定義進入點執行
python entry_point.py web --session_service_uri=sqlite:///./sessions.db
```

#### 選項 2：自定義會話服務 (進階)

請參閱 `til_implementation/til_custom_session_services_20251023/` 以獲取完整實作。

## 多用戶支援

### 使用者隔離

```python
# Alice 的會話
alice_session = await session_service.create_session(
    app_name="commerce_agent",
    user_id="alice@example.com",
    state={"user:sport": "running"}
)

# Bob 的會話
bob_session = await session_service.create_session(
    app_name="commerce_agent",
    user_id="bob@example.com",
    state={"user:sport": "cycling"}
)

# 完全隔離 - Alice 和 Bob 擁有分開的狀態
alice_prefs = await session_service.get_session(..., user_id="alice@example.com", ...)
bob_prefs = await session_service.get_session(..., user_id="bob@example.com", ...)

assert alice_prefs.state["user:sport"] == "running"
assert bob_prefs.state["user:sport"] == "cycling"
```

### 列出使用者的所有會話

```python
# 取得 Alice 的所有會話
alice_sessions = await session_service.list_sessions(
    app_name="commerce_agent",
    user_id="alice@example.com"
)

print(f"Alice has {alice_sessions['total_count']} sessions")
for session in alice_sessions['sessions']:
    print(f"  - {session.id}: {session.state}")
```

## 資料庫架構

ADK 會自動建立以下資料表：

```sql
-- 會話資料表 (由 DatabaseSessionService 建立)
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,           -- 會話 UUID
    app_name TEXT NOT NULL,        -- 代理人應用程式名稱
    user_id TEXT NOT NULL,         -- 使用者識別碼
    state TEXT NOT NULL,           -- JSON 編碼的狀態 dict
    events TEXT NOT NULL,          -- JSON 編碼的事件列表
    last_update_time REAL NOT NULL -- Unix 時間戳記
);

-- 用於高效查詢的索引
CREATE INDEX idx_sessions_user ON sessions(app_name, user_id);
CREATE INDEX idx_sessions_app ON sessions(app_name);
```

## 效能考量

### SQLite WAL 模式 (推薦)

```python
# 啟用 Write-Ahead Logging 以獲得更好的並行性
db_url = "sqlite:///./sessions.db?mode=wal"

session_service = DatabaseSessionService(db_url=db_url)
```

**優點：**

- 多個讀取者不會阻塞寫入者
- 在並行負載下有更好的效能
- 更適合生產環境使用

### 連線池 (PostgreSQL/MySQL)

```python
# 具有連線池的 PostgreSQL
db_url = "postgresql://user:pass@localhost/adk?pool_size=10&max_overflow=20"

session_service = DatabaseSessionService(db_url=db_url)
```

## 故障排除

### 問題："Session not found" (找不到會話)

```python
# ❌ 錯誤 - 會話從未建立
runner.run_async(user_id="user123", session_id="session456", ...)
# 錯誤：Session not found

# ✅ 正確 - 先建立會話
session = await session_service.create_session(
    app_name="commerce_agent",
    user_id="user123"
)
runner.run_async(user_id="user123", session_id=session.id, ...)
```

### 問題："State not persisting" (狀態未持久化)

```python
# ❌ 錯誤 - 直接修改會話
session = await session_service.get_session(...)
session.state["key"] = "value"  # 未持久化！

# ✅ 正確 - 透過 tool_context 修改
def my_tool(value: str, tool_context: ToolContext):
    tool_context.state["key"] = value  # 透過 state_delta 持久化
    return {"status": "success"}
```

### 問題："Database locked" (資料庫被鎖定 - SQLite)

```python
# 解決方案 1：使用 WAL 模式
db_url = "sqlite:///./sessions.db?mode=wal"

# 解決方案 2：增加逾時時間
db_url = "sqlite:///./sessions.db?timeout=30.0"

# 解決方案 3：使用 PostgreSQL 進行高並行
db_url = "postgresql://user:pass@localhost/adk"
```

## 從 InMemorySessionService 遷移

```python
# 之前：記憶體內會話 (重啟後遺失)
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()

# 之後：使用 SQLite 的持久化會話
from google.adk.sessions import DatabaseSessionService

session_service = DatabaseSessionService(
    db_url="sqlite:///./sessions.db?mode=wal"
)

# 不需要更改其他程式碼！ ✅
```

## 最佳實踐

1. **使用 WAL 模式**：在生產環境中的 SQLite。
2. **使用者隔離**：始終使用唯一的 `user_id`。
3. **狀態範圍**：使用適當的前綴 (user:, session:, app:, temp:)。
4. **錯誤處理**：始終將會話操作包裝在 try/except 中。
5. **清理**：定期刪除舊會話以節省磁碟空間。
6. **備份**：定期備份 SQLite 資料庫檔案。
7. **測試**：使用分開的測試資料庫 (`:memory:` 或暫存檔)。

## 參考資料

- **ADK 文件**：https://google.github.io/adk-docs/sessions/
- **TIL：自定義會話服務**：`docs/til/til_custom_session_services_20251023.md`
- **工作範例**：`til_implementation/til_custom_session_services_20251023/`
- **教學 35**：使用 DatabaseSessionService 的商務代理人 E2E
- **官方範例**：`research/adk-samples/python/agents/`

## 下一步

1. **在您的代理人中實作**：替換 `InMemorySessionService`。
2. **測試持久性**：重啟應用程式並驗證狀態是否存活。
3. **監控效能**：檢查資料庫大小和查詢時間。
4. **考慮 PostgreSQL**：用於多伺服器生產部署。
5. **實作清理**：定期刪除舊會話。

---

**建立日期**：2025-01-27
**ADK 版本**：1.17+
**狀態**：已準備好用於生產環境 (Production-ready)

---
# 重點摘要

- **核心概念**：
    - **DatabaseSessionService**：ADK 提供的持久化會話服務。
    - **狀態持久性**：確保對話狀態在應用程式重啟後不會遺失。
    - **Write-Ahead Logging (WAL)**：SQLite 的一種模式，提高並行效能。

- **關鍵技術**：
    - **SQLite/PostgreSQL**：支援的後端資料庫。
    - **ADK Runner**：整合會話服務以自動處理狀態更新。
    - **State Delta**：Runner 捕捉狀態變更並將其寫入資料庫的機制。

- **重要結論**：
    - 在生產環境中，`DatabaseSessionService` 優於 `InMemorySessionService`。
    - 必須透過 `tool_context` 修改狀態，直接修改 `session.state` 不會被持久化。
    - `adk web` 支援 SQLite 持久化，需使用 `--session_service_uri` 參數。

- **行動項目**：
    - 將現有的 `InMemorySessionService` 遷移至 `DatabaseSessionService`。
    - 在 SQLite 連線字串中啟用 WAL 模式 (`?mode=wal`)。
    - 實作使用者隔離，為每個使用者分配唯一的 ID。
