# 教學 14：使用 Server-Sent Events (SSE) 的串流代理

此實作展示了如何使用 Google ADK v1.16.0 的真實串流 API 來實現即時串流回應，提供漸進式文本輸出以提升使用者體驗。

## 總覽

串流代理展示了如何實作漸進式文本輸出，讓回應在生成時即時顯示，模擬即時聊天介面中的串流行為。

## 功能

- **真實 ADK 串流**：使用 Google ADK v1.16.0 的真實串流 API 搭配 `Runner.run_async()`
- **Server-Sent Events**：使用 `StreamingMode.SSE` 進行 SSE 串流以獲得即時回應
- **會話管理 (Session Management)**：使用 `InMemorySessionService` 進行適當的對話上下文管理
- **工具整合**：提供用於串流分析的額外工具
- **綜合測試**：對所有功能進行完整的測試覆蓋
- **展示腳本**：來自教學的多個可運作範例
- **Web API 範例**：包含客戶端程式碼的 FastAPI SSE 端點
- **進階模式**：聚合、進度指示器、多重輸出、超時處理

## 快速入門

1. **設定環境**：
   ```bash
   make setup
   ```

2. **執行測試**：
   ```bash
   make test
   ```

3. **執行展示**：
   ```bash
   make demo
   ```

## 專案結構

```
tutorial14/
├── streaming_agent/           # 主要代理套件
│   ├── __init__.py           # 套件匯出
│   ├── agent.py              # 代理實作
│   └── .env.example          # 環境變數範本
├── demos/                    # 可運作的教學展示腳本
│   ├── basic_streaming_demo.py         # 基本串流範例
│   ├── streaming_modes_demo.py         # StreamingMode 設定
│   ├── streaming_chat_app.py           # 完整的聊天應用程式
│   ├── advanced_patterns_demo.py       # 4 種進階串流模式
│   ├── streaming_aggregator_demo.py    # 回應聚合
│   ├── fastapi_sse_demo.py             # FastAPI SSE 端點
│   ├── sse_client.html                 # 客戶端 JavaScript
│   └── streaming_tests_demo.py         # 綜合測試
├── tests/                    # 測試套件
│   ├── __init__.py
│   ├── test_agent.py         # 代理功能測試
│   ├── test_imports.py       # 匯入驗證測試
│   └── test_structure.py     # 專案結構測試
├── pyproject.toml            # 現代 Python 套件設定
├── requirements.txt          # 依賴項目
├── Makefile                 # 開發指令
└── README.md                # 本檔案
```

## 關鍵元件

### 代理設定

`root_agent` 的設定包含：
- **模型**：`gemini-2.0-flash` 以獲得快速回應
- **工具**：`format_streaming_info` 和 `analyze_streaming_performance`

### 串流函式

- `stream_agent_response()`：使用真實 ADK API 的核心串流函式，並具備備援模擬機制
- `get_complete_response()`：用於測試的非串流版本
- `create_demo_session()`：用於會話管理的佔位符

### 工具

1. **format_streaming_info**：提供關於串流功能的資訊
2. **analyze_streaming_performance**：分析串流效能特性

## 展示腳本

所有來自教學文件的程式碼片段和範例都已實作為可運作的展示腳本：

### 1. 基本串流展示 (`demos/basic_streaming_demo.py`)

展示使用 ADK 真實 API 的基本串流實作：

```bash
python demos/basic_streaming_demo.py
```

功能：
- 基本的 `Runner.run_async()` 用法
- 適當的會話管理
- 漸進式文本輸出
- 多個展示查詢

### 2. 串流模式展示 (`demos/streaming_modes_demo.py`)

顯示不同的 `StreamingMode` 設定：

```bash
python demos/streaming_modes_demo.py
```

展示：
- `StreamingMode.SSE` 用於 Server-Sent Events
- `StreamingMode.NONE` 用於阻塞式回應
- 設定差異與使用模式

### 3. 串流聊天應用程式 (`demos/streaming_chat_app.py`)

來自教學的完整互動式聊天應用程式：

```bash
# 互動模式
python demos/streaming_chat_app.py

# 或修改腳本以執行展示模式
```

功能：
- 包含會話管理的 `StreamingChatApp` 類別
- 互動式與展示對話模式
- 即時串流顯示
- 錯誤處理與優雅關閉

### 4. 進階模式展示 (`demos/advanced_patterns_demo.py`)

實作所有 4 種進階串流模式：

```bash
python demos/advanced_patterns_demo.py
```

展示的模式：
- **回應聚合**：在串流時收集完整回應
- **進度指示器**：在串流期間提供視覺回饋
- **多重輸出**：同時將區塊傳送到多個目的地
- **超時保護**：優雅地處理緩慢的回應

### 5. 串流聚合器展示 (`demos/streaming_aggregator_demo.py`)

顯示回應聚合技術：

```bash
python demos/streaming_aggregator_demo.py
```

功能：
- 手動聚合實作
- 區塊分析與統計
- 完整回應重建

### 6. FastAPI SSE 展示 (`demos/fastapi_sse_demo.py`)

使用 Server-Sent Events 串流的 Web API：

```bash
# 如有需要，安裝 FastAPI
pip install fastapi uvicorn

# 執行伺服器
uvicorn demos.fastapi_sse_demo:app --reload

# 在瀏覽器中訪問：
# http://localhost:8000/docs     - API 文件
# http://localhost:8000/client   - 測試客戶端介面
```

功能：
- 使用 SSE 的 FastAPI `StreamingResponse`
- RESTful 聊天端點
- 內建 HTML 測試客戶端
- 用於 Web 應用程式的 CORS 標頭

### 7. SSE 客戶端 (`demos/sse_client.html`)

用於測試 SSE 端點的客戶端 JavaScript：

```bash
# 在瀏覽器中開啟或使用網頁伺服器提供服務
python -m http.server 8080
# 然後訪問：http://localhost:8080/demos/sse_client.html
```

功能：
- 即時 SSE 連線處理
- 漸進式訊息顯示
- 錯誤處理與重新連線
- 簡潔、響應式的 UI

### 8. 綜合測試 (`demos/streaming_tests_demo.py`)

展示串流測試模式的單元測試：

```bash
python -m pytest demos/streaming_tests_demo.py -v
```

測試覆蓋範圍：
- 基本串流功能
- 不同的串流模式
- 錯誤處理與超時
- 並發會話測試
- FastAPI 端點模擬

## 使用範例

### 基本串流

```python
from streaming_agent import stream_agent_response

async def chat():
    print("使用者: 你好！")
    print("Agent: ", end="", flush=True)

    async for chunk in stream_agent_response("你好！"):
        print(chunk, end="", flush=True)

    print()
```

### 完整回應

```python
from streaming_agent import get_complete_response

response = await get_complete_response("解釋量子計算")
print(response)
```

## 測試

執行綜合測試套件：

```bash
make test
```

測試涵蓋：
- 代理設定與建立
- 串流功能模擬
- 工具函式行為
- 匯入驗證
- 專案結構合規性

## 開發

### 可用的 Make 指令

- `make setup` - 安裝依賴與套件
- `make test` - 執行測試套件
- `make demo` - 執行串流展示
- `make clean` - 移除快取檔案

### 執行測試

```bash
# 執行所有測試
pytest tests/ -v

# 執行並計算覆蓋率
pytest tests/ --cov=streaming_agent --cov-report=html

# 執行特定測試檔案
pytest tests/test_agent.py
```

## API 參考

### 核心函式

#### `stream_agent_response(query)`

為查詢串流代理回應（模擬）。

**參數：**
- `query` (str): 使用者查詢

**回傳：** AsyncIterator[str] - 文本區塊

#### `get_complete_response(query)`

取得完整回應（非串流）。

**參數：**
- `query` (str): 使用者查詢

**回傳：** str - 完整回應文本

#### `create_demo_session()`

建立一個新的會話佔位符。

**回傳：** None

### 工具

#### `format_streaming_info()`

取得關於串流功能的資訊。

**回傳：** 包含串流資訊的字典

#### `analyze_streaming_performance(query_length=100)`

分析串流效能特性。

**參數：**
- `query_length` (int): 用於分析的查詢長度

**回傳：** 包含效能分析的字典

## 實作說明

此實作使用 Google ADK v1.16.0 的真實串流 API：

- **真實串流 API**：使用 `Runner.run_async()` 搭配 `StreamingMode.SSE` 以實現實際的漸進式輸出
- **會話管理**：使用 `InMemorySessionService` 進行適當的對話上下文管理
- **備援機制**：如果真實串流失敗，則退回至模擬串流
- **教育重點**：展示真實與備援串流模式
- **可測試性**：易於使用模擬的 ADK 元件進行測試

## 相關教學

- **教學 01**：Hello World 代理 - 基本代理設定
- **教學 02**：函式工具 - 工具整合
- **教學 13**：程式碼執行 - 進階代理模式

## 貢獻

1. 遵循 `tests/` 中的測試模式
2. 新增功能時需附上對應的測試
3. 若有任何變更，請更新文件
4. 提交前確保所有測試皆通過

## 授權

此實作為 ADK 訓練儲存庫的一部分。

---

### 重點摘要
- **核心概念**：此專案展示如何使用 Google ADK v1.16.0 的真實串流 API 建立一個串流代理 (Streaming Agent)，以實現漸進式的文本輸出，模擬即時聊天介面的使用者體驗。
- **關鍵技術**：
    - Google ADK v1.16.0 (`Runner.run_async()`)
    - Server-Sent Events (SSE) (`StreamingMode.SSE`)
    - FastAPI (`StreamingResponse`)
    - 會話管理 (Session Management) (`InMemorySessionService`)
    - Python `asyncio`
- **重要結論**：透過 ADK 的串流 API 和 SSE 技術，開發者可以有效地建立即時互動的 AI 代理，提供更佳的使用者體驗。專案提供了從基本到進階的完整範例，涵蓋了串流、測試、Web API 整合等多個方面。
- **行動項目**：
    1.  執行 `make setup` 安裝環境依賴。
    2.  執行 `make test` 進行測試。
    3.  執行 `make demo` 觀看基本串流展示。
    4.  探索 `demos/` 目錄下的各個進階範例，了解不同的串流模式與應用。