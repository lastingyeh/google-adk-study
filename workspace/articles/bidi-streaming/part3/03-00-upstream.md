歡迎來到這份深度技術筆記。我是你們的技術導師。在掌握了 ADK 的架構組件與生命週期後，我們今天要進入實戰中最關鍵的環節：**訊息傳遞 (Upstream)**。

在雙向串流的脈絡下，「上游 (Upstream)」指的是從使用者端將資料傳送至 AI 代理程式的過程。這不僅是傳送文字，更包含了即時音訊、影像影格以及控制對話節奏的訊號。ADK 透過 `LiveRequestQueue` 徹底簡化了這一切，讓我們能像打電話一樣與 AI 進行多模態互動。

### 📌 訊息傳遞 (Upstream) 學習地圖

1.  **核心介面：LiveRequestQueue** —— 統一的訊息容器與非同步管理。
2.  **三大訊息傳遞模式**：
    *   **離散文字**：`send_content()` 的回合制互動。
    *   **即時串流**：`send_realtime()` 的音訊與影像處理。
    *   **控制訊號**：活動訊號 (Activity Signals) 與優雅關閉。
3.  **實戰並行架構**：上游任務 (Upstream Task) 的非同步實作。
4.  **數據技術指標**：音訊與影像的規格約束。

---

### 一、 核心組件：`LiveRequestQueue` 的設計哲學

在原始的 API 開發中，處理文字、音訊、視訊通常需要管理多個複雜的通道。但 **ADK 的精髓在於簡化**。它提供了 `LiveRequestQueue` 作為統一介面，將所有輸入類型封裝進 `LiveRequest` 模型中。

**關鍵特性：**
*   **執行緒安全 (Thread-safe)**：這是一個非同步隊列，能安全地緩衝並排序傳入的訊息。
*   **非阻塞發送 (Non-blocking)**：它的發送方法（如 `send_content`）是同步的，不需 `await` 即可立即返回，這確保了 UI 的流暢性。
*   **對話唯一性**：**這代表什麼？** 每一個 `run_live()` 呼叫都必須擁有一個全新的隊列，嚴禁重複使用，否則會導致訊息順序錯亂或狀態損毀。

---

### 二、 訊息傳遞模式：如何與 AI 對話

根據來源資料，我們將上游訊息分為三種類型，每種都有其特定的應用場景。

#### 1. 離散文字互動 (`send_content`)
當使用者輸入文字時，我們會觸發一個完整的「對話回合」，促使模型立即生成回應。
*   **技術結構**：使用 `Content` 保存 `Part` 陣列。
*   **實戰提示**：雖然支援多個 Part，但大多數情況僅使用單個文字 Part。

#### 2. 即時多模態串流 (`send_realtime`)
這是雙向串流的核心，用於處理持續不斷的二進位數據。

| 模態          | 技術規格                  | 處理建議                             |
| :------------ | :------------------------ | :----------------------------------- |
| **音訊**      | 16-bit PCM, 16kHz, 單聲道 | 建議以 50-100ms 為一塊進行分段發送。 |
| **影像/視訊** | JPEG 格式, 768x768 解析度 | 建議頻率為 **每秒 1 幀 (1 FPS)**。   |

#### 3. 活動與控制訊號
*   **活動訊號 (VAD)**：預設情況下，Live API 內建自動語音活動偵測 (VAD)。僅在手動控制（如「一鍵通 Push-to-talk」）時，才需發送 `ActivityStart` 與 `ActivityEnd`。
*   **關閉訊號**：透過 `close()` 發送，這是確保雲端資源釋放、避免「殭屍會話」的唯一手段。

---

### 三、 代碼即真理：上游任務 (Upstream Task) 的實作

在雙向串流應用程式中，上游任務必須作為一個獨立的協程 (Coroutine) 運作。以下是來源資料中 `bidi-demo` 的核心邏輯註解：

```python
# [導師點評]：這是上游任務的典型設計。它是一個無限迴圈，
# 持續監聽來自 WebSocket 的輸入，並根據類型轉發給隊列。

async def upstream_task() -> None:
    """從 WebSocket 接收訊息並發送到 LiveRequestQueue。"""
    while True:
        message = await websocket.receive()

        # 1. 處理音訊數據 (二進位影格)
        if "bytes" in message:
            # [關鍵在於]：必須符合 16kHz PCM 格式
            audio_blob = types.Blob(
                mime_type="audio/pcm;rate=16000", data=message["bytes"]
            )
            live_request_queue.send_realtime(audio_blob) # 同步方法，非阻塞發送

        # 2. 處理文字與影像 (JSON 格式)
        elif "text" in message:
            json_message = json.loads(message["text"])

            # 處理文字請求
            if json_message.get("type") == "text":
                content = types.Content(
                    parts=[types.Part(text=json_message["text"])]
                )
                live_request_queue.send_content(content) # 觸發立即回應

            # 處理靜態影像 (Base64 解碼)
            elif json_message.get("type") == "image":
                image_data = base64.b64decode(json_message["data"])
                image_blob = types.Blob(
                    mime_type="image/jpeg", data=image_data
                )
                live_request_queue.send_realtime(image_blob) # 以 1 FPS 發送影格
```

---

### 四、 場景驅動教學：視覺感知與主動式推薦

**提問：** 「如果使用者只是開著鏡頭，不說話，AI 能接收到訊息嗎？」

**解析：** 根據 *Shopper's Concierge* 的展示，這正是雙向串流的強大之處。
*   **主動感知**：即使使用者沒有發送文字指令，應用程式仍可透過 `send_realtime()` 以 1 FPS 的頻率持續發送環境影像。
*   **上游回饋**：模型透過上游接收到的影像影格（如書桌上的筆電），主動生成「下游」的回應（如推薦螢幕架或支架）。這種「觀察 -> 理解 -> 主動建議」的流程，完全依賴上游任務中穩定的影像串流傳輸。

---

### 💡 知識延伸與總結

訊息傳遞 (Upstream) 的穩定性直接決定了 AI 代理程式的「感知力」。

**實戰導向總結：**
1.  **統一入口**：無論文字或音訊，請透過 `LiveRequestQueue` 進行，它會自動處理編碼與傳輸。
2.  **音訊規格**：請務必在用戶端完成 16kHz PCM 的轉換，ADK 不負責格式轉換。
3.  **優雅退出**：當 WebSocket 中斷時，務必呼叫 `live_request_queue.close()`，否則殭屍會話會持續消耗並行配額。

🏷️ `upstream-messaging`, `live-request-queue`, `multi-modal-input`, `gemini-live-api`, `real-time-audio`

**下一課預告**：我們將探討「下游 (Downstream)」，學習如何接收並處理模型產生的即時事件。