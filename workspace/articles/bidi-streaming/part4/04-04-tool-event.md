歡迎回到這堂深度技術實作課。我是你們的資深技術導師。

在「下游（Downstream）」事件處理的脈絡下，除了文字與音訊，最能展現 **ADK 雙向串流 (Bidi-streaming)** 智慧價值的莫過於其對「工具」的編排能力。在原始 API 中，處理 Function Call 是一場惡夢，但在 ADK 的框架下，這被轉化為一種優雅的自動化流程。

---

### 📌 工具調用事件：自動化編排學習地圖

1.  **自動執行的底層機制**：為何我們不再需要手動處理「請求-執行-回傳」的循環？
2.  **場景驅動教學**：三種工具模式（普通、長時執行、串流）的實戰對話。
3.  **邏輯具象化**：工具調用類型與生命週期對比。
4.  **代碼即真理**：從工具定義到 `AsyncGenerator` 的實作註解。
5.  **知識延伸與收斂**：`InvocationContext` 在工具開發中的核心地位。

---

### 一、 自動執行的底層機制：解放開發者的雙手

在更大的事件處理背景下，ADK 的 `run_live()` 最強大的功能之一就是 **自動工具執行**。

**這代表什麼？** 如果直接使用原始 Gemini Live API，你必須手動接收模型的 `function_call`、在自己的伺服器執行工具、正確格式化 `function_response` 並將其傳回模型。這在串流情境中極其複雜，因為你還要同時處理進行中的音訊與文字流。

**關鍵在於**，ADK 完全抽象化了此過程。當你在代理程式上定義工具後，`run_live()` 會自動執行以下循環：
*   **(Detects) 偵測**：識別模型回傳的函式調用。
*   **(Executes) 並行執行**：為了效能，ADK 會並行處理工具請求。
*   **(Formats & Sends)**：自動按照 Live API 要求格式化回應並傳回模型。
*   **(Yields)**：將調用與回應事件都產生給應用程式，供 UI 顯示或日誌記錄。

---

### 二、 場景驅動教學：工具模式的實戰對話

我們透過三個開發場景，來看看三種不同的工具處理邏輯。

#### 💡 場景一：即時搜尋工具 (Simple Auto-Execution)
**提問：** 「如果使用者問：『現在 XYZ 股價是多少？』，我需要攔截事件來幫模型查資料嗎？」
**解析：**
不需要。在 `agent.py` 中定義好 Google 搜尋或自定義 API 後，ADK 會自動接手。
*   **技術表現**：下游會產生 `function_call` 事件，緊接著是 `function_response`。
*   **作者語意**：這些事件的 `author` 會是你的代理程式名稱，並持久化到 ADK Session 的工具執行歷史中。

#### 💡 場景二：需要人工審核的財務轉帳 (Long-running Tools)
**提問：** 「有些操作需要幾分鐘甚至人工確認，會卡住串流嗎？」
**解析：**
這時我們使用 **長時間執行工具 (Long-running Tools)**，標記 `is_long_running=True`。
*   **關鍵機制**：串流不會停止，`Event` 物件中的 `long_running_tool_ids` 欄位會追蹤待處理的操作。
*   **價值**：UI 可以顯示「正在處理中...」的指示器，而 AI 可以繼續與使用者聊天，直到工具完成。

#### 💡 場景三：股票價格持續監控 (Streaming Tools)
**提問：** 「我能讓工具在執行期間，持續把中間結果『餵』回給模型嗎？」
**解析：**
這就是 **串流工具 (Streaming Tools)** 的魅力。
*   **實作需求**：工具必須是 `async` 函數，且回傳類型為 `AsyncGenerator`。
*   **技術注入**：ADK 會自動為該工具建立一個專用的 `LiveRequestQueue` 並注入為 `input_stream` 參數。工具可以利用此佇列，將即時更新（如股價波動或視訊偵測結果）傳回模型，讓 AI 做出漸進式反應。

---

### 三、 邏輯具象化：工具調用類型對比表

| 特性         | 普通工具 (Simple)  | 長時執行工具 (Long-running) | 串流工具 (Streaming)      |
| :----------- | :----------------- | :-------------------------- | :------------------------ |
| **執行方式** | 立即、並行執行     | 非同步處理，不阻塞串流      | 持續產生中間結果          |
| **回傳類型** | 標準 Python 對象   | `Task` 或未來結果           | `AsyncGenerator`          |
| **通訊通道** | 單次回應循環       | 透過 ID 追蹤狀態            | 專用的 `LiveRequestQueue` |
| **適用場景** | 資料查詢、簡單計算 | 人工審核、繁重運算          | 股價監控、視訊流分析      |

---

### 四、 代碼即真理：定義與實作模式

根據來源資料，定義一個合格的工具必須遵循嚴格的非同步結構。

#### 1. 代理程式端的工具宣告
```python
# [導師點評]：在 Agent 定義時直接宣告工具。
# ADK 會從 Python 函式中自動產生 Schema，無需手動編寫 JSON。
agent = Agent(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    tools=[google_search, my_custom_tool], # [關鍵在此]：自動工具執行的起點
    instructions="You are a helpful assistant..."
)
```

#### 2. 串流工具的結構規範
```python
# [導師點評]：定義串流工具的兩大硬性規定：
# 1. 必須是 async 函數。
# 2. 必須回傳 AsyncGenerator。

async def monitor_stock_price(symbol: str) -> AsyncGenerator[str, None]:
    """監控股價變化並持續回傳。"""
    while True:
        price = await fetch_price(symbol)
        # [關鍵在於]：yield 的內容會被 ADK 捕獲並傳回模型
        yield f"Current price of {symbol} is {price}"
        await asyncio.sleep(60)
```

#### 3. 串流工具的生命週期管理
**重要提示**：對於影片或持續性的串流工具，你必須提供一個 `stop_streaming(function_name: str)` 函式，以便模型能明確停止操作。這些工具佇列在整個 `run_live()` 調用期間持續存在，並在結束時銷毀。

---

### 五、 知識延伸與收斂：開發者的核心武器

當你開發自定義工具或回呼時，**InvocationContext** 是你最重要的執行狀態容器。

*   **一個調用 = 一個上下文**：`InvocationContext` 在你呼叫 `run_live()` 時建立，隨對話從頭到尾隨行。
*   **工具開發者的權力**：透過此上下文，你的工具可以存取 `context.session.state`（持久性鍵值儲存）或將 `context.end_invocation` 設為 `True` 以立即強制終止對話。
*   **自動注入**：當模型調用串流工具時，ADK 會自動將正確的工具佇列注入為 `input_stream` 參數。

**實戰導向總結：**
在 ADK 的下游處理中，工具調用不再是孤立的請求。透過 **自動工具執行**，ADK 將複雜的「函式調用-執行-回應」邏輯轉化為透明的事件流。對於需要持續回饋的場景，利用 **Streaming Tools** 與專用的 `LiveRequestQueue` 配合，可以實現極具互動性的「主動式代理程式」體驗。

🏷️ `tool-call-events`, `auto-tool-execution`, `streaming-tools`, `adk-downstream`, `invocation-context`

**延伸思考**：在 `SequentialAgent` 工作流程中，工具執行如何跨代理程式保持連貫？由於 `InvocationContext` 跨越整個 `run_live()` 調用，工具執行的歷史紀錄會透過 `context.session.events` 完美保留。

---

[← 上一頁](./04-03-transcription.md) | [下一頁 →](./04-05-error-handler.md) | [課程首頁 ↩](../COURSE_PLAN.md)