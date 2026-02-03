歡迎回到這堂深度技術實作課。我是你們的資深技術導師。

在 ADK 雙向串流 (Bidi-streaming) 的應用開發中，**`RunConfig`** 是決定代理程式「性格」與「溝通方式」的指揮中心。其中最基礎卻也最關鍵的戰略決策，就是 **「回應模式 (Response Modalities)」** 的選擇：我們究竟該讓 AI 傳回 **文字 (TEXT)** 還是 **音訊 (AUDIO)**？

這不只是介面呈現的問題，更涉及到模型架構的底層約束與使用者體驗的設計。

---

### 📌 戰略級配置：回應模式學習地圖

1.  **回應模式的核心定義**：理解 TEXT 與 AUDIO 的功能定位。
2.  **模型架構的硬性約束**：為什麼「原生音訊模型」與「半串聯模型」的選擇不同？
3.  **場景驅動教學**：透過三個實戰場景，決定最佳的回應策略。
4.  **邏輯具象化**：回應模式與模型架構相容性矩陣。
5.  **代碼即真理**：在實戰中動態配置 `RunConfig`。

---

### 一、 核心定義：回應模式的「單一選擇」規則

在 `RunConfig` 中，`response_modalities` 參數控制模型生成輸出的方式。

**關鍵在於：** 雖然 Live API 支援多模態輸入（您可以同時發送文字、音訊與影像），但在 **輸出（回應）** 端，每個會話 (Session) 被限制為 **只能選擇一種回應模式**。

**這代表什麼？**
一旦對話初始化完成，您就無法在會話中途切換型態。這就像一場通訊：您必須在開始前決定這是一場「簡訊對話」還是「語音通話」。

*   **TEXT 模式**：模型回傳文字 Token，適用於傳統聊天機器人或效能導向的應用。
*   **AUDIO 模式**：模型回傳原始音訊位元組 (Raw bytes)，適用於亞秒級延遲的類人對話。

---

### 二、 場景驅動教學：選型標準與解決方案

透過「提問」與「解析」的對話，我們來看看如何根據需求進行配置。

#### 💡 場景 1：追求極致反應速度的文字助理
**提問：** 「老師，如果我的應用主要是文字聊天，但我偶爾想看到 AI 的回應速度變快，我該怎麼選？」
**解析：**
**這代表您應該選擇 TEXT 模式。** 對於半串聯模型 (Half-cascade) 來說，TEXT 模式通常能提供更好的效能。
*   **關鍵在於：** 文字傳輸的 Payload 遠小於音訊，且不需要音訊解碼時間。
*   **決策建議：** 若使用 `gemini-1.5` 系列模型，必須使用 `TEXT` 並搭配 `StreamingMode.SSE`。

#### 💡 場景 2：自然情感豐富的語音管家
**提問：** 「我想要做一個像真人一樣有情感起伏的語音助手，該選哪種模式？」
**解析：**
**您必須選擇 AUDIO 模式。** 這是發揮原生音訊模型 (Native Audio) 全部價值的唯一路徑。
*   **關鍵在於：** 原生音訊模型（如 `gemini-2.5-flash-native-audio`）不支援文字回應模式。它們直接生成音訊，保留了語調與情緒線索。

#### 💡 場景 3：語音優先但需要文字紀錄的無障礙應用
**提問：** 「如果模型只能回傳音訊（AUDIO），但我的使用者需要即時字幕或對話歷史紀錄怎麼辦？」
**解析：**
這就是 **「音訊逐字稿 (Audio Transcription)」** 進階功能的用武之地。
*   **解決方案：** 在 `RunConfig` 中設定 `response_modalities=["AUDIO"]`，同時啟用 `output_audio_transcription`。
*   **這代表什麼？** 模型會開口說話，同時 API 會在背景自動將語音轉成文字並以獨立事件傳回給您。

---

### 三、 邏輯具象化：回應模式與模型相容性矩陣

為了強化視覺記憶，我為大家整理了這份配置對照表：

| 特性                   | TEXT 模式              | AUDIO 模式                |
| :--------------------- | :--------------------- | :------------------------ |
| **主要功能**           | 生成文字區塊           | 生成原始 PCM 音訊 (24kHz) |
| **支援模型：原生音訊** | ❌ 不支援               | ✅ 必須使用 (預設值)       |
| **支援模型：半串聯**   | ✅ 支援 (效能較佳)      | ✅ 支援 (使用 TTS 生成)    |
| **支援模型：1.5 系列** | ✅ 支援 (僅限 SSE 模式) | ❌ 不支援 Live API 音訊    |
| **中斷處理**           | 支援 (文字截斷)        | 支援 (音訊快取排空)       |
| **無障礙方案**         | 直接顯示文字           | 需開啟「音訊逐字稿」      |

---

### 四、 代碼即真理：生產級 RunConfig 初始化

在實戰中，我們通常會根據所選模型的名稱來自動決定回應模式。請看來源資料中 `bidi-demo` 的核心實作：

```python
# [導師點評]：這裡展示了 Phase 2 的自動化配置策略。
# 關鍵在於：檢測模型名稱中是否包含 "native-audio"。

model_name = agent.model
is_native_audio = "native-audio" in model_name.lower()

if is_native_audio:
    # 1. 原生音訊模型：強制使用 AUDIO 模式
    response_modalities = ["AUDIO"]

    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=response_modalities,
        # [關鍵點]：因為是 AUDIO 模式，必須開啟逐字稿功能以獲取文字
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        session_resumption=types.SessionResumptionConfig(),
        # 僅原生模型支援的情感對話功能
        enable_affective_dialog=affective_dialog if affective_dialog else None,
    )
else:
    # 2. 半串聯模型：預設使用 TEXT 模式以獲取最佳效能
    response_modalities = ["TEXT"]

    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=response_modalities,
        input_audio_transcription=None,
        output_audio_transcription=None,
        session_resumption=types.SessionResumptionConfig(),
    )
```

---

### 💡 知識延伸與收斂

在配置回應模式時，請記住以下三條「導師守則」：

1.  **預設行為警示**：如果您在 `RunConfig` 中遺漏了 `response_modalities`，ADK 會自動預設為 `["AUDIO"]`。如果您正在建構純文字機器人，請務必明確宣告 `["TEXT"]`。
2.  **輸入不限**：回應模式只限制「AI 如何說」，不限制「使用者如何給」。無論輸出是文字還是音訊，您的 `LiveRequestQueue` 始終可以同時接收文字、音訊與影像輸入。
3.  **成本與配額**：AUDIO 模式通常比 TEXT 模式消耗更多頻寬與配額，且對連線持續時間有較嚴格的限制（例如 Gemini Live API 的 15 分鐘/2 分鐘上限）。

**總結：**
`RunConfig` 的回應模式是串流應用程式的基石。文字模式（TEXT）帶來效率與精準；音訊模式（AUDIO）則帶來情感與自然的類人體驗。根據您的產品定位選擇合適的模態，並善用逐字稿功能來彌補 AUDIO 模式下的文字缺失。

#ResponseModalities #RunConfig #NativeAudio #BidiStreaming #GeminiLiveAPI