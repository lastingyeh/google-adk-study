歡迎回到這份深度技術實作指南。我是你們的資深技術導師。在掌握了文字標記與音訊串流後，我們今天要探討的是 **ADK 雙向串流 (Bidi-streaming)** 下游處理中，最能提升使用者信任感與無障礙體驗的環節：**逐字稿事件 (Transcription Events)**。

在即時對話的脈絡下，逐字稿不僅是「語音轉文字 (STT)」的呈現，更是連繫使用者意圖與 AI 回應的視覺橋樑。ADK 內建了強大的轉錄機制，讓開發者無需額外整合第三方服務，即可在毫秒間捕捉對話的每一個字句。

---

### 📌 逐字稿事件處理學習地圖

1.  **內建轉錄的核心價值**：擺脫外部服務，實現原生低延遲。
2.  **雙向轉錄結構拆解**：`input_transcription` 與 `output_transcription` 的技術細節。
3.  **狀態管理的關鍵：Finished 標記**：如何正確處理部分（Partial）與最終文字。
4.  **多代理程式 (Multi-agent) 的強制邏輯**：為什麼在特定架構下轉錄無法被關閉。
5.  **UI 渲染實踐模式**：動態對話氣泡與「輸入中」指示器的同步邏輯。

---

### 一、 技術定位：為什麼我們需要原生逐字稿？

在更大的事件處理背景下，逐字稿事件是以獨立欄位（而非 `content` 組件）的形式存在於 `Event` 物件中。

**這代表什麼？**
傳統架構需要將音訊送往專門的 STT 服務，這會增加網路往返時間與系統複雜度。ADK 的解決方案是由 Live API 直接在產生音訊的同時提供逐字稿，這不僅確保了**極低的延遲**，還能實現以下價值：
*   **無障礙功能**：為聽障使用者提供即時字幕。
*   **對話日誌記錄**：無需額外後處理即可產生結構化的對話歷史。
*   **使用者確認**：讓使用者能即時確認 AI 是否正確聽懂了指令。

---

### 二、 場景驅動教學：逐字稿的實戰應用

我們透過三個實際開發場景，將逐字稿的處理邏輯具象化：

#### 💡 場景一：「AI 真的聽到了嗎？」——輸入轉錄 (Input Transcription)
**提問：** 「在使用者說話期間，我該如何讓 UI 顯示他們的語音內容，以減少等待的焦慮感？」
**解析：** 關鍵在於監聽 `event.input_transcription`。
*   **技術特點**：即使模型尚未開始回應，`input_transcription` 就會隨著使用者的語音流動而產生。
*   **作者語意**：**關鍵在此**，雖然轉錄由模型產生，但 ADK 會自動將輸入逐字稿事件的 `author` 標記為 `"user"`，確保對話紀錄的正確歸因。

#### 💡 場景二：處理「打字機」效果——部分與完成標記
**提問：** 「我收到的逐字稿文字會重複出現，我該怎麼處理這些碎片？」
**解析：** 這是因為轉錄具備 `finished` 標記。
*   **Finished = False**：代表這是**部分轉錄 (Partial)**，文字會持續累加，適合顯示「...」輸入指示器。
*   **Finished = True**：代表這是該回合的**最終轉錄**，此時應移除指示器並將氣泡轉為完成狀態。
*   **持久化重點**：在 ADK Session 中，僅會儲存 `finished=True` 的最終逐字稿，部分轉錄僅具暫時性。

#### 💡 場景三：多代理程式切換——隱藏的強制需求
**提問：** 「我明明在 `RunConfig` 中把逐字稿設為 `None`，為什麼還是收到了逐字稿事件？」
**解析：** **這代表你的代理程式具備子代理程式 (sub_agents)。**
*   在多代理程式架構下，ADK 會**自動啟用**輸入與輸出逐字稿，無論你的設定為何。這是因為系統需要這些「文字背景」在不同的代理程式之間傳遞對話狀態，否則代理程式轉移 (Transfer) 會失敗。

---

### 三、 邏輯具象化：逐字稿事件欄位對照表

| 欄位名稱               | 資料來源   | 內容定義                         | 作者歸屬 (Author)              |
| :--------------------- | :--------- | :------------------------------- | :----------------------------- |
| `input_transcription`  | 使用者語音 | 使用者說話內容的轉錄結果         | `"user"`                       |
| `output_transcription` | 模型語音   | 模型回應語音的轉錄結果           | 代理程式名稱 (如 `"my_agent"`) |
| `.text`                | 轉錄物件內 | 實際轉錄出的文字字串             | N/A                            |
| `.finished`            | 轉錄物件內 | 標示此片段是否為該回合的完整結果 | N/A                            |

---

### 四、 代碼即真理：從配置到 UI 渲染

我們必須分兩端來處理逐字稿：伺服器端的配置與用戶端的狀態轉換。

#### 1. 伺服器端：RunConfig 宣告
在 `bidi-demo` 的實作中，我們可以看到如何在 `RunConfig` 中啟動這兩項功能：

```python
# [導師點評]：在 Phase 2 初始化時，為原生音訊模型開啟雙向逐字稿
# 這消除了對外部 STT 服務的需求

run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"],
    # [關鍵在此]：開啟輸入與輸出逐字稿
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
    session_resumption=types.SessionResumptionConfig(),
)
```

#### 2. 用戶端：處理「部分」與「完成」狀態
JavaScript 用戶端必須精確判斷 `finished` 標記來更新 UI：

```javascript
// [導師點評]：這是處理輸出逐字稿的核心邏輯
if (adkEvent.outputTranscription && adkEvent.outputTranscription.text) {
    const transcriptionText = adkEvent.outputTranscription.text;
    const isFinished = adkEvent.outputTranscription.finished;

    // [這代表什麼？]：如果是第一次收到輸出逐字稿，
    // 代表模型開始說話，我們應強制完成所有仍活躍的輸入逐字稿氣泡。
    if (currentInputTranscriptionId != null && currentOutputTranscriptionId == null) {
        finalizeInputTranscription(); // 清除使用者的 "..." 指示器
    }

    if (isFinished) {
        // [關鍵在此]：Final 轉錄包含完整文字，替換整個氣泡內容並移除指示器
        updateMessageBubble(currentOutputElement, transcriptionText, false);
    } else {
        // [關鍵在此]：Partial 轉錄則持續附加文字，並保留打字指示器
        updateMessageBubble(currentOutputElement, transcriptionText, true);
    }
}
```

---

### 五、 知識延伸與收斂：防禦性編程建議

在處理逐字稿事件時，請務必記住以下「導師守則」：

1.  **兩層空值檢查**：對於逐字稿，務必先檢查物件是否存在 (`if event.input_transcription`)，再檢查文字是否非空 (`if text and text.strip()`)，以防止 `None` 導致的崩潰。
2.  **時序敏感度**：`partial=False` 的完整文字事件一律會在 `turn_complete=True` 事件**之前**產生。請以此邏輯來安排 UI 的最終歸檔。
3.  **效能考量**：逐字稿是輕量級的文字事件，不需要像音訊一樣考慮 Base64 的傳輸開銷，可以放心透過 WebSocket 傳送。

**實戰總結：**
逐字稿事件是 AI 代理程式的「文字倒影」。透過正確配置 `RunConfig` 並在下游精準捕捉 `finished` 標記，你可以構建出像真人對話一樣反應靈敏、且具備高度透明度的即時多模態應用。

#ADK #TranscriptionEvents #BidiStreaming #GeminiLiveAPI #RealTimeUI

**延伸思考**：當 `interrupted=True` 發生時，正在進行中的逐字稿會如何？根據來源，模型音訊快取會排空，此時下游應停止更新對應的 `output_transcription` 並將其標記為中斷。