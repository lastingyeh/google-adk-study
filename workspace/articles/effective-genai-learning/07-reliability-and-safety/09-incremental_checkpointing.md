# 增量檢查點架構 (incremental_checkpointing)

在構建長達數小時甚至數天的長工作流（Long-running Workflows）時，架構師最恐懼的場景莫過於任務執行到 99% 時，因為一個暫時性的網路抖動或 API 超時導致整個進程崩潰，迫使系統必須從頭開始。這不僅是運算資源（Token 與算力）的巨大浪費，更會嚴重打擊用戶體驗。**增量檢查點 (Incremental Checkpointing)** 模式的核心在於將「執行進度」與「單一進程生命週期」解耦，確保系統具備在失敗點「原地復甦」的能力。

---

### 情境 1：實施里程碑式狀態持久化以應對階段性失敗

在處理如多階段文檔處理或複雜報表生成的任務時，開發者常習慣寫一個巨大的 `async` 函數跑到底。然而，強健的系統應該在每個關鍵子任務（Sub-task）完成後，立即將中間結果寫入持久化層。

#### 核心概念
將工作流拆分為多個「具備幂等性的階段」。在執行每一階段前，先檢查持久化存儲中是否已存在該階段的輸出成果。如果存在，直接跳過計算進入下一階段。

#### 程式碼範例 (以多階段貸款審核為例)

```python
# ❌ Bad: 缺乏檢查點的線性執行
# 一旦 risk_assessment 失敗，先前耗時的 document_parsing 必須重做
async def process_loan_application(app_id):
    docs = await document_parsing_tool(app_id)  # 耗時 2 分鐘
    credit = await credit_check_tool(app_id)    # 耗時 1 分鐘
    risk = await risk_assessment_tool(docs, credit) # 若此處崩潰，前 3 分鐘前功盡棄
    return risk

# ✅ Better: 實施增量檢查點模式
# 參考 adk-docs.txt: 利用 session.state 管理中間進度
async def process_loan_with_checkpoints(context: InvocationContext):
    state = context.session.state
    app_id = state.get("app_id")

    # 階段 1: 文檔解析
    if "stage1_docs" not in state:
        docs = await document_parsing_tool(app_id)
        state["stage1_docs"] = docs  # 建立檢查點
        await context.save_state()    # 強制持久化

    # 階段 2: 信用檢查
    if "stage2_credit" not in state:
        credit = await credit_check_tool(app_id)
        state["stage2_credit"] = credit
        await context.save_state()

    # 階段 3: 最終評估 (即使重啟也能直接從 state 讀取前兩步結果)
    risk = await risk_assessment_tool(state["stage1_docs"], state["stage2_credit"])
    return risk
```

#### 底層原理探討與權衡
*   **為什麼有效 (Rationale)**：這將系統的「最大損失範圍」從整個工作流縮小到了單個步驟。它確保了系統在面對非決定性錯誤（如資源耗盡或 OOM）時具有防禦性。
*   **權衡 (Trade-off)**：頻繁的 IO 操作（寫入數據庫）會增加「快樂路徑（Happy Path）」的延遲。此外，管理多個版本的中間狀態會增加數據存儲的負擔。
*   **拇指法則 (Rule of thumb)**：僅在**資源密集型（Resource-intensive）**或**高風險（High-risk）**的步驟之後設置檢查點。對於執行時間小於 5 秒的微小步驟，檢查點的 IO 開銷可能大於其價值。

---

### 情境 2：優先使用持久化 `SessionService` 搭配 `ResumabilityConfig` 實現原地復甦

在生產環境中，AI Agent 的運行實例（如 Cloud Run 或 GKE Pod）可能會因為部署新版本或節點維修而隨時被終止。作為架構師，我們不應假設進程是長存的，而應將 Agent 視為「無狀態的執行單元」，並將其「靈魂（狀態）」寄託於持久化層。

#### 核心概念
將狀態從進程記憶體（Ephemeral）抽離至外部持久化存儲（Durable）。Google ADK 透過 `SessionService` 的多態實現（Polymorphism）提供了這種抽象。當啟用 `ResumabilityConfig` 時，ADK 不僅保存 `state`，還會記錄工作流的執行進度，確保重啟後能精確從斷點恢復，而非僅僅載入變數。

#### 程式碼範例

```python
# ❌ Bad: 使用 InMemorySessionService (僅適用於測試)
# 一旦 Pod 重啟，所有 Session 與 State 都會丟失，無法恢復
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

session_service = InMemorySessionService()
runner = Runner(agent=my_agent, session_service=session_service)

# ✅ Better: 配置 DatabaseSessionService 並啟用 Resumability
# 引用來源: adk-docs/sessions&memory/session/index.md & adk-docs/agent-runtime/resume.md
from google.adk.apps import App, ResumabilityConfig
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner

# 1. 使用持久化資料庫後端 (例如 PostgreSQL 或 SQLite)
# 注意：生產環境請確保使用非同步驅動程式 (如 asyncpg)
db_service = DatabaseSessionService(db_url="postgresql://user:pass@host/db")

# 2. 配置 App 啟用可恢復性 (Resumability)
app = App(
    name="loan_processor_app",
    root_agent=loan_agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)

# 3. 透過 Runner 執行
runner = Runner(app=app, session_service=db_service)

# 即使此進程崩潰，新實例只需憑相同的 session_id 即可恢復
# ADK 會自動比對事件歷史，跳過已完成的步驟
async for event in runner.run_async(user_id="u_123", session_id="s_789"):
    print(event.content)
```

#### 底層原理探討與權衡
*   **為什麼有效 (Rationale)**：`DatabaseSessionService` 確保了 `session.state` 的 **Durability (持久性)**。配合 `ResumabilityConfig`，ADK 的 `Runner` 在啟動時會執行「重播（Replay）」或「狀態恢復」邏輯：它會掃描資料庫中的 `events` 歷史，重新建立代理的內部狀態。對於 `SequentialAgent` 或 `LoopAgent`，它能自動定位到最後一個未完成的子代理。
*   **權衡 (Trade-off)**：引入外部資料庫增加了系統的複雜度與維運成本。此外，每次 `append_event` 都會觸發一次資料庫寫入，在高併發場景下需要注意資料庫的 IOPS 瓶頸。
*   **拇指法則 (Rule of Thumb)**：對於任何執行時間超過 30 秒或涉及多步工具呼叫的工作流，**必須** 使用持久化 `SessionService`。對於單次問答（One-off QA），使用 `InMemory` 以換取極致性能。

---

### ADK Session 儲存策略對比

| 特性 | `InMemorySessionService` | `DatabaseSessionService` | `VertexAiSessionService` |
| :--- | :--- | :--- | :--- |
| **持久性** | 無 (重啟即失) | 高 (受控於資料庫) | 極高 (託管服務) |
| **擴展性** | 差 (限於單機) | 中 (受限於 DB 連線) | 極高 (雲端原生) |
| **適用場景** | 本地開發、單機測試 | 企業內部應用、自管環境 | 生產級、大規模 AI 服務 |
| **設定成本** | 零配置 | 需要資料庫與驅動 | 需要 GCP 專案與權限 |

---

### 跨實例恢復時序圖

```mermaid
sequenceDiagram
    participant Instance_A as 舊實例 (Pod A)
    participant DB as 外部資料庫 (State/Events)
    participant Instance_B as 新實例 (Pod B)

    Instance_A->>DB: 執行步驟 1，寫入 Event & State (save_state)
    Note over Instance_A: 💥 進程崩潰 (OOM 或 重啟)

    Instance_B->>DB: get_session(session_id)
    DB-->>Instance_B: 回傳歷史事件與最後狀態

    Note over Instance_B: Runner 發現 Resumability 啟用
    Instance_B->>Instance_B: 重播事件，定位斷點

    Instance_B->>DB: 從步驟 2 繼續執行並寫入結果
    Instance_B-->>User: 完成任務
```

---

### 延伸思考

**1️⃣ 問題一**：如果 Agent 在執行 `DatabaseSessionService.append_event` 寫入資料庫的瞬間崩潰，會造成狀態不一致嗎？

**👆 回答**：這涉及到 **原子性（Atomicity）**。ADK 的持久化服務通常會將「事件附加」與「狀態更新」包裝在同一個資料庫事務（Transaction）中。如果寫入失敗，整個更新會回滾，Agent 重啟後會從「上一個成功寫入的事件」開始。雖然這可能導致某些工具被重複呼叫（At-least-once），但保證了資料庫內狀態的完整性。

---

**2️⃣ 問題二**：`session.state` 的大小有限制嗎？如果存儲過多數據會影響恢復速度嗎？

**👆 回答**：絕對會。`Runner` 在恢復時需要從資料庫讀取並反序列化整個 `state`。如果 state 達到數 MB，IO 延遲與反序列化開銷會顯著增加。**架構師的拇指法則**：State 應保持「瘦身（Lean）」，僅存儲 Metadata、URI 或標記。大文件應存放於 Cloud Storage，State 僅保存其 `gs://` 路徑。

---

**3️⃣ 問題三**：如果我更新了 Agent 的程式碼邏輯（例如修改了步驟順序），舊的 Session 還能恢復嗎？

**👆 回答**：這是一個危險操作。ADK 的恢復機制依賴於「事件歷史與程式碼結構的一致性」。如果結構發生變更，`Runner` 可能無法正確對齊事件。建議在更新邏輯時同時更新 `app_name` 的版本號，或者在 `state` 中記錄 `schema_version`，當版本不匹配時強制 Agent 重新開始（Restarting）而非恢復（Resuming）。
