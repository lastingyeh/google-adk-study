歡迎來到這份技術深度筆記。我是你們的資深技術導師，在我們討論過 `send_content()` 如何處理文字對話輪次後，今天我們要進入 **ADK 雙向串流 (Bidi-streaming)** 的真正戰場：**`send_realtime()` 與多模態資料流**。

如果說 `send_content()` 是在寫信，那麼 `send_realtime()` 就是在進行「現場直播」。它不處理離散的訊息，而是處理持續不斷的 **音訊塊、影像影格與視訊流**。這種模式是讓 AI 具備「聽力」與「視力」的核心動脈，更是實現亞秒級延遲互動的關鍵。

---

### 📌 `send_realtime()` 串流實戰地圖

1.  **即時模式 (Real-time Mode) 的本質**：為什麼它與輪次模式（Turn-based）不同？
2.  **音訊串流規格與最佳實務**：從 16kHz PCM 到 50ms 分段策略。
3.  **視覺與影像處理**：理解 1 FPS 的「眼睛」如何觀察世界。
4.  **底層資料容器：Blob 與 Pydantic**：自動化的 Base64 處理機制。
5.  **場景驅動：主動感知應用**：如何實現「看見環境並主動建議」？

---

### 一、 即時模式的本質：持續性 vs. 離散性

在 ADK 的架構中，`send_realtime()` 專門用於處理二進位數據串流。

*   **連續處理**：不同於文字訊息會觸發立即的回應，模型對 `send_realtime()` 的資料是**持續監聽與處理**的，不一定會按回合結束。
*   **非阻塞發送**：發送方法會立即將資料加入隊列而不阻塞，確保使用者介面在 AI 繁重處理時仍能保持流暢。
*   **靈活的 MIME 類型**：透過 MIME 類型，模型能立即辨識傳入的是音訊（PCM）還是影像（JPEG）。

#### 💡 邏輯具象化：多模態輸入規格表

| 模態             | 格式要求                | 建議規格                   | 關鍵特性                   |
| :--------------- | :---------------------- | :------------------------- | :------------------------- |
| **音訊 (Audio)** | 16-bit PCM (有符號整數) | 16kHz, 單聲道 (Mono)       | 需採分段串流 (50-100ms/塊) |
| **影像 (Image)** | JPEG (image/jpeg)       | 768x768 解析度             | 單張快照或環境背景         |
| **視訊 (Video)** | 逐影格 JPEG             | 最高 **1 FPS** (每秒 1 幀) | 適用於理解環境而非動態追蹤 |

---

### 二、 音訊串流：賦予 AI 聽力

發送音訊時，**關鍵在於分段策略 (Chunking Strategy)**。ADK 不會替你進行音訊格式轉換，因此資料必須在進入 `send_realtime()` 前就符合規格。

**這代表什麼？**
如果你一次發送太大的音訊塊，延遲會增加；如果太小，則網路開銷會上升。
*   **導師建議**：使用 **50-100ms** 的分段大小（在 16kHz 下約為 1600-3200 位元組）能取得延遲與開銷的最佳平衡。

#### ⚡ 代碼即真理：FastAPI 接收並轉發音訊塊
以下是來源資料中處理二進位音訊影格的核心邏輯：

```python
# [導師點評]：這是 Phase 3 上游任務處理二進位影格的標準模式。
# 我們從客戶端 WebSocket 接收原始位元組 (bytes)

if "bytes" in message:
    audio_data = message["bytes"]
    logger.debug(f"接收到二進位音訊塊: {len(audio_data)} bytes")

    # [關鍵在於]：建立 Blob 並指定 MIME 類型為 16kHz PCM
    # 這是 Live API 要求的標準音訊輸入格式
    audio_blob = types.Blob(
        mime_type="audio/pcm;rate=16000",
        data=audio_data
    )

    # 呼叫 send_realtime 進行非阻塞傳送
    live_request_queue.send_realtime(audio_blob)
```

---

### 三、 影像與視訊：AI 的眼睛

在 ADK 中，視訊並非透過 H.264 或 mp4 傳輸，而是被簡化為**持續的 JPEG 影格**。

*   **影格率限制**：建議最高為 **1 FPS**。雖然這不足以處理體育分析或高速運動追蹤，但對於理解物理世界的上下文（例如辨識桌上的筆電或損壞的機器零件）已經綽綽有餘。
*   **視覺環境感知 (Visual Awareness)**：這是 `send_realtime()` 最驚豔的應用。如 *Shopper's Concierge* 展示，AI 能「看見」你身處居家辦公環境，並主動建議螢幕架或燈具。

#### ⚡ 代碼即真理：處理 Base64 影像資料
當我們從瀏覽器傳送畫面截圖時，通常會使用 Base64 編碼，以下是伺服器端的處理邏輯：

```python
# [導師點評]：處理影像時，我們通常接收 Base64 字串並解碼
elif json_message.get("type") == "image":
    logger.debug("接收到影像資料")

    # 解碼 Base64 數據
    image_data = base64.b64decode(json_message["data"])
    mime_type = json_message.get("mimeType", "image/jpeg")

    # [關鍵在於]：同樣使用 Blob 封裝，但 MIME 類型改為影像
    # 這會告訴模型當前是視覺輸入
    image_blob = types.Blob(
        mime_type=mime_type,
        data=image_data
    )

    # 使用 send_realtime 傳送視覺影格
    live_request_queue.send_realtime(image_blob)
```

---

### 四、 底層機制：`Blob` 與 `LiveRequest`

在底層，`send_realtime()` 實際上是在構建一個 `LiveRequest` 物件，並將其放入非同步隊列中。

*   **互斥性規則**：在單個 `LiveRequest` 中，`content` (文字) 與 `blob` (音訊/影像) 是**互斥的**。這就是為什麼導師建議使用便利方法 `send_realtime()`，因為它會自動幫你確保這種約束，避免驗證錯誤。
*   **自動序列化**：`Blob` 物件中的原始位元組在透過網路傳輸（JSON 序列化）時，Pydantic 會自動處理 Base64 編碼，確保資料的安全傳輸。

---

### 五、 場景驅動：主動性對話 (Proactive Dialogue)

**提問：** 「如果使用者開著鏡頭但不說話，`send_realtime()` 如何發揮作用？」

**解析：**
根據來源資料，這正是「主動式音訊 (Proactive Audio)」與視覺感知結合的範例。
1.  應用程式透過 `send_realtime()` 每秒發送一個環境影格。
2.  模型分析影像序列並轉化為上下文。
3.  如果啟用了原生音訊模型的「主動性 (Proactivity)」，模型不需要使用者提問，就能根據「看見」的內容（如筆電和支架）主動開口建議。

這讓 AI 從一個「被動的回應者」變成了一個「主動的參與者」。

---

### 💡 知識延伸與總結

`send_realtime()` 是 ADK 實現多模態互動的命脈。它不僅傳遞資料，還維持了對話的動態感。

**實戰導向總結：**
*   **規格至上**：音訊必須是 **16kHz PCM**，影像建議為 **1 FPS JPEG**。
*   **非阻塞發送**：利用其非同步特性，在 `upstream_task` 中並行處理各種模態。
*   **搭配 VAD**：預設情況下，API 的語音活動偵測 (VAD) 會自動從你的音訊流中判斷說話邊界，無需手動發送活動訊號。

🏷️ `send-realtime`, `multi-modal-streaming`, `16khz-pcm`, `computer-vision-ai`, `bidi-messaging`

**下一課預告**：我們將探討「下游 (Downstream)」，學習如何從 `run_live()` 接收並處理 AI 傳回的多模態事件。