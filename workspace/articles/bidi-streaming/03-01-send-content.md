歡迎回到這份深度技術筆記。我是你們的資深技術導師。

在我們探討 **ADK 雙向串流 (Bidi-streaming)** 的上游 (Upstream) 訊息傳遞時，雖然音訊與視覺的即時性令人驚艷，但「文字」依然是對話邏輯的核心。今天我們要深入解構 `send_content()` 方法，看看它如何定義對話的「輪次」，以及在串流架構中如何處理文字數據。

---

### 📌 `send_content()` 學習地圖

1.  **輪次模式的本質**：為什麼文字訊息會觸發立即回應？
2.  **架構解構：Content 與 Part**：理解資料容器的階層關係。
3.  **上游場景驅動**：在串流過程中插入文字請求。
4.  **代碼即真理**：FastAPI 中的文字發送實作。
5.  **導師點評與最佳實踐**：與 `send_realtime()` 的關鍵區別。

---

### 一、 輪次模式的本質：什麼是「對話輪次」？

在 ADK 中，`send_content()` 與 `send_realtime()` 的最大區別在於其對「時間」的處理方式。

*   **send_realtime()**：處理的是持續、細碎的二進位流（如音訊），模型會連續監聽但不一定立即結束回合。
*   **send_content()**：採用的是 **輪次模式 (Turn-based mode)**。
    *   **這代表什麼？** 每當你呼叫此方法發送一條文字訊息，它就代表一個「離散的對話輪次」。
    *   **關鍵機制**：此操作會向模型發出一個完整輪次的訊號，進而**觸發模型立即生成回應**。

---

### 二、 邏輯具象化：Content 與 Part 的階層關係

在傳送文字時，我們並不是直接丟出一串字串，而是將其封裝進一個結構化的容器中。

| 組件 | 技術定義 | 在 Bidi-streaming 中的角色 |
| :--- | :--- | :--- |
| **Content** | 訊息容器 | 代表對話中單個訊息或輪次，保存一個 Part 陣列。 |
| **Part** | 內容片段 | 訊息中的各個最小片段。在上游文字傳遞中，主要使用 `text` 欄位。 |

**導師建議**：在實務操作中，絕大多數的 `send_content()` 訊息僅使用**單個文字 Part**。雖然結構支援多個 Part（例如混合文字與結構化數據），但對於 Live API 而言，多模態輸入（音訊/視訊）通常使用不同的機制，而非封裝在 `Part` 裡。

---

### 三、 場景驅動教學：當文字介入串流

**提問：** 「如果使用者正在進行語音對話，突然在 App 視窗輸入了一段文字，這會發生什麼？」

**解析：**
根據來源資料，這正是雙向串流的強大之處。由於 `send_content()` 是**非阻塞 (Non-blocking)** 的，它會立即將文字訊息加入 `LiveRequestQueue`。
*   模型接收到文字內容後，會將其視為當前對話歷史的一部分。
*   因為這是一個明確的「內容發送」，模型會停止之前的思考（或產生中斷標記），並針對這段新文字立即產生回應。

---

### 四、 代碼即真理：FastAPI 文字發送實作

以下是來源資料中 `bidi-demo` 的核心實作，展示了在 `upstream_task` 中如何處理 JSON 格式的文字請求：

```python
# [導師點評]：這是 Phase 3 活躍工作階段中的上游任務。
# 注意它是如何將 WebSocket 接收到的 JSON 訊息轉換為 ADK 的 Content 物件。

elif "text" in message:
    text_data = message["text"]
    json_message = json.loads(text_data)

    # 提取文字並發送到 LiveRequestQueue
    if json_message.get("type") == "text":
        logger.debug(f"正在發送文字內容: {json_message['text']}")

        # [架構要點]：建立 Content 並放入一個 Part 數組，裡面包含 text 欄位
        content = types.Content(
            parts=[types.Part(text=json_message["text"])]
        )

        # [關鍵在於]：呼叫 send_content()。
        # 此方法是同步且非阻塞的，它會立即返回，確保 UI 不會卡頓。
        live_request_queue.send_content(content)
```
*(參考來源：)*

---

### 五、 知識收斂與最佳實踐

在構建上游訊息傳遞邏輯時，請務必遵循以下準則：

1.  **區分模態通道**：請勿將 `send_content()` 與圖片或影像數據（`inline_data`）混合使用。影像與持續音訊應始終使用 `send_realtime()` 進行傳輸。
2.  **避免手動處理工具回應**：雖然 `Part` 支援 `function_response`，但 **ADK 會自動處理工具執行迴圈**。身為開發者，你通常不需要在 `send_content()` 中手動構建這些複雜的結構。
3.  **善用非阻塞特性**：由於 `send_content()` 立即返回，你可以在非同步程式碼的任何地方呼叫它，而不需要使用 `await`，這簡化了開發複雜度。
4.  **確保對話唯一性**：再次強調，`LiveRequestQueue` 是對話特定且有狀態的。**每個對話都必須使用新的隊列**發送 `send_content`，否則會帶入上一個對話的殘留訊號。

**總結：**
`send_content()` 是驅動 AI 代理程式邏輯轉向的齒輪。它將文字輸入定義為一個明確的「請求點」，迫使模型在串流的海洋中停下來，針對特定的文字指令給出精準的回應。

#send_content #ConversationTurns #ADKUpstream #GeminiBidi #TextInteraction