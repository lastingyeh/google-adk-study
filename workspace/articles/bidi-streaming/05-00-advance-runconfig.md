歡迎來到這份深度技術指南。我是你們的資深技術導師，今天我們要探討的是 ADK 雙向串流 (Bidi-streaming) 架構中，最能體現「開發者控制力」的戰略核心：**RunConfig（配置與進階功能）**。

在更大的應用程式生命週期中，如果說 `Agent` 是靈魂，`Runner` 是身體，那麼 `RunConfig` 就是這組對話的「行為準則」與「超能力插件」。它不只是簡單的參數集合，而是決定了 AI 如何感知情緒、如何處理中斷，以及如何在長達數小時的對話中保持記憶。

---

### 📌 戰略級配置：RunConfig 學習地圖

1.  **戰略定位**：RunConfig 在生命週期「階段 2」的關鍵任務。
2.  **核心抉擇：BIDI vs. SSE 模式**：理解通訊協定的根本差異。
3.  **進階功能矩陣**：從模態控制到「無限會話」的技術實現。
4.  **場景驅動教學**：三種實戰配置場景與導師解析。
5.  **代碼即真理**：生產級 `RunConfig` 初始化實作點評。
6.  **知識收斂**：關鍵資源與實戰總結。

---

### 一、 戰略定位：定義對話的「物理定律」

在 ADK 的生命週期中，`RunConfig` 建立於 **「階段 2：對話執行緒初始化」**。

**這代表什麼？**
雖然 `Agent` 和 `Runner` 是啟動後全域共享的無狀態組件，但 **`RunConfig` 是對話特定的 (Session-specific)**。
*   **關鍵在於**：你可以為同一個代理程式配置不同的行為。例如：一位使用者可能偏好純文字互動，而另一位則需要具備情感感知的語音通話。這種靈活性讓你只需透過「宣告式配置」，就能將基礎設施開發減少數個月的工作量。

---

### 二、 核心抉擇：BIDI 模式與 SSE 模式

在配置 `RunConfig` 時，第一個戰略決策是選擇 `StreamingMode`。

| 特性         | StreamingMode.BIDI (雙向串流)           | StreamingMode.SSE (伺服器端串流)  |
| :----------- | :-------------------------------------- | :-------------------------------- |
| **底層協定** | WebSocket (Live API)                    | HTTP 串流 (標準 Gemini API)       |
| **通訊模式** | 真正的雙向通訊，可同時發送與接收        | 傳統「請求-回應」模式，單向資料流 |
| **關鍵能力** | 插嘴偵測、低延遲語音、視覺感知          | 文字對話、大上下文視窗 (1.5 Pro)  |
| **適用場景** | 即時語音 AI、個人購物管家、現場技術協助 | 文字聊天機器人、長文摘要          |

---

### 三、 場景驅動教學：進階功能實戰

透過以下三個場景，我們來解析 `RunConfig` 如何將抽象概念轉化為解決方案。

#### 💡 場景 1：原生音訊模型的「語音優先」配置
**問：** 「導師，我想使用具備同理心的語音代理程式，但我聽說原生音訊模型不支援文字模式？」
**解析：** 沒錯，這是模型架構的限制。
*   **關鍵在於**：原生音訊模型 (Native Audio) 直接處理音訊，不支援 `TEXT` 回應模態。
*   **解決方案**：在 `RunConfig` 中強制設定 `response_modalities=["AUDIO"]`，並啟用 `AudioTranscriptionConfig` 來獲取文字逐字稿以滿足無障礙需求。

#### 💡 場景 2：跨越「10 分鐘連線障礙」的無限對話
**問：** 「Live API 的 WebSocket 連線在 10 分鐘後會自動斷開，我該如何讓 AI 進行長達一小時的教學輔導？」
**解析：** 這需要 `Session Resumption`（會話恢復）與 `Context Window Compression`（上下文視窗壓縮）的組合拳。
*   **會話恢復**：啟用後，ADK 會自動快取「恢復句柄」，在斷線時透明地重新連線，使用者完全不會察覺。
*   **視窗壓縮**：當對話 Token 達到閾值時自動摘要，這能將會話持續時間延長至「無限時間」，消除硬性的時間上限。

#### 💡 場景 3：情感感知與主動性 (Proactivity)
**問：** 「我希望 AI 能像真人一樣，看到使用者沮喪時主動安慰，甚至主動提出建議。」
**解析：** 這需要啟用 `enable_affective_dialog` 與 `proactivity`。
*   **技術限制**：這些進階功能目前 **僅限於原生音訊模型**。
*   **行為模式**：AI 會偵測語調中的情緒線索並調整回應風格，甚至能在沒有明確提示的情況下主動提供後續資訊。

---

### 四、 代碼即真理：RunConfig 初始化範例

讓我們直接進入來源資料中的 `main.py` 實作。請注意這段代碼如何根據模型名稱自動調整 `RunConfig`：

```python
# [導師點評]：這是 Phase 2 的核心。
# 我們根據模型名稱動態調整 RunConfig，將平台差異抽象化。

model_name = agent.model
is_native_audio = "native-audio" in model_name.lower()

if is_native_audio:
    # 1. 配置原生音訊專用的進階功能
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["AUDIO"], # [關鍵] 原生音訊僅支援 AUDIO
        input_audio_transcription=types.AudioTranscriptionConfig(), # 啟用逐字稿
        output_audio_transcription=types.AudioTranscriptionConfig(),
        session_resumption=types.SessionResumptionConfig(), # 啟用自動重連

        # [導師點評]：啟用情感對話與主動性，賦予 AI 類人反應力
        proactivity=(
            types.ProactivityConfig(proactive_audio=True)
            if proactivity else None
        ),
        enable_affective_dialog=affective_dialog if affective_dialog else None,
    )
else:
    # 2. 配置半串聯模型 (Half-cascade)，優先考慮效能
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["TEXT"], # [關鍵] 半串聯優先使用 TEXT 模式
        session_resumption=types.SessionResumptionConfig(),
    )
```

---

### 五、 知識延伸與收斂

在配置 `RunConfig` 時，請務必記住以下關鍵資源與實戰策略：

1.  **會話持久化 (save_live_blob)**：若需要事後回顧音訊對話，必須設定為 `True`，這會將音訊串流彙整為檔案並儲存至工作階段歷史中。
2.  **自定義元數據 (custom_metadata)**：這是一個極其強大的工具，允許你將任意 JSON 數據附加到每個事件中，用於後續的分析、除錯或合規追蹤。
3.  **組合式工具調用 (support_cfc)**：如果你需要模型同時並行呼叫多個工具或進行工具鏈接，請啟用此實驗性功能（僅支援 Gemini 2.x 模型）。

**導師總結：**
`RunConfig` 是 ADK 雙向串流的指揮中心。透過精確配置，你可以讓同一個 `Agent` 在開發環境（Gemini Live API）與生產環境（Vertex AI Live API）之間切換而無需更改程式碼。掌握了 `RunConfig`，你就掌握了建構「生產級」AI 代理程式的鑰匙。

#RunConfig #BidiStreaming #LiveAPI #ContextCompression #AffectiveDialogue

**延伸閱讀**：若需深入瞭解 VAD (語音活動檢測) 的手動控制細節，請參閱《開發指南第 5 部分：語音活動檢測 (VAD)》。