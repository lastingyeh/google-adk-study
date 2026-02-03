歡迎來到這堂深度技術課程。我是你們的資深技術導師，在探討過如何將訊息送往 AI（上游）後，今天我們要進入雙向串流架構中最具動態性的部分：**事件處理 (Downstream)**。

在 ADK 的架構中，「下游 (Downstream)」代表從 AI 代理程式流向使用者的資訊流。這不再是傳統 API 傳回的一個完整 JSON 包，而是一系列即時產生的**事件 (Events)**。這些事件包含了文字碎片、音訊區塊、逐字稿，甚至是 AI 想要執行工具的請求。

---

### 📌 下游事件處理學習地圖

1.  **核心指揮家：`run_live()`** —— 理解非同步產生器的運作本質。
2.  **Event 類別解構**：掌握 Pydantic 模型的關鍵欄位與作者語意。
3.  **對話流控制標記**：深潛 `partial`、`interrupted` 與 `turn_complete`。
4.  **自動工具執行**：ADK 如何在下游流程中靜默處理 Function Call。
5.  **實戰序列化策略**：如何優雅地將事件推向 Web 用戶端。

---

### 一、 核心機制：`run_live()` 的非同步美學

下游處理的起點是 `run_live()` 方法。這是一個**非同步產生器 (Async Generator)**，它在事件產生時立即輸出，無需緩衝或輪詢。

**這代表什麼？**
當 AI 開始思考或說話時，事件會「滴流」出來。我們的應用程式不需要等待 AI 講完一整句話，就能即時更新 UI。

#### ⚡ 代碼即真理：下游任務的實作架構
以下是來源資料中 `bidi-demo` 的核心下游處理邏輯：

```python
# [導師點評]：這是 Phase 3 的下游核心。
# 我們使用 async for 遍歷產生器，這確保了低延遲的即時傳遞。

async def downstream_task() -> None:
    """從 run_live() 接收 Events 並發送到 WebSocket。"""
    logger.debug("下游任務啟動，呼叫 runner.run_live()")

    # run_live() 會隨著對話展開持續產生 Event 物件
    async for event in runner.run_live(
        user_id=user_id,
        session_id=session_id,
        live_request_queue=live_request_queue,
        run_config=run_config,
    ):
        # [關鍵在於]：序列化。exclude_none=True 能大幅縮減網路傳輸量
        event_json = event.model_dump_json(exclude_none=True, by_alias=True)
        logger.debug(f"[SERVER] Event: {event_json}")

        # 將事件即時推向前端 WebSocket
        await websocket.send_text(event_json)

    logger.debug("run_live() 產生器已完成")
```


---

### 二、 邏輯具象化：Event 物件的關鍵組成

ADK 的 `Event` 類別是一個統一的容器，它將不同性質的資訊標準化。

| 事件類型          | 內容與用途                                 | 是否持久化至 Session？        |
| :---------------- | :----------------------------------------- | :---------------------------- |
| **文字事件**      | 模型的文字回應碎片。                       | 是（僅限最終合併內容）        |
| **音訊 (Inline)** | 即時播放的原始音訊位元組 (`inline_data`)。 | **否**（具暫時性）            |
| **音訊 (File)**   | 儲存在成品中的音訊檔案引用 (`file_data`)。 | 是（需啟用 `save_live_blob`） |
| **逐字稿**        | 使用者與模型的語音轉文字結果。             | 是（僅限最終逐字稿）          |
| **工具調用**      | 模型請求執行的函式資訊。                   | 是（以維護工具執行歷史）      |
| **中繼資料**      | Token 使用量與權杖計數。                   | 是（用於成本監控）            |

**關鍵點在於作者語意 (Author Semantics)**：在下游事件中，`event.author` 不會只是字面上的 "model"。如果是模型回應，作者會顯示為**代理程式名稱**（如 "my_agent"）；如果是使用者音訊的逐字稿，作者則會被歸因為 "user"。

---

### 三、 場景驅動教學：掌握對話控制標記

要建立類人的互動體驗，你必須精通三個標記：`partial`、`interrupted` 與 `turn_complete`。

#### 提問：「如果 AI 正在講話，使用者突然插嘴問問題，下游會發生什麼？」
**解析：**
1.  **插嘴偵測**：ADK 會偵測到上游新輸入，並在下游產生一個 `interrupted=True` 的事件。
2.  **技術行動**：這代表什麼？這是一個訊號，告訴你的 UI 必須立即停止呈現當前輸出（如停止播放音訊或清除輸入指示器）。
3.  **狀態清理**：此時模型的音訊快取會被自動排空 (Flush)。

#### 提問：「為什麼我們需要區分 `partial`？」
**解析：**
*   `partial=True`：代表這只是回應的一部分（增量區塊），用於即時串流顯示。
*   `partial=False`：代表這是目前為止的**完整合併文字**。如果你不需要即時刷新，只需監聽 `partial=False` 即可獲得正確的段落內容。

---

### 四、 核心優勢：自動工具執行 (Auto Tool Execution)

下游流程中最讓開發者省心的功能就是**自動化工具編排**。

在原始 API 中，你必須手動接收 `function_call`、執行它、再傳回 `function_response`。但在 ADK 的下游流程中：
*   **自動偵測**：ADK 在 `run_live()` 內部會偵測到模型請求工具。
*   **並行執行**：它會自動執行你註冊的工具並獲得結果。
*   **透明回傳**：ADK 會自動將回應發回模型，而你的 `run_live()` 迴圈只需坐收產生的工具執行事件（僅供日誌或 UI 顯示使用）。

---

### 五、 知識延伸與收斂

處理下游事件時，效能與清理是成功的關鍵。

**實戰導向總結：**
*   **序列化優化**：二進位音訊在轉為 JSON 時會增加約 33% 的開銷。在生產環境中，建議考慮 WebSocket 二進位框架來分離音訊數據。
*   **正確關閉**：`run_live()` 的結束可能源於手動關閉、代理程式任務完成或逾時。無論原因為何，務必在 `finally` 區塊中執行資源清理。
*   **錯誤處理**：遇到 `SAFETY` 或 `MAX_TOKENS` 等錯誤時，應使用 `break` 終止迴圈；遇到 `UNAVAILABLE` 等暫時性問題則可考慮 `continue` 以等待恢復。

透過掌握下游事件處理，你賦予了代理程式「表達」的能力，並能以極高的精準度控制使用者體驗的每一個瞬間。

#ADKDownstream #RunLiveEvents #ReactiveUI #AutoToolExecution #BidiStreaming

**更多資源**：
*   關於 `Event` 類別的完整定義，請參閱《第 3 部分：Event 類別》。
*   關於如何配置 RunConfig 以調整回應模態，請參閱《第 4 部分：理解 RunConfig》。