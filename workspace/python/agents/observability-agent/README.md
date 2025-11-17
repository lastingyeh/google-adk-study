# 教學 18：事件與可觀測性

為 Google ADK 代理程式提供全面的可觀測性實作，包含事件追蹤、指標收集與監控儀表板。

## 功能

- **事件追蹤**：監控所有代理程式的動作、工具呼叫與狀態變更
- **指標收集**：追蹤效能、錯誤與上報情況
- **即時警報**：針對特定的事件模式發出警報
- **客戶服務代理程式**：具備可觀測性的完整實作
- **全面測試**：49 個測試案例，涵蓋所有可觀測性功能

## 快速入門

```bash
# 設定環境
make setup

# 設定您的 Google API 金鑰
export GOOGLE_API_KEY=your_api_key_here

# 使用 ADK 網站介面執行代理程式
make dev

# 或執行示範情境
make demo
```

## 安裝

### 先決條件

- Python 3.10 或更高版本
- Google API 金鑰 (Gemini)

### 設定

```bash
# 安裝依賴套件
make setup

# 執行測試
make test

# 檢視測試覆蓋率
make coverage
```

## 使用方式

### 使用 ADK 網站介面執行

```bash
make dev
# 開啟 http://localhost:8000
# 從下拉式選單中選擇 "observability_agent"
# 嘗試範例查詢以查看事件追蹤
```

### 示範情境

`make demo` 指令會執行四個客戶服務情境：

1.  **訂單狀態查詢** - 帶有工具呼叫的簡單查詢
2.  **小額退款** - 低於門檻的退款 (已批准)
3.  **大額退款** - 超過門檻的退款 (已上報)
4.  **庫存檢查** - 產品可用性查詢

每個情境都會展示：
- 事件的建立與追蹤
- 工具呼叫的記錄
- 狀態管理
- 上報處理
- 綜合報告

### 範例查詢

```python
# 訂單狀態查詢
"我的訂單 ORD-001 的狀態是什麼？"

# 退款請求 (小額)
"我想要為訂單 ORD-002 申請 50 美元的退款"

# 退款請求 (大額 - 觸發上報)
"我需要為訂單 ORD-003 申請 150 美元的退款"

# 庫存檢查
"產品 PROD-B 有庫存嗎？"
```

## 事件追蹤

代理程式會追蹤所有互動：

### 事件類型

- **customer_query**：使用者請求
- **tool_call**：帶有參數的工具調用
- **agent_response**：代理程式回覆
- **escalation**：上報給主管的請求

### 收集的指標

- **總事件數**：所有產生的事件
- **工具呼叫**：使用的工具數量與類型
- **上報**：上報次數與原因
- **回應時間**：代理程式延遲指標
- **錯誤率**：工具與代理程式的錯誤

### 事件報告

會產生兩份綜合報告：

1.  **事件摘要報告**：
    -   依類型分類的總事件數
    -   工具使用統計
    -   上報摘要

2.  **詳細時間軸**：
    -   按時間順序的事件記錄
    -   完整的事件詳情
    -   工具參數與結果

## 專案結構

```
tutorial18/
├── observability_agent/
│   ├── __init__.py           # 套件初始化，匯出 root_agent
│   └── agent.py              # CustomerServiceMonitor 實作
├── tests/
│   ├── test_agent.py         # 代理程式設定測試
│   ├── test_events.py        # 事件追蹤測試
│   ├── test_imports.py       # 匯入驗證
│   ├── test_observability.py # 指標與記錄測試
│   └── test_structure.py     # 專案結構測試
├── Makefile                  # 開發指令
├── pyproject.toml            # 專案設定
├── requirements.txt          # Python 依賴套件
├── README.md                 # 本檔案
└── .env.example              # 環境變數範本
```

## 測試

### 執行所有測試

```bash
make test
```

### 測試覆蓋率

```bash
make coverage
```

### 測試結構

- **test_agent.py**：代理程式設定與初始化 (11 個測試)
- **test_events.py**：事件建立與追蹤 (8 個測試)
- **test_observability.py**：指標、記錄、警報 (18 個測試)
- **test_imports.py**：匯入驗證 (7 個測試)
- **test_structure.py**：專案結構 (5 個測試)

**總計**：49 個綜合測試 (100% 通過)

## 架構

### CustomerServiceMonitor

實作可觀測性的主要類別：

```python
class CustomerServiceMonitor:
    """具備全面事件監控的客戶服務。"""

    def __init__(self):
        # 事件儲存
        self.events: List[Dict] = []

        # 具備工具的客戶服務代理程式
        self.agent = Agent(...)

    async def handle_customer_query(self, customer_id, query):
        # 追蹤查詢、執行代理程式、記錄回應
        ...

    def get_event_summary(self) -> str:
        # 產生摘要報告
        ...

    def get_detailed_timeline(self) -> str:
        # 產生時間軸報告
        ...
```

### 可觀測性類別

1.  **EventLogger**：用於事件的結構化記錄
2.  **MetricsCollector**：效能指標追蹤
3.  **EventAlerter**：基於模式的即時警報

## 設定

### 環境變數

從範本建立 `.env` 檔案：

```bash
cp .env.example .env
```

必要變數：

```bash
GOOGLE_API_KEY=your_api_key_here
```

選用 (適用於 Vertex AI)：

```bash
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

## 最佳實踐

### 事件追蹤

✅ **應做**：
- 記錄所有關鍵的狀態變更
- 在事件中包含豐富的上下文
- 追蹤帶有參數的工具呼叫
- 對於有風險的操作使用上報機制

❌ **不應做**：
- 記錄敏感資料 (密碼、權杖)
- 建立沒有上下文的事件
- 忽略錯誤事件
- 略過上報規則

### 指標收集

✅ **應做**：
- 追蹤所有操作的延遲
- 監控錯誤率
- 設定警報門檻
- 隨時間匯總指標

❌ **不應做**：
- 阻塞指標收集
- 儲存無限制的指標
- 忽略效能下降
- 略過錯誤追蹤

## 疑難排解

### 事件未出現

**解決方案**：確保事件已正確建立：

```python
event = Event(
    invocation_id='inv-123',  # 必要
    author='agent_name',       # 必要
    content=types.Content(...) # 必要
)
```

### 狀態未持續

**解決方案**：使用 session 來管理狀態：

```python
session = Session()
result = await runner.run_async(query, agent=agent, session=session)
```

### ADK 網站代理程式未出現

**解決方案**：確保套件已安裝：

```bash
pip install -e .
adk web  # 而非 "adk web observability_agent"
```

## 資源

- [教學 18 文件](../../../notes/google-adk-training-hub/adk_training/18-events_observability.md)
- [ADK 事件文件](https://google.github.io/adk-docs/events/)
- [Google ADK Python](https://github.com/google/adk-python)

## 授權

Apache License 2.0

### 重點摘要
- **核心概念**：本專案旨在為 Google ADK 代理程式實作一個全面的可觀測性系統，涵蓋事件追蹤、指標收集與即時警報。
- **關鍵技術**：使用 Google ADK 的 `Event` 與 `EventActions` 來追蹤客戶查詢、工具呼叫、代理程式回應與上報流程。透過自訂的 `CustomerServiceMonitor` 類別來集中管理所有監控邏輯。
- **重要結論**：一個健全的可觀測性系統對於監控、除錯及優化 AI 代理程式至關重要。透過結構化的事件記錄與指標收集，開發者可以深入了解代理程式的行為與效能。
- **行動項目**：
    1.  設定 `GOOGLE_API_KEY` 環境變數。
    2.  執行 `make setup` 安裝依賴套件。
    3.  執行 `make dev` 啟動具備 Web UI 的代理程式，或執行 `make demo` 來觀看預設的客戶服務情境。
