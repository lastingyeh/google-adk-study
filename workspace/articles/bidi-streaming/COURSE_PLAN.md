# Google ADK 雙向串流 (Bidi-Streaming) 架構與實戰大師班

歡迎來到這份深度技術課程計劃。本課程基於 Google 代理程式開發套件 (ADK) 的核心技術文件編寫，旨在協助資深開發者與架構師掌握次世代 AI 互動技術——**雙向串流 (Bidi-streaming)**。

在本課程中，您將學習如何擺脫傳統「提問-等待」的 API 模式，構建出具備**響應式中斷**、**原生多模態**與**主動感知能力**的生產級 AI 代理程式。



## 📚 課程模組總覽

本課程分為六大模組，共 26 個單元，循序漸進地涵蓋了從底層架構到產業應用的完整光譜。

### 🔹 模組一：技術基石與架構全貌 (Foundations)
本模組建立對 Bidi-streaming 技術的基礎認知，解析核心組件與平台選擇策略。

*   **單元 1: 雙向串流核心概念**
    *   **來源文件**: [`01-00-basic.md`](./part1/01-00-basic.md)
    *   **學習重點**:
        *   理解從「發送電郵」到「撥打電話」的互動典範轉移。
        *   掌握三大核心特性：雙向通訊、響應式中斷、原生多模態。
        *   認識資料流向：上游 (Upstream) 與下游 (Downstream) 的並行架構。

*   **單元 2: 深入 Live API 平台**
    *   **來源文件**: [`01-01-live-api.md`](./part1/01-01-live-api.md)
    *   **學習重點**:
        *   Gemini Live API (快速原型) vs. Vertex AI Live API (生產部署) 的選擇策略。
        *   原生音訊模型 (Native Audio) 與半串聯模型 (Half-Cascade) 的架構差異。
        *   理解物理「連線 (Connection)」與邏輯「會話 (Session)」的區別。

*   **單元 3: ADK 核心組件解構**
    *   **來源文件**: [`01-02-adk-components.md`](./part1/01-02-adk-components.md)
    *   **學習重點**:
        *   全域無狀態組件：`Agent`, `Runner`。
        *   會話特定組件：`LiveRequestQueue`, `RunConfig`。
        *   執行態狀態容器：`InvocationContext` 的作用。

*   **單元 4: 串流關鍵特性**
    *   **來源文件**: [`01-03-streaming-features.md`](./part1/01-03-streaming-features.md)
    *   **學習重點**:
        *   響應式中斷 (Responsive Interruption) 的使用者體驗價值。
        *   語音活動偵測 (VAD) 與輪替對話機制。
        *   FastAPI WebSocket 的上游/下游並行任務實作模式。

---

### 🔹 模組二：應用程式生命週期管理 (Lifecycle Mastery)
本模組深入探討如何正確管理連線生命週期，這是構建穩定應用的關鍵。

*   **單元 5: 四階段生命週期總覽**
    *   **來源文件**: [`02-00-app-lifecycle.md`](./part2/02-00-app-lifecycle.md)
    *   **學習重點**:
        *   掌握從「全域初始化」到「優雅終止」的四個階段。
        *   區分長期記憶 (ADK Session) 與短期快取 (Live API Session)。

*   **單元 6: Phase 1 & 2 - 初始化策略**
    *   **來源文件**: [`02-01-app-init.md`](./part2/02-01-app-init.md), [`02-02-app-run.md`](./part2/02-02-app-run.md)
    *   **學習重點**:
        *   建立可重用的 `Agent` 與 `SessionService`。
        *   實作「獲取或建立 (Get-or-Create)」模式以支援會話恢復。
        *   根據模型名稱動態配置 `RunConfig`。

*   **單元 7: Phase 3 - 事件迴圈實戰**
    *   **來源文件**: [`02-03-event-loop.md`](./part2/02-03-event-loop.md)
    *   **學習重點**:
        *   使用 `asyncio.gather` 實現上游與下游的並行處理。
        *   非阻塞式訊息發送與即時事件遍歷。

*   **單元 8: Phase 4 - 優雅終止**
    *   **來源文件**: [`02-04-queue-close.md`](./part2/02-04-queue-close.md)
    *   **學習重點**:
        *   理解 `LiveRequestQueue.close()` 的重要性。
        *   如何預防「殭屍會話 (Zombie Sessions)」導致的配額耗盡。
        *   使用 `finally` 區塊確保資源釋放。

---

### 🔹 模組三：上游通訊機制 (Upstream Mechanics)
本模組專注於如何將使用者端的多模態數據（文字、音訊、影像）正確傳送給 AI。

*   **單元 9: 上游任務設計**
    *   **來源文件**: [`03-00-upstream.md`](./part3/03-00-upstream.md)
    *   **學習重點**:
        *   `LiveRequestQueue` 的執行緒安全特性與單次使用原則。
        *   統一的訊息傳遞介面設計。

*   **單元 10: 文字互動機制**
    *   **來源文件**: [`03-01-send-content.md`](./03-01-send-content.md)
    *   **學習重點**:
        *   `send_content()` 的輪次 (Turn-based) 觸發邏輯。
        *   `Content` 與 `Part` 的結構封裝。

*   **單元 11: 即時多模態串流**
    *   **來源文件**: [`03-02-send-realtime.md`](./part3/03-02-send-realtime.md)
    *   **學習重點**:
        *   使用 `send_realtime()` 傳送持續資料流。
        *   音訊規格：16kHz PCM 分段策略。
        *   視覺規格：1 FPS JPEG 影格傳輸。

*   **單元 12: VAD 與控制訊號**
    *   **來源文件**: [`03-03-vad.md`](./part3/03-03-vad.md)
    *   **學習重點**:
        *   自動 VAD (預設) vs. 手動活動訊號 (Manual Signals) 的選擇。
        *   實作「一鍵通 (Push-to-talk)」模式的訊號時序。

*   **單元 13: 關閉訊號**
    *   **來源文件**: [`03-04-close.md`](./part3/03-04-close.md)
    *   **學習重點**:
        *   BIDI 模式下的手動關閉責任。
        *   關閉訊號在佇列與後端的傳遞路徑。

---

### 🔹 模組四：下游事件處理 (Downstream Processing)
本模組解析如何處理 AI 傳回的即時事件流，包括文字、音訊與工具請求。

*   **單元 14: 事件處理核心**
    *   **來源文件**: [`04-00-downstream.md`](./part4/04-00-downstream.md)
    *   **學習重點**:
        *   `run_live()` 非同步產生器的運作機制。
        *   `Event` 物件結構與作者語意 (Author Semantics)。

*   **單元 15: 文字事件與狀態標記**
    *   **來源文件**: [`04-01-text-event.md`](./part4/04-01-text-event.md)
    *   **學習重點**:
        *   解碼 `partial`, `turn_complete`, `interrupted` 標記。
        *   實作即時打字機效果與 UI 狀態切換。

*   **單元 16: 音訊事件處理**
    *   **來源文件**: [`04-02-audio-event.md`](./part4/04-02-audio-event.md)
    *   **學習重點**:
        *   Inline Data (即時播放) vs. File Data (持久化) 的區別。
        *   處理 24kHz PCM 輸出的採樣率陷阱。
        *   Base64 序列化的效能考量。

*   **單元 17: 逐字稿事件**
    *   **來源文件**: [`04-03-transcription.md`](./part4/04-03-transcription.md)
    *   **學習重點**:
        *   原生雙向逐字稿的優勢。
        *   處理 `input_transcription` 與 `output_transcription`。
        *   利用 `finished` 標記更新 UI 對話氣泡。

*   **單元 18: 工具執行編排**
    *   **來源文件**: [`04-04-tool-event.md`](./part4/04-04-tool-event.md)
    *   **學習重點**:
        *   ADK 的自動工具執行 (Auto-execution) 機制。
        *   一般工具、長時運行工具與串流工具 (Streaming Tools) 的實作。

*   **單元 19: 錯誤處理策略**
    *   **來源文件**: [`04-05-error-handler.md`](./part4/04-05-error-handler.md)
    *   **學習重點**:
        *   分辨 `SAFETY` (中斷) 與 `UNAVAILABLE` (重試) 錯誤。
        *   處理速率限制 (Rate Limit) 與連線逾時。

---

### 🔹 模組五：進階配置與戰略 (Advanced Configuration)
本模組探討如何透過 `RunConfig` 將 AI 代理程式從「聊天機器人」升級為「智慧代理」。

*   **單元 20: RunConfig 戰略總覽**
    *   **來源文件**: [`05-00-advance-runconfig.md`](./part5/05-00-advance-runconfig.md)
    *   **學習重點**:
        *   `RunConfig` 在對話初始化中的角色。
        *   BIDI 模式與 SSE 模式的戰略抉擇。

*   **單元 21: 回應模態決策**
    *   **來源文件**: [`05-01-response.md`](./part5/05-01-response.md)
    *   **學習重點**:
        *   TEXT 模式 (效能) vs. AUDIO 模式 (情感) 的取捨。
        *   原生音訊模型的模態限制。

*   **單元 22: 會話恢復機制**
    *   **來源文件**: [`05-02-session-resumption.md`](./part5/05-02-session-resumption.md)
    *   **學習重點**:
        *   跨越 10 分鐘連線限制的自動重連技術。
        *   恢復句柄 (Resumption Handle) 的運作原理。

*   **單元 23: 上下文視窗壓縮**
    *   **來源文件**: [`05-03-compaction.md`](./part5/05-03-compaction.md)
    *   **學習重點**:
        *   實現「無限時長對話」的滑動視窗策略。
        *   `trigger_tokens` 與 `target_tokens` 的參數調優。

*   **單元 24: 音訊模型架構選型**
    *   **來源文件**: [`05-04-audio-model.md`](./part5/05-04-audio-model.md)
    *   **學習重點**:
        *   Native Audio 架構的端到端優勢。
        *   Half-Cascade 架構的穩定性與工具支援。

*   **單元 25: 進階感知能力**
    *   **來源文件**: [`05-05-affective.md`](./part5/05-05-affective.md)
    *   **學習重點**:
        *   啟用主動性 (Proactivity) 實現預判需求。
        *   啟用情感對話 (Affective Dialogue) 實現同理心互動。

---

### 🔹 模組六：產業實戰場景 (Real-world Scenarios)
本模組透過具體的產業案例，展示技術如何轉化為商業價值。

*   **單元 26: 實戰應用總論**
    *   **來源文件**: [`06-00-scenario.md`](./part6/06-00-scenario.md)
    *   **學習重點**:
        *   從技術規格到商業場景的對照。
        *   跨模態融合的應用哲學。

*   **案例研究 1: 電商導購 (Shopper's Concierge)**
    *   **來源文件**: [`06-01-commerce.md`](./part6/06-01-commerce.md)
    *   **重點**: 視覺環境感知、模糊語意搜尋、深度研究代理。

*   **案例研究 2: 客服與技術支援**
    *   **來源文件**: [`06-02-customer-service.md`](./part6/06-02-customer-service.md)
    *   **重點**: 視訊分診、免持操作、即時中斷修正。

*   **案例研究 3: 遠距醫療與分診**
    *   **來源文件**: [`06-03-tele-health.md`](./part6/06-03-tele-health.md)
    *   **重點**: 情緒安撫 (情感對話)、患部影像分析 (1 FPS)。

*   **案例研究 4: 金融服務與財富管理**
    *   **來源文件**: [`06-04-finance.md`](./part6/06-04-finance.md)
    *   **重點**: 螢幕共享、即時市場模擬、串流工具監控。
