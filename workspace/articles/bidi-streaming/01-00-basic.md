歡迎回到這份深度技術筆記。我是你們的技術導師，今天我們將深入探討 Google **代理程式開發套件 (ADK)** 的核心靈魂：**雙向串流 (Bidi-streaming)** 的技術架構與運作邏輯。

在傳統的 AI 互動中，我們習慣了「提問並等待」的僵化模式，這就像在傳送電子郵件；而 **雙向串流** 則代表了一場根本性的變革——它讓 AI 互動變得更像「撥打電話」：流暢、自然，且具備即時中斷與回應的能力。

---

### 📌 雙向串流技術架構地圖

1.  **架構核心定義**：為什麼 Bidi-streaming 是與傳統 AI 互動的根本轉變？
2.  **三大核心組件**：解析 `LiveRequestQueue`、`Runner` 與 `Agent` 的職責。
3.  **底層技術支援**：Gemini Live API 與 Vertex AI Live API 的異同。
4.  **四階段生命週期**：從初始化到優雅終止的運作邏輯。
5.  **代碼解析與實戰場景**：透過 FastAPI 與 WebSocket 實現雙向通訊。

---

### 一、 核心定義：從「發送電郵」到「撥打電話」

在 ADK 的語境下，雙向串流不僅僅是資料的傳遞，它實現了真正意義上的 **全雙工 (Full-duplex) 通訊**。

*   **雙向通訊 (Bidirectional)**：持續的資料交換，無需等待完整回應。
*   **響應式中斷 (Responsive Interruption)**：這是提升用戶體驗最重要的技術亮點。如果 AI 正在長篇大論，使用者可以隨時插嘴，AI 會立即停止並處理新的輸入。
*   **原生多模態 (Native Multimodal)**：採用 Gemini 原生音訊模型，直接理解與生成語音，不需經過 STT 或 TTS 的中間處理，從而實現極低延遲。

---

### 二、 架構組件：解構 ADK 的核心模組

來源資料明確指出，ADK 將複雜的基礎設施開發（連線管理、工具編排、狀態持久化）轉化為「宣告式配置」。

#### 1. 高階組件職責表

| 組件名稱 | 技術職責 | 關鍵屬性 |
| :--- | :--- | :--- |
| **Agent** | 定義 AI 的行為、人格、模型與工具。 | 無狀態且可重用。 |
| **LiveRequestQueue** | 訊息隊列，緩衝並排序傳入的文字、音訊、視訊或控制訊號。 | 對話特定且有狀態，不可重用。 |
| **Runner** | 執行引擎，負責編排對話流、管理對話狀態並提供 `run_live()` 介面。 | 應用程式啟動時建立一次，多個會話共享。 |
| **RunConfig** | 定義特定會話的串流行為（模態、逐字稿、會話恢復）。 | 對話特定，可針對不同使用者客製化。 |

#### 2. 底層 API 平台：Gemini vs. Vertex AI
**關鍵點在於**，ADK 提供了一種透明的平台靈活性。開發者可以在本地使用 Gemini Live API (AI Studio) 快速原型設計，然後無縫遷移到 Vertex AI (Google Cloud) 進行生產部署，這一切 **無需更改應用程式代碼**，只需調整環境配置。

---

### 三、 邏輯具象化：串流資料流向圖

為了強化視覺記憶，我們可以將資料的流動拆解為 **上游 (Upstream)** 與 **下游 (Downstream)** 兩個並行的任務：

```text
[使用者應用程式] <--- WebSocket/SSE ---> [ADK 框架] <--- WebSocket ---> [Live API 後端]
      |                                    |                           |
      | (上游任務)                          | (處理與編排)               | (模型計算)
      +--- 發送文字/音訊/視訊 -----------> [LiveRequestQueue] --------> | 接收輸入
                                           |                           |
      | (下游任務)                          | (自動工具執行)             | (產生回應)
      <--- 接收 Event (文字/音訊/逐字稿) --- [run_live()] <----------- +--- 產生事件
```

---

### 四、 代碼即真理：FastAPI WebSocket 實作分析

來源資料中提供了一個完整的參考實作，展示了如何協調非同步的雙向流。

```python
# [導師點評]：這是 Phase 3 的核心。我們使用 asyncio.gather 啟動兩個並行的非同步任務。
# upstream_task 處理「入站」訊息，downstream_task 處理「出站」事件。

async def upstream_task() -> None:
    """接收來自 WebSocket 的訊息並發送到 LiveRequestQueue。"""
    while True:
        message = await websocket.receive()
        if "bytes" in message:
            # [實戰提示]：音訊必須符合 16-bit PCM, 16kHz 格式
            audio_blob = types.Blob(mime_type="audio/pcm;rate=16000", data=message["bytes"])
            live_request_queue.send_realtime(audio_blob)
        elif "text" in message:
            # 處理文字請求，透過 send_content 觸發模型回應
            json_message = json.loads(message["text"])
            if json_message.get("type") == "text":
                content = types.Content(parts=[types.Part(text=json_message["text"])])
                live_request_queue.send_content(content)

async def downstream_task() -> None:
    """接收來自 run_live() 的 Event 並發送到 WebSocket。"""
    # run_live 是一個非同步產生器，會持續產生離散的對話事件
    async for event in runner.run_live(
        user_id=user_id,
        session_id=session_id,
        live_request_queue=live_request_queue,
        run_config=run_config,
    ):
        # 序列化為 JSON。排除 None 欄位是為了最小化 payload 大小
        event_json = event.model_dump_json(exclude_none=True, by_alias=True)
        await websocket.send_text(event_json)

try:
    await asyncio.gather(upstream_task(), downstream_task())
finally:
    # [關鍵原則]：務必關閉隊列，否則會產生計入配額的「殭屍會話」
    live_request_queue.close()
```

---

### 五、 場景驅動教學：解決生產級痛點

**提問：** 「如果使用者的網路突然不穩斷開，整個對話歷史會丟失嗎？」

**解析：** 這就是 ADK 架構中 **會話恢復 (Session Resumption)** 的價值所在。
*   **這代表什麼？** 在底層，Live API 連線通常限制在 10 分鐘左右。
*   **ADK 的處理方式**：如果啟用了 `session_resumption`，ADK 會自動快取「恢復句柄」。當偵測到網路連線中斷或達到時間限制時，ADK 會在幕後透明地重新連線，保留完整的對話歷史與工具執行狀態，使用者完全不會察覺。

**提問：** 「對於長時間的導購對話，如何防止 Token 超限導致會話中斷？」

**解析：** 您應該啟用 **上下文視窗壓縮 (Context Window Compression)**。
*   當 Token 達到預設閾值（例如 trigger_tokens），Live API 會自動摘要較早的對話，並保留最近的內容。
*   **實戰導向總結**：啟用此功能後，會話持續時間將變為「無限時間」，這對於需要深度諮詢的電商管家場景至關重要。

---

### 💡 知識延伸與收斂

ADK 的雙向串流架構成功地將低階的 WebSocket 管理抽象化，讓開發者能透過 `run_live()` 事件迴圈專注於業務邏輯。無論是 **模糊語意搜尋** 還是 **視覺環境感知**（如 *Shopper's Concierge* 示範中 AI「看見」桌面環境並推薦商品），其核心皆建立在這一套穩定且具備彈性的架構之上。

**學習建議：**
*   **掌握四階段生命週期**：初始化 -> 初始化會話 -> 事件迴圈 -> 優雅終止。
*   **善用 `RunConfig`**：它是控制回應模態、VAD 設定與配額管理的「控制台」。
*   **關注音訊規格**：輸入 16kHz PCM，輸出 24kHz PCM（原生音訊模型）。

#GoogleADK #BidiStreaming #GeminiLiveAPI #AIAgentArchitecture #RealTimeMultimodal