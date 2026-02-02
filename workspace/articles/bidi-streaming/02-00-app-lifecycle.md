歡迎來到這份深度技術筆記。我是你們的資深技術導師，今天我們將聚焦於 **ADK 雙向串流 (Bidi-streaming)** 的核心骨架：**應用程式生命週期 (Application Lifecycle)**。

在開發即時 AI 代理程式時，生命週期的管理決定了系統的穩定性與資源效率。ADK 將複雜的 WebSocket 管理與狀態持久化整合進一個 **四階段生命週期** 中。理解這四個階段，能讓你從「寫出會動的代碼」跨越到「構建生產級應用」。

---

### 📌 ADK 雙向串流生命週期地圖

1.  **階段 1：全域初始化** —— 建立一次，全域共享的基礎設施。
2.  **階段 2：工作階段啟動** —— 為每個對話執行緒配置專屬資源。
3.  **階段 3：事件迴圈運作** —— 實戰中的「上游/下游」並行通訊模式。
4.  **階段 4：優雅終止** —— 資源清理與避免「殭屍會話」的關鍵。
5.  **核心架構對比** —— ADK Session 與 Live API Session 的長期 vs 短期策略。

---

### 一、 階段 1：應用程式初始化 (啟動時執行一次)

在這個階段，我們建立的是**無狀態且可重用**的組件。它們在應用程式啟動時載入，並在所有使用者連線之間共享。

*   **Agent**：定義代理程式的指令、工具與模型行為。
*   **SessionService**：負責跨對話儲存歷史紀錄。生產環境建議使用 `DatabaseSessionService` 或 `VertexAiSessionService`。
*   **Runner**：對話的執行環境，負責編排所有的串流邏輯。

#### 💡 場景驅動：資源共享
**問：** 「為什麼我們不在每次使用者連線時都建立一個新的 Agent 實例？」
**解析：** 關鍵在於效能與資源管理。Agent 本身是不帶對話狀態的 (Stateless)，它是定義 AI 個性的模板。將其全域化可以減少初始化開銷，並讓 Runner 能高效地編排多個連線。

---

### 二、 階段 2：對話執行緒初始化 (每個對話一次)

當使用者發起連線（例如透過 WebSocket）時，我們進入第二階段。這時的任務是為「這一次對談」量身打造環境。

1.  **獲取/建立 Session**：透過 `user_id` 與 `session_id` 識別對話。
2.  **配置 RunConfig**：宣告串行的行為（例如：使用音訊還是文字、是否啟動自動重連）。
3.  **建立 LiveRequestQueue**：這是通訊的專屬管道。**請注意：** 切勿在多個對話中重複使用隊列，否則會導致訊息順序混亂。

---

### 三、 階段 3：`run_live()` 雙向串流實戰

這是生命週期中最活躍的階段，體現了雙向串流與傳統模式的根本不同。這不再是「提問並等待」，而是並行的「說」與「聽」。

#### ⚡ 代碼即真理：上游與下游的並行舞步
在實作中，我們通常使用 FastAPI 與 WebSocket，並採用 `asyncio.gather` 來同時運行兩個非同步任務。

```python
# [導師點評]：這是 Phase 3 的核心架構。
# 我們必須並行處理「上游」(傳送給 AI) 與「下游」(接收 AI 回應)

async def upstream_task():
    """上游：從 WebSocket 接收並推入 LiveRequestQueue"""
    while True:
        message = await websocket.receive()
        if "bytes" in message:
            # 傳送音訊 Blob
            live_request_queue.send_realtime(types.Blob(data=message["bytes"], ...))
        elif "text" in message:
            # 傳送文字指令
            live_request_queue.send_content(types.Content(...))

async def downstream_task():
    """下游：從 run_live() 接收事件並推回 WebSocket"""
    # [關鍵在於]：run_live 是一個非同步產生器
    async for event in runner.run_live(..., live_request_queue=live_request_queue, ...):
        # 序列化事件為 JSON 並傳回客戶端
        await websocket.send_text(event.model_dump_json(exclude_none=True))

# 啟動並行任務
await asyncio.gather(upstream_task(), downstream_task())
```

---

### 四、 階段 4：終止 Live API 對話

當對話結束（使用者斷線或任務完成）時，我們必須進入清理程序。

*   **主動關閉**：呼叫 `live_request_queue.close()`。
*   **這代表什麼？** 這會向 Live API 發送一個結束訊號，讓後端乾淨地終止會話。
*   **如果不關閉會怎樣？** 來源資料明確警告：未呼叫 `close()` 會導致「殭屍會話」殘留在雲端，計入你的**並行配額**，直到超時為止，這可能導致新使用者無法連線。

---

### 五、 邏輯具象化：生命週期組件關係

為了強化記憶，我們可以用下表區分「長期持久性」與「短期串流」組件：

| 範疇 | 組件 | 持續時間 | 儲存層級 |
| :--- | :--- | :--- | :--- |
| **持久化記憶** | **ADK Session** | 數小時、數天或數月 | 透過 `SessionService` 儲存在資料庫 |
| **即時通訊** | **Live API Session** | 單次 `run_live()` 循環 (通常 < 15 分鐘) | 由 Live API 後端管理的短暫上下文 |
| **訊息緩衝** | **LiveRequestQueue** | 僅限單次連線 | 記憶體內的非同步隊列 |

---

### 💡 知識延伸與收斂

理解生命週期後，你會發現 ADK 的價值在於**平台抽象化**。同一套生命週期代碼，你可以在開發階段使用 **Gemini Live API** (快速原型)，並在生產階段無縫切換到 **Vertex AI Live API** (企業級穩定性)，而無需重寫對話邏輯。

**實戰總結：**
1.  **非同步是前提**：所有的生命週期操作（如 `run_live`, `get_session`）都必須在 `async` 上下文中運行。
2.  **確保清理**：永遠使用 `try/finally` 區塊來呼叫 `live_request_queue.close()`。
3.  **區分 Session**：ADK Session 是長期記憶，Live API Session 是短暫的對話快取。

#GoogleADK #BidiStreaming #SoftwareLifecycle #AIAgents #FastAPI