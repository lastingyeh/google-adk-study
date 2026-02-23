# 資料庫連線管理與併發優化

在建構生產級的生成式 AI 應用（如基於 Google ADK 的聊天機器人）時，資料庫通常用於儲存對話歷史（Session History）與使用者狀態（State）。在高併發情境下，若不正確管理資料庫連線，系統會迅速因耗盡連線數而崩潰。資深架構師的準則是：**連線是昂貴且有限的資源，必須透過「連線池（Pooling）」進行池化與重用。**

---

### 情境 1：優先使用「連線池」而非「單次連線」

**核心概念**：
建立資料庫 TCP 連線需要經過握手（Handshake）與身分驗證，這是一項沉重的開銷。在高併發下，為每個請求開啟新連線會導致作業系統的檔案描述符（File Descriptors）耗盡。連線池預先建立一組連線並緩存，讓請求「借用」並「歸還」，極大化資源利用率。

**程式碼範例**：

```python
# ❌ Bad: 在每個請求中手動 connect/close，在高併發下會拋出 "Too many connections"
async def log_event_bad(event_data):
    # 每次呼叫都重新建立連線，效能極差且易失敗
    conn = await asyncpg.connect(user='user', password='password', database='adk_db')
    try:
        await conn.execute("INSERT INTO events(data) VALUES($1)", event_data)
    finally:
        await conn.close()

# ✅ Better: 使用 `asyncpg.create_pool` 維護長連線池**
# 在應用程式啟動時初始化連線池 (例如 FastAPI lifespan)
pool = await asyncpg.create_pool(
    dsn='postgresql://user:password@localhost/adk_db',
    min_size=10, # 最小保持連線數
    max_size=50  # 最大併發連線上限
)

async def log_event_better(event_data):
    # 從連線池中「獲取」而非「建立」連線
    async with pool.acquire() as conn: # 自動處理歸還
        await conn.execute("INSERT INTO events(data) VALUES($1)", event_data)
```

**底層原理探討與權衡**：
*   **獲取機制（Acquisition）**：當連線池達到 `max_size` 且所有連線都在使用中時，下一個請求會掛起並等待連線釋放。這提供了一種天然的「背壓（Backpressure）」機制，保護資料庫不被壓垮。
*   **權衡**：連線池過大會增加資料庫端的記憶體壓力；過小則會增加應用端的等待延遲。建議根據資料庫硬體進行基準測試以找到「金髮姑娘（Goldilocks）」平衡點。

---

### 情境 2：在 Google ADK 中實作持久化 `SessionService`

**核心概念**：
預設的 `InMemorySessionService` 在重啟後會遺失所有對話。在生產環境中，必須切換至 `DatabaseSessionService` 或 `VertexAiSessionService`。這要求開發者正確配置非同步驅動（如 `sqlite+aiosqlite` 或 `postgresql`），以確保 Agent 在存取對話歷史時不會阻塞事件循環。

**程式碼範例**：

```python
# ✅ Better: 在 ADK 中整合具備連線池能力的資料庫服務
from google.adk.sessions import DatabaseSessionService

# 使用異步驅動程式網址以發揮最高效能
# 對於生產級 Postgres 建議搭配外部 Pooler 如 PgBouncer
db_url = "postgresql+asyncpg://user:pass@localhost/adk_sessions"
session_service = DatabaseSessionService(db_url=db_url)

# ADK Runner 會自動透過連線池存取 session.state 與 events
runner = Runner(
    agent=root_agent,
    session_service=session_service
)
```

---

### 情境 3：使用「訊號量 (Semaphore)」精確限制脆弱 API 的併發

**核心概念**：
有時資料庫或外部 API（例如某些向量資料庫的免費層級）限制非常嚴格，即使連線池也可能因瞬間併發過高而觸發 429 錯誤。這時應使用 `asyncio.Semaphore` 來控制「進入執行狀態」的協程數量，而非僅僅是「連線」數量。

**程式碼範例**：

```python
# ✅ Better: 使用 Semaphore 保護低併發限制的資源
import asyncio

# 限制全域僅能有 5 個協程同時對資料庫進行寫入
db_semaphore = asyncio.Semaphore(5)

async def restricted_db_op(data):
    async with db_semaphore: # 若已滿，此處會暫停協程執行
        async with pool.acquire() as conn:
            await conn.execute("UPDATE state SET val = $1", data)
```

---

### 併發優化技術對比表

| 技術項目                      | 解決的問題                         | 適用場景                                  |
| :---------------------------- | :--------------------------------- | :---------------------------------------- |
| **連線池 (Pooling)**          | 減少建立 TCP 連線的延遲與 CPU 消耗 | 所有資料庫互動、HTTP 會話 (ClientSession) |
| **非同步驅動 (Async Driver)** | 防止單一查詢阻塞整個事件循環       | 所有的 I/O 密集型 GenAI 應用              |
| **訊號量 (Semaphore)**        | 防止下游資源因併發瞬間爆量而崩潰   | 脆弱的舊系統、具備硬性頻率限制的外部 API  |
| **分組/分區 (Partitioning)**  | 解決大規模數據處理的鎖競爭問題     | 大規模 RAG 索引建構、批量數據遷移         |

#### 資料庫連線池生命週期
```mermaid
sequenceDiagram
    participant App as 應用服務 (ADK Runner)
    participant Pool as 連線池 (Pool)
    participant DB as 數據庫 Server

    Note over Pool,DB: 啟動時建立 min_size 條長連線
    App->>Pool: acquire()
    alt 連線池有空閒
        Pool-->>App: 回傳現有連線
    else 連線池已滿 (max_size)
        Pool-->>App: 協程掛起等待 (Wait)
    end
    App->>DB: 執行 SQL (session.state update)
    DB-->>App: 回傳結果
    App->>Pool: release() (透過 async with 自動完成)
    Note over Pool: 連線重置後放回可用隊列
```

---

### 延伸思考

**1️⃣ 問題一**：在微服務架構中，如果多個 ADK 執行個體同時存取同一個資料庫，連線池應該如何設定？

**👆 回答**：這是一個常見的陷阱。如果每個實例設定 `max_size=50`，且有 10 個實例，總連線數將達 500。資料庫端必須支援此數量的連線。來源建議在此種架構下，考慮在資料庫前端部署 **PgBouncer (Postgres)** 或使用 **AlloyDB / Spanner** 等具備高併發管理能力的託管服務。

---

**2️⃣ 問題二**：ADK 的 `temp:` 狀態與持久化資料庫狀態有何不同？

**👆 回答**：`temp:` 前綴的狀態僅存在於 **當次呼叫（Invocation** 中，隨後會被捨棄。這類數據不應寫入資料庫，以減少 I/O 開銷。只有 `user:`、`app:` 或無前綴的 session state 才需要透過 `DatabaseSessionService` 進行昂貴的資料庫寫入操作。

---

**3️⃣ 問題三**：如果資料庫查詢非常慢，會影響 AI 模型的生成速度嗎？

**👆 回答**：會的。在 ADK 的事件循環中，Agent 在執行工具（如存取 RAG 資料庫）時會暫停生成。如果資料庫查詢因併發過高而變慢，將直接拉長**首字時間 (TTFT)**。使用索引優化（如 `HNSW` 向量索引）與連線池是維持即時互動體驗的基礎。