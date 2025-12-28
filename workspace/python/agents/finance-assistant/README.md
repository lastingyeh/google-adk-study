# 教學 02：函式工具實作 (Finance Assistant)

函式工具教學的完整、可運作的實作。透過自訂的 Python 函式，將您的代理從一個對話者轉變為一個問題解決者，這些函式會根據使用者請求自動執行。

## 快速入門

```bash
# 設定與安裝
make setup

# 執行財務助理
make dev

# 執行綜合測試
make test

# 清理
make clean
```

## 這個代理的功能

- **個人財務助理**：計算複利、貸款支付和儲蓄目標
- **自動工具選擇**：LLM 根據使用者請求決定何時使用工具
- **並行工具執行**：ADK 自動同時執行多個工具以獲得更佳效能
- **真實世界計算**：準確的財務數學與人性化的解釋

## 專案結構

```
finance-assistant/
├── README.md                    # 本檔案
├── Makefile                     # 建置與測試指令
├── finance_assistant/           # 代理實作
│   ├── __init__.py             # Python 套件標記
│   ├── agent.py                # 包含 3 個財務計算工具的代理
│   └── .env.example            # 環境範本
├── tests/                       # 綜合測試套件
│   ├── __init__.py
│   ├── test_agent.py           # 代理設定測試
│   ├── test_tools.py           # 工具函式測試
│   ├── test_imports.py         # 匯入驗證測試
│   └── test_structure.py       # 專案結構測試
├── requirements.txt            # Python 依賴套件
└── parallel_demo/               # 進階並行執行展示
    ├── __init__.py
    ├── agent.py                # 並行工具呼叫範例
    └── .env.example
```

## 先決條件

- Python 3.9+
- Google API 金鑰（可於 [Google AI Studio](https://aistudio.google.com/app/apikey) 免費取得）

## 設定說明

1. **安裝依賴套件**：

   ```bash
   pip install -r requirements.txt
   ```

2. **設定 API 金鑰**：

   ```bash
   cp finance_assistant/.env.example finance_assistant/.env
   # 編輯 finance_assistant/.env 並加入您的 GOOGLE_API_KEY
   ```

3. **執行代理**：

   ```bash
   make dev
   ```

   然後在您的瀏覽器中開啟 <http://localhost:8000>

## 展示情境

### 基本財務計算

**複利**：

```text
使用者：如果我投資 10,000 美元，年利率 6%，為期 5 年，我將會有多少錢？

代理：讓我為您計算！

[工具呼叫: calculate_compound_interest(principal=10000, annual_rate=6, years=5)]

根據計算，如果您投資 10,000 美元，年利率 6%，每月複利計算，為期 5 年，您將大約有 13,488.50 美元。這表示您將賺取 3,488.50 美元的利息 - 還不錯！
```

**貸款支付**：

```text
使用者：一筆 300,000 美元的抵押貸款，利率 4.5%，為期 30 年，每月還款金額是多少？

代理：我將為您計算該抵押貸款的還款金額。

[工具呼叫: calculate_loan_payment(loan_amount=300000, annual_rate=4.5, years=30)]

對於一筆 300,000 美元的貸款，利率 4.5%，為期 30 年，您的每月還款金額為 1,520.06 美元。在貸款期間，您總共將支付 547,221.60 美元，其中 247,221.60 美元是利息。
```

**儲蓄目標**：

```text
使用者：我希望在 3 年內存下 50,000 美元作為頭期款。每個月需要存多少錢？

代理：很棒的目標！讓我為您計算每月所需的儲蓄金額。

[工具呼叫: calculate_monthly_savings(target_amount=50000, years=3)]

要在 3 年內達到 50,000 美元，年回報率為 5%，您需要每月儲蓄 1,315.07 美元。您總共將貢獻 47,342.52 美元，其餘部分來自投資回報。繼續努力！
```

### 並行工具執行展示

試試進階的並行執行範例：

```bash
make parallel-demo
```

**並行查詢**：

```text
比較這三個投資選項：
1. 10,000 美元，利率 5%，為期 10 年
2. 15,000 美元，利率 4%，為期 10 年
3. 12,000 美元，利率 6%，為期 10 年
```

**會發生什麼事**：

- Gemini 辨識出需要 3 個獨立的計算
- ADK 同時執行所有三個工具（非循序執行）
- 結果在約 0.5 秒內返回，而不是約 1.5 秒
- 代理提供比較分析

## 主要功能展示

- **函式工具**：一般 Python 函式變為 LLM 可呼叫的工具
- **自動工具選擇**：LLM 讀取 docstrings 並決定何時使用工具
- **並行執行**：透過 `asyncio.gather()` 同時執行多個工具
- **類型提示**：參數類型引導 LLM 工具使用
- **結構化回傳**：包含狀態和人類可讀報告的 Dict 格式
- **錯誤處理**：優雅的錯誤處理與有意義的訊息
- **真實世界用例**：實用的財務計算

## 開發指令

| 指令                  | 描述                                     |
| ----------------------- | ---------------------------------------------- |
| `make setup`            | 安裝依賴套件並設定環境                     |
| `make dev`              | 啟動 ADK 開發伺服器（主要代理）              |
| `make parallel-demo`    | 啟動 ADK 開發伺erv器（並行執行展示）        |
| `make test`             | 執行所有測試                                 |
| `make test-unit`        | 僅執行單元測試                             |
| `make test-tools`       | 測試財務計算函式                           |
| `make test-integration` | 執行整合測試                               |
| `make clean`            | 移除產生的檔案                             |
| `make help`             | 顯示所有可用指令                           |

## 測試

執行綜合測試套件：

```bash
make test
```

測試涵蓋：

- 代理設定與工具註冊
- 財務計算準確性
- 工具函式錯誤處理
- 匯入驗證
- 專案結構合規性
- 並行執行模式（當 API 金鑰可用時）

## 已實作的工具函式

### 1. `calculate_compound_interest()`

- **目的**：計算複利下的投資增長
- **公式**：`A = P(1 + r/n)^(nt)`
- **參數**：principal, annual_rate, years, compounds_per_year
- **回傳**：最終金額、賺取利息、格式化報告

### 2. `calculate_loan_payment()`

- **目的**：計算貸款/抵押貸款的每月還款金額
- **公式**：`M = P[r(1+r)^n]/[(1+r)^n-1]`
- **參數**：loan_amount, annual_rate, years
- **回傳**：每月還款金額、總支付金額、總利息

### 3. `calculate_monthly_savings()`

- **目的**：確定達到目標所需的每月儲蓄金額
- **公式**：`PMT = FV / [((1+r)^n - 1) / r]`
- **參數**：target_amount, years, annual_return
- **回傳**：每月儲蓄金額、總貢獻金額、賺取利息

## 進階功能

### 並行工具呼叫

當符合以下條件時，ADK 會自動並行執行多個工具：

- LLM 在單一回合中請求多個工具
- 工具是獨立的（沒有循序依賴）
- 使用 Gemini 2.5-flash 或 2.0-flash 模型

**效能**：3 個並行工具可提升 3 倍速度（0.5 秒 vs 1.5 秒）

### 工具設計最佳實踐

- **清晰的名稱**：`calculate_compound_interest` 而非 `calc_int`
- **全面的 Docstrings**：解釋何時及如何使用
- **類型提示**：引導 LLM 參數使用
- **結構化回傳**：`{"status": "success", "report": "..."}`
- **錯誤處理**：回傳錯誤 dicts，不要引發例外
- **專注的範圍**：一個函式 = 一個特定任務

## 疑難排解

### 代理未呼叫工具

- 檢查事件分頁 - Gemini 是否考慮了該工具？
- 驗證 docstring 是否清楚解釋了何時使用該工具
- 確保函式名稱符合使用者意圖

### 傳遞了錯誤的參數

- 檢閱類型提示和參數描述
- 在 docstrings 中加入範例
- 檢查參數名稱衝突

### 工具執行錯誤

- 在工具函式中加入 try/except 區塊
- 回傳錯誤狀態 dicts 而非引發例外
- 在整合前獨立測試工具

### 並行執行未運作

- 使用 Gemini 2.5-flash 或 2.0-flash 模型
- 確保工具是真正獨立的
- 檢查事件分頁是否有並行的 FunctionCall 事件


## 檔案概觀

- **`finance_assistant/agent.py`**：包含 3 個財務計算工具的主要代理
- **`parallel_demo/agent.py`**：進階並行工具執行範例
- **`tests/test_tools.py`**：驗證財務計算的準確性
- **`tests/test_agent.py`**：測試代理設定與工具註冊

## 效能說明

- **並行執行**：對於多個獨立計算，速度提升 3 倍
- **CPU 密集型**：Python GIL 限制了純 CPU 並行性，但 asyncio 有所幫助
- **I/O 密集型**：網路呼叫從並行執行中獲益最多
- **混合工作負載**：兩者結合可獲得最佳效能