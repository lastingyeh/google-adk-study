# Phase 2: 工具整合與前端 UI 實作步驟

本文件基於 `planning.md` 的規劃，將 Phase 2 的目標拆解為更詳細、可執行的開發步驟。

---

## 📋 Phase 2 目標概述

時程: Week 3 - Week 4 (約 2 週)

核心目標: 擴充 Agent 的工具使用能力，並建立一個功能完整的前端 Web UI，提升使用者互動體驗。

技術棧: Google Search API, BuiltInCodeExecutor, React (Vite), AG-UI Protocol, Tailwind CSS

成功標準:

- ✅ Agent 具備網路搜尋與程式碼執行能力
- ✅ React 前端專案成功建立並與後端串接
- ✅ UI 支援串流顯示、多輪對話與 Markdown 渲染
- ✅ 完成模式切換 UI，並能反映後端狀態

---

## Week 3: 核心工具整合

目標: 為 Agent 整合 Google Search、Code Execution 與 Artifact Management 等核心工具，擴展其解決問題的能力。

### 3.1 Google Search Grounding (參考 Day 7: grounding-agent)

- [ ] 啟用 Grounding 功能:
  - 在 `ConversationAgent` 和 `StrategicPlannerAgent` 中使用 `google_search` Tool。
  - 確保 Agent 在需要時能自動觸發網路搜尋以獲取最新資訊。
- [ ] 功能測試與驗證:
  - 測試案例: 提出需要即時資訊的問題，例如「今天天氣如何？」或「最新的 AI 新聞是什麼？」。
  - 驗證要點:
    - Agent 能正確回傳包含網路搜尋結果的答案。
    - 回應中包含引用來源 (citations)。

### 3.2 Code Execution (參考 Day 21: code-calculator)

- [ ] 整合 `BuiltInCodeExecutor`:
  - 在 `StrategicPlannerAgent` 的工具列表中加入 `BuiltInCodeExecutor`。
  - 確保只有在策略規劃模式 (`#think`) 下才能執行程式碼，以符合安全設計。
- [ ] 功能測試與驗證:
  - 測試案例:
    - `#think 計算 123 * 456`
    - `#think 寫一個 Python 函式來計算費波那契數列`
  - 驗證要點:
    - Agent 能正確執行程式碼並回傳結果。
    - 程式碼執行環境是隔離且安全的。
    - 對於不安全的程式碼 (如檔案操作) 能有效拒絕。

### 3.3 File Upload/Download (參考 Day 26: artifact-agent)

- [ ] 整合 `Artifact Tool`:
  - 在 Agent 中加入檔案上傳與下載的工具。
  - 實作後端邏輯以處理檔案的暫存與讀取。
- [ ] API 端點擴充:
  - 建立 `POST /artifacts/upload` 端點。
  - 建立 `GET /artifacts/download/{file_id}` 端點。
- [ ] 功能測試與驗證:
  - 測試案例:
    - 上傳一個 `data.csv` 檔案，並要求 Agent 分析內容 (`#think 分析這個 CSV 檔案的欄位與前五行`)。
    - 要求 Agent 生成一個檔案並提供下載連結 (`#think 產生一份關於專案架構的 Markdown 文件`)。
  - 驗證要點:
    - 檔案能成功上傳至後端。
    - Agent 能讀取並理解上傳的檔案內容。
    - Agent 能生成檔案並讓使用者下載。

---

## Week 4: Web UI 建構

目標: 使用 React 和 AG-UI Protocol 建立一個現代化的前端介面，取代 CLI 工具，提供完整的視覺化互動體驗。

### 4.1 React Vite 專案設定 (參考 Day 40: data-analysis-dashboard)

- [ ] 建立前端專案:
  - 在 `not-chat-gpt` 根目錄下建立 `frontend` 資料夾。
  - 使用 `npm create vite@latest frontend -- --template react-ts` 初始化專案。
- [ ] 安裝核心依賴:
  - `npm install`
  - `npm install tailwindcss postcss autoprefixer @headlessui/react`
  - `npm install @google/generative-ai` (用於 AG-UI Protocol)
- [ ] Tailwind CSS 配置:
  - 執行 `npx tailwindcss init -p`。
  - 設定 `tailwind.config.js` 與 `index.css`。

### 4.2 AG-UI Protocol 整合與串流顯示

- [ ] 建立 `AGUIProvider`:
  - 在 `App.tsx` 中設定 `AGUIProvider`，並指向後端 ADK 服務的 URL。
- [ ] 實作對話核心元件:
  - 建立 `Chat.tsx` 元件。
  - 使用 `useConversation` hook 管理對話狀態。
  - 實作訊息輸入框 (`<Input>`) 與訊息列表 (`<History>`)。
- [ ] 串流回應顯示:
  - 驗證後端 `/run_sse` 或 `/run_live` 端點的串流回應能即時呈現在 UI 上。
  - 測試長篇回覆的打字機效果。

### 4.3 UI 功能完善

- [ ] Markdown 渲染:
  - 引入 `react-markdown` 和 `remark-gfm` 套件。
  - 確保 Agent 回應中的 Markdown 格式 (如程式碼區塊、清單、表格) 能正確渲染。
- [ ] 對話管理 UI:
  - 實作「新增對話」、「載入歷史對話」、「刪除對話」的按鈕與邏輯。
  - 串接後端的 session 管理 API。
- [ ] 模式切換控制元件:
  - 建立一個 Toggle Switch 元件，用於在「一般對話」和「策略規劃」模式間切換。
  - UI 狀態需與後端 Agent 的思考模式同步。
  - 設計一個狀態指示器，清晰地顯示當前 Agent 的運作模式。

### 4.4 Makefile 整合

- [ ] 擴充 `Makefile`:
  - `make dev-frontend`: 啟動前端開發伺服器。
  - `make dev-fullstack`: 同時啟動後端與前端開發伺服器。
  - `make build-frontend`: 建構生產環境的前端靜態檔案。

---

## 📊 Phase 2 里程碑檢查點

### Week 3 完成標準

- ✅ Agent 能夠使用 Google Search 查詢即時資訊並提供引用。
- ✅ Agent 能夠在安全環境中執行 Python 程式碼。
- ✅ 使用者可以上傳檔案供 Agent 分析，並能下載 Agent 生成的檔案。
- ✅ 所有工具整合功能皆有對應的測試案例。

### Week 4 完成標準

- ✅ React 前端專案可獨立運作並成功連線至後端。
- ✅ 對話介面支援完整的串流、歷史紀錄與 Markdown 渲染。
- ✅ 使用者可透過 UI 管理對話 session。
- ✅ UI 上的模式切換功能運作正常，並能反映後端狀態。
- ✅ `make` 指令完成整合，簡化開發與建構流程。

---

## 🔗 Phase 間的銜接

### Phase 2 → Phase 3 交付物

- ✅ 具備多種工具使用能力的進階 Agent。
- ✅ 一個功能完整的 React Web UI。
- ✅ 前後端分離的架構，並透過 API 與 AG-UI Protocol 溝通。
- ✅ 完整的 `fullstack` 開發與部署腳本。

### Phase 3 期待

- 進階 RAG: 實現更複雜的文檔理解與多文件問答。
- Agentic Workflow: 設計多 Agent 協作的複雜工作流。
- 部署與維運: 將應用程式容器化並部署至雲端 (Cloud Run)。
- 監控與日誌: 整合 OpenTelemetry 進行效能監控。
