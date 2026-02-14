# Agent Memory Systems: Short-term Conversation & Long-term Knowledge Storage (agent_memory_systems)

作為一名軟體架構師，在設計 Agent 系統時，最常見的誤區之一就是混淆了「短期對話狀態」與「長期知識記憶」。這不僅會導致 Context Window 爆炸，還會讓 Agent 在長期運行後變得越來越「健忘」或反應遲鈍。

本章節將深入探討 Google ADK 中的記憶系統設計，教你如何正確區分 `Session` 與 `MemoryService`，並掌握狀態管理的最佳實務。

### 情境 1：區分短期狀態與長期記憶 (distinguish_memory_scope)

#### 核心概念簡述

Agent 的記憶系統可以類比為人類的記憶模型：
*   **短期記憶 (`Session` / `State`)**：就像工作記憶（Working Memory），用於處理當前對話、追蹤任務進度。它受限於 LLM 的 Context Window 大小。
*   **長期記憶 (`MemoryService`)**：就像長期記憶（Long-Term Memory）或圖書館，用於儲存歷史對話、使用者偏好、事實知識。它必須是「可搜尋的」，Agent 需要時才去檢索。

**拇指法則**：
*   如果資訊僅對「當前對話」有用（例如：使用者的訂房日期），存入 `Session State`。
*   如果資訊對「未來對話」也有用（例如：使用者的飲食偏好），存入 `MemoryService`。

#### 程式碼範例

```python
# ❌ Bad: 將所有歷史塞入 Session
# 試圖將所有過去的對話記錄都保留在 `Session` 中，會迅速耗盡 Token 配額，導致 LLM 遺忘最早的指令，甚至崩潰。

# ❌ Bad: 試圖在單一 Session 中無限累積歷史
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
# 假設這是一個已經運行了很久的 session_id
session_id = "long_running_session"

# 每次新對話都繼續使用同一個 session，導致 events 列表無限增長
# 最終會超出 LLM 的 Context Window
async def chat(user_input):
    runner = Runner(..., session_service=session_service)
    # 錯誤：沒有機制將舊對話歸檔到長期記憶
    await runner.run_async(session_id=session_id, new_message=user_input)

# ✅ Better: 使用 MemoryService 歸檔與檢索

# 正確的做法是定期將完成的 `Session` 歸檔到 `MemoryService`，並在新的 `Session` 中按需檢索。

# ✅ Better: 分離短期與長期記憶
mport asyncio
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.memory import InMemoryMemoryService # 匯入 MemoryService
from google.adk.runners import Runner
from google.adk.tools import load_memory # 用於查詢記憶的工具
from google.genai.types import Content, Part

# --- 常數 ---
APP_NAME = "memory_example_app"
USER_ID = "mem_user"
MODEL = "gemini-2.0-flash" # 使用有效的模型

# --- 代理定義 ---
# 代理 1：擷取資訊的簡單代理
info_capture_agent = LlmAgent(
    model=MODEL,
    name="InfoCaptureAgent",
    instruction="確認使用者的陳述。",
)

# 代理 2：可以使用記憶的代理
memory_recall_agent = LlmAgent(
    model=MODEL,
    name="MemoryRecallAgent",
    instruction="回答使用者的問題。如果答案可能在過去的對話中，請使用 'load_memory' 工具。",
    tools=[load_memory] # 提供工具給代理
)

# --- 服務 ---
# 服務必須在運行器之間共享，以共享狀態和記憶
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService() # 示範使用記憶體內儲存

async def run_scenario():
    # --- 場景 ---

    # 第 1 輪：在會話中擷取一些資訊
    print("--- 第 1 輪：擷取資訊 ---")
    runner1 = Runner(
        # 從資訊擷取代理開始
        agent=info_capture_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service # 提供記憶服務給 Runner
    )
    session1_id = "session_info"
    await runner1.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
    user_input1 = Content(parts=[Part(text="我最喜歡的專案是 Project Alpha。")], role="user")

    # 執行代理
    final_response_text = "(無最終回應)"
    async for event in runner1.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text = event.content.parts[0].text
    print(f"代理 1 回應: {final_response_text}")

    # 取得已完成的會話
    completed_session1 = await runner1.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

    # 將此會話的內容添加到記憶服務中
    print("\n--- 正在將會話 1 添加到記憶中 ---")
    await memory_service.add_session_to_memory(completed_session1)
    print("會話已添加到記憶中。")

    # 第 2 輪：在新的會話中回想資訊
    print("\n--- 第 2 輪：回想資訊 ---")
    runner2 = Runner(
        # 使用第二個代理，它擁有記憶工具
        agent=memory_recall_agent,
        app_name=APP_NAME,
        session_service=session_service, # 重複使用相同的服務
        memory_service=memory_service   # 重複使用相同的服務
    )
    session2_id = "session_recall"
    await runner2.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)
    user_input2 = Content(parts=[Part(text="我最喜歡的專案是什麼？")], role="user")

    # 執行第二個代理
    final_response_text_2 = "(無最終回應)"
    async for event in runner2.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text_2 = event.content.parts[0].text
    print(f"代理 2 回應: {final_response_text_2}")

# 要執行此範例，您可以使用以下程式碼片段：
# asyncio.run(run_scenario())

# await run_scenario()
```

### 3️⃣ 底層原理與權衡

*   **Context Window 限制**：LLM 的注意力機制（Attention Mechanism）隨著 Context 長度增加，計算成本呈二次方增長，且準確率可能下降（Lost in the Middle 現象）。將歷史轉移到 `MemoryService` 是以「檢索延遲」換取「推理效率」與「準確性」。
*   **語義搜尋 vs. 關鍵字**：`InMemoryMemoryService` 僅支援簡單關鍵字匹配，適合開發測試。生產環境建議使用 `VertexAiMemoryBankService`，它利用 Embedding 進行向量語義搜尋，能理解「我喜歡的食物」與「壽司」的關聯。

---

### 情境 2：善用前綴管理狀態範圍 (use_state_prefixes)

#### 核心概念簡述

`session.state` 是一個鍵值對集合（Key-Value Map）。為了避免變數名稱衝突並控制資料的生命週期，ADK 引入了「前綴命名空間」機制。

**拇指法則**：
*   **`temp:`**：僅在當前 Agent 呼叫（Invocation）內有效。用完即丟。
*   **無前綴**：僅在當前 `Session` 內有效。
*   **`user:`**：跟隨使用者 ID，跨 Session 共享（需配合持久化服務）。
*   **`app:`**：全域應用程式設定，所有使用者共享。

#### 程式碼範例

```python
# ❌ Bad: 濫用全域命名
# 變數作用域不明，容易導致資料汙染
def my_tool(context):
    # 這到底是只用一次的變數，還是要存很久的？
    context.state["count"] = 1
    # 這應該是使用者偏好，但沒加前綴，換個 Session 就沒了
    context.state["language"] = "en"

# ✅ Better: 明確的範圍定義
# 使用前綴精確控制生命週期
def my_tool(context):
    # 1. 臨時變數：僅在本次推理鏈中使用 (例如 API 呼叫的中間結果)
    context.state["temp:api_retry_count"] = 0

    # 2. Session 變數：當前對話中有效 (例如訂單編號)
    context.state["current_order_id"] = "ORD-999"

    # 3. User 變數：跟隨使用者，跨 Session 持久化 (例如語言偏好)
    # 需使用支援持久化的 SessionService (如 Database/VertexAI)
    context.state["user:preferred_language"] = "zh-TW"
```

#### 底層原理與權衡

*   **序列化要求**：所有存入 State 的值必須是**可序列化（Serializable）**的基本型別（str, int, bool, list, dict）。切勿存入複雜物件（如 DB Connection, File Handle），因為 State 會被儲存到資料庫或 Redis 中。
*   **隔離性**：使用 `user:` 前綴可以實現簡單的「使用者畫像（User Profile）」管理，而無需額外建立使用者資料庫表。但若資料量過大，仍建議使用專門的資料庫。

---

### 情境 3：透過事件驅動更新狀態 (update_state_via_events)

#### 核心概念簡述

在 ADK 中，`Session` 物件的狀態更新應該是**事件驅動（Event-Driven）**的。這意味著你應該透過「發送事件」或使用 `Context` 來更新狀態，而不是直接修改 `Session` 物件的屬性。

**拇指法則**：
*   在 Tool 或 Callback 中：總是使用 `context.state`。
*   在外部系統整合時：使用 `append_event` 加上 `state_delta`。
*   **永遠不要**在 Context 之外直接 `session.state['key'] = value`。

#### 程式碼範例

```python
# ❌ Bad: 直接修改 Session 物件
# 這種方式繞過了 ADK 的事件追蹤系統，導致狀態變更不會被記錄，持久化層（Database）也不會知道資料變了，造成資料不一致。
# 直接修改 Session 物件，不會觸發持久化
session = await session_service.get_session(...)
session.state["status"] = "active" # 錯誤！這只是改了記憶體裡的物件
# 下次讀取 session 時，"status" 還是舊的值


# ✅ Better: 使用 Context 或 Append Event
# (場景 A): 在 Tool/Callback 內部
def my_tool(context: ToolContext):
    # 框架會自動追蹤此變更，並將其包裝為 Event
    context.state["status"] = "active"

# ✅ Better (場景 B): 在外部系統 (如 Webhook 接收端)
from google.adk.events import Event, EventActions
import time

async def external_update(session_id):
    session = await session_service.get_session(..., session_id=session_id)

    # 建立一個帶有 state_delta 的事件
    event = Event(
        invocation_id="webhook_update",
        author="system",
        actions=EventActions(state_delta={"status": "active"}), # 明確指定變更
        timestamp=time.time()
    )

    # 透過 append_event 寫入，保證持久化與一致性
    await session_service.append_event(session, event)
```

#### 底層原理與權衡

*   **Event Sourcing**：ADK 採用類似 Event Sourcing 的模式。狀態的最終結果是由一系列 Event 推導出來的（或者至少是透過 Event 觸發快照更新）。直接修改物件破壞了這個鏈條。
*   **並發安全性**：透過 `append_event`，底層的 `SessionService` 可以處理併發寫入問題（雖然目前多數實作是 Last-Write-Wins，但介面保留了鎖定或合併的可能性）。

---

### 📊 總結與比較

| 特性 | Session State | MemoryService |
| :--- | :--- | :--- |
| **用途** | 當前對話上下文、任務進度 | 歷史歸檔、長期知識、使用者畫像 |
| **存取速度** | 極快 (In-Memory / Cache) | 較慢 (需搜尋 / 網路請求) |
| **容量限制** | 受限於 LLM Context Window | 理論上無限 (取決於儲存後端) |
| **檢索方式** | 直接存取 (Key-Value) | 語義搜尋 (Semantic Search) 或 關鍵字 |
| **生命週期** | 短期 (Session/User Scope) | 永久 |

### 延伸思考

**1️⃣ 問題一**：我應該把 RAG (Retrieval-Augmented Generation) 的文件放在哪裡？`MemoryService` 嗎？

**👆 回答**：
這取決於文件的性質。
*   如果是**靜態的企業知識庫**（如 HR 手冊），通常建議使用專門的 Vector DB 或 Search Engine，並透過一個標準的 `Tool` (如 `search_knowledge_base`) 讓 Agent 存取。
*   如果是**動態生成的對話記憶**（如「使用者上次說他喜歡紅色」），則非常適合放入 `MemoryService`。
*   `VertexAiMemoryBankService` 其實模糊了這兩者的界線，它既可以存對話，也可以當作輕量級的知識庫使用。

**2️⃣ 問題二**：如何決定何時將 Session 歸檔到 Memory？

**👆 回答**：
常見策略有：
1.  **時間驅動**：Session 閒置超過一定時間（如 30 分鐘）。
2.  **任務驅動**：當一個明確的任務完成時（如「訂單已確認」）。
3.  **長度驅動**：當 `session.events` 數量超過閾值時，觸發摘要（Summarization）並歸檔，然後清空當前 Events 但保留 State。

---
