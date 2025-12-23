# TOOLS 應用說明文件

## 重點摘要
- **核心概念**：定義代理可使用的功能模組 (Tools)。
- **關鍵技術**：Python Functions, Error Handling, Mock Data Generation。
- **重要結論**：工具必須回傳結構化的字典 (status, report, data)，以便 Agent 統一處理。
- **行動項目**：將 `get_current_weather` 與 `search_knowledge_base` 內的模擬邏輯替換為真實 API 呼叫。

### 計算流程圖 (Calculate Expression)
```mermaid
graph TD
    A[輸入表達式] --> B{包含 '% of'?}
    B -->|是| C[解析百分比計算]
    B -->|否| D{結尾是 '%'? }
    D -->|是| E[轉換為小數]
    D -->|否| F[過濾非允許字元]
    F --> G{字串為空?}
    G -->|是| H[回傳錯誤]
    G -->|否| I[執行 eval 安全計算]
    C --> J[回傳結果]
    E --> J
    I --> J
```
---
### 搜尋流程圖 (Search Knowledge Base)
```mermaid
graph TD
    A[輸入查詢] --> B[分割為關鍵字集合]
    B --> C[遍歷知識庫條目]
    C --> D[計算關鍵字重疊分數]
    D --> E[排序結果]
    E --> F{有匹配結果?}
    F -->|是| G[回傳 Top N 結果]
    F -->|否| H["回傳預設結果 (模擬)"]
```