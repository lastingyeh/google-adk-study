歡迎來到這堂關於 **ADK 雙向串流 (Bidi-streaming)** 的戰略級配置課程。我是你們的技術導師。

在我們建構即時 AI 代理程式時，最核心的技術決策之一就是選擇適合的**音訊模型架構**。在 `RunConfig` 的配置脈絡下，選擇「原生音訊 (Native Audio)」或「半串聯 (Half-Cascade)」架構，將直接決定你的 AI 是僅僅在「讀稿」，還是真正具備「情感與感知」的對話夥伴。

---

### 📌 音訊模型架構學習地圖

1.  **核心架構定義**：端到端原生處理 vs. 混合式 TTS 處理。
2.  **關鍵特性對照**：自然度、語言偵測與功能支援。
3.  **進階功能專屬權**：主動性 (Proactivity) 與情感對話 (Affective Dialog)。
4.  **回應模態約束**：為什麼原生音訊模型「不支援」純文字模式？。
5.  **實戰配置邏輯**：如何透過代碼動態判定並配置 `RunConfig`。

---

### 一、 核心架構：原生音訊 vs. 半串聯

在 ADK 的架構中，這兩種模型處理音訊的方式有本質上的不同：

*   **原生音訊 (Native Audio)**：這是一種完全整合的**端到端**架構。模型直接理解音訊輸入並直接生成音訊輸出，不經過中間文字轉換。**這代表什麼？** AI 能保留語速、語調與情緒，實現極其流暢且自然的類人對話。
*   **半串聯 (Half-Cascade)**：這是一種混合架構。雖然音訊輸入是原生處理的，但回應會先生成文字，再透過文字轉語音 (TTS) 引擎合成為音訊。這種架構在生產環境中提供了更穩健的工具執行 (Tool execution) 能力。

#### 📊 架構對比與技術指標

| 特性                    | 原生音訊模型 (Native Audio)    | 半串聯模型 (Half-Cascade)        |
| :---------------------- | :----------------------------- | :------------------------------- |
| **運作原理**            | 直接音訊對音訊，無中間轉換     | 音訊輸入 -> 文字生成 -> TTS 輸出 |
| **語音自然度**          | 極高，具情感表現力與語調       | 穩定但具備成熟的 TTS 品質        |
| **回應模態 (Modality)** | **僅限 AUDIO**（文字需靠轉譯） | 支援 TEXT 與 AUDIO               |
| **語言處理**            | 自動偵測語言                   | 需手動配置語言代碼               |
| **進階功能**            | 支援主動性與情感對話           | 不支援主動性/情感功能            |

---

### 二、 場景驅動教學：架構選型實戰

作為導師，我將帶入三個實戰開發場景，協助你理解如何根據需求在 `RunConfig` 中做決定。

#### 💡 場景 1：高感性的電商客服或同理心助手
**提問：** 「如果我要建構一個能感知使用者沮喪情緒，並能用溫和語調給予安慰的客服機器人，該選哪種？」
**解析：**
**關鍵在於「情感對話 (Affective Dialog)」功能**。
*   這種功能目前**僅限原生音訊模型**支援。原生架構能偵測情緒線索並調整回應風格。
*   **決策**：選擇原生音訊模型。在 `RunConfig` 中必須啟用 `AUDIO` 模態，並開啟 `enable_affective_dialog=True`。

#### 💡 場景 2：追求極致效能的文字優先助理
**提問：** 「我的應用程式主要是文字聊天，但希望在需要時能快速切換到語音，我該注意什麼？」
**解析：**
**這代表你需要靈活的回應形式**。
*   原生音訊模型不支援 `RunConfig` 的 `TEXT` 回應模式，這會導致初始回應時間較慢。
*   **決策**：選擇半串聯模型。它支援 `response_modalities=["TEXT"]`，在僅限文字的用例中可實現更快的響應。

#### 💡 場景 3：需要極高工具執行可靠性的商業流程
**提問：** 「我的代理程式需要頻繁呼叫複雜的 API 工具，哪種架構比較保險？」
**解析：**
根據來源，**半串聯模型在生產環境中提供了更好的可靠性和更穩健的工具執行**。
*   **決策**：選擇半串聯模型。它利用成熟的 TTS 與文字生成邏輯，在處理函式呼叫 (Function Call) 時表現更為穩定。

---

### 三、 代碼即真理：RunConfig 的自動化配置

在實戰中，我們通常會根據模型名稱自動調整架構配置。以下是來源資料中 `bidi-demo` 的核心實作邏輯：

```python
# [導師點評]：這是在 Phase 2 (對話初始化) 中的關鍵動作。
# 我們透過檢測模型名稱中是否包含 "native-audio" 來切換 RunConfig 策略。

model_name = agent.model
is_native_audio = "native-audio" in model_name.lower() # [佐證點：140]

if is_native_audio:
    # 1. 原生音訊模型：強制要求 AUDIO 模式
    # [關鍵在於]：原生模型不支援文字模式，文字紀錄必須透過轉譯獲得。
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["AUDIO"], # 僅支援 AUDIO
        input_audio_transcription=types.AudioTranscriptionConfig(), # 必須啟用轉譯
        output_audio_transcription=types.AudioTranscriptionConfig(),
        session_resumption=types.SessionResumptionConfig(),
        # 僅原生模型支援的進階功能
        proactivity=types.ProactivityConfig(proactive_audio=True) if proactivity else None,
        enable_affective_dialog=affective_dialog if affective_dialog else None,
    )
else:
    # 2. 半串聯模型：預設使用 TEXT 以獲取最佳效能
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["TEXT"], # 為了效能，預設使用 TEXT
        input_audio_transcription=None,
        output_audio_transcription=None,
        session_resumption=types.SessionResumptionConfig(),
    )
```

---

### 四、 知識延伸與收斂

在更大的雙向串流背景下，選擇架構也意味著選擇了開發者的「控制邊界」：

1.  **語言偵測的便利性**：原生音訊模型會自動從背景中判斷語言，而半串聯模型則需要你手動在 `speech_config.language_code` 中配置。
2.  **語音庫的廣度**：原生音訊模型支援擴展語音清單，除了 8 種內建語音外，還能使用來自 TTS 服務的額外語音。
3.  **無障礙與對話歷史**：由於原生音訊模型僅輸出音訊，**務必啟用「音訊逐字稿」功能**，才能在不損失低延遲特性的情況下，獲得文字紀錄供 UI 顯示或歷史查詢。

**導師總結：**
原生音訊架構是為了追求「極致自然」而生，適合具備高度同理心的互動場景；半串聯架構則是為了「生產穩定與效能」而存在，適合需要頻繁工具調用的文字與語音混合應用。在你的 `RunConfig` 中，請務必根據模型名稱進行環境變數配置，以確保在切換平台（Gemini vs. Vertex AI）時能獲得最佳體驗。

#NativeAudio #HalfCascade #RunConfig #GeminiLiveAPI #AIAgentArchitecture