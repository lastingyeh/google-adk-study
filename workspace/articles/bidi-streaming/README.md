# Bidi-streaming 技術深度筆記

歡迎來到這份深度技術筆記。我是你們的資深技術導師，今天我們將深入探討 Google **代理程式開發套件 (ADK)** 的核心靈魂：**雙向串流 (Bidi-streaming)**。

在傳統的 AI 互動中，我們習慣了「提問並等待」的僵化模式，這就像在傳送電子郵件；而 **雙向串流** 則代表了一場根本性的變革——它讓 AI 互動變得更像「撥打電話」：流暢、自然，且具備即時中斷與回應的能力。我們將從架構、生命週期到實戰配置，逐一解構這項技術。

### 📌 雙向串流學習地圖

1.  **核心定義與技術價值**：為什麼選擇 Bidi-streaming 而非傳統 API？
2.  **架構組件解構**：理解 `LiveRequestQueue`、`Runner` 與事件模型。
3.  **四階段生命週期**：從初始化到優雅終止的實戰流程。
4.  **模型架構差異**：原生音訊模型 vs. 半串聯模型。
5.  **RunConfig 深度配置**：掌握會話恢復與上下文視窗壓縮。

---

### 一、 為什麼我們需要雙向串流？
在開發「生產級」應用時，低延遲與類人互動是成功的關鍵。雙向串流不僅僅是資料的傳遞，它實現了以下三大核心特性：

*   **雙向通訊 (Bidirectional)**：人類和 AI 可以同時說話、聆聽和回應，資料交換不需等待完整回應。
*   **響應式中斷 (Responsive Interruption)**：這是提升用戶體驗最重要的功能。如果 AI 正在長篇大論，使用者可以隨時插嘴糾正，AI 會立即停止並解決新問題。
*   **原生多模態 (Native Multimodal)**：不再需要經過 STT (語音轉文字) 或 TTS (文字轉語音) 的繁瑣中間層，Gemini 原生音訊模型能直接理解與生成語音，實現極低延遲。

#### 💡 場景驅動教學：購物管家
**問：** 「如果我在電商 App 中展示一張我的客廳照片，AI 能做什麼？」
**解析：** 根據來源資料中的 *Shopper's Concierge 2* 展示，具備 Bidi 功能的代理程式能透過**環境感知 (Visual Awareness)**，「看見」你的桌子與筆電，主動詢問是否需要推薦螢幕架或檯燈。這種從「被動等待指令」轉向「主動觀察環境」的轉變，正是 Bidi-streaming 的魅力所在。

---

### 二、 ADK  vs. 原始 Live API：為何不直接調用？
許多開發者會問：「為什麼不直接用原始的 Google GenAI SDK？」關鍵在於 ADK 將數個月的基礎設施開發簡化為**宣告式配置**。

| 功能分類 | 原始 Live API (Raw) | ADK 雙向串流 |
| :--- | :--- | :--- |
| **工具執行** | 需手動處理 Function Call 回應 | **自動化執行**工具並回傳結果 |
| **連線管理** | 需自行實作重連與恢復邏輯 | **自動重連**與會話恢復 (Session Resumption) |
| **狀態持久化** | 需手動實作資料庫儲存 | 內建支援 SQL、Vertex AI 等**工作階段持久化** |
| **非同步框架** | 需手動協調雙向資料流 | 提供統一的 `LiveRequestQueue` 介面 |

---

### 三、 核心實戰：四階段生命週期與代碼分析
我們開發 ADK Bidi 應用程式時，必須遵循這四個階段：

#### 階段 1：應用程式初始化
我們需要建立 Agent、SessionService 與 Runner。這些組件在啟動時建立一次，並在所有會話中共享。

#### 階段 2：工作階段初始化
為每個使用者建立 `RunConfig` 與 `LiveRequestQueue`。

#### 階段 3：`run_live()` 事件迴圈
這是實戰的核心。我們必須在**非同步上下文**中運行，並採取「上游/下游任務」並行執行的模式。

#### ⚡ 代碼即真理：FastAPI WebSocket 實作註解
以下是來源資料中具備技術權威感的實作範例：

```python
# [導師點評]：這是 Phase 3 的核心。我們啟動兩個任務：
# upstream_task 負責將 WebSocket 訊息推入 ADK 佇列
# downstream_task 負責從 ADK 獲取 Event 並推回 WebSocket

async def upstream_task() -> None:
    """接收來自 WebSocket 的訊息並發送到 LiveRequestQueue。"""
    while True:
        message = await websocket.receive()
        if "bytes" in message:
            # 處理音訊二進位流 (16-bit PCM, 16kHz)
            audio_blob = types.Blob(mime_type="audio/pcm;rate=16000", data=message["bytes"])
            live_request_queue.send_realtime(audio_blob) # 這是非阻塞的
        elif "text" in message:
            # 處理文字請求
            json_message = json.loads(message["text"])
            if json_message.get("type") == "text":
                content = types.Content(parts=[types.Part(text=json_message["text"])])
                live_request_queue.send_content(content) # 發送離散的對話輪次

async def downstream_task() -> None:
    """接收來自 run_live() 的 Event 並發送到 WebSocket。"""
    # [關鍵在於]：run_live 是非同步產生器，它會即時產生 Event 物件
    async for event in runner.run_live(
        user_id=user_id,
        session_id=session_id,
        live_request_queue=live_request_queue,
        run_config=run_config,
    ):
        # 序列化事件為 JSON 並排除 None 欄位以節省頻寬
        event_json = event.model_dump_json(exclude_none=True, by_alias=True)
        await websocket.send_text(event_json)

# 使用 gather 同時運行上游與下游，實現真正的雙向通訊
try:
    await asyncio.gather(upstream_task(), downstream_task())
finally:
    # 階段 4：終止。務必關閉佇列，否則會產生「殭屍會話」消耗配額
    live_request_queue.close()
```

---

### 四、 關鍵配置：深度掌握 RunConfig
`RunConfig` 是你控制串流行為的控制台。

#### 1. 會話恢復 (Session Resumption)
**這代表什麼？** 原生 Live API 的單個連線通常限制在 10 分鐘內。透過啟用 `session_resumption`，ADK 會自動快取「恢復句柄」，在連線中斷時透明地重新連線，使用者完全不會察覺。

#### 2. 上下文視窗壓縮 (Context Window Compression)
對於長達數小時的對話，Token 限制與時間上限是開發者的噩夢。當 Token 達到 `trigger_tokens` 閾值時，ADK 會自動進行摘要壓縮，這能將會話持續時間延長至**無限時間**。

#### 3. 原生音訊 vs. 半串聯模型
我們在選擇模型時必須非常小心其架構差異：

| 特性 | 原生音訊模型 (Native Audio) | 半串聯模型 (Half-Cascade) |
| :--- | :--- | :--- |
| **處理方式** | 端到端直接處理音訊 | 語音轉文字後再處理 |
| **回應形式** | 僅限 AUDIO (預設) | 支援 TEXT 與 AUDIO |
| **進階功能** | 支援**情感對話**與**主動式音訊** | 不支援主動性功能 |

---

### 五、 知識收斂與實戰總結
雙向串流 (Bidi-streaming) 不僅僅是一項功能，它是 AI 代理程式朝向**實體化 (Embodiment)** 與**主動化**邁進的重要一步。

**關鍵總結：**
*   **非同步是必須的**：所有的 Bidi 應用必須在非同步上下文中運行。
*   **優雅終止**：永遠記得呼叫 `live_request_queue.close()`，避免耗盡並行會話配額。
*   **多代理整合**：使用 `SequentialAgent` 時，ADK 會自動管理代理程式間的透明切換與背景傳遞。

想要更進一步，我建議你安裝並執行 `bidi-demo` 範例，親自體驗亞秒級延遲的震撼。

#GoogleADK #GeminiLive #BidiStreaming #MultimodalAI #AgentDevelopmentKit