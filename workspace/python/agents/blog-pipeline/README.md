# 教學 04：循序工作流程 - 部落格創建管線

使用 ADK 的 `SequentialAgent` 實現完整的部落格文章創建管線。這展示了如何將多個代理按嚴格順序串連，讓每個代理的輸出成為下一個代理的輸入。

## 管線概覽

部落格創建管線由 4 個按順序運行的代理組成：

1. **研究代理** - 收集關於主題的關鍵事實和資訊
2. **寫作代理** - 根據研究創建引人入勝的部落格草稿
3. **編輯代理** - 審查草稿並提供建設性回饋
4. **格式化代理** - 應用編輯回饋並格式化為 markdown

## 快速開始

```bash
# 安裝依賴項
make setup

# 啟動開發伺服器
make dev
```

然後在瀏覽器中開啟 `http://localhost:8000` 並選擇 "blog_pipeline"。

## 試試這些提示

- "寫一篇關於人工智慧的部落格文章"
- "創建一篇解釋太陽能板如何運作的部落格文章"
- "寫關於網際網路的歷史"
- "關於電動車及其對氣候影響的部落格文章"

## 運作原理

### 狀態流程

```
使用者輸入 → 研究代理 → state['research_findings']
  ↓
寫作代理 (讀取 {research_findings}) → state['draft_post']
  ↓
編輯代理 (讀取 {draft_post}) → state['editorial_feedback']
  ↓
格式化代理 (讀取 {draft_post} + {editorial_feedback}) → 最終輸出
```

### 核心概念

- **`SequentialAgent`**：按嚴格順序編排代理
- **`output_key`**：將代理回應儲存到共享狀態
- **`{key}` 語法**：將狀態值注入代理指令
- **共享 `InvocationContext`**：所有代理存取相同狀態

## 專案結構

```
tutorial04/
├── blog_pipeline/           # 代理實作
│   ├── __init__.py         # 套件標記
│   ├── agent.py            # 管線定義
│   └── .env.example        # 環境範本
├── tests/                  # 完整測試
│   ├── __init__.py
│   ├── test_agent.py       # 代理和管線測試
│   ├── test_imports.py     # 匯入驗證
│   └── test_structure.py   # 專案結構測試
├── requirements.txt        # 依賴項
├── Makefile               # 開發指令
└── README.md              # 本檔案
```

## 測試

```bash
# 執行完整測試套件
make test

# 測試涵蓋：
# - 代理配置和匯入
# - SequentialAgent 管線結構
# - 狀態管理和資料流
# - 個別代理功能
# - 整合測試
```

## 開發

### 新增代理

要擴充管線，請將新代理加入 `sub_agents` 清單：

```python
# 新增事實查核代理
fact_checker_agent = Agent(
  name="fact_checker",
  model="gemini-2.0-flash",
  instruction="驗證以下內容的事實：{draft_post}",
  output_key="fact_check_results"
)

blog_creation_pipeline = SequentialAgent(
  sub_agents=[
    research_agent,
    writer_agent,
    fact_checker_agent,  # 插入到編輯前
    editor_agent,
    formatter_agent
  ]
)
```

### 修改代理指令

每個代理都有專注的指令。更新它們以自訂行為：

```python
writer_agent = Agent(
  instruction=(
    "根據以下內容撰寫技術部落格文章：{research_findings}\n"
    "包含程式碼範例並詳細說明..."
  ),
  output_key="draft_post"
)
```

## 配置

複製 `.env.example` 為 `.env` 並新增您的 API 金鑰：

```bash
cp blog_pipeline/.env.example blog_pipeline/.env
# 使用您的 GOOGLE_API_KEY 編輯 .env
```

## 事件與除錯

在 ADK 網頁 UI 中開啟 **Events 分頁**以查看：

- 每個代理的啟動和完成
- 狀態值的儲存和注入
- 精確的執行順序

這對理解和除錯管線非常寶貴。

## 實際應用

循序工作流程非常適合：

- **內容創建**：研究 → 寫作 → 編輯 → 發布
- **資料處理**：提取 → 轉換 → 驗證 → 載入
- **品質控制**：創建 → 審查 → 修正 → 核准
- **分析管線**：收集 → 分析 → 視覺化 → 報告
- **程式碼工作流程**：撰寫 → 審查 → 重構 → 測試

## 相關教學

- [教學 01](../tutorial01/)：Hello World 代理 - 基本代理設定
- [教學 02](../tutorial02/)：函式工具 - 新增自訂工具
- [教學 03](../tutorial03/)：OpenAPI 工具 - API 整合
- 教學 05：平行處理 - 同時運行代理

## 貢獻

此實作遵循先前教學中建立的模式。若要進行變更：

1. 更新 `blog_pipeline/agent.py` 中的代理程式碼
2. 在 `tests/` 中新增對應測試
3. 如有需要更新此 README
4. 執行 `make test` 以確保一切正常運作

## 授權

本教學是 ADK 培訓系列的一部分。

---

## 📌 重點總結

1. **循序代理管線**：使用 `SequentialAgent` 串連 4 個代理（研究→寫作→編輯→格式化）
2. **狀態共享機制**：透過 `output_key` 儲存結果，用 `{key}` 注入到下一個代理
3. **實用應用場景**：內容創建、資料處理、品質控制等需要順序執行的工作流程
4. **開發與測試**：提供完整的測試套件和可擴充的架構設計
5. **除錯工具**：使用 Events 分頁追蹤執行流程和狀態變化
6. **詳細說明**：README 提供完整的專案結構、使用說明和開發指南與[相關連結](./blog_pipeline/README.md)