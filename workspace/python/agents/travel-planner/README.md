# 教學 05：平行處理 - 旅遊規劃系統

本實作展示了 ADK 中的 **ParallelAgent（平行代理）** 模式和 **扇出/聚合（fan-out/gather）** 技術，用於並行執行。旅遊規劃器同時搜尋航班、飯店和活動，然後將結果合併成完整的行程。

## 概述

旅遊規劃系統展示：

- **ParallelAgent（平行代理）**：多個代理的並行執行
- **扇出/聚合模式**：平行資料收集 + 順序合成
- **狀態管理**：平行和順序代理之間的資料流
- **實際效能**：比順序執行快 3 倍

## 架構

```
text
使用者查詢 → ParallelAgent（3 個並行搜尋）
         ├─ 航班搜尋器 → state['flight_options']
         ├─ 飯店搜尋器 → state['hotel_options']
         └─ 活動搜尋器 → state['activity_options']
         ↓
      SequentialAgent（合併結果）
         ↓
      行程建構器 → 最終旅遊行程
```

## 快速開始

1. **安裝相依套件：**

   ```bash
   make setup
   ```

2. **設定 API 金鑰：**

   ```bash
   cp travel_planner/.env.example travel_planner/.env
   # 編輯 travel_planner/.env 並新增你的 Google AI API 金鑰
   ```

3. **啟動開發伺服器：**

   ```bash
   make dev
   ```

4. **開啟 [http://localhost:8000](http://localhost:8000)** 並選擇 "travel_planner"

## 範例提示

嘗試這些提示來查看平行處理的實際運作：

- `"規劃巴黎 3 日遊"`
- `"紐約週末度假，包含文化活動"`
- `"東京 5 日遊，2 人，經濟實惠"`
- `"峇里島放鬆一週，含海灘活動"`

## 運作原理

### 平行執行

系統使用 `ParallelAgent` 同時執行三個搜尋：

- **航班搜尋器**：搜尋可用航班
- **飯店搜尋器**：尋找合適住宿
- **活動搜尋器**：推薦當地景點

### 順序合成

所有平行搜尋完成後，`SequentialAgent` 執行：

- **行程建構器**：將所有結果合併成完整旅遊計畫

### 效能優勢

- **順序執行**：約 30 秒（3 個代理 × 每個 10 秒）
- **平行執行**：約 10 秒（全部 3 個並行執行）
- **結果**：I/O 密集任務執行速度快 3 倍

## 實作細節

### 代理結構

```python
# 平行搜尋代理
flight_finder = Agent(name="flight_finder", output_key="flight_options")
hotel_finder = Agent(name="hotel_finder", output_key="hotel_options")
activity_finder = Agent(name="activity_finder", output_key="activity_options")

# 平行執行
parallel_search = ParallelAgent(
  name="ParallelSearch",
  sub_agents=[flight_finder, hotel_finder, activity_finder]
)

# 順序合併
itinerary_builder = Agent(
  name="itinerary_builder",
  instruction="...{flight_options}...{hotel_options}...{activity_options}..."
)

# 完整管線
travel_planning_system = SequentialAgent(
  sub_agents=[parallel_search, itinerary_builder]
)
```

### 狀態流程

1. 平行代理使用 `output_key` 將結果儲存到狀態
2. 行程建構器使用 `{key}` 語法從狀態讀取
3. 資料流向：平行 → 狀態 → 順序 → 輸出

## 測試

執行完整測試套件：

```bash
make test
```

測試涵蓋：

- ✅ 代理設定和指令
- ✅ ParallelAgent 結構和子代理
- ✅ SequentialAgent 管線流程
- ✅ 狀態管理和資料注入
- ✅ 匯入和模組結構
- ✅ 專案檔案組織

## 開發

### 專案結構

```
text
tutorial05/
├── travel_planner/           # 代理實作
│   ├── __init__.py          # 套件初始化
│   ├── agent.py             # 代理定義和管線
│   └── .env.example         # 環境變數範本
├── tests/                   # 完整測試套件
│   ├── __init__.py
│   ├── test_agent.py        # 代理和管線測試
│   ├── test_imports.py      # 匯入驗證測試
│   └── test_structure.py    # 專案結構測試
├── requirements.txt         # Python 相依套件
├── Makefile                # 開發指令
└── README.md               # 本文件
```

### 關鍵檔案

- **`travel_planner/agent.py`**：完整代理實作
- **`tests/test_agent.py`**：50+ 項完整測試
- **`Makefile`**：使用者友善的開發指令

## 學習成果

完成本教學後，你將理解：

- ✅ **ParallelAgent** 用於並行執行
- ✅ **扇出/聚合模式** 用於實際工作流程
- ✅ 透過平行處理進行 **效能最佳化**
- ✅ 平行和順序代理之間的 **狀態管理**
- ✅ 結合不同代理類型的 **管線設計**

## 實際應用

此模式非常適合：

- **資料收集**：同時搜尋多個 API
- **內容生成**：並行建立變體
- **分析任務**：對相同資料執行不同分析
- **驗證**：同時檢查多個條件
- **研究**：從不同來源收集資訊

## 疑難排解

### 常見問題

**「代理似乎依序執行」**

- 檢查事件標籤 - 它們應該同時啟動
- 可能受到 API 速率限制的影響

**「行程建構器缺少資料」**

- 驗證平行代理是否已定義 `output_key`
- 檢查行程指令中的 `{key}` 語法

**「效能沒有改善」**

- 平行加速取決於任務類型
- I/O 密集任務最能受益於平行處理

### 除錯模式

啟用詳細日誌記錄：

```bash
ADK_LOG_LEVEL=DEBUG make dev
```

## 下一步

- **教學 06**：多代理系統 - 結合順序和平行模式
- **進階模式**：錯誤處理、條件流程、巢狀平行處理
- **生產部署**：擴展平行代理以實現高吞吐量應用

## 貢獻

本實作遵循既定的教學模式：

1. **程式碼優先**：文件之前先完成實作
2. **完整測試**：50+ 項測試涵蓋所有功能
3. **使用者友善設定**：簡單的 `make setup && make dev` 工作流程
4. **清晰文件**：逐步指南和範例

## 連結

- **教學**：[教學 05：平行處理](../../docs/tutorial/05_parallel_processing.md)
- **ADK 文件**：google.github.io/adk-docs/
- **上一個教學**：[教學 04 實作](../tutorial04/)

---

## 🎯 重點說明

### 核心概念
1. **平行處理**：使用 ParallelAgent 同時執行多個任務，顯著提升效能
2. **扇出/聚合模式**：先平行收集資料，再順序合成結果
3. **狀態管理**：透過 `output_key` 和 `{key}` 語法在代理間傳遞資料

### 效能提升
- **3倍速度提升**：從順序執行的 30 秒降至平行執行的 10 秒
- 最適合 I/O 密集型任務（如 API 呼叫、資料庫查詢）

### 實際應用
- 旅遊規劃：同時搜尋航班、飯店、活動
- 資料收集：並行查詢多個資料源
- 內容生成：同時產生多個變體

_為 ADK 社群用 ❤️ 打造_