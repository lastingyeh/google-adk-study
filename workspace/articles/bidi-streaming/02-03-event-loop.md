歡迎來到這份深度技術筆記。我是你們的資深技術導師，今天我們將進入 **ADK 雙向串流 (Bidi-streaming)** 生命週期中最核心、也最精彩的環節：**階段 3：`run_live()` 事件迴圈**。

在傳統的 AI 互動中，對話是「回合制」的；但在階段 3 中，對話演變成了「並行制」。這就像從發送電子郵件轉向即時通話。在這個階段，上游（發送）與下游（接收）任務是同時並進的，這正是實現亞秒級延遲與自然中斷互動的關鍵技術底層。

---

### 📌 階段 3：`run_live()` 學習地圖

1.  **並行任務模型**：理解 `asyncio.gather` 如何實現雙向通訊。
2.  **上游任務 (Upstream)**：解析 `LiveRequestQueue` 的分發機制。
3.  **下游任務 (Downstream)**：解構 `run_live()` 事件產生器的運作邏輯。
4.  **實戰代碼演練**：剖析 FastAPI WebSocket 實作細節。
5.  **核心特性支撐**：插嘴偵測 (Interruption) 與回合切換 (Turn-taking)。

---

### 一、 核心機制：為什麼需要並行 (Concurrent)？

**提問：** 「如果 AI 正在生成長篇回應，使用者突然想糾正它，系統如何即時反應？」

**解析：** 這就是階段 3 的技術價值所在。在 `run_live()` 事件迴圈中，我們不使用「請求-回應」模式，而是建立兩個**獨立但並行**的任務：
*   **上游任務**：負責將使用者的文字、音訊或影像「推入」隊列。
*   **下游任務**：負責「拉取」AI 產出的文字、音訊、逐字稿或工具調用事件。

這代表即使 AI 正在說話（下游活動），上游任務依然可以隨時接收新的輸入並傳送給模型，從而觸發中斷標記。

---

### 二、 邏輯具象化：上游與下游的協同流程

我們可以使用下表來釐清這兩個並行任務的職責邊界：

| 維度 | 上游任務 (Upstream) | 下游任務 (Downstream) |
| :--- | :--- | :--- |
| **資料流向** | WebSocket 客戶端 → `LiveRequestQueue` | `run_live()` → WebSocket 客戶端 |
| **通訊組件** | 使用 `LiveRequestQueue` 的便利方法 | 遍歷 `run_live()` 非同步產生器 |
| **處理內容** | 文字、16kHz PCM 音訊、JPEG 影格、活動訊號 | 文字區塊、24kHz PCM 音訊、逐字稿、工具調用 |
| **關鍵特性** | **非阻塞 (Non-blocking)**，立即返回 | **即時串流 (Real-time)**，無緩衝傳遞 |

---

### 三、 代碼即真理：FastAPI 雙向任務實作

在 ADK 的開發實務中，階段 3 必須在**非同步上下文 (Async Context)** 中運行。以下是來源資料中具備權威性的實作範例，請注意我對並行邏輯的重點標註：

```python
# [導師點評]：這是 Phase 3 的核心。我們啟動兩個協程 (Coroutines) 並使用 gather 合併。
# 這確保了上游與下游能「同時」運作，互不阻塞。

async def upstream_task() -> None:
    """上游：接收 WebSocket 訊息並發送到 LiveRequestQueue。"""
    while True:
        message = await websocket.receive()

        # 處理音訊二進位流 (16kHz PCM)
        if "bytes" in message:
            audio_blob = types.Blob(mime_type="audio/pcm;rate=16000", data=message["bytes"])
            live_request_queue.send_realtime(audio_blob) # [關鍵點]：此方法為非阻塞

        # 處理文字訊息
        elif "text" in message:
            json_message = json.loads(message["text"])
            if json_message.get("type") == "text":
                content = types.Content(parts=[types.Part(text=json_message["text"])])
                live_request_queue.send_content(content) # 發送對話輪次

async def downstream_task() -> None:
    """下游：從 run_live() 接收事件並發送到 WebSocket。"""
    # run_live() 是一個非同步產生器，會持續產出 Event 物件
    async for event in runner.run_live(
        user_id=user_id,
        session_id=session_id,
        live_request_queue=live_request_queue, # 傳入上游建立的隊列
        run_config=run_config,
    ):
        # 將事件序列化為 JSON 並發送給用戶端
        event_json = event.model_dump_json(exclude_none=True, by_alias=True)
        await websocket.send_text(event_json)

# 使用 gather 同時運行任務，任何一方異常都會傳遞並取消另一方
try:
    await asyncio.gather(upstream_task(), downstream_task())
except WebSocketDisconnect:
    logger.debug("用戶端正常斷開連線") #
```

---

### 四、 階段 3 的進階行為處理

在串流互動期間，有幾項特性決定了對話的「類人感」：

#### 1. 處理插嘴偵測 (Interruption)
當上游任務在模型產生回應時發送了新輸入，下游的 `run_live()` 會產生一個帶有 `interrupted=True` 標記的事件。
*   **技術行為**：這會立即排空模型的音訊快取。
*   **開發者義務**：應用程式應立即停止用戶端的所有音訊播放並清除部分文字顯示。

#### 2. 自動工具執行
**關鍵在於**，在階段 3 中，ADK 會自動處理工具編排。
*   當模型在下游產生 `function_call` 事件時，ADK 會**並行執行**該工具，並自動將 `function_response` 發回模型，而無需開發者手動干預。

---

### 五、 知識延伸與收斂

階段 3 是整個雙向串流應用程式的「心臟」。透過 `run_live()` 事件迴圈，ADK 將數個月的底層基礎設施（如 WebSocket 重連、音訊逐字稿生成、VAD 狀態同步）轉化為一個簡潔的 `async for` 語法。

**實戰導向總結：**
*   **必須並行**：請務必使用 `asyncio.gather` 同時啟動上、下游任務，否則無法實現中斷功能。
*   **非阻塞發送**：`LiveRequestQueue.send_realtime()` 等方法是同步設計的，可以直接從非同步代碼中呼叫而不需要 `await`。
*   **資源管理**：階段 3 的結束通常由上游發送 `close()` 訊號或下游遇到錯誤觸發，務必在 `finally` 區塊中確保隊列被關閉，以釋放雲端配額。

#ADKBidiStreaming #RunLiveEventLoop #AsyncioGather #LiveRequestQueue #ConcurrentAI

**延伸思考**：在 `SequentialAgent` 場景中，階段 3 會如何運作？它會在同一個 `run_live()` 迴圈中透明地切換代理程式，而不需要重新初始化會話。