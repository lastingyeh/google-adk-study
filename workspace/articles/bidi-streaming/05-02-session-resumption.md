歡迎來到這堂技術進階課。我是你們的資深技術導師。

在 **ADK 雙向串流 (Bidi-streaming)** 的世界裡，連線的穩定性是決定使用者體驗（UX）是否流暢的生命線。今天我們要深入討論 **RunConfig** 配置中一個極其關鍵的功能：**會話恢復 (Session Resumption)**。這項技術解決了即時通訊中最令人頭痛的「連線中斷」問題，讓 AI 代理程式能像真人一樣，在網路波動後依然能接續之前的對話記憶。

---

### 📌 會話恢復 (Session Resumption) 學習地圖

1.  **連線 vs. 會話**：理解為什麼會話能跨越連線存在。
2.  **自動化重新連線機制**：ADK 如何透明化處理「10 分鐘連線限制」。
3.  **場景驅動教學**：透過三個開發實戰場景，掌握恢復邏輯。
4.  **邏輯具象化**：連線生命週期與恢復流程圖。
5.  **代碼即真理**：在 `RunConfig` 與伺服器端實作恢復配置。
6.  **知識收斂**：生產環境的最佳實踐與限制。

---

### 一、 核心概念：連線 (Connection) 與會話 (Session) 的本質區別

在討論恢復之前，我們必須釐清這兩個容易混淆的概念：

*   **連線 (Connection)**：這是 ADK 與 Live API 伺服器之間的實體 WebSocket 連結，屬於網路傳輸層。
*   **會話 (Session)**：這是由 Live API 後端維護的邏輯對話上下文，包含對話歷史、工具狀態與模型上下文。

**關鍵在於：** 雖然一個連線（WebSocket）可能會因為網路故障或平台限制而中斷，但「會話」可以透過恢復功能（Session Resumption）跨越多個連線而持續存在。這代表使用者不必在重新連線後重新解釋他們的意圖。

---

### 二、 場景驅動教學：為什麼我們需要會話恢復？

#### 💡 場景 1：跨越「10 分鐘連線障礙」的無限對話
**提問：** 「導師，我聽說 Live API 的 WebSocket 連線在 10 分鐘後會自動斷開？這是否代表我的語音對話助手不能服務超過 10 分鐘？」
**解析：**
**這代表什麼？** 如果你不啟用恢復功能，是的。但 **ADK 完全自動化了這一過程**。
*   當連線達到 10 分鐘限制時，ADK 會檢測到連線優雅關閉，並自動使用最近快取的「恢復句柄 (Resumption Handle)」透明地重新連線。
*   **價值**：對開發者來說是透明的，你的 `run_live()` 事件迴圈會無縫繼續，使用者完全不會察覺到連線曾經斷過。

#### 💡 場景 2：處理短暫的網路閃斷 (Network Jitter)
**提問：** 「如果使用者的手機進入電梯，導致 4G/5G 訊號斷開幾秒鐘，對話會遺失嗎？」
**解析：**
只要啟用了會話恢復，ADK 會嘗試自動修復連線。
*   **技術細節**：在整個會話期間，Live API 會持續傳送 `session_resumption_update` 訊息，ADK 會將最新句柄快取在 `InvocationContext` 中。
*   **結果**：一旦網路恢復，ADK 會立刻發起新連線並帶入舊句柄，對話歷史將完整保留。

#### 💡 場景 3：開發者的責任邊界
**提問：** 「既然 ADK 會自動處理重新連線，我還需要在 FastAPI 伺服器寫任何代碼嗎？」
**解析：**
注意，ADK 處理的是 **ADK 與 Live API 後端之間** 的 WebSocket 連線。
*   **您的責任**：您仍需負責管理 **使用者（瀏覽器）與您的伺服器之間** 的 WebSocket 連線。
*   **導師建議**：如果使用者與伺服器的連線斷了，您需要在用戶端實作重連邏輯（如 `app.js` 中的 `setTimeout` 重連模式）。

---

### 三、 邏輯具象化：自動重新連線流程

我們可以使用文字序列圖來解構這項技術的內部運作：

```text
[ADK 應用程式]          [ADK Runner/Runner]          [Live API 後端]
      |                      |                           |
      |--- run_live() ------>|                           |
      |                      |---- 建立 WebSocket ------>| (連線啟動)
      |                      |                           |
      |<-- 事件串流 ---------|<------- session_resumption_update (快取句柄)
      |                      |                           |
      |                      |---- [~10分鐘後] 優雅關閉 ----| (連線結束)
      |                      |                           |
      |                      |-- 使用快取句柄自動重連 ------>| (恢復會話)
      |                      |                           |
      |<-- 事件無縫繼續 ------|<------- 會話狀態保留 -------|
```

---

### 四、 代碼即真理：生產級 RunConfig 配置

在實務中，啟用此功能只需要在 `RunConfig` 中傳入一個配置物件。請看來源資料中 `main.py` 的精簡實作：

```python
# [導師點評]：這是 Phase 2 的核心配置。
# 我們透過 SessionResumptionConfig 啟用自動重新連線機制。

run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    # [關鍵在此]：啟用自動會話恢復。這讓 ADK 負責監控連線狀態與句柄快取。
    session_resumption=types.SessionResumptionConfig(),

    # 若需支援更長的對話，建議搭配「上下文視窗壓縮」
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=100000,
        target_tokens=80000
    ) if is_long_conversation else None,

    response_modalities=["AUDIO"],
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
)
```

---

### 五、 知識延伸與收斂：最佳實務建議

在更大的 RunConfig 配置背景下，會話恢復是邁向「生產級」應用的第一步。

*   **何時應啟用**：**強烈建議在所有生產應用程式中啟用**。它讓對話跨越 10 分鐘限制，處理網路中斷。
*   **配合上下文壓縮**：雖然恢復能解決「連線」時間限制，但不能解決「會話」本身的 Token 限制。若要實現真正無限時長的對話，請務必搭配 `context_window_compression` 使用。
*   **不適合的情況**：如果您的對話非常短（< 10 分鐘）且每一輪都是獨立的（無狀態互動），或者您正在開發環境中進行精確的單次回合除錯，則可以考慮停用。

**實戰總結：**
會話恢復功能是 ADK 為開發者提供的「防彈背心」。它將複雜的 WebSocket 重連與句柄管理封裝在 `RunConfig` 之後，確保了對話的連續性。記住，ADK 處理後端的穩定，而你則專注於處理前端使用者的重連感官體驗。

#SessionResumption #RunConfig #BidiStreaming #LiveAPI #AutoReconnect

**標籤：** #SessionResumption #BidiStreaming #RunConfig #ReliableAI #GeminiLiveAPI