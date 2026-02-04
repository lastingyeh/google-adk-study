歡迎回到這份深度技術實務課。我是你們的資深技術導師，在探討過文字事件標記後，今天我們要進入 **ADK 雙向串流 (Bidi-streaming)** 中最具感官互動性的領域：**音訊事件處理**。

在下游（Downstream）事件處理的背景脈絡下，音訊資料並非以單一形式存在，而是根據用途被拆解為兩條截然不同的路徑：用於亞秒級即時播放的 **內嵌資料 (Inline_data)**，以及用於長期歷史紀錄與回顧的 **檔案資料 (File_data)**,。理解這兩者的技術邊界，是從實驗室原型跨越到生產級語音代理程式的關鍵。

---

### 📌 音訊下游事件處理學習地圖

1.  **音訊資料的雙重形態**：解構 `inline_data`（即時性）與 `file_data`（持久性）。
2.  **技術規格與格式約束**：掌握 24kHz PCM 輸出與自動序列化機制。
3.  **場景驅動教學**：
    *   場景一：實現亞秒級即時語音播放（採樣率陷阱）。
    *   場景二：對話歷史的持久化儲存（`save_live_blob`）。
    *   場景三：處理「插嘴」中斷時的音訊緩衝清理。
4.  **效能優化與序列化**：解決 Base64 編碼帶來的傳輸開銷。

---

### 一、 邏輯具象化：音訊事件類型對比表

在 ADK 架構中，我們必須區分「耳朵聽到的」與「硬碟存下的」。以下是根據來源資料整理的差異化對照：

| 特性           | 內嵌資料 (Inline Data)              | 檔案資料 (File Data)                    |
| :------------- | :---------------------------------- | :-------------------------------------- |
| **傳輸內容**   | 原始音訊位元組 (`part.inline_data`) | 儲存在成品的檔案引用 (`part.file_data`) |
| **持久化狀態** | **暫時性**：不儲存至 ADK Session    | **持久性**：可存儲於工作階段歷史紀錄    |
| **主要用途**   | **即時播放**，追求極低延遲          | **回顧對話**、歷史重播或品質稽核        |
| **觸發條件**   | `response_modalities=["AUDIO"]`     | 需明確啟用 `save_live_blob=True`,       |

---

### 二、 場景驅動教學：將抽象事件轉化為實作體驗

#### 💡 場景一：為什麼 AI 的聲音聽起來像「花栗鼠」？
**提問：** 「導師，我收到音訊事件了，但我直接丟到播放器，AI 的聲音聽起來又快又尖，這是為什麼？」
**解析：** 這是新手最常遇到的**採樣率陷阱**。
*   **關鍵在於**：Live API 的輸入與輸出規格並不對稱。
*   **技術數據**：使用者輸入通常是 16kHz PCM，但**原生音訊模型 (Native Audio) 的輸出是 24,000 Hz (24kHz)**,。
*   **解決方案**：我們在建立用戶端的 `AudioContext` 時，務必指定 `sampleRate: 24000`，否則聲音會發生畸變。

#### 💡 場景二：如何實現「隔天還能聽」的對話歷史？
**提問：** 「使用者希望在對話結束後能下載或重聽錄音，我該從 `inline_data` 慢慢拼湊嗎？」
**解析：** 絕對不要這樣做。這代表你需要啟用 `file_data`。
*   **這代表什麼？** `inline_data` 是碎片化的，且為了效能考量，ADK 預設不會將其存入資料庫,。
*   **解決方案**：在 `RunConfig` 中開啟 `save_live_blob=True`,。ADK 會自動將音訊串流彙整成檔案並存入「成品 (Artifacts)」服務中，並在你的持久化 Session 中留下檔案引用，這才是正確的持久化路徑,。

#### 💡 場景三：處理「插嘴」時的音訊緩衝清理
**提問：** 「當使用者中斷 AI 時，AI 雖然停止生成了，但我的喇叭還在播放殘留的音訊塊，這很尷尬。」
**解析：** 這涉及到 `interrupted=True` 標記與用戶端緩衝區的管理,。
*   **技術行為**：當下游收到中斷事件時，模型的音訊快取會在後端被自動排空。
*   **我們的責任**：在用戶端收到此標記時，必須立即通知播放器清空本地環狀緩衝區（Ring Buffer），例如發送 `endOfAudio` 指令，徹底停止舊的回應播放,。

---

### 三、 代碼即真理：音訊下游處理實作

我們來看看來源資料中具備技術權威感的實作註解：

#### 1. 配置持久化音訊儲存
要在下游獲得 `file_data` 事件，我們必須在初始化時正確宣告 `RunConfig`：

```python
# [導師點評]：這是 Phase 2 的核心配置。
# 啟用 save_live_blob 後，音訊會被彙整並持久化到成品與 Session 服務中
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"], # 強制開啟音訊回應模式
    save_live_blob=True,           # 關鍵：開啟音訊持久化存儲
    # 同時建議開啟逐字稿，這會讓對話歷史具備文字搜尋能力
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
)
```

#### 2. 下游事件遍歷與序列化
我們利用 `run_live()` 產生器向下游分發事件：

```python
# [導師點評]：這是 Phase 3 的下游任務
# 關鍵在此：model_dump_json() 會將二進位的 bytes 欄位進行 Base64 編碼,
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config,
):
    # exclude_none=True 能有效縮減 JSON 體積，提升傳輸效率
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    await websocket.send_text(event_json)
```

#### 3. 用戶端 24kHz 播放處理 (JavaScript)
用戶端接收到 JSON 後，需將 `inline_data` 送往 24kHz 的播放器：

```javascript
// [導師點評]：建立 AudioContext 時必須指定 24000 採樣率
const audioContext = new AudioContext({ sampleRate: 24000 });

// [關鍵在此]：ADK 在反序列化時會自動將 Base64 轉回原始位元組
if (adkEvent.content && adkEvent.content.parts) {
    for (const part of adkEvent.content.parts) {
        if (part.inlineData) {
            // 送往 AudioWorklet 進行播放
            audioPlayerNode.port.postMessage(base64ToArray(part.inlineData.data));
        }
    }
}
```

✍️ 更多參考程式碼，請見 [`audio.js`](./codes/audio.js)

---

### 四、 知識延伸與收斂

在更大的「事件處理」脈絡下，音訊資料是頻寬消耗與系統資源的關鍵點。

*   **序列化開銷**：我們發現 `model_dump_json()` 將原始位元組轉為 Base64 時，會增加約 **133% 的傳輸開銷**,。
*   **效能優化建議**：在極端重視延遲的生產環境中，建議考慮使用 WebSocket 的**二進位框架 (Binary Frames)** 分開傳送音訊數據，這能節省顯著的頻寬,。
*   **自動解碼便利性**：當我們在 Python 程式碼中存取 `part.inline_data.data` 時，ADK 內部透過 Pydantic 已經自動完成了 Base64 解碼，我們拿到的是即用型的位元組。

**導師總結：**
`inline_data` 是為了讓代理程式「活起來」的動脈，強調低延遲與即時性,；而 `file_data` 是為了讓代理程式「有記憶」的基礎，強調持久化與回溯,。在開發時，請優先確保 24kHz 播放環境的正確性，並根據業務需求謹慎開啟 `save_live_blob` 的存儲開關，以平衡功能與存儲成本。

🏷️ `bidi-streaming`, `audio-events`, `inline-data`, `audio-persistence`, `native-audio`