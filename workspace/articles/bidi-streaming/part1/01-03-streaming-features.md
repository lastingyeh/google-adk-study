歡迎來到這份深度技術筆記。我是你們的資深技術導師。

在我們探討 Google 代理程式開發套件 (ADK) 的核心時，**雙向串流 (Bidi-streaming)** 不僅僅是一項功能，它是對 AI 互動範式的根本性重塑。在更大的技術背景下，它代表著從「非同步請求」轉向「全雙工對話」的跨越。今天，我們將解構這項技術的特性、架構支撐以及它如何改變生產級應用的開發。

---

### 📌 雙向串流核心特性學習地圖

1.  **通訊範式的轉移**：從「電子郵件」模式到「電話對談」模式。
2.  **三大支柱特性**：響應式中斷、原生多模態與語音活動偵測 (VAD)。
3.  **底層架構解密**：WebSocket 全雙工協定與 Live API 平台。
4.  **實戰應用場景**：環境感知與主動式對話。
5.  **生命週期與並行模式**：上游與下游任務的協同。

---

### 一、 通訊範式的轉移：為什麼它與眾不同？

我們首先要理解，雙向串流與傳統 AI 互動有著本質的差異。傳統互動像是「傳送電子郵件」，你發送完整訊息並等待回傳；而雙向串流則像是「撥打電話」，雙方可以同時說話、聆聽和回應。

#### 💡 邏輯具象化：串流類型對比表

根據來源資料，我們可以將雙向串流與其他常見模式進行區分：

| 串流類型               | 數據流向                | 關鍵特性                     | 互動體驗                 |
| :--------------------- | :---------------------- | :--------------------------- | :----------------------- |
| **伺服器端串流 (SSE)** | 單向 (Server -> Client) | 持續接收資料但無法即時回饋   | 像觀看直播影片           |
| **Token 級別串流**     | 單向 (模型產出)         | 逐字生成但不可中斷           | 觀看他人即時輸入文字     |
| **雙向串流 (Bidi)**    | **雙向 (Full-duplex)**  | **具備中斷支援、多模態輸入** | **自然對話，可隨時插嘴** |

---

### 二、 核心特性深潛：自然互動的技術靈魂

雙向串流的技術權威感來自於它對人類對話細節的精準模擬。

#### 1. 響應式中斷 (Responsive Interruption)
這是提升使用者體驗最重要的功能。**這代表什麼？** 當 AI 正在長篇大論解釋複雜概念時，使用者可以隨時插嘴提出澄清。系統會偵測到中斷訊號（`interrupted=True`），AI 會立即停止當前輸出並處理新問題。

#### 2. 原生多模態 (Native Multimodal)
**關鍵在於**，ADK 採用了 Gemini 原生音訊模型。與傳統做法不同，它不需要經過「語音轉文字 (STT)」再到「文字轉語音 (TTS)」的中間層。模型直接理解音訊並生成音訊，大幅降低了延遲，實現了亞秒級的回應速度。

#### 3. 語音活動偵測 (VAD)
系統內建 VAD 機制，能自動判斷使用者何時說完話，實現精準的「輪流對話 (Turn-taking)」，消除了尷尬的停頓。

---

### 三、 架構組件：支撐雙向串流的骨幹

在 ADK 架構中，雙向串流由多個專業組件協同完成，實現了關注點分離。

*   **LiveRequestQueue**：這是一個執行緒安全的非同步隊列，負責緩衝並排序上游的使用者訊息（文字、音訊、視訊）。
*   **Runner & run_live()**：這是執行引擎，它建立持久的 WebSocket 連線，並以非同步產生器的方式即時產生事件。
*   **RunConfig**：允許開發者宣告式地配置模態（TEXT/AUDIO）、會話恢復與壓縮策略。

---

### 四、 代碼即真理：並行任務的實作註解

在雙向串流中，應用程式必須同時處理「發送」與「接收」。以下是來源資料中典型的 **上游/下游並行模式**：

```python
# [導師點評]：這是實現雙向性的核心——上游與下游任務必須並行執行
# 我們使用 asyncio.gather 來啟動這兩個協程

async def upstream_task() -> None:
    """接收來自 WebSocket 的訊息並推入 LiveRequestQueue。"""
    while True:
        message = await websocket.receive()
        if "bytes" in message:
            # 處理 16kHz PCM 音訊塊
            audio_blob = types.Blob(mime_type="audio/pcm;rate=16000", data=message["bytes"])
            live_request_queue.send_realtime(audio_blob) # 非阻塞發送
        elif "text" in message:
            # 處理文字請求
            json_message = json.loads(message["text"])
            if json_message.get("type") == "text":
                content = types.Content(parts=[types.Part(text=json_message["text"])])
                live_request_queue.send_content(content) # 發送離散輪次

async def downstream_task() -> None:
    """從 run_live() 獲取 Event 並推回客戶端。"""
    async for event in runner.run_live(
        user_id=user_id, session_id=session_id,
        live_request_queue=live_request_queue, run_config=run_config,
    ):
        # 序列化事件並傳回
        event_json = event.model_dump_json(exclude_none=True, by_alias=True)
        await websocket.send_text(event_json)

# [關鍵實作]：同時運行並確保清理
try:
    await asyncio.gather(upstream_task(), downstream_task())
finally:
    # 務必優雅關閉隊列，避免產生「殭屍會話」計入配額
    live_request_queue.close()
```

---

### 五、 場景驅動：從功能到實際價值

**提問：** 「在電商場景中，雙向串流如何超越傳統機器人？」
**解析：** 根據 *Shopper's Concierge* 的案例，雙向串流賦予了代理程式「視覺感知」與「主動性」。
*   **主動對話**：AI 可以觀察攝影機畫面，辨識出使用者的桌面環境（如筆電、支架），並主動詢問是否需要推薦相關電子產品。
*   **模糊語意理解**：使用者可以用口語描述「印有跳舞的人的杯子」，AI 結合視覺與對話背景，在海量商品中精準定位。

---

### 💡 知識延伸與總結

ADK 的雙向串流架構將數個月的基礎設施開發（連線管理、中斷處理、自動轉錄）簡化為 **宣告式配置**。

**實戰導向總結：**
*   **選擇 BIDI 模式**：當你需要即時音訊/影片、插嘴支援或 VAD 時，BIDI 是唯一選擇。
*   **管理會話恢復**：啟用 `session_resumption` 來對抗物理連線的 10 分鐘限制。
*   **注意配額**：Live API 有並行會話限制（Gemini 約 50-1,000 個），生產環境需考慮「會話池」設計。

🏷️ `bidi-streaming`, `low-latency-ai`, `adk-architecture`, `gemini-live-api`, `real-time-multimodal`

**更多學習資源**：
*   有關 VAD 的微調，請參閱《第 5 部分：語音活動檢測》。
*   有關配額增加流程，請訪問 Google Cloud 的「配額」管理頁面。

---

[← 上一頁](./01-02-adk-components.md) | [下一頁 (Part 2) →](../part2/02-00-app-lifecycle.md) | [課程首頁 ↩](../COURSE_PLAN.md)