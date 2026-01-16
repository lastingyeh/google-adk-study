# Deep Search - ADK Frontend 應用程式架構文件

## 概述

這是一個基於 React + TypeScript + Vite 構建的 AI 深度搜尋聊天應用程式前端，用於與 Google ADK (Agent Development Kit) 後端進行互動，執行深度研究查詢並生成綜合報告。

## 技術棧

- **框架**: React 18 + TypeScript
- **建置工具**: Vite
- **路由**: React Router
- **UI 元件**: Radix UI + Tailwind CSS
- **Markdown 渲染**: ReactMarkdown + remark-gfm
- **HTTP 通訊**: Fetch API (SSE - Server-Sent Events)

## 專案結構

```
frontend/src/
├── App.tsx                      # 主應用程式元件
├── main.tsx                     # 應用程式入口點
├── utils.ts                     # 工具函數
├── global.css                   # 全域樣式
├── vite-env.d.ts               # TypeScript 環境定義
└── components/                  # 元件目錄
    ├── WelcomeScreen.tsx        # 歡迎畫面
    ├── ChatMessagesView.tsx     # 聊天訊息檢視
    ├── InputForm.tsx            # 輸入表單
    ├── ActivityTimeline.tsx     # 活動時間軸
    └── ui/                      # UI 基礎元件
        ├── badge.tsx
        ├── button.tsx
        ├── card.tsx
        ├── input.tsx
        ├── scroll-area.tsx
        ├── select.tsx
        ├── tabs.tsx
        └── textarea.tsx
```

## 核心元件

### 1. App.tsx - 主應用程式元件

**職責**:
- 管理應用程式全域狀態
- 處理會話 (Session) 建立與管理
- SSE 事件串流處理
- 後端健康檢查與連接管理

**關鍵狀態**:
```typescript
- userId: 使用者 ID
- sessionId: 會話 ID
- appName: 應用程式名稱
- messages: 訊息陣列 (MessageWithAgent[])
- displayData: 顯示資料
- isLoading: 載入狀態
- messageEvents: 訊息事件映射 (Map<string, ProcessedEvent[]>)
- websiteCount: 網站數量統計
- isBackendReady: 後端就緒狀態
```

**核心功能**:

1. **會話管理**
   - `createSession()`: 建立新會話
   - 自動重試機制 (`retryWithBackoff`)

2. **後端健康檢查**
   - `checkBackendHealth()`: 檢查後端服務狀態
   - 最多重試 60 次，間隔 2 秒

3. **SSE 事件處理**
   - `extractDataFromSSE()`: 解析 SSE 資料
   - `processSseEventData()`: 處理 SSE 事件
   - 支援多種事件類型：
     - 文字部分 (textParts)
     - 函數呼叫 (functionCall)
     - 函數回應 (functionResponse)
     - 來源資料 (sources)
     - 最終報告 (finalReportWithCitations)

4. **代理 (Agent) 標題映射**
   ```typescript
   getEventTitle(agentName: string): string
   - plan_generator → "Planning Research Strategy"
   - section_planner → "Structuring Report Outline"
   - section_researcher → "Initial Web Research"
   - enhanced_search_executor → "Enhanced Web Research"
   - interactive_planner_agent → "Interactive Planning"
   - report_composer_with_citations → 最終報告
   ```

**畫面狀態**:
- 後端載入中畫面 (`BackendLoadingScreen`)
- 後端不可用畫面
- 歡迎畫面 (`WelcomeScreen`)
- 聊天訊息檢視 (`ChatMessagesView`)

---

### 2. WelcomeScreen.tsx - 歡迎畫面元件

**職責**:
- 顯示應用程式首頁
- 接收使用者初始查詢

**UI 特色**:
- 居中卡片式設計
- 毛玻璃效果背景 (`backdrop-blur-md`)
- 懸停動畫效果
- 包含標題、描述與輸入表單

**Props**:
```typescript
{
  handleSubmit: (query: string) => void  // 提交處理函數
  isLoading: boolean                     // 載入狀態
  onCancel: () => void                   // 取消函數
}
```

---

### 3. ChatMessagesView.tsx - 聊天訊息檢視元件

**職責**:
- 顯示聊天訊息列表
- 渲染人類與 AI 訊息氣泡
- 整合活動時間軸
- 提供複製功能

**子元件**:

#### HumanMessageBubble
- 使用者訊息氣泡
- 深色背景 (`bg-neutral-700`)
- 支援 Markdown 渲染

#### AiMessageBubble
- AI 回應訊息氣泡
- 三種顯示模式：
  1. **直接顯示模式**: `interactive_planner_agent` 或最終報告
  2. **時間軸模式**: 包含研究過程的活動時間軸
  3. **後備模式**: 其他一般訊息

**Markdown 渲染**:
- 支援 GFM (GitHub Flavored Markdown)
- 自訂樣式元件：h1-h3, p, a, ul/ol, blockquote, code, pre, table 等
- 連結以 Badge 形式顯示
- 程式碼區塊深色主題

**功能**:
- 訊息複製 (Copy to clipboard)
- 新聊天按鈕
- 自動捲動到最新訊息
- 載入指示器

---

### 4. InputForm.tsx - 輸入表單元件

**職責**:
- 接收使用者輸入
- 支援多行文字輸入
- 鍵盤快捷鍵處理

**Props**:
```typescript
{
  onSubmit: (query: string) => void
  isLoading: boolean
  context?: 'homepage' | 'chat'  // 控制提示文字
}
```

**互動**:
- Enter 鍵送出 (Shift+Enter 換行)
- 自動聚焦
- 送出後清空輸入
- 禁用狀態管理

**提示文字**:
- Homepage: "Ask me anything... e.g., A report on the latest Google I/O"
- Chat: "Respond to the Agent, refine the plan, or type 'Looks good'..."

---

### 5. ActivityTimeline.tsx - 活動時間軸元件

**職責**:
- 顯示 AI 代理執行過程
- 展示研究步驟與事件
- 視覺化函數呼叫與回應

**Props**:
```typescript
{
  processedEvents: ProcessedEvent[]  // 處理過的事件陣列
  isLoading: boolean                 // 載入狀態
  websiteCount: number               // 網站數量
}
```

**事件類型處理**:
1. **functionCall**: 函數呼叫
   - 顯示函數名稱與參數
   - 藍色圖示 (`Activity` icon)

2. **functionResponse**: 函數回應
   - 顯示回應資料
   - 綠色圖示

3. **text**: 文字內容
   - Markdown 渲染
   - 支援動態內容

4. **sources**: 來源資料
   - 顯示檢索到的網站連結
   - 黃色連結圖示

**UI 特色**:
- 可摺疊/展開
- 網站數量徽章顯示
- 時間軸視覺化設計
- 載入動畫
- 滾動區域 (max-height: 320px)

**圖示映射**:
```typescript
- "function call" → 藍色 Activity 圖示
- "function response" → 綠色 Activity 圖示
- "research" → Search 圖示
- "thinking" → 旋轉 Loader 圖示
- "retrieved sources" → 黃色 Link 圖示
- 其他 → 預設 Activity 圖示
```

---

### 6. utils.ts - 工具函數

**函數**:
```typescript
cn(...inputs: ClassValue[]): string
```
- 結合 `clsx` 與 `tailwind-merge`
- 用於條件式 CSS 類別合併
- 避免 Tailwind 樣式衝突

---

## UI 元件庫 (components/ui)

基於 **Radix UI** 的自訂元件集：

| 元件 | 用途 |
|------|------|
| `badge.tsx` | 徽章顯示 (如網站數量、連結) |
| `button.tsx` | 按鈕元件 |
| `card.tsx` | 卡片容器 |
| `input.tsx` | 輸入框 |
| `scroll-area.tsx` | 滾動區域 |
| `select.tsx` | 下拉選單 |
| `tabs.tsx` | 分頁元件 |
| `textarea.tsx` | 多行文字輸入 |

---

## 資料流與狀態管理

### 訊息流程

```
使用者輸入查詢
    ↓
WelcomeScreen/ChatMessagesView (InputForm)
    ↓
App.handleSubmit()
    ↓
建立/使用現有 Session
    ↓
發送 POST /api/run_sse
    ↓
接收 SSE 串流
    ↓
extractDataFromSSE() → 解析事件
    ↓
processSseEventData() → 處理事件
    ↓
更新 messages 與 messageEvents
    ↓
ChatMessagesView 渲染
    ↓
顯示 ActivityTimeline 與訊息內容
```

### 狀態更新機制

1. **訊息累積**:
   - `accumulatedTextRef`: 儲存累積的文字內容
   - 適用於 `interactive_planner_agent`

2. **事件追蹤**:
   - `messageEvents`: Map<string, ProcessedEvent[]>
   - 每個 AI 訊息 ID 對應其事件陣列

3. **網站計數**:
   - `websiteCount`: 從 `section_researcher` 或 `enhanced_search_executor` 提取
   - 來自 `url_to_short_id` 物件的鍵數量

---

## API 整合

### 端點

1. **POST** `/api/apps/app/users/u_999/sessions/{sessionId}`
   - 建立新會話
   - 回應: `{ userId, id, appName }`

2. **GET** `/api/docs`
   - 後端健康檢查

3. **POST** `/api/run_sse`
   - 執行查詢 (SSE 串流)
   - 請求體:
     ```json
     {
       "appName": "...",
       "userId": "...",
       "sessionId": "...",
       "newMessage": {
         "parts": [{ "text": "query" }],
         "role": "user"
       },
       "streaming": false
     }
     ```

### SSE 事件格式

```
data: {
  "content": {
    "parts": [
      { "text": "..." },
      { "functionCall": {...} },
      { "functionResponse": {...} }
    ],
    "role": "model"
  },
  "author": "agent_name",
  "actions": {
    "stateDelta": {
      "research_plan": "...",
      "final_report_with_citations": "...",
      "sources": {...},
      "url_to_short_id": {...}
    }
  },
  "usageMetadata": {...}
}
```

---

## 樣式系統

### Tailwind 配色方案

**中性色 (Neutral)**:
- `neutral-100`: 淺色文字
- `neutral-300`: 次要文字
- `neutral-400`: 提示/圖示
- `neutral-600`: 邊框/分隔線
- `neutral-700`: 卡片/氣泡背景
- `neutral-800`: 深色背景
- `neutral-900`: 最深背景/程式碼區塊

**強調色**:
- `blue-400/500`: 主要互動元素、連結
- `purple-500`: 次要強調
- `pink-500`: 動畫裝飾
- `green-500`: 成功/完成狀態
- `red-400`: 錯誤/取消
- `yellow-400`: 警告/來源

### 設計特色

- **毛玻璃效果**: `bg-neutral-900/50 backdrop-blur-md`
- **陰影**: `shadow-2xl shadow-black/60`
- **圓角**: `rounded-2xl`, `rounded-3xl`
- **漸變懸停**: `transition-all duration-300`
- **響應式**: `max-w-2xl`, `max-w-4xl`, `sm:max-w-[90%]`

---

## 錯誤處理

1. **重試機制**:
   - `retryWithBackoff()`: 指數退避重試
   - 最多重試 10 次，最大延遲 5 秒
   - 總時長限制 2 分鐘

2. **後端檢查**:
   - 應用程式啟動時自動檢查
   - 60 次重試，間隔 2 秒
   - 顯示載入畫面或錯誤訊息

3. **SSE 錯誤處理**:
   - 解析錯誤時記錄並繼續
   - 顯示錯誤訊息氣泡
   - 支援取消正在進行的請求

---

## 使用者體驗 (UX) 亮點

1. **即時回饋**:
   - SSE 串流即時顯示
   - 載入動畫與進度指示
   - 網站數量即時更新

2. **互動性**:
   - 可摺疊時間軸
   - 訊息複製功能
   - 鍵盤快捷鍵

3. **視覺層次**:
   - 清晰的訊息區分 (人類 vs AI)
   - 時間軸視覺化
   - Markdown 格式化

4. **狀態管理**:
   - 後端就緒檢查
   - 優雅的錯誤處理
   - 會話持久化

---

## 效能優化

1. **自動捲動**: 使用 ref 與 `useEffect` 確保最新訊息可見
2. **條件渲染**: 根據狀態只渲染必要元件
3. **事件累積**: 避免過度重新渲染
4. **Memo 化**: 子元件接收穩定 props

---

## 開發者備註

### 關鍵設計決策

1. **為何使用 SSE 而非 WebSocket?**
   - 單向資料流適合此應用場景
   - 更簡單的實作與除錯
   - HTTP/2 支援更佳

2. **訊息與事件分離**:
   - `messages`: 顯示的最終訊息
   - `messageEvents`: 過程中的事件追蹤
   - 允許靈活的 UI 呈現

3. **代理識別**:
   - `currentAgentRef`: 追蹤當前活動代理
   - 用於決定內容如何累積與顯示

### 擴展點

1. **新增代理類型**: 在 `getEventTitle()` 中添加映射
2. **自訂事件類型**: 擴展 `ProcessedEvent.data.type`
3. **UI 主題**: 修改 Tailwind 配置與樣式變數
4. **國際化**: 添加 i18n 支援

---

## 總結

此前端應用程式提供了完整的 AI 深度搜尋聊天體驗，具備：
- ✅ 即時串流回應
- ✅ 視覺化研究過程
- ✅ 優雅的錯誤處理
- ✅ 響應式設計
- ✅ 豐富的互動功能

透過模組化的元件設計與清晰的資料流，應用程式易於維護與擴展。
